#!/usr/bin/env python3
"""Local immutable Claude job packets and inert returns; never launches a model."""
import argparse
import contextlib
import fcntl
import functools
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys
import tempfile
import unicodedata

from research_archive import Archive, ArchiveError, canonical, sha, _safe_path, _publish, _fsync_dir
from philosophy_round import start_record

PROTOCOL = 'philosophy-claude-bridge.v1'
MAX_FILE = 16 * 1024 * 1024
MAX_TOTAL = 96 * 1024 * 1024
MAX_FILES = 256
ID = re.compile(r'^[a-z0-9][a-z0-9._-]{0,95}$')


def identifier(value):
    if not isinstance(value, str) or not ID.fullmatch(value):
        raise ArchiveError('invalid bridge identifier')
    return value


def relative(value):
    if not isinstance(value, str) or not value or len(value) > 300:
        raise ArchiveError('bounded relative path required')
    p = PurePosixPath(value)
    if (p.is_absolute() or '\\' in value or value != str(p) or
            any(s.startswith('.') or ':' in s for s in p.parts) or
            unicodedata.normalize('NFC', value) != value or any(ord(c) < 32 for c in value)):
        raise ArchiveError('unsafe relative path')
    return value


def strict_json(raw):
    def pairs(items):
        result = {}
        for k, v in items:
            if k in result:
                raise ArchiveError('duplicate JSON key')
            result[k] = v
        return result
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=lambda v: (_ for _ in ()).throw(ArchiveError('nonfinite JSON')))


def read_file(path, maximum=MAX_FILE):
    path = _safe_path(path)
    before = path.lstat()
    if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1 or before.st_size > maximum:
        raise ArchiveError('input must be a bounded single-link regular file')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        opened = os.fstat(fd)
        data = b''
        while len(data) <= maximum:
            part = os.read(fd, min(1024 * 1024, maximum + 1 - len(data)))
            if not part:
                break
            data += part
        after = os.fstat(fd)
        current = path.lstat()
        fields = ('st_dev', 'st_ino', 'st_size', 'st_mtime_ns', 'st_ctime_ns', 'st_nlink')
        if len(data) > maximum or any(getattr(before, f) != getattr(x, f) for x in (opened, after, current) for f in fields):
            raise ArchiveError('file changed during bounded read')
        return data
    finally:
        os.close(fd)


def tree(path, runtime=False):
    """No-follow snapshot; decoration is excluded, content races fail closed."""
    path = _safe_path(path)
    files, ignored, observations, file_observations = {}, [], [], []
    total = 0
    def visit(base, prefix=''):
        nonlocal total
        before = base.lstat()
        if not stat.S_ISDIR(before.st_mode) or os.path.ismount(base):
            raise ArchiveError('real non-mount directory required')
        names = sorted(os.listdir(base))
        observations.append((base, before, names))
        folded = set()
        for name in names:
            key = unicodedata.normalize('NFKC', name).casefold()
            if key in folded:
                raise ArchiveError('case/Unicode path collision')
            folded.add(key)
            rel = prefix + name
            if runtime and name in {'.DS_Store', '.claude', '.cc-writes'}:
                ignored.append({'path': rel, 'reason': 'excluded_runtime_metadata_not_traversed'})
                continue
            relative(rel)
            child = base / name
            info = child.lstat()
            if stat.S_ISDIR(info.st_mode):
                visit(child, rel + '/')
            else:
                files[rel] = read_file(child)
                file_observations.append((child, child.lstat()))
                total += len(files[rel])
                if total > MAX_TOTAL or len(files) > MAX_FILES:
                    raise ArchiveError('tree exceeds collection bounds')
    visit(path)
    for base, before, names in observations:
        after = base.lstat()
        if sorted(os.listdir(base)) != names or any(getattr(before, f) != getattr(after, f) for f in ('st_ino', 'st_dev', 'st_mtime_ns', 'st_ctime_ns')):
            raise ArchiveError('directory changed during snapshot')
    for path, before in file_observations:
        after = path.lstat()
        if any(getattr(before, f) != getattr(after, f) for f in ('st_ino', 'st_dev', 'st_size', 'st_mtime_ns', 'st_ctime_ns', 'st_nlink')):
            raise ArchiveError('previously read output changed during tree snapshot')
    return files, ignored


