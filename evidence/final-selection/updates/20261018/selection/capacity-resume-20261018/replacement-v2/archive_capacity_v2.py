"""Canonical acceptance of the assigned M12-N2 or M13-N2 attempt-002; never dispatches a model.

Static derivative of the frozen prepare/accept checks. Native capture and lineage
APIs are reused unchanged. An accepted map is emitted only after actual review
and lineage events exist. Quarantine never produces an accepted map.
"""
from pathlib import Path
import argparse
import fcntl
import json
import re
import sys
from resolver_v2 import ROOT, RUN, HERE, JOBS, runner, module, load_ready, load_attempt_resolution, load_resolution, descriptor
frozen = module('selection_capacity_v2_frozen_archiver', RUN / 'archive_reviews.py')
require, read, load = frozen.require, frozen.read, frozen.load
sha, strict, encode = frozen.sha, frozen.strict, frozen.encode
versions_for, resolve_session, native_selection = frozen.versions_for, frozen.resolve_session, frozen.native_selection
BOUNDARY = frozen.BOUNDARY
sys.path.insert(0, str(RUN / 'finalization-preparation'))
from closure_writer import save_once as atomic_publish
capture, public_selection = frozen.capture, frozen.public_selection


def save_once(location, value, root=ROOT):
    location = Path(location)
    require(location.is_relative_to(root) and not any(p.is_symlink() for p in (location,*location.parents)), 'Unsafe receipt output')
    atomic_publish(location, encode(value))

