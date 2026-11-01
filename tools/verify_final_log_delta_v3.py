#!/usr/bin/env python3
"""Read-only repository check of a separately hash-pinned final visible delta.

Uses no native source, database, canonical archive, Git, network or model.
The frozen predecessor verifier runs with only its two indices overlaid by
temporary baseline copies; all its other checks use the retained repository.
"""
from pathlib import Path
import argparse, collections, copy, hashlib, importlib.util, json, re, sys, tarfile, tempfile
sys.dont_write_bytecode = True
PREDECESSOR_SHA = '285f99a0d246722fe487edda0d14da57b1f2609cdc0b9d28b725a7e635191b0b'
BASE_INDEX_SHA = '020ee8a044027f5a2e5e1e111684c5a0f1725ea63d9c686fdb99afdeaae1e5e9'
BASE_BUNDLES_SHA = '53049591132ff4f75b2afbcc5c2533dae4fe6e79f337fa7423d6859f89a111e7'
RUN = 'deep-verification-20261031'
V10_EXACT_RULE = {'path': f'runs/{RUN}/archive-repair-v10-exact-url/EXACT_URL_RULE.json',
                  'sha256': 'c5b556be20d8d0580df67954a97b99ca756b23d7b4cec6b6b6de054275b4e780',
                  'bytes': 1290}
HEX = re.compile(r'[0-9a-f]{64}\Z')
EXPECTED_JOBS = {f'V{i:02d}-{role}' for i in range(1, 11) for role in ('A', 'L')}
ADMINISTRATIVE_PATHS = {f'runs/{RUN}/' + name for name in
                        ('WORD_COUNT_PREFLIGHT.json', 'DEADLINE_TIMEZONE_CHECK.json',
                         'coordinator-reading/READING_REGISTER.json')}


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def regular(root, name):
    path = Path(name)
    require(isinstance(name, str) and name and str(path) == name and not path.is_absolute()
            and not {'..', '.git'} & set(path.parts) and '\\' not in name and '\0' not in name,
            'Unsafe repository path')
    path = root / path
    require(path.is_file() and not any(p.is_symlink() for p in (path, *path.parents)),
            'Missing or symlink source: ' + name)
    return path


