#!/usr/bin/env python3
"""Bounded PILOT10 marker capture. Never prints artifact or session text.

Canonical APIs remain authoritative; checkpoint projection is deferred to the
coordinator so parallel authors never need to read aggregate derived views.
"""
import argparse
import fcntl
import json
import os
from pathlib import Path
import sys

import capture_codex as capture
import collector_source
import philosophy_round as rounds
from research_archive import Archive, ArchiveError, _read, _safe_path, canonical, sha
from research_timeline import Timeline, unknown

CAMPAIGN = Path('research/campaigns/pilot10-20260908')


def own_file(root, essay, name):
    path = rounds.local(root, name)
    own = root / CAMPAIGN / ('essay-' + essay)
    if not path.is_relative_to(own):
        raise ArchiveError('artifact must be within this essay directory')
    return path


def save_once(path, value):
    data = canonical(value)
    _safe_path(path)
    if path.exists():
        if _read(path) != data:
            raise ArchiveError('immutable receipt conflict')
        return
    with path.open('xb') as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())


def discover(root, agent_path):
    config = json.loads(_read(root / 'collector/config.json'))
    found = collector_source.discover_sessions(
        Path(config['state_db']).expanduser(), root, {})
    matches = [s for s in found if s['agent_path'] == agent_path]
    if len(matches) != 1:
        raise ArchiveError('exact agent path is absent or ambiguous')
    item = matches[0]
    if item['session_kind'] != 'subagent' or item['source_cwd'] != str(root):
        raise ArchiveError('requires a non-runtime subagent in this exact laboratory')
    return {key: item[key] for key in
            ('session_id', 'source_path', 'source_cwd', 'agent_path')}


def marker_record(source, session_id, root, essay, stage, digest):
    """Select only one safe visible commentary line from the exact own source."""
    marker = f'[PILOT10:{essay}:{stage} sha256={digest}]'
    with capture.regular_file(source) as stream:
        size = os.fstat(stream.fileno()).st_size
        if size > 64 * 1024 * 1024:
            raise ArchiveError('own source exceeds bounded scan size')
        snapshot = stream.read(size)
    lines = snapshot[:snapshot.rfind(b'\n') + 1].splitlines(keepends=True)
    if not lines:
        raise ArchiveError('native source has no complete metadata')
    meta = capture.strict_json(lines[0])
    if (meta.get('type') != 'session_meta' or
            meta.get('payload', {}).get('id') != session_id or
            meta.get('payload', {}).get('cwd') != str(root)):
        raise ArchiveError('native source identity mismatch')
    matches = []
    for number, raw in enumerate(lines, 1):
        record = capture.strict_json(raw)
        if capture.classify(record, number, set(), set()) is not None:
            continue
        payload = record['payload']
        if (payload.get('type') != 'message' or payload.get('role') != 'assistant'
                or payload.get('phase', payload.get('channel')) != 'commentary'):
            continue
        text = '\n'.join(c['text'] for c in payload['content'])
        if marker in text:
            matches.append({'line': number, 'timestamp': record['timestamp'],
                            'raw_sha256': sha(raw), 'marker': marker})
    if len(matches) != 1:
        raise ArchiveError('requires exactly one actual own visible commentary marker for artifact hash')
    return matches[0]


def bind_marker(root, archive, identity, essay, stage, digest, run):
    source = Path(identity['source_path'])
    observed = marker_record(source, identity['session_id'], root, essay, stage, digest)
    report = capture.capture(archive.root, source, identity['session_id'], root,
                             start_line=observed['line'], end_line=observed['line'], run_id=run)
    if report['status'] != 'BOUNDED_COMPLETE' or len(report['raw_event_ids']) != 1:
        raise ArchiveError('mandatory bounded marker capture is incomplete')
    observed.update(coverage_event_id=report['coverage_event_id'],
                    raw_event_ids=report['raw_event_ids'], capture_status=report['status'])
    return observed


def candidate(archive, start, essay, stage, digest):
    context = {key: start[key] for key in
               ('actor', 'session_id', 'run_id', 'operation_id', 'attempt_id')}
    return Timeline(archive).candidate(
        f'pilot10-{essay}-{stage}', 'thesis' if stage == 'question' else 'essay', digest,
        start['payload']['epoch_event_id'], start['id'], 'INITIAL_PILOT', 'PILOT10', 'AI',
        'DERIVED' if stage == 'decision' else 'ORIGINAL', context,
        parent_candidate_events=[f'candidate:pilot10-{essay}-contribution'] if stage == 'decision' else [],
        birth=unknown('writing start was not observed; separate receipt records visible hash attestation time'))