def prepare_job(job, mapping, ready, run_dir=RUN, root=ROOT):
    job_id=ready["job"]["id"]
    require(job_id in JOBS,"Unknown exception")
    require(job == ready["job"] and job["id"] == job_id, "Only exact replacement job allowed")
    attempt = run_dir / "results" / job["id"] / "attempt-002"
    receipt = load(attempt / "receipt.json", root)
    require(receipt.get("status") in {runner.COMPLETE, runner.QUARANTINED}, "Only finished local reviews are supported; failed/unfinished attempt requires root repair")
    require(receipt.get('job_id') == job_id and receipt.get('physical_attempt') == 2, 'Local receipt is not explicit002')
    require(receipt.get('replacement_ready_event_id') == ready['ready_event_id'] and receipt.get('failed_attempt_event_id') == ready['failed_attempt']['event_id'], 'Local002 recovery references differ')
    require(receipt.get('session_id') != ready['failed_attempt']['session_id'], 'Replacement reused failed SID')
    for recorded, requested in [('prompt_sha256','prompt_sha256'), ('schema_sha256','schema_sha256'), ('requested_model','model'), ('requested_effort','effort'), ('requested_service_tier','service_tier')]:
        require(receipt.get(recorded) == job[requested], 'Replacement input/config differs')
    for name, digest in receipt.get('outputs', {}).items():
        require((root / name).parent == attempt and sha(read(root / name, root)) == digest, 'Replacement output drift')
    outputs = receipt.get("outputs")
    require(isinstance(outputs, dict) and bool(outputs), "Output hash manifest absent")
    expected = {root / name for name in outputs}
    actual = set(attempt.iterdir())
    require(actual == expected | {attempt / "receipt.json"}, "Unexpected/unbound file inside finished attempt")
    required = {"launch.json", "native-check.json", "native-visible.json", "stderr.json", "visible-events.jsonl", "final.txt"}
    require(required <= {p.name for p in expected}, "Required visible evidence missing")
    files = [{"path": str(p.relative_to(root)), "sha256": sha(read(p, root)), "bytes": p.stat().st_size} for p in sorted(actual)]
    prompt, schema = runner.check_inputs(job, root)
    sid = receipt.get("session_id")
    require(isinstance(sid, str) and re.fullmatch(r"[A-Za-z0-9_-]{8,100}", sid), "Missing exact native session identity")
    launch = load(attempt / "launch.json", root)
    require(launch.get("job_id") == job["id"] and launch.get("prompt_sha256") == job["prompt_sha256"] and launch.get("schema_sha256") == job["schema_sha256"], "Launch identity differs")
    argv = launch.get("argv")
    require(isinstance(argv, list) and argv and argv == runner.command(job, attempt, root, executable=argv[0]), "Launch command differs from bound runner")
    require(launch.get("argv_sha256") == sha(json.dumps(argv, separators=(",", ":")).encode()) and receipt.get("argv") == argv, "Launch command digest differs")
    proof, visible, finals = runner.inspect_native(sid, prompt.decode(), job, root)
    require(not proof["isolation_failures"], "Native isolation/configuration check failed")
    require(load(attempt / "native-check.json", root) == proof, "Saved native proof differs from current source")
    require(load(attempt / "native-visible.json", root) == {"session_id": sid, "records": visible}, "Saved native visible capture differs")
    events = [strict(line) for line in read(attempt / "visible-events.jsonl", root).splitlines()]
    require(all(isinstance(e, dict) and not e.get("unexpected") for e in events), "Unexpected CLI event in finished review")
    require([e.get("thread_id") for e in events if e.get("type") == "thread.started"] == [sid], "CLI session identity mismatch")
    completed = len([e for e in events if e.get("type") == "turn.completed"]) == 1
    errors = [e["message"] for e in events if e.get("type") in {"error", "turn.failed"}]
    stderr = load(attempt / "stderr.json", root)
    require(isinstance(stderr.get("lines"), list) and all(isinstance(x, str) for x in stderr["lines"]), "Malformed stderr capture")
    require(stderr.get("exit_code") == receipt.get("cli_exit_code"), "CLI exit code mismatch")
    status, flags, value = runner.classify(finals, stderr["lines"], read(attempt / "final.txt", root).decode(), schema, errors, completed, stderr["exit_code"], job)
    require(status == receipt["status"] and flags == receipt.get("quality_flags"), "Local verdict does not reproduce")
    if status == runner.COMPLETE:
        require(value == load(attempt / "response.json", root), "Accepted response differs from native final")
        require(isinstance(value.get("reason_ru"), list) and len(value["reason_ru"]) >= 2 and all(isinstance(x, str) and x.strip() for x in value["reason_ru"]), "Concrete rationale absent")
        require(value.get("read_complete") is True, "Full reading not confirmed")
        require(("verdict" if job.get("phase") == "pair" else "recommendation") in value, "PAIR_ARCHIVE_EXTENSION_REQUIRED: verdict/recommendation absent")
    else:
        require(not (attempt / "response.json").exists(), "Quarantined review must not carry accepted response.json")
    versions = versions_for(job, mapping, root)
    source = resolve_session(sid, root)
    selected = native_selection(source, proof, visible, prompt.decode(), job, root)
    return {"job": job, "receipt": receipt, "files": files, "proof": proof, "value": value,
            "versions": versions, "source": source, "selected": selected}



def capture_job(w, item, input_event, run_dir=RUN, root=ROOT):
    job, sid = item["job"], item["receipt"]["session_id"]
    cache = run_dir / "results" / job["id"] / "CAPTURE_RECEIPT.json"
    selection = public_selection(item["selected"])
    if cache.exists():
        prior = load(cache, root)
        require(prior.get("session_id") == sid and prior.get("selection") == selection, "Existing capture receipt differs")
        return prior
    records, evidence = [], []
    for selected in item["selected"]:
        number = selected["line"]
        if selected["mode"] == "standard":
            result = capture(root / "research/archive", item["source"], sid, root,
                             start_line=number, end_line=number, run_id=run_dir.name, archive_writer=w)
            require(result["status"] == "BOUNDED_COMPLETE" and result["captured_records"] == 1 and result["raw_records"][0]["sha256"] == selected["record_sha256"], "Standard native capture has a gap; root repair required")
            records.append({"mode": "standard", "line": number, "capture": result})
            evidence += [result["coverage_event_id"]] + result["raw_event_ids"] + result.get("run_binding_event_ids", [])
        else:
            hashes = [w.put(token) for token in selected["tokens"]]
            descriptor = {k: v for k, v in selected.items() if k != "tokens"}
            descriptor.update(token_sha256=hashes, boundary=BOUNDARY, status="EXACT_VISIBLE_JSON_STRING_FRAGMENTS")
            ev = w.append({"kind": "research.selection.visible_fragment.captured", "actor": {"id": "selection-capture", "role": "tool"},
                           "session_id": sid, "run_id": run_dir.name, "operation_id": "selection-fragment:" + sid + ":" + str(number),
                           "attempt_id": "visible-fragment-v1", "parents": [input_event], "outputs": hashes,
                           "payload": descriptor}, run_dir.name + ":fragment:" + sid + ":" + str(number))
            records.append({"mode": "exact-visible-fragment", "line": number, "event_id": ev["id"], **descriptor})
            evidence.append(ev["id"])
    result = {"status": "BOUNDED_VISIBLE_CAPTURE_ACCEPTED", "session_id": sid, "selection": selection,
              "records": records, "evidence_events": list(dict.fromkeys(evidence)), "boundary": BOUNDARY,
              "full_provider_capture": False, "standard_adapter_complete_for_all_records": all(x["mode"] == "standard" for x in item["selected"])}
    save_once(cache, result, root)
    return result


