"""Explicit finite-selection closure with a named capacity-v4 validator. No content decisions, dispatch or services.

Only the CLI/execute entry point opens one writer. Core checkpoint creation is
disabled unless root explicitly allows its standard derived-view updates.
"""
from pathlib import Path
import argparse
import copy
import json
import os
import sys
import uuid

from resolver_v2 import ROOT, RUN, HERE, load_resolution
sys.path.insert(0, str(RUN / 'finalization-preparation'))
import validate_capacity_v4 as validation
import finalize_scaffold as scaffold
from validate_final import Check, Invalid, STAGES, require, strict, encode, sha

SUMMARY_FIELDS = ('question', 'outcome', 'contribution', 'criticism', 'limitations',
                  'next_step', 'method_change', 'comparability', 'coverage_boundary')


def save_once(path, data):
    """Publish complete fsynced bytes atomically; never replace an old artifact."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.parent / ('.closure-publish-' + uuid.uuid4().hex + '.tmp')
    try:
        with temp.open('xb') as handle:
            handle.write(data); handle.flush(); os.fsync(handle.fileno())
        try:
            os.link(temp, path)
        except FileExistsError:
            require(not path.is_symlink() and path.read_bytes() == data, 'Existing artifact differs; preserved: ' + str(path))
        fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try: os.fsync(fd)
        finally: os.close(fd)
    finally:
        if temp.exists(): temp.unlink()


def descriptor(root, path, data):
    return {'path': str(path.relative_to(root)), 'sha256': sha(data), 'bytes': len(data)}


def check_request(existing, request):
    require(all(existing.get(key) == value for key, value in request.items()), 'Existing canonical event differs from closure request')


def close_with_writer(root, run_dir, request_artifact, w, *, allow_checkpoint_derived_updates=False,
                      lineage_api=None, checkpoint_api=None, validator_api=validation.validate, map_receipt=None):
    """Consume root's immutable request using the caller's single audited writer."""
    root, run_dir = Path(root).resolve(), Path(run_dir).resolve()
    def checker(events=None):
        return Check(root, run_dir, list(w.events()) if events is None else events, w.get)
    c = checker()
    request_bytes = c.read(request_artifact['path'], request_artifact['sha256'])
    require(len(request_bytes) == request_artifact['bytes'], 'Request byte count mismatch')
    req = strict(request_bytes)
    require(req['schema'] == 'selection-closure-request.v1' and req['run_id'] == run_dir.name, 'Closure request identity mismatch')
    require(isinstance(req['session_id'], str) and req['session_id'], 'Actual coordinator session required')
    require(type(allow_checkpoint_derived_updates) is bool, 'Derived-update permission must be explicit bool')
    require(set(req['stages']) == set(STAGES[1:]), 'Explicit four remaining stage specifications required')
    require(req['selection_gate_event_ids'] and len(set(req['selection_gate_event_ids'])) == len(req['selection_gate_event_ids']), 'Nonempty unique actual selection gates required')
    require(set(req['coordinator_configuration']) >= {'requested', 'observed'}, 'Root coordinator configuration required')
    start = c.load('START_RECEIPT.json', run_dir)
    first = c.event(start['run_start_event'], 'operation.started')
    require(first['payload']['protocol'] == 'philosophy-round.v1' and first['payload']['purpose'] == 'research', 'Expected original research operation')
    require(start['bindings'] == first['bindings'], 'Original operation binding mismatch')
    require(req['session_id'] == first['session_id'], 'Closure must retain the original coordinator session')
    gates = [c.event(eid)['id'] for eid in req['selection_gate_event_ids']]
    require(map_receipt is not None, 'Explicit capacity-v4 map receipt required')
    resolution = load_resolution(root, run_dir, map_receipt, list(w.events()), w.get)
    require(resolution['map_event_id'] in gates, 'Actual accepted-attempt map must be an explicit selection gate')
    validator_spec = req['validator']
    require(validator_spec['name'] == 'capacity-v4', 'Explicit v4 validator required')
    require(c.path(validator_spec['code']['path']) == HERE / 'validate_capacity_v4.py', 'Unexpected validator code path')
    c.read(validator_spec['code']['path'], validator_spec['code']['sha256'])
    require(validator_spec['map_receipt'] == descriptor(root, Path(map_receipt).resolve(), Path(map_receipt).read_bytes()), 'Request/map receipt mismatch')
    outputs = {}
    for name in ('final_plan', 'validation_report', 'final_receipt'):
        path = c.path(req['outputs'][name])
        require(path.is_relative_to(run_dir), 'Closure output must remain inside run')
        outputs[name] = path
    require(len(set(outputs.values())) == 3 and outputs['final_receipt'] == run_dir / 'FINAL_RECEIPT.json', 'Distinct outputs and canonical FINAL_RECEIPT path required')
    require(outputs['final_plan'] != c.path(req['plan_input']['path']), 'Preserve input plan; use a separate finalized-plan path')
    require(isinstance(req['export_files'], list), 'Explicit export-files list required')
    generated = req.get('export_generated', [])
    require(isinstance(generated, list) and len(generated) == len(set(generated)) and set(generated) <= {'final_plan', 'validation_report', 'closure_request'}, 'Unknown or duplicate explicit generated export')
    pending = req.get('pending_goal_steps', list(scaffold.DEFAULT_PENDING_GOAL_STEPS))
    require(isinstance(pending, list) and len(pending) == len(set(pending)) and all(isinstance(x, str) and x.strip() for x in pending), 'Invalid pending goal list')

    # Read every explicit input before appending any event. No recursive scan.
    artifacts = [request_artifact, req['plan_input'], req['checkpoint']['summary'], validator_spec['code'], validator_spec['map_receipt']] + req['export_files']
    for spec in req['stages'].values():
        require(spec['files'] and spec['evidence_event_ids'], 'Stage needs explicit artifacts and actual evidence')
        for eid in spec['evidence_event_ids']: c.event(eid)
        artifacts += spec['files']
    input_plan_data = c.read(req['plan_input']['path'], req['plan_input']['sha256'])
    plan = strict(input_plan_data)
    language = plan['plain_language_review']
    artifacts.append(language['artifact'])
    attestation_data = c.read(language['artifact']['path'], language['artifact']['sha256'])
    attestation = strict(attestation_data)
    require(attestation.get('concrete_plain_ru_2_to_3_sentences_each') is True and attestation.get('decisions_sha256') == sha(encode(plan['decisions'])), 'Missing/stale root plain-language attestation')
    decision_evidence = list(dict.fromkeys(e for d in plan['decisions'] for e in d['evidence_event_ids']))
    for eid in decision_evidence: c.event(eid)
    summary_data = c.read(req['checkpoint']['summary']['path'], req['checkpoint']['summary']['sha256'])
    summary = strict(summary_data)
    require(all(isinstance(summary.get(k), str) and summary[k].strip() for k in SUMMARY_FIELDS), 'Core checkpoint summary fields missing')
    require(summary['outcome'] == 'CONTINUE', 'Administrative research checkpoint requires explicit CONTINUE scope')
    coverage = req['checkpoint']['coverage_event_ids']
    require(isinstance(coverage, list) and len(coverage) == len(set(coverage)) and start['preserved_standard_capture_gap'] in coverage, 'Original coverage gap must be retained')
    for eid in coverage: c.event(eid, 'capture.coverage')
    history = [e for e in c.events.values() if e.get('run_id') == run_dir.name]
    checkpoints = [e for e in history if e['kind'] == 'checkpoint']
    require(len(checkpoints) <= 1, 'Conflicting existing core checkpoints')
    checkpoint_returns = [e for e in history if e['kind'] == 'research.selection.closure.checkpoint_api_returned']
    require(len(checkpoint_returns) <= 1, 'Duplicate checkpoint API return markers')
    standard_stages = [e for e in history if e['kind'] == 'round.stage']
    checkpoint_parents = [first['id']] + [e['id'] for e in standard_stages] + coverage
    if checkpoints:
        cp = checkpoints[0]
        require(cp['parents'] == checkpoint_parents and cp['outputs'] == [req['checkpoint']['summary']['sha256']] and cp['payload']['summary'] == summary and cp['payload']['capture_status'] == 'INCOMPLETE' and cp['payload']['truth_status'] == 'NOT_CERTIFIED', 'Existing checkpoint incompatible; do not overwrite')
        terminals = [e for e in history if e['kind'] == 'operation.interrupted' and e['payload'].get('checkpoint') == cp['id']]
        require(len(terminals) <= 1, 'Duplicate core terminal')
        if checkpoint_returns:
            marker = checkpoint_returns[0]
            require(marker['payload']['status'] == 'STANDARD_CHECKPOINT_API_RETURNED' and marker['payload']['checkpoint_event_id'] == cp['id'] and marker['payload']['request_sha256'] == request_artifact['sha256'] and marker['outputs'] == [req['checkpoint']['summary']['sha256']] and cp['id'] in marker['parents'], 'Checkpoint API return marker mismatch')
        needs_checkpoint = not terminals or (allow_checkpoint_derived_updates and not checkpoint_returns)
    else:
        require(not checkpoint_returns, 'Checkpoint return marker has no checkpoint')
        needs_checkpoint = True
    require(not needs_checkpoint or allow_checkpoint_derived_updates, 'Core checkpoint absent/incomplete: explicit --allow-checkpoint-derived-updates is required for standard API')

    file_bytes, explicit_files = {}, []
    for row in artifacts:
        require(isinstance(row, dict) and {'path', 'sha256', 'bytes'} <= set(row) and type(row['bytes']) is int, 'Input manifest requires exact path/hash/bytes')
        data = c.read(row['path'], row['sha256'])
        require(len(data) == row['bytes'], 'Input byte count mismatch')
        require(c.path(row['path']) not in outputs.values(), 'An output path collides with a preserved input')
        if row['path'] in file_bytes:
            require(file_bytes[row['path']] == data, 'Conflicting duplicate input')
        else:
            file_bytes[row['path']] = data
            explicit_files.append({k: row[k] for k in ('path', 'sha256', 'bytes')})
    for row in explicit_files:
        require(w.put(file_bytes[row['path']]) == row['sha256'], 'Archive stored different explicit input bytes')
    stage_evidence = [eid for spec in req['stages'].values() for eid in spec['evidence_event_ids']]
    intake_req = {'kind': 'research.selection.closure.inputs', 'actor': {'id': req['session_id'], 'role': 'AI'},
                  'session_id': req['session_id'], 'run_id': run_dir.name, 'operation_id': run_dir.name,
                  'attempt_id': 'finite-closure-v1', 'bindings': start['bindings'],
                  'parents': list(dict.fromkeys([start['event_id']] + gates + decision_evidence + stage_evidence)),
                  'outputs': list(dict.fromkeys(x['sha256'] for x in explicit_files)),
                  'payload': {'files': explicit_files, 'request_sha256': request_artifact['sha256'],
                              'allow_checkpoint_derived_updates': allow_checkpoint_derived_updates,
                              'boundary': scaffold.BOUNDARY}}
    intake = w.append(intake_req, run_dir.name + ':closure-inputs:v1')
    if language.get('event_id'):
        existing = checker().event(language['event_id'])
        require(language['artifact']['sha256'] in existing['outputs'] and set(decision_evidence) <= checker().ancestors(existing['id']), 'Previously accepted plain-language event does not bind exact artifact/dependencies')
    else:
        language_req = {'kind': 'research.selection.language_check', 'actor': {'id': req['session_id'], 'role': 'AI'},
                        'session_id': req['session_id'], 'run_id': run_dir.name, 'operation_id': run_dir.name,
                        'attempt_id': 'finite-closure-v1', 'bindings': start['bindings'],
                        'parents': list(dict.fromkeys([intake['id']] + decision_evidence)),
                        'outputs': [language['artifact']['sha256']],
                        'payload': {'decisions_sha256': attestation['decisions_sha256'], 'boundary': 'Root supplied exact plain-language assertion; writer performed no semantic review.'}}
        language['event_id'] = w.append(language_req, run_dir.name + ':closure-language-check:v1')['id']
    final_plan_data = encode(plan)
    save_once(outputs['final_plan'], final_plan_data)
    plan_artifact = descriptor(root, outputs['final_plan'], final_plan_data)
    require(w.put(final_plan_data) == plan_artifact['sha256'], 'Finalized-plan object mismatch')
    report = validator_api(root, run_dir, plan, list(w.events()), w.get, map_receipt=map_receipt)
    require(report.get("validator") == "capacity-v4" and report.get("preserved_failed_attempts") == 2 and report.get("replacement_map_event_id") == resolution["map_event_id"], "Validator did not attest explicit capacity mapping")
    report_data = encode(report)
    save_once(outputs['validation_report'], report_data)
    report_artifact = descriptor(root, outputs['validation_report'], report_data)
    require(w.put(report_data) == report_artifact['sha256'], 'Validation-report object mismatch')

    stage_ids = {}
    for stage in STAGES[1:]:
        snapshot = list(w.events())
        same = [e for e in snapshot if e.get('run_id') == run_dir.name and e['kind'] == 'research.selection.stage' and e['payload']['stage'] == stage]
        require(len(same) <= 1, 'Duplicate existing custom stage')
        # The true historical archive prefix reconstructs an identical replay.
        prefix = snapshot[:next(i for i, e in enumerate(snapshot) if e['id'] == same[0]['id'])] if same else snapshot
        spec = req['stages'][stage]
        stage_files = list(spec['files']) + ([plan_artifact] if stage == 'decision' else [])
        evidence = list(dict.fromkeys(spec['evidence_event_ids'] + [intake['id']]))
        built = scaffold.stage_request(checker(prefix), report, stage, req['session_id'], stage_files, evidence)
        if same: check_request(same[0], built['event'])
        stage_ids[stage] = w.append(built['event'], built['delivery_key'])['id']

    if lineage_api is None:
        sys.path.insert(0, str(root / 'scripts'))
        import essay_lineage as lineage_api
    c = checker(); mapping = c.load('LINEAGE_INPUTS.json', run_dir)
    known = lineage_api.index(c.events.values())
    selected_lineages = {}
    decision_event = c.event(stage_ids['decision'], 'research.selection.stage')
    for decision in plan['decisions']:
        cid = decision['candidate_id']; row = mapping[cid]
        relevant = [c.event(eid, 'essay.lineage.entry') for eid in report['review_lineage_event_ids']
                    if any(x['entry_id'] == row['assigned_entry'] for x in c.events[eid]['payload']['entry']['assessment']['versions'])]
        entry = lineage_api.base_entry(run_dir.name + ':' + cid + ':final-selection-v1', row['entity'], 'selection', ' '.join(decision['reason_ru']))
        entry.update(parents=[row['assigned_entry']] + [e['payload']['entry']['id'] for e in relevant],
                     artifacts=[{'path': row['version']['path'], 'sha256': row['version']['sha256'], 'role': 'frozen-current-version'},
                                {'path': plan_artifact['path'], 'sha256': plan_artifact['sha256'], 'role': 'selection-rationale'}],
                     evidence=list(dict.fromkeys([decision_event['id']] + decision['evidence_event_ids'])),
                     occurred_at=decision_event['timestamp'], actor='AI coordinator ' + req['session_id'],
                     configuration=copy.deepcopy(req['coordinator_configuration']), workflow=run_dir.name,
                     decision={'action': decision['selection'], 'reason': decision['reason_ru'], 'originals_retained': True},
                     gaps=[scaffold.BOUNDARY])
        # Selected originals already have accepted lineage; require stored bytes.
        require(c.read(row['version']['path'], row['version']['sha256']) == c.obj(row['version']['sha256']), 'Selected original absent from object store')
        event = lineage_api.append(w, entry, req['session_id'], known, c.events)
        c.events[event['id']] = event
        selected_lineages[cid] = event['id']

    if needs_checkpoint:
        if checkpoint_api is None:
            sys.path.insert(0, str(root / 'scripts'))
            from philosophy_round import checkpoint as checkpoint_api
        cp = checkpoint_api(root, w, run_dir.name, req['checkpoint']['summary']['path'], coverage, incomplete=True)
    else:
        cp = checkpoints[0]
    c = checker(); cp = c.event(cp['id'], 'checkpoint')
    require(cp['parents'] == checkpoint_parents and cp['outputs'] == [req['checkpoint']['summary']['sha256']] and cp['payload']['summary'] == summary and cp['payload']['capture_status'] == 'INCOMPLETE', 'Standard checkpoint API returned incompatible evidence')
    require(any(e['kind'] == 'operation.interrupted' and e.get('run_id') == run_dir.name and e['payload'].get('checkpoint') == cp['id'] for e in c.events.values()), 'Core terminal absent after checkpoint')
    if needs_checkpoint:
        terminals = [e for e in c.events.values() if e['kind'] == 'operation.interrupted' and e.get('run_id') == run_dir.name and e['payload'].get('checkpoint') == cp['id']]
        require(len(terminals) == 1, 'Exactly one actual checkpoint terminal required')
        returned = {'kind': 'research.selection.closure.checkpoint_api_returned',
                    'actor': {'id': req['session_id'], 'role': 'AI'}, 'session_id': req['session_id'],
                    'run_id': run_dir.name, 'operation_id': run_dir.name, 'attempt_id': 'finite-closure-v1',
                    'bindings': start['bindings'], 'parents': [cp['id'], terminals[0]['id'], intake['id']],
                    'outputs': [req['checkpoint']['summary']['sha256']],
                    'payload': {'status': 'STANDARD_CHECKPOINT_API_RETURNED', 'checkpoint_event_id': cp['id'],
                                'request_sha256': request_artifact['sha256'],
                                'boundary': 'The permitted standard checkpoint call returned after its derived-view functions. This marker does not certify whole capture or completion of the overall goal.'}}
        w.append(returned, run_dir.name + ':closure-checkpoint-api-returned:v1')
        c = checker()
    exports = list(req['export_files'])
    generated_refs = {'final_plan': plan_artifact, 'validation_report': report_artifact, 'closure_request': request_artifact}
    exports += [generated_refs[key] for key in generated]
    actual_return_markers = [e['id'] for e in c.events.values() if e.get('run_id') == run_dir.name and e['kind'] == 'research.selection.closure.checkpoint_api_returned']
    final = scaffold.final_request(c, report, req['session_id'], plan_artifact, report_artifact,
                                   selected_lineages, cp['id'], gates + actual_return_markers, files=exports, pending_goal_steps=pending)
    final['event']['payload'].update(preserved_failed_attempts=2, accepted_attempt_map_event_id=resolution['map_event_id'],
                                    failed_attempt_event_ids=[x['failed_attempt']['event_id'] for x in resolution['exceptions'].values()])
    end = w.append(final['event'], final['delivery_key'])
    receipt = scaffold.receipt_from_actual_event(checker(), end['id'])
    save_once(outputs['final_receipt'], encode(receipt))
    return receipt


def execute(root, run_dir, request_path, archive, **options):
    root, run_dir, request_path = Path(root).resolve(), Path(run_dir).resolve(), Path(request_path).resolve()
    require(request_path.is_relative_to(run_dir), 'Closure request must be inside run directory')
    data = request_path.read_bytes()
    artifact = descriptor(root, request_path, data)
    with archive.writer() as writer:
        return close_with_writer(root, run_dir, artifact, writer, **options)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--request', required=True, type=Path)
    parser.add_argument('--validator', required=True, choices=['capacity-v4'])
    parser.add_argument('--map-receipt', required=True, type=Path)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--run-dir', type=Path, default=RUN)
    parser.add_argument('--allow-checkpoint-derived-updates', action='store_true', help='Permit the standard checkpoint API to update its derived biography/knowledge views')
    args = parser.parse_args()
    sys.path.insert(0, str(args.root / 'scripts'))
    from research_archive import Archive
    receipt = execute(args.root, args.run_dir, args.request, Archive(args.root / 'research/archive'),
                      allow_checkpoint_derived_updates=args.allow_checkpoint_derived_updates, validator_api=validation.validate, map_receipt=args.map_receipt)
    print(json.dumps({'status': receipt['status'], 'event_id': receipt['event_id'], 'scope': receipt['scope'],
                      'pending_goal_steps': receipt['pending_goal_steps']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
