"""Synthetic no-provider batch tests; inputs contain no private/research content."""
import copy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import claude_batch as batch
from research_archive import ArchiveError
ROOT=Path(__file__).resolve().parents[1]


def request():
    def task(name,deps):
        return {'id':name,'essay_id':'sample','role':'technical','depends_on':deps,
                'configuration':{'model':'claude-opus-5','effort':'low','ui_mode':'not_applicable_subagent'},
                'prompt':'Write a synthetic receipt. No research.', 'inputs':[], 'required_outputs':['report.md'],'public_web':False}
    return {'output_transport':'native_write','batch_id':'synthetic-batch','purpose':'technical','dispatcher_ui_mode':'UNKNOWN','tasks':[task('first',[]),task('second',['first'])]}


class BatchTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.ws=Path(self.temp.name).resolve();self.req=request()
        self.files=batch.compile_packet(ROOT,self.req)
        for name,data in self.files.items():
            p=self.ws/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
        self.base=self.ws/'batches/synthetic-batch'
        for t in self.req['tasks']:(self.base/'tasks'/t['id']/'output').mkdir()
        self.mod=batch.runtime(self.base);self.b=self.mod.Batch(self.base)
        self.h={'session_id':'parent','cwd':str(self.ws),'transcript_path':str(self.ws/'native/parent.jsonl')}
        self.call('SessionStart')
        self.call('UserPromptSubmit',prompt='Start synthetic batch')
    def tearDown(self):self.temp.cleanup()
    def call(self,event,**kw):return self.b.dispatch({**self.h,'hook_event_name':event,**kw})
    def spawn(self,tid='first',aid='child'):
        name=self.b.tasks[tid]['agent_name']
        r=self.call('PreToolUse',tool_name='Agent',tool_use_id='launch-'+aid,tool_input={'subagent_type':name,'prompt':'DO NOT TRUST THIS PARENT CONTENT'})
        self.assertNotIn('DO NOT TRUST',r['hookSpecificOutput']['updatedInput']['prompt'])
        self.call('SubagentStart',agent_id=aid,agent_type=name)
    def write(self,name='report.md',text='Synthetic output',aid='child',call='write'):
        p=self.base/'tasks/first/output'/name
        self.call('PreToolUse',agent_id=aid,tool_name='Write',tool_use_id=call,tool_input={'file_path':str(p),'content':text})
        p.write_text(text)
        self.call('PostToolUse',agent_id=aid,tool_name='Write',tool_use_id=call,tool_response={'success':True})
        return p
    def native(self,p,effort='low'):
        def row(role,c):return {'type':role,'sessionId':'parent','agentId':'child','cwd':str(self.ws),'effort':effort,'message':{'role':role,'model':'claude-opus-5','content':c}}
        data=[row('assistant',[{'type':'thinking','thinking':'HIDDEN_DO_NOT_SAVE'},{'type':'tool_use','id':'write','name':'Write','input':{'file_path':str(p),'content':p.read_text()}}]),row('user',[{'type':'tool_result','tool_use_id':'write','content':'File created successfully at: '+str(p)}]),row('assistant',[{'type':'text','text':'Done'}])]
        path=self.ws/'native/parent/subagents/agent-child.jsonl';path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(b''.join(self.mod.encoded(x)for x in data));return path
    def finish(self,p,effort='low'):
        source=self.native(p,effort)
        return self.call('SubagentStop',agent_id='child',agent_type=self.b.tasks['first']['agent_name'],agent_transcript_path=str(source))
    def test_auto_seal_dependencies_hidden_exclusion_and_idempotence(self):
        self.spawn();p=self.write();self.finish(p)
        state=self.b.state();self.assertIn('first',state['done']);self.assertEqual(self.b.summary(state)['ready'],['second'])
        count=len(list((self.base/'.journal/events').glob('*')));self.finish(p);self.assertEqual(count,len(list((self.base/'.journal/events').glob('*'))))
        for p in (self.base/'.journal/objects').iterdir():self.assertNotIn(b'HIDDEN_DO_NOT_SAVE',p.read_bytes())
        result=batch.inspect_return(ROOT,self.ws,'synthetic-batch');self.assertEqual(result['summary']['completed'],1)
    def test_unready_or_unknown_task_and_cross_essay_read_block(self):
        with self.assertRaises(ValueError):self.spawn('second')
        self.spawn()
        with self.assertRaises(ValueError):self.call('PreToolUse',agent_id='child',tool_name='Read',tool_use_id='read',tool_input={'file_path':str(self.base/'tasks/second/input/task.md')})
        with self.assertRaises(ValueError):self.call('PreToolUse',tool_name='Write',tool_use_id='bad',tool_input={'file_path':'BATCH.json','content':'bad'})
    def test_overwrite_and_native_mode_mismatch(self):
        self.spawn();p=self.write()
        with self.assertRaises(ValueError):self.write()
        with self.assertRaisesRegex(ValueError,'model/effort'):self.finish(p,'xhigh')
        self.assertFalse(self.b.state()['done'])
    def test_pending_result_blocks_dependent_work(self):
        self.spawn();p=self.base/'tasks/first/output/report.md'
        self.call('PreToolUse',agent_id='child',tool_name='Write',tool_use_id='w',tool_input={'file_path':str(p),'content':'x'})
        with self.assertRaisesRegex(ValueError,'durable result'):self.call('PreToolUse',agent_id='child',tool_name='Read',tool_use_id='r',tool_input={'file_path':str(self.base/'tasks/first/input/task.md')})
    def test_pause_control_drift_and_no_duplicate_resume(self):
        self.spawn()
        self.call('SessionStart',session_id='another')
        with self.assertRaises(ValueError):self.call('UserPromptSubmit',session_id='another',prompt='Cannot steal active batch')
        (self.ws/'BATCH.json').write_text('{}')
        with self.assertRaisesRegex(ValueError,'active'):self.call('Stop')
    def test_sealed_file_and_journal_tamper(self):
        self.spawn();p=self.write();self.finish(p);p.write_text('changed')
        with self.assertRaisesRegex(ValueError,'sealed'):self.call('Stop')
    def test_dispatcher_continues_dependency_after_restart(self):
        self.spawn();p=self.write();self.finish(p)
        self.call('PostToolUse',tool_name='Agent',tool_use_id='launch-child',tool_response={'status':'completed'})
        self.b=self.mod.Batch(self.base)
        self.call('SessionStart')
        self.assertEqual(self.b.summary(self.b.state())['ready'],['second'])
        self.spawn('second','child-two')
        self.assertEqual(self.b.state()['agents']['child-two'],'second')

    def test_inputs_and_config_rejected_before_export(self):
        req=request();req['tasks'][1]['essay_id']='other'
        with self.assertRaises(ArchiveError):batch.compile_packet(ROOT,req)
        req=request();req['tasks'][0]['configuration']['ui_mode']='Ultracode'
        with self.assertRaises(ArchiveError):batch.compile_packet(ROOT,req)
        req=request();req['tasks'][0]['configuration']['effort']='imaginary'
        with self.assertRaises(ArchiveError):batch.compile_packet(ROOT,req)
    def test_forged_file_without_write_receipt_is_not_sealed(self):
        self.spawn();p=self.base/'tasks/first/output/report.md';p.write_text('forged')
        with self.assertRaisesRegex(ValueError,'durable Write'):self.finish(p)
    def test_journal_chain_corruption_blocks_next_action(self):
        self.spawn();p=next((self.base/'.journal/events').glob('*.json'));p.write_text('{}')
        with self.assertRaises((ValueError,KeyError)):self.call('Stop')
    def test_worker_tools_require_child_identity(self):
        self.spawn()
        with self.assertRaisesRegex(ValueError,'unregistered'):self.call('PreToolUse',agent_id='unknown',tool_name='Read',tool_use_id='bad',tool_input={'file_path':'BATCH.json'})
    def test_resume_requires_original_child(self):
        self.spawn()
        self.call('PostToolUse',tool_name='Agent',tool_use_id='launch-child',tool_response={'status':'partial'})
        with self.assertRaisesRegex(ValueError,'original'):self.spawn()
        r=self.call('PreToolUse',tool_name='Agent',tool_use_id='resume',tool_input={'subagent_type':self.b.tasks['first']['agent_name'],'resume':'child','prompt':'unused'})
        self.assertEqual(r['hookSpecificOutput']['updatedInput']['resume'],'child')

    def test_legacy_leaf_cannot_claim_batch(self):
        with self.assertRaisesRegex(ValueError,'exact released'):self.call('SessionStart',cwd=str(self.ws/'jobs/old'))

    def test_word_counter_no_estimates(self):
        self.assertEqual(self.mod.word_count(b'# Title\nOne word.\n## Bibliography\nNot counted')['word_units'],3)

    def test_first_prompt_binds_without_matching_startup(self):
        import shutil
        shutil.rmtree(self.base/'.journal')
        self.call('SessionStart',session_id='desktop-provisional')
        self.assertIsNone(self.b.state()['parent_session'])
        self.call('UserPromptSubmit',prompt='Actual launch')
        self.assertEqual(self.b.state()['parent_session'],'parent')
        self.call('SessionStart',session_id='another-provisional')
        self.assertEqual(self.b.state()['parent_session'],'parent')

    def test_first_prompt_without_session_start(self):
        import shutil
        shutil.rmtree(self.base/'.journal')
        self.call('UserPromptSubmit',prompt='Actual launch')
        self.assertEqual(self.b.state()['parent_session'],'parent')

    def test_parent_visible_capture_and_human_prompt(self):
        self.call('UserPromptSubmit',prompt='Start the technical batch.')
        path=Path(self.h['transcript_path']);path.parent.mkdir()
        row={'type':'assistant','sessionId':'parent','cwd':str(self.ws),'effort':'low','message':{'role':'assistant','model':'claude-opus-5','content':[{'type':'thinking','thinking':'HIDDEN_PARENT_CANARY'},{'type':'text','text':'Working.'}]}}
        path.write_bytes(self.mod.encoded(row))
        result=self.call('Stop')
        self.assertEqual(result['decision'],'block')
        objects=b''.join(p.read_bytes() for p in (self.base/'.journal/objects').iterdir())
        self.assertIn(b'Start the technical batch.',objects)
        self.assertIn(b'Working.',objects)
        self.assertNotIn(b'HIDDEN_PARENT_CANARY',objects)


