#!/usr/bin/env python3
"""Versioned, exact-input artifact transport for heterogeneous essay workflows.

No provider calls or philosophical evaluation. See docs/HUNDRED_ARTIFACTS.md.
All commands accept --request LAB_RELATIVE_JSON except validate --run RUN.
marker is read-only: its output must be emitted as REAL assistant commentary
before record. Native capture never imports whole transcripts or tool bodies.
"""
import argparse
import contextlib
import datetime as dt
import json
import os
from pathlib import Path
import re
import sys
import uuid

import capture_codex as capture
import essay_lineage as lineage
import philosophy_round as rounds
from research_archive import Archive, ArchiveError, _read, canonical, sha
from research_timeline import Timeline, unknown

PROTOCOL = 'hundred-artifacts.v1'
PHASES = {'idea', 'sources', 'draft', 'critique', 'revision', 'final', 'evaluation', 'other'}
ID = re.compile(r'[A-Za-z0-9][A-Za-z0-9_.:/-]{0,140}')
GAPS = ['Exact selected files and one native visible hash attestation only.',
        'A saved-input declaration does not prove no additional context was read.',
        'Distinct observed sessions do not prove intellectual independence.',
        'Native model configuration is not backend attestation; writing start is unknown.',
        'Hidden reasoning, unreviewed tools and unselected transcript records are excluded.']


def ident(value):
    if not isinstance(value, str) or not ID.fullmatch(value) or '..' in value.split('/'):
        raise ArchiveError('invalid bounded identifier')
    return value


