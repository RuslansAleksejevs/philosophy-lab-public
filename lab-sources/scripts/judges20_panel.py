#!/usr/bin/env python3
"""Record bounded evidence from a prepared, blinded JUDGES20 panel packet.

Preparation belongs to the coordinator after all twenty essays are sealed.
This helper never selects manuscripts or treats a local receipt as authority.
"""
import argparse
import fcntl
import json
from pathlib import Path
import sys

import judges20_artifacts as essay_tools
import philosophy_round as rounds
from research_archive import Archive, ArchiveError, _read, _safe_path, canonical, sha

BASE = Path('research/campaigns/judges20-20260912/panel')
RUN = 'judges20-panel-20260912'


def own(root, judge, relative):
    directory = root / BASE / judge
    path = rounds.local(root, str(BASE / judge / relative))
    if not path.is_relative_to(directory):
        raise ArchiveError('panel artifact must stay within this judge packet')
    return path


def packet(root, archive, start, judge):
    registry = json.loads(_read(root / 'research/judges/20260912/registry.json'))
    if judge not in {j['judge_id'] for j in registry['judges']}:
        raise ArchiveError('judge is absent from the fixed registry')
    data = _read(own(root, judge, 'packet.json'))
    manifest = json.loads(data)
    if manifest.get('judge_id') != judge or manifest.get('run_id') != RUN:
        raise ArchiveError('packet identity mismatch')
    if (set(manifest) != {'judge_id', 'run_id', 'display_order', 'files'}
            or sorted(manifest['display_order']) != ['A', 'B', 'C']):
        raise ArchiveError('packet must contain only blinded input metadata and one complete display order')
    events = [e for e in archive.events() if e['kind'] == 'round.panel_packet'
              and e['run_id'] == RUN and e['payload'].get('judge_id') == judge]
    if len(events) != 1:
        raise ArchiveError('requires one canonical prepared packet')
    event = events[0]
    if (event['bindings'] != start['bindings'] or start['id'] not in event['parents']
            or event['payload'].get('manifest_sha256') != sha(data)
            or sha(data) not in event['outputs'] or archive.get(sha(data)) != data):
        raise ArchiveError('packet does not match canonical preparation')
    files = manifest.get('files', [])
    if not files or len({f['path'] for f in files}) != len(files):
        raise ArchiveError('packet files are empty or duplicate')
    if {'A.md', 'B.md', 'C.md', 'profile.md', 'task.txt', 'rules.md'} != {f['path'] for f in files}:
        raise ArchiveError('packet must contain exactly the six designated blinded inputs')
    for item in files:
        body = _read(own(root, judge, item['path']))
        if (sha(body) != item['sha256'] or item['sha256'] not in event['outputs']
                or archive.get(item['sha256']) != body):
            raise ArchiveError('prepared input bytes changed')
    return event, manifest


