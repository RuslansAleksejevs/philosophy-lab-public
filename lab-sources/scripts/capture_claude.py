#!/usr/bin/env python3
"""Capture selected safe visible fragments from one explicitly bound Claude JSONL."""
import argparse
from collections import Counter
import datetime
import json
import re
from pathlib import Path
import sys

from research_archive import ArchiveError, canonical, sha
from philosophy_bridge import (read_file, strict_json, workspace_job, event, bridge_lock, with_archive)
from philosophy_round import start_record

FORMAT = 'claude-visible-fragments.v1'
KNOWN_INTERNAL = {'system', 'attachment', 'queue-operation', 'custom-title', 'ai-title',
                  'atis-latch', 'last-prompt', 'mode', 'progress', 'file-history-snapshot',
                  'file-history-delta', 'summary', 'pr-link', 'saved_hook_context', 'agent-name'}
ENVELOPE_KEYS = {'type', 'message', 'cwd', 'sessionId', 'timestamp', 'uuid', 'parentUuid',
                 'isSidechain', 'entrypoint', 'gitBranch', 'userType', 'version', 'origin',
                 'permissionMode', 'promptId', 'promptSource', 'apiBlockIndex', 'effort',
                 'requestId', 'sourceToolAssistantUUID', 'toolUseResult', 'isMeta',
                 'isCompactSummary', 'agentId', 'slug'}
MESSAGE_KEYS = {'content', 'role', 'diagnostics', 'id', 'model', 'type', 'usage',
                'stop_details', 'stop_reason', 'stop_sequence', 'container', 'context_management'}
BLOCKED_TOOL_MARKERS = ('<system-reminder>', '"thinking"', '"redacted_thinking"',
                        '"signature"', '"encrypted_content"', '-----BEGIN PRIVATE KEY-----',
                        '.codex/sessions/', '.claude/projects/', 'api_key', 'authorization: bearer')


def safe_reviewed_tool(block, public_pdf_paths=()):
    """Additional conservative guard; explicit body review remains mandatory."""
    kind = block.get('type')
    allowed = {'type', 'id', 'name', 'input', 'caller'} if kind == 'tool_use' else {'type', 'tool_use_id', 'content', 'is_error'}
    if set(block) - allowed:
        return False
    if kind == 'tool_use' and (not isinstance(block.get('name'), str) or not isinstance(block.get('id'), str) or not isinstance(block.get('input'), dict)):
        return False
    # Observed in the explicitly selected Desktop smoke and documented by the
    # Messages tool-use schema. No programmatic/unknown caller body is admitted.
    if kind == 'tool_use' and 'caller' in block and block['caller'] != {'type': 'direct'}:
        return False
    if kind == 'tool_result' and (not isinstance(block.get('tool_use_id'), str) or not isinstance(block.get('content'), (str, list))):
        return False
    text = json.dumps(block, ensure_ascii=False).lower()
    # Only exact, separately reviewed public-PDF cache paths may be exempted.
    # The caller validates their job/session location and current content hash.
    # No directory prefix or other runtime content is exempted.
    for path in public_pdf_paths:
        text = re.sub(re.escape(json.dumps(path, ensure_ascii=False)[1:-1].lower())
                      + r'(?=["\s\]\)\\])', '<reviewed-public-pdf>', text)
    return not any(marker.lower() in text for marker in BLOCKED_TOOL_MARKERS)


def validate_public_pdfs(source, session_id, reviewed_public_pdfs):
    if not isinstance(reviewed_public_pdfs, dict):
        raise ArchiveError('reviewed public PDFs require an exact path/hash mapping')
    for path, digest in reviewed_public_pdfs.items():
        p = Path(path)
        if (not p.is_absolute() or p.parent != Path(source).parent / session_id / 'tool-results'
                or not re.fullmatch(r'webfetch-[0-9]+-[A-Za-z0-9]+\.pdf', p.name)
                or not isinstance(digest, str) or not re.fullmatch(r'[0-9a-f]{64}', digest)):
            raise ArchiveError('public PDF is outside the exact bound session cache')
        data = read_file(p)
        if not data.startswith(b'%PDF-') or sha(data) != digest:
            raise ArchiveError('reviewed public PDF bytes changed or are not PDF')
    return tuple(reviewed_public_pdfs)


