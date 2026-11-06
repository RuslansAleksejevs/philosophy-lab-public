#!/usr/bin/env python3
"""Mechanical import of one existing AI manuscript candidate, without reauthoring.

Request JSON: source_stage_event_id, artifact_sha256, source_lineage_id,
import_id, session_id (actual mechanical coordinator), reason. Optional:
artifact_type (default essay). --inspect validates and prints metadata only.

Requires an existing round.stage, exact archived bytes and matching old lineage.
The new candidate retains the old stage's actor/session and old start/epoch/config
bindings. Its birth is UNKNOWN. Original source model/config observations are
retained exactly in a separate import link; unsupported typed-model formats are
not converted into a fabricated observation. This script never calls a provider
or copies a transcript, and does not execute merely by being imported.
"""
import argparse
import json
from pathlib import Path
import sys

import essay_lineage as lineage
from hundred_artifacts import cached_events
from philosophy_round import local
from research_archive import Archive, ArchiveError, _read, sha
from research_timeline import Timeline, unknown


def inspect(writer, request):
    known = {e['id']: e for e in writer.events()}
    source = known.get(request['source_stage_event_id'])
    expected = request['artifact_sha256']
    if not source or source['kind'] != 'round.stage' or expected not in source['outputs']:
        raise ArchiveError('select exact existing round.stage and its manuscript output')
    if source['actor']['role'] != 'AI':
        raise ArchiveError('this narrow adapter requires existing canonical AI-origin stage provenance')
    if sha(writer.get(expected)) != expected:
        raise ArchiveError('existing manuscript object mismatch')
    entries = lineage.index(known.values())
    old_lineage = entries.get(request['source_lineage_id'])
    if old_lineage is None:
        raise ArchiveError('select the exact existing source lineage entry')
    entry = old_lineage['payload']['entry']
    if expected not in [a['sha256'] for a in entry['artifacts']] and source['id'] not in entry['evidence']:
        raise ArchiveError('selected old lineage does not bind the exact source stage or artifact')
    starts = [e for e in known.values() if e['run_id'] == source['run_id'] and e['kind'] == 'operation.started'
              and e['payload'].get('protocol') == 'philosophy-round.v1'
              and e['attempt_id'] == source['attempt_id']]
    if len(starts) != 1:
        raise ArchiveError('source requires one exact historical round start')
    first = starts[0]
    if source['bindings'] != first['bindings'] or first['id'] not in source['parents']:
        raise ArchiveError('source stage differs from its bound historical start')
    Timeline(writer).validate_epoch(first['payload']['epoch_event_id'], first['bindings'])
    for field in ('import_id', 'session_id', 'reason'):
        if not isinstance(request[field], str) or not request[field].strip():
            raise ArchiveError('nonempty ' + field + ' required')
    if request.get('artifact_type', 'essay') not in ('essay', 'thesis', 'idea', 'other'):
        raise ArchiveError('unsupported artifact type')
    return known, source, first, old_lineage


def import_candidate(writer, request, request_body):
    _, source, first, old_lineage = inspect(writer, request)
    token = sha((request['import_id'] + '\n' + source['id'] + '\n' + request['artifact_sha256']).encode())[:40]
    context = {key: first[key] for key in ('actor', 'session_id', 'run_id', 'operation_id', 'attempt_id')}
    context.update(actor=dict(source['actor']), session_id=source['session_id'])
    source_model = source['model']
    if source_model.get('status') == 'unknown' or (set(source_model) == {'status', 'value', 'source'} and isinstance(source_model['value'], str)):
        model = source_model
    else:
        model = unknown('Exact historical model/configuration observation is preserved in the linked import event; not coerced into a typed label.')
    candidate = Timeline(writer).candidate('hundred-legacy-' + token,
        request.get('artifact_type', 'essay'), request['artifact_sha256'], first['payload']['epoch_event_id'],
        first['id'], first['payload']['stage_id'], first['payload']['selection_round_id'], 'AI', 'IMPORTED', context,
        birth=unknown('Historical manuscript birth time unavailable; current import time is not generation time.'), model=model)
    linked = writer.append({
        'kind': 'hundred.legacy_candidate_import', 'actor': {'id': 'hundred-legacy-candidate-import', 'role': 'tool'},
        'session_id': request['session_id'], 'run_id': 'hundred-legacy-import',
        'operation_id': 'legacy-import-' + token, 'attempt_id': 'legacy-import-' + token,
        'bindings': first['bindings'],
        'parents': [source['id'], first['id'], old_lineage['id'], candidate['id']],
        'inputs': [request['artifact_sha256']],
        'outputs': [writer.put(request_body), writer.put(_read(Path(__file__)))],
        'payload': {'protocol': 'hundred-legacy-candidate-import.v1', 'request': request,
                    'candidate_event_id': candidate['id'], 'source_stage_event_id': source['id'],
                    'source_lineage_id': request['source_lineage_id'],
                    'original_actor': source['actor'], 'original_session_id': source['session_id'],
                    'source_configuration': {'source_event_model': source_model,
                                             'lineage_configuration': old_lineage['payload']['entry']['configuration']},
                    'scope': 'Mechanical exact-version import; source authorship/configuration retained, no new manuscript or native attestation'}
    }, 'hundred-legacy-import:' + token)
    return {'candidate_event_id': candidate['id'], 'import_event_id': linked['id'],
            'artifact_sha256': request['artifact_sha256'], 'source_lineage_id': request['source_lineage_id'],
            'original_session_id': source['session_id'], 'original_actor': source['actor']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--request', required=True)
    parser.add_argument('--inspect', action='store_true')
    args = parser.parse_args()
    root = args.root.absolute()
    try:
        body = _read(local(root, args.request))
        request = json.loads(body)
        with Archive(root / 'research/archive').writer() as writer, cached_events(writer):
            if args.inspect:
                _, source, first, entry = inspect(writer, request)
                result = {'validated': True, 'writes': False, 'source_stage_event_id': source['id'],
                          'source_lineage_id': entry['payload']['entry']['id'], 'artifact_sha256': request['artifact_sha256'],
                          'original_actor': source['actor'], 'original_session_id': source['session_id'],
                          'original_run_id': source['run_id'], 'original_epoch_event_id': first['payload']['epoch_event_id']}
            else:
                result = import_candidate(writer, request, body)
        print(json.dumps(result, sort_keys=True))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print('legacy import error: ' + str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
