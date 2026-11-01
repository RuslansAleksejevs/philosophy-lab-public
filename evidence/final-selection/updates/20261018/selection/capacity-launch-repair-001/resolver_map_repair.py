"""Canonical map projection for108/001 + M12/003 + M13/002; no writer on import."""
from pathlib import Path
import argparse
import fcntl
import json
import sys
from resolver_repair import ROOT,RUN,HERE,JOBS,TARGETS,runner,require,strict,encode,descriptor,file_bytes,Evidence,load_ready
sys.path.insert(0,str(RUN/'finalization-preparation'))
from closure_writer import save_once


def load_attempt_resolution(root,run_dir,map_receipt_path,events,get_object):
    root,run_dir=Path(root).resolve(),Path(run_dir).resolve();events=list(events)
    e=Evidence(root,run_dir,events,get_object)
    receipt_path=runner.regular(map_receipt_path,run_dir);receipt=strict(receipt_path.read_bytes())
    jid=receipt['logical_job_id'];require(jid in JOBS,'Unknown mapped replacement')
    require(receipt['status']=='ACCEPTED_ATTEMPTS_MAP_ARCHIVED','Actual map acceptance required')
    event=e.event(receipt['event_id'],'research.selection.accepted_attempts.mapped')
    payload=event['payload']
    require(payload['status']==receipt['status'] and payload['logical_job_id']==jid and payload['accepted_attempt']==TARGETS[jid] and payload['preserved_failed_attempts']==TARGETS[jid]-1,'Wrong map attempt/failure accounting')
    mapping=strict(e.bound(receipt['map'],event));e.bound(receipt['ready_receipt'],event)
    require(mapping['schema']=='selection-accepted-attempts.v3' and mapping['logical_job_id']==jid,'Wrong explicit map schema/job')
    execution=receipt['execution_files']
    expected={str((run_dir/'capacity-launch-repair-001'/n).relative_to(root)) for n in ('archive_repair.py','resolver_map_repair.py','finish_replacements.py','test_map_repair.py','MAP_TESTS.json')}
    require({r['path'] for r in execution}==expected and payload['execution_files']==execution,'Map code/test manifest differs')
    for row in execution:e.bound(row,event)
    ready=load_ready(root,run_dir,root/receipt['ready_receipt']['path'],events,get_object,jid)
    require(mapping['input_event_id']==ready['input_event_id'] and mapping['ready_event_id']==ready['ready_event_id'] and mapping['failed_attempt']==ready['failed_attempt'],'Map dropped original failure/repair/input')
    if jid==JOBS[0]:require(mapping['local_launch_failure']==ready['local_launch_failure'],'Local launch failure changed')
    else:require('local_launch_failure' not in mapping,'M13 has no local initialization failure')
    accepted=mapping['accepted_attempt'];review=e.event(accepted['event_id'],'research.selection.review.completed')
    require(accepted['number']==TARGETS[jid] and accepted['path']==str(ready['attempt'].relative_to(root)),'Wrong accepted physical target')
    require(review['payload']['status']=='REVIEW_ARCHIVED' and review['payload']['job_id']==jid and review['payload']['accepted_attempt']==TARGETS[jid] and review['payload']['local_launch_failure_event_id']==ready['local_launch_failure']['event_id'],'Review not bound to explicit repair')
    require(accepted['session_id']==review['session_id'] and accepted['session_id']!=ready['failed_attempt']['session_id'],'Missing fresh accepted session')
    require({ready['input_event_id'],ready['ready_event_id'],ready['failed_attempt']['event_id'],ready['local_launch_failure']['event_id']}<=set(review['parents']),'Review lost explicit failure/repair parents')
    require(event['bindings']==review['bindings']==ready['receipt']['bindings'],'Map/review bindings differ')
    require({ready['ready_event_id'],ready['failed_attempt']['event_id'],review['id']}<=set(event['parents']),'Map parents missing')
    require(accepted['files']==review['payload']['files'],'Accepted file manifest differs')
    require({r['path'] for r in accepted['files']}=={str(p.relative_to(root)) for p in ready['attempt'].iterdir()},'Accepted attempt file set changed')
    for row in accepted['files']:e.bound(row,review)
    ar=strict((run_dir/'results'/jid/'ARCHIVE_RECEIPT.json').read_bytes())
    require(ar['status']=='REVIEW_ARCHIVED' and ar['job_id']==jid and ar['event_id']==review['id'] and ar['session_id']==accepted['session_id'] and ar['files']==accepted['files'],'Logical archive receipt differs')
    require(ar['accepted_attempt']==TARGETS[jid] and ar['input_event_id']==ready['input_event_id'] and ar['replacement_ready_event_id']==ready['ready_event_id'] and ar['failed_attempt_event_id']==ready['failed_attempt']['event_id'] and ar['local_launch_failure_event_id']==ready['local_launch_failure']['event_id'],'Logical receipt dropped accepted attempt/history')
    require({p.name for p in (run_dir/'results'/jid).glob('attempt-*')}=={'attempt-%03d'%i for i in range(1,TARGETS[jid]+1)},'Unexpected physical attempt')
    evidence=ready['evidence_files']+ready['repair']['receipt']['files']+[receipt['ready_receipt'],receipt['map'],descriptor(root,receipt_path)]+execution
    safe=[r for r in evidence if Path(r['path']).name not in {'native-visible.json','visible-events.jsonl','stderr.json'} and not r['path'].endswith('.jsonl')]
    out={**ready,**mapping,'map_event_id':event['id'],'map_receipt':descriptor(root,receipt_path),
         'evidence_files':list({r['path']:r for r in safe}.values())}
    if jid!=JOBS[0]:out.pop('local_launch_failure',None)
    return out


