#!/usr/bin/env python3
"""Local, project-scoped Codex collector. No model or network calls."""
from __future__ import annotations

import argparse
import collections
import contextlib
import copy
import datetime as dt
import fcntl
import hashlib
import json
import os
import re
from pathlib import Path
import signal
import stat
import sys
import time
import uuid

from capture_codex import regular_file, rollout_file, strict_json, classify, TOOL_TYPES, CALL_TYPES, OUTPUT_TYPES, automation_heartbeat
from research_archive import Archive, ArchiveError, canonical, _safe_path
from collector_source import discover_sessions, project_record
from collector_safety import contains_credential, redact_value

VERSION = 1
STOP = False
COMPATIBLE_CAPTURE_SIGNATURE = '0abd26f67ef779ffd625bdaf3d331ed6c035b5f5cdc13d5f804df13b3dd5e43f'
COMPATIBLE_COLLECTOR_SHA256 = '3f91e9359cd91a65389092847aa96a4aa9f710d63de45ce014be0a7b05bdf3d0'
CAPTURE_VERSION_ORDER = ('collector/config.json', 'scripts/collector.py',
                        'scripts/collector_source.py', 'scripts/collector_safety.py',
                        'scripts/capture_codex.py', 'scripts/codex_rollout.py',
                        'scripts/research_archive.py', 'scripts/collector_views.py')
COMPATIBILITY_PATH = 'collector/capture-compatibility.json'


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def parse_capture_compatibility(raw):
    """One bounded transition; malformed declarations never enable collection."""
    value = strict_json(raw)
    fields = {'schema_version', 'purpose', 'from_signature', 'from_collector_sha256', 'current_files'}
    replacements = {'scripts/collector.py', 'scripts/collector_views.py'}
    if (not isinstance(value, dict) or set(value) != fields
            or type(value.get('schema_version')) is not int or value['schema_version'] != 1
            or value.get('purpose') != 'renderer-only-compatibility-20261031'
            or not isinstance(value.get('current_files'), dict)
            or set(value['current_files']) != replacements):
        raise ValueError('invalid capture compatibility manifest schema')
    hashes = [value['from_signature'], value['from_collector_sha256'], *value['current_files'].values()]
    if any(not isinstance(h, str) or not re.fullmatch('[a-f0-9]{64}', h) for h in hashes):
        raise ValueError('invalid capture compatibility manifest hash')
    return value


def capture_compatibility(manifest, current_files, index, archive):
    """Verify stored source bytes before recognizing the single old signature.

    This does not rewrite or relabel any cursor. Other code/config changes keep
    the ordinary strict reset behavior, even with a well-formed stale manifest.
    """
    inactive = {'active': False, 'reason': 'not_configured'}
    if manifest is None:
        return inactive
    inactive['reason'] = 'exact_transition_not_compatible'
    if (manifest['from_signature'] != COMPATIBLE_CAPTURE_SIGNATURE
            or manifest['from_collector_sha256'] != COMPATIBLE_COLLECTOR_SHA256):
        return inactive
    for name, expected in manifest['current_files'].items():
        if name not in current_files or digest(current_files[name]) != expected:
            return inactive
    old = index.get('collector-version:' + manifest['from_signature'])
    if (not old or old.get('kind') != 'collector.version'
            or old.get('payload', {}).get('signature') != manifest['from_signature']):
        return inactive
    files = old['payload'].get('files')
    if not isinstance(files, dict) or set(files) != set(CAPTURE_VERSION_ORDER):
        return inactive
    if files.get('scripts/collector.py') != COMPATIBLE_COLLECTOR_SHA256:
        return inactive
    if any(not isinstance(h, str) or not re.fullmatch('[a-f0-9]{64}', h) for h in files.values()):
        return inactive
    if not set(files.values()) <= set(old.get('outputs', [])):
        return inactive
    # Archive.get verifies each immutable object's hash. A corrupt/missing
    # object is an archive error, never permission to skip verification.
    stored = {name: archive.get(files[name]) for name in CAPTURE_VERSION_ORDER}
    old_signature = digest(b''.join(name.encode() + b'\0' + stored[name] for name in CAPTURE_VERSION_ORDER))
    if old_signature != manifest['from_signature']:
        return inactive
    if set(current_files) != set(CAPTURE_VERSION_ORDER) | {COMPATIBILITY_PATH}:
        return inactive
    for name in CAPTURE_VERSION_ORDER:
        if name not in manifest['current_files'] and current_files[name] != stored[name]:
            return inactive
    return {'active': True, 'from_signature': old_signature, 'from_version_event_id': old['id'],
            'source_session_id': old['session_id'],
            'boundary': 'Only this audited renderer/version transition. Original cursors, capture gaps and records remain unchanged.'}


