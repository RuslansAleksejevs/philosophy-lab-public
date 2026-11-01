"""ROOT EXECUTION ONLY: one writer, archive M12 then run/archive M13 and map both.

Run only after the M12 dispatcher process has exited. Actual CLI execution needs
the same approved outer process permissions. No attempt is retried automatically.
"""
from pathlib import Path
import argparse
import fcntl
import json
import sys
from resolver_repair import ROOT,RUN,HERE,runner,require,descriptor,file_bytes
from archive_repair import accept_with_writer
from runner_repair import execute
from resolver_map_repair import complete_with_writer


def emit(value):
    print(json.dumps(value,ensure_ascii=False),flush=True)


def finish_with_writer(root,run,lane,w,summary_output=None):
    # The driver is explicit additional technical evidence, never a model input.
    own=descriptor(root,lane/'finish_replacements.py')
    require(w.put(file_bytes(root,own))==own['sha256'],'Driver object mismatch')
    repair=lane/'REPAIR_RECEIPT.json'
    first=accept_with_writer(root,run,repair,'M12-N2',w)
    emit({'phase':'M12_ARCHIVED','status':first['status'],'event_id':first.get('event_id')})
    if first['status']!='REVIEW_ARCHIVED':return {'status':'STOPPED_M12_NOT_ACCEPTED'}
    result=execute(root,run,repair,'M13-N2',w)
    emit({'phase':'M13_LOCAL','result':result})
    status=result['status']
    if status=='SKIPPED_EXISTING_PHYSICAL_ATTEMPT_NO_RETRY':
        receipt=run/'results/M13-N2/attempt-002/receipt.json'
        if not receipt.is_file():return {'status':'STOPPED_EXISTING_M13_WITHOUT_FINISHED_RECEIPT'}
        status=runner.strict_json(receipt.read_bytes())['status']
    if status not in {runner.COMPLETE,runner.QUARANTINED}:
        return {'status':'STOPPED_M13_NOT_COMPLETE','local_result':result}
    second=accept_with_writer(root,run,repair,'M13-N2',w)
    emit({'phase':'M13_ARCHIVED','status':second['status'],'event_id':second.get('event_id')})
    if second['status']!='REVIEW_ARCHIVED':return {'status':'STOPPED_M13_QUARANTINED'}
    group=complete_with_writer(root,run,w)
    if summary_output is not None:
        from resolver_repair import load_resolution
        import summary_repair_v3 as summary
        resolution=load_resolution(root,run,lane/'ACCEPTED_ATTEMPTS_RECEIPT.json',w.events(),w.get)
        coverage,value=summary.summarize(run,resolution)
        require(coverage['accepted_reviews']==110 and value is not None,'Summary incomplete')
        summary.frozen.write_outputs(summary_output,coverage,value)
        emit({'phase':'SUMMARY_WRITTEN','directory':str(summary_output),'accepted_reviews':110})
    return group


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--summary-output',type=Path,default=RUN/'summaries/COMPLETE_REPAIR_V3')
    args=parser.parse_args();output=args.summary_output.absolute()
    require(output.is_relative_to(RUN) and not output.exists(),'Summary output must be a fresh path inside selection run')
    sys.path.insert(0,str(ROOT/'scripts'));from research_archive import Archive
    with (RUN/'archive-reviews.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        with Archive(ROOT/'research/archive').writer() as w:result=finish_with_writer(ROOT,RUN,HERE,w,output)
    emit(result)
    if result['status']!='CAPACITY_REPLACEMENTS_COMPLETE_ARCHIVED':raise SystemExit(2)


if __name__=='__main__':main()
