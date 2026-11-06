#!/usr/bin/env python3
"""Bounded review inventory + one-pass reviewed capture/collection/Write verification.
No model calls. Hidden reasoning is never written to the review inventory.
"""
import argparse
from collections import Counter
from pathlib import Path
import capture_claude as cc
import philosophy_bridge as b
from research_archive import ArchiveError, canonical, sha
from philosophy_round import start_record


def inspect(source, session, workspace, first, last):
    raw, cutoff, rows = cc.source_snapshot(Path(source), session, Path(workspace))
    if not (1 <= first <= last <= len(rows)):
        raise ArchiveError('closed complete-line range required')
    fragments = []; models = Counter(); tools = Counter()
    for n, line, r in rows:
        if not first <= n <= last or r.get('isMeta') or r.get('type') not in ('assistant', 'user'): continue
        m = r.get('message', {}); content = m.get('content', [])
        if r['type'] == 'assistant': models[m.get('model', 'UNKNOWN'), r.get('effort', 'UNKNOWN')] += 1
        for i, block in enumerate(content if isinstance(content, list) else []):
            if block.get('type') not in ('tool_use', 'tool_result'): continue
            if block['type'] == 'tool_use': tools[block.get('name', 'UNKNOWN')] += 1
            fragments.append({'line': n, 'index': i, 'sha256': sha(cc.fragments(line)[('message', 'content', i)]),
                              'kind': block['type'], 'reviewed': False})
    return {'protocol': 'claude-intake-review.v1', 'source_snapshot_sha256': sha(raw), 'session_id': session,
            'workspace': str(workspace), 'range': [first, last], 'fragments': fragments,
            'reviewer': '', 'reviewed_at': '', 'public_pdfs': {},
            'configuration_observations': {'requested_ui_mode': {'value': 'UNKNOWN', 'source': 'unavailable'},
                                         'observed_ui_mode': {'value': 'UNKNOWN', 'source': 'unavailable', 'observed_at': 'UNKNOWN'},
                                         'agent_policy': {'value': 'UNKNOWN', 'source': 'unavailable'}},
            'summary': {'native_models': [{'model': k[0], 'effort': k[1], 'records': v} for k, v in models.items()],
                        'tool_calls': dict(tools), 'partial_tail_bytes': len(raw) - cutoff}}