def accept_with_writer(root, run_dir, ready_receipt, map_path, map_receipt_path, w, *, lineage_api=None):
    """Caller supplies the single archive writer; exact replay only."""
    root, run_dir = Path(root).resolve(), Path(run_dir).resolve()
    events = list(w.events())
    ready = load_ready(root, run_dir, ready_receipt, events, w.get)
    job = ready['job']; job_id=job['id']
    start, _ = runner.gate(run_dir, root)
    require({p.name for p in (run_dir / 'results' / job_id).glob('attempt-*')} == {'attempt-001','attempt-002'}, 'Extra/missing physical attempt')
    map_path, map_receipt_path = Path(map_path).absolute(), Path(map_receipt_path).absolute()
    require(map_path != map_receipt_path and all(p.is_relative_to(run_dir / 'capacity-resume-20261018') and '..' not in p.parts for p in (map_path,map_receipt_path)), 'Map outputs must be distinct new recovery paths')
    destination=run_dir/'capacity-resume-20261018/replacement-v2'/job_id
    require(map_path==destination/'ACCEPTED_ATTEMPTS.v2.json' and map_receipt_path==destination/'ACCEPTED_ATTEMPTS_RECEIPT.json','Use the exact per-job map paths required by the sequential gate')
    require(not any(p.is_symlink() for dest in (map_path,map_receipt_path) for p in (dest,*dest.parents)), 'Symlink map output forbidden')
    # Accepted replay is read-only after full canonical map verification.
    if Path(map_receipt_path).exists():
        resolved = load_attempt_resolution(root, run_dir, map_receipt_path, events, w.get)
        require(load(map_receipt_path, root)['map']['path'] == str(map_path.relative_to(root)), 'Replay requested a different map path')
        return load(run_dir / 'results' / job_id / 'ARCHIVE_RECEIPT.json', root)
    mapping = load(run_dir / 'LINEAGE_INPUTS.json', root)
    mapping_sha = sha(read(run_dir / 'LINEAGE_INPUTS.json', root))
    indexed = {e['id']: e for e in events}
    require(mapping_sha in indexed[start['event_id']]['outputs'] and w.get(mapping_sha) == read(run_dir / 'LINEAGE_INPUTS.json', root), 'Original lineage map not retained')
    item = prepare_job(job, mapping, ready, run_dir, root)
    sid, receipt = item['receipt']['session_id'], item['receipt']
    # Every other logical review is already accepted; no SID can be reused.
    from runner_capacity_v2 import prerequisites, predecessor
    sessions = prerequisites(root, run_dir, ready, events, w.get)
    prior = predecessor(root,run_dir,ready,events,w.get)
    require(sid in sessions and sessions[sid] == ready['attempt'], 'Replacement SID conflicts with prior attempt')
    known = frozen.index(events)
    for version in item['versions']:
        parent = known.get(version['entry_id'])
        require(parent and parent['id'] == version['assigned_event'] and parent['payload']['entry']['entity'] == version['entity'], 'Assigned lineage parent mismatch')
        require(any(a['sha256'] == version['sha256'] for a in parent['payload']['entry']['artifacts']), 'Assigned exact version absent')
    item['capture'] = capture_job(w, item, ready['ready_event_id'], run_dir, root)
    indexed = {e['id']: e for e in w.events()}
    frozen.verify_files(item['files'], root)
    frozen.canonical_capture_check(item['capture'], indexed, w)
    for f in item['files']:
        require(w.put(read(root / f['path'], root)) == f['sha256'], 'Canonical output differs')
    prompt_sha = w.put(read(root / job['prompt_file'], root))
    rubric_path = run_dir / 'RUBRIC.txt'; rubric_sha = sha(read(rubric_path, root))
    require(any(f['path'] == str(rubric_path.relative_to(root)) and f['sha256'] == rubric_sha for f in start['files']), 'Original rubric not frozen')
    w.put(read(rubric_path, root))
    cap_sha = w.put(encode(item['capture']))
    accepted = receipt['status'] == runner.COMPLETE
    status = 'REVIEW_ARCHIVED' if accepted else 'QUARANTINED_REVIEW_ARCHIVED_MISSING'
    history = {'accepted_attempt': 2 if accepted else None, 'physical_attempt': 2,
               'attempt_path': str(ready['attempt'].relative_to(root)),
               'replacement_ready_event_id': ready['ready_event_id'], 'failed_attempt_event_id': ready['failed_attempt']['event_id']}
    event_request = {'kind': 'research.selection.review.completed' if accepted else 'research.selection.review.quarantined',
                    'actor': {'id': sid, 'role': 'AI'}, 'session_id': sid, 'run_id': run_dir.name,
                    'operation_id': run_dir.name + ':' + job_id, 'attempt_id': 'replacement-review-v2',
                    'timestamp': receipt['completed_at'],
                    'parents': list(dict.fromkeys([start['event_id'], ready['ready_event_id'], ready['failed_attempt']['event_id']] + ([prior['map_event_id']] if prior else []) + [v['assigned_event'] for v in item['versions']] + item['capture']['evidence_events'])),
                    'bindings': start['bindings'], 'inputs': [prompt_sha, rubric_sha],
                    'outputs': [f['sha256'] for f in item['files']] + [cap_sha],
                    'payload': {'status': status, 'job_id': job_id, 'phase': 'individual', 'files': item['files'],
                                'versions': item['versions'], 'capture_sha256': cap_sha, 'quality_flags': receipt['quality_flags'],
                                'response': item['value'], 'boundary': item['capture']['boundary'], **history}}
    ev = w.append(event_request, run_dir.name + ':' + job_id + ':review-archive-attempt-002-v2')
    indexed[ev['id']] = ev
    entry = frozen.base_entry(run_dir.name + ':' + job_id + ':evaluation-v1', item['versions'][0]['entity'],
                              'evaluation' if accepted else 'cli_attempt',
                              'Свежий отзыв после одной явно принятой замены пустой capacity-попытки; первая ошибка сохранена.' if accepted else 'Единственная замена сохранена без принятого отзыва; повтор не разрешён.')
    entry.update(parents=[v['entry_id'] for v in item['versions']], evidence=[ev['id'], ready['failed_attempt']['event_id'], ready['ready_event_id']],
                 occurred_at=receipt['completed_at'], actor='Fresh Codex review ' + sid, workflow=run_dir.name,
                 configuration={'requested': {k:job[k] for k in ('model','effort','service_tier')}, 'observed': item['proof']['configurations']},
                 artifacts=[{'path':f['path'],'sha256':f['sha256'],'role':'review-output'} for f in item['files']],
                 gaps=[BOUNDARY, 'Earlier capacity failure is not an assessment. Backend computation is not attested.'])
    if accepted:
        entry['assessment'] = {'versions':[{'entry_id':v['entry_id'],'sha256':v['sha256']} for v in item['versions']],
                               'judge':{'requested':{'profile_id':job['profile_id'],'role':job['role'],**entry['configuration']['requested']},'observed':item['proof']['configurations']},
                               'rubric_sha256':rubric_sha,'prompt_sha256':prompt_sha,'order':[v['entry_id'] for v in item['versions']],
                               'verdict':item['value']['recommendation'],'rationale':item['value']['reason_ru'], 'round':run_dir.name,
                               'scores':item['value'].get('scores'), 'ordered_blind_ids':[v['blind_id'] for v in item['versions']]}
    else:
        entry['attempt'] = {'job_id':job_id,'status':status,'quality_flags':receipt['quality_flags'],'session_id':sid}
    lineage_api = lineage_api or frozen.append_lineage
    lev = lineage_api(w, entry, sid, known, indexed)
    output = {'status':status,'job_id':job_id,'session_id':sid,'event_id':ev['id'],
              'lineage_event_id':lev['id'],'lineage_entry_id':entry['id'],'files':item['files'],
              'capture_sha256':cap_sha,'capture_status':item['capture']['status'],'input_event_id':start['event_id'], **history}
    lane_receipt = run_dir / 'results' / job_id / 'ARCHIVE_RECEIPT.json'
    save_once(lane_receipt, output, root); w.put(read(lane_receipt, root))
    if not accepted: return output
    mapping = {'schema':'selection-accepted-attempts.v2','logical_job_id':job_id,'input_event_id':start['event_id'],
               'ready_event_id':ready['ready_event_id'],'failed_attempt':ready['failed_attempt'],
               'accepted_attempt':{'number':2,'path':history['attempt_path'],'session_id':sid,'event_id':ev['id'],'files':item['files']}}
    save_once(map_path, mapping, root)
    map_ref = descriptor(root,map_path); ready_ref = descriptor(root,Path(ready_receipt))
    for item in (map_ref,ready_ref): require(w.put(read(root / item['path'],root)) == item['sha256'], 'Map object differs')
    mapped = w.append({'kind':'research.selection.accepted_attempts.mapped','actor':{'id':'selection-archive','role':'tool'},
                       'session_id':'selection-archive','run_id':run_dir.name,'operation_id':run_dir.name+':'+job_id,
                       'attempt_id':'accepted-attempt-map-v2','parents':[ready['ready_event_id'],ready['failed_attempt']['event_id'],ev['id'],lev['id']],
                       'bindings':start['bindings'],'outputs':[map_ref['sha256'],ready_ref['sha256']],
                       'payload':{'status':'ACCEPTED_ATTEMPTS_MAP_ARCHIVED','logical_job_id':job_id,'accepted_attempt':2,'preserved_failed_attempts':1}}, run_dir.name+':'+job_id+':accepted-attempt-map-v2')
    result = {'status':'ACCEPTED_ATTEMPTS_MAP_ARCHIVED','logical_job_id':job_id,'event_id':mapped['id'],'map':map_ref,'ready_receipt':ready_ref}
    save_once(map_receipt_path,result,root)
    load_attempt_resolution(root,run_dir,map_receipt_path,list(w.events()),w.get)
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ready-receipt',type=Path,required=True)
    parser.add_argument('--map',type=Path,required=True)
    parser.add_argument('--map-receipt',type=Path,required=True)
    parser.add_argument('--root',type=Path,default=ROOT)
    parser.add_argument('--run-dir',type=Path,default=RUN)
    parser.add_argument('--check-only',action='store_true')
    args = parser.parse_args()
    archive = frozen.Archive(args.root / 'research/archive')
    if args.check_only:
        ready = load_ready(args.root,args.run_dir,args.ready_receipt,list(archive.events()),archive.get)
        prepare_job(ready['job'],load(args.run_dir/'LINEAGE_INPUTS.json',args.root),ready,args.run_dir,args.root)
        result = {'status':'REPLACEMENT_ARCHIVE_CHECK_ONLY_NO_WRITES'}
    else:
        with (args.run_dir/'archive-reviews.lock').open('a') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
            with archive.writer() as w:
                result = accept_with_writer(args.root,args.run_dir,args.ready_receipt,args.map,args.map_receipt,w)
    print(json.dumps({'status':result['status'],'event_id':result.get('event_id')},ensure_ascii=False))


if __name__ == '__main__': main()
