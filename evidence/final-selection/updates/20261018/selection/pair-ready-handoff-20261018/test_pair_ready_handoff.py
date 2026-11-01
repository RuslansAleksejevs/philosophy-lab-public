"""Synthetic logical-receipt integration only; fake writer, no real archive."""
from pathlib import Path
import importlib.util
import unittest
import bind_pair_ready as B


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


baseline = module("frozen_pair_ready_tests", B.HELPER.with_name("test_archive_pair_ready.py"))


class PairReadyV2Contract(unittest.TestCase):
    def setUp(self):
        self.f = baseline.PairReady(methodName="test_local_check_writes_nothing")
        self.f.setUp()
        self.addCleanup(self.f.tearDown)
        f = self.f
        self.coordinator = f.spec["coordinator_artifacts"]
        self.helpers = f.spec["helper_inputs"]
        lane = "runs/final-selection-20261018/capacity-resume-20261018/replacement-v2/"
        maps, exceptions = {}, {}
        for jid in sorted(B.EXCEPTIONS):
            name = "runs/final-selection-20261018/results/" + jid + "/ARCHIVE_RECEIPT.json"
            receipt = f.A.decode(f.A.read(f.root, name))
            receipt.update(accepted_attempt=2, session_id="TEST_ONLY_REPLACEMENT_" + jid)
            f.put(name, receipt)
            event = next(e for e in f.archive.records if e["id"] == receipt["event_id"])
            event["session_id"] = receipt["session_id"]
            event["payload"]["accepted_attempt"] = 2
            maps[jid] = f.put(lane + jid + "/ACCEPTED_ATTEMPTS_RECEIPT.json", {"TEST_ONLY": True, "logical_job_id": jid})
            exceptions[jid] = {"accepted_attempt": {"event_id": receipt["event_id"], "session_id": receipt["session_id"]}, "failed_attempt": {"session_id": "TEST_ONLY_FAILED_" + jid}}
        self.map_ref = f.put(lane + "ACCEPTED_ATTEMPTS.v2.json", {"schema": "selection-capacity-map.v2", "attempt_map_receipts": maps})
        self.group_ref = f.put(lane + "ACCEPTED_ATTEMPTS_RECEIPT.json", {"status": "CAPACITY_REPLACEMENTS_COMPLETE_ARCHIVED", "event_id": "TEST_ONLY_GROUP_MAP", "map": self.map_ref})
        self.event = {"id": "TEST_ONLY_GROUP_MAP", "kind": "research.selection.capacity_replacements.accepted", "run_id": f.run.name, "payload": {"status": "CAPACITY_REPLACEMENTS_COMPLETE_ARCHIVED"}, "outputs": [self.map_ref["sha256"], *(x["sha256"] for x in maps.values())]}
        f.archive.records.append(self.event)
        # Fake already-verified resolver boundary. Full resolver's real checks
        # remain covered by frozen replacement-v2/test_capacity_v2.py.
        self.resolution = {"schema": "selection-capacity-resolution.v2", "input_event_id": "TEST_ONLY_OLD_READY", "map_event_id": self.event["id"], "exceptions": exceptions, "evidence_files": [self.map_ref, self.group_ref, *maps.values()]}

    def bind(self):
        f = self.f
        return B.build_spec(f.root, f.run, f.spec["preparation"], self.coordinator,
                            self.group_ref, self.resolution, f.archive.records, self.helpers)

    def test_110_logical_receipts_and_two_002_are_accepted_by_frozen_helper(self):
        f = self.f
        f.spec = self.bind()
        self.assertEqual(len(f.spec["individual_review_receipts"]), 110)
        self.assertEqual(f.archive.put_count, 0)
        check = f.spec["check_events"][0]
        self.assertEqual(len(check["artifacts"]), 3)
        self.assertNotIn(self.group_ref["sha256"], {x["sha256"] for x in check["artifacts"]})
        f.save_spec()
        receipt = f.accept()
        self.assertEqual(receipt["status"], "SELECTION_INPUTS_ARCHIVED")
        self.assertIn("TEST_ONLY_GROUP_MAP", f.archive.records[-2]["parents"])
        self.assertEqual(f.archive.append_count, 2)

    def test_group_event_cannot_fake_stored_output(self):
        self.event["outputs"].pop()
        with self.assertRaisesRegex(ValueError, "does not bind"):
            self.bind()
        self.assertEqual(self.f.archive.put_count, 0)

    def test_missing_110th_receipt_is_not_ready(self):
        (self.f.run / "results/M22-J2/ARCHIVE_RECEIPT.json").unlink()
        with self.assertRaisesRegex(ValueError, "Missing or unsafe"):
            self.bind()

    def test_changed_original_input_event_rejected(self):
        self.resolution["input_event_id"] = "TEST_ONLY_WRONG_INPUT"
        with self.assertRaisesRegex(ValueError, "Original input event"):
            self.bind()

    def test_failed_sid_cannot_become_replacement(self):
        self.resolution["exceptions"]["M12-N2"]["failed_attempt"]["session_id"] = "TEST_ONLY_REPLACEMENT_M12-N2"
        with self.assertRaisesRegex(ValueError, "Failed session"):
            self.bind()

    def test_unmapped_third_replacement_rejected(self):
        f = self.f
        name = "runs/final-selection-20261018/results/M22-J2/ARCHIVE_RECEIPT.json"
        receipt = f.A.decode(f.A.read(f.root, name))
        receipt["accepted_attempt"] = 2
        f.put(name, receipt)
        with self.assertRaisesRegex(ValueError, "Ordinary logical review"):
            self.bind()

    def test_duplicate_vote_session_rejected(self):
        f = self.f
        name = "runs/final-selection-20261018/results/M22-J2/ARCHIVE_RECEIPT.json"
        receipt = f.A.decode(f.A.read(f.root, name))
        receipt["session_id"] = "TEST_ONLY_REPLACEMENT_M12-N2"
        f.put(name, receipt)
        with self.assertRaisesRegex(ValueError, "Duplicate accepted session"):
            self.bind()

    def test_accept_rechecks_canonical_map_before_any_write(self):
        f = self.f
        f.spec = self.bind()
        f.save_spec()
        f.archive.records.remove(self.event)
        with self.assertRaisesRegex(ValueError, "Accepted check event absent"):
            f.accept()
        self.assertEqual((f.archive.put_count, f.archive.append_count), (0, 0))


if __name__ == "__main__":
    unittest.main(verbosity=2)