def nonempty(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ArchiveError(label + ' requires nonempty text')
    return value


def unique(values):
    return list(dict.fromkeys(values))


def origin_id(entity, run):
    return 'hundred-origin:' + sha((entity + '\n' + run).encode())[:32]


@contextlib.contextmanager
def cached_events(writer):
    """One defensive snapshot per locked CLI command, updated after each append.

    These reviewed APIs read event dictionaries without mutating them. The
    archive's private audited state remains separate and fully validated.
    """
    original_events, original_append_many = writer.events, writer.append_many
    cache = {e['id']: e for e in original_events()}
    def events():
        writer._ensure_open()
        return list(cache.values())
    def append_many(requests):
        result = original_append_many(requests)
        cache.update((e['id'], e) for e in result)
        return result
    writer.events, writer.append_many = events, append_many
    try:
        yield writer
    finally:
        writer.events, writer.append_many = original_events, original_append_many


def state(writer, run):
    events = writer.events()
    known = {e['id']: e for e in events}
    plans = [e for e in events if e['run_id'] == run and e['kind'] == 'hundred.plan']
    if len(plans) != 1:
        raise ArchiveError('run requires exactly one hundred plan')
    plan = plans[0]
    return known, plan, known[plan['payload']['start_event_id']]


def stage_event(known, run, stage, kind):
    matches = [e for e in known.values() if e['run_id'] == run and e['kind'] == kind
               and e['payload'].get('stage') == stage]
    if len(matches) > 1:
        raise ArchiveError('conflicting stage events')
    return matches[0] if matches else None


def open_run(known, first):
    if any(e['run_id'] == first['run_id'] and e['kind'] in
           ('operation.completed', 'operation.interrupted', 'operation.failed')
           for e in known.values()):
        raise ArchiveError('closed run; append a linked new run')
    controls = [e for e in known.values() if e['run_id'] == first['run_id']
                and e['kind'] in ('round.pause', 'round.resume')]
    if controls and controls[-1]['kind'] == 'round.pause':
        raise ArchiveError('run paused')


def files(root, selected, *, directory=None, known=None):
    if not isinstance(selected, list):
        raise ArchiveError('files/inputs must be an explicit list')
    result = []
    seen = set()
    for item in selected:
        item = {'path': item} if isinstance(item, str) else dict(item)
        path = rounds.local(root, item['path'])
        if directory is not None and not path.is_relative_to(directory):
            raise ArchiveError('output/source must belong to this exact entity directory')
        name = str(path.relative_to(root))
        if name in seen:
            raise ArchiveError('duplicate selected path')
        seen.add(name)
        body = _read(path)
        if not body.strip():
            raise ArchiveError('empty selected artifact')
        digest = sha(body)
        if item.get('sha256', digest) != digest:
            raise ArchiveError('selected file hash mismatch')
        source = item.get('from_event_id')
        if source and (known is None or source not in known or digest not in known[source]['outputs']):
            raise ArchiveError('dependency is not an exact output of its selected event')
        result.append({'path': name, 'sha256': digest, 'role': item.get('role', 'input'),
                       **({'from_event_id': source} if source else {})})
    return result


def store_files(root, writer, selected):
    for item in selected:
        if writer.put(_read(rounds.local(root, item['path']))) != item['sha256']:
            raise ArchiveError('file changed between selection and archival write')


def requirements(request):
    value = {'idea_before_draft': True, 'sources_before_draft': True,
             'minimum_independent_critiques': 1, 'fresh_revision': False,
             'required_stages': [], 'method_exemptions': {}}
    value.update(request.get('requirements', {}))
    if set(value) != {'idea_before_draft', 'sources_before_draft', 'minimum_independent_critiques',
                      'fresh_revision', 'required_stages', 'method_exemptions'}:
        raise ArchiveError('unknown requirements field')
    for name in ('idea_before_draft', 'sources_before_draft', 'fresh_revision'):
        if not isinstance(value[name], bool):
            raise ArchiveError('requirement must be boolean')
    count = value['minimum_independent_critiques']
    if type(count) is not int or count < 0:
        raise ArchiveError('minimum_independent_critiques must be nonnegative')
    exemptions = value['method_exemptions']
    if not isinstance(exemptions, dict):
        raise ArchiveError('method_exemptions must be an object')
    for reason in exemptions.values():
        nonempty(reason, 'method exemption')
    for option, key in [('idea_before_draft', 'idea'), ('sources_before_draft', 'sources'),
                        ('minimum_independent_critiques', 'critique')]:
        if not value[option] and not exemptions.get(key):
            raise ArchiveError('disabled requirement needs explicit method exemption: ' + key)
    if not isinstance(value['required_stages'], list):
        raise ArchiveError('required_stages must be a list')
    for stage in value['required_stages']:
        ident(stage)
    return value


def write_origin(writer, request, selected, plan, first):
    entity, run, session = request['entity'], request['run_id'], request['session_id']
    entry = lineage.base_entry(origin_id(entity, run), entity, 'origin', 'Exact authorized neutral workflow inputs')
    entry.update(parents=request.get('lineage_parents', []), artifacts=selected,
                 evidence=[plan['id'], first['id']] + request.get('evidence_event_ids', []),
                 actor={'role': 'AI', 'session_id': session}, workflow={'protocol': PROTOCOL, 'run_id': run},
                 configuration={'requested': request['requested'], 'observed': 'UNKNOWN'}, gaps=GAPS)
    origin = lineage.append(writer, entry, session)
    return {'run_id': run, 'plan_event_id': plan['id'], 'start_event_id': first['id'],
            'origin_lineage_id': entry['id'], 'lineage_event_id': origin['id']}


def init(root, writer, request, request_body):
    run, entity = ident(request['run_id']), ident(request['entity'])
    session = ident(request['session_id'])
    directory = rounds.local(root, request['directory'])
    if not directory.is_dir():
        raise ArchiveError('entity directory must already exist')
    prior = writer.events()
    known = {e['id']: e for e in prior}
    selected = files(root, request['inputs'], known=known)
    req = requirements(request)
    topology = request.get('topology', 'five-stage')
    if topology not in ('five-stage', 'flexible'):
        raise ArchiveError('unknown topology')
    if topology == 'five-stage' and not req['minimum_independent_critiques']:
        raise ArchiveError('one-shot requires explicit flexible topology')
    for key in ('model', 'effort'):
        nonempty(request['requested'][key], 'requested ' + key)
    purpose = request.get('purpose', 'research')
    if purpose not in ('research', 'technical'):
        raise ArchiveError('purpose must be research or technical')
    plans = [e for e in prior if e['run_id'] == run and e['kind'] == 'hundred.plan']
    normalized = dict(request, requirements=req, topology=topology, inputs=selected)
    if any(key not in known for key in request.get('evidence_event_ids', [])):
        raise ArchiveError('unknown explicitly selected origin evidence')
    prior_lineage = lineage.index(prior)
    if any(key not in prior_lineage for key in request.get('lineage_parents', [])):
        raise ArchiveError('unknown explicitly selected origin lineage parent')
    if plans:
        if len(plans) != 1 or plans[0]['payload']['request'] != normalized:
            raise ArchiveError('immutable plan conflict')
        return write_origin(writer, request, selected, plans[0], known[plans[0]['payload']['start_event_id']])
    store_files(root, writer, selected)
    raw_sha = writer.put(request_body)
    helper = writer.put(_read(Path(__file__)))
    method_data = _read(rounds.local(root, request['method']))
    method = json.loads(method_data)
    stage_id = ident(request.get('stage_id', 'HUNDRED'))
    selection_id = ident(request.get('selection_round_id', 'HUNDRED'))
    if topology == 'five-stage':
        first = rounds.start(root, writer, run, session, purpose, request['method'],
                             [i['path'] for i in selected], stage_id=stage_id, selection_round_id=selection_id)
    else:
        if any(e['run_id'] == run for e in prior):
            raise ArchiveError('run already exists without a matching plan')
        bindings = {'method': [writer.put(method_data)],
                    'input': [i['sha256'] for i in selected],
                    'instruction': [writer.put(_read(root / p)) for p in
                                    ('AGENTS.md', 'AGENT_POLICY.md', 'USER_PREFERENCES.md', 'workflows/ROUND.md')],
                    'config': [helper] + [writer.put(_read(root / p)) for p in
                               ('LAB_PROFILE.json', '.codex/config.toml', '.lab/philosophy.json')]}
        context = {'actor': {'id': session, 'role': 'AI'}, 'session_id': session,
                   'run_id': run, 'operation_id': 'round-' + run, 'attempt_id': 'hundred-' + uuid.uuid4().hex}
        epoch_id = 'hundred-' + sha(canonical({k: bindings[k] for k in ('method', 'instruction', 'config')}))[:24]
        epoch = next((e for e in prior if e['id'] == 'epoch:' + epoch_id), None)
        if epoch is None:
            epoch = Timeline(writer).epoch(epoch_id, 'Hundred workflow configuration', bindings,
                'Exact versioned inputs for a flexible research topology.',
                'Method exemptions are bound explicitly; no causal comparison claim.', context)
        first = writer.append(dict(context, kind='operation.started', bindings=bindings, parents=[epoch['id']],
            payload={'protocol': PROTOCOL, 'purpose': purpose, 'method_id': method['id'],
                     'epoch_event_id': epoch['id'], 'stage_id': stage_id, 'selection_round_id': selection_id}),
            'hundred-start:' + run)
    event = rounds.envelope(first, 'hundred.plan', parents=[first['id']],
        payload={'protocol': PROTOCOL, 'start_event_id': first['id'], 'request': normalized,
                 'request_sha256': raw_sha, 'helper_sha256': helper})
    event['outputs'] = unique([raw_sha, helper] + [i['sha256'] for i in selected])
    saved = writer.append(event, 'hundred-plan:' + run)
    return write_origin(writer, request, selected, saved, first)


def ancestors(known, parents):
    found = {}
    def visit(key):
        if key in found:
            return
        event = known.get(key)
        if event is None or event['kind'] != 'hundred.stage':
            raise ArchiveError('parent must be an existing hundred.stage event')
        if not stage_event(known, event['run_id'], event['payload']['stage'], 'hundred.receipt'):
            raise ArchiveError('parent archival attempt is incomplete; replay its record first')
        found[key] = event
        for parent in event['payload']['stage_parents']:
            visit(parent)
    for key in parents:
        visit(key)
    return list(found.values())


def gate(known, plan, request):
    parents = request.get('parents', [])
    family = ancestors(known, parents)
    phases = {e['payload']['phase'] for e in family}
    requirements = plan['payload']['request']['requirements']
    if request['phase'] == 'draft':
        for phase in ('idea', 'sources'):
            if requirements[phase + '_before_draft'] and phase not in phases:
                raise ArchiveError('archive ' + phase + ' ancestry before preparing a draft')
    if request.get('independent'):
        if request['phase'] != 'critique':
            raise ArchiveError('independent flag applies to critique phases')
        related = [e for e in known.values() if e['run_id'] == request['run_id']
                   and e['kind'] == 'hundred.prepared'
                   and e['payload']['stage'] != request['stage']]
        related = [e for e in related if e['payload']['request']['phase'] != 'sources']
        related_family = [e for e in family if e['payload']['phase'] != 'sources']
        if any(e['session_id'] == request['session_id'] for e in related + related_family):
            raise ArchiveError('independent critic must use a distinct actual session')
        if any(e['payload']['phase'] == 'critique' for e in family):
            raise ArchiveError('independent critic cannot have another critique as content ancestry')
    if request['phase'] in ('revision', 'final'):
        critics = {e['session_id'] for e in family if e['payload']['phase'] == 'critique'
                   and e['payload']['independent']}
        if len(critics) < requirements['minimum_independent_critiques']:
            raise ArchiveError('revision/final requires the configured independent critique ancestry')
        if request['session_id'] in critics:
            raise ArchiveError('critic cannot author the resulting revision/final')
        if request['phase'] == 'revision' and requirements['fresh_revision'] and any(
                e['session_id'] == request['session_id'] for e in family):
            raise ArchiveError('this method requires a fresh revision context')
    return family


def prepare(root, writer, request, request_body):
    known, plan, first = state(writer, request['run_id'])
    normalized = dict(request)
    normalized['stage'] = ident(request['stage'])
    normalized['session_id'] = ident(request['session_id'])
    if request['kind'] not in lineage.KINDS or request['phase'] not in PHASES:
        raise ArchiveError('unknown lineage kind or phase')
    nonempty(request['summary'], 'stage summary')
    if request.get('canonical_stage') not in (None, *rounds.STAGES):
        raise ArchiveError('unknown canonical_stage')
    if request.get('canonical_stage') and plan['payload']['request']['topology'] != 'five-stage':
        raise ArchiveError('canonical_stage applies only to five-stage topology')
    selected = files(root, request['inputs'], known=known)
    normalized.update(inputs=selected, parents=unique(request.get('parents', [])),
                      independent=request.get('independent', False))
    if type(normalized['independent']) is not bool:
        raise ArchiveError('independent must be boolean')
    family = gate(known, plan, normalized)
    # References explicitly distinguish selected bytes from mere workflow order.
    direct = set(normalized['parents'])
    if any(i.get('from_event_id') and i['from_event_id'] not in direct for i in selected):
        raise ArchiveError('selected dependency event must be a declared direct parent')
    for parent in normalized['parents']:
        if not any(i.get('from_event_id') == parent for i in selected):
            raise ArchiveError('every content parent requires an exact selected output input')
    old = stage_event(known, request['run_id'], request['stage'], 'hundred.prepared')
    if old:
        if old['payload']['request'] != normalized:
            raise ArchiveError('immutable stage preparation conflict')
        return {'prepared_event_id': old['id'], 'stage': request['stage']}
    open_run(known, first)
    if not normalized['parents'] and request['kind'] not in ('origin', 'idea') and request['phase'] != 'sources':
        raise ArchiveError('this stage requires explicit artifact ancestry')
    store_files(root, writer, selected)
    raw = writer.put(request_body)
    event = rounds.envelope(first, 'hundred.prepared', request['session_id'],
        parents=unique([first['id'], plan['id']] + normalized['parents']),
        payload={'protocol': PROTOCOL, 'stage': request['stage'], 'request': normalized, 'request_sha256': raw})
    event['inputs'] = [i['sha256'] for i in selected]
    event['outputs'] = [raw]
    saved = writer.append(event, 'hundred-prepare:' + request['run_id'] + ':' + request['stage'])
    return {'prepared_event_id': saved['id'], 'stage': request['stage'], 'input_sha256s': event['inputs']}


def snapshot(root, plan, request):
    directory = rounds.local(root, plan['payload']['request']['directory'])
    names = [request['artifact']] + request.get('files', [])
    if request.get('final_file'):
        if request['final_file'] == request['artifact']:
            raise ArchiveError('final manuscript must be separate from revision response')
        names.append(request['final_file'])
    manifest = request.get('source_manifest')
    if manifest:
        names.append(manifest)
    selected = files(root, unique(names), directory=directory)
    source_items = []
    if manifest:
        source_items = json.loads(_read(rounds.local(root, manifest)))
        if not isinstance(source_items, list):
            raise ArchiveError('source manifest must be a list')
        for item in source_items:
            nonempty(item.get('citation'), 'source citation')
            if item.get('read_status') not in ('full', 'excerpt', 'metadata', 'unavailable'):
                raise ArchiveError('explicit full/excerpt/metadata/unavailable reading coverage required')
            if item.get('path'):
                extra = files(root, [item], directory=directory)
                if not any(i['path'] == extra[0]['path'] for i in selected):
                    selected += extra
                elif next(i['sha256'] for i in selected if i['path'] == extra[0]['path']) != extra[0]['sha256']:
                    raise ArchiveError('source bytes changed')
            elif item['read_status'] != 'unavailable':
                raise ArchiveError('actually read source requires saved evidence bytes')
    return {'request': request, 'files': selected, 'source_items': source_items}


def marker_for(run, stage, payload):
    return '[HUNDRED:' + ident(run) + ':' + ident(stage) + ' sha256=' + sha(canonical(payload)) + ']'


def native_capture(root, writer, first, session, marker, source=None):
    source = Path(source) if source else capture.resolve_session(session, root)
    matches = []
    with capture.regular_file(source) as stream:
        size = os.fstat(stream.fileno()).st_size
        if size > 64 * 1024 * 1024:
            raise ArchiveError('selected native source exceeds bounded scan')
        snapshot_bytes = stream.read(size)
    lines = snapshot_bytes[:snapshot_bytes.rfind(b'\n') + 1].splitlines(keepends=True)
    if not lines:
        raise ArchiveError('native source has no complete session metadata')
    meta = capture.strict_json(lines[0])
    if meta.get('type') != 'session_meta' or meta.get('payload', {}).get('id') != session or meta['payload'].get('cwd') != str(root):
        raise ArchiveError('exact native session/cwd mismatch')
    for number, raw in enumerate(lines, 1):
        record = capture.strict_json(raw)
        if capture.classify(record, number, set(), set()) is not None:
            continue
        payload = record['payload']
        if payload.get('type') != 'message' or payload.get('role') != 'assistant' or payload.get('phase', payload.get('channel')) != 'commentary':
            continue
        if marker in '\n'.join(c['text'] for c in payload['content']).splitlines():
            matches.append((number, record['timestamp']))
    if len(matches) != 1:
        raise ArchiveError('requires exactly one real own commentary line matching the exact packet hash')
    number, timestamp = matches[0]
    report = capture.capture(writer.root, source, session, root, start_line=number, end_line=number,
                             run_id=first['run_id'], archive_writer=writer)
    if report['status'] != 'BOUNDED_COMPLETE' or len(report['raw_event_ids']) != 1:
        raise ArchiveError('mandatory native marker capture incomplete')
    return {'raw_event_ids': report['raw_event_ids'], 'coverage_event_id': report['coverage_event_id'],
            'run_binding_ids': report.get('run_binding_event_ids', []), 'timestamp': timestamp, 'marker': marker}


def record(root, writer, request, request_body, source=None):
    known, plan, first = state(writer, request['run_id'])
    prepared = stage_event(known, request['run_id'], request['stage'], 'hundred.prepared')
    if prepared is None:
        raise ArchiveError('prepare exact stage inputs before doing dependent work')
    task = prepared['payload']['request']
    # Prepared inputs are sealed; verify both current files and archived object hashes.
    files(root, task['inputs'], known=known)
    packet = snapshot(root, plan, request)
    if task['phase'] == 'sources':
        if not request.get('source_manifest'):
            raise ArchiveError('source stage requires exact saved source manifest')
        nonempty(request.get('source_note'), 'source retrieval/coverage note')
    if task['phase'] == 'revision' and task.get('canonical_stage') == 'decision' and not request.get('final_file'):
        raise ArchiveError('canonical revision decision requires a separate final manuscript')
    parent_candidates = request.get('candidate', {}).get('parent_candidate_events', [])
    if task['kind'] in ('revision', 'final') and not parent_candidates:
        raise ArchiveError('revision/final requires explicit candidate parent events')
    for key in parent_candidates:
        parent = known.get(key)
        if not parent or parent['kind'] != 'candidate.created' or parent['payload']['artifact_sha256'] not in prepared['inputs']:
            raise ArchiveError('candidate parent must be an exact prepared input version')
    # Validate typed comparison/selection before a native capture or stage write.
    if task['kind'] in ('evaluation', 'tournament', 'selection', 'correction'):
        preliminary = lineage.base_entry('hundred-preflight', plan['payload']['request']['entity'], task['kind'], task['summary'])
        preliminary['parents'] = [known[p]['payload']['lineage_id'] for p in task['parents']]
        if task['kind'] in ('evaluation', 'tournament'):
            preliminary['assessment'] = request['assessment']
            if any(request['assessment'][k] not in prepared['inputs'] for k in ('rubric_sha256', 'prompt_sha256')):
                raise ArchiveError('assessment rubric and prompt must be exact prepared inputs')
        if task['kind'] == 'selection':
            preliminary['decision'] = request['decision']
        lineage.validate(preliminary, lineage.index(known.values()), known, writer.get)
    old = stage_event(known, request['run_id'], request['stage'], 'hundred.stage')
    if old and old['payload']['packet'] != packet:
        raise ArchiveError('immutable record conflict; preserve old artifact and use a new stage')
    if old is None:
        open_run(known, first)
    gate(known, plan, task)
    marker = marker_for(request['run_id'], request['stage'], packet)
    if old:
        bound = old['payload']['capture']
    else:
        bound = native_capture(root, writer, first, prepared['session_id'], marker, source)
    store_files(root, writer, packet['files'])
    raw_sha = writer.put(request_body)
    packet_sha = writer.put(canonical(packet))
    entity = plan['payload']['request']['entity']
    line_id = 'hundred:' + sha((entity + '\n' + request['run_id'] + '\n' + request['stage']).encode())[:40]
    event = rounds.envelope(first, 'hundred.stage', prepared['session_id'],
        parents=unique([first['id'], plan['id'], prepared['id']] + task['parents'] +
                       bound['raw_event_ids'] + bound['run_binding_ids'] + [bound['coverage_event_id']]),
        payload={'protocol': PROTOCOL, 'stage': request['stage'], 'phase': task['phase'],
                 'kind': task['kind'], 'independent': task['independent'], 'stage_parents': task['parents'],
                 'lineage_id': line_id, 'packet': packet, 'packet_sha256': packet_sha,
                 'request_sha256': raw_sha, 'prepared_event_id': prepared['id'], 'capture': bound})
    event['inputs'] = prepared['inputs']
    event['outputs'] = unique([raw_sha, packet_sha] + [i['sha256'] for i in packet['files']])
    saved = old or writer.append(event, 'hundred-stage:' + request['run_id'] + ':' + request['stage'])
    known[saved['id']] = saved
    artifact = next(i['sha256'] for i in packet['files'] if i['path'] == request.get('final_file', request['artifact']))
    primary = next(i['sha256'] for i in packet['files'] if i['path'] == request['artifact'])
    entry = lineage.base_entry(line_id, entity, task['kind'], task['summary'])
    entry['parents'] = [known[p]['payload']['lineage_id'] for p in task['parents']] or [origin_id(entity, request['run_id'])]
    entry['artifacts'] = [dict(i, role='input') for i in task['inputs']] + [dict(i, role='output') for i in packet['files']]
    observed = []
    current = {e['id']: e for e in writer.events()}
    for key in bound['raw_event_ids']:
        model = current[key]['model']
        if model.get('status') == 'known':
            observed.append({'evidence_event_id': key, **model})
    entry.update(evidence=[saved['id'], bound['coverage_event_id']] + bound['raw_event_ids'],
                 actor={'role': 'AI', 'session_id': prepared['session_id']}, occurred_at=bound['timestamp'],
                 configuration={'requested': task.get('requested', plan['payload']['request']['requested']),
                                'observed': {'observations': observed} if observed else 'UNKNOWN'},
                 workflow={'protocol': PROTOCOL, 'run_id': request['run_id'], 'stage': request['stage'],
                           'phase': task['phase'], 'independent_context_declared': task['independent']}, gaps=GAPS)
    if task['kind'] in ('evaluation', 'tournament'):
        entry['assessment'] = request['assessment']
        assessment = request['assessment']
        if any(assessment[k] not in prepared['inputs'] for k in ('rubric_sha256', 'prompt_sha256')):
            raise ArchiveError('assessment rubric and prompt must be exact prepared inputs')
    if task['kind'] == 'selection':
        entry['decision'] = request['decision']
    linked = lineage.append(writer, entry, prepared['session_id'])
    result = {'stage_event_id': saved['id'], 'lineage_id': line_id, 'lineage_event_id': linked['id'],
              'artifact_sha256': primary, 'coverage_event_id': bound['coverage_event_id']}
    if task['kind'] in ('idea', 'draft', 'revision', 'final') or request.get('candidate'):
        candidate_spec = request.get('candidate', {})
        parent_candidates = candidate_spec.get('parent_candidate_events', [])
        if task['kind'] in ('revision', 'final') and not parent_candidates:
            raise ArchiveError('revision/final requires explicit candidate parent events')
        context = {k: first[k] for k in ('actor', 'session_id', 'run_id', 'operation_id', 'attempt_id')}
        context.update(actor={'id': prepared['session_id'], 'role': 'AI'}, session_id=prepared['session_id'])
        made = Timeline(writer).candidate('hundred-' + sha(line_id.encode())[:32],
            candidate_spec.get('artifact_type', 'idea' if task['kind'] == 'idea' else 'essay'), artifact,
            first['payload']['epoch_event_id'], first['id'], first['payload']['stage_id'],
            first['payload']['selection_round_id'], 'AI',
            candidate_spec.get('genesis', 'MERGED' if len(parent_candidates) > 1 else 'DERIVED' if parent_candidates else 'ORIGINAL'),
            context, parent_candidate_events=parent_candidates,
            birth=unknown('Writing start unknown; visible packet attestation is recorded separately.'))
        result['candidate_event_id'] = made['id']
    supporting = []
    if task['phase'] in ('sources', 'critique'):
        support = rounds.envelope(first, 'round.source_snapshot' if task['phase'] == 'sources' else 'round.judge_review',
            prepared['session_id'], parents=[saved['id']],
            payload={'protocol': PROTOCOL, 'stage_event_id': saved['id'], 'artifact_sha256': primary,
                     'manifest_sha256': packet_sha, 'coverage_event_id': bound['coverage_event_id'],
                     'context_separation': 'Distinct observed session only' if task['independent'] else 'Not declared independent'})
        support['outputs'] = [primary, packet_sha]
        supporting.append(writer.append(support, 'hundred-support:' + request['run_id'] + ':' + request['stage'])['id'])
    if task.get('canonical_stage'):
        if task['canonical_stage'] == 'decision':
            ancestor_ids = {e['id'] for e in ancestors(known, task['parents'])}
            supporting += [e['id'] for e in writer.events() if e['kind'] == 'round.judge_review'
                           and e['run_id'] == request['run_id'] and e['payload'].get('stage_event_id') in ancestor_ids]
        canonical_stage = rounds.record(root, writer, request['run_id'], task['canonical_stage'], request['artifact'],
                                       prepared['session_id'], bound['raw_event_ids'], request.get('source_note', ''),
                                       supporting_events=unique(supporting))
        result['canonical_stage_event_id'] = canonical_stage['id']
    receipt = rounds.envelope(first, 'hundred.receipt', prepared['session_id'],
        parents=unique([saved['id'], linked['id']] + [result[k] for k in ('candidate_event_id', 'canonical_stage_event_id') if k in result]),
        payload={'protocol': PROTOCOL, 'stage': request['stage'], 'result': result})
    receipt_event = writer.append(receipt, 'hundred-receipt:' + request['run_id'] + ':' + request['stage'])
    return dict(result, receipt_event_id=receipt_event['id'])


@contextlib.contextmanager
def defer_views():
    refresh, backfill, render = rounds.refresh, lineage.backfill, lineage.render
    try:
        rounds.refresh = lambda *_: None
        lineage.backfill = lambda *_: None
        lineage.render = lambda *_: None
        yield
    finally:
        rounds.refresh, lineage.backfill, lineage.render = refresh, backfill, render


def checkpoint(root, writer, request, request_body):
    known, plan, first = state(writer, request['run_id'])
    errors = validate(writer, request['run_id'], complete=False)
    if errors:
        raise ArchiveError('; '.join(errors))
    stages = [e for e in known.values() if e['run_id'] == request['run_id'] and e['kind'] == 'hundred.stage']
    requirements = plan['payload']['request']['requirements']
    names = {e['payload']['stage'] for e in stages}
    if not set(requirements['required_stages']) <= names:
        raise ArchiveError('required method stages are missing')
    final = known.get(request['final_stage_event_id'])
    if final not in stages or final['payload']['phase'] not in ('final', 'revision', 'draft'):
        raise ArchiveError('select one exact final manuscript stage')
    family = ancestors(known, [final['id']])
    critics = {e['session_id'] for e in family if e['payload']['phase'] == 'critique' and e['payload']['independent']}
    if len(critics) < requirements['minimum_independent_critiques']:
        raise ArchiveError('selected final omits required independent critics')
    summary_path = rounds.local(root, request['summary'])
    if not summary_path.is_relative_to(rounds.local(root, plan['payload']['request']['directory'])):
        raise ArchiveError('checkpoint summary must belong to the entity')
    raw = _read(summary_path)
    summary = json.loads(raw)
    for key in ('question', 'outcome', 'contribution', 'criticism', 'limitations', 'next_step', 'method_change', 'comparability', 'coverage_boundary'):
        nonempty(summary.get(key), 'checkpoint ' + key)
    if summary['outcome'] not in ('CONTINUE', 'REVISE', 'SET_ASIDE', 'COMPLETE_TECHNICAL'):
        raise ArchiveError('unsupported checkpoint outcome')
    if summary['outcome'] == 'COMPLETE_TECHNICAL' and first['payload']['purpose'] != 'technical':
        raise ArchiveError('technical outcome requires technical purpose')
    coverage = unique(e['payload']['capture']['coverage_event_id'] for e in stages)
    if plan['payload']['request']['topology'] == 'five-stage':
        with defer_views():
            cp = rounds.checkpoint(root, writer, request['run_id'], request['summary'], coverage)
    else:
        old = next((e for e in known.values() if e['run_id'] == request['run_id'] and e['kind'] == 'checkpoint'), None)
        if not old:
            open_run(known, first)
        event = rounds.envelope(first, 'checkpoint', parents=[first['id']] + [e['id'] for e in stages] + coverage,
            payload={'protocol': PROTOCOL, 'research_date': dt.datetime.now(dt.timezone.utc).date().isoformat(),
                     'summary': summary, 'capture_status': 'BOUNDED_COMPLETE', 'purpose': first['payload']['purpose'],
                     'truth_status': 'NOT_CERTIFIED', 'topology': 'flexible',
                     'method_exemptions': requirements['method_exemptions'], 'final_stage_event_id': final['id']})
        event['outputs'] = [writer.put(raw)]
        if old:
            if old['outputs'] != event['outputs'] or old['parents'] != event['parents'] or old['payload']['final_stage_event_id'] != final['id']:
                raise ArchiveError('immutable checkpoint conflict')
            cp = old
        else:
            cp = writer.append(event, 'checkpoint:' + request['run_id'])
        writer.append(rounds.envelope(first, 'operation.completed', parents=[first['id'], cp['id']],
            payload={'checkpoint': cp['id'], 'outcome': summary['outcome'],
                     'scope': 'Selected manuscript workflow complete under bound exemptions; no truth or eligibility certificate'}),
            'round-terminal:' + request['run_id'])
    binding = rounds.envelope(first, 'hundred.checkpoint_binding',
        parents=[cp['id'], plan['id']] + [e['id'] for e in stages],
        payload={'protocol': PROTOCOL, 'checkpoint_event_id': cp['id'], 'final_stage_event_id': final['id'],
                 'method_exemptions': requirements['method_exemptions']})
    writer.append(binding, 'hundred-checkpoint-binding:' + request['run_id'])
    return {'checkpoint_event_id': cp['id'], 'final_stage_event_id': final['id'], 'coverage_event_ids': coverage}


def validate(writer, run, complete=True):
    known, plan, first = state(writer, run)
    errors = []
    stages = [e for e in known.values() if e['run_id'] == run and e['kind'] == 'hundred.stage']
    entries = lineage.index(known.values())
    for event in stages:
        try:
            p = event['payload']
            prepared = known[p['prepared_event_id']]
            task = prepared['payload']['request']
            if prepared['kind'] != 'hundred.prepared' or prepared['run_id'] != run or prepared['sequence'] >= event['sequence']:
                raise ArchiveError('missing prior exact preparation')
            if prepared['session_id'] != event['session_id'] or prepared['inputs'] != event['inputs']:
                raise ArchiveError('stage input/session binding mismatch')
            if any(p[key] != task[key] for key in ('stage', 'phase', 'kind', 'independent')) or p['stage_parents'] != task['parents']:
                raise ArchiveError('stage differs from prepared role/topology')
            if sha(canonical(p['packet'])) != p['packet_sha256'] or writer.get(p['packet_sha256']) != canonical(p['packet']):
                raise ArchiveError('packet object mismatch')
            for item in p['packet']['files']:
                if item['sha256'] not in event['outputs'] or sha(writer.get(item['sha256'])) != item['sha256']:
                    raise ArchiveError('artifact not stored exactly')
            marker = marker_for(run, p['stage'], p['packet'])
            bound = p['capture']
            coverage = known[bound['coverage_event_id']]
            if coverage['kind'] != 'capture.coverage' or coverage['run_id'] != run or coverage['session_id'] != event['session_id'] or coverage['payload'].get('status') != 'BOUNDED_COMPLETE':
                raise ArchiveError('incomplete/mismatched native coverage')
            for key in bound['raw_event_ids']:
                raw = known[key]
                if raw['kind'] != 'capture.raw_record' or raw['session_id'] != event['session_id'] or key not in coverage['parents'] or key not in event['parents']:
                    raise ArchiveError('missing exact raw evidence')
                native = capture.strict_json(writer.get(raw['payload']['raw_sha256']))
                if capture.classify(native, raw['payload']['source_line'], set(), set()) is not None or native['payload'].get('role') != 'assistant' or native['payload'].get('phase', native['payload'].get('channel')) != 'commentary':
                    raise ArchiveError('not a permitted assistant commentary attestation')
                if marker not in '\n'.join(c['text'] for c in native['payload']['content']).splitlines():
                    raise ArchiveError('native marker does not bind exact artifact packet')
                if raw['run_id'] != run and not any(known[b]['kind'] == 'capture.run_binding' and
                        known[b]['run_id'] == run and known[b]['payload'].get('raw_event_id') == key and
                        b in event['parents'] and b in coverage['parents'] for b in bound['run_binding_ids']):
                    raise ArchiveError('foreign-run native original lacks explicit run binding')
            if not bound['raw_event_ids']:
                raise ArchiveError('missing native attestation')
            gate(known, plan, task)
            line = entries.get(p['lineage_id'])
            if line is None:
                raise ArchiveError('lineage missing; replay record to finish interrupted archival attempt')
            lineage.validate(line['payload']['entry'], entries, known, writer.get)
            if not stage_event(known, run, p['stage'], 'hundred.receipt'):
                raise ArchiveError('stage receipt missing; replay record before dependent work')
        except (ValueError, KeyError, OSError) as exc:
            errors.append(event['payload'].get('stage', '?') + ': ' + str(exc))
    if complete:
        cps = [e for e in known.values() if e['run_id'] == run and e['kind'] == 'checkpoint']
        if len(cps) != 1:
            errors.append('requires one canonical checkpoint')
        if not any(e['run_id'] == run and e['kind'] == 'hundred.checkpoint_binding' for e in known.values()):
            errors.append('canonical checkpoint binding missing')
        if len(cps) == 1:
            cp = cps[0]
            if not {e['payload']['capture']['coverage_event_id'] for e in stages} <= set(cp['parents']):
                errors.append('checkpoint omits stage coverage')
            if not any(e['run_id'] == run and e['kind'] == 'operation.completed' and
                       e['payload'].get('checkpoint') == cp['id'] and cp['id'] in e['parents'] for e in known.values()):
                errors.append('canonical completion missing')
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['init', 'prepare', 'marker', 'record', 'checkpoint', 'validate'])
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--request')
    parser.add_argument('--run')
    parser.add_argument('--source', type=Path, help='Exact own authorized native source; default exact session-ID database lookup')
    parser.add_argument('--init-request', help='Offline marker only: local init JSON supplies directory; record verifies canonical plan')
    args = parser.parse_args()
    root = args.root.absolute()
    try:
        if args.command == 'validate':
            if not args.run:
                raise ArchiveError('validate requires --run')
            with Archive(root / 'research/archive').writer() as writer, cached_events(writer):
                errors = validate(writer, args.run)
            print(json.dumps({'run_id': args.run, 'ok': not errors, 'errors': errors}))
            return 1 if errors else 0
        if not args.request:
            raise ArchiveError('command requires --request')
        body = _read(rounds.local(root, args.request))
        request = json.loads(body)
        if args.command == 'marker' and args.init_request:
            initial = json.loads(_read(rounds.local(root, args.init_request)))
            if initial['run_id'] != request['run_id']:
                raise ArchiveError('offline marker run differs from selected init request')
            plan = {'payload': {'request': initial}}
            print(marker_for(request['run_id'], request['stage'], snapshot(root, plan, request)))
            return 0
        with Archive(root / 'research/archive').writer() as writer, cached_events(writer):
            if args.command == 'marker':
                _, plan, _ = state(writer, request['run_id'])
                print(marker_for(request['run_id'], request['stage'], snapshot(root, plan, request)))
                return 0
            if args.command == 'record':
                result = record(root, writer, request, body, args.source)
            else:
                result = globals()[args.command](root, writer, request, body)
        print(json.dumps(result, sort_keys=True))
        return 0
    except (ValueError, KeyError, OSError, TypeError) as exc:
        print('hundred artifact error: ' + str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
