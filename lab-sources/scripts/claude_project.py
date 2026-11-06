#!/usr/bin/env python3
"""One persistent Claude folder. Explicit jobs, closed returns, recoverable controls.
No model launches, session discovery, daemon, or provider permission attestation.
"""
import argparse
import os
from pathlib import Path
import tempfile
import philosophy_bridge as b
from research_archive import ArchiveError, canonical, sha, _safe_path, _fsync_dir
from philosophy_round import start_record

PROTOCOL = 'philosophy-claude-project.v2'
IDLE_INSTRUCTIONS = b'''# Claude research workbench
Read CURRENT.json. If state is not ACTIVE, stop: no task is released.
Use a NEW chat per job. Never reuse another job's conversation.
Do not read jobs/, work/, archives or other folders when no job is active.
Codex alone changes tasks and preserves the canonical archive.
'''


def states(archive, workspace):
    return [e for e in archive.events() if e['kind'] == 'bridge.project.state'
            and e['payload'].get('workspace') == str(workspace)]


def latest(archive, workspace):
    history = states(archive, workspace)
    if not history:
        raise ArchiveError('persistent project is not registered')
    return history[-1]


def control_bytes(state, archive):
    return {k: archive.get(v) for k, v in state['payload']['controls'].items()}


def check_controls(workspace, state, archive):
    for name, data in control_bytes(state, archive).items():
        if b.read_file(workspace / name) != data:
            raise ArchiveError('project control drift or interrupted publication; recover exact recorded state')
    local = workspace / '.claude/settings.local.json'
    if local.exists() and b.strict_json(b.read_file(local)) != {}:
        raise ArchiveError('local settings override project policy')


def check_closed(workspace, state):
    for job, expected in state['payload']['closed_outputs'].items():
        files, _ = b.tree(workspace / 'work' / job / 'output', runtime=True)
        if b.file_records(files) != expected:
            raise ArchiveError('closed job changed, possibly a stale chat; preserve and investigate before continuing')