def codex_raw_index(events):
    """Only Codex line envelopes belong in the Codex collector cursor index.

    Claude fragments and unknown captures stay in the archive/provider views.
    Do not interpret their field names or collapse their fragment ordinals.
    A malformed declared Codex envelope still raises instead of being hidden.
    """
    return {(e['session_id'], e['payload']['source_line']): e for e in events
            if e['kind'] == 'capture.raw_record'
            and e['payload'].get('format') == 'codex-visible-selection.v1'}


def coverage_summary(sessions):
    """Collection liveness, text completeness and tool review are different claims."""
    if not isinstance(sessions, list):
        return {'coverage_healthy': None, 'unresolved_gap_count': None,
                'sessions_with_gaps': None, 'tool_schema_gap_count': None,
                'text_or_unknown_gap_count': None, 'pending_tool_records': None,
                'boundary': 'Coverage unavailable: this report has no session inventory.'}
    # An unreadable source is not evidence of complete coverage. Its last
    # accepted cursor still contributes known gaps/pending tools, explicitly
    # without claiming that cursor covers today's source.
    failed = [s for s in sessions if s.get('status') == 'ERROR']
    def known(s):
        if s.get('status') == 'ERROR':
            cursor = s.get('last_committed_cursor') or {}
            return cursor.get('gaps', []), cursor.get('pending_tools', 0)
        return s.get('gaps', []), s.get('pending_tool_records', 0)
    gaps = [(s['session_id'], g) for s in sessions for g in known(s)[0]]
    tool_gaps = sum(g.get('surface') == 'tools' for _, g in gaps)
    return {'coverage_healthy': not gaps and not failed, 'unresolved_gap_count': len(gaps),
            'sessions_with_gaps': len({sid for sid, _ in gaps}),
            'tool_schema_gap_count': tool_gaps, 'text_or_unknown_gap_count': len(gaps)-tool_gaps,
            'pending_tool_records': sum(known(s)[1] for s in sessions),
            'sessions_with_errors': len(failed),
            'error_sessions_without_cursor': sum(not s.get('last_committed_cursor') for s in failed),
            'counts_include_last_committed_cursors': bool(failed)}


def add_coverage_status(report):
    summary = coverage_summary(report.get('sessions'))
    report['coverage_summary'] = summary
    report['coverage_healthy'] = summary['coverage_healthy']
    attention = list(report.get('attention', []))
    if summary['coverage_healthy'] is None and summary['boundary'] not in attention:
        attention.append(summary['boundary'])
    if summary['unresolved_gap_count']:
        warning = ('Unresolved coverage gaps: ' + str(summary['unresolved_gap_count']) +
                   ' in ' + str(summary['sessions_with_gaps']) + ' session(s); inspect per-session gaps.')
        if warning not in attention:
            attention.append(warning)
    if summary.get('sessions_with_errors'):
        warning = (str(summary['sessions_with_errors']) + ' session(s) could not be read; '
                   'known counts include last committed cursors, not verified current coverage.')
        if warning not in attention:
            attention.append(warning)
    report['attention'] = attention
    return report


def cursor_text_status(cursor):
    return 'GAPS' if any(g.get('surface') != 'tools' for g in cursor.get('gaps', [])) else 'TEXT_COMPLETE_THROUGH_CURSOR'


def cursor_tools_status(cursor):
    if any(g.get('surface') == 'tools' for g in cursor.get('gaps', [])):
        return 'UNSUPPORTED_SCHEMA'
    return 'REVIEW_REQUIRED' if cursor.get('pending_tools') else 'NO_PENDING_TOOLS'


def log_error(root,message):
    directory=_safe_path(Path(root)/'collector/runtime'); directory.mkdir(parents=True,exist_ok=True)
    path=_safe_path(directory/'operational.log'); older=_safe_path(directory/'operational.log.1')
    if path.exists() and path.stat().st_size>=256*1024: os.replace(path,older)
    with path.open('a') as stream:
        stream.write(now()+' '+str(message)[:2000]+'\n'); stream.flush(); os.fsync(stream.fileno())


def atomic_json(path, value):
    path = _safe_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.parent / ('.tmp-' + uuid.uuid4().hex)
    try:
        with temp.open('xb') as stream:
            os.chmod(temp, 0o600)
            stream.write(canonical(value)); stream.flush(); os.fsync(stream.fileno())
        os.replace(temp, path)
        fd = os.open(path.parent, os.O_DIRECTORY)
        try: os.fsync(fd)
        finally: os.close(fd)
    finally:
        if temp.exists(): temp.unlink()