def predecessor(root):
    path = regular(root, 'tools/verify_recovered_logs.py')
    require(sha(path.read_bytes()) == PREDECESSOR_SHA, 'Frozen predecessor verifier changed')
    spec = importlib.util.spec_from_file_location('frozen_recovery_verifier', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def index_by(rows, key, label):
    result = {}
    for row in rows:
        value = row[key]
        require(value not in result, 'Duplicate ' + label)
        result[value] = row
    return result


def descriptor(row):
    require(isinstance(row, dict) and {'path', 'sha256', 'bytes'} <= set(row)
            and isinstance(row['path'], str) and isinstance(row['sha256'], str)
            and HEX.fullmatch(row['sha256']) and type(row['bytes']) is int and row['bytes'] >= 0,
            'Invalid exact descriptor')
    return {k: row[k] for k in ('path', 'sha256', 'bytes')}


def event_check(base, event):
    require(isinstance(event, dict) and event.get('schema_version') == 1
            and type(event.get('sequence')) is int and event['sequence'] > 0
            and isinstance(event.get('id'), str) and isinstance(event.get('payload'), dict)
            and isinstance(event.get('parents'), list) and len(set(event['parents'])) == len(event['parents'])
            and isinstance(event.get('outputs'), list) and isinstance(event.get('inputs'), list),
            'Invalid exported canonical event')
    unsigned = dict(event)
    digest = unsigned.pop('sha256', None)
    require(digest == sha((base.canonical(unsigned) + '\n').encode()), 'Canonical event self-hash mismatch')
    return event


def union_check(base, olddocs, currentdocs, additions, inherited, cutoffs):
    """Type-sensitive preservation plus exact new visible-source identities."""
    require(set(olddocs) <= set(currentdocs), 'Historical session disappeared')
    added = {}; old_count = 0; inherited_seen = set()
    baseline_texts = {sha(m['text'].encode()) for d in olddocs.values() for m in d['messages']}
    inherited_map = index_by(inherited, 'identity', 'inherited identity')
    for sid, doc in currentdocs.items():
        rows = doc['messages']; lookup = {base.key(m): m for m in rows}
        require(len(lookup) == len(rows) and len({(m['source_line'], m['role']) for m in rows}) == len(rows),
                'Duplicate or conflicting visible source identity')
        prior = {base.key(m): m for m in olddocs.get(sid, {}).get('messages', [])}
        for key, message in prior.items():
            require(key in lookup and base.canonical(lookup[key]) == base.canonical(message),
                    'Historical typed message object changed: ' + sid)
            old_count += 1
        for key in set(lookup) - set(prior):
            message = lookup[key]; identity = (sid, *key)
            require(sid in cutoffs and message['source_line'] <= cutoffs[sid]['source_line_cutoff'],
                    'New message outside bound native prefix')
            if message.get('inherited_copy') is True:
                proof = inherited_map.get(identity)
                require(proof is not None and message.get('origin') == 'INHERITED_VISIBLE_COPY'
                        and proof['source_line_sha256'] == message.get('source_line_sha256')
                        and proof['text_sha256'] in baseline_texts
                        and message.get('transformation') == ['omit_bound_inherited_user_message_flag',
                                                              'visible_text_and_allowlisted_metadata_only'],
                        'Unbound or mislabelled inherited copy')
                normalized = copy.deepcopy(message); normalized.pop('inherited_copy')
                normalized['origin'] = 'USER_ROLE_INPUT' if message['role'] == 'user' else 'AI_VISIBLE_RESPONSE'
                normalized['transformation'] = ['visible_text_and_allowlisted_metadata_only']
                base.new_message(normalized, sid, {})
                inherited_seen.add(identity)
            else:
                base.new_message(message, sid, {})
            row = {k: message[k] for k in ('session_id', 'source_line', 'role', 'text_sha256',
                                          'source_line_sha256', 'origin', 'inherited_copy') if k in message}
            require(identity not in added, 'Duplicate addition')
            added[identity] = row
    expected = {}
    for row in additions:
        identity = (row['session_id'], row['source_line'], row['role'], row['text_sha256'])
        require(identity not in expected, 'Duplicate addition descriptor'); expected[identity] = row
    require(base.canonical(sorted(added.items())) == base.canonical(sorted(expected.items())),
            'Declared additions differ from exact message union')
    require(inherited_seen == set(inherited_map), 'Inherited proof is not exhausted exactly')
    return old_count, len(added), len(inherited_seen)


class Verifier:
    def __init__(self, root, manifest_path, manifest_sha256):
        self.root = Path(root).absolute(); self.base = predecessor(self.root)
        require(isinstance(manifest_sha256, str) and HEX.fullmatch(manifest_sha256), 'Caller must pin manifest SHA-256')
        raw = regular(self.root, manifest_path).read_bytes()
        require(sha(raw) == manifest_sha256, 'Final delta manifest changed')
        self.manifest = self.base.strict_json(raw); self.manifest_path = manifest_path
        self.reader = self.base.Verifier(self.root); self.artifacts = {}; self.events = {}

    def bound(self, row):
        row = descriptor(row)
        return self.reader.read(row['path'], row)

    def source(self, row):
        require(row['path'] in self.artifacts, 'Source artifact absent from exact bundle: ' + row['path'])
        raw = self.artifacts[row['path']]
        require(sha(raw) == row['sha256'] and ('bytes' not in row or len(raw) == row['bytes']),
                'Source artifact differs from accepted descriptor')
        return raw

    def administrative_check(self):
        rows = self.manifest.get('administrative_artifacts', [])
        entries = index_by(rows, 'path', 'administrative evidence')
        canonical_paths = {r['path'] for r in self.manifest['safe_artifacts']}
        require(set(entries) <= ADMINISTRATIVE_PATHS and not set(entries) & canonical_paths,
                'Administrative evidence scope or canonical attribution overlap')
        for row in rows:
            require(set(row) == {'path', 'sha256', 'bytes'}, 'Administrative evidence cannot claim canonical attribution')
            descriptor(row)
            self.base.private_check(self.base.strict_json(self.source(row)), row['path'], hidden=True)
        return len(rows)

    def projection_check(self, jid, event, terminal):
        """Check a canonical safe projection without recovering withheld URLs."""
        b = self.base; public = terminal.get('archive_projection')
        if isinstance(public, dict) and public.get('schema') == 'archive-native-output-projection.v3':
            return self.exact_native_projection_check(jid, event, terminal)
        if isinstance(public, dict) and public.get('schema') == 'archive-native-output-projection.v2':
            return self.native_projection_check(jid, event, terminal)
        if public is None:
            require('archive_projection' not in event['payload'], 'Projection sidecar absent from terminal')
            return None
        require(public.get('schema') == 'archive-safe-output-projection.v1'
                and public.get('scientific_response_unchanged') is True
                and public.get('evidence') == event['payload'].get('archive_projection'), 'Projection terminal/event binding differs')
        sidecar = b.strict_json(self.source(public['evidence']))
        policy_id = 'SIGNED_S3_PUBLIC_RESPONSE_URL_OMISSION_V1'
        require(sidecar.get('schema') == public['schema'] and sidecar.get('policy_id') == policy_id
                and sidecar.get('job_id') == jid and jid.endswith('-L') and sidecar.get('session_id') == event['session_id']
                and sidecar.get('scientific_response_unchanged') is True and sidecar.get('originals_written') is False
                and sidecar.get('policy_event_id') == public.get('policy_event_id')
                and sidecar.get('policy_manifest_sha256') == public.get('manifest_sha256')
                and sidecar.get('original_terminal_receipt') == public.get('original_terminal_receipt')
                and sidecar.get('withheld_originals') == public.get('withheld_originals'), 'Projection identity/policy differs')
        policy = self.events.get(sidecar['policy_event_id'])
        require(policy is not None and policy['kind'] == 'research.verification.web_projection_policy.accepted'
                and policy['run_id'] == RUN and policy['id'] in event['parents']
                and policy['payload'].get('status') == 'DEEP_VERIFICATION_SAFE_WEB_PROJECTION_ARCHIVED'
                and sidecar['policy_manifest_sha256'] in policy['outputs'], 'Projection policy not canonically bound')
        original_ref = sidecar['original_terminal_receipt']; original = b.strict_json(self.source(original_ref))
        require(b.canonical({k:v for k,v in terminal.items() if k not in {'outputs','archive_projection'}}) ==
                b.canonical({k:v for k,v in original.items() if k != 'outputs'}), 'Projection changed original scientific terminal metadata')
        olddir = str(Path(original_ref['path']).parent)
        withheld = index_by(sidecar['withheld_originals'], 'path', 'withheld original')
        require(set(withheld) == {olddir + '/native-check.json', olddir + '/native-visible.json'}, 'Unexpected withheld original scope')
        for name, ref in withheld.items():
            descriptor(ref)
            require(ref['sha256'] == original['outputs'].get(name) and name not in self.artifacts,
                    'Unsafe original changed or exported')
        public_files = index_by(sidecar['public_files'], 'path', 'public projection file')
        newdir = str(Path(event['payload']['receipt']['path']).parent)
        require(newdir.endswith('/archive-projection-v1')
                and set(public_files) == {newdir + '/native-check.json', newdir + '/native-visible.json'}
                and event['payload']['native_check'] == public_files[newdir + '/native-check.json'], 'Wrong public projection files')
        expected = {name:digest for name,digest in original['outputs'].items() if name not in withheld}
        for ref in list(public_files.values()) + [public['evidence'], original_ref]:
            self.source(ref); expected[ref['path']] = ref['sha256']
        require(b.canonical(terminal['outputs']) == b.canonical(expected), 'Projection changed/dropped other original outputs')
        for name in (olddir + '/response.json', olddir + '/final.txt'):
            require(name in original['outputs'] and terminal['outputs'].get(name) == original['outputs'][name],
                    'Projection changed scientific response/final binding')
        proof = b.strict_json(self.source(public_files[newdir + '/native-check.json']))
        visible = b.strict_json(self.source(public_files[newdir + '/native-visible.json']))
        require(proof.get('native_source_prefix') == sidecar.get('native_source_prefix')
                and proof.get('session_id') == visible.get('session_id') == event['session_id'], 'Projection native-prefix/session commitment differs')
        key = lambda r:(r['line'], r['record_sha256'], r['call_id'])
        left = {key(r):r for r in proof['public_web_calls'] if r.get('type') == 'public_web_output'}
        right = {key(r):r for r in visible['records'] if r.get('type') == 'public_web_output'}
        require(b.canonical(sorted(left.items())) == b.canonical(sorted(right.items())), 'Public proof/visible projection copies differ')
        ledger = sidecar['ledger']; changed = {}
        require(ledger.get('schema') == 'safe-web-url-projection.v1' and ledger.get('policy_id') == policy_id
                and ledger.get('session_id') == event['session_id'], 'Projection ledger identity differs')
        for row in ledger['records']:
            identity = (row['source_line'], row['source_record_sha256'], row['call_id'])
            require(identity in left and row['source_line'] not in changed and row.get('projection_copies') == 2,
                    'Unbound/duplicate projected output')
            text = left[identity]['text'].encode(); omissions = row['omissions']
            require(sha(text) == row['projected_text_sha256'] and len(text) == row['projected_text_bytes']
                    and HEX.fullmatch(row['source_text_sha256']) and type(row['source_text_bytes']) is int
                    and 0 < row['source_text_bytes'] <= 2 * 1024 * 1024
                    and row['omission_count'] == len(omissions) and 1 <= len(omissions) <= 64, 'Projected text/ledger hash or bound differs')
            shift = 0; previous_end = 0
            for omission in omissions:
                offset, length = omission['source_utf8_start'], omission['url_bytes']
                digest = omission['url_sha256']
                require(type(offset) is int and offset >= previous_end and type(length) is int and 1 <= length <= 16384
                        and offset + length <= row['source_text_bytes'] and HEX.fullmatch(digest)
                        and omission.get('reason') == 'SIGNED_PUBLIC_URL_QUERY_CREDENTIALS', 'Invalid URL omission commitment')
                marker = '[SIGNED PUBLIC URL EXCLUDED; sha256=' + digest + '; bytes=' + str(length) + ']'
                require(omission['replacement'] == marker and text[offset + shift:offset + shift + len(marker.encode())] == marker.encode(), 'URL omission marker/position differs')
                shift += len(marker.encode()) - length; previous_end = offset + length
            require(row['source_text_bytes'] + shift == len(text), 'Projection byte conservation differs')
            changed[row['source_line']] = row
        require(ledger.get('source_output_records') == len(changed) > 0
                and ledger.get('omitted_url_count') == sum(r['omission_count'] for r in changed.values()), 'Projection omission totals differ')
        return {'evidence':public['evidence'], 'changed':changed, 'policy_event_id':policy['id']}

    def native_projection_check(self, jid, event, terminal):
        """Verify an explicit native-first projection; never invent old proof files."""
        b = self.base; public = terminal['archive_projection']; evidence = public['evidence']
        side = b.strict_json(self.source(evidence)); sid = event['session_id']
        require(public.get('schema') == side.get('schema') == 'archive-native-output-projection.v2'
                and event['payload'].get('archive_projection') == evidence
                and side.get('policy_id') == 'SIGNED_S3_PUBLIC_RESPONSE_URL_OMISSION_V2'
                and side.get('job_id') == jid and side.get('session_id') == sid
                and side.get('policy_event_id') == public.get('policy_event_id')
                and side.get('policy_manifest_sha256') == public.get('manifest_sha256')
                and public.get('scientific_text_unchanged') is True
                and side.get('scientific_text_unchanged') is True
                and side.get('unsafe_intermediate_files_written') is False
                and 'withheld_originals' not in side and 'original_terminal_receipt' not in side,
                'Native projection identity/boundary differs')
        policy = self.events.get(side['policy_event_id'])
        require(policy is not None and policy['kind'] == 'research.verification.native_projection_policy.accepted'
                and policy['run_id'] == RUN and policy['id'] in event['parents']
                and policy['payload'].get('status') == 'DEEP_VERIFICATION_SAFE_NATIVE_PROJECTION_ARCHIVED'
                and policy['payload'].get('manifest_sha256') == side['policy_manifest_sha256']
                and side['policy_manifest_sha256'] in policy['outputs'], 'Native projection policy not canonically bound')
        original_ref = side['original_attempt_receipt']; original = b.strict_json(self.source(original_ref))
        olddir = f'runs/{RUN}/results/{jid}/attempt-001'
        original_files = index_by(side['original_files'], 'path', 'preserved attempt file')
        require(original_ref['path'] in original_files and original_files[original_ref['path']] == original_ref
                and all(str(Path(name).parent) == olddir for name in original_files), 'Preserved attempt scope differs')
        for ref in original_files.values(): self.source(ref)
        fixed = ('job_id','session_id','transport_version','requested_model','requested_effort','requested_service_tier',
                 'prompt_sha256','schema_sha256','argv_sha256','argv','started_at')
        require(all(k in original and b.canonical(terminal.get(k)) == b.canonical(original[k]) for k in fixed)
                and original['job_id'] == jid and original['session_id'] == sid and original['transport_version'] == 4
                and side.get('original_receipt_status') == original.get('status'), 'Native projection changed attempt/configuration metadata')
        mode = side.get('mode')
        if mode == 'MECHANICAL_REVALIDATION_FROM_FAILED_ATTEMPT':
            require(jid == 'V05-L' and original_ref['path'] == olddir + '/failure.json'
                    and original['status'] == 'FAILED_PRESERVED_NO_RETRY'
                    and isinstance(original.get('ended_at'), str) and bool(original['ended_at'])
                    and terminal.get('ended_at') == original['ended_at']
                    and original.get('error') == 'Credential-shaped public text excluded'
                    and original.get('automatic_retry') is False
                    and original.get('process_state') == {'process_stopped':True,'stderr_drained':True,'exit_code':0,'forced_kill':False}
                    and side.get('original_proof_files_existed') is False
                    and terminal.get('disposition') == 'MECHANICAL_REVALIDATION_NO_MODEL_RERUN'
                    and type(terminal.get('additional_model_calls')) is int and terminal['additional_model_calls'] == 0,
                    'Failed attempt mechanical revalidation is not exact')
            require(set(original_files) == {olddir + '/' + name for name in
                    ('failure.json','final.txt','launch.json','stderr.json','visible-events.jsonl','structural-diagnostics.jsonl')},
                    'Mechanical original six-file inventory differs')
            require(not any(name in original_files or name in self.artifacts for name in
                            (olddir + '/receipt.json', olddir + '/native-check.json', olddir + '/native-visible.json', olddir + '/response.json')),
                    'Mechanical revalidation invented original complete proof/response files')
            failures = [self.events[eid] for eid in policy['parents'] if eid in self.events
                        and self.events[eid]['kind'] == 'research.verification.mechanical_failure.preserved'
                        and original_ref['sha256'] in self.events[eid]['outputs']]
            require(len(failures) == 1 and failures[0]['run_id'] == RUN
                    and failures[0]['payload'].get('status') == 'MECHANICAL_FAILURE_PRESERVED_NO_MODEL_RERUN'
                    and original_ref in failures[0]['payload'].get('files', []), 'Original failed attempt lacks accepted preservation')
        else:
            require(mode == 'COMPLETED_NATIVE_PROJECTED_ATTEMPT'
                    and jid in {'V07-L','V08-A','V08-L','V09-A','V09-L','V10-A','V10-L'}
                    and original_ref['path'] == olddir + '/receipt.json'
                    and original['status'] == 'COMPLETE_LOCAL_PENDING_CANONICAL_ARCHIVE'
                    and isinstance(original.get('completed_at'), str) and bool(original['completed_at'])
                    and terminal.get('completed_at') == original['completed_at']
                    and side.get('original_proof_files_existed') is True,
                    'Unapproved future projected attempt')
            require(set(original_files) == set(original['outputs']) | {original_ref['path']}
                    and all(name in original_files and original_files[name]['sha256'] == digest
                            for name,digest in original['outputs'].items()), 'Original completed outputs not preserved')
        final_ref = side['unchanged_scientific_final']
        require(final_ref.get('path') == olddir + '/final.txt' and original_files.get(final_ref['path']) == final_ref,
                'Original scientific final not preserved')
        final_raw = self.source(final_ref)
        newdir = f'runs/{RUN}/results/{jid}/native-projection-v2'
        files = index_by(side['public_files'], 'path', 'native public copy')
        require(set(files) == {newdir + '/' + name for name in ('native-check.json','native-visible.json','response.json')}
                and event['payload']['receipt']['path'] == newdir + '/receipt.json'
                and evidence['path'] == newdir + '/PROJECTION.json'
                and event['payload']['native_check'] == files[newdir + '/native-check.json'], 'Native public copy paths differ')
        expected = {r['path']:r['sha256'] for r in list(original_files.values()) + list(files.values()) + [evidence]}
        require(b.canonical(terminal['outputs']) == b.canonical(expected), 'Native projection output inventory differs')
        proof = b.strict_json(self.source(files[newdir + '/native-check.json']))
        visible = b.strict_json(self.source(files[newdir + '/native-visible.json']))
        response = b.strict_json(self.source(files[newdir + '/response.json']))
        require(proof.get('session_id') == visible.get('session_id') == sid
                and proof.get('native_source_prefix') == side.get('native_source_prefix')
                and proof.get('isolation_failures') == [], 'Native projection source/isolation differs')
        prefix = side['native_source_prefix']
        require(set(prefix) == {'bytes','sha256','records','newline_terminated'} and type(prefix['bytes']) is int
                and 0 < prefix['bytes'] <= 64*1024*1024 and HEX.fullmatch(prefix['sha256'])
                and type(prefix['records']) is int and prefix['records'] > 0 and prefix['newline_terminated'] is True,
                'Invalid native projection prefix')
        finals = [r for r in visible['records'] if r.get('role') == 'assistant' and r.get('phase') in {'final','final_answer'}]
        require(len(finals) == 1 and finals[0]['text'].encode() == final_raw
                and proof.get('final_lines') == [finals[0]['line']]
                and b.canonical(response) == b.canonical(b.strict_json(final_raw)), 'Native scientific final/response changed')
        ledger = side['ledger']; require(b.canonical(ledger) == b.canonical(proof.get('public_web_projection')),
                                       'Native projection ledger differs from proof')
        require(ledger.get('schema') == 'native-public-web-projection.v2'
                and ledger.get('policy_id') == side['policy_id'] and ledger.get('session_id') == sid
                and ledger.get('original_native_record_hashes_retained') is True
                and ledger.get('scientific_text_unchanged') is True and ledger.get('unsafe_intermediate_files_written') is False,
                'Native projection ledger boundary differs')
        key = lambda r:(r['line'],r['record_sha256'],r['call_id'])
        left_rows = [r for r in proof['public_web_calls'] if r.get('type') == 'public_web_output']
        right_rows = [r for r in visible['records'] if r.get('type') == 'public_web_output']
        left = {key(r):r for r in left_rows}; right = {key(r):r for r in right_rows}
        require(len(left) == len(left_rows) and len(right) == len(right_rows)
                and b.canonical(sorted(left.items())) == b.canonical(sorted(right.items())), 'Native public projection copies differ')
        changed = {}
        for row in ledger['records']:
            identity = (row['source_line'],row['source_record_sha256'],row['call_id'])
            require(identity in left and row['source_line'] not in changed and row.get('projection_copies') == 2,
                    'Unbound native projected output')
            text = left[identity]['text'].encode(); omissions = row['omissions']
            require(sha(text) == row['projected_text_sha256'] and len(text) == row['projected_text_bytes']
                    and HEX.fullmatch(row['source_text_sha256']) and type(row['source_text_bytes']) is int
                    and 0 < row['source_text_bytes'] <= 2*1024*1024 and row['omission_count'] == len(omissions)
                    and 1 <= len(omissions) <= 64, 'Native projected text commitment differs')
            shift = 0; previous_end = 0
            for omission in omissions:
                offset,length,digest = omission['source_utf8_start'],omission['url_bytes'],omission['url_sha256']
                require(type(offset) is int and offset >= previous_end and type(length) is int and 1 <= length <= 16384
                        and offset + length <= row['source_text_bytes'] and HEX.fullmatch(digest)
                        and omission.get('reason') == 'SIGNED_PUBLIC_URL_QUERY_CREDENTIALS'
                        and omission.get('variant') in {'SIGV2_REGIONAL_TEMPORARY','SIGV4_PATH_STYLE_PDF'},
                        'Invalid native URL omission commitment')
                marker = '[SIGNED PUBLIC URL EXCLUDED; sha256=' + digest + '; bytes=' + str(length) + ']'
                require(omission['replacement'] == marker and text[offset+shift:offset+shift+len(marker.encode())] == marker.encode(),
                        'Native omission marker/position differs')
                shift += len(marker.encode()) - length; previous_end = offset + length
            require(row['source_text_bytes'] + shift == len(text), 'Native projection byte conservation differs')
            changed[row['source_line']] = row
        require(type(ledger.get('source_output_records')) is int and ledger['source_output_records'] == len(changed)
                and type(ledger.get('omitted_url_count')) is int
                and ledger['omitted_url_count'] == sum(r['omission_count'] for r in changed.values())
                and (not changed or jid.endswith('-L'))
                and (mode != 'MECHANICAL_REVALIDATION_FROM_FAILED_ATTEMPT' or bool(changed)), 'Native projection omission totals/scope differ')
        return {'evidence':evidence,'changed':changed,'policy_event_id':policy['id'],'native_projection_v2':True}

    def exact_native_projection_check(self, jid, event, terminal):
        """Verify only the single completed V10-L exception; no new general policy."""
        b = self.base; public = terminal['archive_projection']; evidence = public['evidence']
        side = b.strict_json(self.source(evidence)); sid = event['session_id']
        require(side.get('exact_rule') == V10_EXACT_RULE, 'Exact V10 rule descriptor changed')
        rule = b.strict_json(self.source(V10_EXACT_RULE))
        require(rule.get('schema') == 'single-public-url-omission-rule.v1'
                and jid == rule['job_id'] == 'V10-L' and sid == rule['session_id']
                and side.get('native_source_prefix') == rule['native_source_prefix'],
                'Exact V10 job/session/source prefix changed')
        require(public.get('schema') == side.get('schema') == 'archive-native-output-projection.v3'
                and event['payload'].get('archive_projection') == evidence
                and side.get('policy_id') == 'SIGNED_S3_V10_EXACT_URL_OMISSION_V3'
                and side.get('job_id') == jid and side.get('session_id') == sid
                and side.get('policy_event_id') == public.get('policy_event_id')
                and side.get('policy_manifest_sha256') == public.get('manifest_sha256')
                and public.get('scientific_text_unchanged') is True
                and side.get('scientific_text_unchanged') is True
                and side.get('unsafe_intermediate_files_written') is False
                and 'withheld_originals' not in side and 'original_terminal_receipt' not in side,
                'Native projection identity/boundary differs')
        policy = self.events.get(side['policy_event_id'])
        require(policy is not None and policy['kind'] == 'research.verification.native_projection_policy.accepted'
                and policy['run_id'] == RUN and policy['id'] in event['parents']
                and policy['payload'].get('status') == 'DEEP_VERIFICATION_SAFE_NATIVE_PROJECTION_ARCHIVED'
                and policy['payload'].get('manifest_sha256') == side['policy_manifest_sha256']
                and side['policy_manifest_sha256'] in policy['outputs'], 'Native projection policy not canonically bound')
        require(policy['payload'].get('exact_rule') == V10_EXACT_RULE
                and V10_EXACT_RULE in policy['payload'].get('files', [])
                and V10_EXACT_RULE['sha256'] in policy['outputs'], 'Exact V10 rule not canonically bound')
        manifests = [ref for ref in policy['payload']['files']
                     if ref.get('sha256') == side['policy_manifest_sha256']]
        require(len(manifests) == 1, 'Exact V10 policy manifest file missing or ambiguous')
        manifest = b.strict_json(self.source(manifests[0]))
        require(manifest.get('exact_rule') == V10_EXACT_RULE
                and V10_EXACT_RULE in manifest.get('files', []), 'Exact V10 rule not bound in policy manifest')
        original_ref = side['original_attempt_receipt']; original = b.strict_json(self.source(original_ref))
        olddir = f'runs/{RUN}/results/{jid}/attempt-001'
        original_files = index_by(side['original_files'], 'path', 'preserved attempt file')
        require(original_ref['path'] in original_files and original_files[original_ref['path']] == original_ref
                and all(str(Path(name).parent) == olddir for name in original_files), 'Preserved attempt scope differs')
        for ref in original_files.values(): self.source(ref)
        fixed = ('job_id','session_id','transport_version','requested_model','requested_effort','requested_service_tier',
                 'prompt_sha256','schema_sha256','argv_sha256','argv','started_at')
        require(all(k in original and b.canonical(terminal.get(k)) == b.canonical(original[k]) for k in fixed)
                and original['job_id'] == jid and original['session_id'] == sid and original['transport_version'] == 4
                and side.get('original_receipt_status') == original.get('status'), 'Native projection changed attempt/configuration metadata')
        mode = side.get('mode')
        if mode == 'MECHANICAL_REVALIDATION_FROM_FAILED_ATTEMPT':
            require(jid == 'V10-L' and original_ref['path'] == olddir + '/failure.json'
                    and original['status'] == 'FAILED_PRESERVED_NO_RETRY'
                    and isinstance(original.get('ended_at'), str) and bool(original['ended_at'])
                    and terminal.get('ended_at') == original['ended_at']
                    and original.get('error') == 'Credential outside approved signed public response URL'
                    and original.get('automatic_retry') is False
                    and original.get('process_state') == {'process_stopped':True,'stderr_drained':True,'exit_code':0,'forced_kill':False}
                    and side.get('original_proof_files_existed') is False
                    and terminal.get('disposition') == 'MECHANICAL_REVALIDATION_NO_MODEL_RERUN'
                    and type(terminal.get('additional_model_calls')) is int and terminal['additional_model_calls'] == 0,
                    'Failed attempt mechanical revalidation is not exact')
            require(set(original_files) == {olddir + '/' + name for name in
                    ('failure.json','final.txt','launch.json','stderr.json','visible-events.jsonl','structural-diagnostics.jsonl')},
                    'Mechanical original six-file inventory differs')
            require(not any(name in original_files or name in self.artifacts for name in
                            (olddir + '/receipt.json', olddir + '/native-check.json', olddir + '/native-visible.json', olddir + '/response.json')),
                    'Mechanical revalidation invented original complete proof/response files')
            failures = [self.events[eid] for eid in policy['parents'] if eid in self.events
                        and self.events[eid]['kind'] == 'research.verification.mechanical_failure.preserved'
                        and original_ref['sha256'] in self.events[eid]['outputs']]
            require(len(failures) == 1 and failures[0]['run_id'] == RUN
                    and failures[0]['payload'].get('status') == 'MECHANICAL_FAILURE_PRESERVED_NO_MODEL_RERUN'
                    and original_ref in failures[0]['payload'].get('files', []), 'Original failed attempt lacks accepted preservation')
        else:
            raise ValueError('Exact V10 policy permits only preserved failed-attempt revalidation')
        final_ref = side['unchanged_scientific_final']
        require(final_ref.get('path') == olddir + '/final.txt' and original_files.get(final_ref['path']) == final_ref,
                'Original scientific final not preserved')
        final_raw = self.source(final_ref)
        newdir = f'runs/{RUN}/results/{jid}/native-projection-v3'
        files = index_by(side['public_files'], 'path', 'native public copy')
        require(set(files) == {newdir + '/' + name for name in ('native-check.json','native-visible.json','response.json')}
                and event['payload']['receipt']['path'] == newdir + '/receipt.json'
                and evidence['path'] == newdir + '/PROJECTION.json'
                and event['payload']['native_check'] == files[newdir + '/native-check.json'], 'Native public copy paths differ')
        expected = {r['path']:r['sha256'] for r in list(original_files.values()) + list(files.values()) + [evidence]}
        require(b.canonical(terminal['outputs']) == b.canonical(expected), 'Native projection output inventory differs')
        proof = b.strict_json(self.source(files[newdir + '/native-check.json']))
        visible = b.strict_json(self.source(files[newdir + '/native-visible.json']))
        response = b.strict_json(self.source(files[newdir + '/response.json']))
        require(proof.get('session_id') == visible.get('session_id') == sid
                and proof.get('native_source_prefix') == side.get('native_source_prefix')
                and proof.get('isolation_failures') == [], 'Native projection source/isolation differs')
        prefix = side['native_source_prefix']
        require(set(prefix) == {'bytes','sha256','records','newline_terminated'} and type(prefix['bytes']) is int
                and 0 < prefix['bytes'] <= 64*1024*1024 and HEX.fullmatch(prefix['sha256'])
                and type(prefix['records']) is int and prefix['records'] > 0 and prefix['newline_terminated'] is True,
                'Invalid native projection prefix')
        finals = [r for r in visible['records'] if r.get('role') == 'assistant' and r.get('phase') in {'final','final_answer'}]
        require(len(finals) == 1 and finals[0]['text'].encode() == final_raw
                and proof.get('final_lines') == [finals[0]['line']]
                and b.canonical(response) == b.canonical(b.strict_json(final_raw)), 'Native scientific final/response changed')
        ledger = side['ledger']; require(b.canonical(ledger) == b.canonical(proof.get('public_web_projection')),
                                       'Native projection ledger differs from proof')
        require(ledger.get('schema') == 'native-public-web-projection.v3'
                and ledger.get('policy_id') == side['policy_id'] and ledger.get('session_id') == sid
                and ledger.get('original_native_record_hashes_retained') is True
                and ledger.get('scientific_text_unchanged') is True and ledger.get('unsafe_intermediate_files_written') is False,
                'Native projection ledger boundary differs')
        require(b.canonical(ledger.get('exact_rule')) == b.canonical(rule), 'Exact V10 inline rule changed')
        key = lambda r:(r['line'],r['record_sha256'],r['call_id'])
        left_rows = [r for r in proof['public_web_calls'] if r.get('type') == 'public_web_output']
        right_rows = [r for r in visible['records'] if r.get('type') == 'public_web_output']
        left = {key(r):r for r in left_rows}; right = {key(r):r for r in right_rows}
        require(len(left) == len(left_rows) and len(right) == len(right_rows)
                and b.canonical(sorted(left.items())) == b.canonical(sorted(right.items())), 'Native public projection copies differ')
        changed = {}
        for row in ledger['records']:
            identity = (row['source_line'],row['source_record_sha256'],row['call_id'])
            require(identity in left and row['source_line'] not in changed and row.get('projection_copies') == 2,
                    'Unbound native projected output')
            text = left[identity]['text'].encode(); omissions = row['omissions']
            require(sha(text) == row['projected_text_sha256'] and len(text) == row['projected_text_bytes']
                    and HEX.fullmatch(row['source_text_sha256']) and type(row['source_text_bytes']) is int
                    and 0 < row['source_text_bytes'] <= 2*1024*1024 and row['omission_count'] == len(omissions)
                    and 1 <= len(omissions) <= 64, 'Native projected text commitment differs')
            shift = 0; previous_end = 0
            for omission in omissions:
                offset,length,digest = omission['source_utf8_start'],omission['url_bytes'],omission['url_sha256']
                require(type(offset) is int and offset >= previous_end and type(length) is int and 1 <= length <= 16384
                        and offset + length <= row['source_text_bytes'] and HEX.fullmatch(digest)
                        and omission.get('reason') == 'SIGNED_PUBLIC_URL_QUERY_CREDENTIALS'
                        and omission.get('variant') in {'SIGV2_REGIONAL_TEMPORARY','SIGV4_V10_EXACT_PUBLIC_URL'},
                        'Invalid native URL omission commitment')
                marker = '[SIGNED PUBLIC URL EXCLUDED; sha256=' + digest + '; bytes=' + str(length) + ']'
                require(omission['replacement'] == marker and text[offset+shift:offset+shift+len(marker.encode())] == marker.encode(),
                        'Native omission marker/position differs')
                shift += len(marker.encode()) - length; previous_end = offset + length
            require(row['source_text_bytes'] + shift == len(text), 'Native projection byte conservation differs')
            changed[row['source_line']] = row
        require(type(ledger.get('source_output_records')) is int and ledger['source_output_records'] == len(changed)
                and type(ledger.get('omitted_url_count')) is int
                and ledger['omitted_url_count'] == sum(r['omission_count'] for r in changed.values())
                and (not changed or jid.endswith('-L'))
                and (mode != 'MECHANICAL_REVALIDATION_FROM_FAILED_ATTEMPT' or bool(changed)), 'Native projection omission totals/scope differ')
        require(set(changed) == {rule['source_line']} and ledger['source_output_records'] == 1
                and ledger['omitted_url_count'] == 3, 'Exact V10 observed omission inventory changed')
        row = changed[rule['source_line']]
        require(all(row[field] == rule[field] for field in
                    ('source_line','source_record_sha256','call_id','source_text_sha256','source_text_bytes')),
                'Exact V10 public output identity changed')
        exact = [o for o in row['omissions'] if o['variant'] == 'SIGV4_V10_EXACT_PUBLIC_URL']
        require(len(exact) == 1 and all(exact[0][field] == rule[field]
                for field in ('source_utf8_start','url_sha256','url_bytes'))
                and sum(o['variant'] == 'SIGV2_REGIONAL_TEMPORARY' for o in row['omissions']) == 2,
                'Exact V10 URL exception not consumed once or old omission variants changed')
        return {'evidence':evidence,'changed':changed,'policy_event_id':policy['id'],'native_projection_v3':True}

    def baseline(self):
        b = self.manifest['baseline']
        require(b['message_count'] == 14939 and b['indexed_sessions'] == 3384, 'Wrong baseline counts')
        raw_index = self.bound(b['index']); raw_bundles = self.bound(b['bundle_manifest'])
        require(sha(raw_index) == BASE_INDEX_SHA and sha(raw_bundles) == BASE_BUNDLES_SHA,
                'Baseline is not the frozen 14939-message edition')
        base = self.base
        # Only these paths change in the temporary overlay. No repository files
        # are copied, replaced or written, and predecessor source is untouched.
        with tempfile.TemporaryDirectory(prefix='philosophy-log-baseline-') as directory:
            temporary = Path(directory)
            overlay = {'logs/index.json': temporary / 'index.json',
                       'logs/bundles/manifest.json': temporary / 'bundles.json'}
            overlay['logs/index.json'].write_bytes(raw_index)
            overlay['logs/bundles/manifest.json'].write_bytes(raw_bundles)
            class Overlay(base.Verifier):
                def path(inner, rel):
                    return overlay[rel] if rel in overlay else super().path(rel)
            verifier = Overlay(self.root); report = verifier.run()
            oldindex = base.strict_json(raw_index)
            docs = verifier.conversations(oldindex)
        require(report['status'] == 'PASS' and report['union_messages'] == 14939, 'Predecessor verification failed')
        return oldindex, base.strict_json(raw_bundles), docs, report

    def cutoff_check(self):
        old = index_by(self.reader.load(self.base.PREFIX + '/native-source-cutoffs.json'), 'session_id', 'old native cutoff')
        rows = self.base.strict_json(self.bound(self.manifest['source_cutoffs']))
        current = index_by(rows, 'session_id', 'native cutoff')
        for sid, row in current.items():
            require(row.get('source_kind') != 'internal_runtime' and type(row.get('source_bytes_at_cutoff')) is int
                    and row['source_bytes_at_cutoff'] > 0 and type(row.get('source_line_cutoff')) is int
                    and row['source_line_cutoff'] > 0 and HEX.fullmatch(row.get('source_prefix_sha256', '')),
                    'Invalid new native prefix identity')
            previous = old.get(sid)
            if previous:
                require(row.get('previous_prefix_matched') is True
                        and row.get('previous_prefix_bytes') == previous['source_bytes_at_cutoff']
                        and row.get('previous_prefix_sha256') == previous['source_prefix_sha256']
                        and row['source_bytes_at_cutoff'] >= previous['source_bytes_at_cutoff']
                        and row['source_line_cutoff'] >= previous['source_line_cutoff'], 'Prior native prefix binding differs')
                if row['source_bytes_at_cutoff'] == previous['source_bytes_at_cutoff']:
                    require(row['source_prefix_sha256'] == previous['source_prefix_sha256'], 'Same-length native prefix hash differs')
            else:
                require(row.get('previous_prefix_bytes') == 0 and row.get('previous_prefix_sha256') is None
                        and row.get('previous_prefix_matched') is None, 'Invented prior native prefix')
            self.base.private_check(row, 'source cutoff', hidden=True)
        return current

    def accepted_check(self):
        b = self.base; m = self.manifest
        rows = m['canonical_events']; ids = index_by(rows, 'event_id', 'canonical event descriptor')
        for eid, row in ids.items():
            event = event_check(b, b.strict_json(self.source(row)))
            require(event['id'] == eid and row['path'] == f'research/archive/events/{event["sequence"]:012d}.json',
                    'Exported canonical identity/path mismatch')
            self.events[eid] = event
        jobs = b.strict_json(self.source(m['scientific_jobs']))['jobs']
        by_job = index_by(jobs, 'id', 'scientific job')
        require(set(by_job) == EXPECTED_JOBS, 'Scientific queue is not the exact20-job set')
        records = index_by(m['safe_artifacts'], 'path', 'safe artifact')
        for row in records.values():
            self.source(row)
            require(row.get('canonical_event_ids') and len(set(row['canonical_event_ids'])) == len(row['canonical_event_ids']),
                    'Missing/duplicate artifact attribution')
            for eid in row['canonical_event_ids']:
                require(eid in self.events and row['sha256'] in self.events[eid]['outputs'] + self.events[eid]['inputs'],
                        'Artifact not bound by named canonical event')
        accepted = index_by(m['accepted_scientific'], 'job_id', 'accepted scientific result')
        require(set(accepted) == EXPECTED_JOBS and len({r['session_id'] for r in accepted.values()}) == 20,
                'Exactly20 independent accepted scientific sessions required')
        web_events = set(); self.projections = {}
        for jid, row in accepted.items():
            event = self.events.get(row['archive_event_id']); receipt = b.strict_json(self.source(row['receipt']))
            require(event is not None and self.source(row['canonical_event']) == self.source(ids[event['id']]), 'Acceptance event reference mismatch')
            payload = event['payload']; job = by_job[jid]
            require(event['kind'] == 'research.verification.result.accepted' and event['run_id'] == RUN
                    and event['session_id'] == row['session_id'] and payload.get('job_id') == jid
                    and payload.get('scientific') is True and payload.get('independence_verified') is True
                    and payload.get('status') == 'DEEP_VERIFICATION_RESULT_ARCHIVED'
                    and receipt.get('event_id') == event['id'] and receipt.get('job_id') == jid
                    and receipt.get('session_id') == row['session_id'] and receipt.get('status') == payload['status']
                    and b.canonical(receipt.get('files')) == b.canonical(payload.get('files'))
                    and receipt.get('receipt') == payload.get('receipt'), 'Scientific receipt/event mismatch')
            terminal = b.strict_json(self.source(payload['receipt']))
            require(terminal.get('status') == 'COMPLETE_LOCAL_PENDING_CANONICAL_ARCHIVE'
                    and terminal.get('job_id') == jid and terminal.get('session_id') == row['session_id']
                    and not terminal.get('quality_flags'), 'Invalid accepted terminal result')
            require(terminal.get('requested_model') == 'gpt-6-astra' and terminal.get('requested_effort') == 'ultra'
                    and terminal.get('requested_service_tier') == 'default', 'Accepted configuration differs')
            version = 3 if jid in {'V01-A', 'V02-A'} else 4
            transports = [self.events[eid] for eid in event['parents'] if eid in self.events
                          and self.events[eid]['kind'] == f'research.verification.transport_v{version}.accepted']
            require(len(transports) == 1 and transports[0]['run_id'] == RUN, 'Exact accepted transport parent missing')
            transport = transports[0]
            queue_path = f'runs/{RUN}/jobs_v{version}.json'
            refs = index_by(transport['payload']['files'], 'path', 'transport input')
            require(queue_path in refs, 'Transport queue not bound')
            queue = b.strict_json(self.source(refs[queue_path]))['jobs']
            runtime_jobs = index_by(queue, 'id', 'runtime job')
            require(set(runtime_jobs) == EXPECTED_JOBS | {'SMOKE-L3'}, 'Accepted transport finite queue differs')
            runtime_job = runtime_jobs[jid]
            changed = {k for k in set(job) | set(runtime_job) if b.canonical(job.get(k)) != b.canonical(runtime_job.get(k))}
            require(not changed or job['role'] == 'literature' and changed == {'prompt_file', 'prompt_sha256'}, 'Scientific job changed beyond neutral transport appendix')
            for field in ('prompt', 'schema'):
                name = runtime_job[field + '_file']; digest = runtime_job[field + '_sha256']
                require(name in refs and refs[name]['sha256'] == digest
                        and terminal.get(field + '_sha256') == digest, 'Accepted runtime input differs')
                self.source(refs[name])
            if changed:
                appendix = f'runs/{RUN}/transport-repair-v2/TRANSPORT_INSTRUCTION.txt'
                require(appendix in refs, 'Neutral transport appendix not accepted')
                require(self.source(refs[runtime_job['prompt_file']]) == self.source({'path':job['prompt_file'],'sha256':job['prompt_sha256']}) + self.source(refs[appendix]), 'Literature prompt amendment is not exact neutral appendix')
            for ref in payload['files']:
                self.source(ref)
                require(ref['path'] in records and ref['sha256'] == records[ref['path']]['sha256']
                        and event['id'] in records[ref['path']]['canonical_event_ids'], 'Accepted artifact missing from inventory')
            for name, digest in terminal['outputs'].items():
                self.source({'path': name, 'sha256': digest})
            projection = self.projection_check(jid, event, terminal)
            if projection is not None: self.projections[jid] = projection
            for eid in payload.get('web_event_ids', []):
                require(eid not in web_events and eid in self.events, 'Duplicate/missing web event')
                web_events.add(eid)
        coordinator = m['coordinator']; ce = self.events.get(coordinator['archive_event_id'])
        cr = b.strict_json(self.source(coordinator['receipt']))
        require(ce is not None and ce['kind'] == 'research.verification.completed' and ce['run_id'] == RUN
                and cr.get('event_id') == ce['id'] and cr.get('status') == 'VERIFICATION_COMPLETE_BOUNDED'
                and cr.get('scientific_results_accepted') == 20 and ce['payload'].get('scientific_results_accepted') == 20
                and ce['payload'].get('status') == cr['status'] and cr.get('submission_authorized') is False,
                'Accepted coordinator closure missing')
        require(self.source(coordinator['canonical_event']) == self.source(ids[ce['id']]), 'Coordinator event reference mismatch')
        for field in ('decision', 'cards', 'primary', 'reserves', 'submission_authorized'):
            require(b.canonical(cr.get(field)) == b.canonical(ce['payload'].get(field)), 'Coordinator receipt differs from accepted decision')
        primary, reserves = cr.get('primary', []), cr.get('reserves', [])
        require(len(primary) == 3 and len(reserves) == 2 and len(set(primary + reserves)) == 5
                and set(primary + reserves) <= {f'V{i:02d}' for i in range(1, 11)}
                and {row['archive_event_id'] for row in accepted.values()} <= set(ce['parents']),
                'Coordinator3+2 or20-result provenance missing')
        for key in ('decision', 'cards'): self.source(cr[key])
        return accepted, web_events

    def accepted_visible_check(self, accepted, docs):
        count = 0
        for row in accepted.values():
            sid = row['session_id']; visible = self.base.strict_json(self.source(row['native_visible']))
            event = self.events[row['archive_event_id']]
            require(any(ref['path'] == row['native_visible']['path'] and ref['sha256'] == row['native_visible']['sha256']
                        for ref in event['payload']['files']), 'Native visible proof is not accepted for this job')
            require(visible.get('session_id') == sid and sid in docs, 'Accepted visible session absent from final union')
            lookup = {(m['source_line'], m['role']):m for m in docs[sid]['messages']}
            for record in visible['records']:
                if record.get('role') not in {'user', 'assistant'}: continue
                message = lookup.get((record['line'], record['role']))
                require(message is not None and message['text'] == record['text']
                        and message.get('source_line_sha256', message.get('raw_sha256')) == record['record_sha256'],
                        'Accepted scientific visible record absent or changed in final union')
                count += 1
        return count

    def overlap_check(self, files, prior_report):
        evidence = self.manifest['audit_evidence']; ref = evidence['tool_pending_export_overlap']
        source = descriptor(evidence['tool_pending_export_overlap_source'])
        require(descriptor(ref) == descriptor(files[ref['path']]), 'Tool-overlap evidence not file-bound')
        raw = self.bound(ref)
        require(sha(raw) == source['sha256'] and len(raw) == source['bytes'], 'Tool-overlap source copy changed')
        report = self.base.strict_json(raw)
        reviewed = self.reader.load(self.base.PREFIX + '/reviewed-codex-tools.json')['records']
        key = lambda r:(r['session_id'], r['source_line'], r['source_record_sha256'])
        expected = {key(r) for r in reviewed}; actual = {key(r) for r in report['records']}
        count = len(expected); generic = prior_report['pending_native_tool_records']
        require(len(reviewed) == count and len(report['records']) == count and actual == expected,
                'Tool-overlap identities differ from retained reviewed tools')
        disposition = 'EXACT_EXPORTED_TOOL_INCLUDED_IN_GENERIC_PENDING'
        require(report.get('status') == 'PASS_BOUNDED_TOOL_EXPORT_OVERLAP'
                and report.get('generic_native_tool_pending_count') == generic
                and report.get('exported_reviewed_tool_fragments') == report.get('exact_overlap') == count
                and report.get('generic_pending_without_this_supplement_identity') == generic - count
                and report.get('dispositions') == {disposition:count}
                and all(r.get('projection_kind') == 'tool_pending' and r.get('disposition') == disposition for r in report['records']),
                'Tool-overlap counts/dispositions differ')
        old = index_by(self.reader.load(self.base.PREFIX + '/native-source-cutoffs.json'), 'session_id', 'old native cutoff')
        prefixes = index_by(report['verified_original_source_prefixes'], 'session_id', 'overlap prefix')
        require(set(prefixes) == {r['session_id'] for r in reviewed}, 'Tool-overlap prefix inventory differs')
        for sid, row in prefixes.items():
            require(sid in old and row.get('verified') is True and row.get('bytes') == old[sid]['source_bytes_at_cutoff']
                    and row.get('sha256') == old[sid]['source_prefix_sha256'], 'Tool-overlap prefix binding differs')
        return count

    def run(self):
        b = self.base; m = self.manifest; prefix = m.get('prefix', '')
        require(m.get('schema') == 'final-visible-log-delta.v1'
                and re.fullmatch(r'logs/updates/[A-Za-z0-9][A-Za-z0-9_.-]+', prefix)
                and self.manifest_path == prefix + '/MANIFEST.json', 'Invalid final delta location/schema')
        files = index_by(m['files'], 'path', 'delta file')
        for name, row in files.items():
            require(name.startswith(prefix + '/') or name in {'logs/index.json', 'logs/bundles/manifest.json'}, 'Delta escaped output scope')
            raw = self.bound(row)
            if name.endswith('.json'): b.private_check(b.strict_json(raw), name, hidden=True)
            elif name.endswith('.jsonl'): b.private_check([b.strict_json(line) for line in raw.splitlines() if line.strip()], name, hidden=True)
            elif name.endswith(('.md', '.txt', '.py')): b.private_check(raw.decode(), name, hidden=True)
            else: require(name.endswith('.tar.gz'), 'Unapproved final-delta file type')
        actual_paths = {str(p.relative_to(self.root)) for p in (self.root / prefix).rglob('*') if p.is_file()}
        require(actual_paths == {p for p in files if p.startswith(prefix + '/')} | {self.manifest_path}, 'Unlisted final-delta file')
        for key in ('current_index', 'current_bundle_manifest', 'source_cutoffs', 'inherited_proof'):
            require(descriptor(m[key]) == descriptor(files[m[key]['path']]), 'Unbound delta descriptor')
        require(m['current_index']['path'] == 'logs/index.json' and m['current_bundle_manifest']['path'] == 'logs/bundles/manifest.json', 'Wrong current index paths')
        oldindex, oldbundles, olddocs, prior_report = self.baseline()
        overlap_count = self.overlap_check(files, prior_report)
        current = b.strict_json(self.bound(m['current_index'])); bundles = b.strict_json(self.bound(m['current_bundle_manifest']))
        oldmap = index_by(oldbundles['bundles'], 'path', 'baseline bundle')
        newmap = index_by(bundles['bundles'], 'path', 'current bundle')
        addedmap = index_by(m['new_bundles'], 'path', 'new bundle')
        require(not set(oldmap) & set(addedmap) and set(newmap) == set(oldmap) | set(addedmap), 'Bundle union changed')
        for name, row in {**oldmap, **addedmap}.items():
            require(b.canonical(row) == b.canonical(newmap[name]), 'Retained/new bundle descriptor changed')
        wanted = collections.defaultdict(set)
        for row in current['sessions']:
            if row.get('conversation_archive'):
                wanted['logs/' + b.safe_name(row['conversation_archive'])].add(b.safe_name(row['conversation_member']))
        require(set(wanted) <= {'logs/' + p for p in newmap}, 'Conversation points outside bound bundles')
        for name, row in newmap.items():
            rel = 'logs/' + name; full = dict(row, path=rel)
            if name in addedmap: require(descriptor(full) == descriptor(files[rel]), 'New bundle not file-bound')
            self.reader.bundle(full, wanted[rel], new=name in addedmap)
        currentdocs = self.reader.conversations(current); cutoffs = self.cutoff_check()
        inherited = b.strict_json(self.bound(m['inherited_proof']))
        require(inherited.get('schema') == 'bound-inherited-visible-identities.v1' and len(inherited['records']) == 8, 'Exactly8 inherited identities required')
        original_ref = descriptor(inherited['original_report'])
        original_name = prefix + '/historical-gap-classification/VISIBLE_OVERLAP.json'
        original_raw = self.bound(files[original_name])
        require(sha(original_raw) == original_ref['sha256'] and len(original_raw) == original_ref['bytes'], 'Inherited classification source changed')
        original = b.strict_json(original_raw); expected_inherited = {}
        old_identities = {(sid, *b.key(message)) for sid, doc in olddocs.items() for message in doc['messages']}
        for row in original['records']:
            identity = (row['session_id'], row['source_line'], row['role'], row['text_sha256'])
            if identity in old_identities: continue
            require(identity not in expected_inherited and row.get('inherited_user_message') is True
                    and row.get('only_removed_field') == 'metadata.inherited_user_message'
                    and row.get('projection_kind_after_one_field_omission') == 'text'
                    and bool(row.get('matches_in_frozen_union')), 'Unapproved original inherited classification')
            expected_inherited[identity] = row
        require(len(expected_inherited) == 8, 'Original inherited classification does not identify exactly8 missing copies')
        proof = []
        for row in inherited['records']:
            require(row.get('inherited_user_message') is True and row.get('only_removed_field') == 'metadata.inherited_user_message', 'Wrong inherited proof')
            identity = (row['session_id'], row['source_line'], row['role'], row['text_sha256'])
            expected_row = expected_inherited.get(identity)
            require(expected_row is not None and all(b.canonical(expected_row.get(k)) == b.canonical(value) for k, value in row.items()), 'Minimal inherited proof differs from original classification')
            proof.append(dict(row, identity=identity))
        counts = union_check(b, olddocs, currentdocs, m['additions'], proof, cutoffs)
        added_counts = collections.Counter(row['session_id'] for row in m['additions'])
        for sid, row in cutoffs.items():
            require(type(row.get('added_messages')) is int and row['added_messages'] == added_counts[sid],
                    'Native cutoff/addition counts differ')
        require(counts[0] == m['old_messages'] == 14939 and counts[1] == m['added_messages']
                and counts[2] == m['inherited_copies'] == 8
                and sum(counts[:2]) == m['union_messages'] == current['message_count']
                and len(currentdocs) == m['indexed_sessions'], 'Final union counts disagree')
        supplemental = index_by(m['supplemental_bundles'], 'path', 'supplemental bundle')
        expected = [m['safe_artifacts_bundle']] + ([m['public_web_bundle']] if m.get('public_web_bundle') else [])
        require(b.canonical(sorted(supplemental.values(), key=lambda x:x['path'])) == b.canonical(sorted(expected, key=lambda x:x['path'])), 'Supplemental bundle inventory differs')
        for name, row in supplemental.items():
            require(descriptor(row) == descriptor(files[name]), 'Supplemental bundle not file-bound')
            names = [x['path'] for x in row['members']]; self.reader.bundle(row, names, new=True)
            if name == m['safe_artifacts_bundle']['path']:
                self.artifacts = {p: self.reader.member_cache[(name, p)] for p in names}
        administrative_count = self.administrative_check()
        accepted, web_events = self.accepted_check()
        accepted_visible = self.accepted_visible_check(accepted, currentdocs)
        web = m.get('public_web_bundle'); seen = set()
        for row in web['members'] if web else []:
            value = b.strict_json(self.reader.member_cache[(web['path'], row['path'])]); eid = value['canonical_event_id']
            require(eid in web_events and eid not in seen and row['path'] == eid + '.json', 'Unbound/duplicate public web member'); seen.add(eid)
            event = self.events[eid]; p = event['payload']; fragment = value['fragment']; jid = value['job_id']
            require(event['kind'] == 'research.verification.public_web_fragment' and event['run_id'] == RUN
                    and event['session_id'] == value['session_id'] == accepted[jid]['session_id']
                    and p['job_id'] == jid and p['fragment_sha256'] == value['fragment_sha256']
                    and value['fragment_sha256'] == sha((json.dumps(fragment, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode())
                    and p['source_line'] == fragment['line'] and p['source_record_sha256'] == value['source_record_sha256'] == fragment['record_sha256'], 'Public web fragment binding differs')
            require(fragment.get('role') == 'tool' and fragment.get('type') in {'public_web_call', 'public_web_output', 'web_search_call'}, 'Unapproved web fragment')
            common = {'line', 'record_sha256', 'role', 'type', 'status'}
            if fragment['type'] == 'public_web_output':
                require(set(fragment) == common | {'call_id', 'text'} and isinstance(fragment['text'], str)
                        and len(fragment['text'].encode()) <= 2 * 1024 * 1024 and fragment['status'] == 'completed',
                        'Unapproved public web output fields')
            elif fragment['type'] == 'public_web_call':
                require(set(fragment) == common | {'call_id', 'actions'} and isinstance(fragment['actions'], list)
                        and bool(fragment['actions']) and fragment['status'] == 'issued', 'Unapproved public web call fields')
            else:
                require(set(fragment) == common | {'id', 'action'} and isinstance(fragment['action'], dict)
                        and fragment['action'].get('type') in {'search', 'open_page', 'find_in_page'}
                        and fragment['status'] == 'completed', 'Unapproved builtin public web fields')
            b.private_check(fragment, 'public web fragment', hidden=True)
            projection = self.projections.get(jid)
            if projection and (projection.get('native_projection_v2') or projection.get('native_projection_v3')):
                changed = fragment['line'] in projection['changed']
                require(p.get('archive_projection') == projection['evidence']
                        and projection['policy_event_id'] in event['parents']
                        and p.get('signed_urls_omitted') is changed and 'original_fragment_sha256' not in p,
                        'Native public web projection attribution differs')
                if changed:
                    row = projection['changed'][fragment['line']]
                    require(p.get('source_text_sha256') == row['source_text_sha256']
                            and p.get('source_text_bytes') == row['source_text_bytes'], 'Native web source text commitment differs')
                else:
                    require('source_text_sha256' not in p and 'source_text_bytes' not in p,
                            'Unchanged native public fragment claims omission metadata')
            elif projection:
                changed = fragment['line'] in projection['changed']
                require(p.get('archive_projection') == projection['evidence']
                        and projection['policy_event_id'] in event['parents']
                        and p.get('signed_urls_omitted') is changed
                        and HEX.fullmatch(p.get('original_fragment_sha256', '')), 'Public web omission attribution differs')
                if not changed:
                    require(p['original_fragment_sha256'] == value['fragment_sha256'], 'Unchanged web fragment was rewritten')
            else:
                require('archive_projection' not in p, 'Unbound public web projection')
        require(seen == web_events and len(seen) == m['public_web_fragments'], 'Public web evidence inventory differs')
        return {'status': 'PASS', 'baseline_message_objects_preserved': counts[0], 'added_visible_messages': counts[1],
                'inherited_copies': counts[2], 'union_messages': m['union_messages'], 'indexed_sessions': len(currentdocs),
                'accepted_scientific': len(accepted), 'public_web_fragments': len(seen),
                'accepted_visible_records_in_union': accepted_visible,
                'retained_reviewed_tools_also_in_generic_pending': overlap_count,
                'safe_projected_scientific_results': len(self.projections),
                'administrative_artifacts_without_canonical_acceptance_claim': administrative_count,
                'baseline_bundle_files_verified': prior_report['bundle_files_verified'],
                'new_bundle_files_verified': len(addedmap) + len(supplemental),
                'credential_scan_findings': 0, 'native_sources_read': 0, 'repository_writes': 0,
                'boundary': 'Exact pinned export and typed union preservation. Exported event self-hashes and acceptance links checked; no new canonical chain audit. Prefix commitments and source line ranges verified from bound reports; native originals are not exported or reread. Explicit gaps remain; no whole-provider capture or novelty claim.'}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    p.add_argument('--manifest', required=True); p.add_argument('--manifest-sha256', required=True)
    args = p.parse_args()
    try:
        result = Verifier(args.root, args.manifest, args.manifest_sha256).run()
    except (ValueError, KeyError, TypeError, OSError, UnicodeError, tarfile.TarError) as exc:
        print(json.dumps({'status': 'FAIL', 'reason': str(exc)}, ensure_ascii=False)); return 1
    print(json.dumps(result, ensure_ascii=False, indent=2)); return 0


if __name__ == '__main__':
    sys.exit(main())
