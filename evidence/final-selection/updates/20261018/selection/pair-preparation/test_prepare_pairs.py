"""Synthetic-only preparation tests; no real manuscript or review is opened."""
from pathlib import Path
import copy
import importlib.util
import itertools
import json
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("pair_preparer", HERE / "prepare_pairs.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
spec_runner = importlib.util.spec_from_file_location("pair_test_runner", HERE.parent / "runner.py")
runner = importlib.util.module_from_spec(spec_runner)
spec_runner.loader.exec_module(runner)


class Pairs(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name).resolve()
        self.run = self.root / "runs" / "synthetic-selection"
        self.templates = self.run / "pair-preparation"
        self.templates.mkdir(parents=True)
        for name in ("prepare_pairs.py", "pair-schema.template.json", "pair-rubric.template.txt"):
            (self.templates / name).write_bytes((HERE / name).read_bytes())
        self.bodies = {}
        rows = []
        for index in range(1, 7):
            cid, mid = "SYNTH_" + str(index), "M" + str(index).zfill(2)
            data = ("Synthetic text " + str(index) + "\r\nLiteral café — α.\r\nBibliography\r\nSynthetic source.\r\n").encode()
            path = self.run / "blind" / (mid + ".md")
            m.write_new(path, data)
            self.bodies[cid] = data
            rows.append({"candidate": cid, "blind_id": mid, "version": {"path": str(path.relative_to(self.root)), "sha256": m.sha(data), "current": True}})
        profile_materials = {}
        for profile in ("synthetic_one", "synthetic_two", "synthetic_three"):
            directory = self.root / "research/judges/20261007" / profile
            files = []
            for name in ("profile-v1.md", "source-evidence.md"):
                path = directory / name
                data = ("Synthetic profile material: " + profile + " / " + name + "\r\n").encode()
                m.write_new(path, data)
                files.append(m.file_record(path, data, self.root))
            profile_materials[profile] = files
        jobs = [{"id": "synthetic-" + profile, "phase": "individual", "profile_id": profile, "input_sources": files}
                for profile, files in profile_materials.items()]
        m.write_new(self.run / "ALLOCATION.json", m.encode({"rows": rows}))
        m.write_new(self.run / "queue.json", m.encode({"jobs": jobs}))
        m.write_new(self.run / "RUBRIC.txt", b"SYNTHETIC COMMON RUBRIC\nUse the same criteria for every text.\n")
        bound = [self.run / n for n in ("ALLOCATION.json", "queue.json", "RUBRIC.txt")] + list((self.run / "blind").glob("*.md"))
        files = [m.file_record(path, path.read_bytes(), self.root) for path in bound]
        m.write_new(self.run / "START_RECEIPT.json", m.encode({"status": "SELECTION_INPUTS_ARCHIVED", "event_id": "event-synthetic-only", "files": files}))
        self.originals = {path: path.read_bytes() for path in bound + [self.run / "START_RECEIPT.json"]}

    def tearDown(self):
        self.temporary.cleanup()

    def pair(self, number=1, ids=("SYNTH_1", "SYNTH_2")):
        first, second = ids
        return {"pair_id": "P" + str(number).zfill(2), "candidate_ids": [first, second],
                "rationale": "ROOT_PRIVATE_RATIONALE: selected after separate review; never tell the worker.",
                "profiles": ["synthetic_one", "synthetic_two"],
                "order_by_role": {"N1": [first, second], "N2": [second, first], "N3": [first, second], "J1": [second, first], "J2": [first, second]}}

    def generate(self, pairs=None, batch="pairs-001"):
        plan = {"batch_id": batch, "pairs": pairs or [self.pair()]}
        plan_path = self.run / (batch + "-plan.json")
        m.write_new(plan_path, m.encode(plan))
        return m.prepare(plan_path, run_dir=self.run, root=self.root, template_dir=self.templates)

    def test_five_roles_share_configuration_and_expected_output(self):
        report = self.generate()
        queue = m.load((self.run / "pair-batches/pairs-001/queue.json").read_bytes())
        self.assertEqual(len(queue["jobs"]), 5)
        self.assertEqual([job["role"] for job in queue["jobs"]], list(m.ROLES))
        self.assertEqual([job["profile_id"] for job in queue["jobs"]], ["neutral"] * 3 + ["synthetic_one", "synthetic_two"])
        for job in queue["jobs"]:
            self.assertEqual((job["model"], job["effort"], job["service_tier"]), ("gpt-6-astra", "ultra", "default"))
            self.assertEqual(job["expected_output"], {"review_id": job["id"], "pair_id": "P01", "profile_id": job["profile_id"]})
            self.assertEqual(job["phase"], "pair")
            runner.check_job(job)
        self.assertEqual((report["jobs"], report["cumulative_pairs"], report["cumulative_jobs"]), (5, 1, 5))

    def test_full_literal_bytes_and_bibliographies_are_preserved(self):
        self.generate()
        queue = m.load((self.run / "pair-batches/pairs-001/queue.json").read_bytes())
        for job in queue["jobs"]:
            prompt = (self.root / job["prompt_file"]).read_bytes()
            for span in job["manuscript_spans"]:
                cid = "SYNTH_" + str(int(span["blind_id"][1:]))
                self.assertEqual(prompt[span["start_byte"]:span["end_byte"]], self.bodies[cid])
                self.assertIn(b"\r\nBibliography\r\n", prompt[span["start_byte"]:span["end_byte"]])
                self.assertEqual(m.sha(self.bodies[cid]), span["sha256"])
            self.assertEqual(m.sha(prompt), job["prompt_sha256"])

    def test_rationale_and_candidate_ids_never_enter_prompt(self):
        self.generate()
        for path in (self.run / "pair-batches/pairs-001/packets").glob("*.txt"):
            prompt = path.read_bytes()
            self.assertNotIn(b"ROOT_PRIVATE_RATIONALE", prompt)
            self.assertNotIn(b"SYNTH_1", prompt)
            self.assertNotIn(b"SYNTH_2", prompt)
        self.assertIn(b"ROOT_PRIVATE_RATIONALE", (self.run / "pair-batches/pairs-001/PAIR_PLAN.json").read_bytes())

    def test_profile_sources_only_reach_assigned_profile_role(self):
        self.generate()
        directory = self.run / "pair-batches/pairs-001/packets"
        for role in ("N1", "N2", "N3"):
            self.assertNotIn(b"Synthetic profile material:", (directory / ("P01-" + role + ".txt")).read_bytes())
        self.assertIn(b"Synthetic profile material: synthetic_one", (directory / "P01-J1.txt").read_bytes())
        self.assertNotIn(b"Synthetic profile material: synthetic_two", (directory / "P01-J1.txt").read_bytes())

    def test_same_profile_or_missing_order_is_rejected_before_output(self):
        for index, mutate in enumerate((lambda p: p.update(profiles=["synthetic_one"] * 2), lambda p: p["order_by_role"].pop("N3"))):
            pair = self.pair(); mutate(pair)
            with self.assertRaises(ValueError):
                self.generate([pair], "invalid-" + str(index))
        self.assertFalse((self.run / "pair-batches").exists())

    def test_unbalanced_order_is_rejected(self):
        pair = self.pair()
        pair["order_by_role"] = {role: pair["candidate_ids"] for role in m.ROLES}
        with self.assertRaises(ValueError):
            self.generate([pair])

    def test_duplicate_pair_reversed_is_rejected_across_batches(self):
        self.generate()
        with self.assertRaises(ValueError):
            self.generate([self.pair(2, ("SYNTH_2", "SYNTH_1"))], "pairs-002")
        self.assertFalse((self.run / "pair-batches/pairs-002").exists())

    def test_global_ten_pair_fifty_job_ceiling(self):
        combinations = list(itertools.combinations(self.bodies, 2))
        first = [self.pair(index + 1, ids) for index, ids in enumerate(combinations[:10])]
        report = self.generate(first)
        self.assertEqual((report["cumulative_pairs"], report["cumulative_jobs"]), (10, 50))
        with self.assertRaises(ValueError):
            self.generate([self.pair(11, combinations[10])], "pairs-002")

    def test_frozen_manuscript_or_profile_drift_stops_preparation(self):
        for filename in (self.run / "blind/M01.md", self.root / "research/judges/20261007/synthetic_one/source-evidence.md"):
            original = filename.read_bytes()
            filename.write_bytes(original + b"changed")
            with self.assertRaises(ValueError):
                self.generate(batch="drift-" + filename.stem)
            filename.write_bytes(original)
        self.assertFalse((self.run / "pair-batches").exists())

    def test_existing_batch_and_initial_inputs_remain_unchanged(self):
        self.generate()
        plan = self.run / "pairs-001-plan.json"
        before = {path: path.read_bytes() for path in (self.run / "pair-batches/pairs-001").rglob("*") if path.is_file()}
        with self.assertRaises(ValueError):
            m.prepare(plan, run_dir=self.run, root=self.root, template_dir=self.templates)
        for path, data in {**self.originals, **before}.items():
            self.assertEqual(path.read_bytes(), data)

    def test_no_dispatch_or_canonical_ready_receipt_created(self):
        report = self.generate()
        directory = self.run / "pair-batches/pairs-001"
        self.assertEqual(report["model_calls"], 0)
        self.assertEqual(report["archive_writes"], 0)
        self.assertFalse((directory / "START_RECEIPT.json").exists())
        self.assertFalse((directory / "PAIR_INPUT_RECEIPT.json").exists())
        self.assertFalse((self.run / "results").exists())

    def test_pair_schema_accepts_requested_shape_and_runner_quarantines_false(self):
        schema = m.load((self.templates / "pair-schema.template.json").read_bytes())
        value = {"review_id": "P01-N1", "pair_id": "P01", "profile_id": "neutral", "read_complete": True,
                 "thesis_a": "Synthetic thesis A", "thesis_b": "Synthetic thesis B", "comparison": {"argument": "A reason", "significance": "B reason", "originality": "Unknown"},
                 "concerns_a": [{"location": "Synthetic paragraph 1", "reason": "Synthetic concern", "reply": "Synthetic reply"}], "concerns_b": [],
                 "verdict": "tie", "confidence": "low", "reason_ru": ["Первое предложение.", "Второе предложение."], "limits": ["Synthetic-only test."]}
        runner.validate(value, schema)
        expected = {"id": "P01-N1", "expected_output": {"review_id": "P01-N1", "pair_id": "P01", "profile_id": "neutral"}}
        value["read_complete"] = False
        raw = json.dumps(value)
        self.assertEqual(runner.classify([{"text": raw}], [], raw, schema, job=expected)[0], runner.QUARANTINED)


if __name__ == "__main__":
    unittest.main(verbosity=2)