def timestamp(value):
    if not isinstance(value, str):
        return None
    try:
        t = datetime.datetime.fromisoformat(value.replace('Z', '+00:00'))
        return t if t.tzinfo is not None else None
    except ValueError:
        return None


def fragments(raw):
    """Exact JSON spans, preserving safe fragment bytes without copying its envelope.

    Hidden-thinking siblings are parsed for structure but never returned/stored.
    A fragment is explicitly not claimed to be a complete original JSONL record.
    """
    text = raw.decode('utf-8')
    decoder = json.JSONDecoder()
    result = {}
    def ws(i):
        while i < len(text) and text[i].isspace(): i += 1
        return i
    def visit(i, path):
        i = ws(i)
        begin = i
        if text[i] == '{':
            i = ws(i + 1)
            while text[i] != '}':
                key, i = decoder.raw_decode(text, i)
                i = ws(i)
                if text[i] != ':': raise ArchiveError('invalid object delimiter')
                i = visit(i + 1, path + (key,))
                i = ws(i)
                if text[i] == '}': break
                if text[i] != ',': raise ArchiveError('invalid object separator')
                i = ws(i + 1)
            end = i + 1
        elif text[i] == '[':
            i, n = ws(i + 1), 0
            while text[i] != ']':
                i = visit(i, path + (n,)); n += 1
                i = ws(i)
                if text[i] == ']': break
                if text[i] != ',': raise ArchiveError('invalid array separator')
                i = ws(i + 1)
            end = i + 1
        else:
            _, end = decoder.raw_decode(text, i)
        if path == ('message', 'content') or (len(path) == 3 and path[:2] == ('message', 'content')):
            result[path] = text[begin:end].encode('utf-8')
        return end
    visit(0, ())
    return result


def source_snapshot(source, session_id, expected_cwd):
    source = Path(source)
    raw = read_file(source, 64 * 1024 * 1024)
    cutoff = raw.rfind(b'\n') + 1
    lines = raw[:cutoff].splitlines(keepends=True)
    parsed = []
    identity_records = 0
    for n, line in enumerate(lines, 1):
        try:
            record = strict_json(line)
        except (ValueError, UnicodeError):
            parsed.append((n, line, None))
            continue
        if not isinstance(record, dict):
            parsed.append((n, line, None)); continue
        if 'sessionId' in record and record['sessionId'] != session_id:
            raise ArchiveError('source session does not match explicitly selected ID')
        if 'cwd' in record:
            if record['cwd'] != str(expected_cwd):
                raise ArchiveError('source cwd does not match this exact job workspace')
            if record.get('sessionId') == session_id:
                identity_records += 1
        parsed.append((n, line, record))
    if not identity_records:
        raise ArchiveError('source has no jointly observed session/cwd identity')
    return raw, cutoff, parsed


