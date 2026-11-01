"""Verify the retained earlier edition, recovered logs, and current navigation."""
if not __debug__:
    raise SystemExit('Optimized Python is unsupported; integrity assertions must remain enabled')

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

from check_links import check_links

ROOT = Path(__file__).resolve().parents[1]
FINAL_MANIFEST = 'logs/updates/20261031-final-verification/MANIFEST.json'
FINAL_VERIFIER = 'tools/verify_final_log_delta_v3.py'
FINAL_VERIFIER_SHA256 = '50f6a21c397ec655e8f052e5b67641aad517640072a374ba65609b1af31fed72'
TOOL_COVERAGE_MANIFEST_SHA256 = 'ebb0e5944325f8b060e013dde45a6124e1e58426a56f139d3c69396c6d674f82'
TOOL_COVERAGE_FILES = {
    'BUNDLE_AND_INDEX_AUDIT.json', 'EXACT_TOOL_IDENTITIES.json',
    'NATIVE_PREFIX_VERIFICATION.json', 'README.md', 'REPORT.json',
    'SCOPE_CLARIFICATION.json', 'audit.py.source', 'FINAL_RECEIPT.json',
}
ADMINISTRATIVE_PREFIX = 'evidence/repository-audit/20261031/'
ADMINISTRATIVE_PACKAGES = {
    'tool-coverage-followup': {
        'manifest_sha256': 'c7c7880c84cce66ea1fae5cfca73e449c0443322d5ee963a56dc58481b4d254e',
        'path_style': 'package-relative',
    },
    'performance-repair': {'manifest_sha256': '68734b2bb75e27a3e1d36f04953e3a01731bf0d544c49658822f276c394139f3', 'path_style': 'repository-relative'},
    'service-recovery': {'manifest_sha256': '6d788484c631a490c34467470223a3b828adbf18323a24aaa8d42ecff7c7db46', 'path_style': 'repository-relative'},
}


def checked_path(root, name):
    relative = Path(name)
    assert str(relative) == name and not relative.is_absolute() and '..' not in relative.parts, name
    path = root / relative
    current = root
    for part in relative.parts:
        current = current / part
        assert not current.is_symlink(), name
    assert path.is_file(), name
    return path


def log_check_command(root, require_final_delta=False, manifest_sha256=None):
    """Plan the log check, requiring an independently supplied final data hash."""
    final_path = root / FINAL_MANIFEST
    if require_final_delta or manifest_sha256 is not None or final_path.exists() or final_path.is_symlink():
        assert isinstance(manifest_sha256, str) and re.fullmatch('[a-f0-9]{64}', manifest_sha256), \
            'Final delta requires --final-manifest-sha256 with the independently reviewed hash'
        raw = checked_path(root, FINAL_MANIFEST).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == manifest_sha256, 'Final delta manifest hash differs'
        verifier = checked_path(root, FINAL_VERIFIER)
        assert hashlib.sha256(verifier.read_bytes()).hexdigest() == FINAL_VERIFIER_SHA256, 'Final V3 verifier code changed'
        return ([sys.executable, '-B', str(verifier), '--root', str(root),
                 '--manifest', FINAL_MANIFEST, '--manifest-sha256', manifest_sha256], 'FINAL_DELTA_V3')
    return ([sys.executable, '-B', str(checked_path(root, 'tools/verify_recovered_logs.py'))], 'RECOVERED_BASELINE_14939')


def check_tool_coverage(root):
    folder = root / 'evidence/repository-audit/20261031/tool-coverage'
    manifest_path = checked_path(root, 'evidence/repository-audit/20261031/tool-coverage/MANIFEST.json')
    manifest_raw = manifest_path.read_bytes()
    assert hashlib.sha256(manifest_raw).hexdigest() == TOOL_COVERAGE_MANIFEST_SHA256, 'Tool coverage manifest changed'
    manifest = json.loads(manifest_raw)
    assert manifest['status'] == 'EXACT_ADMINISTRATIVE_AUDIT_COPY'
    rows = manifest['files']
    assert len(rows) == len(TOOL_COVERAGE_FILES) and {r['path'] for r in rows} == TOOL_COVERAGE_FILES, \
        'Tool coverage inventory differs'
    for row in rows:
        assert type(row['bytes']) is int and row['bytes'] >= 0
        assert isinstance(row['sha256'], str) and re.fullmatch('[a-f0-9]{64}', row['sha256'])
        raw = checked_path(folder, row['path']).read_bytes()
        assert len(raw) == row['bytes'] and hashlib.sha256(raw).hexdigest() == row['sha256'], row['path']
    return {'files': len(rows), 'manifest_sha256': hashlib.sha256(manifest_raw).hexdigest()}


