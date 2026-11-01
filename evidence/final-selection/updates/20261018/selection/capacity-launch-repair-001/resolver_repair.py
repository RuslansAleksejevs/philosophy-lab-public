"""Explicit physical003/002 repair; preserve original v2 plans and all failures."""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
RUN = HERE.parent
ROOT = RUN.parents[1]
V2 = RUN / 'capacity-resume-20261018/replacement-v2'
sys.path.insert(0, str(V2))
import resolver_v2 as prior
JOBS, SETTINGS = prior.JOBS, prior.SETTINGS
TARGETS = {'M12-N2': 3, 'M13-N2': 2}
runner, module = prior.runner, prior.module
require, strict, encode, sha = prior.require, prior.strict, prior.encode, prior.sha
descriptor, file_bytes, Evidence = prior.descriptor, prior.file_bytes, prior.Evidence
EXPECTED_STDERR = [
    'WARNING: proceeding, even though we could not create PATH aliases: Operation not permitted (os error 1)\n',
    'Error: failed to initialize in-process app-server client: Operation not permitted (os error 1)\n',
]


def inspect_local_failure(root, run, job):
    """No model, archive or prompt read; inspect exact local initialization evidence."""
    root, run = Path(root), Path(run)
    attempt = run / 'results/M12-N2/attempt-002'
    require(job['id'] == 'M12-N2', 'Only the fixed local initialization failure')
    names = {'launch.json', 'failure.json', 'stderr.json', 'visible-events.jsonl'}
    require({p.name for p in attempt.iterdir()} == names, 'Local002 has extra/output/missing files')
    refs = [descriptor(root, attempt / name) for name in sorted(names)]
    data = {Path(x['path']).name: file_bytes(root, x) for x in refs}
    failure, launch, stderr = (strict(data[n]) for n in ('failure.json', 'launch.json', 'stderr.json'))
    require(data['visible-events.jsonl'] == b'', 'Local002 has visible session/events')
    require(failure['status'] == runner.FAILED and failure['session_id'] is None and failure['automatic_retry'] is False, 'Local002 not the preserved no-session failure')
    require(failure['process_state'] == {'process_stopped': True, 'stderr_drained': True, 'exit_code': 1, 'forced_kill': False}, 'Local002 process/capture incomplete')
    require(stderr == {'lines': EXPECTED_STDERR, 'exit_code': 1}, 'Local002 error is not exact app-server initialization EPERM')
    for item in (failure, launch):
        require(item['job_id'] == job['id'] and item['physical_attempt'] == 2, 'Local002 identity differs')
        require(all(item[k] == job[v] for k, v in [('prompt_sha256','prompt_sha256'),('schema_sha256','schema_sha256'),('requested_model','model'),('requested_effort','effort'),('requested_service_tier','service_tier')]), 'Local002 inputs/config differ')
        argv = item['argv']
        require(argv == runner.command(job, attempt, root, executable=argv[0]) and item['argv_sha256'] == sha(__import__('json').dumps(argv, separators=(',', ':')).encode()), 'Local002 command differs')
    require(failure['replacement_ready_event_id'] == launch['replacement_ready_event_id'] and failure['failed_attempt_event_id'] == launch['failed_attempt_event_id'], 'Local002 history differs')
    return {'job_id': job['id'], 'physical_attempt': 2, 'session_id': None,
            'failure_kind': 'cli_initialization_failed_no_observed_session',
            'files': refs, 'observed_sessions': 0, 'observed_turns': 0,
            'observed_assistant_outputs': 0, 'provider_model_calls': 'unknown',
            'native_proof': None, 'review_accepted': False,
            'replacement_ready_event_id': failure['replacement_ready_event_id'],
            'failed_attempt_event_id': failure['failed_attempt_event_id']}


