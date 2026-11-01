"""Targeted synthetic local-init/003 tests. All provider calls and native reads mocked."""
from pathlib import Path
import copy
import json
import tempfile
import unittest
from unittest.mock import patch
import resolver_repair as r
import runner_repair as transport
import ready_repair as ready
import test_capacity_v2 as fixtures


class RepairFixture(fixtures.TwoFixture):
    def __init__(self,root):
        super().__init__(root);self.prepare()
        self.events=self.archive.records;self.objects=self.archive.objects
        self.lane=self.run/'capacity-launch-repair-001';self.lane.mkdir()
        self.file('AUTHORIZATION.json',{'session_id':'fixture-coordinator'})
        old=r.prior.load_ready(self.root,self.run,self.ready_path(r.JOBS[0]),self.events,self.archive.get)
        job=old['job'];attempt=self.run/'results/M12-N2/attempt-002'
        argv=r.runner.command(job,attempt,self.root,executable='/synthetic/codex')
        launch={'job_id':job['id'],'physical_attempt':2,'prompt_sha256':job['prompt_sha256'],'schema_sha256':job['schema_sha256'],
                'requested_model':job['model'],'requested_effort':job['effort'],'requested_service_tier':'default',
                'replacement_ready_event_id':old['ready_event_id'],'failed_attempt_event_id':old['failed_attempt']['event_id'],
                'argv':argv,'argv_sha256':r.sha(json.dumps(argv,separators=(',',':')).encode())}
        failure={**launch,'status':r.runner.FAILED,'session_id':None,'automatic_retry':False,
                 'process_state':{'process_stopped':True,'stderr_drained':True,'exit_code':1,'forced_kill':False}}
        for name,value in [('launch.json',launch),('failure.json',failure),('stderr.json',{'lines':r.EXPECTED_STDERR,'exit_code':1}),('visible-events.jsonl',b'')]:
            self.file('results/M12-N2/attempt-002/'+name,value)
        proof=r.inspect_local_failure(self.root,self.run,job)
        inspection=self.file('capacity-launch-repair-001/INSPECTION.json',{'synthetic':True,'provider_model_calls':'unknown'})
        event=self.event('research.selection.local_launch_failure',parents=[old['input_event_id'],old['ready_event_id'],old['failed_attempt']['event_id']],outputs=[x['sha256'] for x in proof['files']+[inspection]],payload={'status':'LOCAL_LAUNCH_FAILURE_PRESERVED','logical_job_id':job['id'],'physical_attempt':2,'session_id':None})
        stop={'job_id':job['id'],'reason':'Unclassified CLI exit or missing identity','automatic_retry':False}
        self.file('STOP.json',stop)
        preserved=self.file('capacity-launch-repair-001/STOP_ORIGINAL.json',stop)
        code=[self.file('capacity-launch-repair-001/'+name,b'SYNTHETIC launch code/test') for name in ('resolver_repair.py','runner_repair.py','ready_repair.py','test_launch_repair.py','LAUNCH_TESTS.json')]
        self.repair_plan={'schema':'selection-local-launch-repair.v1','target_attempts':r.TARGETS,'automatic_retry':False,
              'original_ready_receipts':{jid:r.descriptor(self.root,self.ready_path(jid)) for jid in r.JOBS},
              'local_launch_failure':{'event_id':event['id'],'files':proof['files'],'inspection':inspection},'preserved_stop':preserved}
        self.repair_request={'schema':'selection-local-launch-repair-request.v1','session_id':'fixture-coordinator','plan':self.repair_plan,'files':code+[inspection,preserved]}
        self.repair_ref=self.file('capacity-launch-repair-001/REQUEST.json',self.repair_request)

    def accept_repair(self):
        with self.archive.writer() as w:
            return ready.accept_with_writer(self.root,self.run,self.repair_ref,w)


class LaunchRepairTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='TEST_ONLY-launch-repair-')
        self.addCleanup(self.temp.cleanup)
        self.f=RepairFixture(self.temp.name)

    def test_ready_routes003_002_and_keeps_old_plans(self):
        f=self.f;before={j:f.ready_path(j).read_bytes() for j in r.JOBS}
        out=f.accept_repair();self.assertEqual(out['status'],'LOCAL_LAUNCH_REPAIR_ACCEPTED_BOUNDED')
        for jid,number in r.TARGETS.items():
            value=r.load_ready(f.root,f.run,f.lane/'REPAIR_RECEIPT.json',f.archive.events(),f.archive.get,jid)
            self.assertEqual(value['physical_attempt'],number)
            self.assertEqual(value['attempt'].name,'attempt-%03d'%number)
            self.assertEqual(f.ready_path(jid).read_bytes(),before[jid])

    def test_nonempty_stdout_or_sid_rejected(self):
        f=self.f;p=f.run/'results/M12-N2/attempt-002/visible-events.jsonl'
        p.write_bytes(b'{"type":"thread.started"}\n')
        with self.assertRaisesRegex(ValueError,'visible session'):r.inspect_local_failure(f.root,f.run,f.byid[r.JOBS[0]])
        p.write_bytes(b'');p=p.with_name('failure.json');d=r.strict(p.read_bytes());d['session_id']='TEST_ONLY_UNEXPECTED';p.write_bytes(r.encode(d))
        with self.assertRaisesRegex(ValueError,'no-session'):r.inspect_local_failure(f.root,f.run,f.byid[r.JOBS[0]])

    def test_other_error_or_live_process_rejected(self):
        f=self.f;p=f.run/'results/M12-N2/attempt-002/stderr.json';old=p.read_bytes();p.write_bytes(r.encode({'lines':['different error'],'exit_code':1}))
        with self.assertRaisesRegex(ValueError,'exact app-server'):r.inspect_local_failure(f.root,f.run,f.byid[r.JOBS[0]])
        p.write_bytes(old);p=p.with_name('failure.json');d=r.strict(p.read_bytes());d['process_state']['process_stopped']=False;p.write_bytes(r.encode(d))
        with self.assertRaisesRegex(ValueError,'incomplete'):r.inspect_local_failure(f.root,f.run,f.byid[r.JOBS[0]])

    def test_changed_config_and_any_final_rejected(self):
        f=self.f;p=f.run/'results/M12-N2/attempt-002/launch.json';old=p.read_bytes();d=r.strict(old);d['requested_effort']='high';p.write_bytes(r.encode(d))
        with self.assertRaisesRegex(ValueError,'inputs/config'):r.inspect_local_failure(f.root,f.run,f.byid[r.JOBS[0]])
        p.write_bytes(old);p.with_name('final.txt').write_text('TEST_ONLY')
        with self.assertRaisesRegex(ValueError,'extra/output'):r.inspect_local_failure(f.root,f.run,f.byid[r.JOBS[0]])

    def test_unaccepted_failure_blocks_ready_before_append(self):
        f=self.f;eid=f.repair_plan['local_launch_failure']['event_id'];f.archive.records[:]=[e for e in f.archive.records if e['id']!=eid]
        count=len(f.archive.records)
        with self.assertRaisesRegex(ValueError,'Missing actual event'):f.accept_repair()
        self.assertEqual(len(f.archive.records),count)
        self.assertFalse((f.lane/'PLAN.json').exists())

    def test_fake_launch003_exact_prompt_and_no_rerun(self):
        f=self.f;f.accept_repair();(f.run/'STOP.json').unlink()
        value=r.load_ready(f.root,f.run,f.lane/'REPAIR_RECEIPT.json',f.archive.events(),f.archive.get,r.JOBS[0])
        job=value['job'];prompt=(f.root/job['prompt_file']).read_text();sid='TEST_ONLY_FRESH_LOCAL_REPAIR'
        answer={'review_id':job['id'],'manuscript_id':job['manuscript_id'],'profile_id':job['profile_id'],'read_complete':True,'recommendation':'consider','reason_ru':['Искусственный пример транспорта.','Вторая искусственная строка.']}
        h=fixtures.transport_helpers
        rows=[h.line('session_meta',{'id':sid,'cwd':str(f.root)}),h.line('turn_context',r.SETTINGS),h.message('user',prompt),h.message('assistant',json.dumps(answer),'final')]
        proof=r.runner.native_records(rows,sid,prompt,job,f.root)
        process=h.FakeProcess([{'type':'thread.started','thread_id':sid},{'type':'turn.started'},{'type':'turn.completed','usage':{}}])
        def popen(argv,**kwargs):
            self.assertEqual(kwargs['env'],r.runner.sanitized_env())
            Path(argv[argv.index('--output-last-message')+1]).write_text(json.dumps(answer));return process
        worker=transport.ReplacementDispatcher(f.run,f.root,value)
        preserved=(f.run/'results/M12-N2/attempt-002/failure.json').read_bytes()
        with patch.object(r.runner.shutil,'which',return_value='/synthetic/codex'),patch.object(r.runner.subprocess,'Popen',side_effect=popen) as launch,patch.object(transport,'inspect_native',return_value=proof):
            result=worker.run_one(job);again=worker.run_one(job)
        self.assertEqual(result['status'],r.runner.COMPLETE);self.assertEqual(launch.call_count,1)
        self.assertEqual(again['status'],'SKIPPED_EXISTING_PHYSICAL_ATTEMPT_NO_RETRY')
        self.assertEqual(process.stdin.saved,prompt)
        self.assertEqual((f.run/'results/M12-N2/attempt-002/failure.json').read_bytes(),preserved)
        self.assertEqual(r.strict((value['attempt']/'receipt.json').read_bytes())['physical_attempt'],3)


if __name__=='__main__':unittest.main(verbosity=2)