def replace_control(path, data):
    path = _safe_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and b.read_file(path) == data:
        return
    fd, name = tempfile.mkstemp(prefix='.project-control-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as f:
            f.write(data); f.flush(); os.fsync(f.fileno())
        os.replace(name, path); _fsync_dir(path.parent)
    finally:
        if os.path.exists(name): os.unlink(name)


def materialize(workspace, state, archive):
    # CURRENT last. Intermediate states fail verification; recovery accepts only recorded bytes.
    files = control_bytes(state, archive)
    for name in sorted(files, key=lambda n: n == 'CURRENT.json'):
        replace_control(workspace / name, files[name])
    check_controls(workspace, state, archive)


def commit(archive, start, workspace, pointer, instructions, settings, closed, parents):
    controls = {'CURRENT.json': canonical(pointer), 'CLAUDE.md': instructions,
                '.claude/settings.json': settings}
    hashes = {p: archive.put(data) for p, data in controls.items()}
    payload = {'workspace': str(workspace), 'pointer': pointer, 'controls': hashes, 'closed_outputs': closed}
    key = 'claude-project-state:' + sha(canonical([payload, parents]))
    ev = archive.append(b.event(start, 'bridge.project.state', pointer.get('job_id') or 'idle',
                               payload, parents=parents, outputs=sorted(set(hashes.values()))), key)
    materialize(workspace, ev, archive)
    return ev


@b.with_archive
def initialize(root, workspace, run_id, *, archive_writer=None):
    root, archive = b.lab(root, archive_writer); workspace = _safe_path(workspace)
    with b.bridge_lock(root):
        history = states(archive, workspace)
        if history:
            check_controls(workspace, history[-1], archive); check_closed(workspace, history[-1])
            return {'state': history[-1]['payload']['pointer']['state'], 'event_id': history[-1]['id']}
        # Existing legacy jobs/ may remain, but never overwrite any pre-existing controls/work.
        for name in ('CURRENT.json', 'CLAUDE.md', '.claude', 'work'):
            if (workspace / name).exists():
                raise ArchiveError('project control destination exists; do not overwrite an unrelated project')
        workspace.mkdir(parents=True, exist_ok=True)
        start = start_record(archive, run_id)
        settings = b.strict_json(b.read_file(root / 'templates/philosophy_claude/settings.json'))
        settings['permissions']['allow'] = ['Read(/CURRENT.json)']
        settings['permissions']['deny'] += ['Read(/jobs/**)', 'Read(/work/**)', 'Edit(/jobs/**)', 'Edit(/work/**)']
        pointer = {'protocol': PROTOCOL, 'state': 'IDLE', 'job_id': None, 'generation': 0}
        ev = commit(archive, start, workspace, pointer, IDLE_INSTRUCTIONS, canonical(settings), {}, [start['id']])
        return {'state': 'IDLE', 'event_id': ev['id'], 'model_launched': False}


@b.with_archive
def publish(root, workspace, job_id, *, archive_writer=None):
    root, archive = b.lab(root, archive_writer); workspace = _safe_path(workspace); b.identifier(job_id)
    with b.bridge_lock(root):
        prior = latest(archive, workspace); check_controls(workspace, prior, archive); check_closed(workspace, prior)
        pointer = prior['payload']['pointer']
        if pointer['state'] == 'ACTIVE':
            if pointer['job_id'] == job_id:
                resolve(root, workspace, archive, pointer)
                return {'state': 'ACTIVE', 'job_id': job_id, 'event_id': prior['id'], 'replayed': True}
            raise ArchiveError('active job must be captured, collected and closed before switching')
        record, manifest = b.prepared(archive, job_id)
        if manifest.get('workspace_layout') != 'persistent':
            raise ArchiveError('new persistent-layout packet required; old job is immutable')
        b.verify_prepared_export(root, archive, record)
        activations = [e for e in archive.events() if e['kind'] == 'bridge.job.activated' and e['payload'].get('job_id') == job_id]
        activated_projects = [e for e in archive.events() if e['kind'] == 'bridge.project.state' and e['payload']['pointer'].get('state') == 'ACTIVE' and e['payload']['pointer'].get('job_id') == job_id]
        if activations or activated_projects:
            raise ArchiveError('job already activated; no relocation or reuse')
        packet = b.expected_packet(archive, record)
        dest = workspace / 'work' / job_id
        files = {'input/' + p: data for p, data in packet.items() if p not in ('CLAUDE.md', 'settings.json')}
        if dest.exists():
            if {p.name for p in dest.iterdir()} != {'input', 'output'}:
                raise ArchiveError('unexpected files in uncommitted job directory')
            observed, _ = b.tree(dest / 'input')
            output, _ = b.tree(dest / 'output', runtime=True)
            if observed != {p[6:]: v for p, v in files.items()} or output:
                raise ArchiveError('uncommitted job directory changed; preserve and investigate')
        else:
            b.publish_directory(dest, files, output=True)
        settings = b.strict_json(packet['settings.json'])
        for old in prior['payload']['closed_outputs']:
            settings['permissions']['deny'] += [f'Read(/work/{old}/**)', f'Edit(/work/{old}/**)']
        start = start_record(archive, manifest['run_id'])
        pointer = {'protocol': PROTOCOL, 'state': 'ACTIVE', 'job_id': job_id,
                   'manifest_sha256': record['payload']['manifest_sha256'], 'generation': pointer['generation'] + 1}
        ev = commit(archive, start, workspace, pointer, packet['CLAUDE.md'], canonical(settings),
                    prior['payload']['closed_outputs'], [prior['id'], record['id']])
        # Canonical project state is itself the activation for persistent workspaces.
        return {'state': 'ACTIVE', 'job_id': job_id, 'event_id': ev['id'], 'fresh_chat_required': True, 'model_launched': False}


def resolve(root, workspace, archive, current):
    state = latest(archive, workspace)
    if current != state['payload']['pointer'] or current['state'] != 'ACTIVE':
        raise ArchiveError('stale or inactive project pointer')
    check_controls(workspace, state, archive); check_closed(workspace, state)
    record, manifest = b.prepared(archive, current['job_id'])
    active = [e for e in archive.events() if e['kind'] == 'bridge.project.state'
              and e['payload']['pointer'].get('state') == 'ACTIVE'
              and e['payload']['pointer'].get('job_id') == current['job_id']]
    if len(active) != 1 or active[0]['id'] != state['id'] or manifest.get('workspace_layout') != 'persistent':
        raise ArchiveError('persistent job has conflicting activation history')
    if current['manifest_sha256'] != record['payload']['manifest_sha256']:
        raise ArchiveError('persistent manifest mismatch')
    packet = b.expected_packet(archive, record)
    files, _ = b.tree(workspace / 'work' / current['job_id'] / 'input')
    if files != {p: data for p, data in packet.items() if p not in ('CLAUDE.md', 'settings.json')}:
        raise ArchiveError('persistent input changed')
    return root, archive, workspace, record, manifest


@b.with_archive
def close(root, workspace, job_id, collection_id, source, *, archive_writer=None):
    import capture_claude as cc
    root, archive = b.lab(root, archive_writer); workspace = _safe_path(workspace)
    state = latest(archive, workspace)
    if state['payload']['pointer']['state'] == 'CLOSED':
        check_controls(workspace, state, archive); check_closed(workspace, state)
        if state['payload']['pointer']['job_id'] != job_id:
            raise ArchiveError('close replay names another job')
        found = [e for e in archive.events() if e['kind'] == 'bridge.return.collected'
                 and e['payload'].get('job_id') == job_id and e['payload'].get('collection_id') == collection_id]
        if len(found) != 1 or found[0]['id'] not in state['parents']:
            raise ArchiveError('close replay names another collection')
        return {'state': 'CLOSED', 'event_id': state['id'], 'replayed': True, 'provider_process_stopped': False}
    root, archive, workspace, record, manifest = b.workspace_job(root, workspace, archive)
    if manifest['job_id'] != job_id or manifest.get('workspace_layout') != 'persistent':
        raise ArchiveError('close must name the exact active persistent job')
    with b.bridge_lock(root):
        state = latest(archive, workspace)
        found = [e for e in archive.events() if e['kind'] == 'bridge.return.collected'
                 and e['payload'].get('job_id') == job_id and e['payload'].get('collection_id') == collection_id]
        if len(found) != 1:
            raise ArchiveError('exact collected return required')
        col = found[0]; data = col['payload']
        if data.get('source_coverage') != 'BOUNDED_COMPLETE':
            raise ArchiveError('close requires complete bounded capture, including partial work')
        events = {e['id']: e for e in archive.events()}
        coverage = events[data['coverage_event_id']]
        report = b.strict_json(archive.get(coverage['payload']['report_sha256']))
        raw, cutoff, rows = cc.source_snapshot(Path(source), col['session_id'], workspace)
        if sha(raw) != report['source_snapshot_sha256'] or cutoff != len(raw) or report['selected_range'][1] != len(rows):
            raise ArchiveError('session changed or has uncaptured tail; capture before closing')
        # Claim may not have advanced since collection.
        claims = [e for e in archive.events() if e['kind'] == 'bridge.job.claimed' and e['payload'].get('job_id') == job_id]
        if not claims or claims[-1]['id'] != data['claim_event_id']:
            raise ArchiveError('return belongs to an earlier claim')
        files, _ = b.tree(b.output_directory(workspace), runtime=True)
        if b.file_records(files) != data['file_records']:
            raise ArchiveError('output changed after collection')
        closed = {**state['payload']['closed_outputs'], job_id: data['file_records']}
        pointer = {**state['payload']['pointer'], 'state': 'CLOSED'}
        settings = b.strict_json(archive.get(state['payload']['controls']['.claude/settings.json']))
        settings['permissions']['allow'] = ['Read(/CURRENT.json)']
        settings['permissions']['deny'] += [f'Read(/work/{job_id}/**)', f'Edit(/work/{job_id}/**)']
        ev = commit(archive, start_record(archive, manifest['run_id']), workspace, pointer,
                    IDLE_INSTRUCTIONS, canonical(settings), closed, [state['id'], col['id'], coverage['id']])
        return {'state': 'CLOSED', 'event_id': ev['id'], 'provider_process_stopped': False,
                'boundary': 'Closed observed bytes; not a provider cancellation. Stale output mutation blocks future operations.'}


@b.with_archive
def recover(root, workspace, *, archive_writer=None):
    root, archive = b.lab(root, archive_writer); workspace = _safe_path(workspace)
    with b.bridge_lock(root):
        history = states(archive, workspace); state = latest(archive, workspace)
        # Never overwrite unknown drift. Only known previous/next control bytes or absent files.
        for name in state['payload']['controls']:
            path = workspace / name
            if path.exists() and sha(b.read_file(path)) not in {e['payload']['controls'][name] for e in history}:
                raise ArchiveError('unrecognized control bytes; recovery will not overwrite them')
        check_closed(workspace, state); materialize(workspace, state, archive)
        return {'state': state['payload']['pointer']['state'], 'event_id': state['id'], 'recovered': True}


@b.with_archive
def status(root, workspace, *, archive_writer=None):
    root, archive = b.lab(root, archive_writer); workspace = _safe_path(workspace)
    state = latest(archive, workspace); check_controls(workspace, state, archive); check_closed(workspace, state)
    pointer = state['payload']['pointer']
    if pointer['state'] == 'ACTIVE': resolve(root, workspace, archive, pointer)
    events = archive.events()
    scoped = [e for e in events if e['kind'] == 'bridge.return.collected'
              and e['payload'].get('workspace') == str(workspace)]
    last = scoped[-1] if scoped else None
    result = {**pointer, 'verified': True,
              'closed_jobs': len(state['payload']['closed_outputs']),
              'provider_runtime': 'UNKNOWN', 'launch_performed_by_this_command': False,
              'last_collected': None, 'output_state': 'NO_JOB'}
    if last:
        result['last_collected'] = {k: last['payload'][k] for k in
                                    ('job_id', 'collection_id', 'disposition', 'source_coverage')}
        result['last_collected']['session_id'] = last['session_id']
    job = pointer.get('job_id')
    if job:
        _, manifest = b.prepared(archive, job, events)
        files, _ = b.tree(workspace / 'work' / job / 'output', runtime=True)
        result['stage'] = manifest['stage']
        result['file_count'] = len(files)
        matching = [e for e in scoped if e['payload']['job_id'] == job
                    and e['payload']['file_records'] == b.file_records(files)]
        result['output_state'] = ('ALREADY_COLLECTED' if matching else
                                  'OUTPUT_PRESENT_UNCOLLECTED' if files else 'NO_OUTPUT_OBSERVED')
        if matching:
            result['matching_collection_id'] = matching[-1]['payload']['collection_id']
            result['matching_disposition'] = matching[-1]['payload']['disposition']
        result['manuscript_counts'] = {}
        from manuscript_count import count
        for name, data in files.items():
            if name.startswith('final-') and name.endswith('.md'):
                try:
                    result['manuscript_counts'][name] = count(data.decode('utf-8'))
                except (ValueError, UnicodeError) as error:
                    result['manuscript_counts'][name] = {'error': str(error), 'length_status': 'REVIEW_REQUIRED'}
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    p.add_argument('--workspace', type=Path, required=True); sub = p.add_subparsers(dest='cmd', required=True)
    q = sub.add_parser('init'); q.add_argument('--run', required=True)
    q = sub.add_parser('publish'); q.add_argument('--job', required=True)
    q = sub.add_parser('close'); q.add_argument('--job', required=True); q.add_argument('--collection', required=True); q.add_argument('--source', type=Path, required=True)
    sub.add_parser('recover'); sub.add_parser('status'); a = p.parse_args()
    try:
        if a.cmd == 'init': r = initialize(a.root, a.workspace, a.run)
        elif a.cmd == 'publish': r = publish(a.root, a.workspace, a.job)
        elif a.cmd == 'close': r = close(a.root, a.workspace, a.job, a.collection, a.source)
        elif a.cmd == 'recover': r = recover(a.root, a.workspace)
        else: r = status(a.root, a.workspace)
        print(canonical(r).decode(), end='')
    except (ValueError, OSError, KeyError, TypeError) as e: p.exit(2, str(e) + '\n')

if __name__ == '__main__': main()
