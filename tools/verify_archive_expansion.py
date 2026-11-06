"""Verify the November 5 source expansion and restore all previous editions."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

import check_links as navigation
import verify_submission_edition as submitted
from verify_release_edition import old_keys

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = 'evidence/archive-expansion/20261105/MANIFEST.json'
PREVIOUS = 'evidence/closeout/20261101/MANIFEST.json'
PREVIOUS_SHA = 'b24d4f9a2bbec1f6d69e3c2dd74f76916083903db2fe0615386e540a83187088'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def at(name):
    p = Path(name)
    require(not p.is_absolute() and '..' not in p.parts and '.git' not in p.parts,
            'Unsafe manifest path')
    return ROOT / p


def inventory(root):
    return {p.relative_to(root).as_posix() for p in root.rglob('*')
            if p.is_file() and not p.is_symlink()
            and not (set(p.relative_to(root).parts) & {'.git', '.cache', '__pycache__'})
            and p.name != '.DS_Store' and p.suffix not in {'.pyc', '.tmp'}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest-sha256')
    args = parser.parse_args()
    manifest = json.loads(at(MANIFEST).read_text())
    if args.manifest_sha256:
        require(sha(at(MANIFEST)) == args.manifest_sha256, 'Expansion manifest changed')
    require(sha(at(PREVIOUS)) == PREVIOUS_SHA, 'Previous manifest changed')
    actual = inventory(ROOT)
    require(actual == set(manifest['edition_files']) | {MANIFEST}, 'Edition inventory differs')
    for name, digest in manifest['edition_files'].items():
        require(sha(at(name)) == digest, 'File changed: ' + name)
    for name, digest in manifest['protected_files'].items():
        require(sha(at(name)) == digest, 'Submitted or earlier manuscript/PDF changed: ' + name)

    sources = json.loads(at('lab-sources/MANIFEST.json').read_text())
    require(sources['pending'] == [], 'Unresolved selected source')
    for row in sources['files']:
        require(sha(at(row['path'])) == row['sha256'], 'Imported source mismatch')
        require(at(row['path']).stat().st_size == row['bytes'], 'Imported source size')
        require(row['transformation'] == 'none', 'Original source was rewritten')
    require(sources['counts_by_kind']['original_history'] == 97, 'Missing original history')
    for key, count in [('scripts', 47), ('tests', 46), ('methods', 20), ('workflows', 6)]:
        require(sources['counts_by_kind'][key] == count, 'Missing source collection: ' + key)
    require(len(list((ROOT / 'docs/essay-evidence').glob('*.md'))) == 107, 'Essay routes')

    index = json.loads(at('logs/index.json').read_text())
    keys, count = old_keys(index)
    require(count == 15302, 'Changed old conversation baseline')
    sessions = {r['session_id'] for r in index['sessions']}
    for label in ['20261101-release', '20261101-submission', '20261105-archive']:
        submitted.add_log_supplement('logs/updates/' + label + '/', keys, sessions)
    catalogue = json.loads(at('logs/catalogue.json').read_text())
    require(len(keys) == catalogue['visible_message_union'], 'Conversation count differs')
    require(len(sessions) == catalogue['total_sessions'], 'Session count differs')
    require({r['session_id'] for r in catalogue['sessions']} == sessions, 'Catalogue session inventory')
    source_indexes = {}
    for entry in catalogue['sessions']:
        for fragment in entry['fragments']:
            if fragment['index'] not in source_indexes:
                source_index = json.loads(at(fragment['index']).read_text())
                source_indexes[fragment['index']] = {r['session_id']: r for r in source_index['sessions']}
            rows = source_indexes[fragment['index']]
            require(entry['session_id'] in rows, 'Catalogue fragment lacks source session')
            expected = rows[entry['session_id']]
            digest = expected.get('conversation_sha256') or expected.get('sha256')
            require(fragment['conversation_sha256'] == digest, 'Catalogue fragment hash')
    bundles = json.loads(at('logs/archive-inventory.json').read_text())
    expected = {p.relative_to(ROOT).as_posix() for p in (ROOT / 'logs').rglob('*.tar.gz')}
    require(expected == {r['path'] for r in bundles['bundles']}, 'Bundle inventory')
    require(len(expected) == bundles['bundle_count'], 'Bundle count')
    for row in bundles['bundles']:
        require(sha(at(row['path'])) == row['sha256'], 'Bundle checksum')

    original = navigation.editorial_files
    navigation.editorial_files = lambda root: sorted(set(original(root)) |
        set((root / 'docs/essay-evidence').glob('*.md')) |
        {root / 'docs/essay-evidence.md', root / 'essays/topics.md'})
    nav = navigation.check_links(ROOT)
    require(nav['status'] == 'PASS', json.dumps(nav['errors']))
    with tempfile.TemporaryDirectory(prefix='philosophy-before-expansion-') as directory:
        view = Path(directory)
        # Reconstruct the predecessor from its explicit inventory, avoiding caches
        # and the newly imported runtime. Never edit a hardlink in place.
        previous = json.loads(at(PREVIOUS).read_text())
        changed = {r['path']: r for r in manifest['previous_files']}
        for name in set(previous['edition_files']) | {PREVIOUS}:
            row = changed.get(name)
            source = at(row['snapshot']) if row else at(name)
            target = view / name
            target.parent.mkdir(parents=True, exist_ok=True)
            try:
                os.link(source, target)
            except OSError:
                shutil.copyfile(source, target)
        subprocess.run([sys.executable, '-B', str(view / 'tools/verify_submission_edition.py'),
                        '--manifest-sha256', PREVIOUS_SHA], check=True)
    print(json.dumps({'status': 'PASS', 'edition': 'archive-expansion-2026-11-05',
                      'files': len(actual), 'imported_sources': len(sources['files']),
                      'protected_files': len(manifest['protected_files']),
                      'visible_messages': len(keys), 'sessions': len(sessions),
                      'log_bundles': len(expected), 'navigation': nav,
                      'historical_submitted_edition': 'PASS'}, indent=2))


if __name__ == '__main__':
    main()