def check_administrative_package(root, package):
    """Check only an explicitly pinned package; unknown final hashes fail closed."""
    assert package in ADMINISTRATIVE_PACKAGES, 'Unknown administrative package'
    spec = ADMINISTRATIVE_PACKAGES[package]
    digest = spec['manifest_sha256']
    assert isinstance(digest, str) and re.fullmatch('[a-f0-9]{64}', digest), \
        'Pending independently reviewed administrative manifest hash: ' + package
    root = Path(root).absolute()
    assert root.is_dir() and not any(p.is_symlink() for p in (root, *root.parents)), \
        'Symlink in administrative root'
    prefix = ADMINISTRATIVE_PREFIX + package + '/'
    manifest_name = prefix + 'MANIFEST.json'
    raw = checked_path(root, manifest_name).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == digest, 'Administrative manifest hash differs: ' + package
    def unique_object(pairs):
        value = {}
        for key, item in pairs:
            assert key not in value, 'Duplicate administrative JSON key'
            value[key] = item
        return value
    def invalid_constant(value):
        raise AssertionError('Nonfinite administrative JSON value')
    manifest = json.loads(raw, object_pairs_hook=unique_object, parse_constant=invalid_constant)
    assert isinstance(manifest, dict) and isinstance(manifest.get('files'), list) and manifest['files'], \
        'Administrative package needs a nonempty file inventory'
    seen = set()
    for row in manifest['files']:
        assert isinstance(row, dict) and {'path', 'sha256', 'bytes'} <= set(row), 'Invalid administrative file descriptor'
        name = row['path']
        assert isinstance(name, str) and name and str(Path(name)) == name \
            and not Path(name).is_absolute() and '..' not in Path(name).parts, 'Invalid administrative path'
        if spec['path_style'] == 'package-relative':
            name = prefix + name
        else:
            assert spec['path_style'] == 'repository-relative', 'Unknown administrative path style'
        assert name.startswith(prefix) and name != manifest_name, 'Administrative path escapes its package or references its manifest'
        assert name not in seen, 'Duplicate administrative file path'
        seen.add(name)
        assert type(row['bytes']) is int and row['bytes'] >= 0, 'Invalid administrative byte count'
        assert isinstance(row['sha256'], str) and re.fullmatch('[a-f0-9]{64}', row['sha256']), 'Invalid administrative file hash'
        data = checked_path(root, name).read_bytes()
        assert len(data) == row['bytes'] and hashlib.sha256(data).hexdigest() == row['sha256'], name
    return {'files': len(seen), 'manifest_sha256': digest}


def check_administrative_packages(root):
    # Resolve every reviewed pin before any edition subprocess or expensive audit.
    for package, spec in ADMINISTRATIVE_PACKAGES.items():
        digest = spec['manifest_sha256']
        assert isinstance(digest, str) and re.fullmatch('[a-f0-9]{64}', digest), \
            'Pending independently reviewed administrative manifest hash: ' + package
    return {name: check_administrative_package(root, name) for name in ADMINISTRATIVE_PACKAGES}


