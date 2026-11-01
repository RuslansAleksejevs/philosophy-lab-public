"""One explicit empty-capacity replacement. Read-only; no model/archive writes.

Exactly M12-N2 and M13-N2 may resolve to attempt-002. Other108 stay001.
An intent/ready receipt is never an accepted-attempt map.
"""
from pathlib import Path
import importlib.util
import json
import sys

HERE = Path(__file__).resolve().parent
RUN = HERE.parents[1]
ROOT = RUN.parents[1]
JOBS = ('M12-N2', 'M13-N2')
SETTINGS = {'model': 'gpt-6-astra', 'effort': 'ultra', 'service_tier': 'default'}


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


runner = module('selection_capacity_v2_frozen_runner', RUN / 'runner.py')
require = lambda test, message: None if test else (_ for _ in ()).throw(ValueError(message))
sha, encode, strict = runner.digest, runner.encode, runner.strict_json


def path(root, name):
    require(isinstance(name, str) and name and not Path(name).is_absolute() and '..' not in Path(name).parts, 'Relative safe path required')
    return runner.regular(Path(root) / name, Path(root))


def file_bytes(root, item, get_object=None):
    data = path(root, item['path']).read_bytes()
    require(sha(data) == item['sha256'] and len(data) == item['bytes'], 'Bound file changed: ' + item['path'])
    if get_object is not None:
        stored = get_object(item['sha256'])
        require(stored == data and sha(stored) == item['sha256'], 'Stored object differs from local file')
    return data


def descriptor(root, location):
    p = runner.regular(location, Path(root)); data = p.read_bytes()
    return {'path': str(p.relative_to(root)), 'sha256': sha(data), 'bytes': len(data)}


class Evidence:
    def __init__(self, root, run, events, get_object):
        self.root, self.run, self.get = Path(root), Path(run), get_object
        self.events = {e['id']: e for e in events}
        require(len(self.events) == len(events), 'Duplicate canonical event ID')
        self.pos = {e['id']: i for i, e in enumerate(events)}

    def event(self, eid, kind):
        require(eid in self.events, 'Missing actual event: ' + str(eid))
        event = self.events[eid]
        require(event['kind'] == kind and event['run_id'] == self.run.name, 'Wrong canonical event kind/run')
        require(all(p in self.events and self.pos[p] < self.pos[eid] for p in event.get('parents', [])), 'Event has absent/future parent')
        return event

    def bound(self, item, event):
        require(item['sha256'] in event['outputs'], 'File absent from actual event outputs')
        return file_bytes(self.root, item, self.get)

    def ancestors(self,eid):
        seen=set();pending=[eid]
        while pending:
            current=pending.pop()
            if current in seen:continue
            require(current in self.events,'Missing actual ancestor')
            parents=self.events[current].get('parents',[])
            require(all(p in self.events and self.pos[p]<self.pos[current] for p in parents),'Absent/future ancestor')
            seen.add(current);pending+=parents
        return seen