def file_records(files):
    return [{'path': p, 'sha256': sha(b), 'bytes': len(b)} for p, b in sorted(files.items())]


def lab(root, archive_writer=None):
    root = _safe_path(root)
    if strict_json(read_file(root / 'LAB_PROFILE.json'))['lab']['kind'] != 'PHILOSOPHY_PROGRAM':
        raise ArchiveError('philosophy laboratory required')
    if not (root / '.lab/philosophy.json').is_file():
        raise ArchiveError('philosophy lab marker missing')
    if archive_writer is not None:
        if not hasattr(archive_writer, '_ensure_open') or archive_writer.root != root / 'research/archive':
            raise ArchiveError('live writer must belong to this exact laboratory archive')
        archive_writer._ensure_open()
        return root, archive_writer
    return root, Archive(root / 'research/archive').init()


def with_archive(function):
    """Acquire archive before bridge lock; permit one explicit same-lock batch."""
    @functools.wraps(function)
    def wrapped(root, *args, archive_writer=None, **kwargs):
        root, archive = lab(root, archive_writer)
        if archive_writer is not None:
            return function(root, *args, archive_writer=archive_writer, **kwargs)
        with archive.writer() as writer:
            return function(root, *args, archive_writer=writer, **kwargs)
    return wrapped


@contextlib.contextmanager
def bridge_lock(root):
    base = _safe_path(root / 'research/bridge')
    base.mkdir(parents=True, exist_ok=True)
    fd = os.open(_safe_path(base / '.lock'), os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise ArchiveError('unsafe bridge lock')
        fcntl.flock(fd, fcntl.LOCK_EX)
        yield
    finally:
        os.close(fd)


def event(start, kind, job_id, payload, *, parents=None, outputs=None, session=None, attempt='bridge-v1'):
    return {'kind': kind, 'actor': {'id': 'philosophy-bridge', 'role': 'tool'},
            'session_id': session or start['session_id'], 'run_id': start['run_id'],
            'operation_id': 'bridge:' + job_id, 'attempt_id': attempt,
            'bindings': start['bindings'], 'parents': parents or [start['id']],
            'outputs': outputs or [], 'payload': {'protocol': PROTOCOL, **payload}}


def prepared(archive, job_id, events=None):
    identifier(job_id)
    found = [e for e in (events if events is not None else archive.events())
             if e['kind'] == 'bridge.job.prepared' and e['payload'].get('job_id') == job_id]
    if len(found) != 1:
        raise ArchiveError('exact prepared job not found')
    record = found[0]
    manifest = strict_json(archive.get(record['payload']['manifest_sha256']))
    return record, manifest


def publish_directory(target, files, output=False):
    target = _safe_path(target)
    if target.exists():
        existing, ignored = tree(target)
        if output:
            raise ArchiveError('workspace exists; verify explicit resume instead')
        if existing != files or ignored:
            raise ArchiveError('immutable packet already exists with different bytes')
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix='.bridge-stage-', dir=target.parent))
    for name, data in sorted(files.items()):
        dest = stage / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        _publish(dest, data)
    if output:
        (stage / 'output').mkdir()
    _fsync_dir(stage)
    if target.exists() or target.is_symlink():
        raise ArchiveError('publication collision; staged bytes retained')
    os.rename(stage, target)
    _fsync_dir(target.parent)


