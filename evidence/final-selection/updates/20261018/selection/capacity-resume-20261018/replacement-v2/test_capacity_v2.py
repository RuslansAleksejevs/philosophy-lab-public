"""Two-failure synthetic fixtures only; every Popen/native provider call is mocked."""
from pathlib import Path
import copy
import json
import sys
import tempfile
import unittest
from unittest.mock import patch
import resolver_v2 as r
import runner_capacity_v2 as transport
import archive_capacity_v2 as archiver
import ready_capacity_v2 as readiness
import validate_capacity_v4 as validator
import closure_capacity_v2 as closure
sys.path.insert(0,str(r.RUN/'finalization-preparation'))
from test_validate_final import Fixture
from test_closure_writer import MemoryArchive,checkpoint_api
import essay_lineage
transport_helpers=r.module('capacity_v2_test_transport',r.RUN/'test_runner.py')


class TwoFixture(Fixture):
    def __init__(self,root):
        super().__init__(Path(root).resolve())
        for event in self.events:
            if event['kind']=='essay.lineage.entry':event['payload']['protocol']=essay_lineage.PROTOCOL
        self.folder=readiness.folder(self.run);self.folder.mkdir(parents=True)
        self.byid={j['id']:j for j in self.jobs};self.old_reviews={};self.proofs={};self.sources={};self.accepted={}
        remove={self.plan['plain_language_review']['event_id']}
        for jid in r.JOBS:
            old=next(e for e in self.events if e['kind']=='research.selection.review.completed' and e['payload']['job_id']==jid)
            review=next(x for x in self.reviews if x['event_id']==old['id']);self.old_reviews[jid]=review;self.reviews.remove(review)
            remove|={old['id'],review['lineage_event_id']}
            remove|={e['id'] for e in self.events if e['kind']=='research.selection.visible_fragment.captured' and e['session_id']==old['session_id']}
            lane=self.run/'results'/jid;(lane/'ARCHIVE_RECEIPT.json').unlink();(lane/'attempt-001/final.json').unlink()
        self.events=[e for e in self.events if e['id'] not in remove]
        refs=list(self.start['files'])
        for name in ('runner.py','test_runner.py'):refs.append(self.file(name,b'SYNTHETIC immutable source'))
        for job in self.jobs:
            for kind in ('prompt','schema'):refs.append(r.descriptor(self.root,self.root/job[kind+'_file']))
            if job['id'] not in r.JOBS:self.file('results/'+job['id']+'/attempt-001/receipt.json',{'status':r.runner.COMPLETE,'session_id':'fresh-'+job['id']})
        self.start['files']=list({x['path']:x for x in refs}.values());self.file('START_RECEIPT.json',self.start)
        next(e for e in self.events if e['id']==self.start['input_event_id'])['outputs']=[x['sha256'] for x in self.start['files']]
        self.failures={};self.failure_proofs={};failure_ids=[]
        for i,jid in enumerate(r.JOBS,1):
            job=self.byid[jid];sid='failed-synthetic-'+jid;prompt=(self.root/job['prompt_file']).read_text()
            rows=[transport_helpers.line('session_meta',{'id':sid,'cwd':str(self.root)}),transport_helpers.line('turn_context',r.SETTINGS),transport_helpers.message('user',prompt)]
            proof=r.runner.native_records(rows,sid,prompt,job,self.root)[0];self.failure_proofs[jid]=proof
            failed={'status':r.runner.FAILED,'job_id':jid,'session_id':sid,'prompt_sha256':job['prompt_sha256'],'schema_sha256':job['schema_sha256'],
                    'requested_model':job['model'],'requested_effort':job['effort'],'requested_service_tier':'default',
                    'process_state':{'process_stopped':True,'stderr_drained':True},'automatic_retry':False}
            stdout=b''.join(json.dumps(e).encode()+b'\n' for e in [{'type':'thread.started','thread_id':sid},{'type':'turn.started'},
                           {'type':'error','message':'Selected model is at capacity. Please try a different model.'}])
            files=[self.file('results/'+jid+'/attempt-001/'+name,data) for name,data in [('launch.json',{'job_id':jid}),('failure.json',failed),('stderr.json',{'lines':[]}),('visible-events.jsonl',stdout)]]
            inspection=self.file('capacity-recovery-%03d/FAILURE_INSPECTION.json'%i,{'native_proof':proof,'assistant_visible_records':0,'final_records':0,'no_completed_output':True,'quota_message_observed':False})
            failure=self.event('research.selection.transport_failure',parents=[self.ready['id']]+([state['id']] if i>1 else []),outputs=[f['sha256'] for f in files+[inspection]],
                      payload={'status':'FAILED_ATTEMPT_PRESERVED','job_id':jid,'session_id':sid,'failure_kind':'provider_capacity_no_visible_review',
                               'review_accepted':False,'quota_message_observed':False,'hidden_computation_claimed':False,'files':files+[inspection]})
            failure_ids.append(failure['id'])
            kind,status=('research.selection.transport_disposition.accepted','CAPACITY_DISPOSITION_ACCEPTED_BOUNDED') if i==1 else ('research.selection.stopped','SELECTION_INCOMPLETE_CAPACITY_STOP')
            state=self.event(kind,parents=[self.ready['id']]+failure_ids,payload={'status':status})
            self.failures[jid]={'failure_event_id':failure['id'],'inspection':inspection,'preserved_state':{'event_id':state['id'],'kind':kind,'status':status}}
        token=json.dumps('Synthetic new human resume; same model, exact existing goal.').encode();digest=r.sha(token);self.objects[digest]=token
        captured=self.event('research.selection.visible_fragment.captured',outputs=[digest],payload={'role':'user','source_line':9999})
        auth=self.file('capacity-resume-20261018/AUTHORIZATION.json',{'synthetic':True,'same_goal':True,'model':'gpt-6-astra'})
        resume=self.event('research.selection.resume.accepted',parents=[self.ready['id'],state['id'],captured['id']],outputs=[auth['sha256']])
        code=[]
        for name in ('resolver_v2.py','runner_capacity_v2.py','archive_capacity_v2.py','ready_capacity_v2.py','validate_capacity_v4.py','closure_capacity_v2.py',
                     'summary_capacity_v2.py','export_capacity_v2.py','test_capacity_v2.py','test_consumers_v2.py','REPLACEMENT_TESTS.json'):
            code.append(self.file('capacity-resume-20261018/replacement-v2/'+name,b'SYNTHETIC bound source/test fixture'))
        self.request={'schema':'capacity-replacements-ready-request.v2','run_id':self.run.name,'session_id':'fixture-coordinator',
                      'authorization':{'event_id':resume['id'],'artifact':auth,'user_capture_event_ids':[captured['id']]},'failures':self.failures,'files':code}
        self.request_ref=self.file('capacity-resume-20261018/replacement-v2/REQUEST.json',self.request)
        self.archive=MemoryArchive(self)

    def prepare(self):
        with self.archive.writer() as w:return readiness.ready_with_writer(self.root,self.run,self.request_ref,w)

    def ready_path(self,jid):return self.folder/jid/'READY_RECEIPT.json'
    def map_path(self,jid):return self.folder/jid/'ACCEPTED_ATTEMPTS.v2.json'
    def map_receipt(self,jid):return self.folder/jid/'ACCEPTED_ATTEMPTS_RECEIPT.json'
    def resolution_path(self):return self.folder/'ACCEPTED_ATTEMPTS_RECEIPT.json'

    def run_fake(self,jid,stderr='',sid=None):
        if not self.ready_path(jid).exists():self.prepare()
        ready=r.load_ready(self.root,self.run,self.ready_path(jid),self.archive.events(),self.archive.get)
        job=self.byid[jid];sid=sid or 'new-synthetic-'+jid;prompt=(self.root/job['prompt_file']).read_text()
        answer={'review_id':jid,'manuscript_id':job['manuscript_id'],'profile_id':job['profile_id'],'read_complete':True,'recommendation':'consider',
                'reason_ru':['Первый искусственный довод проверяет только структуру транспорта.','Второй искусственный довод не является оценкой настоящего эссе.']}
        rows=[transport_helpers.line('session_meta',{'id':sid,'cwd':str(self.root)}),transport_helpers.line('turn_context',r.SETTINGS),
              transport_helpers.message('user',prompt),transport_helpers.line('response_item',{'type':'reasoning','text':'EXCLUDED_TEST_REASONING'}),
              transport_helpers.message('assistant',json.dumps(answer),'final')]
        source=self.root/(jid+'-synthetic-native.jsonl');source.write_bytes(b''.join(rows));self.sources[jid]=source
        self.proofs[jid]=r.runner.native_records(rows,sid,prompt,job,self.root)
        process=transport_helpers.FakeProcess([{'type':'thread.started','thread_id':sid},{'type':'turn.started'},
                 {'type':'item.completed','item':{'type':'agent_message','id':'final','text':json.dumps(answer)}},{'type':'turn.completed','usage':{'input_tokens':20,'output_tokens':10}}],stderr)
        def popen(argv,**kwargs):
            assert kwargs['env']==r.runner.sanitized_env() and '--output-schema' not in argv and 'resume' not in argv
            Path(argv[argv.index('--output-last-message')+1]).write_text(json.dumps(answer));return process
        worker=transport.ReplacementDispatcher(self.run,self.root,ready)
        for prior in transport.prerequisites(self.root,self.run,ready,self.archive.events(),self.archive.get):worker.register_session(prior)
        with patch.object(r.runner.shutil,'which',return_value='/synthetic/codex'),patch.object(r.runner.subprocess,'Popen',side_effect=popen) as launch,patch.object(transport,'inspect_native',return_value=self.proofs[jid]):
            result=worker.run_one(job)
        assert process.stdin.saved==prompt
        return result,worker,launch.call_count

    def accept(self,jid):
        selected=[{**x,'phase':x.get('phase'),'mode':'exact-visible-fragment','adapter_exclusion':'Synthetic only','tokens':[json.dumps(x['text']).encode()]} for x in self.proofs[jid][1]]
        with patch.object(r.runner,'inspect_native',return_value=self.proofs[jid]),patch.object(archiver,'resolve_session',return_value=self.sources[jid]),patch.object(archiver,'native_selection',return_value=selected):
            with self.archive.writer() as w:
                result=archiver.accept_with_writer(self.root,self.run,self.ready_path(jid),self.map_path(jid),self.map_receipt(jid),w)
        if result['status']=='REVIEW_ARCHIVED':self.accepted[jid]=result
        return result

    def complete(self):
        with self.archive.writer() as w:return readiness.complete_with_writer(self.root,self.run,w)

    def finish(self):
        self.prepare()
        for jid in r.JOBS:self.run_fake(jid);self.accept(jid)
        return self.complete()

    def final_plan(self):
        self.events=self.archive.events();self.objects=dict(self.archive.objects)
        replacement={self.old_reviews[j]['event_id']:self.accepted[j]['event_id'] for j in r.JOBS}
        for decision in self.plan['decisions']:decision['evidence_event_ids']=[replacement.get(e,e) for e in decision['evidence_event_ids']]
        for jid in r.JOBS:self.reviews.append({**self.old_reviews[jid],'event_id':self.accepted[jid]['event_id'],'lineage_event_id':self.accepted[jid]['lineage_event_id']})
        self.attest();self.archive.records=copy.deepcopy(self.events);self.archive.objects=dict(self.objects)
        return self.plan

    def closure_request(self):
        plan=self.final_plan()
        for event in self.events:event.setdefault('timestamp','2026-10-18T10:00:00+00:00')
        first=self.event('operation.started',payload={'protocol':'philosophy-round.v1','purpose':'research'})
        first.update(operation_id='synthetic-operation',attempt_id='synthetic-operation',timestamp='2026-10-18T09:00:00+00:00')
        self.events.remove(first);self.events.insert(0,first)
        self.start['run_start_event']=first['id'];self.file('START_RECEIPT.json',self.start)
        summary=self.file('closure-input/SUMMARY.json',{k:('CONTINUE' if k=='outcome' else 'Synthetic finite scope only.') for k in closure.SUMMARY_FIELDS})
        stages={}
        for stage in closure.STAGES[1:]:
            artifact=self.file('closure-input/'+stage+'.txt',('Synthetic '+stage).encode())
            stages[stage]={'files':[artifact],'evidence_event_ids':[x['event_id'] for x in self.reviews]}
        mapped=r.strict(self.resolution_path().read_bytes())['event_id']
        req={'schema':'selection-closure-request.v1','run_id':self.run.name,'session_id':first['session_id'],
             'plan_input':self.file('closure-input/PLAN_INPUT.json',plan),'stages':stages,'selection_gate_event_ids':[mapped],
             'checkpoint':{'summary':summary,'coverage_event_ids':[self.gap['id']]},
             'coordinator_configuration':{'requested':'Synthetic no model','observed':'Synthetic no model'},
             'outputs':{k:str((self.run/name).relative_to(self.root)) for k,name in [('final_plan','closure/FINAL_PLAN.json'),('validation_report','closure/REPORT.json'),('final_receipt','FINAL_RECEIPT.json')]},
             'export_files':[r.descriptor(self.root,self.folder/'ACCEPTED_ATTEMPTS.v2.json')],'export_generated':['final_plan','validation_report','closure_request'],
             'pending_goal_steps':['project_state_update','private_github_update','collector_restore'],
             'validator':{'name':'capacity-v4','code':r.descriptor(self.root,self.folder/'validate_capacity_v4.py'),'map_receipt':r.descriptor(self.root,self.resolution_path())}}
        ref=self.file('closure-input/REQUEST.json',req);self.archive.records=copy.deepcopy(self.events);self.archive.objects=dict(self.objects)
        return self.root/ref['path'],req


class CapacityTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.f=TwoFixture(self.temp.name)

    def test_ready_writer_two_immutable_plans_and_exact_replay(self):
        result=self.f.prepare();count=len(self.f.archive.records)
        self.assertEqual(set(result['ready_receipts']),set(r.JOBS))
        self.assertEqual(self.f.prepare(),result);self.assertEqual(len(self.f.archive.records),count)
        for jid in r.JOBS:
            ready=r.load_ready(self.f.root,self.f.run,self.f.ready_path(jid),self.f.archive.events(),self.f.archive.get)
            self.assertEqual(ready['job'],self.f.byid[jid]);self.assertEqual(ready['plan']['replacement_order'],list(r.JOBS))

    def test_prepare_request_reads_only_explicit_receipt_metadata(self):
        auth=self.f.request['authorization']
        self.f.file('capacity-resume-20261018/ARCHIVE_RECEIPT.json',{'status':'USER_RESUMPTION_ARCHIVED','event_id':auth['event_id'],
                    'authorization':auth['artifact'],'capture_event_ids':auth['user_capture_event_ids'],'input_event_id':self.f.ready['id']})
        for i,jid in enumerate(r.JOBS,1):
            failure=self.f.failures[jid]
            self.f.file('capacity-recovery-%03d/ARCHIVE_RECEIPT.json'%i,{'status':'CAPACITY_DISPOSITION_ACCEPTED_BOUNDED' if i==1 else 'INCOMPLETE_STATE_ARCHIVED',
                        'event_id':failure['preserved_state']['event_id'],'failure_event_id':failure['failure_event_id'],'input_event_id':self.f.ready['id']})
        files=[x for x in self.f.request['files'] if Path(x['path']).name!='REPLACEMENT_TESTS.json']
        self.f.file('capacity-resume-20261018/replacement-v2/REPLACEMENT_TESTS.json',{'status':'PASS_SYNTHETIC_PREPARATION_ONLY','files':files,'failures':0,'errors':0})
        before=len(self.f.archive.records);request=readiness.request_from_receipts(self.f.root,self.f.run,'fixture-coordinator')
        self.assertEqual(request['failures'],self.f.failures);self.assertEqual(request['authorization'],auth)
        self.assertEqual(len(self.f.archive.records),before)
        self.assertEqual(len(request['files']),len(files)+1)

    def test_ready_rejects_missing_fresh_user_capture_before_writes(self):
        eid=self.f.request['authorization']['user_capture_event_ids'][0]
        next(e for e in self.f.archive.records if e['id']==eid)['payload']['role']='assistant'
        count=len(self.f.archive.records)
        with self.assertRaisesRegex(ValueError,'user-visible'):self.f.prepare()
        self.assertEqual(len(self.f.archive.records),count)

    def test_ready_rejects_resume_not_descended_from_second_stop(self):
        resume=next(e for e in self.f.archive.records if e['id']==self.f.request['authorization']['event_id'])
        second_stop=self.f.failures[r.JOBS[1]]['preserved_state']['event_id'];resume['parents'].remove(second_stop)
        count=len(self.f.archive.records)
        with self.assertRaisesRegex(ValueError,'preserved capacity state'):self.f.prepare()
        self.assertEqual(len(self.f.archive.records),count)

    def test_ready_replays_after_first_committed_ready_event(self):
        self.f.archive.fail_after_key=self.f.run.name+':'+r.JOBS[0]+':replacement-ready-v2'
        with self.assertRaisesRegex(RuntimeError,'committed prefix'):self.f.prepare()
        self.assertFalse(self.f.ready_path(r.JOBS[0]).exists())
        result=self.f.prepare()
        self.assertEqual(len([e for e in self.f.archive.records if e['kind']=='research.selection.replacement.ready']),2)
        self.assertEqual(set(result['ready_receipts']),set(r.JOBS))

    def test_other108_gate_closed_if_one_is_not_accepted(self):
        local=self.f.run/'results/M14-N1/attempt-001/receipt.json';local.write_bytes(r.encode({'status':r.runner.FAILED,'session_id':'fresh-M14-N1'}))
        with self.assertRaisesRegex(ValueError,'other108'):self.f.prepare()

    def test_missing_second_plan_cannot_start_first(self):
        self.f.prepare();self.f.ready_path(r.JOBS[1]).unlink()
        with self.assertRaisesRegex(ValueError,'Missing/nonregular'):self.f.run_fake(r.JOBS[0])
        self.assertFalse((self.f.run/'results'/r.JOBS[0]/'attempt-002').exists())

    def test_second_cannot_start_without_first_accepted_map(self):
        self.f.prepare()
        with self.assertRaisesRegex(ValueError,'Missing/nonregular'):self.f.run_fake(r.JOBS[1])
        self.f.run_fake(r.JOBS[0])
        with self.assertRaisesRegex(ValueError,'Missing/nonregular'):self.f.run_fake(r.JOBS[1])

    def test_two_replacements_fresh_exact_inputs_and_no_rerun(self):
        self.f.prepare()
        failures={jid:(self.f.run/'results'/jid/'attempt-001/failure.json').read_bytes() for jid in r.JOBS}
        for jid in r.JOBS:
            result,worker,count=self.f.run_fake(jid);self.assertEqual(result['status'],r.runner.COMPLETE);self.assertEqual(count,1)
            with patch.object(r.runner.subprocess,'Popen',side_effect=AssertionError('NO RERUN')):
                self.assertEqual(worker.run_one(self.f.byid[jid])['status'],'SKIPPED_EXISTING_002_NO_RETRY')
            accepted=self.f.accept(jid);self.assertEqual(accepted['input_event_id'],self.f.ready['id']);self.assertEqual(accepted['accepted_attempt'],2)
            self.assertEqual((self.f.run/'results'/jid/'attempt-001/failure.json').read_bytes(),failures[jid])
        group=self.f.complete();resolution=r.load_resolution(self.f.root,self.f.run,self.f.resolution_path(),self.f.archive.events(),self.f.archive.get)
        self.assertEqual(set(resolution['exceptions']),set(r.JOBS));self.assertEqual(group['status'],'CAPACITY_REPLACEMENTS_COMPLETE_ARCHIVED')

    def test_second_cannot_reuse_first_successful_session(self):
        self.f.run_fake(r.JOBS[0]);first=self.f.accept(r.JOBS[0])
        result,worker,count=self.f.run_fake(r.JOBS[1],sid=first['session_id'])
        self.assertEqual(result['status'],r.runner.FAILED);self.assertEqual(count,1)
        self.assertEqual(worker.run_one(self.f.byid[r.JOBS[1]])['status'],'SKIPPED_EXISTING_002_NO_RETRY')

    def test_first_cannot_reuse_other_failed_session(self):
        result,_,count=self.f.run_fake(r.JOBS[0],sid='failed-synthetic-'+r.JOBS[1])
        self.assertEqual(result['status'],r.runner.FAILED);self.assertEqual(count,1)

    def test_first_quarantine_does_not_enable_second_or_group(self):
        result,_,_=self.f.run_fake(r.JOBS[0],stderr='retrying sampling request (1/5): stream disconnected before completion\n')
        self.assertEqual(result['status'],r.runner.QUARANTINED)
        self.assertEqual(self.f.accept(r.JOBS[0])['status'],'QUARANTINED_REVIEW_ARCHIVED_MISSING')
        with self.assertRaises(ValueError):self.f.run_fake(r.JOBS[1])
        with self.assertRaises(ValueError):self.f.complete()

    def test_second_failure_bytes_and_fake_stored_inspection_rejected(self):
        ref=self.f.failures[r.JOBS[1]]['inspection'];self.f.archive.objects[ref['sha256']]=b'fake'
        with self.assertRaisesRegex(ValueError,'Stored object'):self.f.prepare()

    def test_first_archive_partial_commit_replay_then_second(self):
        self.f.run_fake(r.JOBS[0]);self.f.archive.fail_after_key=self.f.run.name+':'+r.JOBS[0]+':accepted-attempt-map-v2'
        with self.assertRaisesRegex(RuntimeError,'committed prefix'):self.f.accept(r.JOBS[0])
        first=self.f.accept(r.JOBS[0]);count=len(self.f.archive.records)
        self.assertEqual(self.f.accept(r.JOBS[0]),first);self.assertEqual(len(self.f.archive.records),count)
        self.f.run_fake(r.JOBS[1]);self.f.accept(r.JOBS[1]);self.f.complete()

    def test_final110_coverage_two_failures_zero_duplicate_votes(self):
        self.f.finish();plan=self.f.final_plan()
        report=validator.validate(self.f.root,self.f.run,plan,self.f.archive.events(),self.f.archive.get,map_receipt=self.f.resolution_path())
        self.assertEqual((report['individual_reviews'],report['preserved_failed_attempts'],report['protected_unchanged']),(110,2,42))
        self.assertEqual(len(set(report['review_event_ids'])),110)
        (self.f.run/'results'/r.JOBS[1]/'attempt-003').mkdir()
        with self.assertRaisesRegex(ValueError,'Extra replacement'):validator.validate(self.f.root,self.f.run,plan,self.f.archive.events(),self.f.archive.get,map_receipt=self.f.resolution_path())

    def test_final_rejects_any_third_failure(self):
        self.f.finish();plan=self.f.final_plan();event=self.f.event('research.selection.transport_failure',parents=[self.f.ready['id']],payload={'job_id':'M20-N2'});self.f.archive.records.append(event)
        with self.assertRaisesRegex(ValueError,'Unaccounted transport failure'):
            validator.validate(self.f.root,self.f.run,plan,self.f.archive.events(),self.f.archive.get,map_receipt=self.f.resolution_path())

    def test_group_exact_replay_and_missing_first_map_parent_rejected(self):
        result=self.f.finish();count=len(self.f.archive.records);self.assertEqual(self.f.complete(),result);self.assertEqual(len(self.f.archive.records),count)
        second=next(e for e in self.f.archive.records if e['id']==self.f.accepted[r.JOBS[1]]['event_id'])
        firstmap=r.strict(self.f.map_receipt(r.JOBS[0]).read_bytes())['event_id'];second['parents'].remove(firstmap)
        with self.assertRaisesRegex(ValueError,'first accepted map'):
            r.load_resolution(self.f.root,self.f.run,self.f.resolution_path(),self.f.archive.events(),self.f.archive.get)

    def test_v4_closure_explicit_injection_replay_and_finite_scope(self):
        self.f.finish();request,req=self.f.closure_request()
        def call():return closure.execute(self.f.root,self.f.run,request,self.f.archive,validator_api=validator.validate,map_receipt=self.f.resolution_path(),
                                          allow_checkpoint_derived_updates=True,lineage_api=essay_lineage,checkpoint_api=checkpoint_api)
        with patch.object(closure,'HERE',self.f.folder):
            receipt=call();count=len(self.f.archive.records);self.assertEqual(call(),receipt);self.assertEqual(len(self.f.archive.records),count)
        self.assertEqual(receipt['scope'],'finite_selection_only');self.assertFalse(receipt['goal_completion_claimed'])
        self.assertEqual(receipt['remaining_selection_work'],0);self.assertEqual(receipt['preserved_failed_attempts'],2)
        self.assertEqual(len(receipt['failed_attempt_event_ids']),2)
        self.assertEqual(receipt['pending_goal_steps'],req['pending_goal_steps']);self.assertEqual(receipt['core_capture_status'],'INCOMPLETE')
        self.assertIn(receipt['accepted_attempt_map_event_id'],receipt['parent_event_ids'])

    def test_closure_rejects_per_job_map_in_place_of_both(self):
        self.f.finish();request,_=self.f.closure_request();count=len(self.f.archive.records)
        with patch.object(closure,'HERE',self.f.folder):
            with self.assertRaisesRegex(ValueError,'Both replacements'):
                closure.execute(self.f.root,self.f.run,request,self.f.archive,validator_api=validator.validate,map_receipt=self.f.map_receipt(r.JOBS[0]),
                                allow_checkpoint_derived_updates=True,lineage_api=essay_lineage,checkpoint_api=checkpoint_api)
        self.assertEqual(len(self.f.archive.records),count)

    def test_real_archive_ready_two_reviews_maps_only_in_temp(self):
        bindings={key:[] for key in ('method','instruction','config','input')}
        self.f.start['bindings']=bindings;self.f.file('START_RECEIPT.json',self.f.start)
        for event in self.f.archive.records:event['bindings']=bindings
        self.f.archive.objects.update(self.f.objects)
        from research_archive import Archive
        actual=Archive(self.f.root/'synthetic-archive-only').init()
        with actual.writer() as w:
            for digest,data in self.f.archive.objects.items():self.assertEqual(w.put(data),digest)
            for old in self.f.archive.records:
                event=copy.deepcopy(old);event.setdefault('actor',{'id':'synthetic-fixture','role':'tool'})
                event.setdefault('operation_id','fixture-'+old['id']);event.setdefault('attempt_id','fixture-'+old['id'])
                w.append(event,'fixture:'+old['id'])
        self.f.archive=actual
        result=self.f.finish();count=len(actual.events())
        self.assertEqual(result['status'],'CAPACITY_REPLACEMENTS_COMPLETE_ARCHIVED')
        self.assertEqual(self.f.complete(),result);self.assertEqual(len(actual.events()),count)
        self.assertTrue(actual.validate()['ok'])


if __name__=='__main__':unittest.main()
