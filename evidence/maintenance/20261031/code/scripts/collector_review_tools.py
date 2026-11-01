#!/usr/bin/env python3
"""Register an exact-hash tool review; does not print or auto-approve tool bodies."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re

from capture_codex import rollout_file, strict_json, classify, CALL_TYPES, TOOL_TYPES
from collector import Collector, atomic_json
from collector_safety import contains_credential


def review(root,sid,line,sha):
    if type(line) is not int or line<1 or not re.fullmatch('[a-f0-9]{64}',sha):
        raise ValueError('positive source line and exact SHA256 required')
    collector=Collector(root)
    from collector_source import discover_sessions
    sessions={s['session_id']:s for s in discover_sessions(collector.db,collector.root,collector.explicit)}
    if sid not in sessions: raise ValueError('session outside authorized collector scope')
    session=sessions[sid]; blocked=set()
    with rollout_file(Path(session['source_path'])) as stream:
        for number in range(1,line+1):
            raw=stream.readline(16*1024*1024)
            if not raw.endswith(b'\n'): raise ValueError('record absent, partial or oversized')
            record=strict_json(raw); item=record.get('payload',{})
            if number==1 and (record.get('type')!='session_meta' or item.get('id')!=sid
                              or item.get('cwd')!=session['source_cwd']):
                raise ValueError('native source identity mismatch')
            reason=classify(record,number,{number},blocked)
            if item.get('type') in CALL_TYPES and reason is not None: blocked.add(item.get('call_id'))
        if hashlib.sha256(raw).hexdigest()!=sha: raise ValueError('review hash does not match current exact record')
        if item.get('type') not in TOOL_TYPES or reason is not None or contains_credential(record):
            raise ValueError('record excluded by safe tool capture rules')
    archive=collector.archive
    event=archive.append({'kind':'collector.tool_review_decision','actor':{'id':'explicit-tool-review','role':'tool'},
        'session_id':sid,'run_id':'collector:'+sid,'operation_id':'tool-review:'+sid+':'+str(line),
        'attempt_id':'review-v1','payload':{'source_line':line,'raw_sha256':sha,
        'decision':'safe_body_reviewed','boundary':'Caller reviewed exact tool body before invoking this command; automated classifier alone is not approval.'}},
        'tool-review:'+sid+':'+str(line)+':'+sha)
    with collector.lock():
        manifest={str(e['payload']['source_line']):e['payload']['raw_sha256'] for e in archive.events()
                  if e['kind']=='collector.tool_review_decision' and e['session_id']==sid}
        atomic_json(collector.root/'collector/reviews'/(sid+'.json'),manifest)
    return {'event_id':event['id'],'session_id':sid,'source_line':line,'sha256':sha}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--session',required=True); p.add_argument('--line',type=int,required=True)
    p.add_argument('--sha256',required=True)
    args=p.parse_args(); os.umask(0o077)
    print(json.dumps(review(Path(__file__).resolve().parents[1],args.session,args.line,args.sha256)))


if __name__=='__main__': main()