@with_archive
def prepare(root, request, *, archive_writer=None, preview=False):
    root, archive = lab(root, archive_writer)
    if not isinstance(request, dict):
        request = strict_json(read_file(_safe_path(root / relative(str(request)))))
    required = {'job_id', 'essay_id', 'run_id', 'stage', 'prompt'}
    optional = {'selected_inputs', 'model_requested', 'effort_requested', 'style', 'parent_job_id', 'required_outputs', 'public_web', 'purpose', 'export_review', 'workspace_layout'}
    if not isinstance(request, dict) or not required <= set(request) or set(request) - required - optional:
        raise ArchiveError('job request keys differ from contract')
    for name in ('job_id', 'essay_id', 'run_id'):
        identifier(request[name])
    if request['stage'] not in {'author', 'critic', 'revision', 'technical'}:
        raise ArchiveError('unsupported job stage')
    if not isinstance(request['prompt'], str) or not request['prompt'].strip():
        raise ArchiveError('nonempty self-contained prompt required')
    if len(request['prompt'].encode()) > MAX_FILE:
        raise ArchiveError('prompt exceeds byte bound')
    for key in ('model_requested', 'effort_requested', 'style'):
        if key in request and (not isinstance(request[key], str) or not 0 < len(request[key]) <= 4096):
            raise ArchiveError('requested settings must be bounded text')
    if 'public_web' in request and not isinstance(request['public_web'], bool):
        raise ArchiveError('public_web must be boolean')
    if 'required_outputs' in request and (not isinstance(request['required_outputs'], list) or len(request['required_outputs']) > 64):
        raise ArchiveError('required_outputs must be bounded list')
    with bridge_lock(root):
        start = start_record(archive, request['run_id'])
        if request['stage'] == 'technical' and start['payload']['purpose'] != 'technical':
            raise ArchiveError('technical jobs require a technical round')
        parents = [start['id']]
        parent_job = request.get('parent_job_id')
        if parent_job:
            parent, pm = prepared(archive, identifier(parent_job))
            if pm['essay_id'] != request['essay_id']:
                raise ArchiveError('cross-essay continuation forbidden')
            parents.append(parent['id'])
        template_root = root / 'templates/philosophy_claude'
        files = {'prompt.md': request['prompt'].encode(),
                 'output-contract.md': read_file(template_root / 'output-contract.md')}
        instructions = read_file(template_root / 'CLAUDE.md')
        settings = read_file(template_root / 'settings.json')
        layout = request.get('workspace_layout', 'leaf')
        if layout not in ('leaf', 'persistent'):
            raise ArchiveError('unknown workspace layout')
        if layout == 'persistent':
            prefix = 'work/' + request['job_id'] + '/'
            # New packet only: exact rendered bytes are subsequently reviewed and bound.
            def scoped(text):
                return re.sub(r'(?<![A-Za-z0-9_/-])(input|output)/', lambda m: prefix + m.group(1) + '/', text)
            files['prompt.md'] = scoped(request['prompt']).encode()
            files['output-contract.md'] = scoped(files['output-contract.md'].decode()).encode()
            instructions = scoped(instructions.decode().replace('job needs its own leaf workspace.', 'job needs a fresh chat in this persistent project.')).encode() + (
                '\nPersistent-project contract: this fresh chat is bound ONLY to ' + request['job_id'] +
                '. Before each work step reread CURRENT.json; stop if its job_id changes or state is not ACTIVE. '
                'Never follow a later job from this chat. Keep all output at the job-specific paths above. '
                'One permanent project folder is used; new jobs require fresh chats, not new project folders.\n').encode()
            sv = strict_json(settings)
            for key in ('allow', 'deny'):
                sv['permissions'][key] = [r.replace('(/input/', '(/' + prefix + 'input/').replace('(/output/', '(/' + prefix + 'output/') for r in sv['permissions'][key]]
            sv['permissions']['deny'].extend(['Read(/jobs/**)', 'Edit(/jobs/**)', 'Read(/archive/**)', 'Edit(/archive/**)', 'Edit(/work/*/input/**)'])
            settings = canonical(sv)
        if not request.get('public_web', True):
            settings_value = strict_json(settings)
            settings_value['permissions']['allow'] = [x for x in settings_value['permissions']['allow'] if x not in {'WebSearch', 'WebFetch'}]
            settings_value['permissions']['deny'].extend(['WebSearch', 'WebFetch'])
            settings = canonical(settings_value)
        input_records, local_sources = [], []
        inputs = request.get('selected_inputs', [])
        if not isinstance(inputs, list) or len(inputs) > 64:
            raise ArchiveError('bounded explicit selected_inputs required')
        for item in inputs:
            if not isinstance(item, dict) or not {'source', 'label'} <= set(item) or set(item) - {'source', 'label', 'scope', 'owner_essay_id'}:
                raise ArchiveError('selected input requires source/label and explicit optional scope')
            source, label = relative(item['source']), relative(item['label'])
            scope = item.get('scope', 'essay')
            owner = item.get('owner_essay_id', request['essay_id'] if scope == 'essay' else None)
            if scope not in {'essay', 'neutral'} or (scope == 'essay' and owner != request['essay_id']) or (scope == 'neutral' and owner is not None):
                raise ArchiveError('selected input belongs to another essay')
            dest = 'inputs/' + label
            if dest in files:
                raise ArchiveError('duplicate input destination')
            data = read_file(root / source)
            files[dest] = data
            input_records.append({'path': dest, 'scope': scope, 'owner_essay_id': owner, 'sha256': sha(data)})
            local_sources.append({'source': source, 'destination': dest, 'sha256': sha(data)})
        required_outputs = sorted(set(['report.md'] + request.get('required_outputs', [])))
        for name in required_outputs:
            relative(name)
        labels = [unicodedata.normalize('NFKC', p).casefold() for p in files]
        if len(set(labels)) != len(labels) or sum(map(len, files.values())) > MAX_TOTAL:
            raise ArchiveError('input packet collision or total size bound exceeded')
        if any('/'.join(path.split('/')[:n]) in labels for path in labels for n in range(1, len(path.split('/')))):
            raise ArchiveError('input file/directory topology collision')
        manifest = {'protocol': PROTOCOL, 'job_id': request['job_id'], 'essay_id': request['essay_id'],
                    'run_id': request['run_id'], 'stage': request['stage'], 'parent_job_id': parent_job,
                    'model_requested': request.get('model_requested', 'UNKNOWN'),
                    'effort_requested': request.get('effort_requested', 'UNKNOWN'),
                    'style': request.get('style', 'simple human prose'),
                    'public_web': request.get('public_web', True), 'required_outputs': required_outputs,
                    'selected_inputs': input_records, 'files': file_records(files),
                    'claude_instructions_sha256': sha(instructions), 'settings_sha256': sha(settings),
                    'fresh_nonfork_required': request['stage'] in {'author', 'critic', 'revision'},
                    'shared_substantive_memory': False,
                    'isolation_boundary': 'explicit input scope and fresh context; not OS sandbox attestation', **({'workspace_layout': 'persistent'} if layout == 'persistent' else {})}
        encoded = canonical(manifest)
        target = root / 'research/bridge/jobs' / request['job_id']
        payload_files = {**files, 'manifest.json': encoded, 'CLAUDE.md': instructions, 'settings.json': settings}
        from claude_export import candidate, verify as verify_export
        policy_path = root / 'claude-export-policy.json'
        policy = strict_json(read_file(policy_path)) if policy_path.exists() else {'private_terms': []}
        if preview:
            return candidate(payload_files, policy)
        review_digest = None
        if policy_path.exists() or 'export_review' in request:
            if 'export_review' not in request:
                raise ArchiveError('export review required; prepare a preview and review all selected bytes')
            review = strict_json(read_file(root / relative(request['export_review'])))
            review_digest = verify_export(payload_files, policy, review)
        # Detect ID conflicts before publishing or storing changed bytes.
        old = [e for e in archive.events() if e['kind'] == 'bridge.job.prepared' and e['payload'].get('job_id') == request['job_id']]
        if old and old[0]['payload']['manifest_sha256'] != sha(encoded):
            raise ArchiveError('job ID is immutable; use a new job ID')
        with archive.writer() as writer:
            outputs = sorted(set(writer.put(b) for b in payload_files.values()))
            if review_digest:
                assert writer.put(canonical(review)) == review_digest
                outputs.append(review_digest)
            saved = writer.append(event(start, 'bridge.job.prepared', request['job_id'],
                {'job_id': request['job_id'], 'essay_id': request['essay_id'], 'manifest_sha256': sha(encoded),
                 'file_records': file_records(payload_files), 'selected_local_sources': local_sources,
                 'publication': 'local derived packet only; no model launched', **({'export_review_sha256': review_digest} if review_digest else {})}, parents=parents, outputs=outputs),
                'bridge-prepare:' + request['job_id'])
        publish_directory(target, payload_files)
        return {'job_id': request['job_id'], 'manifest_sha256': sha(encoded), 'event_id': saved['id'], 'packet': str(target), 'status': 'PREPARED'}


