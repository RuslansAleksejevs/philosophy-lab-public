"""Disposable synthetic inputs only. No real manuscripts, reviews or archive.

The resolver is replaced only at the consumer boundary by an explicit synthetic
map. Frozen verifier/aggregate functions execute unchanged on fixture bytes.
"""
from pathlib import Path
import copy
import json
import tempfile
import unittest
from unittest.mock import patch

import summary_capacity_v2 as S
import export_capacity_v2 as E

TEST_JOB = "M12-N2"


class Fixture:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.run = self.root / E.SOURCE
        self.run.mkdir(parents=True)
        self.old_input = "TEST_ONLY_ORIGINAL_READY"
        self.resolution = {"schema": "selection-capacity-resolution.v2", "input_event_id": self.old_input,
                           "map_event_id": "TEST_ONLY_GROUP_ACCEPTED_ATTEMPTS_MAP", "evidence_files": [], "exceptions": {}}
        for jid in sorted(S.LOGICAL_JOBS):
            item = {"logical_job_id": jid, "input_event_id": self.old_input,
                    "ready_event_id": "TEST_ONLY_REPLACEMENT_READY_" + jid,
                    "map_event_id": "TEST_ONLY_ACCEPTED_ATTEMPTS_MAP_" + jid,
                    "failed_attempt": {"path": str(self.run / "results" / jid / "attempt-001"),
                                       "event_id": "TEST_ONLY_CAPACITY_FAILURE_" + jid,
                                       "session_id": "TEST_ONLY_FAILED_SESSION_" + jid, "files": []},
                    "accepted_attempt": {"path": str(self.run / "results" / jid / "attempt-002"),
                                         "event_id": "TEST_ONLY_REVIEW_" + jid,
                                         "session_id": "TEST_ONLY_SESSION_" + jid, "files": []},
                    "evidence_files": []}
            failure = self.put("results/" + jid + "/attempt-001/failure.json", {"TEST_ONLY": "capacity failure; no review"})
            item["failed_attempt"]["files"] = [failure]
            for name in ("CAPACITY_FAILURE_RECEIPT.json", "REPLACEMENT_ADDENDUM.json", "ACCEPTED_ATTEMPTS_MAP_RECEIPT.json"):
                item["evidence_files"].append(self.put("capacity-resume-20261018/" + jid + "/" + name, {"TEST_ONLY": name, "job": jid}))
            self.resolution["exceptions"][jid] = item
            self.resolution["evidence_files"] += item["evidence_files"]
        self.resolution["evidence_files"].append(self.put("capacity-resume-20261018/GROUP_MAP_RECEIPT.json", {"TEST_ONLY": "both accepted"}))
        self.new_ready = self.resolution["exceptions"][TEST_JOB]["ready_event_id"]
        schema_ref = self.put("review-schema.json", {"type": "object"})
        self.jobs, allocation, frozen = [], [], [schema_ref]
        for i in range(1, 23):
            mid = f"M{i:02}"
            allocation.append({"candidate": f"TEST_ONLY_CANDIDATE_{i:02}", "blind_id": mid,
                               "profiles": ["TEST_PROFILE_1", "TEST_PROFILE_2"],
                               "version": {"path": f"TEST_ONLY_VERSION_{i:02}", "sha256": "0" * 64}})
            for role in S.ROLES:
                jid = mid + "-" + role
                prompt = self.put("packets/" + jid + ".txt", ("TEST_ONLY neutral placeholder " + jid).encode())
                frozen.append(prompt)
                job = {"id": jid, "phase": "individual", "manuscript_id": mid, "role": role,
                       "profile_id": "neutral" if role.startswith("N") else "TEST_PROFILE_" + role[1],
                       "model": "gpt-6-astra", "effort": "ultra", "service_tier": "default",
                       "prompt_file": prompt["path"], "prompt_sha256": prompt["sha256"],
                       "schema_file": schema_ref["path"], "schema_sha256": schema_ref["sha256"]}
                self.jobs.append(job)
                self.make_review(job)
        frozen += [self.put("queue.json", {"run_id": self.run.name, "jobs": self.jobs}),
                   self.put("ALLOCATION.json", {"rows": allocation})]
        self.start_ref = self.put("START_RECEIPT.json", {"status": "SELECTION_INPUTS_ARCHIVED",
                                                       "event_id": self.old_input, "files": frozen})
        self.queue_ref = next(r for r in frozen if r["path"].endswith("/queue.json"))

    def put(self, name, value):
        data = value if isinstance(value, bytes) else (json.dumps(value, sort_keys=True) + "\n").encode()
        path = self.run / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return {"path": str(path.relative_to(self.root)), "sha256": S.digest(data), "bytes": len(data)}

    def load(self, name):
        return json.loads((self.run / name).read_bytes())

    def resolved(self, job, run_dir, root, resolution):
        # Explicit mock of an already validated canonical resolution, not a
        # default fallback when a replacement receipt happens to be absent.
        self.assert_scope(run_dir, root, resolution)
        attempt = 2 if job["id"] in S.LOGICAL_JOBS else 1
        lane = Path(run_dir) / "results" / job["id"]
        return {"attempt": lane / f"attempt-{attempt:03}", "attempt_number": attempt,
                "archive_receipt": lane / "ARCHIVE_RECEIPT.json", "capture_receipt": lane / "CAPTURE_RECEIPT.json"}

    def assert_scope(self, run_dir, root, resolution):
        if Path(run_dir) != self.run or Path(root) != self.root or set(resolution["exceptions"]) != S.LOGICAL_JOBS:
            raise ValueError("TEST_ONLY resolver scope mismatch")

    def make_review(self, job):
        jid = job["id"]; number = 2 if jid in S.LOGICAL_JOBS else 1
        lane = "results/" + jid + "/"; attempt = lane + f"attempt-{number:03}/"
        sid = "TEST_ONLY_SESSION_" + jid
        value = {"review_id": jid, "manuscript_id": job["manuscript_id"], "profile_id": job["profile_id"],
                 "read_complete": True, "scores": {"overall": 3, "argument": 4, "significance": 2, "originality": 3},
                 "reason_ru": ["Это искусственный пример для проверки программы.", "Он не содержит настоящего философского отзыва."],
                 "recommendation": "borderline"}
        files = [self.put(attempt + "response.json", value), self.put(attempt + "final.txt", value),
                 self.put(attempt + "native-check.json", {"session_id": sid, "prompt_sha256": job["prompt_sha256"],
                    "isolation_failures": [], "tool_calls": [], "other_user_metadata": [],
                    "prompt_lines": [1], "final_lines": [2],
                    "configurations": [{"model": job["model"], "effort": job["effort"], "service_tier": "default"}]}),
                 self.put(attempt + "native-visible.json", {"TEST_ONLY": "opaque evidence"}),
                 self.put(attempt + "launch.json", {"TEST_ONLY": "synthetic launch; no provider"}),
                 self.put(attempt + "stderr.json", []), self.put(attempt + "visible-events.jsonl", b"")]
        receipt = {"status": S.COMPLETE, "job_id": jid, "session_id": sid, "quality_flags": [], "visible_final_count": 1,
                   "prompt_sha256": job["prompt_sha256"], "schema_sha256": job["schema_sha256"],
                   "requested_model": job["model"], "requested_effort": job["effort"], "requested_service_tier": job["service_tier"],
                   "outputs": {f["path"]: f["sha256"] for f in files}}
        files.append(self.put(attempt + "receipt.json", receipt))
        capture = self.put(lane + "CAPTURE_RECEIPT.json", {"status": "BOUNDED_VISIBLE_CAPTURE_ACCEPTED",
                           "session_id": sid, "evidence_events": ["TEST_ONLY_CAPTURE_" + jid]})
        archive = {"status": "REVIEW_ARCHIVED", "job_id": jid, "session_id": sid, "event_id": "TEST_ONLY_REVIEW_" + jid,
                   "input_event_id": self.old_input, "lineage_event_id": "TEST_ONLY_LINEAGE_" + jid,
                   "lineage_entry_id": self.run.name + ":" + jid + ":evaluation-v1",
                   "files": files, "capture_sha256": capture["sha256"], "capture_status": "BOUNDED_VISIBLE_CAPTURE_ACCEPTED"}
        if number == 2:
            exception = self.resolution["exceptions"][jid]
            archive.update(accepted_attempt=2, attempt_path=str((self.run / attempt).relative_to(self.root)),
                           replacement_ready_event_id=exception["ready_event_id"], failed_attempt_event_id=exception["failed_attempt"]["event_id"])
            exception["accepted_attempt"]["files"] = files
        self.put(lane + "ARCHIVE_RECEIPT.json", archive)

    def change_response(self, job_id, value):
        number = 2 if job_id in S.LOGICAL_JOBS else 1
        lane = "results/" + job_id + "/"; attempt = lane + f"attempt-{number:03}/"
        response = self.put(attempt + "response.json", value)
        final = self.put(attempt + "final.txt", value)
        receipt = self.load(attempt + "receipt.json")
        receipt["outputs"].update({response["path"]: response["sha256"], final["path"]: final["sha256"]})
        receipt_ref = self.put(attempt + "receipt.json", receipt)
        replacements = {r["path"]: r for r in (response, final, receipt_ref)}
        archive = self.load(lane + "ARCHIVE_RECEIPT.json")
        archive["files"] = [replacements.get(r["path"], r) for r in archive["files"]]
        self.put(lane + "ARCHIVE_RECEIPT.json", archive)

    def export_spec(self, provenance=True):
        for name in E.MINIMUM_FIXED:
            if not (self.run / name).exists(): self.put(name, {"TEST_ONLY": name})
        counts = {"accepted_individual_reviews": 110, "accepted_neutral_individual": 66,
                  "accepted_profile_individual": 44, "actual_pairs": 0, "accepted_pair_reviews": 0}
        selected = [f"TEST_ONLY_CANDIDATE_{i:02}" for i in range(1, 11)]
        names = {"decisions": "DECISIONS.json", "final_plan": "FINAL_PLAN.json", "summary": "TEST_COUNTS.json",
                 "selection_manifest": "TEST_SELECTION.json", "reading_manifest": "TEST_READING.json", "provenance": "TEST_PROVENANCE.json"}
        named = {key: self.put(name, {"TEST_ONLY": key, "counts": counts, "selected": selected}) for key, name in names.items()}
        return {"schema": "explicit-selection-final-files.v1", "status": "ROOT_SELECTED_FINAL_INPUTS", "named_outputs": named,
                "count_fields": {key: {"input": "summary", "pointer": "/counts/" + key} for key in E.COUNT_KEYS},
                "selected_ids_field": {"input": "summary", "pointer": "/selected"},
                "reading": [{"candidate_id": cid, "source": self.put(f"reading/{i:02}.md", b"TEST_ONLY opaque reading bytes\n")} for i, cid in enumerate(selected, 1)],
                "individual": {"queue": self.queue_ref, "input_receipt": self.start_ref},
                "pairs": {"mode": "EXPLICIT_NO_PAIRS"}, "include_review_evidence": True,
                "include_review_provenance": provenance, "include_technical_files": False}


class ConsumerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="TEST_ONLY-capacity-consumers-v2-")
        self.addCleanup(self.tmp.cleanup)
        self.f = Fixture(self.tmp.name)
        for module in (S, E):
            patcher = patch.object(module, "resolve_job", side_effect=self.f.resolved)
            patcher.start(); self.addCleanup(patcher.stop)

    def summary(self): return S.summarize(self.f.run, self.f.resolution)
    def export(self, spec=None): return E.build(spec or self.f.export_spec(), self.f.root, self.f.resolution)

    def test_complete110_summary_retains_failure_without_counting_it(self):
        failed = {jid: (self.f.run / "results" / jid / "attempt-001/failure.json").read_bytes() for jid in S.LOGICAL_JOBS}
        report, summary = self.summary()
        self.assertEqual((report["accepted_reviews"], report["missing_reviews"], report["preserved_failed_attempts"]), (110, 0, 2))
        self.assertEqual((summary["candidate_count"], summary["review_count"], summary["preserved_failed_attempts"]), (22, 110, 2))
        for jid in S.LOGICAL_JOBS:
            replacement = next(j for j in report["jobs"] if j["job_id"] == jid)
            self.assertIn("/" + jid + "/attempt-002/response.json", replacement["evidence"]["response_file"])
            self.assertEqual((self.f.run / "results" / jid / "attempt-001/failure.json").read_bytes(), failed[jid])
            self.assertFalse((self.f.run / "results" / jid / "attempt-001/receipt.json").exists())
        self.assertEqual(summary["rows"][0]["metrics"], S.frozen.aggregate(summary["rows"][0]["reviews"]))
        self.assertEqual(len({review["evidence"]["session_id"] for row in summary["rows"] for review in row["reviews"]}), 110)

    def test_missing002_does_not_fall_back_to001(self):
        (self.f.run / "results/M12-N2/attempt-002/response.json").unlink()
        self.f.put("results/M12-N2/attempt-001/response.json", {"TEST_ONLY": "must not be read"})
        report, summary = self.summary()
        self.assertEqual(report["accepted_reviews"], 109); self.assertIsNone(summary)

    def test_ordinary001_verification_is_still_strict(self):
        self.f.put("results/M01-N1/attempt-001/final.txt", b"TEST_ONLY changed content\n")
        report, summary = self.summary()
        self.assertEqual(report["accepted_reviews"], 109); self.assertIsNone(summary)

    def test_stale_accepted_map_cannot_certify002(self):
        self.f.resolution["exceptions"][TEST_JOB]["accepted_attempt"]["event_id"] = "TEST_ONLY_WRONG_EVENT"
        report, summary = self.summary()
        self.assertEqual(report["accepted_reviews"], 109); self.assertIsNone(summary)

    def test_recovery_receipt_must_keep_original_input_and_new_dependencies(self):
        name = "results/M12-N2/ARCHIVE_RECEIPT.json"
        archive = self.f.load(name); archive["input_event_id"] = self.f.new_ready; self.f.put(name, archive)
        report, summary = self.summary()
        self.assertEqual(report["accepted_reviews"], 109); self.assertIsNone(summary)
        with self.assertRaises(ValueError): self.export()

    def test_same_failed_and_accepted_session_rejected(self):
        self.f.resolution["exceptions"][TEST_JOB]["failed_attempt"]["session_id"] = self.f.resolution["exceptions"][TEST_JOB]["accepted_attempt"]["session_id"]
        report, summary = self.summary()
        self.assertEqual(report["status"], "INVALID_INPUTS_COVERAGE_ONLY"); self.assertIsNone(summary)
        with self.assertRaises(ValueError): self.export()

    def test_null_originality_rule_unchanged(self):
        value = self.f.load("results/M12-N2/attempt-002/response.json")
        value["scores"]["originality"] = None
        self.f.change_response(TEST_JOB, value)
        report, summary = self.summary()
        self.assertEqual(report["accepted_reviews"], 110)
        metric = next(r for r in summary["rows"] if r["blind_id"] == "M12")["metrics"]["originality"]
        self.assertIsNone(metric["neutral_mean"]); self.assertIsNone(metric["combined_60_40"])
        self.assertEqual(metric["profile_mean"], 3.0)

    def test_export_contains002_provenance_and_all_safe_recovery_metadata(self):
        result = self.export()
        names = {r["path"] for r in result["files"]}
        self.assertEqual(result["accepted_review_counts_verified"]["accepted_individual_reviews"], 110)
        self.assertEqual(result["preserved_failed_attempts"], 2)
        self.assertEqual(len(result["categories"]["accepted_review_receipts"]), 110)
        self.assertEqual(set(result["categories"]["capacity_recovery_evidence"]), {r["path"] for r in self.f.resolution["evidence_files"]})
        for jid in S.LOGICAL_JOBS:
            for leaf in ("response.json", "receipt.json", "launch.json", "native-check.json", "final.txt"):
                self.assertIn(E.SOURCE + "results/" + jid + "/attempt-002/" + leaf, names)
            self.assertFalse(any("results/" + jid + "/attempt-001/" in n for n in names))
        self.assertFalse(any(Path(n).name in {"native-visible.json", "visible-events.jsonl", "stderr.json"} for n in names))

    def test_export_never_parses_response_prose(self):
        self.f.change_response(TEST_JOB, b"TEST_ONLY opaque response; intentionally not valid JSON\n")
        result = self.export()
        self.assertEqual(result["accepted_review_counts_verified"]["accepted_individual_reviews"], 110)

    def test_safe_recovery_metadata_is_required_even_without_optional_evidence(self):
        spec = self.f.export_spec(provenance=False); spec["include_review_evidence"] = False
        result = self.export(spec)
        self.assertEqual(len(result["categories"]["capacity_recovery_evidence"]), 7)
        self.assertNotIn("optional_review_evidence", result["categories"])
        self.f.resolution["evidence_files"] = []
        with self.assertRaises(ValueError): self.export(spec)

    def test_raw_recovery_metadata_rejected(self):
        for leaf in ("stdout.json", "stderr.txt", "native-visible.json", "visible-events.jsonl"):
            with self.subTest(leaf=leaf):
                resolution = copy.deepcopy(self.f.resolution)
                raw = self.f.put("capacity-resume-20261018/" + leaf, {"TEST_ONLY": True})
                resolution["evidence_files"].append(raw)
                resolution["exceptions"][TEST_JOB]["evidence_files"].append(raw)
                with self.assertRaisesRegex(ValueError, "excluded"): E.build(self.f.export_spec(), self.f.root, resolution)

    def test_changed_safe_metadata_hash_rejected(self):
        ref = self.f.resolution["evidence_files"][0]
        (self.f.root / ref["path"]).write_bytes(b"TEST_ONLY changed metadata\n")
        with self.assertRaises(ValueError): self.export()

    def test_export_cannot_accept_quarantined_or_wrong_attempt(self):
        name = "results/M12-N2/ARCHIVE_RECEIPT.json"
        original = self.f.load(name)
        for change in ({"status": "QUARANTINED_REVIEW_ARCHIVED_MISSING"}, {"accepted_attempt": 1}, {"failed_attempt_event_id": "TEST_ONLY_WRONG_FAILURE"}):
            with self.subTest(change=change):
                self.f.put(name, {**original, **change})
                with self.assertRaises(ValueError): self.export()

    def test_pair_export_still_uses_ordinary001_and_actual_pair_input(self):
        spec = self.f.export_spec()
        jobs = []
        for role in S.ROLES:
            template = copy.deepcopy(self.f.jobs[0])
            template.update(id="TEST_PAIR_01-" + role, phase="pair", role=role,
                            expected_output={"pair_id": "TEST_PAIR_01"})
            self.f.make_review(template)
            name = "results/" + template["id"] + "/ARCHIVE_RECEIPT.json"
            archive = self.f.load(name); archive["input_event_id"] = "TEST_ONLY_PAIR_READY"
            self.f.put(name, archive)
            jobs.append(template)
        queue = self.f.put("pairs/queue.json", {"jobs": jobs})
        inputs = {key: self.f.put("pairs/" + key + ".json", {"TEST_ONLY": key}) for key in ("method", "allocation", "rubric", "schema")}
        start = self.f.put("pairs/START_RECEIPT.json", {"event_id": "TEST_ONLY_PAIR_READY", "files": [queue, *inputs.values()]})
        spec["pairs"] = {"mode": "EXPLICIT_ACCEPTED_PAIR_QUEUE", "queue": queue, "input_receipt": start, "method_inputs": inputs}
        summary_name = "TEST_COUNTS.json"; summary = self.f.load(summary_name)
        summary["counts"].update(actual_pairs=1, accepted_pair_reviews=5)
        spec["named_outputs"]["summary"] = self.f.put(summary_name, summary)
        result = self.export(spec)
        self.assertEqual(result["accepted_review_counts_verified"]["accepted_individual_reviews"], 110)
        self.assertEqual(result["accepted_review_counts_verified"]["accepted_pair_reviews"], 5)
        self.assertEqual(result["preserved_failed_attempts"], 2)
        names = {r["path"] for r in result["files"]}
        self.assertIn(E.SOURCE + "results/TEST_PAIR_01-N1/attempt-001/response.json", names)

    def test_m13_replacement_missing_does_not_let_m12_count_twice(self):
        (self.f.run / "results/M13-N2/attempt-002/response.json").unlink()
        report, summary = self.summary()
        self.assertEqual(report["accepted_reviews"], 109)
        self.assertEqual(report["preserved_failed_attempts"], 2)
        self.assertIsNone(summary)
        with self.assertRaises(ValueError): self.export()

    def test_both002_missing_leave108_ordinary_reviews(self):
        for jid in S.LOGICAL_JOBS:
            (self.f.run / "results" / jid / "attempt-002/response.json").unlink()
        report, summary = self.summary()
        self.assertEqual((report["accepted_reviews"], report["missing_reviews"]), (108, 2))
        self.assertIsNone(summary)

    def test_group_map_must_have_exactly_the_two_named_exceptions(self):
        original = copy.deepcopy(self.f.resolution)
        for change in ("missing", "extra", "wrong_schema"):
            with self.subTest(change=change):
                self.f.resolution = copy.deepcopy(original)
                if change == "missing": del self.f.resolution["exceptions"]["M13-N2"]
                elif change == "extra": self.f.resolution["exceptions"]["M14-N2"] = copy.deepcopy(original["exceptions"][TEST_JOB])
                else: self.f.resolution["schema"] = "selection-capacity-resolution.v1"
                report, summary = self.summary()
                self.assertEqual(report["status"], "INVALID_INPUTS_COVERAGE_ONLY")
                self.assertIsNone(summary)
                with self.assertRaises(ValueError): self.export()

    def test_one_accepted_replacement_cannot_be_reused_for_both_jobs(self):
        self.f.resolution["exceptions"]["M13-N2"]["accepted_attempt"]["session_id"] = self.f.resolution["exceptions"][TEST_JOB]["accepted_attempt"]["session_id"]
        report, summary = self.summary()
        self.assertEqual(report["status"], "INVALID_INPUTS_COVERAGE_ONLY")
        self.assertIsNone(summary)
        with self.assertRaises(ValueError): self.export()

    def test_group_export_cannot_omit_second_failure_metadata(self):
        omitted = self.f.resolution["exceptions"]["M13-N2"]["evidence_files"][0]
        self.f.resolution["evidence_files"] = [ref for ref in self.f.resolution["evidence_files"] if ref["path"] != omitted["path"]]
        with self.assertRaisesRegex(ValueError, "omitted or changed"):
            self.export()

    def test_each_replacement_must_keep_the_group_original_input(self):
        self.f.resolution["exceptions"]["M13-N2"]["input_event_id"] = "TEST_ONLY_OTHER_INPUT"
        report, summary = self.summary()
        self.assertEqual(report["status"], "INVALID_INPUTS_COVERAGE_ONLY")
        self.assertIsNone(summary)
        with self.assertRaises(ValueError): self.export()


if __name__ == "__main__": unittest.main(verbosity=2)
