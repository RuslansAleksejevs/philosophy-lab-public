"""Prepare/accept one explicit local-launch repair; no model or STOP mutation."""
from pathlib import Path
import argparse
import fcntl
import json
import sys
from resolver_repair import ROOT, RUN, HERE, V2, JOBS, TARGETS, runner, prior, Evidence, descriptor, file_bytes, strict, encode, require, inspect_local_failure, load_repair
sys.path.insert(0, str(RUN/'finalization-preparation'))
from closure_writer import save_once


def prepare_request(failure_receipt_path, session_id, output):
    """Root-only local preparation. Copy named accepted metadata into this run."""
    failure_receipt_path, output = Path(failure_receipt_path).resolve(), Path(output).absolute()
    require(output.is_relative_to(HERE) and not output.exists(), 'Use a new repair request path')
    failure = strict(file_bytes(ROOT, descriptor(ROOT, failure_receipt_path)))
    require(failure['status']=='LOCAL_LAUNCH_FAILURE_PRESERVED', 'Actual local failure receipt required')
    source = failure_receipt_path.parent
    copies = {}
    for name in ('FAILURE_INSPECTION.json','STOP_ORIGINAL.json','STOP_DISPOSITION.json','ARCHIVE_RECEIPT.json','ARCHIVE_REQUEST.json','CAPTURE_CHECK.json'):
        data = file_bytes(ROOT, descriptor(ROOT, source/name))
        dest = HERE/'local-launch-evidence'/name
        save_once(dest, data)
        copies[name] = descriptor(ROOT, dest)
    jobs = strict((RUN/'queue.json').read_bytes())['jobs']
    proof = inspect_local_failure(ROOT, RUN, next(j for j in jobs if j['id']==JOBS[0]))
    report = strict((HERE/'LAUNCH_TESTS.json').read_bytes())
    require(report['status']=='PASS_SYNTHETIC_PREPARATION_ONLY' and report['failures']==report['errors']==0, 'Launch tests not accepted')
    files = report['files']+[descriptor(ROOT,HERE/'LAUNCH_TESTS.json')]+list(copies.values())
    for item in files: file_bytes(ROOT,item)
    plan = {'schema':'selection-local-launch-repair.v1','target_attempts':TARGETS,'automatic_retry':False,
            'original_ready_receipts':{jid:descriptor(ROOT,V2/jid/'READY_RECEIPT.json') for jid in JOBS},
            'local_launch_failure':{'event_id':failure['event_id'],'files':proof['files'],'inspection':copies['FAILURE_INSPECTION.json']},
            'preserved_stop':copies['STOP_ORIGINAL.json'],
            'boundary':'Original110 logical roles and packets/config unchanged; one explicit local initialization repair. No observed session/output in002; hidden provider computation unknown.'}
    request = {'schema':'selection-local-launch-repair-request.v1','session_id':session_id,'plan':plan,'files':files}
    save_once(output,encode(request))
    return descriptor(ROOT,output)


