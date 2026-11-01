"""Explicit two-job readiness and post-success map acceptance; no model calls.

Only main/execute opens one writer. Root supplies real resume/failure references
and an explicit code/test manifest. No directory scan or invented research input.
"""
from pathlib import Path
import argparse
import json
import sys
from resolver_v2 import (ROOT,RUN,JOBS,runner,Evidence,require,strict,encode,sha,
                         descriptor,file_bytes,check_authorization,check_plan,
                         load_ready,load_attempt_resolution,load_resolution)
sys.path.insert(0,str(RUN/'finalization-preparation'))
from closure_writer import save_once as atomic_save


def folder(run):return Path(run)/'capacity-resume-20261018/replacement-v2'


def save(root,path,value):
    path=Path(path)
    require(path.is_relative_to(root) and '..' not in path.parts and not any(x.is_symlink() for x in (path,*path.parents)),'Unsafe new artifact path')
    atomic_save(path,encode(value))
    return descriptor(root,path)


def request_from_receipts(root,run,session_id):
    """Read only exact metadata receipts; no model, archive, essay or review read."""
    root,run=Path(root).resolve(),Path(run).resolve()
    def read_json(p):return strict(runner.regular(p,root).read_bytes())
    resume=read_json(run/'capacity-resume-20261018/ARCHIVE_RECEIPT.json')
    require(resume['status']=='USER_RESUMPTION_ARCHIVED','Current user resume receipt missing')
    report_path=folder(run)/'REPLACEMENT_TESTS.json';report=read_json(report_path)
    require(report['status']=='PASS_SYNTHETIC_PREPARATION_ONLY' and report['failures']==report['errors']==0,'V2 synthetic acceptance absent')
    files=report['files']+[descriptor(root,report_path)]
    for item in files:file_bytes(root,item)
    failures={}
    for i,jid in enumerate(JOBS,1):
        directory=run/('capacity-recovery-%03d'%i);receipt=read_json(directory/'ARCHIVE_RECEIPT.json')
        kind,status,receipt_status=('research.selection.transport_disposition.accepted','CAPACITY_DISPOSITION_ACCEPTED_BOUNDED','CAPACITY_DISPOSITION_ACCEPTED_BOUNDED') if i==1 else ('research.selection.stopped','SELECTION_INCOMPLETE_CAPACITY_STOP','INCOMPLETE_STATE_ARCHIVED')
        require(receipt['status']==receipt_status and receipt['input_event_id']==resume['input_event_id'],'Preserved capacity receipt differs')
        failures[jid]={'failure_event_id':receipt['failure_event_id'],'preserved_state':{'event_id':receipt['event_id'],'kind':kind,'status':status},
                       'inspection':descriptor(root,directory/'FAILURE_INSPECTION.json')}
    return {'schema':'capacity-replacements-ready-request.v2','run_id':run.name,'session_id':session_id,
            'authorization':{'event_id':resume['event_id'],'artifact':resume['authorization'],'user_capture_event_ids':resume['capture_event_ids']},
            'failures':failures,'files':files}


