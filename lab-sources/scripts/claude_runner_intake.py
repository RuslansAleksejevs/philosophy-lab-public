#!/usr/bin/env python3
"""Import a file-runner collection into the canonical lab archive; no model calls."""
import argparse
from pathlib import Path

from research_archive import Archive, ArchiveError, _read, _json, sha


def ingest(collection, archive, session, run):
    collection = Path(collection)
    receipt_bytes = _read(collection / 'collection.json')
    receipt = _json(collection / 'collection.json')
    if receipt.get('protocol') not in ('claude-file-runner.v1', 'claude-file-runner.v2'):
        raise ArchiveError('Unsupported runner collection')
    files = receipt['files']
    blobs = {}
    for name, expected in files.items():
        p = Path(name)
        if p.is_absolute() or '..' in p.parts:
            raise ArchiveError('Unsafe collection path')
        data = _read(collection / p)
        if sha(data) != expected:
            raise ArchiveError('Collection hash mismatch')
        blobs[name] = data
    outputs = []
    with archive.writer() as writer:
        for data in blobs.values():
            outputs.append(writer.put(data))
        outputs.append(writer.put(receipt_bytes))
        event = writer.append({
            'kind': 'bridge.cli.collection',
            'actor': {'id': 'cli-runner-intake', 'role': 'tool'},
            'session_id': session, 'run_id': run,
            'operation_id': 'cli-intake-' + receipt['packet'],
            'attempt_id': 'intake-' + sha(receipt_bytes)[:24],
            'outputs': sorted(set(outputs)),
            'payload': {'protocol': receipt['protocol'], 'collection_sha256': sha(receipt_bytes),
                        'packet': receipt['packet'], 'files': files,
                        'disposition': 'ARCHIVED_PENDING_NATIVE_REVIEW',
                        'boundary': receipt['boundary'],
                        'meaning': 'Exact selected bytes archived. Not philosophical acceptance or proof of complete provenance.'}
        }, 'cli-collection:' + sha(receipt_bytes))
        from essay_lineage import ingest_cli, render
        lineage_events = ingest_cli(writer, collection, event, session)
        if lineage_events:
            render(writer.root.parents[1], writer)
    return {'event_id': event['id'], 'objects': len(set(outputs)), 'lineage_events': lineage_events,
            'disposition': 'ARCHIVED_PENDING_NATIVE_REVIEW'}


def main():
    import json
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('collection');p.add_argument('--archive',required=True)
    p.add_argument('--session',required=True);p.add_argument('--run',required=True)
    a=p.parse_args()
    print(json.dumps(ingest(a.collection,Archive(Path(a.archive)),a.session,a.run),indent=2))


if __name__=='__main__':main()