def process(root, args, archive):
    expected = '/root/panel_' + args.judge
    if args.agent_path != expected:
        raise ArchiveError('agent path must identify this designated fresh panel judge')
    identity = essay_tools.discover(root, expected)
    start = rounds.start_record(archive, RUN)
    prepared, manifest = packet(root, archive, start, args.judge)
    known = {e['id']: e for e in archive.events()}
    author_sessions = {e['session_id'] for e in known.values()
                       if e['kind'] == 'operation.started'
                       and e['run_id'] in {'judges20-' + str(n) for n in range(51, 71)}}
    if identity['session_id'] in author_sessions | {start['session_id']}:
        raise ArchiveError('panel judge must have a fresh non-author session')
    prior = [e for e in known.values() if e['kind'] == 'round.judge_review' and e['run_id'] == RUN]
    if any(e['session_id'] == identity['session_id'] and e['payload'].get('judge_id') != args.judge for e in prior):
        raise ArchiveError('one actual session cannot impersonate multiple panel judges')
    if args.command == 'sources-extra' and any(e['payload'].get('judge_id') == args.judge for e in prior):
        raise ArchiveError('panel review is sealed; later source use requires a preserved new assessment')
    target = own(root, args.judge, args.file)
    body = _read(target)
    if not body.strip():
        raise ArchiveError('empty panel artifact')
    digest = sha(body)
    stage = 'sources_extra' if args.command == 'sources-extra' else 'review'
    if args.command == 'review':
        previous = [e for e in prior if e['payload'].get('judge_id') == args.judge]
        if previous:
            if (len(previous) != 1 or previous[0]['session_id'] != identity['session_id']
                    or previous[0]['outputs'] != [digest]
                    or prepared['id'] not in previous[0]['parents']):
                raise ArchiveError('sealed panel review conflict')
            result = {'run_id': RUN, 'judge_id': args.judge, 'session_id': identity['session_id'],
                      'review_event_id': previous[0]['id'], 'review_sha256': digest}
            essay_tools.save_once(own(root, args.judge, 'review.receipt.json'), result)
            return result
    bound = essay_tools.bind_marker(root, archive, identity, 'panel-' + args.judge, stage, digest, RUN)
    parents = [start['id'], prepared['id'], bound['coverage_event_id']] + bound['raw_event_ids'] + bound['run_binding_ids']
    if args.command == 'sources-extra':
        items = json.loads(body)
        if not isinstance(items, list):
            raise ArchiveError('source manifest must be a list')
        saved = []
        for item in items:
            if not isinstance(item, dict) or item.get('read_status') not in {'full', 'excerpt', 'metadata', 'unavailable'}:
                raise ArchiveError('source must state actual reading coverage')
            if item.get('path'):
                saved.append({'path': item['path'], 'sha256': archive.put(_read(own(root, args.judge, item['path'])))})
            elif item.get('read_status') != 'unavailable':
                raise ArchiveError('read source needs saved exact evidence')
        event = rounds.envelope(start, 'round.source_snapshot', identity['session_id'], parents=parents,
            payload={'judge_id': args.judge, 'manifest_sha256': digest, 'sources': saved,
                     'coverage': 'Only saved evidence with explicit reading limits; hidden reasoning excluded.'})
        event['outputs'] = [archive.put(body)] + list(dict.fromkeys(x['sha256'] for x in saved))
        result = archive.append(event, 'panel-sources:' + args.judge + ':' + digest)
        return {'source_event_id': result['id'], 'manifest_sha256': digest}
    own_sources = [e['id'] for e in known.values() if e['kind'] == 'round.source_snapshot'
                   and e['run_id'] == RUN and e['session_id'] == identity['session_id']
                   and e['payload'].get('judge_id') == args.judge]
    event = rounds.envelope(start, 'round.judge_review', identity['session_id'], parents=parents + own_sources,
        payload={'judge_id': args.judge, 'artifact_sha256': digest,
                 'packet_event_id': prepared['id'], 'display_order': manifest['display_order'],
                 'raw_event_ids': bound['raw_event_ids'], 'coverage_event_id': bound['coverage_event_id'],
                 'fidelity': 'Experimental source-grounded simulation; no validated voting prediction.',
                 'context_separation': 'Distinct observed session; not proof of intellectual independence.'})
    event['outputs'] = [archive.put(body)]
    saved = archive.append(event, 'panel-review:' + args.judge)
    result = {'run_id': RUN, 'judge_id': args.judge, 'session_id': identity['session_id'],
              'review_event_id': saved['id'], 'review_sha256': digest}
    essay_tools.save_once(own(root, args.judge, 'review.receipt.json'), result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['review', 'sources-extra'])
    parser.add_argument('--judge', required=True)
    parser.add_argument('--agent-path', required=True)
    parser.add_argument('--file', required=True, help='Path relative to this judge packet directory')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    try:
        if not args.judge.replace('_', '').isalnum() or '/' in args.judge:
            raise ArchiveError('invalid judge identifier')
        with own(root, args.judge, '.panel.lock').open('a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            with Archive(root / 'research/archive').writer() as writer:
                result = process(root, args, writer)
        print(json.dumps(result, sort_keys=True))
    except (OSError, ValueError, KeyError) as exc:
        print('panel artifact error: ' + str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