def ready_with_writer(root,run,request_ref,w):
    root,run=Path(root).resolve(),Path(run).resolve()
    request=strict(file_bytes(root,request_ref))
    require(request['schema']=='capacity-replacements-ready-request.v2' and request['run_id']==run.name,'Ready request identity differs')
    require(isinstance(request['session_id'],str) and request['session_id'],'Actual coordinator session required')
    require(set(request['failures'])==set(JOBS),'Exactly two explicit failure references required')
    start,jobs=runner.gate(run,root);byid={j['id']:j for j in jobs}
    events=list(w.events());e=Evidence(root,run,events,w.get)
    original=e.event(start['event_id'],'research.selection.ready')
    authorization=check_authorization(e,request['authorization'],original)
    files=request['files']
    require(files and len(files)==len({f['path'] for f in files}),'Explicit unique adapter manifest required')
    for item in files:file_bytes(root,item)
    plans={}
    for jid in JOBS:
        supplied=request['failures'][jid]
        failure=e.event(supplied['failure_event_id'],'research.selection.transport_failure')
        attempt=run/'results'/jid/'attempt-001'
        failed_files=[descriptor(root,attempt/name) for name in ('launch.json','failure.json','stderr.json','visible-events.jsonl')]
        plan={'schema':'selection-empty-capacity-replacement.v2','logical_job_id':jid,'replacement_order':list(JOBS),
              'maximum_replacement_attempts':1,'automatic_retry':False,'content_changes':False,
              'input_event_id':start['event_id'],'job':byid[jid],'authorization':request['authorization'],
              'preserved_state':supplied['preserved_state'],'failure_inspection':supplied['inspection'],
              'failed_attempt':{'path':str(attempt.relative_to(root)),'event_id':failure['id'],'session_id':failure['payload']['session_id'],'files':failed_files},
              'replacement_attempt':{'number':2,'path':str((run/'results'/jid/'attempt-002').relative_to(root))},
              'predecessor_map_receipt':None if jid==JOBS[0] else str((folder(run)/JOBS[0]/'ACCEPTED_ATTEMPTS_RECEIPT.json').relative_to(root))}
        check_plan(root,run,plan,e,start,byid[jid])
        plans[jid]=plan
    # All content-independent validation precedes the first canonical append.
    required={'resolver_v2.py','runner_capacity_v2.py','archive_capacity_v2.py','ready_capacity_v2.py','validate_capacity_v4.py','closure_capacity_v2.py',
              'summary_capacity_v2.py','export_capacity_v2.py','test_capacity_v2.py','test_consumers_v2.py','REPLACEMENT_TESTS.json'}
    require({str((folder(run)/name).relative_to(root)) for name in required}<={f['path'] for f in files},'Adapter code/tests missing from explicit manifest')
    prior=[]
    for jid in JOBS:
        p=folder(run)/jid/'READY_RECEIPT.json'
        if p.exists():
            ready=load_ready(root,run,p,events,w.get)
            require(ready['plan']==plans[jid] and request_ref in ready['receipt']['files'],'Existing ready belongs to a different immutable request')
            prior.append(ready)
    if len(prior)<2:
        # Only ordinary108 are required here. Sequential predecessor becomes
        # mandatory at model dispatch and acceptance, after both ready events.
        from runner_capacity_v2 import ordinary_prerequisites
        ordinary_prerequisites(root,run,start['event_id'],events)
    for item in files+[request_ref]:require(w.put(file_bytes(root,item))==item['sha256'],'Stored readiness input differs')
    accepted={}
    for jid in JOBS:
        plan_ref=save(root,folder(run)/jid/'PLAN.json',plans[jid])
        require(w.put(file_bytes(root,plan_ref))==plan_ref['sha256'],'Stored plan differs')
        bound=list({f['path']:f for f in files+[request_ref,plan_ref]}.values())
        _,parents=check_plan(root,run,plans[jid],e,start,byid[jid])
        event=w.append({'kind':'research.selection.replacement.ready','actor':{'id':request['session_id'],'role':'AI'},
                        'session_id':request['session_id'],'run_id':run.name,'operation_id':run.name+':capacity-resume:'+jid,
                        'attempt_id':'replacement-ready-v2','parents':list(dict.fromkeys(parents)),
                        'bindings':start['bindings'],'outputs':[f['sha256'] for f in bound],
                        'payload':{'status':'CAPACITY_REPLACEMENT_READY','logical_job_id':jid,'replacement_order':list(JOBS),
                                   'authorization_event_id':authorization['id'],'maximum_replacement_attempts':1,'model_calls':0}},run.name+':'+jid+':replacement-ready-v2')
        receipt={'status':'CAPACITY_REPLACEMENT_READY','logical_job_id':jid,'event_id':event['id'],'input_event_id':start['event_id'],
                 'bindings':start['bindings'],'plan':plan_ref,'files':bound}
        ref=save(root,folder(run)/jid/'READY_RECEIPT.json',receipt)
        w.put(file_bytes(root,ref));accepted[jid]=ref
    for ref in accepted.values():load_ready(root,run,root/ref['path'],list(w.events()),w.get)
    return {'status':'TWO_REPLACEMENT_INPUTS_ARCHIVED','ready_receipts':accepted,'model_calls':0}


