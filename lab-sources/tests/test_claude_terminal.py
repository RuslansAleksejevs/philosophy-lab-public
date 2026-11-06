"""Synthetic tests: no authentication, network or model calls."""
import importlib.util,json,os,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
# Isolate the new adapter from existing bound runners during test discovery.
import importlib.util as _importutil
_standard = ('claude_runner', 'claude_runner_support', 'claude_source_capture')
_saved = {name: sys.modules.get(name) for name in _standard}
_scripts = Path(__file__).resolve().parents[1] / 'scripts' / 'claude_terminal'
def _load(name, filename):
    spec = _importutil.spec_from_file_location(name, _scripts / filename)
    module = _importutil.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module
try:
    capture = _load(__name__ + '_source', 'claude_source_capture.py')
    sys.modules['claude_source_capture'] = capture
    support = _load(__name__ + '_support', 'claude_runner_support.py')
    sys.modules['claude_runner_support'] = support
    r = _load(__name__ + '_runner', 'claude_runner.py')
    sys.modules['claude_runner'] = r
    launcher = _load(__name__ + '_launcher', 'claude_cli_launch.py')
finally:
    for name, module in _saved.items():
        if module is None: sys.modules.pop(name, None)
        else: sys.modules[name] = module

class RunnerTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(prefix='abel-runner-test-');self.addCleanup(self.tmp.cleanup)
  self.base=Path(self.tmp.name).resolve();self.root=self.base/'packet'
  neutral=patch.object(r,'NEUTRAL_ROOT',self.base);neutral.start();self.addCleanup(neutral.stop)
  self.req={'id':'test-round','purpose':'research','tasks':[{'id':'survey','prompt':'Synthetic fixture only.','model':'claude-opus-5-5','effort':'max','public_web':False,'required_outputs':['report.md'],'research_checks':False}]}
  self.request=self.base/'request.json';self.request.write_bytes(r.canonical(self.req))
  r.prepare(self.request,self.root,research_draft=True)
 def test_non_neutral_root_refused(self):
  with self.assertRaisesRegex(ValueError,'neutral research root'):r.neutral_path('/Users/example/packet')
 def test_neutral_symlink_refused(self):
  link=self.base/'alias';link.symlink_to(self.base, target_is_directory=True)
  with self.assertRaisesRegex(ValueError,'symlinks'):r.neutral_path(link/'new')
 def test_personal_paths_blocked(self):
  for value in ('/Users/example/report.md','/home/example/report.md','file:///tmp/a'):
   self.assertTrue(support.relay_screen(value.encode(),'report.md'))
  self.assertFalse(support.relay_screen(b'input/report.md','report.md'))
  self.assertFalse(support.relay_screen(b'https://example.org/home/author/paper','paper.txt'))
 def test_private_prompt_rejected_before_materialization(self):
  self.req['tasks'][0]['prompt']='Read /Users/example/private.md'
  self.request.write_bytes(r.canonical(self.req)); dest=self.base/'new'
  with self.assertRaisesRegex(ValueError,'privacy review'):r.prepare(self.request,dest,True)
  self.assertFalse(dest.exists())
 def test_essay_fields_refused(self):
  self.req['tasks'][0]['manuscripts']=['essay.md'];self.request.write_bytes(r.canonical(self.req))
  with self.assertRaisesRegex(ValueError,'Essay-specific'):r.prepare(self.request,self.base/'new',True)
 def test_multiple_sessions_require_reason(self):
  self.req['tasks'].append({**self.req['tasks'][0],'id':'second'});self.request.write_bytes(r.canonical(self.req))
  with self.assertRaisesRegex(ValueError,'rationale'):r.prepare(self.request,self.base/'new',True)
 def test_interrupted_stage_does_not_publish_partial_work(self):
  t=self.req['tasks'][0];states={'survey':{'status':'pending'}}
  with patch.object(r,'inventory',side_effect=r.FilesChanging('fixture')):
   with self.assertRaises(r.FilesChanging):r.stage(self.root,t,states)
  self.assertFalse((self.root/'work/survey').exists())
  self.assertTrue((r.stage(self.root,t,states)/'input/task.md').exists())
 def release(self):
  m=r.verify(self.root)
  v={'files':{**m['input_hashes'],**m['support_hashes'],'manifest.json':r.digest(r.regular(self.root/'manifest.json')),'runner.py':m['runner_sha256']},'privacy_reviewed':True,'reviewer':'synthetic-test','notes':'Synthetic only','live_test_approved':True,'approval_source':'synthetic-test','subscription_auth_verified':True,'research_approved':True,'technical_acceptance':'synthetic','rules_checked':True,'archive_approval_event':'synthetic'}
  p=self.base/'review.json';p.write_bytes(r.canonical(v));r.release(self.root,p)
 def test_environment_excludes_credentials(self):
  with patch.dict(os.environ,{'ANTHROPIC_API_KEY':'fake','ANTHROPIC_BASE_URL':'fake','CLAUDE_CODE_USE_BEDROCK':'1'}):
   env=r.environment();self.assertNotIn('ANTHROPIC_API_KEY',env);self.assertNotIn('ANTHROPIC_BASE_URL',env)
 def test_explicit_model_max_and_restrictions(self):
  args=r.arguments('claude',self.req['tasks'][0],{'session_id':'id'})
  self.assertEqual(args[args.index('--model')+1],'claude-opus-5-5');self.assertEqual(args[args.index('--effort')+1],'max')
  self.assertIn('--restricted',args);self.assertIn('--safe-mode',args);self.assertNotIn('Bash',args[args.index('--tools')+1]);self.assertNotIn('--dangerously-skip-permissions',args)
 def test_resume_identity(self):
  a=r.arguments('claude',self.req['tasks'][0],{'session_id':'same','session_observed':True});self.assertIn('--resume',a);self.assertEqual(a[-1],'same')
 def test_input_drift_rejected(self):
  (self.root/'inputs/survey/task.md').write_text('changed')
  with self.assertRaises(ValueError):r.verify(self.root)
 def test_symlink_rejected(self):
  p=self.base/'link';p.symlink_to(self.request)
  with self.assertRaises(ValueError):r.regular(p)
 def test_hash_bound_release(self):
  self.release();self.assertTrue((self.root/'release.json').exists())
 def test_no_overwrite_packet(self):
  with self.assertRaises(ValueError):r.prepare(self.request,self.root,True)
 def test_hidden_reasoning_not_persisted(self):
  v=r.visible({'type':'assistant','message':{'model':'claude-opus-5-5','content':[{'type':'thinking','thinking':'SECRET'},{'type':'text','text':'visible'},{'type':'tool_use','name':'Read','input':{'content':'SECRET'}}]}})
  self.assertNotIn('SECRET',json.dumps(v));self.assertEqual(v['text'],['visible'])
 def test_private_source_blocked(self):
  for url in ('file:///etc/passwd','http://example.com','https://127.0.0.1/private','https://user:password@example.com'):
   with self.assertRaises(ValueError):capture.public_url(url)
 def test_source_extraction(self):
  out,_,_=capture.extract(b'<html><head>hidden</head><p>Evidence</p><script>hidden</script></html>','text/html')
  self.assertIn(b'Evidence',out);self.assertNotIn(b'hidden',out)
 def test_native_configuration_rejects_wrong_effort(self):
  self.release();states={'survey':{'status':'pending','session_id':'test'}};work=r.stage(self.root,self.req['tasks'][0],states)
  (work/'output/report.md').write_text('fixture');(work/'output/source-status.json').write_text('{"sources":[{"url":"https://example.com","coverage":"unavailable","note":"fixture"}]}')
  t={**self.req['tasks'][0],'research_checks':True};v=support.validate(r,self.root,t,states['survey'],{'observations':[{'model':'claude-opus-5-5','effort':'xhigh'}]})
  self.assertIn('native_configuration_unverified_or_changed',v['errors'])
 def fake_run(self,quota=False,special=False):
  self.release();fake=self.base/'fake.py'
  fake.write_text('''import sys,json
from pathlib import Path
sid=sys.argv[1];sys.stdin.read()
print(json.dumps({'type':'system','subtype':'init','session_id':sid,'model':'claude-opus-5-5'}),flush=True)
Path('output/report.md').write_text('Preserved partial or complete result')
'''+("import os;os.mkfifo('output/unexpected-pipe')\n" if special else '')+("print(json.dumps({'type':'rate_limit_event','rate_limit_info':{'status':'rejected','resetsAt':1999999999}}),flush=True)\nprint(json.dumps({'type':'result','subtype':'error_during_execution','is_error':True,'result':'usage limit reached','session_id':sid}),flush=True)" if quota else "print(json.dumps({'type':'result','subtype':'success','is_error':False,'result':'done','session_id':sid}),flush=True)"))
  args=lambda exe,t,s:[sys.executable,str(fake),s['session_id']]
  with patch.object(r,'preflight',return_value='fake'),patch.object(r,'arguments',side_effect=args),patch.object(support,'native_observations',return_value={'observations':[]}):
   result=r.run(self.root)
  return result,r.load(self.root/'state.json')['survey']
 def test_success_archives_output(self):
  res,state=self.fake_run();self.assertEqual(res['status'],'done');self.assertIn('report.md',state['outputs']);self.assertTrue(state['session_observed'])
 def test_collect_preserves_hashes_and_refuses_overwrite(self):
  self.fake_run();destination=self.base/'quarantine';r.collect(self.root,destination)
  receipt=r.load(destination/'collection.json')
  for name,key in receipt['files'].items():self.assertEqual(r.digest(r.regular(destination/name)),key)
  self.assertEqual(receipt['canonical_import'],'pending')
  with self.assertRaises(ValueError):r.collect(self.root,destination)
 def test_unreleased_packet_cannot_dispatch(self):
  with patch.object(r,'preflight',side_effect=AssertionError('must not launch')):
   with self.assertRaises(FileNotFoundError):r.run(self.root)
 def test_harness_failure_records_paused_and_path(self):
  with self.assertRaisesRegex(ValueError,'unexpected-pipe'):self.fake_run(special=True)
  s=r.load(self.root/'state.json')['survey'];self.assertEqual(s['status'],'paused');self.assertEqual(s['reason'],'harness_error');self.assertIsNone(s['pid']);self.assertIn('unexpected-pipe',s['harness_error'])
 def test_quota_preserves_session_and_partial(self):
  res,state=self.fake_run(True);self.assertEqual(state['reason'],'quota');self.assertEqual(state['quota_notice']['resetsAt'],1999999999);self.assertIn('report.md',state['outputs']);self.assertTrue(state['session_observed'])
 def test_stop_latch_blocks_dispatch(self):
  self.release();r.atomic(self.root/'STOP.json',r.canonical({'reason':'test'}))
  with patch.object(r,'preflight',side_effect=AssertionError('must not launch')):self.assertEqual(r.run(self.root)['reason'],'batch_stop_latched')
 def test_disappearing_entry_is_retried(self):
  folder=self.base/'changing';folder.mkdir();f=folder/'temporary';f.write_text('partial')
  original=Path.rglob;calls=0
  def listing(p,pattern):
   nonlocal calls
   if p==folder and calls==0:
    calls+=1;f.unlink();return iter([f])
   return original(p,pattern)
  with patch.object(Path,'rglob',listing):self.assertEqual(r.inventory(folder),{})
 def test_old_error_reproduced_by_disappearing_file(self):
  f=self.base/'vanishing';f.write_text('ordinary');listed=[f];f.unlink()
  with self.assertRaisesRegex(ValueError,'Special file in packet'):
   for p in listed:
    if p.is_file():pass
    elif not p.is_dir():raise ValueError('Special file in packet')
 def test_live_snapshot_keeps_last_good_version(self):
  work=self.root/'work/survey/output';work.mkdir(parents=True);(work/'report.md').write_text('complete bytes')
  old=r.snapshot(self.root,'survey')
  with patch.object(r,'tree_bytes',side_effect=r.FilesChanging('test transient')):
   self.assertEqual(r.snapshot(self.root,'survey',live=True),old)
   with self.assertRaises(r.FilesChanging):r.snapshot(self.root,'survey')
  self.assertEqual(r.load(self.root/'snapshots/survey.json'),old)
 def test_real_special_file_is_not_ignored(self):
  folder=self.base/'fifo-test';folder.mkdir();f=folder/'pipe';os.mkfifo(f)
  with self.assertRaisesRegex(ValueError,'Special file in packet: .*pipe'):r.inventory(folder)
 def test_snapshot_stores_exact_captured_bytes(self):
  work=self.root/'work/survey/output';work.mkdir(parents=True);(work/'report.md').write_bytes(b'version-one')
  snapshot=r.snapshot(self.root,'survey');key=snapshot['report.md']
  self.assertEqual(key,r.digest(b'version-one'));self.assertEqual((self.root/'objects'/key).read_bytes(),b'version-one')

if __name__=='__main__':unittest.main()
