import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import creative10_v2_artifacts as c
import essay_lineage as l
from research_archive import Archive, ArchiveError

class PreflightTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name).resolve()
        self.folder=self.root/c.CAMPAIGN/'essay-04';self.folder.mkdir(parents=True)
        (self.folder.parent/'NOVELTY_CRITIC.md').write_text('Synthetic neutral role')
        (self.folder/'novelty-task.txt').write_text('Synthetic neutral task')
        (self.folder/'proposal.md').write_text('Synthetic proposal bytes')
        (self.folder/'report.md').write_text('Synthetic critique bytes')
        (self.folder/'manifest.json').write_text('[]')
        self.archive=Archive(self.root/'research/archive');self.archive.init()
        self.identity={'session_id':'critic','agent_path':'/root/creative_novelty_04'}
    def tearDown(self):self.tmp.cleanup()
    def setup_archive(self,w):
        self.start=w.append({'kind':'fixture','actor':{'id':'author','role':'AI'},'session_id':'author','run_id':'creative10-04',
            'operation_id':'fixture','attempt_id':'fixture','bindings':{'method':[],'input':[],'config':[],'instruction':[]},'payload':{}},'fixture')
        for label in ['origin','idea','selection']:
            e=l.base_entry(c.lineage_id('04',label),'creative10-20260922/essay-04',label,'Synthetic lineage')
            e['parents']=[c.lineage_id('04',p) for p in c.LINEAGE_PARENTS[label]];e['evidence']=[self.start['id']]
            if label=='selection':e['decision']={'status':'PASS_RELATIVE'}
            l.append(w,e,'author')
        self.author_source(w,'initial')
    def author_source(self,w,tag):
        e=c.rounds.envelope(self.start,'round.source_snapshot','author',payload={})
        e['outputs']=[w.put((self.folder/'proposal.md').read_bytes())]
        w.append(e,'source:'+tag)
    def bound(self,w):
        e=w.append(c.rounds.envelope(self.start,'fixture.raw','critic',payload={}), 'raw')
        cov=w.append(c.rounds.envelope(self.start,'fixture.coverage','critic',payload={}), 'coverage')
        return {'timestamp':'2026-09-22T00:00:00Z','coverage_event_id':cov['id'],'raw_event_ids':[e['id']],'run_binding_ids':[]}
    def args(self,verdict='PASS_RELATIVE',attempt='p1'):
        gate={'verdict':verdict,'proposal_path':str((self.folder/'proposal.md').relative_to(self.root)),
              'proposal_sha256':c.sha((self.folder/'proposal.md').read_bytes()),'concrete_increment':'fixture delta',
              'closest_overlap':'fixture overlap','limitations':'fixture boundary'}
        path=self.folder/('gate-'+attempt+'.json');path.write_text(json.dumps(gate))
        return SimpleNamespace(file=str((self.folder/'report.md').relative_to(self.root)),gate=str(path.relative_to(self.root)),
            manifest=str((self.folder/'manifest.json').relative_to(self.root)),attempt=attempt)
    def test_pass_exact_ancestry_replay_missing_and_tampered_release(self):
        with self.archive.writer() as w:
            self.setup_archive(w);bound=self.bound(w);args=self.args()
            with patch.object(c,'bind_marker',return_value=bound):
                receipt=c.precheck(self.root,w,self.start,self.identity,'04',args)
                self.assertEqual(c.precheck(self.root,w,self.start,self.identity,'04',args),receipt)
            c.validate_release(self.root,w,'04')
            entries=l.index(w.events());entry=entries[c.lineage_id('04','preflight-selection')]['payload']['entry']
            self.assertEqual(entry['parents'],[c.lineage_id('04','selection'),c.lineage_id('04','precheck-p1')])
            draft=c.write_lineage(self.root,w,self.start,{'session_id':'author','agent_path':'/root/creative_author_04'},'04','draft',self.start,[self.folder/'proposal.md'])
            self.assertEqual(draft['payload']['entry']['parents'],[c.lineage_id('04','selection'),c.lineage_id('04','preflight-selection')])
            release=self.folder/'preflight-release.json';original=release.read_bytes();release.unlink()
            with self.assertRaises(OSError):c.validate_release(self.root,w,'04')
            release.write_bytes(original);bad=json.loads(original);bad['selection_event_id']='missing';release.write_text(json.dumps(bad))
            with self.assertRaises(ArchiveError):c.validate_release(self.root,w,'04')
            release.write_bytes(original);(self.folder/'proposal.md').write_text('changed')
            with self.assertRaises(ArchiveError):c.validate_release(self.root,w,'04')
    def test_failure_blocks_draft_and_revised_attempt_needs_new_author_snapshot(self):
        with self.archive.writer() as w:
            self.setup_archive(w);bound=self.bound(w)
            with patch.object(c,'bind_marker',return_value=bound):
                c.precheck(self.root,w,self.start,self.identity,'04',self.args('REVISE'))
                with self.assertRaises(OSError):c.validate_release(self.root,w,'04')
                with self.assertRaises(ArchiveError):c.require_lineage(w,'04',['preflight-selection'])
                with self.assertRaises(ArchiveError):c.write_lineage(self.root,w,self.start,{'session_id':'author','agent_path':'/root/creative_author_04'},'04','draft',self.start,[self.folder/'proposal.md'])
                (self.folder/'proposal.md').write_text('revised synthetic proposal')
                args=self.args('PASS_RELATIVE','p2')
                with self.assertRaises(ArchiveError):c.precheck(self.root,w,self.start,self.identity,'04',args)
                self.author_source(w,'revision')
                result=c.precheck(self.root,w,self.start,self.identity,'04',args)
                self.assertEqual(result['verdict'],'PASS_RELATIVE')
                c.validate_release(self.root,w,'04')
                entries=l.index(w.events())
                self.assertEqual(entries[c.lineage_id('04','precheck-p2')]['payload']['entry']['parents'],
                    [c.lineage_id('04','selection'),c.lineage_id('04','precheck-p1')])

if __name__=='__main__':unittest.main()