from test_philosophy_bridge import BridgeFixture
from unittest import mock
import claude_project as project
import claude_export as export

class BatchInstallTests(BridgeFixture):
    def setUp(self):
        super().setUp()
        self.write('claude-export-policy.json',{'private_terms':['Private Person']})
        project.initialize(self.root,self.workspace,'synthetic-run')
        self.req=request()
        self.files=batch.compile_packet(self.root,self.req)
        self.review=export.candidate(self.files,{'private_terms':['Private Person']})
        self.review.update(status='REVIEWED',reviewer='synthetic',reviewed_at='2026-09-13')
        for f in self.review['files']:f.update(classification='neutral_instruction',content_and_metadata_reviewed=True,personal_context_absent=True,notes='Synthetic fixture reviewed.')
    def test_install_and_repeated_install(self):
        first=batch.install(self.root,self.workspace,self.req,self.review,'synthetic-run')
        self.assertEqual(first['status'],'PREPARED_NOT_LAUNCHED')
        self.assertEqual(batch.install(self.root,self.workspace,self.req,self.review,'synthetic-run')['status'],'ALREADY_PREPARED')
        self.assertEqual(project.status(self.root,self.workspace)['state'],'IDLE')
    def test_unreviewed_and_changed_packet_rejected(self):
        self.review['status']='PENDING'
        with self.assertRaises(ArchiveError):batch.install(self.root,self.workspace,self.req,self.review,'synthetic-run')
        self.assertFalse((self.workspace/'BATCH.json').exists())
    def test_partial_install_recovery_preserves_exact_bytes(self):
        original=project.replace_control;calls=[]
        def flaky(path,data):
            calls.append(str(path))
            if len(calls)==3:raise OSError('synthetic interrupted publication')
            return original(path,data)
        with mock.patch.object(project,'replace_control',side_effect=flaky):
            with self.assertRaises(OSError):batch.install(self.root,self.workspace,self.req,self.review,'synthetic-run')
        self.assertFalse((self.workspace/'BATCH.json').exists())
        r=batch.install(self.root,self.workspace,self.req,self.review,'synthetic-run')
        self.assertEqual(r['status'],'PREPARED_NOT_LAUNCHED')
