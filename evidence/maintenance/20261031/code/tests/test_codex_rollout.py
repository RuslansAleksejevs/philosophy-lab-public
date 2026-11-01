"""Synthetic compressed-rollout regression tests; never reads user sessions."""
import hashlib
import builtins
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import codex_rollout as reader
from capture_codex import capture
from collector import Collector, coverage_summary
import test_capture_codex as capture_fixtures
from test_capture_codex import SESSION as CAPTURE_SESSION, message as capture_message
import test_collector as collector_fixtures
from test_collector import SESSION, message, line

try:
    from compression import zstd
except ImportError:
    zstd = None


@unittest.skipIf(zstd is None, "compression fixtures need Python 3.14+ to encode zstd")
class RolloutReaderTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="synthetic-rollout-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.path = self.root / "rollout.jsonl"
        self.packed = self.path.with_name(self.path.name + ".zst")
        self.data = b'{"first":"same original bytes"}\n{"second":2}\n'

    def pack(self, data=None):
        self.packed.write_bytes(zstd.compress(self.data if data is None else data))

    def test_missing_plain_uses_exact_compressed_sibling_with_logical_offsets(self):
        self.pack()
        with reader.rollout_file(self.path) as source:
            self.assertEqual(source.logical_name, self.path.name)
            self.assertEqual(source.logical_stat().st_size, len(self.data))
            first = source.readline()
            self.assertEqual(source.tell(), len(first))
            source.seek(0)
            self.assertEqual(source.read(), self.data)
        with reader.rollout_file(self.packed) as source:
            self.assertEqual(source.read(), self.data)

    def test_plain_wins_when_both_exist(self):
        self.path.write_bytes(b"plain\n")
        self.pack()
        with reader.rollout_file(self.path) as source:
            self.assertEqual(source.read(), b"plain\n")
            self.assertEqual(source.storage_signature()["encoding"], "plain")

    def test_storage_inspection_does_not_decode(self):
        self.pack()
        with mock.patch.object(reader, "_decode_zstd", side_effect=AssertionError("must not decode")):
            with reader.rollout_file(self.path) as source:
                self.assertEqual(source.storage_signature()["bytes"], self.packed.stat().st_size)

    def test_bounded_output_rejects_high_compression_ratio(self):
        self.pack(b"x" * 100_000)
        with self.assertRaisesRegex(ValueError, "bounded uncompressed"):
            with reader.rollout_file(self.path, max_bytes=100) as source:
                source.read()

    def test_complete_frames_required_and_trailing_garbage_rejected(self):
        good = zstd.compress(self.data)
        for bad in (b"", good[:-1], good + b"garbage", good + zstd.compress(b"more")[:-1]):
            with self.subTest(size=len(bad)):
                self.packed.write_bytes(bad)
                with self.assertRaisesRegex(ValueError, "invalid or truncated"):
                    with reader.rollout_file(self.path) as source:
                        source.read()

    def test_concatenated_frames_preserve_exact_bytes(self):
        self.packed.write_bytes(zstd.compress(self.data[:10]) + zstd.compress(self.data[10:]))
        with reader.rollout_file(self.path) as source:
            self.assertEqual(source.read(), self.data)

    def test_symlink_plain_never_falls_back_to_safe_sibling(self):
        self.pack()
        self.path.symlink_to(self.root / "absent")
        with self.assertRaisesRegex(ValueError, "symlink"):
            with reader.rollout_file(self.path):
                self.fail("unsafe source opened")

    def test_compressed_symlink_and_symlink_ancestor_are_rejected(self):
        real = self.root / "real.zst"
        real.write_bytes(zstd.compress(self.data))
        self.packed.symlink_to(real)
        with self.assertRaisesRegex(ValueError, "symlink"):
            with reader.rollout_file(self.path):
                self.fail("unsafe source opened")
        self.packed.unlink()
        self.pack()
        alias = self.root / "alias"
        alias.symlink_to(self.root, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symlink"):
            with reader.rollout_file(alias / self.path.name):
                self.fail("unsafe ancestor opened")

    def test_parent_traversal_and_special_file_are_rejected(self):
        self.pack()
        with self.assertRaisesRegex(ValueError, "traversal"):
            with reader.rollout_file(self.root / "unused" / ".." / self.path.name):
                self.fail("traversal opened")
        self.packed.unlink()
        os.mkfifo(self.packed)
        with self.assertRaisesRegex(ValueError, "regular"):
            with reader.rollout_file(self.path):
                self.fail("FIFO opened")

    def test_in_place_mutation_and_replacement_fail_before_return(self):
        for replace in (False, True):
            with self.subTest(replace=replace):
                self.pack()
                with self.assertRaisesRegex(ValueError, "mutated|replaced"):
                    with reader.rollout_file(self.path) as source:
                        self.assertEqual(source.read(), self.data)
                        if replace:
                            replacement = self.root / "replacement"
                            replacement.write_bytes(self.packed.read_bytes())
                            replacement.replace(self.packed)
                        else:
                            self.packed.write_bytes(zstd.compress(b"changed"))

    def test_compressed_replacement_by_symlink_is_rejected_on_exit(self):
        self.pack()
        with self.assertRaisesRegex(ValueError, "symlink|mutated"):
            with reader.rollout_file(self.path) as source:
                source.read()
                self.packed.unlink()
                self.packed.symlink_to(self.root / "absent")

    def test_missing_only_checks_exact_sibling(self):
        (self.root / "unrelated.jsonl.zst").write_bytes(zstd.compress(self.data))
        with self.assertRaisesRegex(ValueError, "unavailable"):
            with reader.rollout_file(self.path):
                self.fail("unrelated file selected")

    @unittest.skipUnless(reader.shutil.which("zstd"), "optional local zstd not installed")
    def test_cli_fallback_preserves_bytes_and_rejects_truncation_and_size_limit(self):
        original_import = builtins.__import__
        def old_runtime(name, *args, **kwargs):
            if name == "compression":
                raise ImportError("synthetic pre-3.14 runtime")
            return original_import(name, *args, **kwargs)
        self.pack()
        with mock.patch.object(builtins, "__import__", side_effect=old_runtime):
            with reader.rollout_file(self.path) as source:
                self.assertEqual(source.read(), self.data)
            with self.assertRaisesRegex(ValueError, "bounded uncompressed"):
                with reader.rollout_file(self.path, max_bytes=5) as source:
                    source.read()
            self.packed.write_bytes(self.packed.read_bytes()[:-1])
            with self.assertRaisesRegex(ValueError, "invalid or truncated"):
                with reader.rollout_file(self.path) as source:
                    source.read()


@unittest.skipIf(zstd is None, "compression fixtures need Python 3.14+")
class CompressedCaptureTests(unittest.TestCase):
    def setUp(self):
        self.fx = capture_fixtures.CaptureTests()
        self.fx.setUp()
        self.addCleanup(self.fx.tearDown)
        self.data = self.fx.head + capture_message("user", "Original αβ\nexact spaces  ")
        self.fx.source.write_bytes(self.data)
        self.packed = self.fx.source.with_name(self.fx.source.name + ".zst")

    def pack(self, data=None):
        self.packed.write_bytes(zstd.compress(self.data if data is None else data))
        self.fx.source.unlink(missing_ok=True)

    def take(self, source=None, **kwargs):
        return capture(self.fx.archive, source or self.fx.source, CAPTURE_SESSION,
                       self.fx.root, end_line=2, **kwargs)

    def test_same_capture_after_compression_reuses_originals_and_report(self):
        before = self.take()
        self.pack()
        self.assertEqual(self.take(), before)
        self.assertEqual(self.take(self.packed), before)
        self.assertEqual(before["source_snapshot_sha256"], hashlib.sha256(self.data).hexdigest())

    def test_capture_limit_applies_to_expanded_bytes(self):
        self.pack()
        with self.assertRaisesRegex(ValueError, "bounded uncompressed"):
            self.take(max_bytes=len(self.data) - 1)
        self.assertFalse(self.fx.archive.exists())

    def test_truncated_frame_is_rejected_even_if_selected_lines_would_be_decoded(self):
        self.pack()
        self.packed.write_bytes(self.packed.read_bytes()[:-1])
        with self.assertRaisesRegex(ValueError, "invalid or truncated"):
            self.take()
        self.assertFalse(self.fx.archive.exists())

    def test_wrong_identity_is_still_rejected_before_archive(self):
        self.pack(self.data.replace(CAPTURE_SESSION.encode(), b"other-session-0000000"))
        with self.assertRaisesRegex(ValueError, "identity"):
            self.take()
        self.assertFalse(self.fx.archive.exists())


@unittest.skipIf(zstd is None, "compression fixtures need Python 3.14+")
class CompressedCollectorTests(unittest.TestCase):
    def setUp(self):
        self.fx = collector_fixtures.CollectorTests()
        self.fx.setUp()
        self.addCleanup(self.fx.tearDown)
        self.fx.add_bytes(message("user", "Original AAA"))
        self.data = self.fx.source.read_bytes()
        self.packed = self.fx.source.with_name(self.fx.source.name + ".zst")
        self.collector = Collector(self.fx.root)

    def pack(self, data=None):
        self.packed.write_bytes(zstd.compress(self.data if data is None else data))
        self.fx.source.unlink(missing_ok=True)

    def test_transition_preserves_cursor_originals_and_does_not_decode_on_next_poll(self):
        self.collector.collect()
        originals = self.fx.events("capture.raw_record")
        self.pack()
        result = self.collector.collect()
        self.assertEqual(result["status"], "RUNNING")
        cursor = self.fx.cursor()
        self.assertEqual(cursor["offset"], len(self.data))
        self.assertEqual(cursor["observed_size"], len(self.data))
        self.assertEqual(cursor["prefix_sha256"], hashlib.sha256(self.data).hexdigest())
        self.assertEqual(self.fx.events("capture.raw_record"), originals)
        with mock.patch.object(reader, "_decode_zstd", side_effect=AssertionError("unnecessary decode")):
            self.assertEqual(self.collector.collect()["status"], "RUNNING")
        self.assertEqual(self.fx.cursor(), cursor)

    def test_compressed_extension_resumes_at_uncompressed_boundary(self):
        self.collector.collect()
        self.pack(self.data + message("assistant", "Later", phase="final"))
        self.assertEqual(self.collector.collect()["status"], "RUNNING")
        self.assertEqual(self.fx.cursor()["counts"], {"user_prompts": 1, "assistant_final": 1})
        self.assertEqual(len(self.fx.events("capture.raw_record")), 2)
        self.collector.collect(reconcile=True)
        self.assertEqual(len(self.fx.events("capture.raw_record")), 2)

    def test_same_mtime_recompression_stores_new_physical_identity_then_skips(self):
        self.pack()
        self.collector.collect()
        stamp = self.packed.stat()
        self.packed.write_bytes(zstd.compress(self.data, level=1))
        os.utime(self.packed, ns=(stamp.st_atime_ns, stamp.st_mtime_ns))
        self.assertEqual(self.collector.collect()["status"], "RUNNING")
        self.assertEqual(self.fx.cursor()["source_storage"]["ctime_ns"], self.packed.stat().st_ctime_ns)
        with mock.patch.object(reader, "_decode_zstd", side_effect=AssertionError("unnecessary decode")):
            self.assertEqual(self.collector.collect()["status"], "RUNNING")

    def test_valid_compressed_truncation_or_changed_prefix_preserves_history(self):
        self.collector.collect()
        prior = self.fx.events()
        cursor = self.fx.cursor()
        for data, error in ((self.data[:self.data.index(b"\n") + 1], "truncated"),
                            (self.data.replace(b"AAA", b"BBB"), "prefix changed")):
            with self.subTest(error=error):
                self.pack(data)
                result = self.collector.collect()
                self.assertEqual(result["status"], "ERROR")
                self.assertIn(error, result["sessions"][0]["error"])
                self.assertEqual(self.fx.events(), prior)
                self.assertEqual(self.fx.cursor(), cursor)
                self.assertFalse(result["coverage_healthy"])

    def test_corrupt_compressed_source_cannot_commit_partial_prefix(self):
        self.pack()
        prior = self.fx.events()
        self.packed.write_bytes(self.packed.read_bytes()[:-1])
        result = self.collector.collect()
        self.assertEqual(result["status"], "ERROR")
        self.assertIn("invalid or truncated", result["sessions"][0]["error"])
        self.assertEqual(self.fx.events(), prior)

    def test_partial_json_line_remains_gap_in_complete_frame_then_resumes(self):
        tail = message("assistant", "later", phase="final")
        self.pack(self.data + tail[:-3])
        first = self.collector.collect()
        self.assertFalse(first["coverage_healthy"])
        self.assertEqual(self.fx.cursor()["offset"], len(self.data))
        self.pack(self.data + tail)
        self.assertTrue(self.collector.collect()["coverage_healthy"])
        self.assertEqual(len(self.fx.events("capture.raw_record")), 2)

    def test_review_hash_and_line_are_over_uncompressed_bytes(self):
        from collector_review_tools import review
        tool = line({"type": "function_call", "name": "synthetic", "call_id": "synthetic-call",
                     "arguments": "safe synthetic input"})
        self.pack(self.data + tool)
        self.collector.collect()
        sha = hashlib.sha256(tool).hexdigest()
        self.assertEqual(review(self.fx.root, SESSION, 3, sha)["sha256"], sha)
        self.collector.collect()
        self.assertEqual(self.fx.cursor()["pending_tools"], 0)
        raw = self.fx.events("capture.raw_record")
        self.assertEqual(len(raw), 2)
        self.assertEqual(self.fx.archive.get(raw[-1]["outputs"][0]), tool)


class ErrorCoverageTests(unittest.TestCase):
    def test_error_counts_keep_known_cursor_gaps_and_pending_reviews(self):
        summary = coverage_summary([
            {"session_id": "failed", "status": "ERROR", "last_committed_cursor": {
                "gaps": [{"reason": "schema", "surface": "tools"}], "pending_tools": 3}},
            {"session_id": "unseen", "status": "ERROR"},
            {"session_id": "okay", "status": "CAUGHT_UP", "gaps": [], "pending_tool_records": 2}])
        self.assertFalse(summary["coverage_healthy"])
        self.assertEqual(summary["unresolved_gap_count"], 1)
        self.assertEqual(summary["tool_schema_gap_count"], 1)
        self.assertEqual(summary["pending_tool_records"], 5)
        self.assertEqual(summary["sessions_with_errors"], 2)
        self.assertEqual(summary["error_sessions_without_cursor"], 1)

    def test_error_without_gap_is_never_healthy(self):
        self.assertFalse(coverage_summary([{"session_id": "failed", "status": "ERROR"}])
                         ["coverage_healthy"])


if __name__ == "__main__":
    unittest.main()
