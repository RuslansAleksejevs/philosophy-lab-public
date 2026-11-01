"""Verify the repository's originals, quoted prompts, and lossless log bundles.

Run from any directory with Python 3. No network or extra packages are required.
This checks integrity, not philosophical truth or translation quality.
"""
from pathlib import Path
from collections import Counter
import hashlib,json,tarfile,datetime
from zoneinfo import ZoneInfo
from check_links import check_links
from quote_sources import load_quote_message
from timeline_sources import load_timeline_message
from selection_checks import verify_selection_update

ROOT=Path(__file__).resolve().parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
def read(p):return json.loads((ROOT/p).read_text())

essays=read('essays/manifest.json')
assert len(essays['corpus'])==100
for row in essays['corpus']:
    base=ROOT/'essays'/row['id']
    assert sha((base/'original.md').read_bytes())==row['original_sha256'],row['id']
    bio=json.loads((base/'biography.json').read_text())
    assert len(bio['entries'])==row['biography_entries']
    for version in row['versions']:
        assert sha((ROOT/version['path']).read_bytes())==version['sha256']
    if row['english_translation']:
        assert (base/row['english_translation']).is_file()
for row in essays['midterm_revisions']:
    assert sha((ROOT/row['export_path']).read_bytes())==row['sha256']
for row in essays['in_progress']:
    assert sha((ROOT/row['path']).read_bytes())==row['sha256']
for row in essays['set_aside']:
    for f in row['files']:
        assert sha((ROOT/row['path']/f['name']).read_bytes())==f['sha256']
for row in essays.get('post_midterm_completed',[]):
    for f in row['files']:
        assert sha((ROOT/f['path']).read_bytes())==f['sha256'],f['path']
    assert datetime.datetime.fromisoformat(row['release_at']).astimezone(ZoneInfo('America/Los_Angeles')).date().isoformat()==row['release_date_local']

quotes=read('docs/quotes.json')['quotes']
for q in quotes:
    m=load_quote_message(ROOT,q)
    assert m['role']=='user'
    assert sha(m['text'].encode())==q['source_message_sha256']
    assert m['text'][q['start_character']:q['end_character']]==q['original_ru']
    timestamp=m.get('source_timestamp') or m.get('timestamp')
    assert q['source_timestamp']==timestamp
    assert datetime.datetime.fromisoformat(timestamp.replace('Z','+00:00')).astimezone(ZoneInfo(q['display_timezone'])).date().isoformat()==q['date_local']

member_count=0;message_count=0;bundled={};all_snapshot_messages=0;historical_unhashed_messages=0
bundles=read('logs/bundles/manifest.json')['bundles']
assert {str(p.relative_to(ROOT/'logs')) for p in (ROOT/'logs/bundles').glob('*.tar.gz')}=={b['path'] for b in bundles}
for b in bundles:
    path=ROOT/'logs'/b['path']
    assert sha(path.read_bytes())==b['sha256'],b['path']
    expected={m['path']:m for m in b['members']}
    with tarfile.open(path,'r:gz') as t:
        assert set(t.getnames())==set(expected)
        for m in t:
            assert m.isfile() and not m.name.startswith('/') and '..' not in Path(m.name).parts
            raw=t.extractfile(m).read();assert sha(raw)==expected[m.name]['sha256']
            assert len(raw)==expected[m.name]['bytes'];member_count+=1
            if m.name.endswith('/conversation.json'):
                d=json.loads(raw);bundled[(m.name,sha(raw))]=d
                for item in d['messages']:
                    # Historical collector projections can precede this derived field.
                    # Their complete file bytes are still checked against the bundle manifest.
                    if 'text_sha256' in item:
                        assert sha(item['text'].encode())==item['text_sha256']
                    else:
                        historical_unhashed_messages+=1
                    all_snapshot_messages+=1
