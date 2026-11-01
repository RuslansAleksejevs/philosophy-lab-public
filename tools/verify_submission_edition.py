"""Verify the submitted edition, its attachment copies and preserved predecessors.

Read-only; standard library only. No network, model, Git or native logs required.
"""
from pathlib import Path
import argparse
import gzip
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import zipfile

import check_links as navigation
from verify_recovered_logs import private_check
from verify_release_edition import old_keys, message_key

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = 'evidence/closeout/20261101/MANIFEST.json'
PREVIOUS = 'evidence/final-edition/20261101/RELEASE_MANIFEST.json'
PREVIOUS_HASH = '9034766d31eb8de5775c0ef818d7ef0bb005de79fa39d83a55b9c4b9fe02c386'
SELECTED = ['E050', 'E012', 'E051']


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def at(root, name):
    path = Path(name)
    require(not path.is_absolute() and '..' not in path.parts
            and '.git' not in path.parts and str(path) == name, 'Unsafe path')
    return root / path


def load(name):
    return json.loads(at(ROOT, name).read_bytes())


def bound(row):
    raw = at(ROOT, row['path']).read_bytes()
    require(sha(raw) == row['sha256'], 'Changed file: ' + row['path'])
    require('bytes' not in row or len(raw) == row['bytes'], 'Size mismatch')
    return raw


