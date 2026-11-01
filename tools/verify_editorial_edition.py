"""Verify the preserved research edition and the later editorial navigation.

The historical verifier remains unchanged. Restore only the pinned editorial
pages in a temporary view before calling it, then check the live links.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from check_links import check_links

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = 'evidence/editorial/20261031/MANIFEST.json'

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def file_at(root, name):
    p = Path(name)
    if p.is_absolute() or '..' in p.parts or str(p) != name:
        raise ValueError('Invalid relative path: ' + name)
    target = root / p
    if any(x.is_symlink() for x in [target, *target.parents]):
        raise ValueError('Symlink: ' + name)
    return target

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest-sha256', required=True)
    args = parser.parse_args()
    raw = file_at(ROOT, MANIFEST).read_bytes()
    if digest(raw) != args.manifest_sha256:
        raise ValueError('Editorial manifest differs from supplied hash')
    manifest = json.loads(raw)
    if manifest['base_commit'] != '2427b4fb3008f0b848e19ded2f26bb16659ca683':
        raise ValueError('Unexpected historical base')
    seen = set()
    for row in manifest['previous_pages']:
        if row['path'] in seen:
            raise ValueError('Duplicate page')
        seen.add(row['path'])
        if digest(file_at(ROOT, row['snapshot']).read_bytes()) != row['sha256']:
            raise ValueError('Historical page changed: ' + row['path'])
    verifier = file_at(ROOT, manifest['historical_verifier']['path'])
    if digest(verifier.read_bytes()) != manifest['historical_verifier']['sha256']:
        raise ValueError('Historical verifier changed')
    with tempfile.TemporaryDirectory(prefix='philosophy-editorial-check-') as directory:
        view = Path(directory).resolve()
        for source in ROOT.rglob('*'):
            relative = source.relative_to(ROOT)
            if '.git' in relative.parts or '__pycache__' in relative.parts:
                continue
            if source.is_symlink():
                raise ValueError('Symlink in edition')
            if source.is_file():
                target = view / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                try:
                    os.link(source, target)
                except OSError:
                    shutil.copyfile(source, target)
        for row in manifest['previous_pages']:
            target = file_at(view, row['path'])
            target.unlink()
            target.write_bytes(file_at(ROOT, row['snapshot']).read_bytes())
        for name in manifest['new_editorial_pages']:
            file_at(view, name).unlink()
        subprocess.run([sys.executable, '-B', str(view / manifest['historical_verifier']['path']),
                        '--require-final-delta', '--final-manifest-sha256',
                        manifest['final_log_manifest_sha256']], check=True)
    links = check_links(ROOT)
    if links['status'] != 'PASS':
        raise ValueError(links['errors'])
    print(json.dumps({'status': 'PASS', 'historical_pages': len(seen),
                      'current_navigation': links}, indent=2))

if __name__ == '__main__':
    main()