def expected_packet(archive, record):
    return {f['path']: archive.get(f['sha256']) for f in record['payload']['file_records']}


def verify_prepared_export(root, archive, record):
    from claude_export import verify
    policy_path = root / 'claude-export-policy.json'
    if not policy_path.exists():
        return
    digest = record['payload'].get('export_review_sha256')
    if not digest:
        raise ArchiveError('unreviewed legacy packet cannot be newly activated; prepare a reviewed successor')
    verify(expected_packet(archive, record), strict_json(read_file(policy_path)), strict_json(archive.get(digest)))


def output_directory(workspace):
    current = strict_json(read_file(workspace / 'CURRENT.json'))
    if current.get('protocol') == 'philosophy-claude-project.v2':
        return workspace / 'work' / identifier(current['job_id']) / 'output'
    return workspace / 'output'


def workspace_job(root, workspace, archive_writer=None, require_activation=True):
    root, archive = lab(root, archive_writer)
    workspace = _safe_path(workspace)
    current = strict_json(read_file(workspace / 'CURRENT.json'))
    if current.get('protocol') == 'philosophy-claude-project.v2':
        from claude_project import resolve
        return resolve(root, workspace, archive, current)
    if set(current) != {'protocol', 'job_id', 'manifest_sha256'} or current['protocol'] != PROTOCOL:
        raise ArchiveError('invalid current job pointer')
    record, manifest = prepared(archive, current['job_id'])
    if require_activation:
        activations = [e for e in archive.events() if e['kind'] == 'bridge.job.activated'
                       and e['payload'].get('job_id') == current['job_id']]
        if (len(activations) != 1 or activations[0]['payload'].get('workspace') != str(workspace)
                or activations[0]['payload'].get('workspace_sha256') != sha(str(workspace).encode())
                or activations[0]['payload'].get('manifest_sha256') != record['payload']['manifest_sha256']
                or activations[0]['parents'] != [record['id']]):
            raise ArchiveError('job requires one exact immutable activated workspace binding')
    packet = expected_packet(archive, record)
    if current['manifest_sha256'] != sha(packet['manifest.json']):
        raise ArchiveError('workspace names wrong job input digest')
    observed, _ = tree(workspace / 'input')
    expected = {k: v for k, v in packet.items() if k not in {'CLAUDE.md', 'settings.json'}}
    if observed != expected or read_file(workspace / 'CLAUDE.md') != packet['CLAUDE.md'] or read_file(workspace / '.claude/settings.json') != packet['settings.json']:
        raise ArchiveError('workspace instructions or immutable inputs changed')
    local_settings = workspace / '.claude/settings.local.json'
    if local_settings.exists() and strict_json(read_file(local_settings)) != {}:
        raise ArchiveError('workspace local settings override fixed job policy')
    return root, archive, workspace, record, manifest


