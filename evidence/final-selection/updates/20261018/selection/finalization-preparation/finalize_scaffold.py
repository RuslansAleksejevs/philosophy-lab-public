"""Pure request builders. No CLI, archive writer, collector, model or decisions.

Root must put artifacts, append each returned request, refresh actual events, then
build the next request. Delivery keys are stable; never replace preserved events.
"""
from validate_final import Check, IDS, STAGES, Invalid, require, strict, sha, encode

BOUNDARY = ('Finite selection and reading-package acceptance only. Exact visible '
            'capture is bounded; the original standard-adapter gap and core '
            'INCOMPLETE checkpoint remain. No whole-provider capture, philosophical '
            'truth/novelty certification, final-three selection or submission. '
            'This receipt does not claim completion of the overall goal or of '
            'project-state update, private GitHub update, or collector restoration.')

DEFAULT_PENDING_GOAL_STEPS = ('project_state_update', 'private_github_update', 'collector_restore')


def checked_export_files(check, files, event_outputs=None):
    """Verify only root's explicit export list; never scan or include the whole run."""
    require(isinstance(files, list), 'Export files must be an explicit list')
    result, paths = [], set()
    for row in files:
        require(isinstance(row, dict) and {'path', 'sha256', 'bytes'} <= set(row), 'Export file needs path, sha256 and bytes')
        require(type(row['bytes']) is int and row['bytes'] >= 0, 'Export byte count must be a nonnegative integer')
        path = check.path(row['path'])
        require(str(path.resolve().relative_to(check.root)) == row['path'], 'Export path must be canonical and repository-relative')
        require(row['path'] not in paths, 'Duplicate export path')
        paths.add(row['path'])
        try:
            data = check.read(row['path'], row['sha256'])
            stored = check.obj(row['sha256'])
        except (OSError, KeyError) as error:
            raise Invalid('Export local file or stored object missing: ' + row['path']) from error
        require(len(data) == row['bytes'] and data == stored, 'Export file bytes differ from local/stored data')
        require(event_outputs is None or row['sha256'] in event_outputs, 'Export file is not bound by actual final event outputs')
        result.append({k: row[k] for k in ('path', 'sha256', 'bytes')})
    return result


def stage_request(check, report, stage, session_id, artifacts, evidence_event_ids):
    require(isinstance(check, Check), 'Audited read-only snapshot required')
    require(report['status'] == 'FINAL_PACKAGE_VALIDATED_BOUNDED', 'Package validation absent')
    require(stage in STAGES[1:] and artifacts and evidence_event_ids, 'Existing question must be preserved; new stages need artifacts and evidence')
    existing = [e for e in check.events.values() if e.get('run_id') == check.run.name and e['kind'] == 'research.selection.stage']
    require([e['payload']['stage'] for e in existing] == list(STAGES[:STAGES.index(stage)]), 'Stage order/replay mismatch')
    require(existing[0]['id'] == report['question_stage_event_id'], 'Original question was replaced')
    for e in existing:
        check.event(e['id'], 'research.selection.stage')
        require(e['bindings'] == report['bindings'], 'Stage method binding mismatch')
    for eid in evidence_event_ids:
        check.event(eid)
    for f in artifacts:
        require(check.read(f['path'], f['sha256']) == check.obj(f['sha256']), 'Stage artifact bytes not stored')
    parents = list(dict.fromkeys([existing[-1]['id'], report['initial_ready_event_id'], report['plain_language_event_id']] + evidence_event_ids))
    ancestors = set().union(*(check.ancestors(eid) for eid in parents))
    require(set(report['review_event_ids']) <= ancestors, 'Stage omits accepted review dependencies')
    require(session_id and isinstance(session_id, str), 'Coordinator session required')
    return {'event': {'kind': 'research.selection.stage', 'actor': {'id': session_id, 'role': 'AI'},
                     'session_id': session_id, 'run_id': check.run.name, 'operation_id': check.run.name,
                     'attempt_id': 'bounded-stages-v1', 'parents': parents, 'bindings': report['bindings'],
                     'outputs': [f['sha256'] for f in artifacts],
                     'payload': {'stage': stage, 'contribution_origin': 'AI', 'evidence_status': 'ARCHIVED_ARTIFACTS_AND_REVIEW_DEPENDENCIES',
                                 'files': artifacts, 'boundary': BOUNDARY}},
            'delivery_key': check.run.name + ':bounded-stage:' + stage}