def add_log_supplement(prefix, keys, sessions):
    idx = load(prefix + 'INDEX.json')
    bound(idx['baseline'])
    require(len(keys) == idx['baseline']['messages'], 'Wrong log predecessor')
    raw = bound(dict(idx['bundle'], path=prefix + idx['bundle']['path']))
    additions = 0
    with tarfile.open(fileobj=io.BytesIO(raw), mode='r:gz') as archive:
        members = archive.getmembers()
        require(all(m.isfile() for m in members), 'Non-file log member')
        require(len(members) == len(idx['sessions']), 'Log member count')
        require({m.name for m in members} == {r['member'] for r in idx['sessions']},
                'Log member inventory')
        for row in idx['sessions']:
            raw = archive.extractfile(row['member']).read()
            require(sha(raw) == row['sha256'], 'Log member hash')
            doc = json.loads(raw)
            sid = row['session_id']
            require(doc['session']['session_id'] == sid, 'Session identity')
            require(len(doc['messages']) == row['added_messages'], 'Message count')
            for message in doc['messages']:
                require(message['role'] in {'user', 'assistant'}, 'Non-visible role')
                if message['role'] == 'assistant':
                    require(message.get('phase') in {'commentary', 'final', 'final_answer'},
                            'Hidden assistant phase')
                require(sha(message['text'].encode()) == message['text_sha256'], 'Text hash')
                private_check(message, sid, hidden=True)
                key = message_key(sid, message)
                require(key not in keys, 'Repeated or conflicting message identity')
                keys.add(key)
                additions += 1
            sessions.add(sid)
    require(additions == idx['added_messages'], 'Supplement count')
    require(len(keys) == idx['total_visible_messages'], 'Union message count')
    require(len(sessions) == idx['total_sessions_in_union'], 'Union session count')
    raw = bound(dict(idx['cutoffs'], path=prefix + idx['cutoffs']['path']))
    reports = json.loads(gzip.decompress(raw))
    require(len(reports) == idx['scanned_native_sources'], 'Source inventory')
    require(all(r['previous_prefix_matched'] is True for r in reports
                if r['previous_prefix_sha256']), 'Earlier source prefix mismatch')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest-sha256')
    args = parser.parse_args()
    raw = at(ROOT, MANIFEST).read_bytes()
    manifest = json.loads(raw)
    if args.manifest_sha256:
        require(sha(raw) == args.manifest_sha256, 'Supplied manifest pin differs')
    require(sha(at(ROOT, PREVIOUS).read_bytes()) == PREVIOUS_HASH,
            'Changed preceding edition manifest')
    actual = set()
    for path in ROOT.rglob('*'):
        relative = path.relative_to(ROOT)
        if '.git' in relative.parts or '__pycache__' in relative.parts:
            continue
        require(not path.is_symlink(), 'Symlink in edition')
        if path.is_file():
            actual.add(str(relative))
    require(actual == set(manifest['edition_files']) | {MANIFEST},
            'Missing or unlisted edition file')
    for name, digest in manifest['edition_files'].items():
        require(sha(at(ROOT, name).read_bytes()) == digest, 'Edition file changed: ' + name)

    state = load('docs/release-state.json')
    require(state['selected'] == SELECTED, 'Wrong final three')
    require(state['submission']['uploaded_pdf_bytes_verified'] is True,
            'Submission attachment status')
    require(state['submission']['all_form_fields_audited'] is False,
            'Do not turn attachment checks into a full metadata audit')
    receipt = load('evidence/closeout/20261101/SUBMISSION_VERIFICATION.json')
    require(receipt['openreview_mutations'] is False, 'Read-only platform check')
    require(receipt['ai_involvement_observed_all_three'] == 'AI throughout',
            'Observed AI category')
    files = receipt['files']
    require(len(files) == 6 and {(r['essay_id'], r['kind']) for r in files}
            == {(e, k) for e in SELECTED for k in ['essay', 'methodology']},
            'Six submitted attachments')
    for row in files:
        original = at(ROOT, row['repository_pdf']).read_bytes()
        download = at(ROOT, row['downloaded_copy']).read_bytes()
        require(original == download, 'Downloaded attachment differs')
        require(sha(original) == row['sha256'] and len(original) == row['bytes'],
                'Submitted attachment checksum')
    previous_files = load(PREVIOUS)['release_files']
    for essay in state['essays']:
        for key in ['manuscript', 'pdf', 'methodology_pdf', 'abstract', 'full_review']:
            bound(essay[key])
        if essay.get('scoped_review'):
            bound(essay['scoped_review'])
        require(essay['manuscript']['sha256'] == previous_files[essay['manuscript']['path']],
                'Submitted manuscript was rewritten')
        form = load('submission/20261101/forms/' + essay['id'] + '-form.json')
        require(form['ai_involvement'].startswith('AI throughout.'), 'Form category')

    package = load('submission/20261101/MANIFEST.json')
    for row in package['files']:
        bound(row)
    package_root = ROOT / 'submission/20261101'
    expected_package = {str(p.relative_to(ROOT)) for p in package_root.rglob('*')
                        if p.is_file() and p.name != 'MANIFEST.json'}
    require(expected_package == {r['path'] for r in package['files']}, 'Package inventory')
    zip_name = package_root / 'Submission-Package-E050-E012-E051.zip'
    expected_zip = {str(p.relative_to(package_root)) for d in ['pdf', 'latex', 'forms']
                    for p in (package_root / d).rglob('*') if p.is_file()}
    with zipfile.ZipFile(zip_name) as archive:
        require(set(archive.namelist()) == expected_zip, 'ZIP inventory')
        require(len(archive.namelist()) == len(expected_zip), 'Repeated ZIP member')
        for name in expected_zip:
            require(archive.read(name) == at(package_root, name).read_bytes(),
                    'ZIP differs from unpacked file: ' + name)
    for line in (package_root / 'SHA256SUMS.txt').read_text().splitlines():
        digest, name = line.split('  ', 1)
        require(sha(at(package_root, name).read_bytes()) == digest, 'Quick checksum')

    # The dated baseline and both additions form one disjoint retained union.
    baseline = load('logs/index.json')
    keys, count = old_keys(baseline)
    require(count == 15302, 'Retained log baseline')
    sessions = {r['session_id'] for r in baseline['sessions']}
    add_log_supplement('logs/updates/20261101-release/', keys, sessions)
    add_log_supplement('logs/updates/20261101-submission/', keys, sessions)
    require(len(keys) == 15695 and len(sessions) == 3424, 'Final log union')

    # Restore every changed predecessor byte; the original verifier checks all
    # 107 biographies, their manuscripts and every earlier preservation layer.
    with tempfile.TemporaryDirectory(prefix='philosophy-submitted-edition-') as directory:
        view = Path(directory)
        for name in actual:
            source, target = at(ROOT, name), at(view, name)
            target.parent.mkdir(parents=True, exist_ok=True)
            try:
                os.link(source, target)
            except OSError:
                shutil.copyfile(source, target)
        for row in manifest['previous_files']:
            original = bound({'path': row['snapshot'], 'sha256': row['sha256']})
            target = at(view, row['path'])
            target.unlink()
            target.write_bytes(original)
        for name in manifest['added_files']:
            at(view, name).unlink()
        subprocess.run([sys.executable, '-B', str(view / 'tools/verify_release_edition.py'),
                        '--manifest-sha256', PREVIOUS_HASH], check=True)
    prior = navigation.editorial_files
    navigation.editorial_files = lambda root: sorted(set(prior(root)) | {root/'essays/topics.md'})
    nav = navigation.check_links(ROOT)
    require(nav['status'] == 'PASS', str(nav['errors']))
    print(json.dumps({'status': 'PASS', 'edition': state['edition'],
                      'manifest_sha256': sha(at(ROOT, MANIFEST).read_bytes()),
                      'files': len(actual), 'submitted_pdf_matches': len(files),
                      'visible_messages': len(keys), 'indexed_sessions': len(sessions),
                      'predecessor_files_preserved': len(manifest['previous_files']),
                      'navigation': nav}, indent=2))


if __name__ == '__main__':
    main()
