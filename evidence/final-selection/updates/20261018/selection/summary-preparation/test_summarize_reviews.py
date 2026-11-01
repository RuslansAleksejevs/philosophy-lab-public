"""Meaningful synthetic checks only; no real reviews, manuscripts or archives."""
from pathlib import Path
from contextlib import contextmanager
import importlib.util
import json
import shutil
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("summary_under_test", Path(__file__).with_name("summarize_reviews.py"))
s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def fixture(root):
    run = root / "runs" / "selection"
    run.mkdir(parents=True)
    schema = {"type": "object", "required": ["review_id", "manuscript_id", "profile_id", "read_complete", "scores", "recommendation", "reason_ru", "concerns", "limits"],
              "properties": {"scores": {"type": "object", "required": ["overall", "argument", "significance", "originality"],
                "properties": {m: {"type": ["integer", "null"] if m == "originality" else "integer", "minimum": 1, "maximum": 5} for m in (*s.METRICS, "originality")}}}}
    save(run / "review-schema.json", schema)
    jobs, rows = [], []
    for number in range(1, 23):
        mid = "M" + str(number).zfill(2)
        rows.append({"candidate": "E" + str(number).zfill(3), "blind_id": mid, "profiles": ["profile-a", "profile-b"],
                     "version": {"path": "unused-manuscript-" + mid + ".md", "sha256": "a" * 64, "current": True}})
        for role in s.ROLES:
            jid = mid + "-" + role
            prompt = run / "packets" / (jid + ".txt")
            prompt.parent.mkdir(exist_ok=True)
            prompt.write_text("Synthetic frozen input " + jid)
            job = {"id": jid, "phase": "individual", "manuscript_id": mid, "role": role,
                   "profile_id": "neutral" if role.startswith("N") else "profile-" + ("a" if role == "J1" else "b"),
                   "model": "gpt-synthetic", "effort": "high", "service_tier": "default",
                   "prompt_file": str(prompt.relative_to(root)), "prompt_sha256": s.digest(prompt.read_bytes()),
                   "schema_file": str((run / "review-schema.json").relative_to(root)), "schema_sha256": s.digest((run / "review-schema.json").read_bytes())}
            jobs.append(job)
    save(run / "queue.json", {"run_id": "selection", "jobs": jobs})
    save(run / "ALLOCATION.json", {"rows": rows})
    frozen = [{"path": str(p.relative_to(root)), "sha256": s.digest(p.read_bytes())} for p in sorted(run.rglob("*")) if p.is_file()]
    save(run / "START_RECEIPT.json", {"status": "SELECTION_INPUTS_ARCHIVED", "event_id": "event-input", "files": frozen})
    for index, job in enumerate(jobs):
        lane = run / "results" / job["id"]
        attempt = lane / "attempt-001"
        attempt.mkdir(parents=True)
        sid = "synthetic-session-" + str(index)
        score = s.ROLES.index(job["role"]) + 1
        value = {"review_id": job["id"], "manuscript_id": job["manuscript_id"], "profile_id": job["profile_id"], "read_complete": True,
                 "scores": {m: score for m in (*s.METRICS, "originality")}, "recommendation": "borderline",
                 "reason_ru": ["Первый синтетический довод.", "Второй синтетический довод."],
                 "concerns": [{"severity": "open", "kind": "source", "location": "Synthetic", "excerpt": "Synthetic", "reason": "Synthetic concern", "text_response": "Synthetic response", "discriminating_check": "Synthetic check"}],
                 "limits": ["Synthetic limit"]}
        save(attempt / "response.json", value)
        save(attempt / "final.txt", value)
        proof = {"session_id": sid, "prompt_sha256": job["prompt_sha256"], "isolation_failures": [], "tool_calls": [], "other_user_metadata": [],
                 "prompt_lines": [3], "final_lines": [8], "configurations": [{"model": job["model"], "effort": job["effort"], "service_tier": "default"}]}
        save(attempt / "native-check.json", proof)
        for name in ("native-visible.json", "launch.json", "stderr.json", "visible-events.jsonl"):
            save(attempt / name, {"fixture": True})
        save(lane / "CAPTURE_RECEIPT.json", {"status": "BOUNDED_VISIBLE_CAPTURE_ACCEPTED", "session_id": sid, "evidence_events": ["event-capture-" + str(index)]})
        receipt = {"status": s.COMPLETE, "job_id": job["id"], "session_id": sid, "quality_flags": [], "visible_final_count": 1,
                   "prompt_sha256": job["prompt_sha256"], "schema_sha256": job["schema_sha256"], "requested_model": job["model"],
                   "requested_effort": job["effort"], "requested_service_tier": "default"}
        save(attempt / "receipt.json", receipt)
        archive = {"status": "REVIEW_ARCHIVED", "job_id": job["id"], "session_id": sid, "input_event_id": "event-input",
                   "event_id": "event-review-" + str(index), "lineage_event_id": "event-lineage-" + str(index),
                   "lineage_entry_id": "selection:" + job["id"] + ":evaluation-v1"}
        save(lane / "ARCHIVE_RECEIPT.json", archive)
        rebind_job(root, run, job["id"])
    return run


