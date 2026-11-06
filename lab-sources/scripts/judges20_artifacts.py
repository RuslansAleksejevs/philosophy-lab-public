#!/usr/bin/env python3
"""Bounded JUDGES20 marker capture. Never prints artifact or session text.

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
from research_archive import Archive, ArchiveError, _ArchiveWriter, _read, _safe_path, canonical, sha
from research_timeline import Timeline, unknown

CAMPAIGN = Path('research/campaigns/judges20-20260912')


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
    marker = f'[JUDGES20:{essay}:{stage} sha256={digest}]'
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
                             start_line=observed['line'], end_line=observed['line'], run_id=run,
                             archive_writer=archive if isinstance(archive, _ArchiveWriter) else None)
    if report['status'] != 'BOUNDED_COMPLETE' or len(report['raw_event_ids']) != 1:
        raise ArchiveError('mandatory bounded marker capture is incomplete')
    observed.update(coverage_event_id=report['coverage_event_id'],
                    raw_event_ids=report['raw_event_ids'],
                    run_binding_ids=report.get('run_binding_event_ids', []), capture_status=report['status'])
    return observed


def candidate(archive, start, essay, stage, digest):
    context = {key: start[key] for key in
               ('actor', 'session_id', 'run_id', 'operation_id', 'attempt_id')}
    return Timeline(archive).candidate(
        f'judges20-{essay}-{stage}', 'thesis' if stage == 'question' else 'essay', digest,
        start['payload']['epoch_event_id'], start['id'], 'JUDGE_GUIDED_SEARCH', 'JUDGES20', 'AI',
        'DERIVED' if stage == 'decision' else 'ORIGINAL', context,
        parent_candidate_events=[f'candidate:judges20-{essay}-contribution'] if stage == 'decision' else [],
        birth=unknown('writing start was not observed; separate receipt records visible hash attestation time'))


def first_critic(known, start):
    matches = [e for e in known.values() if e['run_id'] == start['run_id'] and e['kind'] == 'round.stage'
               and e['payload'].get('stage') == 'critique']
    if len(matches) != 1 or matches[0]['bindings'] != start['bindings']:
        raise ArchiveError('second review requires the canonical first critique')
    return matches[0]


def second_review(root, archive, start, essay):
    """A receipt locates evidence; canonical events and exact bytes authorize use."""
    directory = root / CAMPAIGN / ('essay-' + essay)
    receipt = json.loads(_read(directory / 'review2.receipt.json'))
    known = {e['id']: e for e in archive.events()}
    critic = first_critic(known, start)
    matches = [e for e in known.values() if e['run_id'] == start['run_id'] and e['kind'] == 'round.judge_review'
               and e['payload'].get('ordinal') == 2]
    if len(matches) != 1:
        raise ArchiveError('requires exactly one canonical second review')
    review = matches[0]; p = review['payload']; sid = review['session_id']
    if (review['bindings'] != start['bindings'] or sid in {start['session_id'], critic['session_id']}
            or not {start['id'], critic['id']} <= set(review['parents'])
            or receipt.get('stage_event_id') != review['id'] or receipt.get('run_id') != start['run_id']
            or receipt.get('stage') != 'review2' or receipt.get('session_id') != sid):
        raise ArchiveError('second review receipt/context does not match canonical provenance')
    digest = p.get('artifact_sha256')
    if (review['outputs'] != [digest] or receipt.get('artifact_sha256') != digest
            or sha(_read(own_file(root, essay, receipt.get('artifact_path', '')))) != digest
            or not archive.get(digest).strip()):
        raise ArchiveError('second review artifact bytes changed or do not match canonical evidence')
    profile = known.get(p.get('profile_event_id')); coverage = known.get(p.get('coverage_event_id'))
    if (not profile or profile['kind'] != 'round.judge_profile' or profile['run_id'] != start['run_id']
            or profile['bindings'] != start['bindings'] or profile['session_id'] != sid
            or profile['id'] not in review['parents'] or receipt.get('profile_event_id') != profile['id']
            or profile['outputs'] != [profile['payload'].get('profile_sha256')]
            or not archive.get(profile['outputs'][0]).strip()):
        raise ArchiveError('second review has invalid exact judge profile evidence')
    if (receipt.get('profile_path') != profile['payload'].get('profile_path')
            or receipt.get('profile_sha256') != profile['payload'].get('profile_sha256')):
        raise ArchiveError('second review receipt names a different judge profile')
    raw_ids = p.get('raw_event_ids', [])
    if (not coverage or coverage['kind'] != 'capture.coverage' or coverage['run_id'] != start['run_id']
            or coverage['session_id'] != sid or coverage['payload'].get('status') != 'BOUNDED_COMPLETE'
            or coverage['id'] not in review['parents'] or not raw_ids
            or not set(raw_ids) <= set(review['parents']) & set(coverage['parents']) & set(profile['parents'])):
        raise ArchiveError('second review lacks exact bounded capture coverage')
    captures = receipt.get('captures', [])
    if (len(captures) != 1 or captures[0].get('coverage_event_id') != coverage['id']
            or captures[0].get('raw_event_ids') != raw_ids):
        raise ArchiveError('second review receipt capture differs from canonical evidence')
    marker = f'[JUDGES20:{essay}:review2 sha256={digest}]'
    for raw_id in raw_ids:
        raw = known.get(raw_id)
        if not raw or raw['kind'] != 'capture.raw_record' or raw['actor']['role'] not in {'assistant', 'AI'}:
            raise ArchiveError('second review needs captured assistant authorship')
        binding = rounds._evidence_run_binding(known, start, raw, sid, review['parents'])
        if binding is not None and binding['id'] not in coverage['parents']:
            raise ArchiveError('second review run binding is absent from capture coverage')
        native = json.loads(archive.get(raw['payload']['raw_sha256']))
        if (capture.classify(native, raw['payload']['source_line'], set(), set()) is not None
                or native['payload'].get('role') != 'assistant'
                or native['payload'].get('phase', native['payload'].get('channel')) != 'commentary'
                or marker not in '\n'.join(c['text'] for c in native['payload']['content'])):
            raise ArchiveError('second review capture does not attest the exact review artifact')
    return review, coverage


def process(root, args, archive=None):
    essay = args.essay
    directory = _safe_path(root / CAMPAIGN / ('essay-' + essay))
    directory.mkdir(parents=True, exist_ok=True)
    role = ('reviewer2_' if args.command == 'review' else
            'reviewer1_' if args.command == 'record' and args.stage == 'critique' else
            args.agent_path.rsplit('/', 1)[-1].split(essay)[0] if args.command == 'sources-extra' else 'author_')
    if role not in ('author_', 'reviewer1_', 'reviewer2_'):
        raise ArchiveError('unknown designated campaign role')
    expected_path = '/root/' + role + essay
    if args.agent_path != expected_path:
        raise ArchiveError('agent path does not match designated essay role')
    identity = discover(root, args.agent_path)
    archive = archive or Archive(root / 'research/archive')
    run = 'judges20-' + essay
    identity_path = directory / 'identity.json'
    if args.command == 'init':
        start = rounds.start(root, archive, run, identity['session_id'], 'research',
                             'methods/judges-v1.json',
                             [str(CAMPAIGN / 'AUTHOR_BRIEF.md'), str(CAMPAIGN / 'campaign.json'),
                              str(CAMPAIGN / 'OPERATIONS.md'), str(CAMPAIGN / ('essay-' + essay) / 'author-task.txt'),
                              'research/judges/20260912/competition/RULES_SUMMARY.md',
                              'research/judges/20260912/competition/rules.html',
                              'research/judges/20260912/competition/faq.html', 'scripts/judges20_artifacts.py'],
                             stage_id='JUDGE_GUIDED_SEARCH', selection_round_id='JUDGES20')
        receipt = dict(identity, run_id=run, start_event_id=start['id'])
        save_once(identity_path, receipt)
        return {'run_id': run, 'session_id': identity['session_id'], 'start_event_id': start['id']}
    author = json.loads(_read(identity_path))
    start = rounds.start_record(archive, run)
    if author['session_id'] != start['session_id'] or author['start_event_id'] != start['id']:
        raise ArchiveError('author identity conflicts with canonical round')
    if expected_path == '/root/author_' + essay and identity['session_id'] != author['session_id']:
        raise ArchiveError('author native identity changed')
    if args.command == 'sources-extra':
        manifest = own_file(root, essay, args.manifest)
        digest = sha(_read(manifest))
        bound = bind_marker(root, archive, identity, essay, 'sources_extra', digest, run)
        event = source_snapshot(root, archive, start, identity, essay, manifest, bound)
        return {'source_event_id': event['id'], 'manifest_sha256': digest}
    if args.command == 'review':
        _read(directory / 'contribution.receipt.json')
        critic = first_critic({e['id']: e for e in archive.events()}, start)
        if identity['session_id'] in {start['session_id'], critic['session_id']}:
            raise ArchiveError('second review must use a session distinct from author and first critic')
        file = own_file(root, essay, args.file)
        digest = sha(_read(file))
        receipt_path = directory / 'review2.receipt.json'
        request = {'run_id': run, 'stage': 'review2', 'session_id': identity['session_id'],
                   'artifact_path': str(file.relative_to(root)), 'artifact_sha256': digest,
                   'profile_path': str(rounds.local(root, args.profile).relative_to(root)),
                   'profile_sha256': sha(_read(rounds.local(root, args.profile)))}
        if receipt_path.exists():
            old = json.loads(_read(receipt_path))
            if any(old.get(k) != v for k, v in request.items()):
                raise ArchiveError('second review replay conflict')
            second_review(root, archive, start, essay)
            return compact(old)
        bound = bind_marker(root, archive, identity, essay, 'review2', digest, run)
        profile = profile_snapshot(root, archive, start, identity, args.profile, bound)
        artifact = archive.put(_read(file))
        event = rounds.envelope(start, 'round.judge_review', identity['session_id'],
            parents=[start['id'], critic['id'], profile['id'], bound['coverage_event_id']] + bound['raw_event_ids'] + bound['run_binding_ids'],
            payload={'ordinal': 2, 'artifact_sha256': artifact,
                     'context_separation': 'distinct observed session, not proof of intellectual independence',
                     'profile_event_id': profile['id'], 'coverage_event_id': bound['coverage_event_id'],
                     'raw_event_ids': bound['raw_event_ids']})
        event['outputs'] = [artifact]
        saved = archive.append(event, 'judge-review:' + run + ':2')
        receipt = dict(request, stage_event_id=saved['id'], captures=[bound], profile_event_id=profile['id'])
        save_once(receipt_path, receipt)
        return compact(receipt)
    if args.command == 'checkpoint':
        review, second_coverage = second_review(root, archive, start, essay)
        summary = own_file(root, essay, args.summary)
        receipts = [json.loads(_read(directory / (s + '.receipt.json'))) for s in rounds.STAGES]
        decision_receipt = receipts[-1]
        decisions = [e for e in archive.events() if e['run_id'] == run and e['kind'] == 'round.stage'
                     and e['payload'].get('stage') == 'decision']
        if len(decisions) != 1 or review['id'] not in decisions[0]['parents']:
            raise ArchiveError('decision must causally depend on the canonical second review')
        receipts.append(json.loads(_read(directory / 'review2.receipt.json')))
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
                   'coverage_event_ids': coverage, 'final_candidate_event_id': decision_receipt['candidate_event_id'],
                   'final_sha256': decision_receipt['final_sha256']}
        save_once(directory / 'checkpoint.receipt.json', receipt)
        return receipt
    stage = args.stage
    supporting_events = []
    if stage == 'decision':
        review, _ = second_review(root, archive, start, essay)
        supporting_events = [review['id']]
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
        if supporting_events:
            canonical_stage = next((e for e in archive.events() if e['id'] == old.get('stage_event_id')), None)
            if not canonical_stage or not set(supporting_events) <= set(canonical_stage['parents']):
                raise ArchiveError('decision receipt omits canonical second-review ancestry')
        return compact(old)
    captures = [bind_marker(root, archive, identity, essay, stage, digest, run)]
    extra = {}
    if stage == 'sources':
        manifest = directory / 'source-manifest.json'
        extra['source_snapshot_event_id'] = source_snapshot(root, archive, start, identity, essay,
                                                            manifest, captures[0])['id']
    if stage == 'critique':
        if not args.profile:
            raise ArchiveError('named judge critique requires exact profile path')
        extra['profile_event_id'] = profile_snapshot(root, archive, start, identity,
                                                     args.profile, captures[0])['id']
    if args.final_file:
        captures.append(bind_marker(root, archive, identity, essay, 'final', final_digest, run))
    event = rounds.record(root, archive, run, stage, request['artifact_path'], identity['session_id'],
                          [e for c in captures for e in c['raw_event_ids']], args.source_note,
                          supporting_events=supporting_events + list(extra.values()))
    receipt = dict(request, stage_event_id=event['id'], captures=captures, **extra)
    if stage in ('question', 'contribution', 'decision'):
        archived_digest = archive.put(_read(final_file)) if stage == 'decision' else digest
        created = candidate(archive, start, essay, stage, archived_digest)
        receipt['candidate_event_id'] = created['id']
    save_once(receipt_path, receipt)
    return compact(receipt)


def compact(receipt):
    return {k: v for k, v in receipt.items() if k.endswith(('_id', '_sha256')) or k == 'stage'}


def source_snapshot(root, archive, start, identity, essay, manifest, bound):
    """Store actually saved own source bytes before the dependent argument."""
    body = _read(manifest)
    items = json.loads(body)
    if not isinstance(items, list):
        raise ArchiveError('source manifest must be a list')
    sources = []
    for item in items:
        if not isinstance(item, dict) or item.get('read_status') not in ('full', 'excerpt', 'metadata', 'unavailable'):
            raise ArchiveError('source has no explicit reading coverage')
        if item.get('path'):
            name = str(CAMPAIGN / ('essay-' + essay) / item['path'])
            path = own_file(root, essay, name)
            sources.append((item['path'], _read(path)))
        elif item.get('read_status') != 'unavailable':
            raise ArchiveError('read source requires saved exact evidence')
    with archive.writer() as writer:
        manifest_sha = writer.put(body)
        stored = [{'path': name, 'sha256': writer.put(data)} for name, data in sources]
        event = rounds.envelope(start, 'round.source_snapshot', identity['session_id'],
            parents=[start['id']] + bound['raw_event_ids'],
            payload={'manifest_sha256': manifest_sha, 'sources': stored,
                     'coverage': 'only actually stored/read evidence; see manifest for gaps'})
        event['outputs'] = [manifest_sha] + list(dict.fromkeys(s['sha256'] for s in stored))
        return writer.append(event, 'source-snapshot:' + start['run_id'] + ':' + manifest_sha)


def profile_snapshot(root, archive, start, identity, name, bound):
    profile = rounds.local(root, name)
    allowed = root / 'research/judges/20260912'
    if not profile.is_relative_to(allowed) or profile.suffix != '.md':
        raise ArchiveError('profile must be a reviewed judge markdown under the fixed corpus root')
    digest = archive.put(_read(profile))
    event = rounds.envelope(start, 'round.judge_profile', identity['session_id'],
        parents=[start['id']] + bound['raw_event_ids'],
        payload={'profile_path': str(profile.relative_to(root)), 'profile_sha256': digest,
                 'fidelity': 'experimental source-grounded simulation, not the actual judge'})
    event['outputs'] = [digest]
    return archive.append(event, 'judge-profile:' + start['run_id'] + ':' + identity['session_id'] + ':' + digest)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for command in ('init', 'record', 'checkpoint', 'review', 'sources-extra'):
        p = sub.add_parser(command)
        p.add_argument('--essay', choices=[f'{n:02}' for n in range(51, 71)], required=True)
        p.add_argument('--agent-path', required=True)
        if command == 'record':
            p.add_argument('--stage', choices=rounds.STAGES, required=True)
            p.add_argument('--file', required=True)
            p.add_argument('--source-note', default='')
            p.add_argument('--final-file')
            p.add_argument('--profile')
        if command == 'checkpoint':
            p.add_argument('--summary', required=True)
        if command == 'review':
            p.add_argument('--file', required=True)
            p.add_argument('--profile', required=True)
        if command == 'sources-extra':
            p.add_argument('--manifest', required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    directory = _safe_path(root / CAMPAIGN / ('essay-' + args.essay))
    directory.mkdir(parents=True, exist_ok=True)
    try:
        with _safe_path(directory / '.artifacts.lock').open('a') as stream:
            fcntl.flock(stream, fcntl.LOCK_EX)
            if args.command == 'init':
                with _safe_path(root / CAMPAIGN / '.starts.lock').open('a') as starts:
                    fcntl.flock(starts, fcntl.LOCK_EX)
                    with Archive(root / 'research/archive').writer() as writer:
                        result = process(root, args, archive=writer)
            else:
                with Archive(root / 'research/archive').writer() as writer:
                    result = process(root, args, archive=writer)
        print(json.dumps(result, sort_keys=True))
    except (OSError, ValueError, KeyError) as exc:
        print('pilot artifact error: ' + str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
