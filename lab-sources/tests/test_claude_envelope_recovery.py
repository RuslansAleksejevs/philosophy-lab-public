"""Delivery survives missing bookkeeping; provenance and real conflicts stay strict."""
import json,unittest
import test_claude_gradual as h

class EnvelopeRecoveryTests(unittest.TestCase):
    setUp=h.GradualTests.setUp
    tearDown=h.GradualTests.tearDown
    call=h.GradualTests.call
    row=h.GradualTests.row
    spawn=h.GradualTests.spawn
    envelope=h.GradualTests.envelope
    native=h.GradualTests.native
    finish=h.GradualTests.finish
    result=h.GradualTests.result

    def test_template_and_real_result_continue_without_choosing(self):
        self.spawn()
        text='```json\n'+self.envelope('checkpoint',{'report.md':'...'})+'\n```\nNow the actual file:\n'+self.envelope('checkpoint',{'report.md':'actual text'})
        self.finish(text);self.result()
        s=self.b.state();self.assertFalse(s.get('halt'));self.assertFalse(s['done'])
        self.assertFalse((self.base/'tasks/first/output/report.md').exists())
        self.assertIn('exactly one',s['checkpoints']['first']['correction'])
        r=self.resume();self.assertIn('without a template',r['hookSpecificOutput']['updatedInput']['message'])
        self.finish(self.envelope(files={'report.md':'actual text'}),append=True)
        self.assertIn('first',self.b.state()['done'])
        self.assertEqual((self.base/'tasks/first/output/report.md').read_text(),'actual text')

    def test_ambiguous_reply_retains_previously_saved_files(self):
        self.spawn();self.finish(self.envelope('checkpoint',{'notes.md':'preserved'}));self.result()
        self.resume();self.finish(self.envelope(files={'report.md':'one'})+'\n'+self.envelope(files={'report.md':'two'}),append=True)
        self.assertFalse(self.b.state().get('halt'))
        self.assertEqual((self.base/'tasks/first/output/notes.md').read_text(),'preserved')
        self.assertFalse((self.base/'tasks/first/output/report.md').exists())
        self.resume('again');self.finish(self.envelope(files={'report.md':'chosen by the same worker'}),append=True)
        self.assertIn('first',self.b.state()['done'])

    def test_duplicate_keys_are_correctable_without_guessing(self):
        self.spawn();text=self.envelope().replace('"files":','"status":"checkpoint","files":')
        self.finish(text);self.result();s=self.b.state()
        self.assertFalse(s.get('halt'));self.assertIn('Duplicate JSON key',s['checkpoints']['first']['correction'])
        self.resume();self.finish(self.envelope(),append=True);self.assertIn('first',self.b.state()['done'])

    def resume(self,key='resume'):
        r=self.call('PreToolUse',tool_name='SendMessage',tool_use_id=key,tool_input={'to':'child'})
        self.result(key,'SendMessage');return r

    def test_missing_status_saves_file_and_continues_same_worker(self):
        self.spawn()
        self.finish(json.dumps({'protocol':'claude-batch-result.v1','task_id':'first','files':{'sources.md':'exact sources'}}));self.result()
        self.assertFalse(self.b.state().get('halt'))
        self.assertEqual((self.base/'tasks/first/output/sources.md').read_text(),'exact sources')
        r=self.resume();self.assertIn('report.md',r['hookSpecificOutput']['updatedInput']['message'])
        self.finish(json.dumps({'files':{'report.md':'exact final'}}),append=True)
        self.assertIn('first',self.b.state()['done'])
        self.assertEqual(self.b.state()['agents'],{'child':'first'})
        events=[json.loads(p.read_text()) for p in (self.base/'.journal/events').glob('*.json')]
        self.assertTrue(any(e['kind']=='task.transport_status_derived' and e['payload']['status']=='complete' for e in events))

    def test_normalized_status_and_unknown_status_do_not_discard_files(self):
        self.spawn();self.finish(self.envelope('unfamiliar',{'notes.md':'kept'}));self.result()
        self.assertFalse(self.b.state().get('halt'))
        self.assertIn('first',self.b.state()['checkpoints'])
        self.resume();self.finish(self.envelope(' COMPLETE ',{'report.md':'done'}),append=True)
        self.assertIn('first',self.b.state()['done'])

    def test_explicit_block_never_inferred_complete(self):
        self.spawn();self.finish(self.envelope(' BLOCKED ',{'report.md':'all required bytes'},reason='Cannot finish reliably'));self.result()
        self.assertFalse(self.b.state()['done'])
        self.assertEqual(self.b.state()['halt']['reason'],'Cannot finish reliably')

    def test_supplied_transport_flags_cannot_forge_completion(self):
        self.spawn();self.finish(self.envelope('checkpoint',{'report.md':'present'},_transport={'status_source':'missing'}));self.result()
        self.assertFalse(self.b.state()['done'])
        self.assertIn('first',self.b.state()['checkpoints'])

    def test_wrong_identity_and_unsafe_files_still_rejected(self):
        for value in [{'protocol':'foreign','files':{'report.md':'bad'}},{'task_id':'other','files':{'report.md':'bad'}},{'files':{'../escape.md':'bad'}}]:
            with self.assertRaises(ValueError):self.b.result_envelope(json.dumps(value),self.b.tasks['first'])

    def test_invalid_files_shape_preserved_as_retry_not_global_halt(self):
        self.spawn();self.finish(json.dumps({'protocol':'claude-batch-result.v1','task_id':'first','files':['report.md']}));self.result()
        self.assertFalse(self.b.state().get('halt'))
        self.assertIn('mapping',self.b.state()['checkpoints']['first']['correction'])
        self.resume();self.finish(self.envelope(),append=True)
        self.assertIn('first',self.b.state()['done'])

    def test_partial_json_without_status_retains_complete_strings(self):
        self.spawn();text='{"protocol":"claude-batch-result.v1","task_id":"first","files":{"notes.md":"exact saved","report.md":"cut off'
        self.finish(text);self.result()
        self.assertFalse(self.b.state().get('halt'))
        self.assertEqual((self.base/'tasks/first/output/notes.md').read_text(),'exact saved')
        self.assertFalse((self.base/'tasks/first/output/report.md').exists())

    def test_resolved_length_instruction_disappears_before_reports(self):
        self.spawn();self.finish(self.envelope('checkpoint',{'final-001.md':'word '*6001}));self.result()
        self.assertIn('6000',self.b.state()['checkpoints']['first']['correction'])
        self.resume('r1');self.finish(self.envelope('checkpoint',{'final-002.md':'short'}),append=True)
        self.resume('r2');self.finish(self.envelope('checkpoint',{'final-selection-001.json':'{"file":"final-002.md"}'}),append=True)
        self.assertNotIn('correction',self.b.state()['checkpoints']['first'])
        r=self.resume('r3');self.assertNotIn('shorter',r['hookSpecificOutput']['updatedInput']['message'])
        self.finish(json.dumps({'files':{'report.md':'finished'}}),append=True)
        self.assertIn('first',self.b.state()['done'])

    def test_invalid_selection_is_correctable_and_old_bytes_survive(self):
        self.spawn();self.finish(self.envelope(files={'report.md':'done','final-001.md':'short','final-selection-001.json':'not json'}));self.result()
        self.assertFalse(self.b.state().get('halt'))
        self.resume();self.finish(self.envelope(files={'final-selection-002.json':'{"file":"final-001.md"}'}),append=True)
        self.assertIn('first',self.b.state()['done'])
        self.assertEqual((self.base/'tasks/first/output/final-selection-001.json').read_text(),'not json')

    def test_real_selected_final_alias_is_accepted_without_rewriting_record(self):
        self.spawn();selection=json.dumps({'selected_final':'final-002.md','superseded_finals':['final-001.md']})
        self.finish(self.envelope(files={'report.md':'done','final-001.md':'word '*6001,'final-002.md':'short','final-selection-001.json':selection}));self.result()
        self.assertIn('first',self.b.state()['done'])
        self.assertEqual((self.base/'tasks/first/output/final-selection-001.json').read_text(),selection)

    def test_conflicting_selection_aliases_require_worker_correction(self):
        self.spawn();self.finish(self.envelope(files={'report.md':'done','final-001.md':'old','final-002.md':'new','final-selection-001.json':'{"file":"final-001.md","selected_final":"final-002.md"}'}));self.result()
        self.assertFalse(self.b.state()['done'])
        self.assertFalse(self.b.state().get('halt'))
        self.assertIn('selection',self.b.state()['checkpoints']['first']['correction'])

    def test_four_complete_independent_chains_with_missing_metadata(self):
        import tempfile
        from pathlib import Path
        import claude_batch
        from test_claude_batch import ROOT,request
        req=request();req.update(output_transport='native_text',recovery_policy='gradual-v1');req['tasks']=[]
        for i in range(4):
            deps=[]
            for stage in ['author','critic','revision']:
                t=request()['tasks'][0];t.update(id=f'essay-{i}-{stage}',essay_id=f'essay-{i}',depends_on=list(deps),required_outputs=['report.md','sources.md','process.md'])
                req['tasks'].append(t);deps.append(t['id'])
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp).resolve()
            for name,data in claude_batch.compile_packet(ROOT,req).items():
                p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
            base=root/'batches/synthetic-batch';mod=claude_batch.runtime(base);b=mod.Batch(base)
            parent=root/'native/parent.jsonl';parent.parent.mkdir();parent.write_bytes(b'')
            common={'cwd':str(root),'session_id':'parent','transcript_path':str(parent)}
            def call(event,**kw):return b.handle({**common,'hook_event_name':event,**kw})
            call('UserPromptSubmit',prompt='Run synthetic complete-chain test')
            for i,t in enumerate(req['tasks']):
                tid=t['id'];aid=f'worker-{i}';(base/'tasks'/tid/'output').mkdir()
                call('PreToolUse',tool_name='Agent',tool_use_id=f'launch-{i}',tool_input={'subagent_type':b.tasks[tid]['agent_name']})
                call('SubagentStart',agent_id=aid,agent_type=b.tasks[tid]['agent_name'])
                child=parent.parent/'parent/subagents'/f'agent-{aid}.jsonl';child.parent.mkdir(parents=True,exist_ok=True)
                for j,name in enumerate(t['required_outputs']):
                    if j:
                        call('PreToolUse',tool_name='SendMessage',tool_use_id=f'resume-{i}-{j}',tool_input={'to':aid})
                        call('PostToolUse',tool_name='SendMessage',tool_use_id=f'resume-{i}-{j}',tool_response='resumed')
                    payload={'files':{name:f'Only synthetic task {tid}, file {name}. No research.'}}
                    if j==1:payload.update(task_id=tid,status=' COMPLETE ')
                    text=json.dumps(payload)
                    row={'type':'assistant','sessionId':'parent','cwd':str(root),'agentId':aid,'effort':'low','message':{'role':'assistant','id':f'm-{i}-{j}','model':'claude-opus-5','stop_reason':'end_turn','content':[{'type':'text','text':text}]}}
                    with child.open('ab') as f:f.write(mod.encoded(row))
                    call('SubagentStop',agent_id=aid,agent_transcript_path=str(child),last_assistant_message=text)
                    if j==0:call('PostToolUse',tool_name='Agent',tool_use_id=f'launch-{i}',tool_response='returned checkpoint')
                    self.assertFalse(b.state().get('halt'),b.state().get('halt'))
                self.assertIn(tid,b.state()['done'])
            self.assertEqual(b.summary(b.state())['state'],'COMPLETE')
            self.assertEqual(len(b.state()['agents']),12)