def check_readable_verification(root, manifest_sha256):
    """After V3 passes, bind every readable copy to its verified bundle member."""
    final_raw = checked_path(root, FINAL_MANIFEST).read_bytes()
    assert hashlib.sha256(final_raw).hexdigest() == manifest_sha256, 'Final manifest changed after verification'
    final = json.loads(final_raw)
    members = final['safe_artifacts_bundle']['members']
    sources = {row['path']: row for row in members}
    assert len(sources) == len(members), 'Duplicate final artifact member'
    prefix = 'evidence/deep-verification/20261031/'
    run = 'runs/deep-verification-20261031/'
    jobs = {f'V{i:02d}-{role}' for i in range(1, 11) for role in ('A', 'L')}
    accepted = {row['job_id']: row for row in final['accepted_scientific']}
    assert set(accepted) == jobs and len(final['accepted_scientific']) == 20
    fixed = {prefix + 'coordinator/' + name: run + 'coordinator-synthesis/' + name for name in
             ('SOURCE_LEDGER.json', 'CONTRIBUTION_MATRIX.json', 'DECISION.json', 'FIVE_CARDS.json', 'CHECKPOINT_SUMMARY.json')}
    fixed.update({prefix + name: run + 'closure/' + name for name in ('REQUEST.json', 'CAPTURE_PLAN.json')})
    fixed[prefix + 'FINAL_RECEIPT.json'] = run + 'FINAL_RECEIPT.json'
    fixed.update({prefix + 'PROTOCOL_NOTE.md': run + 'closure-preparation/PROTOCOL_NOTE.md',
                  prefix + 'METHOD.json': run + 'METHOD.json', prefix + 'input-manifest.json': run + 'MANIFEST.json'})
    expected = set(fixed) | {prefix + group + '/' + job + '.json' for group in ('reports', 'receipts') for job in jobs}
    raw = checked_path(root, prefix + 'manifest.json').read_bytes()
    manifest = json.loads(raw)
    assert manifest['schema'] == 'readable-verification-evidence.v1'
    assert manifest['status'] == 'EXACT_COPIES_OF_ACCEPTED_VERIFICATION_EVIDENCE'
    assert manifest['closure_event_id'] == final['coordinator']['archive_event_id']
    assert type(manifest['scientific_roles']) is int and manifest['scientific_roles'] == 20
    assert type(manifest['new_scientific_roles_from_this_copy']) is int and manifest['new_scientific_roles_from_this_copy'] == 0
    rows = manifest['files']
    assert len(rows) == 51 and {row['path'] for row in rows} == expected, 'Readable evidence must contain the exact51 files'
    indexed = {row['path']: row for row in rows}
    for row in rows:
        assert set(row) == {'path', 'source_path', 'sha256', 'bytes', 'canonical_event_id'}
        source = sources.get(row['source_path'])
        assert source is not None and all(row[k] == source[k] for k in ('sha256', 'bytes')), 'Readable source is not an exact verified artifact member'
        copy_raw = checked_path(root, row['path']).read_bytes()
        assert type(row['bytes']) is int and len(copy_raw) == row['bytes'] and hashlib.sha256(copy_raw).hexdigest() == row['sha256'], row['path']
        if row['path'] in fixed:
            assert row['source_path'] == fixed[row['path']], 'Readable fixed source path differs'
            expected_event = None if row['path'] in {prefix + 'METHOD.json', prefix + 'input-manifest.json'} else manifest['closure_event_id']
            assert row['canonical_event_id'] == expected_event
    for job in sorted(jobs):
        receipt_row = indexed[prefix + 'receipts/' + job + '.json']
        report_row = indexed[prefix + 'reports/' + job + '.json']
        expected_event = accepted[job]['archive_event_id']
        assert receipt_row['source_path'] == run + 'results/' + job + '/ARCHIVE_RECEIPT.json'
        receipt = json.loads(checked_path(root, receipt_row['path']).read_bytes())
        assert receipt['status'] == 'DEEP_VERIFICATION_RESULT_ARCHIVED' and receipt['job_id'] == job and receipt['event_id'] == expected_event
        assert receipt_row['canonical_event_id'] == report_row['canonical_event_id'] == expected_event
        assert report_row['source_path'].startswith(run + 'results/' + job + '/') and Path(report_row['source_path']).name == 'response.json'
        assert any(all(ref[k] == report_row[{'path': 'source_path'}.get(k, k)] for k in ('path', 'sha256', 'bytes'))
                   for ref in receipt['files']), 'Readable report is not bound by its own accepted receipt'
    return {'files': len(rows), 'manifest_sha256': hashlib.sha256(raw).hexdigest()}