def accept_with_writer(root,run,request_ref,w):
    root,run=Path(root).resolve(),Path(run).resolve()
    lane=run/'capacity-launch-repair-001'
    request=strict(file_bytes(root,request_ref));plan=request['plan']
    require(request['schema']=='selection-local-launch-repair-request.v1' and plan['schema']=='selection-local-launch-repair.v1' and plan['target_attempts']==TARGETS and plan['automatic_retry'] is False,'Wrong repair scope')
    start,jobs=runner.gate(run,root);events=list(w.events());e=Evidence(root,run,events,w.get)
    require(request['session_id']==strict((run/'AUTHORIZATION.json').read_bytes())['session_id'],'Wrong root session')
    old={jid:prior.load_ready(root,run,root/plan['original_ready_receipts'][jid]['path'],events,w.get) for jid in JOBS}
    require(set(plan['original_ready_receipts'])==set(JOBS) and all(old[j]['job']['id']==j and old[j]['input_event_id']==start['event_id'] for j in JOBS),'Original ready/input identity differs')
    require(old[JOBS[0]]['plan']['authorization']==old[JOBS[1]]['plan']['authorization'],'Original ready authorizations differ')
    local=plan['local_launch_failure'];failure=e.event(local['event_id'],'research.selection.local_launch_failure')
    require(failure['payload']['status']=='LOCAL_LAUNCH_FAILURE_PRESERVED' and failure['payload']['logical_job_id']==JOBS[0] and failure['payload']['physical_attempt']==2 and failure['payload']['session_id'] is None,'Wrong actual local failure')
    require(failure['bindings']==start['bindings'],'Local failure bindings differ')
    proof=inspect_local_failure(root,run,old[JOBS[0]]['job'])
    require(local['files']==proof['files'],'Local failure files changed')
    for ref in local['files']+[local['inspection']]:e.bound(ref,failure)
    from runner_capacity_v2 import ordinary_prerequisites
    ordinary_prerequisites(root,run,start['event_id'],events)
    require(not (run/'results/M12-N2/attempt-003').exists() and not (run/'results/M13-N2/attempt-002').exists(),'Repair target already started')
    require((run/'STOP.json').read_bytes()==file_bytes(root,plan['preserved_stop']),'Active STOP not exactly preserved')
    require(proof['replacement_ready_event_id']==old[JOBS[0]]['ready_event_id'] and proof['failed_attempt_event_id']==old[JOBS[0]]['failed_attempt']['event_id'],'Local failure history differs')
    parents=[start['event_id'],failure['id']]+[old[jid]['ready_event_id'] for jid in JOBS]
    require({start['event_id'],old[JOBS[0]]['ready_event_id'],old[JOBS[0]]['failed_attempt']['event_id']}<=set(failure['parents']),'Local failure dropped original parents')
    plan_data=encode(plan);plan_path=lane/'PLAN.json'
    rows=request['files']+[request_ref]+list(plan['original_ready_receipts'].values())+local['files']
    required={str((lane/n).relative_to(root)) for n in ('resolver_repair.py','runner_repair.py','ready_repair.py','test_launch_repair.py','LAUNCH_TESTS.json')}
    require(required<={x['path'] for x in rows},'Launch code/tests must be explicitly frozen')
    for row in rows:file_bytes(root,row)
    save_once(plan_path,plan_data);plan_ref=descriptor(root,plan_path)
    rows=list({r['path']:r for r in rows+[plan_ref]}.values())
    for row in rows:require(w.put(file_bytes(root,row))==row['sha256'],'Stored repair bytes differ')
    event=w.append({'kind':'research.selection.local_launch_repair.accepted','actor':{'id':request['session_id'],'role':'AI'},'session_id':request['session_id'],'run_id':run.name,
                    'operation_id':run.name+':local-launch-repair-001','attempt_id':'physical003-repair-v1','parents':parents,'bindings':start['bindings'],
                    'outputs':list(dict.fromkeys(r['sha256'] for r in rows)),
                    'payload':{'status':'LOCAL_LAUNCH_REPAIR_ACCEPTED_BOUNDED','target_attempts':TARGETS,'maximum_new_local_repair_attempts':1,'automatic_retry':False,'preserved_failed_physical_attempts':3,'failed_provider_review_slots':2,'model_calls':0}},run.name+':local-launch-repair-001:v1')
    receipt={'status':'LOCAL_LAUNCH_REPAIR_ACCEPTED_BOUNDED','event_id':event['id'],'input_event_id':start['event_id'],'bindings':start['bindings'],'plan':plan_ref,'files':rows}
    path=lane/'REPAIR_RECEIPT.json';save_once(path,encode(receipt))
    load_repair(root,run,path,list(w.events()),w.get)
    return receipt


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--prepare-request',type=Path);group.add_argument('--request',type=Path)
    parser.add_argument('--failure-receipt',type=Path);parser.add_argument('--session-id')
    args=parser.parse_args()
    if args.prepare_request:
        require(args.failure_receipt and args.session_id,'Actual failure receipt/root session required')
        print(json.dumps({'status':'PREPARED_NO_ARCHIVE_WRITES','request':prepare_request(args.failure_receipt,args.session_id,args.prepare_request)}));return
    sys.path.insert(0,str(ROOT/'scripts'));from research_archive import Archive
    with (RUN/'dispatch.lock').open('a') as dispatch, (RUN/'archive-reviews.lock').open('a') as lock:
        fcntl.flock(dispatch,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        with Archive(ROOT/'research/archive').writer() as w:
            result=accept_with_writer(ROOT,RUN,descriptor(ROOT,args.request.absolute()),w)
    print(json.dumps({'status':result['status'],'event_id':result['event_id']}))


if __name__=='__main__':main()