def final_request(check, report, session_id, plan_artifact, validation_artifact,
                  selection_lineages, checkpoint_event_id, completion_gate_event_ids,
                  *, files=None, pending_goal_steps=None):
    """Build a finite-selection event after actual selection stages and gates.

    completion_gate_event_ids must be nonempty actual selection acceptance gates.
    They need not include subsequent GitHub or collector actions. Those actions can
    depend on this selection receipt. Root may pass the accurate pending goal list;
    even an empty list does not make this helper certify completion of the goal.
    files is root's optional explicit export list; every item is bound in outputs.
    """
    require(report['status'] == 'FINAL_PACKAGE_VALIDATED_BOUNDED', 'Unvalidated final package')
    for name, digest in report['checked_files'].items():
        check.read(name, digest)
    plan_data = check.read(plan_artifact['path'], plan_artifact['sha256'])
    plan = strict(plan_data)
    require(sha(encode(plan)) == report['plan_canonical_sha256'], 'Final plan differs from validated package')
    require(sha(encode(plan['decisions'])) == report['decisions_sha256'], 'Final plan differs from validated decisions')
    require(strict(check.read(validation_artifact['path'], validation_artifact['sha256'])) == report, 'Validation artifact differs from report')
    decisions = {d['candidate_id']: d for d in plan['decisions']}
    stages = [e for e in check.events.values() if e.get('run_id') == check.run.name and e['kind'] == 'research.selection.stage']
    require([e['payload']['stage'] for e in stages] == list(STAGES), 'Exactly five ordered custom stages required')
    require(stages[0]['id'] == report['question_stage_event_id'], 'Original question missing')
    for e in stages:
        check.event(e['id'], 'research.selection.stage')
        require(e['bindings'] == report['bindings'], 'Stage method binding mismatch')
    for left, right in zip(stages, stages[1:]):
        require(left['id'] in check.ancestors(right['id']), 'Stage dependency missing')
    require(set(report['review_event_ids']) <= check.ancestors(stages[-1]['id']), 'Final decision lacks accepted review evidence')
    require(set(selection_lineages) == IDS, 'Exactly 22 final selection lineage events required')
    mapping = check.load('LINEAGE_INPUTS.json', check.run)
    for cid, eid in selection_lineages.items():
        entry = check.event(eid, 'essay.lineage.entry')['payload']['entry']
        require(entry['kind'] == 'selection' and entry['entity'] == mapping[cid]['entity'] and mapping[cid]['assigned_entry'] in entry['parents'], 'Final selection lineage mismatch')
        require(stages[-1]['id'] in entry['evidence'], 'Final selection lineage lacks actual decision stage')
        require(any(f['sha256'] == mapping[cid]['version']['sha256'] and f['path'] == mapping[cid]['version']['path'] for f in entry['artifacts']), 'Final lineage selected different bytes')
        required_review_parents = set()
        for reid in report['review_lineage_event_ids']:
            review_entry = check.event(reid, 'essay.lineage.entry')['payload']['entry']
            if any(x['entry_id'] == mapping[cid]['assigned_entry'] for x in review_entry['assessment']['versions']):
                required_review_parents.add(review_entry['id'])
        require(required_review_parents <= set(entry['parents']), 'Selection lineage omits assessed review parents')
        require(entry['decision']['action'] == decisions[cid]['selection'] and entry['decision']['reason'] == decisions[cid]['reason_ru'], 'Selection lineage differs from final decision')
    cp = check.event(checkpoint_event_id, 'checkpoint')
    require(cp['payload']['capture_status'] == 'INCOMPLETE' and cp['payload']['truth_status'] == 'NOT_CERTIFIED', 'Core gap must remain explicit')
    require(report['preserved_gap_event_id'] in cp['parents'], 'Original core gap not retained')
    require(completion_gate_event_ids, 'Root must supply actual selection acceptance gate events')
    for eid in completion_gate_event_ids:
        check.event(eid)
    for artifact in (plan_artifact, validation_artifact):
        require(check.read(artifact['path'], artifact['sha256']) == check.obj(artifact['sha256']), 'Final artifact not stored')
    require(plan_artifact['sha256'] in stages[-1]['outputs'], 'Decision stage does not bind exact final plan')
    export_files = checked_export_files(check, [] if files is None else files)
    pending = list(DEFAULT_PENDING_GOAL_STEPS) if pending_goal_steps is None else pending_goal_steps
    require(isinstance(pending, list) and all(isinstance(x, str) and x.strip() for x in pending) and len(pending) == len(set(pending)), 'Pending goal steps must be a unique list of nonempty names')
    return {'event': {'kind': 'research.selection.completed', 'actor': {'id': session_id, 'role': 'AI'},
                     'session_id': session_id, 'run_id': check.run.name, 'operation_id': check.run.name,
                     'attempt_id': 'finite-final-v1', 'bindings': report['bindings'],
                     'parents': list(dict.fromkeys([e['id'] for e in stages] + list(selection_lineages.values()) + [checkpoint_event_id] + completion_gate_event_ids)),
                     'outputs': list(dict.fromkeys([plan_artifact['sha256'], validation_artifact['sha256']] + [f['sha256'] for f in export_files])),
                     'payload': {'status': 'SELECTION_COMPLETE_BOUNDED', 'scope': 'finite_selection_only',
                                 'remaining_selection_work': 0, 'pending_goal_steps': list(pending), 'goal_completion_claimed': False,
                                 'files': export_files,
                                 'individual_reviews': 110, 'pairs': report['pairs'], 'pair_reviews': report['pair_reviews'],
                                 'selected': {'main': 8, 'wildcard': 2}, 'protected_originals_unchanged': 42,
                                 'core_capture_status': 'INCOMPLETE', 'preserved_gap_event_id': report['preserved_gap_event_id'],
                                 'boundary': BOUNDARY}},
            'delivery_key': check.run.name + ':finite-complete:v1'}


def receipt_from_actual_event(check, event_id):
    event = check.event(event_id, 'research.selection.completed')
    require(event['payload']['status'] == 'SELECTION_COMPLETE_BOUNDED', 'Finite completion absent')
    require(event['payload'].get('scope') == 'finite_selection_only' and event['payload'].get('remaining_selection_work') == 0 and event['payload'].get('goal_completion_claimed') is False and 'remaining_requested_work' not in event['payload'], 'Actual event must claim only finite selection completion')
    for digest in event['outputs']:
        check.obj(digest)
    files = checked_export_files(check, event['payload']['files'], event['outputs'])
    return {**event['payload'], 'files': files, 'event_id': event['id'], 'parent_event_ids': event['parents'],
            'artifact_sha256': event['outputs']}