@with_archive
def activate(root, job_id, workspace, *, archive_writer=None):
    root, archive = lab(root, archive_writer)
    workspace = _safe_path(workspace)
    # A fresh leaf does not expose any old essay history. Never reuse it for another job.
    with bridge_lock(root):
        record, manifest = prepared(archive, job_id)
        activations = [e for e in archive.events() if e['kind'] == 'bridge.job.activated'
                       and e['payload'].get('job_id') == job_id]
        if activations and (len(activations) != 1 or activations[0]['payload'].get('workspace') != str(workspace)):
            raise ArchiveError('job is already bound to another workspace; create a new job')
        packet = expected_packet(archive, record)
        if manifest.get('workspace_layout') == 'persistent':
            raise ArchiveError('persistent packet requires claude_project publish')
        if not activations:
            verify_prepared_export(root, archive, record)
        if workspace.exists():
            _, _, _, existing, _ = workspace_job(root, workspace, archive_writer, require_activation=bool(activations))
            if existing['id'] != record['id']:
                raise ArchiveError('different job requires a fresh leaf workspace')
        else:
            files = {'CLAUDE.md': packet['CLAUDE.md'], '.claude/settings.json': packet['settings.json'],
                     'CURRENT.json': canonical({'protocol': PROTOCOL, 'job_id': job_id, 'manifest_sha256': sha(packet['manifest.json'])})}
            files.update({'input/' + k: v for k, v in packet.items() if k not in {'CLAUDE.md', 'settings.json'}})
            publish_directory(workspace, files, output=True)
        start = start_record(archive, manifest['run_id'])
        binding = sha(str(workspace).encode())
        saved = archive.append(event(start, 'bridge.job.activated', job_id,
            {'job_id': job_id, 'workspace_sha256': binding, 'workspace': str(workspace),
             'manifest_sha256': record['payload']['manifest_sha256'], 'model_launched': False}, parents=[record['id']]),
            'bridge-activate:' + job_id + ':' + binding)
        return {'status': 'READY_FOR_MANUAL_LAUNCH', 'workspace': str(workspace), 'job_id': job_id, 'event_id': saved['id']}