@b.with_archive
def ingest(root, workspace, source, review, disposition='partial', *, archive_writer=None):
    root, archive, workspace, job, manifest = b.workspace_job(root, workspace, archive_writer)
    if not isinstance(review, dict): review = b.strict_json(b.read_file(Path(review)))
    current = inspect(source, review['session_id'], workspace, *review['range'])
    if set(review) != set(current): raise ArchiveError('intake review schema differs')
    for key in ('protocol', 'source_snapshot_sha256', 'session_id', 'workspace', 'range', 'summary'):
        if review[key] != current[key]: raise ArchiveError('reviewed source/configuration changed')
    if not isinstance(review['reviewer'], str) or not review['reviewer'].strip() or not review['reviewed_at']:
        raise ArchiveError('explicit tool review required')
    if len(review['fragments']) != len(current['fragments']): raise ArchiveError('review fragment inventory differs')
    for r, want in zip(review['fragments'], current['fragments']):
        if r != {**want, 'reviewed': True}: raise ArchiveError('unreviewed or changed tool fragment')
    observations = review['configuration_observations']
    if set(observations) != set(current['configuration_observations']): raise ArchiveError('separate configuration observations required')
    for name, v in observations.items():
        if not isinstance(v, dict) or set(v) != set(current['configuration_observations'][name]): raise ArchiveError('configuration observation schema differs')
        if any(not isinstance(x, str) or not x.strip() for x in v.values()): raise ArchiveError('configuration must have source or explicit UNKNOWN')
    cap = cc.capture(root, workspace, Path(source), review['session_id'], start_line=review['range'][0], end_line=review['range'][1],
                     reviewed_tool_lines=sorted({x['line'] for x in review['fragments']}), reviewed_public_pdfs=review['public_pdfs'], archive_writer=archive)
    if cap['status'] != 'BOUNDED_COMPLETE':
        return {'status': 'CAPTURE_INCOMPLETE', 'coverage_event_id': cap['coverage_event_id'], 'gaps': cap['gaps']}
    # Verification uses ONLY already captured safe original tool fragments, never uncaptured native siblings.
    events = archive.events(); calls = {}; results = {}; launches = []
    for e in events:
        pl = e['payload']
        if e['kind'] != 'capture.raw_record' or pl.get('job_id') != manifest['job_id'] or pl.get('format') != cc.FORMAT: continue
        if pl.get('source_type') not in ('tool_call', 'tool_result'): continue
        block = b.strict_json(archive.get(pl['raw_sha256']))
        key = (e['session_id'], pl['call_id'])
        if block['type'] == 'tool_use':
            calls[key] = (e, block)
            if block.get('name') in ('Agent', 'Task', 'Workflow'): launches.append({'event_id': e['id'], 'tool': block['name'], 'child_model': 'UNKNOWN', 'child_coverage': 'NOT_CAPTURED'})
        else: results[key] = (e, block)
    output = b.output_directory(workspace); observed, _ = b.tree(output, runtime=True)
    verified = []; unverified = []
    for name, data in observed.items():
        matches = []
        for key, (ev, block) in calls.items():
            inp = block.get('input', {}); result = results.get(key)
            if block.get('name') != 'Write' or not isinstance(inp.get('file_path'), str) or not isinstance(inp.get('content'), str) or not result: continue
            path = Path(inp['file_path']); path = path if path.is_absolute() else workspace / path
            # No normalization of traversal or symlinks to bless a different target.
            if '..' in path.parts or str(path) != str(output / name) or inp['content'].encode() != data: continue
            rb = result[1]
            if rb.get('is_error') or not isinstance(rb.get('content'), str): continue
            # Only explicitly observed Write success formats. Unknown result prose is not success.
            message = rb['content']
            if not (message.startswith('File created successfully at: ' + str(path)) or
                    message.startswith('The file ' + str(path) + ' has been updated successfully.')): continue
            matches.append((ev, result[0]))
        if matches:
            call, result = matches[-1]
            verified.append({'path': name, 'sha256': sha(data), 'call_event': call['id'], 'result_event': result['id']})
        else: unverified.append(name)
    collection = b.collect(root, workspace, disposition, archive_writer=archive)
    # PDF review map is not a snapshot: preserve explicitly reviewed bytes as linked source artifacts now.
    pdfs = []
    for path, digest in review['public_pdfs'].items():
        data = cc.read_file(Path(path))
        if sha(data) != digest: raise ArchiveError('reviewed PDF changed before snapshot')
        pdfs.append({'sha256': archive.put(data), 'cache_basename': Path(path).name})
    start = start_record(archive, manifest['run_id']); review_sha = archive.put(canonical(review))
    summary = {'status': 'ORIGIN_VERIFIED' if not unverified and observed else 'ARTIFACT_REVIEW_REQUIRED',
               'job_id': manifest['job_id'], 'coverage_event_id': cap['coverage_event_id'],
               'collection_event_id': collection['event_id'], 'collection_id': collection['collection_id'],
               'verified_writes': verified, 'unverified_files': unverified, 'public_pdf_snapshots': pdfs,
               'native_models': review['summary']['native_models'], 'configuration_observations': observations,
               'observed_agent_launches': launches, 'review_sha256': review_sha,
               'philosophical_status_promoted': False, 'code_executed': False,
               'limits': 'Visible bounded capture, not full provider trace. UI mode is separately sourced; backend/child model routing unavailable.'}
    saved = archive.append(b.event(start, 'bridge.intake.verified', manifest['job_id'], summary,
                           parents=[cap['coverage_event_id'], collection['event_id']], outputs=[review_sha] + [v['sha256'] for v in pdfs]),
                           'claude-intake:' + sha(canonical(summary)))
    return {**summary, 'event_id': saved['id']}


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1]); sub = p.add_subparsers(dest='cmd', required=True)
    q = sub.add_parser('inspect'); q.add_argument('--source', type=Path, required=True); q.add_argument('--session', required=True); q.add_argument('--workspace', type=Path, required=True); q.add_argument('--first', type=int, required=True); q.add_argument('--last', type=int, required=True)
    q = sub.add_parser('ingest'); q.add_argument('--source', type=Path, required=True); q.add_argument('--workspace', type=Path, required=True); q.add_argument('--review', type=Path, required=True); q.add_argument('--disposition', choices=['partial', 'complete'], default='partial')
    a = p.parse_args()
    try:
        r = inspect(a.source, a.session, a.workspace, a.first, a.last) if a.cmd == 'inspect' else ingest(a.root, a.workspace, a.source, a.review, a.disposition)
        print(canonical(r).decode(), end='')
    except (ValueError, OSError, KeyError, TypeError) as e: p.exit(2, str(e) + '\n')

if __name__ == '__main__': main()
