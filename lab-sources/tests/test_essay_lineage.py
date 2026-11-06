import copy
import json
import tempfile
import unittest
from pathlib import Path
from research_archive import Archive
import essay_lineage as l


class LineageTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name).resolve()
        self.archive=Archive(self.root/'research/archive');self.archive.init()
    def tearDown(self):self.temp.cleanup()
    def origin(self,w):
        e=l.base_entry('origin-a','test/essay-01','origin','Exact neutral request')
        e['artifacts']=[{'path':'request.txt','sha256':w.put(b'neutral request'),'role':'prompt'}]
        return e,l.append(w,e,'test-session')
    def test_render_native_and_cli_model_observations(self):
        with self.archive.writer() as w:
            entry=l.base_entry('native-origin','test/native','origin','Native observations')
            entry['configuration']['observed']={'observations':[
                {'status':'known','value':{'model':'astra-fixture','reasoning_effort':'medium'}},
                {'model':'opus-fixture','effort':'xhigh'}]}
            l.append(w,entry,'test-session')
            l.render(self.root,w)
        body=(self.root/'research/biographies/test/native/BIOGRAPHY.md').read_text()
        self.assertIn('astra-fixture / medium',body)
        self.assertIn('opus-fixture / xhigh',body)
        self.assertNotIn('None / None',body)
    def test_append_replay_conflict_missing_parent_and_immutable_version(self):
        with self.archive.writer() as w:
            origin,event=self.origin(w)
            self.assertEqual(l.append(w,origin,'test-session')['id'],event['id'])
            changed=copy.deepcopy(origin);changed['summary']='changed'
            with self.assertRaises(ValueError):l.append(w,changed,'test-session')
            draft=l.base_entry('draft-a','test/essay-01','draft','draft');draft['parents']=['missing']
            with self.assertRaises(ValueError):l.append(w,draft,'test-session')
            draft['parents']=['origin-a'];draft['artifacts']=[{'path':'draft.md','sha256':w.put(b'v1'),'role':'draft'}]
            l.append(w,draft,'test-session')
            self.assertEqual(w.get(draft['artifacts'][0]['sha256']),b'v1')
            l.render(self.root,w)
        self.assertTrue((self.root/'research/biographies/test/essay-01/BIOGRAPHY.md').exists())
    def test_tournament_binds_both_versions_and_rejects_wrong_version(self):
        with self.archive.writer() as w:
            origin,_=self.origin(w)
            for i in ['a','b']:
                e=l.base_entry('draft-'+i,'test/essay-'+i,'draft','draft');e['parents']=['origin-a']
                e['artifacts']=[{'path':'draft.md','sha256':w.put(i.encode()),'role':'draft'}];l.append(w,e,'test-session')
            e=l.base_entry('match-1','test/essay-a','tournament','blind match');e['parents']=['draft-a','draft-b']
            e['assessment']={'versions':[{'entry_id':'draft-'+i,'sha256':l.digest(i.encode())} for i in ['a','b']],
              'judge':{'requested':{'model':'fixture','effort':'low'},'observed':'UNKNOWN'},
              'rubric_sha256':w.put(b'rubric'),'prompt_sha256':w.put(b'prompt'),
              'order':['draft-b','draft-a'],'verdict':'tie','rationale':'different strengths','round':'midterm-1'}
            bad=copy.deepcopy(e);bad['assessment']['versions'][0]['sha256']=w.put(b'newer-version')
            with self.assertRaises(ValueError):l.append(w,bad,'test-session')
            l.append(w,e,'test-session');l.render(self.root,w)
            saved=json.loads((self.root/'research/biographies/test/essay-a/biography.json').read_text())
            self.assertEqual(saved['entries'][-1]['assessment']['verdict'],'tie')
            other=json.loads((self.root/'research/biographies/test/essay-b/biography.json').read_text())
            self.assertEqual(other['entries'][-1]['id'],'match-1')
    def test_legacy_refresh_keeps_versions_and_does_not_invent_settings(self):
        folder=self.root/'research/campaigns/test/essay-01';folder.mkdir(parents=True)
        (folder/'draft.md').write_text('first');(folder/'HISTORY.md').write_text('old history')
        with self.archive.writer() as w:
            l.backfill(self.root,w,'test-session');l.backfill(self.root,w,'test-session')
            self.assertEqual(len(l.index(w.events())),1)
            (folder/'draft.md').write_text('second');l.backfill(self.root,w,'test-session')
            entries=list(l.index(w.events()).values());self.assertEqual(len(entries),2)
            self.assertEqual(entries[-1]['payload']['entry']['configuration']['observed'],'UNKNOWN')
            self.assertEqual(len(entries[-1]['payload']['entry']['parents']),1)
            self.assertEqual((folder/'HISTORY.md').read_text(),'old history')
    def test_cli_import_records_pause_resume_settings_and_is_idempotent(self):
        p=self.root/'collection';(p/'records').mkdir(parents=True);(p/'objects').mkdir()
        m={'id':'packet','purpose':'research','protocol':'fixture','input_hashes':{},'tasks':[
           {'id':'essay-01-author','essay_id':'essay-01','model':'opus','effort':'xhigh','role':'author'}]}
        (p/'manifest.json').write_text(json.dumps(m))
        for n,a in enumerate(['attempt-1','attempt-2']):
            items=[{'kind':'attempt.started','session_id':'same-session','requested':{'model':'opus','effort':'xhigh'},'prompt':'continue'},
                   {'kind':'native.observations','report':{'observations':[{'model':'opus','effort':'xhigh'}]}},
                   {'kind':'attempt.finished','status':'paused' if n==0 else 'done','reason':'quota' if n==0 else 'accepted_files','outputs':{}}]
            for j,r in enumerate(items):
                r.update(attempt=a,task='essay-01-author',at=f'2026-09-21T00:0{n}:{j}0+00:00')
                (p/'records'/f'{n}-{j}.json').write_text(json.dumps(r))
        receipt={'files':{str(f.relative_to(p)):l.digest(f.read_bytes()) for f in p.rglob('*') if f.is_file()}}
        (p/'collection.json').write_bytes(l.canonical(receipt))
        with self.archive.writer() as w:
            self.origin(w);l.bind_packet(w,'packet','test','test-session')
            intake=w.append({'kind':'bridge.cli.collection','actor':{'id':'fixture','role':'tool'},'session_id':'test-session','run_id':'fixture',
                'operation_id':'fixture-intake','attempt_id':'one','payload':{'collection_sha256':l.digest((p/'collection.json').read_bytes())}},'fixture-intake')
            self.assertEqual(len(l.ingest_cli(w,p,intake,'test-session')),3)
            self.assertEqual(l.ingest_cli(w,p,intake,'test-session'),[])
            entries=[e['payload']['entry'] for e in l.index(w.events()).values() if e['payload']['entry']['kind']=='cli_attempt']
            self.assertIn(entries[0]['id'],entries[1]['parents'])
            self.assertTrue(any(x.startswith('cli-origin:') for x in entries[1]['parents']))
            self.assertEqual(entries[0]['attempt']['reason'],'quota')
            self.assertEqual(entries[1]['configuration']['observed']['observations'][0]['effort'],'xhigh')
            (p/'records/0-0.json').write_text('{}')
            with self.assertRaises(ValueError):l.ingest_cli(w,p,intake,'test-session')
