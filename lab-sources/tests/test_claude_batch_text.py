"""Native text transport integration tests, using real lifecycle-shaped records."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock
from test_claude_batch import request, ROOT
import claude_batch as batch


class TextTransportTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.ws=Path(self.tmp.name).resolve()
        self.req=request();self.req['output_transport']='native_text'
        for name,data in batch.compile_packet(ROOT,self.req).items():
            p=self.ws/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
        self.base=self.ws/'batches/synthetic-batch'
        for t in self.req['tasks']:(self.base/'tasks'/t['id']/'output').mkdir()
        self.mod=batch.runtime(self.base);self.b=self.mod.Batch(self.base)
        self.parent=self.ws/'native/parent.jsonl';self.parent.parent.mkdir()
        self.h={'cwd':str(self.ws),'session_id':'parent','transcript_path':str(self.parent)}
        self.call('SessionStart',session_id='desktop-startup')
        self.call('UserPromptSubmit',prompt='Start technical packet')
        self.parent.write_bytes(self.mod.encoded(self.row('user','Start technical packet',child=False)))
    def tearDown(self):self.tmp.cleanup()
    def call(self,event,**kw):return self.b.handle({**self.h,'hook_event_name':event,**kw})
    def row(self,role,content,child=True,effort='low'):
        return {'type':role,'sessionId':'parent','cwd':str(self.ws),'effort':effort,**({'agentId':'child'} if child else {}),'message':{'role':role,'model':'claude-opus-5','content':content}}
    def spawn(self):
        self.call('PreToolUse',tool_name='Agent',tool_use_id='launch',tool_input={'subagent_type':self.b.tasks['first']['agent_name'],'prompt':'untrusted parent comment'})
        self.call('SubagentStart',agent_type=self.b.tasks['first']['agent_name'],agent_id='child')
    def envelope(self,status='complete',files=None,**kw):
        return json.dumps({'protocol':'claude-batch-result.v1','task_id':'first','status':status,'files':files if files is not None else {'report.md':'Exact\ntext — α\n'},**kw},ensure_ascii=False)
    def native(self,text,append=False,effort='low'):
        p=self.parent.parent/'parent/subagents/agent-child.jsonl';p.parent.mkdir(parents=True,exist_ok=True)
        data=self.mod.encoded(self.row('assistant',[{'type':'thinking','thinking':'HIDDEN_TEST_CANARY'},{'type':'text','text':text}],effort=effort))
        p.write_bytes((p.read_bytes() if append and p.exists() else b'')+data);return p
    def finish(self,text,append=False,effort='low'):
        p=self.native(text,append,effort)
        return self.call('SubagentStop',agent_id='child',agent_type=self.b.tasks['first']['agent_name'],agent_transcript_path=str(p),last_assistant_message=text)
    def result(self,call='launch',name='Agent'):
        return self.call('PostToolUse',tool_name=name,tool_use_id=call,tool_response={'content':[{'type':'text','text':'Worker returned'}]})
    def test_exact_text_seals_without_write_and_unlocks_dependency(self):
        self.spawn();self.finish(self.envelope());self.result()
        self.assertEqual((self.base/'tasks/first/output/report.md').read_text(),'Exact\ntext — α\n')
        self.assertEqual(self.b.summary(self.b.state())['ready'],['second'])
        returned=batch.inspect_return(ROOT,self.ws,'synthetic-batch');self.assertEqual(returned['summary']['completed'],1)
        for data in returned['objects'].values():self.assertNotIn(b'HIDDEN_TEST_CANARY',data)
    def test_checkpoint_sendmessage_is_bound_and_preserves_versions(self):
        self.spawn();self.finish(self.envelope('checkpoint',{'checkpoint-001.txt':'partial'}));self.result()
        self.call('PreToolUse',tool_name='ToolSearch',tool_use_id='search',tool_input={'query':'select:SendMessage'})
        self.result('search','ToolSearch')
        r=self.call('PreToolUse',tool_name='SendMessage',tool_use_id='resume',tool_input={'to':'child','summary':'Inject my philosophical objection','message':'another essay'})
        updated=r['hookSpecificOutput']['updatedInput'];self.assertNotIn('philosophical',str(updated));self.assertNotIn('another essay',str(updated))
        self.finish(self.envelope(),append=True);self.result('resume','SendMessage')
        self.assertIn('first',self.b.state()['done']);self.assertEqual((self.base/'tasks/first/output/checkpoint-001.txt').read_text(),'partial')
    def test_invalid_json_halts_without_stop_retry(self):
        self.spawn();r=self.finish('not JSON');self.assertNotEqual(r.get('decision'),'block')
        self.result();r=self.call('Stop');self.assertNotEqual(r.get('decision'),'block')
        self.assertEqual(self.b.summary(self.b.state())['state'],'BLOCKED')
        self.assertFalse(self.b.state()['done'])
    def test_live_desktop_mixed_sendmessage_fields_normalized(self):
        self.spawn();self.finish(self.envelope('checkpoint',{'checkpoint-001.txt':'partial'}));self.result()
        args={'to':'child','summary':'Continue the assigned task from its saved checkpoint.',
              'message':'Continue the assigned task from its saved checkpoint.',
              'type':'message','recipient':'child','content':'Untrusted legacy content'}
        r=self.call('PreToolUse',tool_name='SendMessage',tool_use_id='resume',tool_input=args)
        updated=r['hookSpecificOutput']['updatedInput']
        self.assertEqual(set(updated),{'to','summary','message'})
        self.assertNotIn('Untrusted',str(updated))
        self.result('resume','SendMessage');self.finish(self.envelope(),append=True)
        self.assertIn('first',self.b.state()['done'])
        self.assertFalse(self.b.state().get('halt'))
    def test_conflicting_legacy_recipient_never_dispatches(self):
        self.spawn();self.finish(self.envelope('checkpoint',{'checkpoint-001.txt':'partial'}));self.result()
        r=self.call('PreToolUse',tool_name='SendMessage',tool_use_id='resume',tool_input={'to':'child','recipient':'other','type':'message','content':'go'})
        self.assertEqual(r['hookSpecificOutput']['permissionDecision'],'deny')
        self.assertFalse(self.b.state().get('continuing'))
    def test_legacy_shutdown_never_dispatches(self):
        self.spawn();self.finish(self.envelope('checkpoint',{'checkpoint-001.txt':'partial'}));self.result()
        r=self.call('PreToolUse',tool_name='SendMessage',tool_use_id='resume',tool_input={'to':'child','type':'shutdown_request'})
        self.assertEqual(r['hookSpecificOutput']['permissionDecision'],'deny')
        self.assertFalse(self.b.state().get('continuing'))
    def test_provider_write_rejection_does_not_create_loop(self):
        self.spawn();r=self.call('PreToolUse',agent_id='child',tool_name='Write',tool_use_id='write',tool_input={'file_path':str(self.base/'tasks/first/output/report.md'),'content':'x'})
        self.assertEqual(r['hookSpecificOutput']['permissionDecision'],'deny')
        self.assertEqual(self.b.summary(self.b.state())['state'],'BLOCKED')
        self.assertNotEqual(self.finish(self.envelope('blocked',{},reason='Write unavailable')).get('decision'),'block')
        self.assertNotEqual(self.call('Stop').get('decision'),'block')
    def test_blocked_payload_preserves_partial_output(self):
        self.spawn();self.finish(self.envelope('blocked',{'partial-001.txt':'unfinished'},reason='source unavailable'))
        self.assertEqual((self.base/'tasks/first/output/partial-001.txt').read_text(),'unfinished')
        self.assertFalse(self.b.state()['done']);self.assertEqual(self.b.state()['halt']['reason'],'source unavailable')
    def test_unsupported_discovery_stops_before_another_worker(self):
        self.spawn();self.finish(self.envelope('checkpoint',{'checkpoint-001.txt':'partial'}));self.result()
        self.call('PreToolUse',tool_name='ToolSearch',tool_use_id='search',tool_input={'query':'select:SendMessage'})
        self.call('PostToolUseFailure',tool_name='ToolSearch',tool_use_id='search',error='ToolSearch unavailable')
        r=self.call('PreToolUse',tool_name='Agent',tool_use_id='again',tool_input={'subagent_type':self.b.tasks['second']['agent_name'],'prompt':'go'})
        self.assertEqual(r['hookSpecificOutput']['permissionDecision'],'deny')
    def test_model_effort_mismatch_preserved_but_not_sealed(self):
        self.spawn();self.finish(self.envelope(),effort='high')
        self.assertIn('model/effort',self.b.state()['halt']['reason']);self.assertFalse(self.b.state()['done'])
    def test_foreign_session_cannot_halt_existing_batch(self):
        r=self.call('UserPromptSubmit',session_id='foreign',prompt='steal')
        self.assertIn('same dispatcher',r['reason']);self.assertFalse(self.b.state().get('halt'))
    def test_missing_subagentstop_is_not_success(self):
        self.spawn();self.result();self.assertIn('without a sealed',self.b.state()['halt']['reason'])
    def test_path_traversal_and_duplicate_json_rejected(self):
        for text in [self.envelope(files={'../escape.md':'bad'}),self.envelope().replace('"files":','"status":"complete","files":')]:
            with self.assertRaises(ValueError):self.b.result_envelope(text,self.b.tasks['first'])
    def test_replay_after_materialization_crash_only_accepts_identical_bytes(self):
        self.spawn();text=self.envelope();p=self.native(text)
        h={**self.h,'agent_id':'child','agent_transcript_path':str(p),'last_assistant_message':text}
        original=self.mod.event
        def crash(base,kind,payload):
            if kind=='task.sealed':raise OSError('simulated crash before seal')
            return original(base,kind,payload)
        with mock.patch.object(self.mod,'event',side_effect=crash):
            with self.assertRaises(OSError):self.b.accept_text(self.b.tasks['first'],self.b.state(),h)
        self.assertTrue((self.base/'tasks/first/output/report.md').exists())
        self.b.accept_text(self.b.tasks['first'],self.b.state(),h)
        self.assertIn('first',self.b.state()['done'])
    def test_provider_failure_is_interrupted_not_complete(self):
        self.spawn();r=self.call('StopFailure',error='rate limit')
        self.assertEqual(self.b.summary(self.b.state())['state'],'INTERRUPTED');self.assertNotEqual(r.get('decision'),'block')
    def test_final_length_failure_preserves_content_without_loop(self):
        self.spawn();self.finish(self.envelope(files={'report.md':'ok','final-001.md':'word '*6001}))
        self.assertTrue((self.base/'tasks/first/output/final-001.md').exists());self.assertIn('6000',self.b.state()['halt']['reason'])
    def test_duplicate_stop_and_return_are_idempotent_for_sealed_task(self):
        self.spawn();text=self.envelope();self.finish(text);receipt=self.b.state()['done']['first']['receipt']
        self.finish(text);self.assertEqual(self.b.state()['done']['first']['receipt'],receipt)
    def test_delayed_native_flush_is_reconciled_on_parent_result(self):
        self.spawn();text=self.envelope();p=self.parent.parent/'parent/subagents/agent-child.jsonl'
        r=self.call('SubagentStop',agent_id='child',agent_type=self.b.tasks['first']['agent_name'],agent_transcript_path=str(p),last_assistant_message=text)
        self.assertIn('awaiting',r['systemMessage']);self.assertFalse(self.b.state().get('halt'))
        self.assertIn('first',self.b.state()['staged'])
        self.native(text);self.result();self.assertIn('first',self.b.state()['done'])
    def test_async_continuation_waits_without_repeat_or_stop_loop(self):
        self.spawn();self.finish(self.envelope('checkpoint',{'checkpoint-001.txt':'partial'}));self.result()
        self.call('PreToolUse',tool_name='SendMessage',tool_use_id='resume',tool_input={'to':'child','summary':'continue'})
        self.result('resume','SendMessage')
        r=self.call('Stop',last_assistant_message='Waiting for the registered worker.')
        self.assertNotEqual(r.get('decision'),'block');self.assertFalse(self.b.state().get('halt'))
        self.assertIn('first',self.b.state()['continuing'])
        self.finish(self.envelope(),append=True)
        self.assertFalse(self.b.state()['continuing']);self.assertIn('first',self.b.state()['done'])
    def test_background_start_after_sendmessage_receipt_keeps_same_agent(self):
        self.spawn();self.finish(self.envelope('checkpoint',{'checkpoint-001.txt':'partial'}));self.result()
        self.call('PreToolUse',tool_name='SendMessage',tool_use_id='resume',tool_input={'to':'child','summary':'continue'})
        self.result('resume','SendMessage')
        self.call('SubagentStart',agent_type=self.b.tasks['first']['agent_name'],agent_id='child')
        self.assertFalse(self.b.state().get('halt'))
        self.finish(self.envelope(),append=True);self.assertIn('first',self.b.state()['done'])
    def test_background_start_cannot_replace_registered_agent(self):
        self.spawn();self.finish(self.envelope('checkpoint',{'checkpoint-001.txt':'partial'}));self.result()
        self.call('PreToolUse',tool_name='SendMessage',tool_use_id='resume',tool_input={'to':'child','summary':'continue'})
        self.result('resume','SendMessage')
        self.call('SubagentStart',agent_type=self.b.tasks['first']['agent_name'],agent_id='foreign')
        self.assertEqual(self.b.state()['agents'],{'child':'first'})
        self.assertFalse(self.b.state().get('halt'))
    def test_late_unknown_worker_cannot_turn_complete_into_blocked(self):
        self.b.tasks.pop('second')
        self.spawn();self.finish(self.envelope());self.result()
        before=self.b.state()
        for kind in ('SubagentStop','Stop','StopFailure','PostToolUse','SubagentStart'):
            self.call(kind,agent_id='unrelated',agent_type='unrelated',last_assistant_message='UNRELATED_PRIVATE_CANARY')
        self.assertEqual(self.b.state(),before)
        self.assertEqual(self.b.summary(self.b.state())['state'],'COMPLETE')
        for p in (self.base/'.journal/objects').iterdir():self.assertNotIn(b'UNRELATED_PRIVATE_CANARY',p.read_bytes())
    def test_unknown_worker_tool_is_denied_without_halting_owner(self):
        before=self.b.state()
        r=self.call('PreToolUse',agent_id='unrelated',tool_name='Read',tool_use_id='alien',tool_input={'file_path':'BATCH.json'})
        self.assertEqual(r['hookSpecificOutput']['permissionDecision'],'deny')
        self.assertEqual(before,self.b.state())
    def test_compatible_extra_fields_are_removed_before_dispatch(self):
        r=self.call('PreToolUse',tool_name='Agent',tool_use_id='launch',tool_input={'subagent_type':self.b.tasks['first']['agent_name'],'prompt':'anything','display_color':'blue','model':None})
        self.assertEqual(set(r['hookSpecificOutput']['updatedInput']),{'subagent_type','prompt','description'})
    def test_legacy_recipient_and_extra_metadata_continue_same_worker(self):
        self.spawn();self.finish(self.envelope('checkpoint',{'checkpoint-001.txt':'partial'}));self.result()
        r=self.call('PreToolUse',tool_name='SendMessage',tool_use_id='resume',tool_input={'recipient':'child','content':'parent prose','trace_label':'new-ui-field'})
        self.assertEqual(r['hookSpecificOutput']['updatedInput']['to'],'child')
        self.assertNotIn('trace_label',r['hookSpecificOutput']['updatedInput'])
        self.result('resume','SendMessage');self.finish(self.envelope(),append=True)
        self.assertIn('first',self.b.state()['done'])
    def test_parallel_reads_have_separate_receipts_before_launch(self):
        for call,path in [('r1',self.ws/'BATCH.json'),('r2',self.base/'STATUS.json')]:
            r=self.call('PreToolUse',tool_name='Read',tool_use_id=call,tool_input={'file_path':str(path)})
            self.assertEqual(r['hookSpecificOutput']['permissionDecision'],'allow')
        self.result('r2','Read');self.result('r1','Read');self.spawn()
        self.assertFalse(self.b.state().get('halt'))
    def test_result_metadata_does_not_reject_valid_files(self):
        self.spawn();self.finish(self.envelope(note='A harmless extra result field'));self.result()
        self.assertIn('first',self.b.state()['done'])
    def test_live_checkpoint_with_introductory_sentence(self):
        self.spawn()
        self.finish('First invocation: returning the checkpoint.\n\n'+self.envelope('checkpoint',{'checkpoint-001.txt':'amber\n'}))
        self.result();self.assertIn('first',self.b.state()['checkpoints'])
        self.call('PreToolUse',tool_name='SendMessage',tool_use_id='resume',tool_input={'to':'child'})
        self.result('resume','SendMessage')
        self.finish('Done.\n```json\n'+self.envelope(files={'report.md':'A {brace} and \\"quote\\"\n'})+'\n```\nSaved above.',append=True)
        self.assertIn('first',self.b.state()['done'])
        self.assertEqual((self.base/'tasks/first/output/report.md').read_text(),'A {brace} and \\"quote\\"\n')
    def test_two_result_objects_are_not_silently_selected(self):
        with self.assertRaisesRegex(ValueError,'unambiguous'):
            self.b.result_envelope(self.envelope()+self.envelope(files={'report.md':'different'}),self.b.tasks['first'])
    def test_nested_json_in_file_does_not_become_another_result(self):
        content=self.envelope(files={'report.md':'inner'})
        result=self.b.result_envelope('Result:\n'+self.envelope(files={'report.md':content}),self.b.tasks['first'])
        self.assertEqual(result['files']['report.md'],content)
    def test_completion_notification_is_not_logged_as_human_prompt(self):
        self.spawn()
        self.call('UserPromptSubmit',prompt='<task-notification><task-id>child</task-id>completed</task-notification>')
        kinds=[json.loads(p.read_text())['kind'] for p in (self.base/'.journal/events').glob('*.json')]
        self.assertEqual(kinds.count('human.prompt'),1)
        self.assertEqual(kinds.count('provider.notification'),1)
    def test_unrelated_notification_body_is_not_collected(self):
        before=self.b.state()
        self.call('UserPromptSubmit',prompt='<task-notification><task-id>unrelated</task-id>PRIVATE_OTHER_TASK</task-notification>')
        self.assertEqual(self.b.state(),before)
        for p in (self.base/'.journal/objects').iterdir():self.assertNotIn(b'PRIVATE_OTHER_TASK',p.read_bytes())
    def test_unavailable_source_is_recorded_without_global_halt(self):
        self.spawn();self.b.tasks['first']['public_web']=True
        self.call('PreToolUse',agent_id='child',tool_name='WebFetch',tool_use_id='web',tool_input={'url':'https://example.org/missing.pdf','prompt':'Read source'})
        self.call('PostToolUseFailure',agent_id='child',tool_name='WebFetch',tool_use_id='web',error='HTTP 404')
        self.assertFalse(self.b.state().get('halt'))
        self.assertNotIn('web',self.b.state()['pending'])
        data=b''.join(p.read_bytes() for p in (self.base/'.journal/objects').iterdir())
        self.assertIn(b'HTTP 404',data)
    def test_result_changed_between_hook_and_native_never_seals(self):
        self.spawn();p=self.native(self.envelope(files={'report.md':'different'}))
        self.call('SubagentStop',agent_id='child',agent_type=self.b.tasks['first']['agent_name'],agent_transcript_path=str(p),last_assistant_message=self.envelope())
        self.assertFalse(self.b.state()['done']);self.result()
        self.assertEqual(self.b.summary(self.b.state())['state'],'BLOCKED')
    def test_dispatcher_final_hook_text_preserved_even_if_native_lags(self):
        self.call('Stop',last_assistant_message='Unique last visible message')
        data=b''.join(p.read_bytes() for p in (self.base/'.journal/objects').iterdir())
        self.assertIn(b'Unique last visible message',data)
    def test_background_final_flush_reconciles_on_parent_status_read(self):
        self.spawn();self.finish(self.envelope('checkpoint',{'checkpoint-001.txt':'partial'}));self.result()
        self.call('PreToolUse',tool_name='SendMessage',tool_use_id='resume',tool_input={'to':'child','summary':'continue'});self.result('resume','SendMessage')
        p=self.parent.parent/'parent/subagents/agent-child.jsonl';final=self.envelope()
        self.call('SubagentStop',agent_id='child',agent_transcript_path=str(p),last_assistant_message=final)
        self.assertIn('first',self.b.state()['staged']);self.native(final,append=True)
        self.call('PreToolUse',tool_name='Read',tool_use_id='status',tool_input={'file_path':str(self.base/'STATUS.json')})
        self.assertIn('first',self.b.state()['done']);self.assertFalse(self.b.state()['continuing'])
    def test_repeated_checkpoint_callback_does_not_consume_retry_budget(self):
        self.spawn();text=self.envelope('checkpoint',{'checkpoint-001.txt':'partial'});self.finish(text)
        count=self.b.state()['checkpoints']['first']['count'];self.finish(text)
        self.assertEqual(self.b.state()['checkpoints']['first']['count'],count)

class RecoveredRateLimitTests(TextTransportTests):
    def test_synthetic_error_preserved_without_inventing_effort(self):
        self.spawn()
        p=self.native(self.envelope())
        rows=p.read_bytes().splitlines();error=self.row('assistant',[{'type':'text','text':'Session limit reached'}])
        error.update(isApiErrorMessage=True,error='rate_limit');error.pop('effort');error['message']['model']='<synthetic>'
        p.write_bytes(self.mod.encoded(error)+b'\n'.join(rows)+b'\n')
        self.call('SubagentStop',agent_id='child',agent_transcript_path=str(p),last_assistant_message=self.envelope())
        self.assertIn('first',self.b.state()['done'])
        seals=[json.loads(x.read_text()) for x in (self.base/'.journal/events').glob('*.json')]
        seal=next(e for e in seals if e['kind']=='task.sealed')
        evidence=json.loads((self.base/'.journal/objects'/seal['payload']['native_object']).read_text())
        self.assertEqual(evidence['provider_errors'][0]['error'],'rate_limit')
        self.assertTrue(all(x['effort']=='low' for x in evidence['models']))

class PartialEnvelopeTests(TextTransportTests):
    def test_incomplete_last_file_preserves_only_complete_strings(self):
        text='{"protocol":"claude-batch-result.v1","task_id":"first","status":"complete","files":{"report.md":"Exact\\ntext","process.md":"unfinished'
        r=self.b.result_envelope(text,self.b.tasks['first'])
        self.assertEqual(r['status'],'checkpoint');self.assertEqual(r['files'],{'report.md':'Exact\ntext'})
        self.spawn();self.finish(text);self.result()
        self.assertNotIn('first',self.b.state()['done'])
        self.assertEqual((self.base/'tasks/first/output/report.md').read_text(),'Exact\ntext')
        self.call('PreToolUse',tool_name='SendMessage',tool_use_id='resume',tool_input={'to':'child'})
        self.finish(self.envelope(files={'process.md':'Finished'}),append=True)
        self.assertIn('first',self.b.state()['done'])
    def test_no_complete_file_is_not_salvageable(self):
        text='{"protocol":"claude-batch-result.v1","task_id":"first","status":"complete","files":{"report.md":"unfinished'
        with self.assertRaisesRegex(ValueError,'unambiguous'):self.b.result_envelope(text,self.b.tasks['first'])
