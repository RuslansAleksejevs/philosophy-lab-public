"""Local subprocess fixtures only. Never invokes a real Claude executable."""
import contextlib
import io
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import claude_runner as r

FAKE = '''#!/usr/bin/env python3
import json,sys,pathlib,os,signal,time
args=sys.argv
sid=args[args.index('--resume')+1] if '--resume' in args else args[args.index('--session-id')+1]
sys.stdin.read()
def emit(e):
 e['session_id']=sid;print(json.dumps(e),flush=True)
emit({'type':'system','subtype':'init','model':'fixture'})
p=pathlib.Path('output');p.mkdir(exist_ok=True)
task=pathlib.Path('input/task.md').read_text()
if 'dependency' in task:
 assert pathlib.Path('input/prior.txt').read_text()=='complete'
if 'quota' in task and '--resume' not in args:
 (p/'partial.txt').write_text('preserved')
 emit({'type':'assistant','message':{'content':[{'type':'thinking','thinking':'DO_NOT_CAPTURE'},{'type':'text','text':'Partial saved'}],'model':'fixture'}})
 emit({'type':'result','subtype':'error_during_execution','is_error':True,'result':'rate_limit'})
 sys.exit(1)
if 'interrupt' in task and '--resume' not in args:
 (p/'partial.txt').write_text('preserved')
 emit({'type':'assistant','message':{'content':[{'type':'text','text':'Partial saved'}]}})
 os.kill(os.getppid(),signal.SIGINT)
 time.sleep(1)
 sys.exit(130)
if 'malformed' in task:
 print('not-json',flush=True)
if 'missing' not in task:
 (p/'result.txt').write_text('complete')
if 'tamper' in task:
 pathlib.Path('input/task.md').write_text('changed')
if 'false-success' in task:
 emit({'type':'result','subtype':'error_during_execution','is_error':True,'result':'failed'})
else:
 emit({'type':'result','subtype':'success','is_error':False,'result':'done'})
'''


class FileRunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name).resolve()
        self.fake = self.base / 'fake-claude'
        self.fake.write_text(FAKE); self.fake.chmod(0o700)
        self.packet = self.base / 'packet'

    def tearDown(self):
        self.temp.cleanup()

    def make(self, prompts=('normal',)):
        tasks=[]
        for i, prompt in enumerate(prompts):
            t={'id': 'task-' + str(i), 'prompt': prompt, 'model':'fixture', 'effort':'low',
               'inputs':[], 'required_outputs':['result.txt']}
            if 'dependency' in prompt:
                t['dependencies']=[{'task':'task-0','file':'result.txt','as':'prior.txt'}]
            tasks.append(t)
        req=self.base/'request.json'
        req.write_bytes(r.canonical({'id':'fixture','purpose':'technical','tasks':tasks}))
        r.prepare(req,self.packet)
        # Synthetic approval fixture. It is never used to release live Claude.
        m=r.load(self.packet/'manifest.json')
        review={'files':{**m['input_hashes'],**m['support_hashes'],'manifest.json':r.digest(r.regular(self.packet/'manifest.json')),
                         'runner.py':m['runner_sha256']},'privacy_reviewed':True,'reviewer':'synthetic-test',
                'notes':'fixture only','live_test_approved':True,'approval_source':'synthetic-test',
                'subscription_only_confirmed':True}
        rp=self.base/'review.json';rp.write_bytes(r.canonical(review));r.release(self.packet,rp)

    def run_fake(self, resume_stopped=False):
        with patch.object(r,'preflight',return_value=str(self.fake)),contextlib.redirect_stdout(io.StringIO()):
            return r.run(self.packet, resume_stopped)

    def test_fresh_sessions_and_only_selected_dependencies(self):
        self.make(('normal','dependency'))
        self.assertEqual(self.run_fake()['status'],'done')
        s=r.load(self.packet/'state.json')
        self.assertNotEqual(s['task-0']['session_id'],s['task-1']['session_id'])
        self.assertEqual((self.packet/'work/task-1/input/prior.txt').read_text(),'complete')
        self.assertFalse((self.packet/'work/task-1/input/other').exists())
        count=len(list((self.packet/'records').iterdir()))
        self.run_fake()
        self.assertEqual(count,len(list((self.packet/'records').iterdir())))

    def test_quota_resume_keeps_partial_and_filters_thinking(self):
        self.make(('quota','dependency'))
        self.assertEqual(self.run_fake()['status'],'paused')
        first=r.load(self.packet/'state.json')['task-0']['session_id']
        self.assertFalse((self.packet/'work/task-1').exists())
        self.assertEqual(self.run_fake()['status'],'done')
        self.assertEqual(first,r.load(self.packet/'state.json')['task-0']['session_id'])
        self.assertEqual((self.packet/'work/task-0/output/partial.txt').read_text(),'preserved')
        all_records=b''.join(x.read_bytes() for x in (self.packet/'records').iterdir())
        self.assertNotIn(b'DO_NOT_CAPTURE',all_records)
        self.assertIn(b'Partial saved',all_records)

    def test_actual_sigint_preserves_and_resumes(self):
        self.make(('interrupt',))
        self.assertEqual(self.run_fake()['status'],'paused')
        s=r.load(self.packet/'state.json')['task-0']
        self.assertEqual(s['reason'],'human_stop')
        self.assertEqual(self.run_fake()['reason'],'batch_stop_latched')
        self.assertEqual(self.run_fake(resume_stopped=True)['status'],'done')

    def test_provider_error_with_exit_zero_is_not_success(self):
        self.make(('false-success',))
        self.assertEqual(self.run_fake()['status'],'paused')

    def test_missing_files_are_not_success(self):
        self.make(('missing',))
        self.assertEqual(self.run_fake()['status'],'paused')

    def test_malformed_stream_needs_review(self):
        self.make(('malformed',))
        self.assertEqual(self.run_fake()['status'],'needs_review')

    def test_changed_input_blocks_acceptance(self):
        self.make(('tamper',))
        self.assertEqual(self.run_fake()['status'],'needs_review')

    def test_accepted_outputs_cannot_be_silently_changed(self):
        self.make();self.run_fake()
        (self.packet/'work/task-0/output/result.txt').write_text('changed')
        with self.assertRaisesRegex(ValueError,'Accepted output changed'):
            self.run_fake()
        self.assertIn(r.digest(b'complete'),[p.name for p in (self.packet/'objects').iterdir()])

    def test_release_and_exact_bytes_required(self):
        self.make();(self.packet/'release.json').unlink()
        with self.assertRaises(FileNotFoundError): self.run_fake()
        (self.packet/'inputs/task-0/task.md').write_text('changed')
        with self.assertRaisesRegex(ValueError,'Input bytes changed'): r.verify(self.packet)

    def test_failed_spawn_can_be_retried_without_losing_task(self):
        self.make()
        with patch.object(r,'preflight',return_value=str(self.base/'absent')),contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(r.run(self.packet)['status'],'paused')
        self.assertEqual(self.run_fake()['status'],'done')

    def test_lock_and_live_pid_prevent_duplicate(self):
        self.make()
        with r.lock(self.packet):
            with self.assertRaisesRegex(ValueError,'already owns'): self.run_fake()
        (self.packet/'state.json').write_bytes(r.canonical({'task-0':{'status':'running','pid':os.getpid()}}))
        with self.assertRaisesRegex(ValueError,'still be running'): self.run_fake()

    def test_collect_preserves_versions_and_hashes(self):
        self.make(('quota',));self.run_fake();self.run_fake()
        dest=self.base/'intake';r.collect(self.packet,dest)
        receipt=r.load(dest/'collection.json')
        for name,key in receipt['files'].items():
            self.assertEqual(r.digest(r.regular(dest/name)),key)
        self.assertEqual(receipt['canonical_import'],'pending')
        self.assertTrue((dest/'objects'/r.digest(b'preserved')).exists())

    def test_canonical_intake_is_idempotent_and_detects_tampering(self):
        from claude_runner_intake import ingest
        from research_archive import Archive, ArchiveError
        self.make();self.run_fake()
        dest=self.base/'intake';r.collect(self.packet,dest)
        archive=Archive(self.base/'archive').init()
        first=ingest(dest,archive,'test-session','test-run')
        second=ingest(dest,archive,'test-session','test-run')
        self.assertEqual(first['event_id'],second['event_id'])
        self.assertEqual(len(archive.events()),1)
        (dest/'manifest.json').write_text('{}')
        with self.assertRaisesRegex(ArchiveError,'hash mismatch'):
            ingest(dest,archive,'test-session','test-run')

    def test_no_api_or_injected_context_in_environment(self):
        with patch.dict(os.environ,{'ANTHROPIC_API_KEY':'secret','CLAUDE_CODE_USE_BEDROCK':'1','CLAUDE_CONFIG_DIR':'private'}):
            env=r.environment()
        self.assertNotIn('ANTHROPIC_API_KEY',env)
        self.assertNotIn('CLAUDE_CONFIG_DIR',env)
        args=r.arguments('claude',{'model':'opus','effort':'low'},{'session_id':'id'})
        self.assertIn('--safe-mode',args);self.assertIn('--restricted',args)
        self.assertNotIn('--bare',args);self.assertNotIn('--dangerously-skip-permissions',args)
        self.assertNotIn('Bash',args[args.index('--tools')+1])

    def test_research_preparation_is_paused(self):
        req=self.base/'r.json';req.write_bytes(r.canonical({'id':'x','purpose':'research'}))
        with self.assertRaisesRegex(ValueError,'paused'): r.prepare(req,self.packet)

    def test_research_draft_can_be_prepared_but_not_released_or_run(self):
        self.make()
        req=self.base/'request.json';data=r.load(req);data['purpose']='research';req.write_bytes(r.canonical(data))
        draft=self.base/'research-draft';r.prepare(req,draft,research_draft=True)
        self.assertEqual(r.load(draft/'manifest.json')['purpose'],'research')
        m=r.load(draft/'manifest.json');review=r.load(self.base/'review.json')
        review['files']={**m['input_hashes'],**m['support_hashes'],'manifest.json':r.digest(r.regular(draft/'manifest.json')),'runner.py':m['runner_sha256']}
        (self.base/'review.json').write_bytes(r.canonical(review))
        with self.assertRaisesRegex(ValueError,'Research release requires'):
            r.release(draft,self.base/'review.json')
        with self.assertRaises(FileNotFoundError):
            r.run(draft)

    def test_symlink_outputs_rejected(self):
        self.make();self.run_fake()
        (self.packet/'work/task-0/output/link').symlink_to(self.base/'request.json')
        with self.assertRaisesRegex(ValueError,'Symlink'):r.collect(self.packet,self.base/'out')

    def test_private_tool_bodies_and_system_prompts_are_not_captured(self):
        self.assertIsNone(r.visible({'type':'system','subtype':'other','systemPrompt':'private'}))
        e=r.visible({'type':'assistant','message':{'content':[{'type':'tool_use','name':'Read','input':{'file_path':'private'}},{'type':'thinking','thinking':'private'}]}})
        self.assertNotIn('private',json.dumps(e))


if __name__=='__main__':unittest.main()
