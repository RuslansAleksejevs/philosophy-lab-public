"""Cancellation lifecycle replay: native records may replace missing callbacks."""
import json
import test_claude_gradual as gradual
import unittest

CANCEL=("The user doesn't want to proceed with this tool use. The tool use was rejected "
        "(eg. if it was a file edit, the new_string was NOT written to the file). "
        "STOP what you are doing and wait for the user to tell you how to proceed.")

class InterruptionTests(unittest.TestCase):
    setUp=gradual.GradualTests.setUp
    tearDown=gradual.GradualTests.tearDown
    call=gradual.GradualTests.call
    row=gradual.GradualTests.row
    spawn=gradual.GradualTests.spawn
    native=gradual.GradualTests.native
    envelope=gradual.GradualTests.envelope
    finish=gradual.GradualTests.finish
    result=gradual.GradualTests.result

    def cancel(self,call='launch',child=True):
        r=self.row('user',[{'type':'tool_result','tool_use_id':call,'is_error':True,'content':CANCEL}],child=False)
        with self.parent.open('ab') as f:f.write(self.mod.encoded(r))
        if child:
            p=self.parent.parent/'parent/subagents/agent-child.jsonl';p.parent.mkdir(parents=True,exist_ok=True)
            with p.open('ab') as f:f.write(self.mod.encoded(self.row('user',[{'type':'text','text':'[Request interrupted by user]'}])))

    def resume(self):return self.call('UserPromptSubmit',prompt='Continue the remaining package')
    def send(self,call='resume'):return self.call('PreToolUse',tool_name='SendMessage',tool_use_id=call,tool_input={'to':'child'})
    def status(self,call='status'):return self.call('PreToolUse',tool_name='Read',tool_use_id=call,tool_input={'file_path':str(self.base/'STATUS.json')})

    def test_actual_cancel_without_failure_hook_resumes_original(self):
        self.spawn();self.cancel();r=self.resume()
        self.assertIn('SendMessage',r['hookSpecificOutput']['additionalContext'])
        s=self.b.state();self.assertFalse(s['pending']);self.assertFalse(s['done'])
        self.assertIn('launch',s['interrupted_calls']);self.assertEqual(s['checkpoints']['first']['agent_id'],'child')
        self.assertEqual(self.send()['hookSpecificOutput']['permissionDecision'],'allow')
        self.result('resume','SendMessage');self.finish(self.envelope(),append=True)
        self.assertIn('first',self.b.state()['done']);self.assertEqual(self.b.summary(self.b.state())['ready'],['second'])

    def test_old_interrupted_halt_reconciles(self):
        self.spawn();self.cancel();self.call('Stop')
        self.assertEqual(self.b.state()['halt']['state'],'INTERRUPTED')
        self.resume();self.assertFalse(self.b.state().get('halt'));self.assertFalse(self.b.state()['pending'])

    def test_status_during_pending_launch_and_after_quota(self):
        self.spawn();self.assertEqual(self.status()['hookSpecificOutput']['permissionDecision'],'allow')
        self.result('status','Read');self.call('StopFailure',error='usage limit')
        self.assertEqual(self.status('qstatus')['hookSpecificOutput']['permissionDecision'],'allow')
        self.result('qstatus','Read');self.assertTrue(self.b.state()['quota_wait'])

    def test_read_permission_still_scoped_during_wait(self):
        self.spawn()
        r=self.call('PreToolUse',tool_name='Read',tool_use_id='leak',tool_input={'file_path':str(self.ws/'unassigned-private.txt')})
        self.assertEqual(r['hookSpecificOutput']['permissionDecision'],'deny')
        self.assertFalse(self.b.state().get('halt'))

    def test_new_prompt_does_not_cancel_running_worker(self):
        self.spawn();self.resume();self.assertIn('launch',self.b.state()['pending'])
        self.assertFalse(self.b.state().get('checkpoints'))

    def test_old_cancellation_not_reused_for_new_continuation(self):
        self.spawn();self.cancel();self.resume();self.send();self.result('resume','SendMessage')
        self.resume();self.assertIn('first',self.b.state()['continuing'])
        self.assertEqual(self.send('duplicate')['hookSpecificOutput']['permissionDecision'],'deny')

    def test_background_cancel_after_send_receipt(self):
        self.spawn();self.finish(self.envelope('checkpoint',{'notes.md':'keep'}));self.result()
        self.send();self.result('resume','SendMessage');self.cancel('resume');self.resume()
        self.assertFalse(self.b.state()['continuing']);self.assertEqual((self.base/'tasks/first/output/notes.md').read_text(),'keep')
        self.assertEqual(self.send('again')['hookSpecificOutput']['permissionDecision'],'allow')

    def test_cancel_followed_by_child_activity_is_not_stopped(self):
        self.spawn();self.cancel();self.native('still working',append=True);self.resume()
        self.assertIn('launch',self.b.state()['pending']);self.assertFalse(self.b.state().get('checkpoints'))

    def test_unknown_child_identity_never_relaunched(self):
        self.call('PreToolUse',tool_name='Agent',tool_use_id='launch',tool_input={'subagent_type':self.b.tasks['first']['agent_name']})
        self.cancel(child=False);self.resume();self.assertIn('launch',self.b.state()['pending'])

    def test_aborted_hook_recovers_once_even_without_native_marker(self):
        self.spawn();self.call('PostToolUseFailure',tool_name='Agent',tool_use_id='launch',error='Interrupted',is_interrupt=True)
        self.resume();self.assertFalse(self.b.state().get('halt'));self.send();self.result('resume','SendMessage')
        self.resume();self.assertIn('first',self.b.state()['continuing'])

    def test_child_pending_read_is_preserved_as_unknown(self):
        self.spawn();self.call('PreToolUse',agent_id='child',tool_name='Read',tool_use_id='child-read',tool_input={'file_path':'input/task.md'})
        self.cancel();self.resume();s=self.b.state()
        self.assertFalse(s['pending']);self.assertIn('child-read',s['interrupted_calls']);self.assertFalse(s['done'])

    def test_late_cancelled_callback_cannot_seal_or_halt(self):
        self.spawn();self.cancel();self.resume();self.result()
        self.assertFalse(self.b.state().get('halt'));self.assertFalse(self.b.state()['done'])

    def test_notification_cannot_resume_cancelled_work(self):
        self.spawn();self.cancel();self.call('UserPromptSubmit',prompt='<task-notification><task-id>child</task-id></task-notification>')
        self.assertIn('launch',self.b.state()['pending'])

    def test_integrity_halt_not_cleared_by_continue(self):
        self.spawn();self.cancel();s=self.b.state();self.b.halt(s,'sealed output changed')
        self.resume();self.assertEqual(self.b.state()['halt']['state'],'BLOCKED')

    def test_foreign_prompt_cannot_resume(self):
        self.spawn();self.cancel();self.call('UserPromptSubmit',session_id='foreign',prompt='continue')
        self.assertIn('launch',self.b.state()['pending'])

    def test_repeated_cancel_resume_keeps_one_identity(self):
        self.spawn()
        for i in range(3):
            self.cancel('launch' if i==0 else f'resume{i-1}');self.resume()
            self.assertEqual(self.send(f'resume{i}')['hookSpecificOutput']['permissionDecision'],'allow')
            self.result(f'resume{i}','SendMessage')
        self.assertEqual(self.b.state()['agents'],{'child':'first'})
        self.finish(self.envelope(),append=True);self.assertIn('first',self.b.state()['done'])

    def test_cancellation_after_child_sealed_keeps_seal(self):
        self.spawn();self.finish(self.envelope());seal=self.b.state()['done']['first']
        self.cancel(child=False);self.resume()
        self.assertFalse(self.b.state()['pending']);self.assertEqual(self.b.state()['done']['first'],seal)
        self.assertFalse(self.b.state().get('checkpoints'))

    def test_appended_internal_record_does_not_reuse_cancel_marker(self):
        self.spawn();self.cancel();self.resume();self.send();self.result('resume','SendMessage')
        p=self.parent.parent/'parent/subagents/agent-child.jsonl'
        with p.open('ab') as f:f.write(self.mod.encoded({'type':'attachment','internal':'EXCLUDED_CANARY'}))
        self.resume();self.assertIn('first',self.b.state()['continuing'])
        self.assertFalse(any(b'EXCLUDED_CANARY' in p.read_bytes() for p in (self.base/'.journal/objects').iterdir()))
