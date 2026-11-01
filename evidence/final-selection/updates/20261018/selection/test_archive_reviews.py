"""Synthetic only: no model, live session, or canonical archive access."""
from pathlib import Path
import importlib.util
import json
import tempfile
import unittest
from contextlib import contextmanager
from unittest import mock

spec = importlib.util.spec_from_file_location("selection_archive_under_test", Path(__file__).with_name("archive_reviews.py"))
a = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)
SID = "00000000-0000-0000-0000-000000000001"


def jsonl(value):
    return (json.dumps(value, ensure_ascii=False) + "\n").encode()


def message(text="Visible text", role="user", phase=None):
    return {"type": "response_item", "timestamp": "2026-10-18T00:00:00Z",
            "payload": {"type": "message", "id": "synthetic-visible", "role": role, "phase": phase,
                        "content": [{"type": "input_text" if role == "user" else "output_text", "text": text,
                                     "annotations": ["SECRET_ANNOTATION"], "logprobs": "SECRET_LOGPROBS"}],
                        "internal_chat_message_metadata_passthrough": {"opaque": "SECRET_PASSTHROUGH"}}}


class Fragments(unittest.TestCase):
    def test_exact_token_keeps_native_escapes_and_structural_location(self):
        raw = b'{"text":"wrong","payload":{"content":[{"type":"input_text","text":"A\\u0020B\\n\\\"q\\\""}]}}\n'
        token = a.string_token(raw, ["payload", "content", 0, "text"])
        self.assertEqual(token, b'"A\\u0020B\\n\\\"q\\\""')
        self.assertEqual(json.loads(token), 'A B\n"q"')

    def test_duplicate_keys_rejected(self):
        with self.assertRaises(ValueError):
            a.string_token(b'{"text":"a","text":"b"}', ["text"])

    def test_known_opaque_metadata_never_in_fragment(self):
        obj = message()
        tokens = a.fragment(a.encode(obj), {"role": "user", "text": "Visible text"})
        self.assertEqual(tokens, [b'"Visible text"'])
        self.assertNotIn(b"SECRET", b"".join(tokens))

    def test_assistant_visible_final_supported(self):
        obj = message("Final", "assistant", "final_answer")
        self.assertEqual(a.fragment(a.encode(obj), {"role": "assistant", "phase": "final_answer", "text": "Final"}), [b'"Final"'])

    def test_hidden_phase_and_channel_rejected(self):
        for phase, channel in (("analysis", None), ("final", "analysis")):
            obj = message("Hidden", "assistant", phase)
            obj["payload"]["channel"] = channel
            with self.assertRaises(a.AcceptanceGap):
                a.fragment(a.encode(obj), {"role": "assistant", "phase": phase, "text": "Hidden"})

    def test_unknown_content_key_and_type_rejected(self):
        for key, value in (("unknown_field", "SECRET"), ("type", "image")):
            obj = message()
            obj["payload"]["content"][0][key] = value
            with self.assertRaises(a.AcceptanceGap):
                a.fragment(a.encode(obj), {"role": "user", "text": "Visible text"})

    def test_plaintext_mismatch_rejected(self):
        with self.assertRaises(a.AcceptanceGap):
            a.fragment(a.encode(message()), {"role": "user", "text": "Different"})

    def test_multiple_blocks_are_exact_and_not_reserialized(self):
        obj = message("One")
        obj["payload"]["content"].append({"type": "input_text", "text": "Two"})
        self.assertEqual(a.fragment(a.encode(obj), {"role": "user", "text": "One\nTwo"}), [b'"One"', b'"Two"'])

    def test_freeze_selected_known_records_without_archive_access(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            source, destination = root / "synthetic.jsonl", root / "fragments"
            header = jsonl({"type": "session_meta", "payload": {"id": SID, "cwd": str(root), "private": "SECRET_META"}})
            raw = jsonl(message("Привет\nworld"))
            source.write_bytes(header + raw)
            selections = [{"line": 2, "role": "user", "text": "Привет\nworld", "record_sha256": a.sha(raw)}]
            with mock.patch.object(a, "resolve_session", return_value=source), mock.patch.object(a, "Archive", side_effect=AssertionError("NO ARCHIVE ACCESS")):
                result = a.freeze_visible_fragments(SID, root, selections, destination)
                again = a.freeze_visible_fragments(SID, root, selections, destination)
            self.assertEqual(result, again)
            self.assertEqual(result["status"], "EXACT_VISIBLE_JSON_STRING_FRAGMENTS")
            self.assertFalse(result["full_provider_capture"])
            all_bytes = b"".join(p.read_bytes() for p in destination.iterdir())
            self.assertNotIn(b"SECRET", all_bytes)
            token = (destination / "line-2-part-0.json-string.txt").read_bytes()
            self.assertEqual(json.loads(token), "Привет\nworld")

    def test_freeze_wrong_hash_rejected_before_any_output(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            source = root / "synthetic.jsonl"
            source.write_bytes(jsonl({"type": "session_meta", "payload": {"id": SID, "cwd": str(root)}}) + jsonl(message()))
            with mock.patch.object(a, "resolve_session", return_value=source):
                with self.assertRaises(a.AcceptanceGap):
                    a.freeze_visible_fragments(SID, root, [{"line": 2, "role": "user", "text": "Visible text", "record_sha256": "0" * 64}], root / "no-output")
            self.assertFalse((root / "no-output").exists())

    def test_individual_and_pair_versions_keep_exact_order(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            mapping = {}
            for number in (1, 2):
                path = root / (str(number) + ".md")
                path.write_text("synthetic " + str(number))
                mapping["E" + str(number)] = {"blind_id": "M" + str(number), "assigned_entry": "assigned:" + str(number),
                    "assigned_event": "event:" + str(number), "entity": "essay:" + str(number),
                    "version": {"path": path.name, "sha256": a.sha(path.read_bytes())}}
            one = a.versions_for({"phase": "individual", "manuscript_id": "M1"}, mapping, root)
            self.assertEqual(one[0]["entry_id"], "assigned:1")
            pair = {"phase": "pair", "pair_candidates": ["E1", "E2"], "ordered_blind_ids": ["M2", "M1"],
                    "expected_output": {"pair_id": "P01"}, "rubric_file": "rubric.txt", "rubric_sha256": "a" * 64}
            self.assertEqual([v["candidate"] for v in a.versions_for(pair, mapping, root)], ["E2", "E1"])
            del pair["ordered_blind_ids"]
            with self.assertRaisesRegex(a.AcceptanceGap, "PAIR_ARCHIVE_EXTENSION_REQUIRED"):
                a.versions_for(pair, mapping, root)

    def test_immutable_receipt_refuses_changed_replay(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            path = root / "receipt.json"
            a.save_once(path, {"a": 1}, root)
            a.save_once(path, {"a": 1}, root)
            with self.assertRaises(a.AcceptanceGap):
                a.save_once(path, {"a": 2}, root)


class FakeArchive:
    """In-memory fake. Never opens a real Archive or writes canonical files."""
    def __init__(self, events, objects):
        self.records, self.objects, self.deliveries, self.writer_count = events, objects, {}, 0

    @contextmanager
    def writer(self):
        self.writer_count += 1
        yield self

    def events(self):
        return list(self.records)

    def put(self, data):
        digest = a.sha(data)
        self.objects[digest] = data
        return digest

    def get(self, digest):
        return self.objects[digest]

    def append(self, request, delivery_key):
        if delivery_key in self.deliveries:
            old = self.deliveries[delivery_key]
            assert {k: v for k, v in old.items() if k not in {"id", "delivery_key"}} == request
            return old
        event = {**request, "id": "event-" + a.sha(a.encode(request))[:24], "delivery_key": delivery_key}
        self.records.append(event)
        self.deliveries[delivery_key] = event
        return event


class Batch(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name).resolve()
        self.run = self.root / "runs" / "selection"
        self.attempt = self.run / "results" / "M01-N1" / "attempt-001"
        self.attempt.mkdir(parents=True)
        self.prompt = "Synthetic frozen packet\n"
        self.value = {"review_id": "M01-N1", "manuscript_id": "M01", "profile_id": "neutral", "read_complete": True,
                      "recommendation": "borderline", "reason_ru": ["Первый конкретный довод.", "Второй конкретный довод."]}
        self.manuscript = self.root / "manuscript.md"
        self.manuscript.write_text("Synthetic complete manuscript")
        self.mapping = {"E001": {"blind_id": "M01", "entity": "essay/E001", "assigned_entry": "assigned:E001", "assigned_event": "event-assigned",
                      "version": {"path": "manuscript.md", "sha256": a.sha(self.manuscript.read_bytes())}}}
        self.mapping_file = self.run / "LINEAGE_INPUTS.json"
        self.mapping_file.write_bytes(a.encode(self.mapping))
        for name in ("archive_reviews.py", "CAPTURE_METHOD.md", "test_archive_reviews.py", "RUBRIC.txt"):
            (self.run / name).write_text("Synthetic frozen " + name)
        (self.run / "prompt.txt").write_text(self.prompt)
        (self.run / "schema.json").write_bytes(a.encode({"type": "object"}))
        self.job = {"id": "M01-N1", "phase": "individual", "role": "N1", "manuscript_id": "M01", "profile_id": "neutral",
                    "model": "gpt-6-astra", "effort": "ultra", "service_tier": "default",
                    "prompt_file": "runs/selection/prompt.txt", "prompt_sha256": a.sha(self.prompt.encode()),
                    "schema_file": "runs/selection/schema.json", "schema_sha256": a.sha((self.run / "schema.json").read_bytes())}
        (self.run / "queue.json").write_bytes(a.encode({"jobs": [self.job]}))
        final = json.dumps(self.value, ensure_ascii=False)
        rows = [jsonl({"type": "session_meta", "payload": {"id": SID, "cwd": str(self.root)}}),
                jsonl({"type": "turn_context", "payload": {"model": "gpt-6-astra", "effort": "ultra", "service_tier": "default"}}),
                jsonl(message(self.prompt)), jsonl(message(final, "assistant", "final"))]
        self.native = a.runner.native_records(rows, SID, self.prompt, self.job, self.root)
        self.source = self.root / "native.jsonl"
        self.source.write_bytes(b"".join(rows))
        argv = a.runner.command(self.job, self.attempt, self.root, executable="/synthetic/codex")
        self.receipt = {"job_id": self.job["id"], "session_id": SID, "prompt_sha256": self.job["prompt_sha256"], "schema_sha256": self.job["schema_sha256"],
                        "requested_model": "gpt-6-astra", "requested_effort": "ultra", "requested_service_tier": "default", "argv": argv,
                        "argv_sha256": a.sha(json.dumps(argv, separators=(",", ":")).encode()), "status": a.runner.COMPLETE,
                        "quality_flags": [], "cli_exit_code": 0, "completed_at": "2026-10-18T00:00:00+00:00"}
        (self.attempt / "launch.json").write_bytes(a.encode(self.receipt))
        (self.attempt / "native-check.json").write_bytes(a.encode(self.native[0]))
        (self.attempt / "native-visible.json").write_bytes(a.encode({"session_id": SID, "records": self.native[1]}))
        (self.attempt / "stderr.json").write_bytes(a.encode({"lines": [], "exit_code": 0}))
        (self.attempt / "visible-events.jsonl").write_bytes(jsonl({"type": "thread.started", "thread_id": SID}) + jsonl({"type": "turn.completed"}))
        (self.attempt / "final.txt").write_text(final)
        (self.attempt / "response.json").write_bytes(a.encode(self.value))
        self.receipt["outputs"] = {str(p.relative_to(self.root)): a.sha(p.read_bytes()) for p in self.attempt.iterdir()}
        (self.attempt / "receipt.json").write_bytes(a.encode(self.receipt))
        self.start = {"event_id": "event-ready", "bindings": {}, "files": [{"path": str(p.relative_to(self.root)), "sha256": a.sha(p.read_bytes())} for p in self.run.iterdir() if p.is_file()]}
        parent = a.base_entry("assigned:E001", "essay/E001", "selection", "Synthetic assignment")
        parent["artifacts"] = [{"path": "manuscript.md", "sha256": self.mapping["E001"]["version"]["sha256"], "role": "frozen-candidate"}]
        self.fake = FakeArchive([
            {"id": "event-ready", "kind": "research.selection.ready", "outputs": [a.sha(self.mapping_file.read_bytes())]},
            {"id": "event-assigned", "kind": "essay.lineage.entry", "payload": {"protocol": "essay-lineage.v1", "entry": parent}}], {})

    def tearDown(self):
        self.temporary.cleanup()

    @contextmanager
    def patches(self):
        with mock.patch.object(a.runner, "gate", return_value=(self.start, [self.job])), \
             mock.patch.object(a.runner, "inspect_native", return_value=self.native), \
             mock.patch.object(a, "resolve_session", return_value=self.source), \
             mock.patch.object(a, "Archive", return_value=self.fake), \
             mock.patch.object(a.runner.subprocess, "Popen", side_effect=AssertionError("NO MODEL CALL")):
            yield

    def test_full_acceptance_uses_one_fake_writer_and_replays_without_duplicate_reviews(self):
        with self.patches():
            result = a.accept_batch(["M01-N1"], "b1", run_dir=self.run, root=self.root)
            again = a.accept_batch(["M01-N1"], "b1", run_dir=self.run, root=self.root)
        self.assertEqual(result, again)
        self.assertEqual(self.fake.writer_count, 2)
        reviews = [e for e in self.fake.records if e["kind"] == "research.selection.review.completed"]
        self.assertEqual(len(reviews), 1)
        accepted = a.load(self.run / "results/M01-N1/ARCHIVE_RECEIPT.json", self.root)
        self.assertEqual(accepted["status"], "REVIEW_ARCHIVED")
        self.assertNotIn("SECRET", json.dumps(self.fake.records))
        self.assertNotIn(b"SECRET", b"".join(self.fake.objects.values()))
        lineage = [e for e in self.fake.records if e["kind"] == "essay.lineage.entry" and e["id"] != "event-assigned"][0]
        self.assertEqual(lineage["payload"]["entry"]["assessment"]["order"], ["assigned:E001"])

    def test_check_only_never_opens_writer_or_creates_acceptance(self):
        with self.patches():
            result = a.accept_batch(["M01-N1"], "b1", check_only=True, run_dir=self.run, root=self.root)
        self.assertEqual(result["status"], "CHECK_ONLY_PASSED_NO_ARCHIVE_WRITES")
        self.assertEqual(self.fake.writer_count, 0)
        self.assertFalse((self.run / "results/M01-N1/ARCHIVE_RECEIPT.json").exists())

    def test_output_drift_rejected_before_writer(self):
        (self.attempt / "response.json").write_text("{}")
        with self.patches(), self.assertRaises(ValueError):
            a.accept_batch(["M01-N1"], "b1", run_dir=self.run, root=self.root)
        self.assertEqual(self.fake.writer_count, 0)

    def test_unknown_native_block_prevents_acceptance(self):
        changed = jsonl(message(self.prompt))
        obj = json.loads(changed)
        obj["payload"]["content"][0]["unrecognized"] = "SECRET"
        rows = self.source.read_bytes().splitlines(keepends=True)
        rows[2] = jsonl(obj)
        self.source.write_bytes(b"".join(rows))
        self.native = a.runner.native_records(rows, SID, self.prompt, self.job, self.root)
        (self.attempt / "native-check.json").write_bytes(a.encode(self.native[0]))
        (self.attempt / "native-visible.json").write_bytes(a.encode({"session_id": SID, "records": self.native[1]}))
        self.receipt["outputs"] = {str(p.relative_to(self.root)): a.sha(p.read_bytes()) for p in self.attempt.iterdir() if p.name != "receipt.json"}
        (self.attempt / "receipt.json").write_bytes(a.encode(self.receipt))
        with self.patches(), self.assertRaisesRegex(a.AcceptanceGap, "Unsupported native content block"):
            a.accept_batch(["M01-N1"], "b1", run_dir=self.run, root=self.root)
        self.assertEqual(self.fake.writer_count, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
