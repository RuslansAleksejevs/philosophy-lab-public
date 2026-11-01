"""Synthetic v3 map to frozen pair-ready helper; no real archive or prose."""
import importlib.util
import sys
import unittest
import bind_pair_ready_repair as B

old_dir = B.RUN / 'pair-ready-handoff-20261018'
sys.path.insert(0, str(old_dir))
spec = importlib.util.spec_from_file_location('synthetic_old_pair_fixture', old_dir / 'test_pair_ready_handoff.py')
old = importlib.util.module_from_spec(spec)
spec.loader.exec_module(old)
sys.path.remove(str(old_dir))


class PairBinderRepair(unittest.TestCase):
    def setUp(self):
        base = old.PairReadyV2Contract()
        base.setUp()
        self.addCleanup(base.doCleanups)
        self.f = f = base.f
        self.coordinator, self.helpers = base.coordinator, base.helpers
        self.resolution = base.resolution
        self.resolution['schema'] = 'selection-capacity-resolution.v3'
        lane = 'runs/final-selection-20261018/capacity-launch-repair-001/'
        refs = {}
        for jid, number in B.TARGETS.items():
            name = 'runs/final-selection-20261018/results/' + jid + '/ARCHIVE_RECEIPT.json'
            receipt = f.A.decode(f.A.read(f.root, name))
            receipt['accepted_attempt'] = number
            f.put(name, receipt)
            event = next(e for e in f.archive.records if e['id'] == receipt['event_id'])
            event['payload']['accepted_attempt'] = number
            refs[jid] = f.put(lane + jid + '/ACCEPTED_ATTEMPTS_RECEIPT.json', {'TEST_ONLY': True, 'logical_job_id': jid})
        self.map_ref = f.put(lane + 'ACCEPTED_ATTEMPTS.v3.json', {'schema': 'selection-capacity-map.v3', 'attempt_map_receipts': refs})
        self.group_ref = f.put(lane + 'ACCEPTED_ATTEMPTS_RECEIPT.json', {'status': 'CAPACITY_REPLACEMENTS_COMPLETE_ARCHIVED', 'event_id': base.event['id'], 'map': self.map_ref})
        self.event = base.event
        self.event['outputs'] = [self.map_ref['sha256'], *(r['sha256'] for r in refs.values())]
        self.resolution['evidence_files'] = [self.map_ref, self.group_ref, *refs.values()]

    def bind(self):
        f = self.f
        return B.build_spec(f.root, f.run, f.spec['preparation'], self.coordinator,
                            self.group_ref, self.resolution, f.archive.records, self.helpers)

    def test_exact003_002_and110_accepted_by_frozen_pair_helper(self):
        f = self.f; f.spec = self.bind()
        self.assertEqual(len(f.spec['individual_review_receipts']), 110)
        self.assertEqual(f.archive.put_count, 0)
        self.assertEqual(len(f.spec['check_events'][0]['artifacts']), 3)
        f.save_spec()
        self.assertEqual(f.accept()['status'], 'SELECTION_INPUTS_ARCHIVED')
        self.assertIn(self.event['id'], f.archive.records[-2]['parents'])

    def test_M12_failed002_cannot_fill_slot(self):
        f = self.f; name = 'runs/final-selection-20261018/results/M12-N2/ARCHIVE_RECEIPT.json'
        receipt = f.A.decode(f.A.read(f.root, name)); receipt['accepted_attempt'] = 2; f.put(name, receipt)
        with self.assertRaisesRegex(ValueError, 'mapped physical attempt'): self.bind()

    def test_map_actual_output_cannot_be_omitted(self):
        self.event['outputs'].pop()
        with self.assertRaisesRegex(ValueError, 'does not bind'): self.bind()
        self.assertEqual(self.f.archive.put_count, 0)

    def test_accept_rechecks_actual_event_before_write(self):
        f = self.f; f.spec = self.bind(); f.save_spec(); f.archive.records.remove(self.event)
        with self.assertRaisesRegex(ValueError, 'Accepted check event absent'): f.accept()
        self.assertEqual((f.archive.put_count, f.archive.append_count), (0, 0))


if __name__ == '__main__': unittest.main(verbosity=2)