def check_plan(root, run_dir, plan, e, start, job):
    job_id=job['id'];original=e.event(start['event_id'],'research.selection.ready')
    require(job_id in JOBS and plan['schema']=='selection-empty-capacity-replacement.v2' and plan['logical_job_id']==job_id,'Wrong replacement plan identity')
    require(plan['job']==job and all(job[k]==v for k,v in SETTINGS.items()),'Plan job/config differs')
    require(plan['maximum_replacement_attempts']==1 and plan['automatic_retry'] is False and plan['content_changes'] is False,'Only one unchanged replacement')
    require(plan['input_event_id']==start['event_id'],'Plan original input differs')
    failure = e.event(plan['failed_attempt']['event_id'], 'research.selection.transport_failure')
    state = plan['preserved_state']
    expected = {'M12-N2': ('research.selection.transport_disposition.accepted', 'CAPACITY_DISPOSITION_ACCEPTED_BOUNDED'),
                'M13-N2': ('research.selection.stopped', 'SELECTION_INCOMPLETE_CAPACITY_STOP')}[job_id]
    require((state['kind'],state['status']) == expected, 'Wrong preserved-state kind/status')
    disposition = e.event(state['event_id'],state['kind'])
    require(disposition['payload'].get('status') == state['status'], 'Preserved state status differs')
    require({failure['id'],original['id']} <= set(disposition['parents']), 'Preserved state lacks actual failure/input')
    authorization = check_authorization(e,plan['authorization'],original)
    require(disposition['id'] in e.ancestors(authorization['id']), 'Current resume must follow the preserved capacity state')
    require(all(e.pos[c] > e.pos[disposition['id']] for c in plan['authorization']['user_capture_event_ids']), 'User resume capture predates the preserved capacity state')
    require(failure['bindings'] == disposition['bindings'] == start['bindings'], 'Failure/state bindings differ')
    require(plan['replacement_order'] == list(JOBS), 'Only the predeclared sequential order allowed')
    require(plan['predecessor_map_receipt'] == (None if job_id == JOBS[0] else str((run_dir/'capacity-resume-20261018/replacement-v2'/JOBS[0]/'ACCEPTED_ATTEMPTS_RECEIPT.json').relative_to(root))), 'Wrong predecessor map path')
    payload = failure['payload']; failed = plan['failed_attempt']
    require(payload['status'] == 'FAILED_ATTEMPT_PRESERVED' and payload['job_id'] == job_id and payload['failure_kind'] == 'provider_capacity_no_visible_review', 'Wrong failure disposition')
    require(payload['review_accepted'] is False and payload['quota_message_observed'] is False and payload['hidden_computation_claimed'] is False, 'Failure cannot count as review/quota/hidden-computation claim')
    attempt = run_dir / 'results' / job_id / 'attempt-001'
    require(failed['path'] == str(attempt.relative_to(root)), 'Failed attempt path changed')
    require(failed['session_id'] == payload['session_id'], 'Failed SID differs')
    require({x['path'] for x in failed['files']} == {str(p.relative_to(root)) for p in attempt.iterdir()}, 'Failed attempt file set changed')
    require(len(failed['files']) == len({x['path'] for x in failed['files']}), 'Duplicate failed file')
    for item in failed['files']:
        require(Path(item['path']).parent == Path(failed['path']) and item in payload['files'], 'Failure file binding mismatch')
        e.bound(item, failure)
    require({p.name for p in attempt.iterdir()} == {'launch.json', 'failure.json', 'stderr.json', 'visible-events.jsonl'}, '001 must remain the exact empty failed attempt')
    failed_local = strict((attempt / 'failure.json').read_bytes())
    require(failed_local['status'] == runner.FAILED and failed_local['session_id'] == failed['session_id'], '001 is not a preserved failure')
    require(failed_local['process_state']['process_stopped'] is True and failed_local['process_state']['stderr_drained'] is True, 'Failed process/capture not stopped')
    require(failed_local['job_id'] == job_id and all(failed_local[k] == job[v] for k, v in [('prompt_sha256','prompt_sha256'), ('schema_sha256','schema_sha256'), ('requested_model','model'), ('requested_effort','effort'), ('requested_service_tier','service_tier')]), 'Failed input/config differs')
    inspection = strict(e.bound(plan['failure_inspection'], failure))
    require(inspection['assistant_visible_records'] == inspection['final_records'] == 0 and inspection['no_completed_output'] is True and inspection['quota_message_observed'] is False, 'Failure has output or quota')
    proof = inspection['native_proof']
    require(proof['session_id'] == failed['session_id'] and not proof['isolation_failures'] and proof['prompt_sha256'] == job['prompt_sha256'], 'Failed native identity/isolation/prompt mismatch')
    require(proof['configurations'] and all(c.get('model') == job['model'] and c.get('effort') == job['effort'] and c.get('alternate_effort') in (None,job['effort']) and c.get('service_tier') in (None,'default') for c in proof['configurations']), 'Failed native config mismatch')
    stream = [strict(line) for line in (attempt / 'visible-events.jsonl').read_bytes().splitlines()]
    require([x.get('thread_id') for x in stream if x['type'] == 'thread.started'] == [failed['session_id']], 'Failed stdout SID differs')
    require([x['message'] for x in stream if x['type'] == 'error'] == ['Selected model is at capacity. Please try a different model.'] and all(x['type'] in {'thread.started','turn.started','error'} for x in stream), 'Failure is not the exact no-output capacity case')
    require(strict((attempt / 'stderr.json').read_bytes())['lines'] == [], 'Capacity failure stderr was not empty')
    target = run_dir / 'results' / job_id / 'attempt-002'
    require(plan['replacement_attempt'] == {'number': 2, 'path': str(target.relative_to(root))}, 'Only fixed attempt-002 allowed')
    return target, [failure['id'],disposition['id'],original['id'],authorization['id']]


