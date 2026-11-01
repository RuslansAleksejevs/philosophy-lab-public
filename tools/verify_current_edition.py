"""Check historical sealed evidence and current navigation without rewriting either."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from check_links import check_links
from verify_evidence_supplement import verify_evidence_supplement

ROOT=Path(__file__).resolve().parents[1]
view=json.loads((ROOT/'evidence/maintenance/20261031/HISTORICAL_VIEW.json').read_text())
with tempfile.TemporaryDirectory(prefix='philosophy-edition-check-') as directory:
    historical=Path(directory)
    # Hard links make the read-only historical view inexpensive. Replacements
    # unlink only that view's entry before copying preserved editorial bytes.
    for source in ROOT.rglob('*'):
        relative=source.relative_to(ROOT)
        if '.git' in relative.parts or '__pycache__' in relative.parts:
            continue
        assert not source.is_symlink(),relative
        if source.is_file():
            target=historical/relative;target.parent.mkdir(parents=True,exist_ok=True)
            try:os.link(source,target)
            except OSError:shutil.copyfile(source,target)
    for row in view['files']:
        for name in ('path','historical_path'):
            assert not Path(row[name]).is_absolute() and '..' not in Path(row[name]).parts
        raw=(ROOT/row['historical_path']).read_bytes()
        assert hashlib.sha256(raw).hexdigest()==row['sha256'],row['path']
        target=historical/row['path'];target.unlink();target.write_bytes(raw)
    subprocess.run([sys.executable,'-B',str(historical/'tools/verify_edition.py')],check=True)
links=check_links(ROOT)
assert links['status']=='PASS',links['errors']
maintenance=json.loads((ROOT/'evidence/maintenance/20261031/CODE_MANIFEST.json').read_text())
for row in maintenance['files']:
    assert not Path(row['path']).is_absolute() and '..' not in Path(row['path']).parts
    raw=(ROOT/row['path']).read_bytes()
    assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['sha256'],row['path']
print(json.dumps({'evidence_supplement':verify_evidence_supplement(ROOT),
                  'maintenance_snapshots':len(maintenance['files']),
                  'current_editorial_links':links['local_links'],'status':'PASS'},indent=2))