@with_archive
def capture(root, workspace, source, session_id, *, start_line=1, end_line=None,
            reviewed_tool_lines=(), archive_writer=None, reviewed_public_pdfs=None):
    root, archive, workspace, job, manifest = workspace_job(root, workspace, archive_writer)
    if type(start_line) is not int or start_line < 1 or (end_line is not None and (type(end_line) is not int or end_line < start_line)):
        raise ArchiveError('invalid explicit source range')
    reviewed = set(reviewed_tool_lines)
    if any(type(n) is not int or n < start_line or (end_line is not None and n > end_line) for n in reviewed):
        raise ArchiveError('reviewed tool lines must lie in the exact selected range')
    with bridge_lock(root):
        history = archive.events()
        claims = [e for e in history if e['kind'] == 'bridge.job.claimed'
                  and e['payload'].get('job_id') == manifest['job_id'] and e['session_id'] == session_id
                  and e['payload'].get('workspace') == str(workspace)]
        if not claims:
            raise ArchiveError('claim this exact job/session before selected capture')
        claim = claims[-1]
        start = start_record(archive, manifest['run_id'])
        raw, cutoff, parsed = source_snapshot(source, session_id, workspace)
        public_pdf_paths = validate_public_pdfs(source, session_id, reviewed_public_pdfs or {})
        upper = len(parsed) if end_line is None else end_line
        if start_line > len(parsed) or upper > len(parsed):
            raise ArchiveError('selected range extends beyond complete source lines')
        selected, exclusions, gaps = [], Counter(), []
        selected_calls, selected_results = set(), set()
        blocked_calls = set()
        for _, _, r in parsed:
            m = r.get('message') if isinstance(r, dict) else None
            c = m.get('content') if isinstance(m, dict) else None
            if isinstance(c, list):
                for block in c:
                    if isinstance(block, dict) and block.get('type') == 'tool_use' and not safe_reviewed_tool(block, public_pdf_paths):
                        if isinstance(block.get('id'), str): blocked_calls.add(block['id'])
        latest_user = None
        for number, line, record in parsed[:upper]:
            if record and record.get('type') == 'user' and not record.get('isMeta') and not record.get('isCompactSummary'):
                content = record.get('message', {}).get('content') if isinstance(record.get('message'), dict) else None
                if isinstance(content, str): latest_user = timestamp(record.get('timestamp'))
            if number < start_line:
                continue
            if record is None:
                exclusions['unknown_malformed_record'] += 1; continue
            kind = record.get('type')
            if kind in KNOWN_INTERNAL:
                exclusions['excluded_internal_' + kind] += 1; continue
            if kind not in {'user', 'assistant'}:
                exclusions['unknown_record_type'] += 1; continue
            # Observed in the bound manual pilot: injected user companions carry
            # both flags as literal booleans. Exclude their bodies, never broaden
            # the visible-message allowlist or accept unknown companion schemas.
            if (kind == 'user' and record.get('isMeta') is True
                    and record.get('turnCompanion') is True
                    and not (set(record) - (ENVELOPE_KEYS | {'turnCompanion'}))):
                exclusions['excluded_injected_turn_companion'] += 1; continue
            extra_fields = set(record) - ENVELOPE_KEYS
            # Known denial metadata belongs to a visible failed tool result.
            # Retain that result; never omit the failure as internal noise.
            denial = record.get('message', {}).get('content') if isinstance(record.get('message'), dict) else None
            known_denial = (extra_fields == {'toolDenialKind'} and kind == 'user'
                            and record.get('toolDenialKind') == 'permission-rule'
                            and isinstance(denial, list) and len(denial) == 1
                            and isinstance(denial[0], dict)
                            and denial[0].get('type') == 'tool_result'
                            and denial[0].get('is_error') is True)
            if extra_fields and not known_denial:
                exclusions['unknown_message_envelope_fields'] += 1; continue
            if record.get('isMeta') or record.get('isCompactSummary'):
                exclusions['excluded_injected_context'] += 1; continue
            message = record.get('message')
            if not isinstance(message, dict) or set(message) - MESSAGE_KEYS or message.get('role') != kind or message.get('type') not in {None, 'message'}:
                exclusions['unknown_message_schema'] += 1; continue
            when = timestamp(record.get('timestamp'))
            if not when:
                exclusions['unknown_message_timestamp'] += 1; continue
            if record.get('sessionId') != session_id or record.get('cwd') != str(workspace):
                exclusions['unknown_message_identity'] += 1; continue
            content = message.get('content')
            spans = fragments(line)
            if isinstance(content, str):
                candidates = [(('message', 'content'), content, 'message', None)]
            elif isinstance(content, list):
                candidates = []
                for index, block in enumerate(content):
                    if isinstance(block, dict) and set(block) <= {'type', 'text', 'citations'} and block.get('type') == 'text' and isinstance(block.get('text'), str):
                        # Citation metadata is not retained as part of the original
                        # fragment until its schema is reviewed; don't silently drop it.
                        if block.get('citations'):
                            exclusions['unknown_text_citation_metadata'] += 1; continue
                        candidates.append((('message', 'content', index), block['text'], 'message', None))
                    elif isinstance(block, dict) and block.get('type') in {'thinking', 'redacted_thinking'}:
                        exclusions['excluded_hidden_reasoning'] += 1
                    elif isinstance(block, dict) and block.get('type') in {'tool_use', 'tool_result'}:
                        if number not in reviewed:
                            exclusions['withheld_unreviewed_tool_body'] += 1
                        elif not safe_reviewed_tool(block, public_pdf_paths) or block.get('tool_use_id') in blocked_calls:
                            exclusions['withheld_blocked_tool_body'] += 1
                        elif block['type'] == 'tool_use':
                            selected_calls.add(block['id'])
                            candidates.append((('message', 'content', index), None, 'tool_call', block['id']))
                        else:
                            selected_results.add(block['tool_use_id'])
                            candidates.append((('message', 'content', index), None, 'tool_result', block['tool_use_id']))
                    elif isinstance(block, dict) and block.get('type') == 'server_tool_use':
                        exclusions['withheld_unsupported_server_tool_body'] += 1
                    else:
                        exclusions['unknown_content_block'] += 1
            else:
                exclusions['unknown_content_container'] += 1; continue
            for path, visible, source_type, call_id in candidates:
                if visible is not None and any(marker in visible for marker in ('<system-reminder>', '<local-command-caveat>', '<local-command-stdout>')):
                    exclusions['excluded_injected_instruction_fragment'] += 1; continue
                fragment = spans[path]
                ordinal = str(path[-1]) if isinstance(path[-1], int) else 'string'
                model = message.get('model')
                effort = record.get('effort')
                observation = {'status': 'known', 'value': {'label': model,
                    'effort': effort if isinstance(effort, (str, int, float)) and not isinstance(effort, bool) else 'UNKNOWN',
                    'provenance': 'native transcript label; not backend attestation'}} if isinstance(model, str) and 0 < len(model) <= 200 else {'status': 'unknown', 'reason': 'no model label on selected native message'}
                elapsed = (when - latest_user).total_seconds() if kind == 'assistant' and latest_user and when >= latest_user else None
                selected.append({'line': number, 'fragment': fragment, 'ordinal': ordinal, 'text': visible,
                                 'role': 'tool' if source_type == 'tool_result' else kind,
                                 'native_role': kind, 'source_type': source_type, 'call_id': call_id,
                                 'timestamp': record['timestamp'], 'model': observation,
                                 'source_record_sha256': sha(line),
                                 'elapsed_since_latest_visible_user_seconds': elapsed})
        if end_line is None: gaps.append('live_source_snapshot_not_finalized')
        if cutoff != len(raw): gaps.append('partial_tail_withheld')
        if any(k.startswith('unknown') for k in exclusions): gaps.append('unknown_schema_records_or_fragments_withheld')
        if exclusions['withheld_unreviewed_tool_body']: gaps.append('tool_bodies_require_separate_explicit_safe_review')
        if exclusions['withheld_blocked_tool_body']: gaps.append('reviewed_tool_bodies_blocked_by_safety_guard')
        if exclusions['withheld_unsupported_server_tool_body']: gaps.append('server_tool_schema_not_supported')
        if selected_calls != selected_results: gaps.append('selected_tool_call_result_pairs_incomplete')
        if exclusions['excluded_injected_instruction_fragment']: gaps.append('visible_fragments_containing_injected_instructions_withheld')
        # Preflight every existing source identity before publishing any new record.
        prior = {e['delivery_key']: e for e in history}
        for item in selected:
            key = f"claude-fragment-v1:{session_id}:{item['line']}:{item['ordinal']}"
            old = prior.get(key)
            if old and (old['payload'].get('raw_sha256') != sha(item['fragment'])
                        or old['payload'].get('source_record_sha256') != item['source_record_sha256']
                        or old['run_id'] != manifest['run_id'] or old['payload'].get('job_id') != manifest['job_id']):
                raise ArchiveError('original source fragment changed or rebound to another job')
        raw_ids = []
        with archive.writer() as writer:
            for item in selected:
                digest = writer.put(item['fragment'])
                key = f"claude-fragment-v1:{session_id}:{item['line']}:{item['ordinal']}"
                old = prior.get(key)
                if old:
                    raw_ids.append(old['id']); continue
                request = event(start, 'capture.raw_record', manifest['job_id'],
                    {'format': FORMAT, 'job_id': manifest['job_id'], 'source_basename': Path(source).name,
                     'workspace': str(workspace),
                     'source_line': item['line'], 'source_fragment': item['ordinal'], 'raw_sha256': digest,
                     'source_record_sha256': item['source_record_sha256'],
                     'source_type': item['source_type'], 'call_id': item['call_id'],
                     'native_channel_role': item['native_role'],
                     'contribution_origin': 'AI_PROVIDER_RESPONSE' if item['role'] == 'assistant' else 'TOOL_OUTPUT' if item['role'] == 'tool' else 'UNKNOWN',
                     'origin_limitation': 'A native user role does not establish human authorship; AI-prepared job inputs are separately bound.',
                     'source_record_kind': 'EXACT_SAFE_JSON_FRAGMENT',
                     'full_original_record_retained': False, 'visible_text': item['text'],
                     'source_timestamp': item['timestamp'], 'elapsed_since_latest_visible_user_seconds': item['elapsed_since_latest_visible_user_seconds'],
                     'response_wall_seconds': {'status': 'unknown', 'reason': 'native fragment timestamps do not measure full response execution'},
                     'model_requested': manifest['model_requested'], 'cwd_binding_verified': True},
                     parents=[claim['id']], outputs=[digest], session=session_id, attempt=claim['attempt_id'])
                request['actor'] = {'id': 'claude:' + item['role'], 'role': item['role']}
                request['timestamp'] = item['timestamp']; request['model'] = item['model']
                raw_ids.append(writer.append(request, key)['id'])
            report = {'format': FORMAT, 'job_id': manifest['job_id'], 'session_id': session_id,
                      'workspace': str(workspace), 'claim_event_id': claim['id'],
                      'attempt_id': claim['attempt_id'],
                      'manifest_sha256': job['payload']['manifest_sha256'], 'source_basename': Path(source).name,
                      'source_snapshot_sha256': sha(raw), 'source_snapshot_bytes': len(raw),
                      'selected_range': [start_line, upper], 'partial_tail_bytes': len(raw) - cutoff,
                      'reviewed_tool_lines': sorted(reviewed),
                      **({'reviewed_public_pdfs': reviewed_public_pdfs} if public_pdf_paths else {}),
                      'status': 'INCOMPLETE' if gaps else 'BOUNDED_COMPLETE', 'gaps': gaps,
                      'exclusions': [{'reason': k, 'count': v} for k, v in sorted(exclusions.items()) if v],
                      'raw_event_ids': raw_ids, 'captured_fragments': len(raw_ids), 'full_provider_capture': False,
                      'limitations': ['Exact safe text fragments, not full mixed provider records.',
                                      'Hidden reasoning, system records, raw envelopes and unreviewed/blocked tools are not retained.',
                                      'Model/effort are native labels; response execution time and backend routing remain unknown.',
                                      'Source creation, file timestamps and capture time are distinct. No global transcript scan.']}
            encoded = canonical(report); digest = writer.put(encoded)
            coverage = writer.append(event(start, 'capture.coverage', manifest['job_id'],
                {'job_id': manifest['job_id'], 'format': FORMAT, 'status': report['status'],
                 'workspace': str(workspace), 'claim_event_id': claim['id'],
                 'gaps': gaps, 'exclusions': report['exclusions'], 'report_sha256': digest},
                parents=[claim['id']] + raw_ids, outputs=[digest], session=session_id, attempt=claim['attempt_id']),
                'claude-coverage-v1:' + digest)
        return {**report, 'coverage_event_id': coverage['id']}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    p.add_argument('--workspace', type=Path, required=True)
    p.add_argument('--source', type=Path, required=True, help='One explicitly selected native JSONL, never a directory')
    p.add_argument('--session-id', required=True)
    p.add_argument('--start-line', type=int, default=1)
    p.add_argument('--end-line', type=int)
    p.add_argument('--reviewed-tool-lines', default='', help='Comma-separated exact lines whose tool fragment bodies were explicitly reviewed as safe')
    args = p.parse_args(argv)
    try:
        reviewed = [int(n) for n in args.reviewed_tool_lines.split(',') if n]
        result = capture(args.root, args.workspace, args.source, args.session_id, start_line=args.start_line, end_line=args.end_line, reviewed_tool_lines=reviewed)
    except (ValueError, OSError, KeyError, TypeError) as exc:
        p.exit(2, 'Claude capture failed: ' + str(exc) + '\n')
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