def load_ready(root, run_dir, receipt_path, events, get_object):
    """Verify root's accepted addendum, exact failed attempt and unchanged job."""
    root, run_dir = Path(root).resolve(), Path(run_dir).resolve()
    require(run_dir.is_relative_to(root), 'Run outside root')
    e = Evidence(root, run_dir, list(events), get_object)
    receipt_path = runner.regular(receipt_path, run_dir)
    receipt = strict(receipt_path.read_bytes())
    job_id = receipt.get('logical_job_id')
    require(job_id in JOBS, 'Replacement scope must be one of the exact two IDs')
    require(receipt.get('status') == 'CAPACITY_REPLACEMENT_READY', 'Separate replacement addendum not accepted')
    ready = e.event(receipt['event_id'], 'research.selection.replacement.ready')
    require(ready['payload'].get('status') == 'CAPACITY_REPLACEMENT_READY' and ready['payload'].get('logical_job_id') == job_id, 'Actual ready event has wrong status/scope')
    plan = strict(e.bound(receipt['plan'], ready))
    require(plan['schema'] == 'selection-empty-capacity-replacement.v2' and plan['logical_job_id'] == job_id, 'Replacement scope must be only the assigned exception')
    require(plan['maximum_replacement_attempts'] == 1 and plan['automatic_retry'] is False and plan['content_changes'] is False, 'Only one unchanged replacement allowed')
    start, jobs = runner.gate(run_dir, root)
    original = e.event(start['event_id'], 'research.selection.ready')
    require(receipt['input_event_id'] == plan['input_event_id'] == original['id'], 'Original input event changed')
    require(receipt['bindings'] == ready['bindings'] == original['bindings'] == start['bindings'], 'Replacement bindings differ')
    job = next(j for j in jobs if j['id'] == job_id)
    require(plan['job'] == job and all(job[k] == v for k, v in SETTINGS.items()), 'Replacement job/prompt/schema/config changed')
    target, required_parents = check_plan(root,run_dir,plan,e,start,job)
    require(set(required_parents) <= set(ready['parents']), 'Ready lacks failure/state/input/resume dependencies')
    failed=plan['failed_attempt']
    files = receipt['files']
    require(files and len(files) == len({x['path'] for x in files}), 'Missing/duplicate addendum files')
    for item in files: e.bound(item, ready)
    require(receipt['plan'] in files, 'Plan not in ready manifest')
    frozen = {x['path'] for x in files}
    required_code = {'resolver_v2.py', 'runner_capacity_v2.py', 'archive_capacity_v2.py', 'ready_capacity_v2.py', 'validate_capacity_v4.py', 'closure_capacity_v2.py', 'summary_capacity_v2.py', 'export_capacity_v2.py', 'test_capacity_v2.py', 'test_consumers_v2.py', 'REPLACEMENT_TESTS.json'}
    require({str((run_dir / 'capacity-resume-20261018' / 'replacement-v2' / name).relative_to(root)) for name in required_code} <= frozen, 'Replacement code/tests not frozen by addendum')
    return {'job': job, 'plan': plan, 'receipt': receipt, 'ready_receipt': descriptor(root, receipt_path),
            'ready_event_id': ready['id'], 'input_event_id': original['id'], 'failed_attempt': failed,
            'failure_inspection': plan['failure_inspection'], 'attempt': target,
            'evidence_files': files + [plan['failure_inspection']] + failed['files']}