def load_resolution(root,run_dir,map_receipt_path,events,get_object):
    root,run_dir=Path(root).resolve(),Path(run_dir).resolve();events=list(events)
    e=Evidence(root,run_dir,events,get_object);path=runner.regular(map_receipt_path,run_dir);receipt=strict(path.read_bytes())
    require(receipt['status']=='CAPACITY_REPLACEMENTS_COMPLETE_ARCHIVED','Both replacements not accepted')
    event=e.event(receipt['event_id'],'research.selection.capacity_replacements.accepted');payload=event['payload']
    require(payload['status']==receipt['status'] and payload['logical_job_ids']==list(JOBS) and payload['preserved_failed_attempts']==3 and payload['preserved_capacity_failures']==2 and payload['preserved_local_launch_failures']==1 and payload['failed_provider_review_slots']==2,'Wrong group failure/slot accounting')
    mapping=strict(e.bound(receipt['map'],event))
    require(mapping['schema']=='selection-capacity-map.v3' and set(mapping['attempt_map_receipts'])==set(JOBS),'Exactly fixed003/002 group required')
    exceptions={}
    for jid,row in mapping['attempt_map_receipts'].items():
        e.bound(row,event)
        item=load_attempt_resolution(root,run_dir,root/row['path'],events,get_object)
        require(item['logical_job_id']==jid and item['map_event_id'] in event['parents'],'Wrong group job/parent')
        exceptions[jid]=item
    a,b=exceptions[JOBS[0]],exceptions[JOBS[1]]
    require(mapping['input_event_id']==a['input_event_id']==b['input_event_id'] and a['ready_event_id']==b['ready_event_id'],'Group changed repair or original input')
    require(event['bindings']==a['receipt']['bindings']==b['receipt']['bindings'],'Group bindings differ')
    require(a['map_event_id'] in e.events[b['accepted_attempt']['event_id']]['parents'],'M13 lacks accepted M12 predecessor')
    sids=[x[k]['session_id'] for x in exceptions.values() for k in ('failed_attempt','accepted_attempt')]
    require(len(set(sids))==4,'Capacity/accepted sessions reused')
    evidence=[receipt['map'],descriptor(root,path)]
    for item in exceptions.values():evidence+=item['evidence_files']
    return {'schema':'selection-capacity-resolution.v3','input_event_id':mapping['input_event_id'],'map_event_id':event['id'],'exceptions':exceptions,
            'evidence_files':list({r['path']:r for r in evidence}.values())}


def complete_with_writer(root,run_dir,w):
    root,run_dir=Path(root).resolve(),Path(run_dir).resolve();lane=run_dir/'capacity-launch-repair-001';events=list(w.events())
    refs={jid:descriptor(root,lane/jid/'ACCEPTED_ATTEMPTS_RECEIPT.json') for jid in JOBS}
    found={jid:load_attempt_resolution(root,run_dir,root/ref['path'],events,w.get) for jid,ref in refs.items()}
    a,b=found[JOBS[0]],found[JOBS[1]]
    require(a['input_event_id']==b['input_event_id'] and a['ready_event_id']==b['ready_event_id'],'Different accepted repair/input')
    second=next(e for e in events if e['id']==b['accepted_attempt']['event_id'])
    require(a['map_event_id'] in second['parents'],'M13 did not wait for M12 accepted map')
    sids=[x[k]['session_id'] for x in found.values() for k in ('failed_attempt','accepted_attempt')]
    require(len(set(sids))==4,'Accepted/failed sessions reused')
    mapping={'schema':'selection-capacity-map.v3','input_event_id':a['input_event_id'],'attempt_map_receipts':refs}
    map_path=lane/'ACCEPTED_ATTEMPTS.v3.json';save_once(map_path,encode(mapping));map_ref=descriptor(root,map_path)
    for row in [map_ref,*refs.values()]:require(w.put(file_bytes(root,row))==row['sha256'],'Stored map bytes differ')
    event=w.append({'kind':'research.selection.capacity_replacements.accepted','actor':{'id':'selection-archive','role':'tool'},'session_id':'selection-archive','run_id':run_dir.name,'operation_id':run_dir.name+':launch-repair','attempt_id':'two-replacement-map-v3',
                    'parents':[a['map_event_id'],b['map_event_id']],'bindings':a['receipt']['bindings'],'outputs':[x['sha256'] for x in [map_ref,*refs.values()]],
                    'payload':{'status':'CAPACITY_REPLACEMENTS_COMPLETE_ARCHIVED','logical_job_ids':list(JOBS),'accepted_replacements':2,'preserved_failed_attempts':3,'preserved_capacity_failures':2,'preserved_local_launch_failures':1,'failed_provider_review_slots':2,'model_calls':0}},run_dir.name+':capacity-replacements-accepted-v3')
    receipt={'status':'CAPACITY_REPLACEMENTS_COMPLETE_ARCHIVED','event_id':event['id'],'map':map_ref}
    path=lane/'ACCEPTED_ATTEMPTS_RECEIPT.json';save_once(path,encode(receipt))
    load_resolution(root,run_dir,path,list(w.events()),w.get)
    return receipt


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--complete-maps',required=True,action='store_true');parser.parse_args()
    sys.path.insert(0,str(ROOT/'scripts'));from research_archive import Archive
    with (RUN/'archive-reviews.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        with Archive(ROOT/'research/archive').writer() as w:result=complete_with_writer(ROOT,RUN,w)
    print(json.dumps(result))


if __name__=='__main__':main()
