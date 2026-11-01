"""Verify the final release and restore the preceding reading edition in a temporary view.

Read-only, standard library only. No network, model, Git or native logs required.
"""
from pathlib import Path
import argparse, collections, gzip, hashlib, io, json, os, shutil, subprocess, sys, tarfile, tempfile
import check_links as navigation
from verify_recovered_logs import private_check

ROOT=Path(__file__).resolve().parents[1]
MANIFEST='evidence/final-edition/20261101/RELEASE_MANIFEST.json'
BASE='b5bdc88ec2a08950c6cae29732fd87e4662e4004'
def require(ok,why):
    if not ok:raise ValueError(why)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def at(root,name):
    p=Path(name)
    require(not p.is_absolute() and '..' not in p.parts and '.git' not in p.parts and str(p)==name,'Unsafe path')
    return root/p
def load(name):return json.loads(at(ROOT,name).read_bytes())
def bound(row):
    raw=at(ROOT,row['path']).read_bytes()
    require(sha(raw)==row['sha256'] and ('bytes' not in row or len(raw)==row['bytes']),'Changed file: '+row['path'])
    return raw
def message_key(sid,m):return sid,m['source_line'],m['role']
def old_keys(index):
    keys=set();count=0;bundles=collections.defaultdict(list)
    def add(row,raw):
        nonlocal count
        require(sha(raw)==row['conversation_sha256'],'Old conversation changed')
        doc=json.loads(raw)
        for m in doc['messages']:
            k=message_key(row['session_id'],m);require(k not in keys,'Duplicate old message');keys.add(k);count+=1
    for row in index['sessions']:
        if row.get('conversation_archive'):bundles[row['conversation_archive']].append(row)
        else:add(row,at(ROOT,'logs/'+row['conversation']).read_bytes())
    for name,rows in bundles.items():
        with tarfile.open(at(ROOT,'logs/'+name),'r:gz') as tar:
            for row in rows:add(row,tar.extractfile(row['conversation_member']).read())
    return keys,count
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--manifest-sha256');args=parser.parse_args()
    raw=at(ROOT,MANIFEST).read_bytes();manifest=json.loads(raw)
    if args.manifest_sha256:require(sha(raw)==args.manifest_sha256,'Manifest differs from supplied pin')
    require(manifest['base_commit']==BASE,'Wrong predecessor')
    for name,digest in manifest['release_files'].items():require(sha(at(ROOT,name).read_bytes())==digest,'Release file changed: '+name)
    actual=set()
    for p in ROOT.rglob('*'):
        if '.git' in p.parts or '__pycache__' in p.parts:continue
        require(not p.is_symlink(),'Symlink in release')
        if p.is_file():actual.add(str(p.relative_to(ROOT)))
    require(actual==set(manifest['release_files'])|{MANIFEST},'Unlisted or missing release files')
    state=load('docs/release-state.json')
    require(state['selected']==['E050','E012','E051'],'Wrong final three')
    require(state['submission']['basis']=='human_report' and state['submission']['external_receipts_independently_verified'] is False,'Submission boundary')
    for row in state['essays']:
        for key in ['manuscript','pdf','methodology_pdf','abstract','full_review']:bound(row[key])
        if row.get('scoped_review'):bound(row['scoped_review'])
    for row in load('submission/20261101/MANIFEST.json')['files']:bound(row)
    imported=load('evidence/final-edition/20261101/RESEARCH_IMPORT.json')
    bundle=bound(imported['bundle'])
    with tarfile.open(fileobj=io.BytesIO(bundle),mode='r:gz') as tar:
        require(len(tar.getmembers())==imported['bundle']['members'],'Research member count')
        for row in imported['files']+imported['canonical_events']:
            raw=tar.extractfile(row['path']).read();require(sha(raw)==row['sha256'],'Research archive member changed')
            if row['path'].endswith('native-visible.json'):private_check(json.loads(raw),row['path'],hidden=True)
    prefix='logs/updates/20261101-release/'
    idx=load(prefix+'INDEX.json');baseline=json.loads(bound(idx['baseline']))
    keys,count=old_keys(baseline);require(count==15302,'Wrong retained baseline')
    raw=at(ROOT,prefix+idx['bundle']['path']).read_bytes();require(sha(raw)==idx['bundle']['sha256'],'Log bundle hash')
    additions=0;new_sids=set();old_sids={r['session_id'] for r in baseline['sessions']}
    with tarfile.open(fileobj=io.BytesIO(raw),mode='r:gz') as tar:
        require({m.name for m in tar.getmembers()}=={r['member'] for r in idx['sessions']},'Log member inventory')
        for row in idx['sessions']:
            raw=tar.extractfile(row['member']).read();require(sha(raw)==row['sha256'],'Log member hash')
            doc=json.loads(raw);sid=row['session_id'];require(doc['session']['session_id']==sid,'Session identity')
            require(len(doc['messages'])==row['added_messages'],'Added message count')
            for m in doc['messages']:
                require(m['role'] in {'user','assistant'},'Non-visible role')
                if m['role']=='assistant':require(m.get('phase') in {'commentary','final','final_answer'},'Hidden assistant phase')
                require(sha(m['text'].encode())==m['text_sha256'],'Visible text changed')
                private_check(m,sid,hidden=True)
                k=message_key(sid,m);require(k not in keys,'Old message duplicated or conflicting');keys.add(k);additions+=1
            new_sids.add(sid)
    require(additions==idx['added_messages'] and len(keys)==idx['total_visible_messages'],'Log union count')
    require(len(old_sids|new_sids)==idx['total_sessions_in_union'],'Log union sessions')
    cutoff=at(ROOT,prefix+idx['cutoffs']['path']).read_bytes();require(sha(cutoff)==idx['cutoffs']['sha256'],'Cutoff hash')
    reports=json.loads(gzip.decompress(cutoff));require(len(reports)==idx['scanned_native_sources'],'Source inventory')
    require(all(r['previous_prefix_matched'] is True for r in reports if r['previous_prefix_sha256']),'Earlier prefix mismatch')

    historical=manifest['historical_verifier'];bound(historical)
    with tempfile.TemporaryDirectory(prefix='philosophy-final-release-') as directory:
        view=Path(directory)
        for name in actual:
            source=at(ROOT,name);dest=at(view,name);dest.parent.mkdir(parents=True,exist_ok=True)
            try:os.link(source,dest)
            except OSError:shutil.copyfile(source,dest)
        for row in manifest['previous_pages']:
            raw=bound({'path':row['snapshot'],'sha256':row['sha256']});dest=at(view,row['path']);dest.unlink();dest.write_bytes(raw)
        for name in manifest['added_files']:at(view,name).unlink()
        subprocess.run([sys.executable,'-B',str(view/historical['path']),'--manifest-sha256',historical['manifest_sha256']],check=True)
    prior=navigation.editorial_files
    navigation.editorial_files=lambda root:sorted(set(prior(root))|{root/'essays/topics.md'})
    nav=navigation.check_links(ROOT);require(nav['status']=='PASS',str(nav['errors']))
    print(json.dumps({'status':'PASS','release_manifest_sha256':sha(at(ROOT,MANIFEST).read_bytes()),'files':len(actual),
                     'selected':state['selected'],'visible_messages':len(keys),'indexed_sessions':len(old_sids|new_sids),
                     'earlier_pages_preserved':len(manifest['previous_pages']),'navigation':nav},indent=2))
if __name__=='__main__':main()