def load_attempt_resolution(root, run_dir, map_receipt_path, events, get_object):
    """Accept only a canonical post-success map; recheck original failure too."""
    root, run_dir = Path(root).resolve(), Path(run_dir).resolve()
    e = Evidence(root, run_dir, list(events), get_object)
    mrp = runner.regular(map_receipt_path, run_dir)
    receipt = strict(mrp.read_bytes())
    job_id = receipt.get('logical_job_id')
    require(job_id in JOBS, 'Map scope must be one exact replacement')
    require(receipt.get('status') == 'ACCEPTED_ATTEMPTS_MAP_ARCHIVED', 'Accepted-attempt map receipt missing')
    event = e.event(receipt['event_id'], 'research.selection.accepted_attempts.mapped')
    require(event['payload'].get('status') == 'ACCEPTED_ATTEMPTS_MAP_ARCHIVED' and event['payload'].get('logical_job_id') == job_id and event['payload'].get('accepted_attempt') == 2 and event['payload'].get('preserved_failed_attempts') == 1, 'Actual map event status/scope differs')
    mapping = strict(e.bound(receipt['map'], event))
    e.bound(receipt['ready_receipt'], event)
    ready = load_ready(root, run_dir, root / receipt['ready_receipt']['path'], events, get_object)
    require(mapping['schema'] == 'selection-accepted-attempts.v2' and mapping['logical_job_id'] == job_id, 'Map scope differs')
    require(mapping['input_event_id'] == ready['input_event_id'] and mapping['ready_event_id'] == ready['ready_event_id'] and mapping['failed_attempt'] == ready['failed_attempt'], 'Map history differs')
    require(mapping['accepted_attempt']['path'] == str(ready['attempt'].relative_to(root)) and mapping['accepted_attempt']['number'] == 2, 'Accepted attempt path differs')
    accepted = mapping['accepted_attempt']; review = e.event(accepted['event_id'], 'research.selection.review.completed')
    require(review['payload']['status'] == 'REVIEW_ARCHIVED' and review['payload']['job_id'] == job_id and review['payload']['accepted_attempt'] == 2, 'Map does not reference accepted002')
    require(accepted['session_id'] == review['session_id'] and accepted['session_id'] != ready['failed_attempt']['session_id'], 'Fresh replacement SID missing')
    require({ready['input_event_id'], ready['ready_event_id'], ready['failed_attempt']['event_id']} <= set(review['parents']), 'Accepted review dropped failure/addendum/original input')
    require(event['bindings'] == review['bindings'] == ready['receipt']['bindings'], 'Map/review bindings differ')
    require({ready['ready_event_id'], ready['failed_attempt']['event_id'], review['id']} <= set(event['parents']), 'Map event dependencies missing')
    require(accepted['files'] == review['payload']['files'], 'Accepted002 file manifest differs')
    require({f['path'] for f in accepted['files']} == {str(p.relative_to(root)) for p in ready['attempt'].iterdir()}, 'Accepted002 file set differs')
    for item in accepted['files']: e.bound(item, review)
    lane = run_dir / 'results' / job_id
    ar = strict((lane / 'ARCHIVE_RECEIPT.json').read_bytes())
    require(ar['status'] == 'REVIEW_ARCHIVED' and ar['job_id'] == job_id, 'Logical receipt is not an accepted review')
    require(ar['event_id'] == review['id'] and ar['accepted_attempt'] == 2 and ar['input_event_id'] == ready['input_event_id'] and ar['replacement_ready_event_id'] == ready['ready_event_id'] and ar['failed_attempt_event_id'] == ready['failed_attempt']['event_id'], 'Logical archive receipt is not explicit002')
    require(ar['files'] == accepted['files'] and ar['session_id'] == accepted['session_id'], 'Logical archive receipt differs')
    require({p.name for p in lane.glob('attempt-*')} == {'attempt-001','attempt-002'}, 'Extra replacement attempt')
    evidence = ready['evidence_files'] + [receipt['ready_receipt'], receipt['map'], descriptor(root, mrp)]
    # Native/stdout/stderr are preserved canonically but never enter export-safe metadata.
    safe = [f for f in evidence if Path(f['path']).name not in {'native-visible.json','visible-events.jsonl','stderr.json'} and not f['path'].endswith('.jsonl')]
    return {**ready, **mapping, 'map_event_id': event['id'], 'map_receipt': descriptor(root,mrp),
            'evidence_files': list({f['path']:f for f in safe}.values())}




