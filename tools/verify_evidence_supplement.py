"""Verify the exact accepted preparation supplement using only this repository."""
from pathlib import Path
import hashlib
import json

def verify_evidence_supplement(root):
    root=Path(root)
    prefix=root/'evidence/final-selection/updates/20261031'
    manifest=json.loads((prefix/'MANIFEST.json').read_text())
    imports=manifest['imports']
    paths=set()
    for item in imports:
        path=item['destination']
        assert not Path(path).is_absolute() and '..' not in Path(path).parts,path
        assert path not in paths,path
        paths.add(path)
        raw=(root/path).read_bytes()
        assert len(raw)==item['bytes'] and hashlib.sha256(raw).hexdigest()==item['sha256'],path
    receipt=json.loads((prefix/'preselection/FINAL_RECEIPT.json').read_text())
    assert receipt['status']=='PRESELECTION_COMPLETE_BOUNDED'
    resolution=manifest['accepted_path_resolution']
    assert len(resolution)==manifest['counts']['accepted_preselection_files']==869
    for item in resolution:
        assert item['repository_path'] in paths
        assert hashlib.sha256((root/item['repository_path']).read_bytes()).hexdigest()==item['sha256']
    return {'status':'PASS','exact_imports_checked':len(imports),'accepted_bindings':len(resolution)}

if __name__=='__main__':
    print(json.dumps(verify_evidence_supplement(Path(__file__).resolve().parents[1]),indent=2))
