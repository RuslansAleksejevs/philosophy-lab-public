import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import creative10_artifacts as c
from research_archive import Archive, ArchiveError
import essay_lineage as l


class CreativeGates(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name).resolve()
        self.directory = self.root / c.CAMPAIGN / 'essay-01'
        self.directory.mkdir(parents=True)
    def tearDown(self):
        self.tmp.cleanup()
    def gate(self):
        (self.directory/'query.txt').write_text('synthetic query evidence')
        (self.directory/'work.txt').write_text('synthetic source excerpt')
        manifest = [{'path':'query.txt','read_status':'full'}, {'path':'work.txt','read_status':'excerpt'}]
        (self.directory/'source-manifest.json').write_text(json.dumps(manifest))
        g = {'status':'PASS_RELATIVE','closest_works':[{'citation':'fixture','shared_claim':'overlap','difference':'difference','evidence_path':'work.txt'}],
             'limitations':'Synthetic bounded test only','query_log_path':'query.txt',
             'source_manifest_sha256':c.sha((self.directory/'source-manifest.json').read_bytes())}
        (self.directory/'novelty-gate.json').write_text(json.dumps(g))
        return g
    def test_gate_rejects_failed_status_unbound_comparison_and_changed_manifest(self):
        g=self.gate()
        self.assertEqual(c.novelty_gate(self.root,'01')['status'],'PASS_RELATIVE')
        for key,value in [('status','FAIL'),('closest_works',[]),('source_manifest_sha256','0'*64),('query_log_path','missing')]:
            bad=dict(g);bad[key]=value
            (self.directory/'novelty-gate.json').write_text(json.dumps(bad))
            with self.assertRaises(ArchiveError):c.novelty_gate(self.root,'01')
        g['closest_works'][0]['evidence_path']='not-in-manifest'
        (self.directory/'novelty-gate.json').write_text(json.dumps(g))
        with self.assertRaises(ArchiveError):c.novelty_gate(self.root,'01')
    def test_missing_lineage_blocks_and_final_retains_both_critics_and_original(self):
        archive=Archive(self.root/'research/archive');archive.init()
        with archive.writer() as w:
            with self.assertRaises(ArchiveError):c.require_lineage(w,'01',['selection'])
            evidence=w.append({'kind':'fixture','actor':{'id':'fixture','role':'tool'},'session_id':'synthetic','run_id':'synthetic','operation_id':'synthetic','attempt_id':'one','payload':{}},'fixture')
            for label,parents in c.LINEAGE_PARENTS.items():
                e=l.base_entry(c.lineage_id('01',label),'creative10-20260922/essay-01','critique' if label.startswith('critique') else label,'Synthetic test')
                e['parents']=[c.lineage_id('01',p) for p in parents];e['evidence']=[evidence['id']]
                if label=='selection':e['decision']={'status':'PASS_RELATIVE'}
                l.append(w,e,'synthetic')
                c.require_lineage(w,'01',[label])
            final=l.index(w.events())[c.lineage_id('01','final')]['payload']['entry']
            self.assertEqual(final['parents'],[c.lineage_id('01',p) for p in ['draft','critique1','critique2','revision']])
            filtered=[e for e in w.events() if e.get('payload',{}).get('entry',{}).get('id')!=c.lineage_id('01','selection')]
            with patch.object(w,'events',return_value=filtered):
                with self.assertRaises((ArchiveError,ValueError)):c.require_lineage(w,'01',['final'])

if __name__=='__main__':unittest.main()