def check_authorization(e, authorization, original):
    resume=e.event(authorization['event_id'],'research.selection.resume.accepted')
    require(resume['bindings']==original['bindings'],'Resume binding differs from original inputs')
    e.bound(authorization['artifact'],resume)
    captures=authorization['user_capture_event_ids']
    require(captures and len(captures)==len(set(captures)),'Fresh user capture required')
    chain=e.ancestors(resume['id'])
    for eid in captures:
        captured=e.event(eid,'research.selection.visible_fragment.captured')
        require(eid in chain and captured['payload'].get('role')=='user','Resume lacks exact user-visible capture dependency')
        require(captured['outputs'],'Empty user capture')
        for digest in captured['outputs']:
            require(sha(e.get(digest))==digest,'User capture object not retained')
    require(original['id'] in chain,'Resume omits original inputs')
    return resume


def load_resolution(root,run_dir,map_receipt_path,events,get_object):
    """Both maps must be accepted before any summary/final/export consumer."""
    root,run_dir=Path(root).resolve(),Path(run_dir).resolve();events=list(events)
    e=Evidence(root,run_dir,events,get_object)
    receipt_path=runner.regular(map_receipt_path,run_dir);receipt=strict(receipt_path.read_bytes())
    require(receipt.get('status')=='CAPACITY_REPLACEMENTS_COMPLETE_ARCHIVED','Both replacements must be canonically accepted')
    ev=e.event(receipt['event_id'],'research.selection.capacity_replacements.accepted')
    require(ev['payload'].get('status')==receipt['status'] and ev['payload'].get('logical_job_ids')==list(JOBS) and ev['payload'].get('preserved_failed_attempts')==2,'Aggregate map scope/status differs')
    mapping=strict(e.bound(receipt['map'],ev))
    require(mapping['schema']=='selection-capacity-map.v2' and set(mapping['attempt_map_receipts'])==set(JOBS),'Exactly two exception maps required')
    exceptions={}
    for jid in JOBS:
        ref=mapping['attempt_map_receipts'][jid];e.bound(ref,ev)
        resolved=load_attempt_resolution(root,run_dir,root/ref['path'],events,get_object)
        require(resolved['logical_job_id']==jid and resolved['map_event_id'] in ev['parents'],'Aggregate map has wrong job/dependency')
        exceptions[jid]=resolved
    require(len({x['input_event_id'] for x in exceptions.values()})==1 and mapping['input_event_id']==exceptions[JOBS[0]]['input_event_id'],'Exception original inputs differ')
    require(ev['bindings']==exceptions[JOBS[0]]['receipt']['bindings']==exceptions[JOBS[1]]['receipt']['bindings'],'Aggregate map bindings differ')
    require(exceptions[JOBS[0]]['plan']['authorization']==exceptions[JOBS[1]]['plan']['authorization'],'Exception resume authorization differs')
    require(exceptions[JOBS[0]]['map_event_id'] in e.events[exceptions[JOBS[1]]['accepted_attempt']['event_id']]['parents'],'Second replacement omits first accepted map')
    sids=[x[k]['session_id'] for x in exceptions.values() for k in ('failed_attempt','accepted_attempt')]
    require(len(sids)==len(set(sids))==4,'Failure/replacement session identity reused')
    evidence=[receipt['map'],descriptor(root,receipt_path)]
    for value in exceptions.values():evidence+=value['evidence_files']
    return {'schema':'selection-capacity-resolution.v2','input_event_id':mapping['input_event_id'],'map_event_id':ev['id'],
            'exceptions':exceptions,'evidence_files':list({x['path']:x for x in evidence}.values())}


def resolve_job(job,run_dir,root,resolution):
    lane=Path(run_dir)/'results'/job['id'];number=2 if job['id'] in JOBS else 1
    if number==2:
        require(resolution and resolution['schema']=='selection-capacity-resolution.v2' and set(resolution['exceptions'])==set(JOBS),'Both canonical exceptions required')
        selected=resolution['exceptions'][job['id']]
        require(selected['job']==job and selected['accepted_attempt']['path']==str((lane/'attempt-002').relative_to(root)),'Resolved job/path differs')
    return {'attempt':lane/('attempt-%03d'%number),'archive_receipt':lane/'ARCHIVE_RECEIPT.json',
            'capture_receipt':lane/'CAPTURE_RECEIPT.json','attempt_number':number}
