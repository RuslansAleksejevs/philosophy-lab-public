"""Progressive file delivery and expected subscription pauses; no model calls."""
import json
import test_claude_batch_text as helpers

# Reuse lifecycle helpers, not the base class test suite.
import unittest
class GradualTests(unittest.TestCase):
    tearDown=helpers.TextTransportTests.tearDown
    call=helpers.TextTransportTests.call
    row=helpers.TextTransportTests.row
    spawn=helpers.TextTransportTests.spawn
    envelope=helpers.TextTransportTests.envelope
    native=helpers.TextTransportTests.native
    finish=helpers.TextTransportTests.finish
    result=helpers.TextTransportTests.result
    def setUp(self):
        helpers.TextTransportTests.setUp(self)
        self.b.manifest['recovery_policy']='gradual-v1'
    def test_files_accumulate_and_missing_complete_is_checkpoint(self):
        self.spawn(); self.finish(self.envelope(files={'notes.md':'first exact bytes'})); self.result()
        self.assertFalse(self.b.state()['done'])
        self.call('PreToolUse',tool_name='SendMessage',tool_use_id='resume',tool_input={'to':'child'})
        self.result('resume','SendMessage')
        self.finish(self.envelope(files={'report.md':'last file'}),append=True)
        self.assertEqual((self.base/'tasks/first/output/notes.md').read_text(),'first exact bytes')
        self.assertIn('first',self.b.state()['done'])
    def test_quota_preserves_pending_and_requires_human_resume(self):
        self.spawn()
        self.call('StopFailure',error='rate_limit_error')
        self.assertEqual(self.b.summary(self.b.state())['state'],'WAITING_FOR_QUOTA')
        self.assertIn('launch',self.b.state()['pending'])
        r=self.call('PreToolUse',tool_name='Agent',tool_use_id='duplicate',tool_input={})
        self.assertEqual(r['hookSpecificOutput']['permissionDecision'],'deny')
        self.assertFalse(self.b.state().get('halt'))
        self.call('UserPromptSubmit',prompt='Continue after reset')
        self.assertNotIn('launch',self.b.state()['pending'])
        self.assertEqual(self.b.state()['checkpoints']['first']['agent_id'],'child')
        self.call('PreToolUse',tool_name='SendMessage',tool_use_id='resume',tool_input={'to':'child'})
        self.result('resume','SendMessage');self.finish(self.envelope())
        self.assertIn('first',self.b.state()['done'])
    def test_repeat_quota_is_pause_not_repair(self):
        self.spawn()
        for _ in range(3):
            self.call('StopFailure',error='usage limit reached')
            self.assertFalse(self.b.state().get('halt'))
            self.call('UserPromptSubmit',prompt='Continue')
        self.assertEqual(len(self.b.state()['agents']),1)
    def test_unacknowledged_launch_never_duplicates(self):
        self.call('PreToolUse',tool_name='Agent',tool_use_id='launch',tool_input={'subagent_type':self.b.tasks['first']['agent_name']})
        self.call('StopFailure',error='rate limit')
        r=self.call('UserPromptSubmit',prompt='Continue')
        self.assertEqual(r['decision'],'block')
        self.assertEqual(self.b.summary(self.b.state())['state'],'WAITING_FOR_QUOTA')
        self.assertFalse(self.b.state().get('halt'))
    def test_normal_early_stop_gets_one_automatic_continuation(self):
        self.spawn();self.finish(self.envelope('checkpoint',{'notes.md':'saved'}));self.result()
        self.assertEqual(self.call('Stop').get('decision'),'block')
        self.assertNotEqual(self.call('Stop').get('decision'),'block')
    def test_incomplete_native_reply_preserved_and_retry_bounded(self):
        self.spawn();self.finish('The output was cut off.');self.result()
        self.assertIn('first',self.b.state()['checkpoints'])
        self.assertFalse(self.b.state().get('halt'))
    def test_many_progressing_files_not_three_retry_limit(self):
        self.spawn()
        for i in range(5):
            if i:
                self.call('PreToolUse',tool_name='SendMessage',tool_use_id=f'r{i}',tool_input={'to':'child'})
                self.result(f'r{i}','SendMessage')
            self.finish(self.envelope('checkpoint',{f'part-{i}.txt':str(i)}),append=bool(i))
            if not i:self.result()
        self.assertFalse(self.b.state().get('halt'))
        self.assertEqual(len(self.b.state()['checkpoints']['first']['files']),5)
    def test_large_unicode_file_and_extra_metadata_exact(self):
        self.spawn();text=('α 🧪 \\"\\n'*12000)
        self.finish(self.envelope(files={'report.md':text},extra={'harmless':True}));self.result()
        self.assertEqual((self.base/'tasks/first/output/report.md').read_bytes(),text.encode())
    def test_quota_late_callback_cannot_seal_or_halt(self):
        self.spawn();self.call('StopFailure',error='rate limit');self.call('UserPromptSubmit',prompt='Continue')
        self.result();self.assertFalse(self.b.state().get('halt'));self.assertFalse(self.b.state()['done'])
    def test_compile_opt_in_preserves_native_configuration(self):
        import claude_batch
        from test_claude_batch import ROOT
        request={**self.req,'recovery_policy':'gradual-v1'}
        files=claude_batch.compile_packet(ROOT,request)
        manifest=json.loads(files['batches/synthetic-batch/manifest.json'])
        self.assertEqual(manifest['recovery_policy'],'gradual-v1')
        self.assertEqual(manifest['tasks'][0]['configuration'],request['tasks'][0]['configuration'])
        self.assertIn(b'ONE output file',files['batches/synthetic-batch/tasks/first/input/task.md'])
    def test_native_synthetic_quota_is_not_malformed_output(self):
        self.spawn();p=self.native(self.envelope('checkpoint',{'notes.md':'preserved'}))
        r=self.row('assistant',[{'type':'text','text':'usage limit reached'}])
        r['isApiErrorMessage']=True;r['error']='rate_limit';r['message']['model']='<synthetic>'
        with p.open('ab') as f:f.write(self.mod.encoded(r))
        self.call('SubagentStop',agent_id='child',agent_type=self.b.tasks['first']['agent_name'],agent_transcript_path=str(p),last_assistant_message='usage limit reached')
        self.assertEqual(self.b.summary(self.b.state())['state'],'WAITING_FOR_QUOTA')
        self.assertEqual((self.base/'tasks/first/output/notes.md').read_text(),'preserved')
        self.assertFalse(self.b.state().get('halt'))
        self.result()
        self.assertFalse(self.b.state().get('halt'))
        self.assertEqual(self.b.summary(self.b.state())['state'],'WAITING_FOR_QUOTA')
    def test_status_read_and_denied_callback_during_quota_do_not_break_pause(self):
        self.spawn();self.call('StopFailure',error='rate limit')
        self.call('PreToolUse',tool_name='Read',tool_use_id='status',tool_input={'file_path':str(self.base/'STATUS.json')})
        self.call('PostToolUseFailure',tool_name='Read',tool_use_id='status',error='denied while waiting')
        self.assertFalse(self.b.state().get('halt'))
        self.assertEqual(self.b.summary(self.b.state())['state'],'WAITING_FOR_QUOTA')