@with_archive
def claim(root, workspace, session_id, attempt_id, resume=False, *, archive_writer=None):
    identifier(attempt_id)
    if not isinstance(session_id, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.:-]{0,180}', session_id):
        raise ArchiveError('exact observed session ID required')
    root, archive, workspace, record, manifest = workspace_job(root, workspace, archive_writer)
    with bridge_lock(root):
        previous = [e for e in archive.events() if e['kind'] == 'bridge.job.claimed']
        for e in previous:
            if e['session_id'] == session_id and e['payload'].get('job_id') != manifest['job_id']:
                raise ArchiveError('session reuse across jobs forbidden; use a fresh non-fork context')
        same = [e for e in previous if e['payload'].get('job_id') == manifest['job_id']]
        if any(e['payload'].get('workspace') != str(workspace)
               or e['payload'].get('manifest_sha256') != record['payload']['manifest_sha256'] for e in same):
            raise ArchiveError('claim history conflicts with exact job workspace/input binding')
        replay = next((e for e in same if e['attempt_id'] == attempt_id), None)
        if replay:
            if replay['session_id'] != session_id or replay['payload']['resume'] != resume:
                raise ArchiveError('attempt ID cannot be rebound')
            return {'status': 'CLAIMED', 'event_id': replay['id'], 'job_id': manifest['job_id'], 'session_id': session_id, 'attempt_id': attempt_id}
        if same and not resume and any(e['attempt_id'] != attempt_id for e in same):
            raise ArchiveError('continuation needs explicit resume and new attempt ID')
        if resume and not same:
            raise ArchiveError('cannot resume a job without a prior claim')
        start = start_record(archive, manifest['run_id'])
        saved = archive.append(event(start, 'bridge.job.claimed', manifest['job_id'],
            {'job_id': manifest['job_id'], 'essay_id': manifest['essay_id'], 'workspace': str(workspace),
             'manifest_sha256': record['payload']['manifest_sha256'], 'resume': resume,
             'session_binding': 'explicit operator-selected ID; native capture verifies cwd/session separately',
             'context_freshness': 'required; not proven by folder or claim'},
             parents=[record['id']] + ([same[-1]['id']] if same and same[-1]['attempt_id'] != attempt_id else []),
             session=session_id, attempt=attempt_id), 'bridge-claim:' + manifest['job_id'] + ':' + attempt_id)
        return {'status': 'CLAIMED', 'event_id': saved['id'], 'job_id': manifest['job_id'], 'session_id': session_id, 'attempt_id': attempt_id}