def complete_with_writer(root,run,w):
    root,run=Path(root).resolve(),Path(run).resolve();events=list(w.events())
    refs={jid:descriptor(root,folder(run)/jid/'ACCEPTED_ATTEMPTS_RECEIPT.json') for jid in JOBS}
    resolved={jid:load_attempt_resolution(root,run,root/ref['path'],events,w.get) for jid,ref in refs.items()}
    require(all(resolved[j]['logical_job_id']==j for j in JOBS),'Per-job map identity differs')
    require(len({x['input_event_id'] for x in resolved.values()})==1,'Original input differs across maps')
    require(resolved[JOBS[0]]['plan']['authorization']==resolved[JOBS[1]]['plan']['authorization'],'Maps use different resume authorizations')
    identities=[x[k]['session_id'] for x in resolved.values() for k in ('failed_attempt','accepted_attempt')]
    require(len(set(identities))==4,'Failure/replacement SID reused')
    second=next(e for e in events if e['id']==resolved[JOBS[1]]['accepted_attempt']['event_id'])
    require(resolved[JOBS[0]]['map_event_id'] in second['parents'],'Second replacement lacks first accepted map')
    mapping={'schema':'selection-capacity-map.v2','input_event_id':resolved[JOBS[0]]['input_event_id'],'attempt_map_receipts':refs}
    map_ref=save(root,folder(run)/'ACCEPTED_ATTEMPTS.v2.json',mapping)
    outputs=[map_ref]+list(refs.values())
    for ref in outputs:require(w.put(file_bytes(root,ref))==ref['sha256'],'Stored aggregate map differs')
    event=w.append({'kind':'research.selection.capacity_replacements.accepted','actor':{'id':'selection-archive','role':'tool'},
                    'session_id':'selection-archive','run_id':run.name,'operation_id':run.name+':capacity-resume',
                    'attempt_id':'two-replacement-map-v2','parents':[resolved[j]['map_event_id'] for j in JOBS],
                    'bindings':resolved[JOBS[0]]['receipt']['bindings'],'outputs':[f['sha256'] for f in outputs],
                    'payload':{'status':'CAPACITY_REPLACEMENTS_COMPLETE_ARCHIVED','logical_job_ids':list(JOBS),
                               'accepted_replacements':2,'preserved_failed_attempts':2,'model_calls':0}},run.name+':capacity-replacements-accepted-v2')
    receipt={'status':'CAPACITY_REPLACEMENTS_COMPLETE_ARCHIVED','event_id':event['id'],'map':map_ref}
    destination=folder(run)/'ACCEPTED_ATTEMPTS_RECEIPT.json';save(root,destination,receipt)
    load_resolution(root,run,destination,list(w.events()),w.get)
    return receipt


def execute(root,run,archive,request_path=None,complete=False):
    root,run=Path(root).resolve(),Path(run).resolve()
    require((request_path is None)==complete,'Choose readiness request or final aggregate map')
    import fcntl
    with (run/'archive-reviews.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        with archive.writer() as w:
            return complete_with_writer(root,run,w) if complete else ready_with_writer(root,run,descriptor(root,Path(request_path).resolve()),w)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--request',type=Path);mode.add_argument('--complete-maps',action='store_true');mode.add_argument('--prepare-request',type=Path)
    parser.add_argument('--session-id',help='Actual coordinator session, required with --prepare-request')
    parser.add_argument('--root',type=Path,default=ROOT);parser.add_argument('--run-dir',type=Path,default=RUN)
    args=parser.parse_args()
    if args.prepare_request:
        require(args.session_id,'Actual coordinator session required')
        root,run=args.root.resolve(),args.run_dir.resolve();destination=args.prepare_request.absolute()
        require(destination.is_relative_to(folder(run)),'Prepared request must remain in the v2 directory')
        artifact=save(root,destination,request_from_receipts(root,run,args.session_id))
        print(json.dumps({'status':'PREPARED_NO_ARCHIVE_WRITES','request':artifact},ensure_ascii=False));return
    sys.path.insert(0,str(args.root/'scripts'))
    from research_archive import Archive
    result=execute(args.root,args.run_dir,Archive(args.root/'research/archive'),args.request,args.complete_maps)
    print(json.dumps(result,ensure_ascii=False))


if __name__=='__main__':main()