def rebind_job(root, run, jid):
    lane = run / "results" / jid
    attempt = lane / "attempt-001"
    receipt = json.loads((attempt / "receipt.json").read_text())
    receipt["outputs"] = {str(p.relative_to(root)): s.digest(p.read_bytes()) for p in attempt.iterdir() if p.name != "receipt.json"}
    save(attempt / "receipt.json", receipt)
    archive = json.loads((lane / "ARCHIVE_RECEIPT.json").read_text())
    archive["files"] = [{"path": str(p.relative_to(root)), "sha256": s.digest(p.read_bytes()), "bytes": p.stat().st_size} for p in sorted(attempt.iterdir())]
    archive["capture_sha256"] = s.digest((lane / "CAPTURE_RECEIPT.json").read_bytes())
    save(lane / "ARCHIVE_RECEIPT.json", archive)


def rebind_input(root, run, path):
    start = json.loads((run / "START_RECEIPT.json").read_text())
    for item in start["files"]:
        if item["path"] == str(path.relative_to(root)):
            item["sha256"] = s.digest(path.read_bytes())
    save(run / "START_RECEIPT.json", start)


class Math(unittest.TestCase):
    def reviews(self):
        return [{"role": role, "response": {"scores": {m: number for m in (*s.METRICS, "originality")}}} for number, role in enumerate(s.ROLES, 1)]

    def test_exact_three_two_weight_is_not_fifty_fifty(self):
        result = s.aggregate(self.reviews())["overall"]
        self.assertEqual(result["neutral_mean"], 2.0)
        self.assertEqual(result["profile_mean"], 4.5)
        self.assertEqual(result["combined_60_40"], 3.0)
        self.assertNotEqual(result["combined_60_40"], 3.25)

    def test_null_originality_does_not_become_zero_or_reweighted(self):
        reviews = self.reviews()
        reviews[0]["response"]["scores"]["originality"] = None
        result = s.aggregate(reviews)
        self.assertIsNone(result["originality"]["neutral_mean"])
        self.assertEqual(result["originality"]["neutral_known"], 2)
        self.assertEqual(result["originality"]["profile_mean"], 4.5)
        self.assertIsNone(result["originality"]["combined_60_40"])
        self.assertEqual(result["overall"]["combined_60_40"], 3.0)

    def test_duplicate_or_missing_role_cannot_aggregate(self):
        for reviews in (self.reviews()[:-1], self.reviews()[:-1] + [self.reviews()[0]]):
            with self.assertRaises(s.InvalidEvidence):
                s.aggregate(reviews)


class Evidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base_temp = tempfile.TemporaryDirectory()
        cls.base = Path(cls.base_temp.name).resolve()
        fixture(cls.base)

    @classmethod
    def tearDownClass(cls):
        cls.base_temp.cleanup()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve()
        shutil.copytree(self.base / "runs", self.root / "runs")
        self.run = self.root / "runs/selection"
        self.lane = self.run / "results/M01-N1"
        self.attempt = self.lane / "attempt-001"

    def tearDown(self):
        self.temp.cleanup()

    def assert_blocked(self, expected=109):
        coverage, summary = s.summarize(self.run)
        self.assertIsNone(summary)
        self.assertEqual(coverage["accepted_reviews"], expected)
        self.assertFalse(coverage["summary_generated"])
        text = json.dumps(coverage)
        self.assertNotIn("neutral_mean", text)
        self.assertNotIn("combined_60_40", text)
        self.assertNotIn("Synthetic concern", text)
        return coverage

    def test_all_110_verified_emit_22_in_frozen_order_with_exact_reviews(self):
        coverage, summary = s.summarize(self.run)
        self.assertEqual(coverage["accepted_reviews"], 110)
        self.assertEqual(len(summary["rows"]), 22)
        self.assertEqual([r["blind_id"] for r in summary["rows"]], ["M" + str(i).zfill(2) for i in range(1, 23)])
        row = summary["rows"][0]
        self.assertEqual(row["metrics"]["overall"]["combined_60_40"], 3.0)
        self.assertEqual(row["reviews"][0]["response"], json.loads((self.attempt / "response.json").read_text()))
        self.assertTrue(row["reviews"][0]["evidence"]["lineage_event_id"])
        self.assertNotIn("rank", row)

    def test_one_missing_archive_receipt_blocks_all_means(self):
        (self.lane / "ARCHIVE_RECEIPT.json").unlink()
        coverage = self.assert_blocked()
        self.assertEqual(coverage["status_counts"]["LOCAL_ONLY_NOT_ARCHIVED"], 1)

    def test_quarantined_is_missing_even_if_a_response_file_exists(self):
        archive = json.loads((self.lane / "ARCHIVE_RECEIPT.json").read_text())
        archive["status"] = "QUARANTINED_REVIEW_ARCHIVED_MISSING"
        save(self.lane / "ARCHIVE_RECEIPT.json", archive)
        self.assertEqual(self.assert_blocked()["status_counts"]["QUARANTINED_MISSING"], 1)

    def test_hash_change_blocks_review(self):
        (self.attempt / "response.json").write_text("{}")
        self.assertEqual(self.assert_blocked()["status_counts"]["INVALID_EVIDENCE_MISSING"], 1)

    def test_wrong_response_identity_fails_even_with_rebound_hashes(self):
        value = json.loads((self.attempt / "response.json").read_text())
        value["review_id"] = "M02-N1"
        save(self.attempt / "response.json", value)
        save(self.attempt / "final.txt", value)
        rebind_job(self.root, self.run, "M01-N1")
        self.assert_blocked()

    def test_duplicate_job_is_rejected_even_if_input_hash_is_rebound(self):
        path = self.run / "queue.json"
        queue = json.loads(path.read_text())
        queue["jobs"][-1] = queue["jobs"][0]
        save(path, queue)
        rebind_input(self.root, self.run, path)
        coverage, summary = s.summarize(self.run)
        self.assertIsNone(summary)
        self.assertEqual(coverage["status"], "INVALID_INPUTS_COVERAGE_ONLY")

    def test_wrong_three_two_allocation_is_rejected(self):
        path = self.run / "queue.json"
        queue = json.loads(path.read_text())
        queue["jobs"][2]["role"] = "N2"
        save(path, queue)
        rebind_input(self.root, self.run, path)
        self.assertEqual(s.summarize(self.run)[0]["status"], "INVALID_INPUTS_COVERAGE_ONLY")

    def test_duplicate_output_manifest_entry_is_rejected(self):
        archive = json.loads((self.lane / "ARCHIVE_RECEIPT.json").read_text())
        archive["files"].append(archive["files"][0])
        save(self.lane / "ARCHIVE_RECEIPT.json", archive)
        self.assert_blocked()

    def test_native_configuration_mismatch_is_rejected(self):
        path = self.attempt / "native-check.json"
        proof = json.loads(path.read_text())
        proof["configurations"][0]["effort"] = "low"
        save(path, proof)
        rebind_job(self.root, self.run, "M01-N1")
        self.assert_blocked()

    def test_complete_set_preserves_null_originality_in_response_and_means(self):
        value = json.loads((self.attempt / "response.json").read_text())
        value["scores"]["originality"] = None
        save(self.attempt / "response.json", value)
        save(self.attempt / "final.txt", value)
        rebind_job(self.root, self.run, "M01-N1")
        coverage, summary = s.summarize(self.run)
        self.assertEqual(coverage["accepted_reviews"], 110)
        row = summary["rows"][0]
        self.assertIsNone(row["metrics"]["originality"]["combined_60_40"])
        self.assertIsNone(row["reviews"][0]["response"]["scores"]["originality"])

    def test_incomplete_output_contains_only_coverage_and_is_immutable(self):
        (self.lane / "ARCHIVE_RECEIPT.json").unlink()
        coverage, summary = s.summarize(self.run)
        destination = self.root / "coverage-output"
        s.write_outputs(destination, coverage, summary)
        self.assertEqual([p.name for p in destination.iterdir()], ["coverage.json"])
        with self.assertRaises(s.InvalidEvidence):
            s.write_outputs(destination, coverage, summary)


if __name__ == "__main__":
    unittest.main(verbosity=2)