class Collector:
    def __init__(self, root, config_path=None):
        self.root = _safe_path(Path(root).absolute())
        with regular_file(self.root / 'LAB_PROFILE.json') as f: profile=strict_json(f.read())
        with regular_file(self.root / '.lab/philosophy.json') as f: marker=strict_json(f.read())
        if (profile.get('lab',{}).get('kind')!='PHILOSOPHY_PROGRAM'
                or marker.get('kernel')!='philosophy.v1' or marker.get('archive_format')!='research-archive.v1'):
            raise ValueError('collector target must be an identified philosophy laboratory')
        self.runtime = self.root / 'collector/runtime'
        self.runtime.mkdir(parents=True, exist_ok=True)
        self.config_path = config_path or self.root / 'collector/config.json'
        with regular_file(self.config_path) as f:
            self.config_bytes = f.read(); self.config = strict_json(self.config_bytes)
        if self.config.get('schema_version') != VERSION:
            raise ValueError('unsupported collector configuration')
        if set(self.config)-{'schema_version','project_root','state_db','interval_seconds','explicit_sessions'}:
            raise ValueError('unknown collector configuration field')
        if contains_credential(self.config):
            raise ValueError('credential-shaped value excluded from collector configuration')
        self.compatibility_manifest = None
        compatibility_raw = None
        compatibility_path = self.root / COMPATIBILITY_PATH
        if os.path.lexists(compatibility_path):
            with regular_file(compatibility_path) as stream:
                compatibility_raw = stream.read()
            self.compatibility_manifest = parse_capture_compatibility(compatibility_raw)
        if self.config.get('project_root', '.') != '.':
            raise ValueError('project_root must be the current collector project')
        self.db = Path(self.config['state_db']).expanduser().absolute()
        self.explicit = self.config.get('explicit_sessions', {})
        self.interval = self.config.get('interval_seconds', 10)
        if type(self.interval) not in (int, float) or not 1 <= self.interval <= 3600:
            raise ValueError('invalid interval')
        self.archive = Archive(self.root / 'research/archive')
        self.archive.init()
        with self.archive.writer() as writer:
            self.events = writer.events()
            self.event_dir_mtime = (self.archive.root / 'events').stat().st_mtime_ns
        self.index = {e['delivery_key']: e for e in self.events}
        self.raw = codex_raw_index(self.events)
        self.runs = {}
        for e in self.raw.values(): self.runs.setdefault(e['session_id'], e['run_id'])
        self.state = {}; self.coverage_ids = {}
        for e in self.events:
            if e['kind'] == 'collector.coverage':
                self.state[e['session_id']] = e['payload']['cursor']
                self.coverage_ids[e['session_id']] = e['id']
        self.last_verify = time.monotonic()
        self.last_verified_at = now()
        self.version_files = {'collector/config.json':self.config_bytes}
        for name in ('collector.py','collector_source.py','collector_safety.py','capture_codex.py','codex_rollout.py','research_archive.py','collector_views.py'):
            self.version_files['scripts/'+name]=(Path(__file__).parent/name).read_bytes()
        if compatibility_raw is not None:
            self.version_files[COMPATIBILITY_PATH] = compatibility_raw
        self.signature = digest(b''.join(name.encode()+b'\0'+data for name,data in self.version_files.items()))
        self.capture_compatibility = capture_compatibility(
            self.compatibility_manifest, self.version_files, self.index, self.archive)
        self.compatible_signatures = {self.signature}
        if self.capture_compatibility['active']:
            self.compatible_signatures.add(self.capture_compatibility['from_signature'])

    def record_capture_compatibility(self, sink):
        """Append one explicit adoption record and version, never new capture."""
        compatibility = self.capture_compatibility
        if not compatibility['active']:
            return
        key = 'collector-compatibility:' + compatibility['from_signature'] + ':' + self.signature
        if key in self.index:
            return
        version_key = 'collector-version:' + self.signature
        requests = []
        sid = compatibility['source_session_id']
        def request(kind, payload, delivery_key, parents=(), **extra):
            event = {'id': 'collector-' + digest(delivery_key.encode())[:32], 'kind': kind,
                     'actor': {'id': 'local-collector', 'role': 'tool'}, 'session_id': sid,
                     'run_id': 'collector:' + sid, 'operation_id': 'collector:' + sid,
                     'attempt_id': 'collector-v1', 'parents': list(parents), 'payload': payload, **extra}
            requests.append((event, delivery_key))
            return event['id']
        if version_key in self.index:
            version_id = self.index[version_key]['id']
        else:
            outputs = [sink.put(raw) for raw in self.version_files.values()]
            version_id = request('collector.version', {'signature': self.signature,
                'files': {name: digest(raw) for name, raw in self.version_files.items()}},
                version_key, outputs=outputs)
        manifest_sha = sink.put(self.version_files[COMPATIBILITY_PATH])
        request('collector.capture_compatibility', {
            'protocol': 'renderer-only-compatibility-20261031',
            'from_signature': compatibility['from_signature'], 'to_signature': self.signature,
            'manifest_sha256': manifest_sha, 'capture_rules_unchanged': True,
            'cursors_rewritten': False, 'raw_records_rewritten': False,
            'whole_trace': 'INCOMPLETE', 'boundary': compatibility['boundary']},
            key, parents=[compatibility['from_version_event_id'], version_id], inputs=[manifest_sha])
        committed = sink.append_many(requests)
        self.events.extend(committed)
        for event in committed:
            self.index[event['delivery_key']] = event
        self.event_dir_mtime = (self.archive.root / 'events').stat().st_mtime_ns

    @contextlib.contextmanager
    def lock(self):
        path = _safe_path(self.runtime / 'collector.lock')
        fd = os.open(path, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            yield
        finally: os.close(fd)

    def sync_archive(self, force=False, writer=None):
        changed = (self.archive.root / 'events').stat().st_mtime_ns != self.event_dir_mtime
        if force or changed or time.monotonic() - self.last_verify >= 300:
            self.events = (writer or self.archive).events()
            self.index = {e['delivery_key']: e for e in self.events}
            self.raw = codex_raw_index(self.events)
            for e in self.raw.values(): self.runs.setdefault(e['session_id'], e['run_id'])
            for e in self.events:
                if e['kind']=='collector.coverage':
                    self.state[e['session_id']]=e['payload']['cursor']; self.coverage_ids[e['session_id']]=e['id']
            self.last_verify = time.monotonic(); self.last_verified_at = now()
            self.event_dir_mtime = (self.archive.root / 'events').stat().st_mtime_ns

    def collect(self, reconcile=False):
        with self.lock():
            started = now(); started_mono = time.monotonic()
            sessions = discover_sessions(self.db, self.root, self.explicit)
            results = []; changed = []
            selected={s['session_id'] for s in sessions}
            with self.archive.writer() as writer:
                # Synchronize and publish under one lock. A manual capture or
                # research agent may commit while this collector waits for it.
                self.sync_archive(force=reconcile, writer=writer)
                self.record_capture_compatibility(writer)
                for missing in sorted(set(self.state)-selected):
                    results.append({'session_id':missing,'status':'ERROR','error_type':'MissingSession',
                                    'error':'Previously collected session absent from scoped discovery; originals retained.',
                                    'last_committed_cursor':self.state[missing]})
                for session in sessions:
                    try:
                        result = self.collect_session(session, reconcile, writer)
                        results.append(result)
                        if result['changed']: changed.append(session['session_id'])
                    except Exception as exc:
                        # Report no source text in operational errors.
                        results.append({'session_id': session['session_id'], 'status': 'ERROR',
                                        'error_type': type(exc).__name__, 'error': str(exc)[:500],
                                        'last_committed_cursor': self.state.get(session['session_id'])})
            status = {'schema_version': VERSION, 'pid': os.getpid(), 'last_attempt_at': started,
                      'checked_at': now(), 'last_archive_verified_at': self.last_verified_at,
                      'elapsed_seconds': round(time.monotonic() - started_mono, 6),
                      'interval_seconds': self.interval, 'sessions': results,
                      'discovered_sessions': len(sessions), 'changed_sessions': changed,
                      'chat_sessions':sum(s.get('session_kind')!='internal_runtime' for s in sessions),
                      'internal_excluded_sessions':sum(s.get('session_kind')=='internal_runtime' for s in sessions),
                      'status': 'ERROR' if any(s['status'] == 'ERROR' for s in results) else 'RUNNING',
                      'capture_compatibility': self.capture_compatibility,
                      'boundary': 'Text/metadata automatic; unreviewed tools and unsupported attachments remain explicit gaps.'}
            if changed or reconcile:
                from collector_views import refresh
                refresh(self.root, self.archive, events=self.events,
                        changed_sessions=None if reconcile else set(changed))
            status['elapsed_seconds']=round(time.monotonic()-started_mono,6)
            status['next_poll_delay_seconds']=min(3600,max(self.interval,status['elapsed_seconds']*4))
            status['archive_event_count']=len(self.events)
            status['attention']=['Review archive scale and memory before further growth'] if len(self.events)>=50000 else []
            add_coverage_status(status)
            atomic_json(self.runtime / 'status.json', status)
            return status

    def collect_session(self, session, reconcile=False, writer=None):
        sink=writer or self.archive
        if session.get('collection_policy')=='EXCLUDED_INTERNAL_RUNTIME':
            return self.exclude_internal_session(session,sink)
        sid = session['session_id']; source = Path(session['source_path'])
        previous = self.state.get(sid)
        review_path = self.root / 'collector/reviews' / (sid + '.json')
        reviewed = {}
        if review_path.exists():
            with regular_file(review_path) as stream: reviewed = strict_json(stream.read())
        if not isinstance(reviewed,dict) or any(not re.fullmatch(r'[1-9][0-9]*',k) or not isinstance(v,str)
                                               or not re.fullmatch(r'[a-f0-9]{64}',v) for k,v in reviewed.items()):
            raise ValueError('review manifest must map positive source lines to exact SHA256 hashes')
        review_hash = digest(canonical(reviewed))
        identity = redact_value({k:v for k,v in session.items() if k != 'source_path'})
        identity_hash = digest(canonical(identity))
        with rollout_file(source) as stream:
            storage = stream.storage_signature()
            source_basename = stream.logical_name
            if (previous and not reconcile and previous.get('signature') in self.compatible_signatures
                    and previous.get('review_hash') == review_hash
                    and previous.get('identity_hash') == identity_hash
                    and previous.get('source_storage') == storage):
                return {'session_id':sid, 'status':'CAUGHT_UP', 'changed':False,
                        'coverage': previous['coverage'], 'last_committed_at': previous['committed_at'],
                        'text_coverage':cursor_text_status(previous), 'tools_coverage':cursor_tools_status(previous),
                        'counts': previous['counts'], 'source_line': previous['lines'],
                        'pending_tool_records': previous['pending_tools'], 'gaps': previous['gaps']}
            st = stream.logical_stat(); first = stream.readline(1024 * 1024)
            header = strict_json(first)
            if header.get('type') != 'session_meta' or header.get('payload', {}).get('id') != sid:
                raise ValueError('native session identity mismatch')
            if Path(header['payload']['cwd']).absolute() != Path(session['source_cwd']).absolute():
                raise ValueError('native session cwd mismatch')
            if previous and st.st_size < previous['offset']:
                raise ValueError('source truncated before committed cursor')
            # Verify committed bytes before trusting a cursor, including replacement at same path.
            hasher = hashlib.sha256(); stream.seek(0)
            if previous:
                remaining = previous['offset']
                while remaining:
                    chunk = stream.read(min(1024 * 1024, remaining))
                    if not chunk: raise ValueError('source shortened during prefix check')
                    hasher.update(chunk); remaining -= len(chunk)
                if hasher.hexdigest() != previous['prefix_sha256']:
                    raise ValueError('committed source prefix changed')
            reset = (not previous or reconcile or previous.get('signature') not in self.compatible_signatures
                     or previous.get('review_hash') != review_hash)
            if reset:
                stream.seek(0); hasher = hashlib.sha256()
                cursor = {'offset':0, 'lines':0, 'turn_id':None,
                          'model':{'status':'unknown','reason':'no observed configuration'},
                          'counts':{}, 'pending_tools':0, 'gaps':[], 'exclusions':{}, 'blocked_calls':[]}
            else: cursor = copy.deepcopy(previous)
            cursor['gaps'] = [g for g in cursor['gaps'] if g['reason'] != 'partial_live_tail']
            requests = []; added = {}; new_raw = {}
            def emit(kind, payload, key, parents=(), timestamp=None, model=None, **extra):
                if key in self.index: return self.index[key]['id']
                if key in added: return added[key]
                event_id = 'collector-' + digest(key.encode())[:32]
                event = {'id':event_id,'kind':kind, 'actor':{'id':'local-collector','role':'tool'},
                         'session_id':sid, 'run_id':'collector:' + sid,
                         'operation_id':'collector:' + sid,'attempt_id':'collector-v1',
                         'parents':list(parents),'payload':payload, **extra}
                if timestamp: event['timestamp'] = timestamp
                if model: event['model'] = model
                requests.append((event,key)); added[key] = event_id
                return event_id
            identity_id = emit('capture.session_identified', identity,
                               'collector-identity:' + sid + ':' + identity_hash)
            version_key='collector-version:'+self.signature
            version_outputs=[]
            if version_key not in self.index:
                version_outputs=[sink.put(data) for data in self.version_files.values()]
            version_id=emit('collector.version',{'signature':self.signature,
                'files':{name:digest(data) for name,data in self.version_files.items()}},version_key,
                outputs=version_outputs)
            coverage_parents = [identity_id,version_id]
            if reviewed:
                coverage_parents.append(emit('collector.tool_review_manifest',{'reviewed_source_lines':reviewed},
                                        'collector-reviews:'+sid+':'+review_hash,parents=[identity_id]))
            if sid in self.coverage_ids: coverage_parents.append(self.coverage_ids[sid])
            while stream.tell() < st.st_size:
                position = stream.tell()
                raw = stream.readline(min(16 * 1024 * 1024, st.st_size - position))
                if not raw.endswith(b'\n'):
                    if len(raw) >= 16 * 1024 * 1024:
                        # Hash/drain a large record without retaining it; preserve later text.
                        oversized_hasher=hasher.copy(); oversized_hasher.update(raw)
                        while stream.tell()<st.st_size and not raw.endswith(b'\n'):
                            raw=stream.readline(min(1024*1024,st.st_size-stream.tell())); oversized_hasher.update(raw)
                        if raw.endswith(b'\n'):
                            cursor['lines']+=1; cursor['offset']=stream.tell(); hasher=oversized_hasher
                            cursor['gaps'].append({'source_line':cursor['lines'],'reason':'oversized_record_not_retained'})
                            continue
                    cursor['gaps'].append({'source_line':cursor['lines']+1,'reason':'partial_live_tail'})
                    break
                line = cursor['lines'] + 1
                try: record = strict_json(raw)
                except (ValueError,UnicodeError):
                    cursor['gaps'].append({'source_line':line,'reason':'malformed_complete_json_record','sha256':digest(raw)})
                    hasher.update(raw); cursor['offset']=stream.tell(); cursor['lines']=line
                    continue
                projected = project_record(record,line,sid,cursor['turn_id'],cursor['model'])
                projected = redact_value(projected)
                kind = projected['kind']; payload = projected['payload']
                key = 'collector-' + kind + ':' + sid + ':' + str(line)+':'+self.signature
                timestamp = record.get('timestamp')
                if kind == 'text':
                    if contains_credential(record):
                        payload=dict(payload)
                        payload.pop('text_blocks',None); payload['retain_original']=False
                        payload['attachment_gaps']=payload.get('attachment_gaps',[])+['credential_excluded; original not retained']
                    raw_id = None
                    if payload.get('retain_original', False):
                        old = self.raw.get((sid,line)); raw_hash = digest(raw)
                        if old and old['payload']['raw_sha256'] != raw_hash:
                            raise ValueError('conflicting previously archived native bytes')
                        if old: raw_id = old['id']
                        else:
                            sha = sink.put(raw)
                            item = record['payload']; raw_key = f'codex-visible-v1:{sid}:{line}'
                            raw_id = emit('capture.raw_record',
                                {'format':'codex-visible-selection.v1','source_basename':source_basename,
                                 'source_line':line,'raw_sha256':sha,'source_type':item['type'],
                                 'call_id':item.get('call_id'),'source_timestamp':timestamp,
                                 'source_timestamp_provenance':'local-native-record; clock not independently attested',
                                 'cwd_binding_verified':True}, raw_key, timestamp=timestamp,
                                model=payload.get('observed_model',cursor['model']),
                                actor={'id':'codex:' + item['role'],'role':item['role']},
                                run_id=self.runs.get(sid,'codex:' + sid),
                                operation_id=f'codex-source-line:{sid}:{line}',attempt_id='capture-v1',outputs=[sha])
                    projected_payload = dict(payload)
                    projected_payload['raw_event_id'] = raw_id
                    # Text is retained here only if mixed attachment source cannot be preserved safely.
                    if raw_id: projected_payload.pop('text',None)
                    if raw_id: projected_payload.pop('text_blocks',None)
                    coverage_parents.append(emit('collector.message',projected_payload,key,
                                                 parents=[raw_id] if raw_id else [identity_id],timestamp=timestamp))
                    count = 'user_prompts' if payload['role']=='user' else (
                        'assistant_final' if payload.get('phase') in ['final','final_answer'] else 'assistant_commentary')
                    cursor['counts'][count] = cursor['counts'].get(count,0)+1
                    for gap in payload.get('attachment_gaps',[]):
                        cursor['gaps'].append({'source_line':line,'reason':str(gap)})
                elif kind in ('lifecycle','model','agent_metadata'):
                    coverage_parents.append(emit('collector.'+kind,payload,key,parents=[identity_id],timestamp=timestamp))
                elif kind == 'tool_pending':
                    heartbeat = automation_heartbeat(record['payload'])
                    if heartbeat:
                        cursor['counts']['automation_triggers'] = cursor['counts'].get('automation_triggers', 0)+1
                    # No tool body enters the archive until exact-hash explicit review.
                    if (reviewed.get(str(line)) == digest(raw)
                            and not contains_credential(record)
                            and classify(record,line,{line},set(cursor.get('blocked_calls',[]))) is None):
                        item=record['payload']; old=self.raw.get((sid,line)); sha=sink.put(raw)
                        if old and old['payload']['raw_sha256']!=sha: raise ValueError('reviewed tool bytes conflict')
                        raw_id=old['id'] if old else emit('capture.raw_record',
                            {'format':'codex-visible-selection.v1','source_basename':source_basename,
                             'source_line':line,'raw_sha256':sha,'source_type':item['type'],
                             'call_id':item.get('call_id'),'source_timestamp':timestamp,
                             'source_timestamp_provenance':'local-native-record; clock not independently attested',
                             'cwd_binding_verified':True, **(heartbeat or {})},f'codex-visible-v1:{sid}:{line}',timestamp=timestamp,
                            model=cursor['model'], actor={'id':'codex:tool' if item['type'] in OUTPUT_TYPES else 'codex:assistant',
                                                       'role':'tool' if item['type'] in OUTPUT_TYPES else 'assistant'},
                            run_id=self.runs.get(sid,'codex:'+sid),operation_id=f'codex-source-line:{sid}:{line}',
                            attempt_id='capture-v1',outputs=[sha])
                        coverage_parents.append(emit('collector.tool_reviewed',{'source_line':line,'raw_event_id':raw_id,
                                                     'turn_id':payload.get('turn_id'),
                                                     **(heartbeat or {})},
                                                     key+':reviewed',parents=[raw_id],timestamp=timestamp))
                    else:
                        cursor['pending_tools'] += 1
                        coverage_parents.append(emit('collector.tool_pending',{**payload,'raw_sha256':digest(raw)},key,
                                                     parents=[identity_id],timestamp=timestamp))
                elif kind == 'gap':
                    cursor['gaps'].append({'source_line':line,'reason':payload.get('reason','unknown_schema'),
                                           'surface':payload.get('surface','text_or_unknown')})
                else:
                    reason=payload.get('reason','excluded')
                    native=record.get('payload',{})
                    if reason in ('excluded:sensitive_tool_body','excluded:blocked_tool_call'):
                        cursor['pending_tools']+=1
                        if native.get('type') in CALL_TYPES and native.get('call_id') not in cursor.setdefault('blocked_calls',[]):
                            cursor['blocked_calls'].append(native['call_id'])
                        coverage_parents.append(emit('collector.tool_pending',{
                            'source_line':line,'turn_id':cursor['turn_id'],'record_type':native.get('type'),
                            'call_id':native.get('call_id'),'raw_sha256':digest(raw),'review_status':'BLOCKED',
                            'reason':reason},key,parents=[identity_id],timestamp=timestamp))
                    cursor['exclusions'][reason]=cursor['exclusions'].get(reason,0)+1
                cursor['turn_id']=projected.get('next_turn'); cursor['model']=projected.get('next_model')
                hasher.update(raw); cursor['offset']=stream.tell(); cursor['lines']=line
            endstat=stream.logical_stat()
            if endstat.st_size < st.st_size: raise ValueError('source truncated during collection')
            if endstat.st_mtime_ns!=st.st_mtime_ns:
                stream.seek(0); verify_hash=hashlib.sha256(); remaining=cursor['offset']
                while remaining:
                    chunk=stream.read(min(1024*1024,remaining))
                    if not chunk: raise ValueError('source shortened while verifying snapshot')
                    verify_hash.update(chunk); remaining-=len(chunk)
                if verify_hash.hexdigest()!=hasher.hexdigest(): raise ValueError('source mutated during collection')
        cursor.update(prefix_sha256=hasher.hexdigest(), observed_size=st.st_size,mtime_ns=st.st_mtime_ns,
                      inode=st.st_ino,device=st.st_dev,source_storage=storage,
                      signature=self.signature,review_hash=review_hash,
                      identity_hash=identity_hash, committed_at=now(),
                      coverage='GAPS' if cursor['gaps'] else 'TEXT_COMPLETE_THROUGH_CURSOR')
        # A frozen content boundary identifies the attempt independently of wall clock retries.
        coverage_key='collector-coverage:'+sid+':'+digest(canonical({
            'offset':cursor['offset'],'prefix':cursor['prefix_sha256'],'signature':self.signature,
            'review':review_hash,'identity':identity_hash,'size':st.st_size,'mtime':st.st_mtime_ns,
            'source_storage':storage}))
        if coverage_key not in self.index:
            emit('collector.coverage',{'cursor':cursor,'source_basename':source_basename,
                 'text_status':cursor_text_status(cursor),'tools_status':cursor_tools_status(cursor),
                 'whole_trace':'INCOMPLETE','boundary':'Known internal exclusions are intentional; live tail and unsupported surfaces explicit.'},
                 coverage_key,parents=list(dict.fromkeys(coverage_parents)))
        committed=sink.append_many(requests) if requests else []
        for event in committed:
            self.index[event['delivery_key']]=event
            if event['kind']=='capture.raw_record': self.raw[(sid,event['payload']['source_line'])]=event
        existing_ids={e['id'] for e in self.events}
        self.events.extend(e for e in committed if e['id'] not in existing_ids)
        # Cursor is advanced only after durable archive commit. Runtime state is a cache.
        if coverage_key in self.index: cursor=self.index[coverage_key]['payload']['cursor']
        self.state[sid]=cursor
        self.coverage_ids[sid]=self.index[coverage_key]['id']
        atomic_json(self.runtime / 'cursor-cache.json',self.state)
        self.event_dir_mtime=(self.archive.root/'events').stat().st_mtime_ns
        return {'session_id':sid,'status':'CAUGHT_UP','changed':bool(committed),
                'coverage':cursor['coverage'],'last_committed_at':cursor['committed_at'],
                'text_coverage':cursor_text_status(cursor), 'tools_coverage':cursor_tools_status(cursor),
                'counts':cursor['counts'],'source_line':cursor['lines'],
                'pending_tool_records':cursor['pending_tools'],'gaps':cursor['gaps']}

    def exclude_internal_session(self,session,sink):
        """Metadata-only correction/exclusion; never open internal runtime bodies."""
        sid=session['session_id']; identity=redact_value({k:v for k,v in session.items() if k!='source_path'})
        identity_key='collector-identity:'+sid+':'+digest(canonical(identity))
        exclusion_key='collector-internal-exclusion:'+sid+':'+digest(canonical(identity))
        requests=[]
        def emit(kind,payload,key,parents=()):
            eid='collector-'+digest(key.encode())[:32]
            if key not in self.index:
                requests.append(({'id':eid,'kind':kind,'actor':{'id':'local-collector','role':'tool'},
                    'session_id':sid,'run_id':'collector:'+sid,'operation_id':'collector:'+sid,
                    'attempt_id':'internal-exclusion-v1','parents':list(parents),'payload':payload},key))
            return eid
        identity_id=emit('capture.session_identified',identity,identity_key)
        previous=[e for e in self.events if e['session_id']==sid and e['kind']=='capture.raw_record']
        emit('collector.session_excluded',{'reason':'Native subagent.other is internal runtime, not an authorized chat.',
            'collection_policy':'EXCLUDED_INTERNAL_RUNTIME','prior_raw_records_count':len(previous),
            'correction':'Earlier observations retained append-only; exclude this session from chat totals, readable transcript bodies and research/publication lineage.'},
            exclusion_key,[identity_id]+[e['id'] for e in previous])
        committed=sink.append_many(requests) if requests else []
        self.events.extend(committed)
        for e in committed:self.index[e['delivery_key']]=e
        self.event_dir_mtime=(self.archive.root/'events').stat().st_mtime_ns
        return {'session_id':sid,'status':'EXCLUDED','changed':bool(committed),
                'coverage':'EXCLUDED_INTERNAL_RUNTIME','counts':{},'pending_tool_records':0,'gaps':[]}


def status(root):
    path=Path(root)/'collector/runtime/status.json'
    with regular_file(path) as stream: report=strict_json(stream.read())
    age=(dt.datetime.now(dt.timezone.utc)-dt.datetime.fromisoformat(report['checked_at'])).total_seconds()
    report['age_seconds']=round(age,2)
    report['fresh']=age<=max(60,report.get('next_poll_delay_seconds',report.get('interval_seconds',10))*2+report.get('elapsed_seconds',0))
    if not report['fresh']: report['status']='STALE'
    return add_coverage_status(report)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument('command',choices=['collect-once','reconcile','verify','status','watch'])
    args=parser.parse_args(); os.umask(0o077)
    if args.command=='status':
        report=status(args.root); print(json.dumps(report,ensure_ascii=False,indent=2))
        return 0 if report['status']=='RUNNING' and report.get('coverage_healthy',False) else 1
    collector=Collector(args.root)
    if args.command=='verify':
        report=collector.archive.validate(); print(json.dumps(report,ensure_ascii=False,indent=2)); return 0 if report['ok'] else 1
    if args.command!='watch':
        report=collector.collect(reconcile=args.command=='reconcile')
        print(json.dumps(report,ensure_ascii=False,indent=2)); return 1 if report['status']=='ERROR' else 0
    def stop(signum,frame):
        global STOP
        STOP=True
    signal.signal(signal.SIGTERM,stop); signal.signal(signal.SIGINT,stop)
    last_error=None
    delay=collector.interval
    while not STOP:
        try:
            result=collector.collect()
            delay=result['next_poll_delay_seconds']
            error=canonical([(s['session_id'],s.get('error_type'),s.get('error')) for s in result['sessions'] if s['status']=='ERROR']) if result['status']=='ERROR' else None
        except Exception as exc:
            error=(type(exc).__name__+': '+str(exc)[:500]).encode()
            delay=min(collector.interval, 30)
            try: atomic_json(collector.runtime/'status.json',{'status':'ERROR','checked_at':now(),
                             'interval_seconds':collector.interval,'error':error.decode(),'pid':os.getpid()})
            except OSError: pass
        if error and error!=last_error: log_error(collector.root,error.decode())
        last_error=error
        until=time.monotonic()+delay
        while not STOP and time.monotonic()<until: time.sleep(min(0.25,max(0,until-time.monotonic())))
    return 0


if __name__=='__main__':
    try: sys.exit(main())
    except Exception as exc:
        error=type(exc).__name__+': '+str(exc)[:500]
        if 'watch' in sys.argv:
            try: log_error(Path(__file__).resolve().parents[1],error)
            except OSError: pass
        else: print(error,file=sys.stderr)
        sys.exit(1)