def metadata_state(files, job_id):
    if 'metadata.json' not in files:
        return {'status': 'ABSENT', 'observed_model': 'UNKNOWN', 'observed_effort': 'UNKNOWN'}
    try:
        value = strict_json(files['metadata.json'])
    except (ValueError, UnicodeError):
        return {'status': 'INVALID_PRESERVED_INERT'}
    if not isinstance(value, dict):
        return {'status': 'INVALID_PRESERVED_INERT'}
    if 'job_id' in value and value['job_id'] != job_id:
        raise ArchiveError('output metadata names a different job')
    allowed = {'job_id', 'observed_model', 'observed_effort', 'session_id', 'started_at', 'finished_at', 'response_wall_seconds', 'status', 'limitations'}
    if set(value) - allowed:
        return {'status': 'INVALID_PRESERVED_INERT'}
    return {'status': 'UNVERIFIED_PROVIDER_REPORT', 'values': value}


@with_archive
def collect(root, workspace, disposition='partial', *, archive_writer=None):
    if disposition not in {'partial', 'complete'}:
        raise ArchiveError('disposition must be partial or complete')
    root, archive, workspace, record, manifest = workspace_job(root, workspace, archive_writer)
    with bridge_lock(root):
        files, ignored = tree(output_directory(workspace), runtime=True)
        missing = [name for name in manifest['required_outputs'] if name not in files or not files[name].strip()]
        if disposition == 'complete' and missing:
            raise ArchiveError('completed return missing required artifacts: ' + ', '.join(missing))
        metadata = metadata_state(files, manifest['job_id'])
        history = archive.events()
        earlier = [e for e in history if e['kind'] == 'bridge.return.collected' and e['payload'].get('job_id') == manifest['job_id']]
        # Progress/metadata may evolve; numbered manuscript artifacts cannot change or disappear.
        mutable = {'metadata.json', 'report.md'}
        for old in earlier:
            for f in old['payload']['file_records']:
                if f['path'] not in mutable and (f['path'] not in files or sha(files[f['path']]) != f['sha256']):
                    raise ArchiveError('previous artifact overwritten or removed; preserve it and write a new version')
        records = file_records(files)
        digest = sha(canonical({'job_id': manifest['job_id'], 'manifest_sha256': record['payload']['manifest_sha256'], 'files': records}))
        start = start_record(archive, manifest['run_id'])
        claims = [e for e in history if e['kind'] == 'bridge.job.claimed' and e['payload'].get('job_id') == manifest['job_id']]
        if any(e['payload'].get('workspace') != str(workspace)
               or e['payload'].get('manifest_sha256') != record['payload']['manifest_sha256'] for e in claims):
            raise ArchiveError('return has conflicting historical claim/workspace bindings')
        claim_record = claims[-1] if claims else None
        capture = [e for e in history if claim_record is not None and e['kind'] == 'capture.coverage'
                   and e['payload'].get('job_id') == manifest['job_id']
                   and e['payload'].get('workspace') == str(workspace)
                   and e['session_id'] == claim_record['session_id']
                   and e['attempt_id'] == claim_record['attempt_id']
                   and e['run_id'] == manifest['run_id']
                   and claim_record['id'] in e['parents']]
        coverage = capture[-1] if capture else None
        collection_id = sha(canonical({'content_set_sha256': digest, 'disposition': disposition,
                             'claim_event_id': claim_record['id'] if claim_record else None,
                             'coverage_event_id': coverage['id'] if coverage else None}))
        previous = next((e for e in earlier if e['payload'].get('collection_id') == collection_id), None)
        if previous:
            # Repair only a missing derived copy after an interrupted publication;
            # the original canonical event and objects are never replaced.
            encoded = canonical({k: v for k, v in previous['payload'].items() if k != 'protocol'})
            target = root / 'research/bridge/returns' / manifest['job_id'] / collection_id
            publish_directory(target, {**{'artifacts/' + p: b for p, b in files.items()}, 'collection.json': encoded})
            return {'status': 'ALREADY_COLLECTED', 'event_id': previous['id'], 'job_id': manifest['job_id'], 'content_set_sha256': digest, 'collection_id': collection_id, 'disposition': disposition}
        metadata_report = {'job_id': manifest['job_id'], 'manifest_sha256': record['payload']['manifest_sha256'],
                           'workspace': str(workspace), 'collection_id': collection_id,
                           'claim_event_id': claim_record['id'] if claim_record else None,
                           'file_records': records, 'content_set_sha256': digest, 'disposition': disposition,
                           'status': 'COMPLETE_ARTIFACTS_UNVERIFIED' if disposition == 'complete' else 'INCOMPLETE',
                           'missing_final_artifacts': missing, 'metadata': metadata, 'ignored_entries': ignored,
                           'source_coverage': coverage['payload'].get('status') if coverage else 'NOT_CAPTURED',
                           'coverage_event_id': coverage['id'] if coverage else None,
                           'code_executed': False, 'philosophical_status_promoted': False}
        encoded = canonical(metadata_report)
        with archive.writer() as writer:
            objects = sorted(set([writer.put(b) for b in files.values()] + [writer.put(encoded)]))
            saved = writer.append(event(start, 'bridge.return.collected', manifest['job_id'], metadata_report,
                parents=[record['id']] + ([claim_record['id']] if claim_record else []) + ([coverage['id']] if coverage else []),
                outputs=objects, session=claim_record['session_id'] if claim_record else None,
                attempt=claim_record['attempt_id'] if claim_record else 'bridge-v1'),
                'bridge-collect:' + manifest['job_id'] + ':' + collection_id)
        target = root / 'research/bridge/returns' / manifest['job_id'] / collection_id
        publish_directory(target, {**{'artifacts/' + p: b for p, b in files.items()}, 'collection.json': encoded})
        return {'status': metadata_report['status'], 'event_id': saved['id'], 'job_id': manifest['job_id'],
                'content_set_sha256': digest, 'collection_id': collection_id, 'disposition': disposition, 'source_coverage': metadata_report['source_coverage'], 'path': str(target)}