for s in read('logs/index.json')['sessions']:
    if s['lane']=='chats':
        raw=(ROOT/'logs'/s['conversation']).read_bytes()
        assert sha(raw)==s['conversation_sha256']
        d=json.loads(raw);rendered=(ROOT/'logs'/s['readable']).read_text()
        for m in d['messages']:
            assert sha(m['text'].encode())==m['text_sha256']
            assert m['text'] in rendered
            message_count+=1
    else:
        d=bundled[(s['conversation_member'],s['conversation_sha256'])]
        message_count+=len(d['messages'])
    # Every current projection must carry an independently recomputable text hash,
    # even when the unchanged historical source had no such derived field.
    for m in d['messages']:
        assert sha(m['text'].encode())==m['text_sha256'],(s['session_id'],m.get('source_line'))
    timestamps=[m.get('source_timestamp') or m.get('timestamp') for m in d['messages']]
    assert s['dates']['timestamped_messages']==sum(t is not None for t in timestamps)
    assert s['dates']['undated_messages']==sum(t is None for t in timestamps)
    for key in ['first','last']:
        original=s['dates'][key+'_message_at'];shown=s['dates'][key+'_message_local']
        if original:
            assert datetime.datetime.fromisoformat(original.replace('Z','+00:00')).astimezone(ZoneInfo(s['dates']['display_timezone'])).isoformat()==shown
    assert len(d['messages'])==sum(s['counts'].values())
claude_messages=0
for row in read('logs/claude/index.json').get('direct_post_midterm_conversations',[]):
    raw=(ROOT/'logs'/row['conversation']).read_bytes();assert sha(raw)==row['sha256']
    d=json.loads(raw);rendered=(ROOT/'logs'/row['readable']).read_text()
    for m in d['messages']:
        assert sha(m['text'].encode())==m['text_sha256'] and m['text'] in rendered
        assert m['source_timestamp']
        claude_messages+=1
timeline=read('docs/timeline.json')
for e in timeline['events']:
    assert datetime.datetime.fromisoformat(e['source_timestamp'].replace('Z','+00:00')).astimezone(ZoneInfo(timeline['display_timezone'])).date().isoformat()==e['date_local']
    source=e['source']
    if {'session_id','source_line','text_sha256'} <= source.keys():
        message=load_timeline_message(ROOT,e)
        assert message['role']=='user' and sha(message['text'].encode())==source['text_sha256'],e['id']
        assert (message.get('source_timestamp') or message.get('timestamp'))==e['source_timestamp'],e['id']

selection=read('evidence/final-selection/manifest.json')
for row in selection['files']:
    raw=(ROOT/row['path']).read_bytes()
    assert len(raw)==row['bytes'] and sha(raw)==row['sha256'],row['path']
    if row['transformation']=='unchanged bytes':
        assert sha(raw)==row['source_sha256']
for version in selection['versions']:
    raw=(ROOT/version['repository_path']).read_bytes()
    assert sha(raw)==version['source_sha256'] and len(raw)==version['bytes'],version['repository_path']
current=read('evidence/final-selection/current/decisions.json')
initial=read('evidence/final-selection/initial/decisions.json')
assert current['candidate_count']==22
assert len({row['id'] for row in current['candidates']})==22
assert Counter(row['decision'] for row in current['candidates'])=={'keep':13,'revise':9}
assert current['counts']=={'keep':13,'revise':9,'defer':0}
assert current['changed_decisions']==['E086']
assert current['step2_started'] is False and current['manuscript_edits'] is False
version_keys={(v['id'],v['variant']):v for v in selection['versions']}
for candidate in current['candidates']:
    for version in candidate['versions']:
        exported=version_keys[(candidate['id'],version['variant'])]
        assert exported['source_sha256']==version['sha256']
        assert exported['current']==version['current']
for event_info in selection['source_events']:
    event=read(event_info['repository_path'])
    assert event['id']==event_info['event_id'] and event['sha256']==event_info['event_sha256']
    assert event['recorded_at']==event_info['recorded_at']
    receipt=read(str(Path(event_info['repository_path']).parent/'FINAL_RECEIPT.json'))
    assert receipt['event_id']==event['id'] and receipt['event_sha256']==event['sha256']

verify_selection_update(ROOT)

links=check_links(ROOT)
assert links['status']=='PASS',json.dumps(links['errors'],ensure_ascii=False)
print(json.dumps({'original_manuscripts':100,'post_midterm_completed_essays':len(essays.get('post_midterm_completed',[])),'verified_quotations_and_dates':len(quotes),'verified_timeline_dates':len(timeline['events']),'verified_bundle_members':member_count,'current_codex_messages':message_count,'new_direct_claude_visible_messages':claude_messages,'historical_messages_without_derived_text_hash':historical_unhashed_messages,'selection_candidates':len(current['candidates']),'selection_versions_verified':len(selection['versions']),'selection_evidence_files_verified':len(selection['files']),'editorial_local_links':links['local_links'],'editorial_anchors':links['anchors_checked'],'status':'PASS'},indent=2))