def process(root, args):
    essay = args.essay
    directory = _safe_path(root / CAMPAIGN / ('essay-' + essay))
    directory.mkdir(parents=True, exist_ok=True)
    expected_path = '/root/' + ('critic_' if args.command == 'record' and args.stage == 'critique' else 'essay_') + essay
    if args.agent_path != expected_path:
        raise ArchiveError('agent path does not match designated essay role')
    identity = discover(root, args.agent_path)
    archive = Archive(root / 'research/archive')
    run = 'pilot10-' + essay
    identity_path = directory / 'identity.json'
    if args.command == 'init':
        start = rounds.start(root, archive, run, identity['session_id'], 'research',
                             'methods/simple-v1.json',
                             [str(CAMPAIGN / 'AUTHOR_BRIEF.md'), str(CAMPAIGN / 'campaign.json'),
                              str(CAMPAIGN / 'OPERATIONS.md'), 'scripts/pilot_artifacts.py'],
                             stage_id='INITIAL_PILOT', selection_round_id='PILOT10')
        receipt = dict(identity, run_id=run, start_event_id=start['id'])
        save_once(identity_path, receipt)
        return {'run_id': run, 'session_id': identity['session_id'], 'start_event_id': start['id']}
    author = json.loads(_read(identity_path))
    start = rounds.start_record(archive, run)
    if author['session_id'] != start['session_id'] or author['start_event_id'] != start['id']:
        raise ArchiveError('author identity conflicts with canonical round')
    if expected_path == '/root/essay_' + essay and identity['session_id'] != author['session_id']:
        raise ArchiveError('author native identity changed')
    if args.command == 'checkpoint':
        summary = own_file(root, essay, args.summary)
        receipts = [json.loads(_read(directory / (s + '.receipt.json'))) for s in rounds.STAGES]
        coverage = list(dict.fromkeys(m['coverage_event_id'] for r in receipts for m in r['captures']))
        # Only derived projection is deferred. The existing API performs every
        # canonical checkpoint, exact-evidence, coverage, and terminal check.
        refresh = rounds.refresh
        try:
            rounds.refresh = lambda *_: None
            event = rounds.checkpoint(root, archive, run, str(summary.relative_to(root)), coverage)
        finally:
            rounds.refresh = refresh
        receipt = {'run_id': run, 'checkpoint_event_id': event['id'], 'summary_sha256': sha(_read(summary)),
                   'coverage_event_ids': coverage, 'final_candidate_event_id': receipts[-1]['candidate_event_id'],
                   'final_sha256': receipts[-1]['final_sha256']}
        save_once(directory / 'checkpoint.receipt.json', receipt)
        return receipt
    stage = args.stage
    index = rounds.STAGES.index(stage)
    if index:
        _read(directory / (rounds.STAGES[index - 1] + '.receipt.json'))
    file = own_file(root, essay, args.file)
    digest = sha(_read(file))
    if stage == 'sources' and not args.source_note.strip():
        raise ArchiveError('sources require explicit --source-note retrieval and coverage statement')
    final_file = own_file(root, essay, args.final_file) if args.final_file else file
    if args.final_file and stage != 'decision':
        raise ArchiveError('--final-file is only valid for decision')
    final_digest = sha(_read(final_file))
    request = {'run_id': run, 'stage': stage, 'session_id': identity['session_id'],
               'artifact_path': str(file.relative_to(root)), 'artifact_sha256': digest,
               'source_note': args.source_note, 'final_path': str(final_file.relative_to(root)),
               'final_sha256': final_digest}
    receipt_path = directory / (stage + '.receipt.json')
    if receipt_path.exists():
        old = json.loads(_read(receipt_path))
        if any(old.get(k) != v for k, v in request.items()):
            raise ArchiveError('stage receipt replay conflict')
        return compact(old)
    captures = [bind_marker(root, archive, identity, essay, stage, digest, run)]
    if args.final_file:
        captures.append(bind_marker(root, archive, identity, essay, 'final', final_digest, run))
    event = rounds.record(root, archive, run, stage, request['artifact_path'], identity['session_id'],
                          [e for c in captures for e in c['raw_event_ids']], args.source_note)
    receipt = dict(request, stage_event_id=event['id'], captures=captures)
    if stage in ('question', 'contribution', 'decision'):
        archived_digest = archive.put(_read(final_file)) if stage == 'decision' else digest
        created = candidate(archive, start, essay, stage, archived_digest)
        receipt['candidate_event_id'] = created['id']
    save_once(receipt_path, receipt)
    return compact(receipt)


def compact(receipt):
    return {k: v for k, v in receipt.items() if k.endswith(('_id', '_sha256')) or k == 'stage'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for command in ('init', 'record', 'checkpoint'):
        p = sub.add_parser(command)
        p.add_argument('--essay', choices=[f'{n:02}' for n in range(1, 11)], required=True)
        p.add_argument('--agent-path', required=True)
        if command == 'record':
            p.add_argument('--stage', choices=rounds.STAGES, required=True)
            p.add_argument('--file', required=True)
            p.add_argument('--source-note', default='')
            p.add_argument('--final-file')
        if command == 'checkpoint':
            p.add_argument('--summary', required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    directory = _safe_path(root / CAMPAIGN / ('essay-' + args.essay))
    directory.mkdir(parents=True, exist_ok=True)
    try:
        with _safe_path(directory / '.artifacts.lock').open('a') as stream:
            fcntl.flock(stream, fcntl.LOCK_EX)
            result = process(root, args)
        print(json.dumps(result, sort_keys=True))
    except (OSError, ValueError, KeyError) as exc:
        print('pilot artifact error: ' + str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