def load_repair(root, run, receipt_path, events, get_object):
    root, run = Path(root).resolve(), Path(run).resolve()
    events = list(events); e = Evidence(root, run, events, get_object)
    receipt_path = runner.regular(receipt_path, run)
    receipt = strict(receipt_path.read_bytes())
    require(receipt['status'] == 'LOCAL_LAUNCH_REPAIR_ACCEPTED_BOUNDED', 'Local launch repair not accepted')
    ev = e.event(receipt['event_id'], 'research.selection.local_launch_repair.accepted')
    require(ev['payload']['status'] == receipt['status'], 'Repair event status differs')
    plan = strict(e.bound(receipt['plan'], ev))
    require(plan['schema'] == 'selection-local-launch-repair.v1' and plan['target_attempts'] == TARGETS and plan['automatic_retry'] is False, 'Only fixed003/002 without automatic retry')
    require(set(plan['original_ready_receipts']) == set(JOBS), 'Both original ready receipts required')
    old = {}
    for jid in JOBS:
        ref = plan['original_ready_receipts'][jid]
        e.bound(ref, ev)
        value = prior.load_ready(root, run, root / ref['path'], events, get_object)
        require(value['job']['id'] == jid, 'Wrong original logical job')
        old[jid] = value
    require(len({x['input_event_id'] for x in old.values()}) == 1 and receipt['input_event_id'] == old[JOBS[0]]['input_event_id'], 'Original input changed')
    require(old[JOBS[0]]['plan']['authorization'] == old[JOBS[1]]['plan']['authorization'], 'Original ready authorizations differ')
    require(receipt['bindings'] == ev['bindings'] == old[JOBS[0]]['receipt']['bindings'] == old[JOBS[1]]['receipt']['bindings'], 'Repair bindings changed')
    local = plan['local_launch_failure']
    failure = e.event(local['event_id'], 'research.selection.local_launch_failure')
    require(failure['bindings'] == receipt['bindings'], 'Local failure bindings differ')
    require(failure['payload']['status'] == 'LOCAL_LAUNCH_FAILURE_PRESERVED' and failure['payload']['logical_job_id'] == JOBS[0] and failure['payload']['physical_attempt'] == 2 and failure['payload']['session_id'] is None, 'Wrong local failure event')
    proof = inspect_local_failure(root, run, old[JOBS[0]]['job'])
    require(local['files'] == proof['files'], 'Local failure files differ')
    for row in local['files']: e.bound(row, failure)
    e.bound(local['inspection'], failure)
    require(proof['replacement_ready_event_id'] == old[JOBS[0]]['ready_event_id'] and proof['failed_attempt_event_id'] == old[JOBS[0]]['failed_attempt']['event_id'], 'Local failure is not the original approved attempt002')
    require({old[JOBS[0]]['input_event_id'], old[JOBS[0]]['ready_event_id'], old[JOBS[0]]['failed_attempt']['event_id']} <= set(failure['parents']), 'Local failure dropped original history')
    stop = strict(e.bound(plan['preserved_stop'], ev))
    require(stop['job_id'] == JOBS[0] and stop['reason'] == 'Unclassified CLI exit or missing identity' and stop['automatic_retry'] is False, 'Wrong preserved STOP')
    require({failure['id'], *[v['ready_event_id'] for v in old.values()], receipt['input_event_id']} <= set(ev['parents']), 'Repair dependencies missing')
    require(receipt['files'] and len(receipt['files']) == len({r['path'] for r in receipt['files']}), 'Repair files missing/duplicate')
    for ref in receipt['files']: e.bound(ref, ev)
    required = {str((run/'capacity-launch-repair-001'/n).relative_to(root)) for n in ('resolver_repair.py','runner_repair.py','ready_repair.py','test_launch_repair.py','LAUNCH_TESTS.json')}
    require(required <= {r['path'] for r in receipt['files']} and receipt['plan'] in receipt['files'], 'Repair launch code/tests/plan not frozen')
    return {'receipt': receipt, 'receipt_ref': descriptor(root, receipt_path), 'plan': plan, 'event': ev,
            'original_ready': old, 'local_launch_failure': local}


def load_ready(root, run_dir, receipt_path, events, get_object, job_id):
    require(job_id in JOBS, 'Only the two original replacement jobs')
    repair = load_repair(root, run_dir, receipt_path, events, get_object)
    ready = dict(repair['original_ready'][job_id])
    ready.update(attempt=Path(run_dir)/'results'/job_id/f'attempt-{TARGETS[job_id]:03}',
                 physical_attempt=TARGETS[job_id], original_ready_event_id=ready['ready_event_id'],
                 ready_event_id=repair['event']['id'], repair=repair,
                 repair_receipt=repair['receipt_ref'], local_launch_failure=repair['local_launch_failure'])
    return ready


def resolve_job(job, run_dir, root, resolution):
    number = TARGETS.get(job['id'], 1)
    if job['id'] in JOBS:
        require(resolution['schema'] == 'selection-capacity-resolution.v3' and set(resolution['exceptions']) == set(JOBS), 'Accepted explicit003/002 resolution required')
        selected = resolution['exceptions'][job['id']]
        require(selected['job'] == job and selected['accepted_attempt']['number'] == number, 'Mapped logical job/attempt differs')
    lane = Path(run_dir)/'results'/job['id']
    return {'attempt': lane/f'attempt-{number:03}', 'attempt_number': number,
            'archive_receipt': lane/'ARCHIVE_RECEIPT.json', 'capture_receipt': lane/'CAPTURE_RECEIPT.json'}


def load_attempt_resolution(root, run_dir, map_receipt_path, events, get_object):
    from resolver_map_repair import load_attempt_resolution as load
    return load(root, run_dir, map_receipt_path, events, get_object)


def load_resolution(root, run_dir, map_receipt_path, events, get_object):
    from resolver_map_repair import load_resolution as load
    return load(root, run_dir, map_receipt_path, events, get_object)
