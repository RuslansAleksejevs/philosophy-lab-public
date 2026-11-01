"""Synthetic003→map→002→group map; real lineage API, in-memory writer only."""
from pathlib import Path
import copy
import json
import tempfile
import unittest
from unittest.mock import patch
import resolver_repair as r
import runner_repair as transport
import archive_repair as archiver
import resolver_map_repair as maps
import validate_repair_v5 as validator
import closure_repair_v4 as closure
from test_launch_repair import RepairFixture
import test_capacity_v2 as oldtests


class MapFixture(RepairFixture):
    def __init__(self,root):
        super().__init__(root)
        for name in ('archive_repair.py','resolver_map_repair.py','finish_replacements.py','test_map_repair.py','MAP_TESTS.json'):
            self.file('capacity-launch-repair-001/'+name,b'SYNTHETIC explicit map code/tests')
        self.accept_repair();(self.run/'STOP.json').unlink()

    def resolution_path(self):return self.lane/'ACCEPTED_ATTEMPTS_RECEIPT.json'

    def fake_run(self,jid):
        ready=r.load_ready(self.root,self.run,self.lane/'REPAIR_RECEIPT.json',self.archive.events(),self.archive.get,jid)
        job=ready['job'];sid='fresh-repair-synthetic-'+jid;prompt=(self.root/job['prompt_file']).read_text()
        answer={'review_id':jid,'manuscript_id':job['manuscript_id'],'profile_id':job['profile_id'],'read_complete':True,'recommendation':'consider',
                'reason_ru':['Первая искусственная строка проверяет технический транспорт.','Вторая искусственная строка сохраняет структуру ответа.']}
        h=oldtests.transport_helpers
        rows=[h.line('session_meta',{'id':sid,'cwd':str(self.root)}),h.line('turn_context',r.SETTINGS),h.message('user',prompt),h.message('assistant',json.dumps(answer),'final')]
        source=self.root/(jid+'-native-synthetic.jsonl');source.write_bytes(b''.join(rows));self.sources[jid]=source
        self.proofs[jid]=r.runner.native_records(rows,sid,prompt,job,self.root)
        process=h.FakeProcess([{'type':'thread.started','thread_id':sid},{'type':'turn.started'},{'type':'turn.completed','usage':{'input_tokens':10,'output_tokens':10}}])
        def popen(argv,**kwargs):
            assert kwargs['env']==r.runner.sanitized_env()
            Path(argv[argv.index('--output-last-message')+1]).write_text(json.dumps(answer));return process
        worker=transport.ReplacementDispatcher(self.run,self.root,ready)
        for sid in transport.prerequisites(self.root,self.run,ready,self.archive.events(),self.archive.get):worker.register_session(sid)
        with patch.object(r.runner.shutil,'which',return_value='/synthetic/codex'),patch.object(r.runner.subprocess,'Popen',side_effect=popen),patch.object(transport,'inspect_native',return_value=self.proofs[jid]):
            result=worker.run_one(job)
        assert process.stdin.saved==prompt
        return result

    def accept_physical(self,jid):
        selected=[{**x,'phase':x.get('phase'),'mode':'exact-visible-fragment','adapter_exclusion':'Synthetic only','tokens':[json.dumps(x['text']).encode()]} for x in self.proofs[jid][1]]
        with patch.object(r.runner,'inspect_native',return_value=self.proofs[jid]),patch.object(archiver,'resolve_session',return_value=self.sources[jid]),patch.object(archiver,'native_selection',return_value=selected):
            with self.archive.writer() as w:
                result=archiver.accept_with_writer(self.root,self.run,self.lane/'REPAIR_RECEIPT.json',jid,w)
        if result['status']=='REVIEW_ARCHIVED':self.accepted[jid]=result
        return result

    def finish_repair(self):
        for jid in r.JOBS:self.fake_run(jid);self.accept_physical(jid)
        with self.archive.writer() as w:return maps.complete_with_writer(self.root,self.run,w)


class MapRepairTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='TEST_ONLY-map-repair-');self.addCleanup(self.tmp.cleanup)
        self.f=MapFixture(self.tmp.name)

    def test_sequential_maps_keep110_and_all3_failures(self):
        f=self.f;preserved={str(p):p.read_bytes() for jid,n in [('M12-N2',1),('M12-N2',2),('M13-N2',1)] for p in (f.run/'results'/jid/f'attempt-{n:03}').iterdir()}
        result=f.finish_repair()
        resolution=maps.load_resolution(f.root,f.run,f.resolution_path(),f.archive.events(),f.archive.get)
        self.assertEqual(result['status'],'CAPACITY_REPLACEMENTS_COMPLETE_ARCHIVED')
        self.assertEqual({j:x['accepted_attempt']['number'] for j,x in resolution['exceptions'].items()},r.TARGETS)
        self.assertNotIn('local_launch_failure',resolution['exceptions']['M13-N2'])
        records=f.archive.events();reviews=[e for e in records if e['kind']=='research.selection.review.completed']
        self.assertEqual(len(reviews),110)
        self.assertEqual(len({e['session_id'] for e in reviews}),110)
        group=next(e for e in records if e['id']==result['event_id'])
        self.assertEqual([group['payload'][k] for k in ('preserved_failed_attempts','preserved_capacity_failures','preserved_local_launch_failures','failed_provider_review_slots')],[3,2,1,2])
        for name,data in preserved.items():self.assertEqual(Path(name).read_bytes(),data)
        before=len(records)
        f.accept_physical('M12-N2');f.accept_physical('M13-N2')
        with f.archive.writer() as w:self.assertEqual(maps.complete_with_writer(f.root,f.run,w),result)
        self.assertEqual(len(f.archive.records),before)

    def test_M13_waits_for_actual_M12_map(self):
        f=self.f
        with self.assertRaises((ValueError,FileNotFoundError)):
            f.fake_run('M13-N2')
        self.assertFalse((f.run/'results/M13-N2/attempt-002').exists())

    def test_changed_map_execution_file_blocks_dependent_resolution(self):
        f=self.f;f.finish_repair()
        (f.lane/'resolver_map_repair.py').write_bytes(b'changed synthetic code')
        with self.assertRaises(ValueError):maps.load_resolution(f.root,f.run,f.resolution_path(),f.archive.events(),f.archive.get)

    def test_extra_physical_attempt_cannot_be_hidden(self):
        f=self.f;f.finish_repair();(f.run/'results/M12-N2/attempt-004').mkdir()
        with self.assertRaisesRegex(ValueError,'Unexpected physical attempt'):maps.load_resolution(f.root,f.run,f.resolution_path(),f.archive.events(),f.archive.get)

    def test_full110_validator_then_finite_closure_with_timestamp_replay(self):
        f=self.f;f.finish_repair();plan=f.final_plan()
        report=validator.validate(f.root,f.run,plan,f.archive.events(),f.archive.get,map_receipt=f.resolution_path())
        self.assertEqual((report['individual_reviews'],report['preserved_failed_attempts'],report['protected_unchanged']),(110,3,42))
        for event in f.events:event.setdefault('timestamp','2026-10-18T10:00:00+00:00')
        first=f.event('operation.started',payload={'protocol':'philosophy-round.v1','purpose':'research'})
        first.update(operation_id='synthetic-operation',attempt_id='synthetic-operation',timestamp='2026-10-18T09:00:00+00:00')
        f.events.remove(first);f.events.insert(0,first)
        f.start['run_start_event']=first['id'];f.file('START_RECEIPT.json',f.start)
        summary=f.file('closure-input/SUMMARY.json',{k:('CONTINUE' if k=='outcome' else 'Synthetic finite scope only.') for k in closure.SUMMARY_FIELDS})
        stages={stage:{'files':[f.file('closure-input/'+stage+'.txt',('Synthetic '+stage).encode())],'evidence_event_ids':[x['event_id'] for x in f.reviews]} for stage in closure.STAGES[1:]}
        code=f.file('capacity-launch-repair-001/validate_repair_v5.py',Path(validator.__file__).read_bytes())
        req={'schema':'selection-closure-request.v1','run_id':f.run.name,'session_id':first['session_id'],'plan_input':f.file('closure-input/PLAN_INPUT.json',plan),
             'stages':stages,'selection_gate_event_ids':[r.strict(f.resolution_path().read_bytes())['event_id']],
             'checkpoint':{'summary':summary,'coverage_event_ids':[f.gap['id']]},'coordinator_configuration':{'requested':'Synthetic','observed':'Synthetic'},
             'outputs':{k:str((f.run/name).relative_to(f.root)) for k,name in [('final_plan','closure/FINAL_PLAN.json'),('validation_report','closure/REPORT.json'),('final_receipt','FINAL_RECEIPT.json')]},
             'export_files':[r.descriptor(f.root,f.lane/'ACCEPTED_ATTEMPTS.v3.json')],'export_generated':['final_plan','validation_report','closure_request'],
             'pending_goal_steps':['project_state_update','private_github_update','collector_restore'],
             'validator':{'name':'launch-repair-v5','code':code,'map_receipt':r.descriptor(f.root,f.resolution_path())}}
        ref=f.file('closure-input/REQUEST.json',req);f.archive.records=copy.deepcopy(f.events);f.archive.objects=dict(f.objects)
        def call():return closure.execute(f.root,f.run,f.root/ref['path'],f.archive,validator_api=validator.validate,map_receipt=f.resolution_path(),allow_checkpoint_derived_updates=True,lineage_api=oldtests.essay_lineage,checkpoint_api=oldtests.checkpoint_api)
        with patch.object(closure,'HERE',f.lane):
            receipt=call();count=len(f.archive.records);self.assertEqual(call(),receipt)
        self.assertEqual(len(f.archive.records),count)
        self.assertFalse(receipt['goal_completion_claimed'])
        self.assertEqual(receipt['pending_goal_steps'],req['pending_goal_steps'])
        event=next(e for e in f.archive.records if e['id']==receipt['event_id'])
        self.assertEqual(receipt['completed_at'],event['timestamp'])
        self.assertEqual(len(receipt['failed_attempt_event_ids']),3)


if __name__=='__main__':unittest.main(verbosity=2)
