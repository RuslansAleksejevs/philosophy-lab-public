"""Verify dated reading links, selection membership and the preserved prior edition."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import check_links as navigation

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = 'evidence/editorial/20261101/MANIFEST.json'

def require(condition, message):
    if not condition:
        raise ValueError(message)

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def file_at(root, name):
    p = Path(name)
    require(not p.is_absolute() and '..' not in p.parts and str(p) == name, 'Unsafe path: ' + name)
    target = root / p
    require(not any(x.is_symlink() for x in [target, *target.parents]), 'Symlink: ' + name)
    return target

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest-sha256', required=True)
    args = parser.parse_args()
    raw = file_at(ROOT, MANIFEST).read_bytes()
    require(digest(raw) == args.manifest_sha256, 'Reading manifest differs from supplied hash')
    manifest = json.loads(raw)
    require(manifest['base_commit'] == '43f36eb6b09bc29703bd2922aac90e58a24fb080', 'Unexpected base')
    for row in manifest['previous_pages']:
        require(digest(file_at(ROOT, row['snapshot']).read_bytes()) == row['sha256'], 'Changed snapshot: ' + row['path'])
    for row in manifest['current_files']:
        require(digest(file_at(ROOT, row['path']).read_bytes()) == row['sha256'], 'Changed reading file: ' + row['path'])
    state = json.loads(file_at(ROOT, 'docs/reading-state.json').read_text())
    essays = state['essays']
    expected = {f'E{i:03d}' for i in range(1, 101)} | {f'F{i:02d}' for i in range(1, 7)} | {'S02'}
    require(len(essays) == 107 and {r['id'] for r in essays} == expected, 'Essay inventory')
    require(len(state['themes']) == 10 and len({r['id'] for r in state['themes']}) == 10, 'Theme inventory')
    themes = {r['id'] for r in state['themes']}
    decisions = json.loads(file_at(ROOT, state['sources'][0]['path']).read_text())['decisions']
    decisions = {r['candidate_id']: r for r in decisions}
    for row in state['sources'] + state['reviews']:
        require(digest(file_at(ROOT, row['path']).read_bytes()) == row['sha256'], 'Changed evidence: ' + row['path'])
    for row in essays:
        require(row['theme'] in themes and row['question'].endswith('?'), 'Missing topic or question')
        actual = digest(file_at(ROOT, row['text']).read_bytes())
        require(actual == row['text_sha256'], 'Wrong manuscript: ' + row['id'])
        if row['id'] in decisions:
            require(actual == decisions[row['id']]['version']['sha256'], 'Comparison version mismatch')
            require(row['selection_20261019'] == decisions[row['id']]['selection'], 'Decision mismatch')
        require(file_at(ROOT, row['history']).is_file(), 'Missing biography')
    stages = state['stages']
    routes = [stages[k] for k in ['midterm_nine','rescued_six','later_seven']]
    require([len(r) for r in routes] == [9,6,7], 'Route counts')
    require(len(set(sum(routes, []))) == 22 and set(sum(routes, [])) == set(decisions), 'Route membership')
    main_ids = {k for k,v in decisions.items() if v['selection'] == 'main'}
    wildcard_ids = {k for k,v in decisions.items() if v['selection'] == 'wildcard'}
    require(set(stages['reading_main']) == main_ids and len(main_ids) == 8, 'Main selection')
    require(set(stages['reading_wildcards']) == wildcard_ids and len(wildcard_ids) == 2, 'Wildcards')
    require(set(stages['outside_reading_ten']) == set(decisions)-main_ids-wildcard_ids, 'Outside selection')
    trio = json.loads(file_at(ROOT, 'evidence/selection-update/20261101/DECISION.json').read_text())
    require(stages['human_choice'] == trio['selected'] == ['E050','E012','E051'], 'Human choice')
    require('E051' not in decisions and stages['human_return_from_outside_pool'] == ['E051'], 'E051 return route')
    require({r['id'] for r in essays if r['human_choice']} == set(trio['selected']), 'Catalogue flags')
    require(stages['ai_recommendation'] == ['E050','E009','E012'] and stages['ai_reserves'] == ['E078','E041'], 'Historical recommendation')
    require(state['visibility'] == 'private', 'Visibility policy')
    catalogue = file_at(ROOT, 'essays/topics.md').read_text()
    ids = re.findall(r'^\*\*([EFS][0-9]{2,3}) · ', catalogue, re.M)
    require(len(ids) == 107 and set(ids) == expected, 'Catalogue coverage')
    for row in essays:
        require(f'[Working text]({row["text"].removeprefix("essays/")})' in catalogue, 'Catalogue version link')
    imports = json.loads(file_at(ROOT, 'evidence/selection-update/20261101/IMPORT_MANIFEST.json').read_text())
    for row in imports['files']:
        require(digest(file_at(ROOT, row['path']).read_bytes()) == row['sha256'], 'Imported result changed')

    # Restore navigation only in a temporary view; source files remain untouched.
    historical = manifest['historical_verifier']
    require(digest(file_at(ROOT, historical['path']).read_bytes()) == historical['sha256'], 'Prior verifier changed')
    with tempfile.TemporaryDirectory(prefix='philosophy-reading-check-') as directory:
        view = Path(directory).resolve()
        for source in ROOT.rglob('*'):
            relative = source.relative_to(ROOT)
            if '.git' in relative.parts or '__pycache__' in relative.parts:
                continue
            require(not source.is_symlink(), 'Symlink in edition')
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
        for name in manifest['added_files']:
            file_at(view, name).unlink()
        subprocess.run([sys.executable, '-B', str(view / historical['path']),
                        '--manifest-sha256', historical['manifest_sha256']], check=True)

    # The earlier checker predates the thematic page; include it explicitly.
    old_inventory = navigation.editorial_files
    navigation.editorial_files = lambda root: sorted(set(old_inventory(root)) | {root / 'essays/topics.md'})
    result = navigation.check_links(ROOT)
    require(result['status'] == 'PASS', str(result['errors']))
    print(json.dumps({'status':'PASS', 'essays':107, 'themes':10,
                      'selection_pool':22, 'human_choice':stages['human_choice'],
                      'preserved_previous_pages':len(manifest['previous_pages']),
                      'navigation':result}, indent=2))

if __name__ == '__main__':
    main()