def historical_view(destination):
    view = json.loads((ROOT / 'evidence/repository-audit/20261031/HISTORICAL_VIEW.json').read_text())
    assert view['base_commit'] == '6f3748923631d43945a9ea03909e56b867a5ef0c'
    for source in ROOT.rglob('*'):
        relative = source.relative_to(ROOT)
        if '.git' in relative.parts or '__pycache__' in relative.parts:
            continue
        assert not source.is_symlink(), relative
        if source.is_file():
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            try:
                os.link(source, target)
            except OSError:
                shutil.copyfile(source, target)
    seen = set()
    for row in view['files']:
        assert row['path'] not in seen, row['path']
        seen.add(row['path'])
        raw = checked_path(ROOT, row['historical_path']).read_bytes()
        assert len(raw) == row['bytes'] and hashlib.sha256(raw).hexdigest() == row['sha256']
        target = checked_path(destination, row['path'])
        target.unlink()
        target.write_bytes(raw)
    return len(seen)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--require-final-delta', action='store_true',
                        help='Fail if the accepted final delta or its pinned V3 verifier is absent')
    parser.add_argument('--final-manifest-sha256',
                        help='Independently reviewed SHA-256 of the final export manifest')
    args = parser.parse_args(argv)
    administrative = check_administrative_packages(ROOT)
    log_command, log_mode = log_check_command(ROOT, args.require_final_delta, args.final_manifest_sha256)
    tool_coverage = check_tool_coverage(ROOT)
    with tempfile.TemporaryDirectory(prefix='philosophy-rebuilt-check-') as name:
        previous = Path(name)
        count = historical_view(previous)
        subprocess.run([sys.executable, '-B', str(previous / 'tools/verify_current_edition.py')], check=True)
    subprocess.run(log_command, check=True)
    readable = check_readable_verification(ROOT, args.final_manifest_sha256) if log_mode == 'FINAL_DELTA_V3' else None
    links = check_links(ROOT)
    assert links['status'] == 'PASS', links['errors']
    history = json.loads((ROOT / 'evidence/repository-audit/20261031/history/milestones.json').read_text())
    assert history['display_timezone'] == 'America/Los_Angeles'
    assert history['earliest_preserved_source']['source_timestamp'] == '2026-09-07T20:08:33.758Z'
    repair = json.loads((ROOT / 'evidence/repository-audit/20261031/parser-repair/MANIFEST.json').read_text())
    for row in repair['files']:
        raw = checked_path(ROOT, row['path']).read_bytes()
        assert len(raw) == row['bytes'] and hashlib.sha256(raw).hexdigest() == row['sha256'], row['path']
    history_manifest = json.loads((ROOT / 'evidence/repository-audit/20261031/history/MANIFEST.json').read_text())
    gap_root = ROOT / 'evidence/repository-audit/20261031/gap-review'
    gaps = json.loads((gap_root / 'MANIFEST.json').read_text())
    for source_root, manifest in [(ROOT, history_manifest), (gap_root, gaps)]:
        for row in manifest['files']:
            raw = checked_path(source_root, row['path']).read_bytes()
            assert len(raw) == row['bytes'] and hashlib.sha256(raw).hexdigest() == row['sha256'], row['path']
    print(json.dumps({'status': 'PASS', 'preserved_predecessor_files': count,
                      'current_log_check': log_mode,
                      'final_delta_required': args.require_final_delta,
                      'tool_coverage_files': tool_coverage['files'],
                      'tool_coverage_manifest_sha256': tool_coverage['manifest_sha256'],
                      'administrative_packages': administrative,
                      'readable_verification': readable,
                      'current_editorial_links': links['local_links'],
                      'history_source_index': 'PASS', 'history_files': len(history_manifest['files']),
                      'classified_gap_files': len(gaps['files']),
                      'parser_repair_snapshots': len(repair['files'])}, indent=2))


if __name__ == '__main__':
    main()
