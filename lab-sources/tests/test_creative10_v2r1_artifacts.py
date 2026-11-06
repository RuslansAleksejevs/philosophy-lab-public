"""Synthetic lifecycle regression; native-marker transport is mocked explicitly."""
import json
from types import SimpleNamespace
from unittest.mock import patch
import creative10_v2_artifacts as original
import creative10_v2r1_artifacts as repaired
from test_creative10_v2_artifacts import PreflightTests


class RepairLifecycleTests(PreflightTests):
    def test_original_precheck_then_repaired_review_and_replay(self):
        with self.archive.writer() as w:
            self.setup_archive(w)
            initial=self.bound(w)
            with patch.object(original,'bind_marker',return_value=initial):
                original.precheck(self.root,w,self.start,self.identity,'04',self.args())
            before=[e for e in w.events() if e['kind']=='round.judge_profile']
            self.assertEqual(len(before),1)
            profile=str((self.folder.parent/'NOVELTY_CRITIC.md').relative_to(self.root))
            self.assertEqual(repaired.profile_snapshot(self.root,w,self.start,self.identity,profile,initial)['id'],before[0]['id'])
            # Complete canonical draft and first-critique ancestry without native
            # provider activity; native review marker is represented by fixtures.
            author={'session_id':'author','agent_path':'/root/creative_author_04'}
            original.write_lineage(self.root,w,self.start,author,'04','draft',self.start,[self.folder/'proposal.md'])
            (self.folder/'opponent-task.txt').write_text('Synthetic opponent task')
            critic=w.append(original.rounds.envelope(self.start,'round.stage','opponent',payload={'stage':'critique'}),'first-critic')
            original.write_lineage(self.root,w,self.start,{'session_id':'opponent','agent_path':'/root/creative_opponent_04'},'04','critique1',critic,[self.folder/'report.md'])
            (self.folder/'identity.json').write_text(json.dumps({'session_id':'author','start_event_id':self.start['id']}))
            (self.folder/'contribution.receipt.json').write_text('{}')
            raw=w.append(original.rounds.envelope(self.start,'fixture.raw','critic',payload={'phase':'postdraft'}),'postdraft-raw')
            coverage=w.append(original.rounds.envelope(self.start,'fixture.coverage','critic',payload={'phase':'postdraft'}),'postdraft-coverage')
            bound={'timestamp':'2026-09-22T01:00:00Z','coverage_event_id':coverage['id'],
                   'raw_event_ids':[raw['id']],'run_binding_ids':[]}
            args=SimpleNamespace(command='review',essay='04',agent_path='/root/creative_novelty_04',
                                 file=str((self.folder/'report.md').relative_to(self.root)),profile=profile)
            # Round binding tested separately below. Full second_review capture
            # validation belongs to native capture; this test isolates replay and
            # profile event identity without fabricating actual native records.
            with patch.object(repaired,'discover',return_value=self.identity), \
                 patch.object(repaired.rounds,'start_record',return_value=self.start), \
                 patch.object(repaired,'bind_transport_repair'), \
                 patch.object(repaired,'bind_marker',return_value=bound):
                result=repaired.process(self.root,args,w)
                profiles=[e for e in w.events() if e['kind']=='round.judge_profile']
                self.assertEqual(len(profiles),2)
                self.assertNotEqual(profiles[0]['parents'],profiles[1]['parents'])
                self.assertEqual(repaired.profile_snapshot(self.root,w,self.start,self.identity,profile,bound)['id'],profiles[1]['id'])
                count=len(w.events())
                with patch.object(repaired,'second_review',return_value=(None,None)):
                    self.assertEqual(repaired.process(self.root,args,w),result)
                self.assertEqual(len(w.events()),count)
            self.assertTrue((self.folder/'review2.receipt.json').exists())
            self.assertEqual(len([e for e in w.events() if e['kind']=='round.judge_review']),1)

    def test_transport_repair_requires_original_binding_and_replays(self):
        from research_archive import ArchiveError
        with self.archive.writer() as w:
            self.setup_archive(w)
            scripts=self.root/'scripts';scripts.mkdir()
            notes=self.root/'runs/creative10-20260922';notes.mkdir(parents=True)
            (scripts/'creative10_v2_artifacts.py').write_bytes(b'original synthetic helper')
            (scripts/'creative10_v2r1_artifacts.py').write_bytes(b'repaired synthetic helper')
            (notes/'V2R1_TRANSPORT_REPAIR.md').write_bytes(b'synthetic repair note')
            with self.assertRaises(ArchiveError):repaired.bind_transport_repair(self.root,w,self.start,self.identity)
            self.start['bindings']['input']=[w.put(b'original synthetic helper')]
            first=repaired.bind_transport_repair(self.root,w,self.start,self.identity)
            second=repaired.bind_transport_repair(self.root,w,self.start,self.identity)
            self.assertEqual(first['id'],second['id'])
            self.assertEqual(first['kind'],'round.transport_correction')