@with_archive
def status(root, workspace=None, *, archive_writer=None):
    root, archive = lab(root, archive_writer)
    events = archive.events()
    if workspace:
        _, _, _, record, manifest = workspace_job(root, workspace, archive_writer)
        output, _ = tree(output_directory(Path(workspace)), runtime=True)
        return {'job_id': manifest['job_id'], 'input_verified': True, 'output_files': len(output),
                'model_launched_by_bridge': False, 'history': [{'kind': e['kind'], 'id': e['id']} for e in events if e['payload'].get('job_id') == manifest['job_id']]}
    return {'jobs': [{'job_id': e['payload']['job_id'], 'event_id': e['id']} for e in events if e['kind'] == 'bridge.job.prepared'], 'model_launched_by_bridge': False}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    sub = p.add_subparsers(dest='command', required=True)
    q = sub.add_parser('prepare'); q.add_argument('--request', required=True); q.add_argument('--preview', action='store_true')
    q = sub.add_parser('activate'); q.add_argument('--job-id', required=True); q.add_argument('--workspace', type=Path, required=True)
    for name in ('claim', 'resume'):
        q = sub.add_parser(name); q.add_argument('--workspace', type=Path, required=True); q.add_argument('--session-id', required=True); q.add_argument('--attempt-id', required=True)
    q = sub.add_parser('collect'); q.add_argument('--workspace', type=Path, required=True); q.add_argument('--disposition', choices=['partial', 'complete'], default='partial')
    q = sub.add_parser('status'); q.add_argument('--workspace', type=Path)
    args = p.parse_args(argv)
    try:
        if args.command == 'prepare': result = prepare(args.root, args.request, preview=args.preview)
        elif args.command == 'activate': result = activate(args.root, args.job_id, args.workspace)
        elif args.command in {'claim', 'resume'}: result = claim(args.root, args.workspace, args.session_id, args.attempt_id, args.command == 'resume')
        elif args.command == 'collect': result = collect(args.root, args.workspace, args.disposition)
        else: result = status(args.root, args.workspace)
    except (ValueError, OSError, KeyError, TypeError) as exc:
        p.exit(2, 'bridge failed: ' + str(exc) + '\n')
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
