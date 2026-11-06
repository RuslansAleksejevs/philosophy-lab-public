"""Evidence-linked batch configuration view; never translate native effort to UI mode."""
import json
from research_archive import sha


def report(result, ui_observations=()):
    """Render only captured observations. UI requires a separate dated source."""
    ui_observations = [o for o in ui_observations
                       if o.get('session_id') == result['state'].get('parent_session')]
    for observation in ui_observations:
        if not all(observation.get(k) for k in ('source_kind', 'observed_at', 'value', 'evidence')):
            raise ValueError('UI observation needs its own source and time')
    objects = result['objects']
    tasks = {t['id']: t for t in result['manifest']['tasks']}
    children = []
    for event in result['events']:
        if event['kind'] not in ('task.sealed', 'task.checkpoint'):
            continue
        payload = event['payload']
        ref = payload['native_object']
        raw = objects[ref]
        if sha(raw) != ref:
            raise ValueError('configuration evidence hash differs')
        native = json.loads(raw)
        children.append({
            'task_id': payload['task'], 'essay_id': tasks[payload['task']]['essay_id'],
            'stage_outcome': event['kind'],
            'agent_id': native['agent_id'], 'session_id': native['session_id'],
            'requested': tasks[payload['task']]['configuration'],
            'native_observations': native['models'],
            'native_evidence_object': ref, 'native_source_sha256': native['source_sha256'],
            'ui_mode_observed': 'UNKNOWN',
            'ui_mode_scope': 'No child UI observation; not_applicable_subagent in request is a policy label, not an observation.',
        })
    return {
        'protocol': 'claude-configuration-report.v1', 'batch_id': result['batch_id'],
        'dispatcher_session_id': result['state'].get('parent_session', 'UNKNOWN'),
        'dispatcher_ui_mode_requested': result['manifest']['dispatcher_ui_mode_requested'],
        'dispatcher_ui_mode_observed': 'UNKNOWN_FROM_NATIVE_JOURNAL',
        'separate_ui_observations': list(ui_observations),
        'ui_coverage': 'Native journal does not establish slider selection. Consult separately dated UI/user observations; never backfill earlier turns.',
        'workers': children,
        'agent_policy': 'Fixed sequential custom workers; no Workflow, nested agents, or free substantive dispatcher orchestration.',
        'policy_source': 'Bound CLAUDE.md, custom agent definitions and manifest controls; not evidence of actual launches.',
        'limits': 'Native labels are observations, not backend attestation. No scalar ranking of Ultracode against max. Unknown settings stay unknown.',
    }
