"""Synthetic batch, interruption, and concurrency checks; not research evidence."""
import json
import multiprocessing
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import research_archive as module
from research_archive import Archive, ArchiveError


def request(kind="synthetic.record", **updates):
    value = {"kind": kind, "actor": {"id": "synthetic-actor", "role": "test"},
             "session_id": "synthetic-session", "run_id": "synthetic-run",
             "operation_id": "synthetic-operation", "attempt_id": "synthetic-attempt",
             "payload": {"synthetic": True}}
    value.update(updates)
    return value


def batch_writer(root, number):
    Archive(root).append_many([
        (request(id="shared"), "shared-delivery"),
        (request(id="worker-%d" % number, parents=["shared"]), "worker-%d" % number),
    ])


class ArchiveBatchTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="synthetic-archive-batch-")
        self.base = Path(self.temp.name).resolve()
        self.archive = Archive(self.base / "archive").init()

    def tearDown(self):
        self.temp.cleanup()

    def test_writer_views_include_pending_appends_and_reject_closed_use(self):
        with self.archive.writer() as writer:
            with mock.patch.object(self.archive, "_audit", wraps=self.archive._audit) as audit:
                writer.append(request(id="visible"), "visible")
                self.assertEqual(writer.view()["events"][0]["id"], "visible")
                self.assertIn("visible", writer.markdown())
                self.assertEqual(audit.call_count, 1)
        self.assertEqual(self.archive.view()["events"][0]["id"], "visible")
        with self.assertRaises(ArchiveError):
            writer.markdown()

    def test_batch_audits_and_reads_records_once_and_objects_once(self):
        digest = self.archive.put(b"synthetic exact bytes\r\n\x00\xff")
        self.archive.append(request(id="existing", inputs=[digest]), "existing-key")
        entries = [(request(id="new-%d" % n, inputs=[digest],
                            parents=["existing" if n == 0 else "new-%d" % (n - 1)]),
                    "new-key-%d" % n) for n in range(12)]
        with mock.patch.object(self.archive, "_audit", wraps=self.archive._audit) as audit, \
                mock.patch.object(self.archive, "_records", wraps=self.archive._records) as records, \
                mock.patch.object(self.archive, "get", wraps=self.archive.get) as get:
            result = self.archive.append_many(entries)
            self.assertEqual(audit.call_count, 1)
            self.assertEqual(records.call_count, 1)
            self.assertEqual(get.call_count, 1)
        self.assertEqual([e["sequence"] for e in result], list(range(2, 14)))
        self.assertEqual(self.archive.get(digest), b"synthetic exact bytes\r\n\x00\xff")
        self.assertTrue(self.archive.validate()["ok"])

    def test_events_reuses_one_fully_audited_read_of_each_event_file(self):
        expected = self.archive.append_many([(request(id="first"), "first-key"),
                                             (request(id="second", parents=["first"]), "second-key")])
        with mock.patch.object(self.archive, "_audit", wraps=self.archive._audit) as audit, \
                mock.patch.object(self.archive, "_records", wraps=self.archive._records) as records, \
                mock.patch.object(module, "_read", wraps=module._read) as reads:
            self.assertEqual(self.archive.events(), expected)
            self.assertEqual(audit.call_count, 1)
            self.assertEqual(records.call_count, 1)
            event_reads = [call.args[0].name for call in reads.call_args_list
                           if call.args[0].parent == self.archive.root / "events"]
            self.assertEqual(event_reads, ["000000000001.json", "000000000002.json"])

    def test_single_read_still_rejects_noncanonical_and_invalid_json_originals(self):
        event = self.archive.append(request(id="event"), "event-key")
        path = self.archive.root / "events" / "000000000001.json"
        for data, reason in [(json.dumps(event, indent=2).encode(), "not canonical"),
                             (b'{"synthetic":', "invalid JSON"), (b'\xff\xff', "invalid JSON")]:
            with self.subTest(reason=reason):
                path.chmod(0o600)
                path.write_bytes(data)
                report = self.archive.validate()
                self.assertFalse(report["ok"])
                self.assertTrue(any(reason in e["error"] for e in report["errors"]), report)
                with self.assertRaisesRegex(ArchiveError, "integrity"):
                    self.archive.events()

    def test_ordered_replay_retains_exact_bytes_and_does_not_modify_input(self):
        original = request(timestamp="2020-01-02T03:04:05+00:00")
        untouched = json.loads(json.dumps(original))
        first = self.archive.append(original, "original-key")
        entries = [(original, "original-key"),
                   (request(id="new", parents=[first["id"]]), "new-key"),
                   (original, "original-key")]
        result = self.archive.append_many(entries)
        files = {p.name: p.read_bytes() for p in (self.archive.root / "events").iterdir()}
        self.assertEqual(self.archive.append_many(entries), result)
        self.assertEqual(first, result[0])
        self.assertEqual(first, result[2])
        self.assertEqual(result[0]["recorded_at"], first["recorded_at"])
        self.assertEqual(files, {p.name: p.read_bytes() for p in (self.archive.root / "events").iterdir()})
        self.assertEqual(original, untouched)
        self.assertEqual(len(self.archive.events()), 2)

    def test_identical_duplicate_within_batch_returns_one_committed_event(self):
        value = request()
        result = self.archive.append_many([(value, "repeat"), (value, "repeat")])
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], result[1])
        self.assertEqual(self.archive.events(), [result[0]])

    def test_invalid_later_request_never_publishes_valid_prefix(self):
        existing = self.archive.append(request(id="existing"), "existing-key")
        valid = (request(id="valid"), "valid-key")
        invalid = [
            (request(payload={"changed": True}), "existing-key"),
            (request(id="existing"), "different-key"),
            (request(id="valid"), "duplicate-new-id"),
            (request(payload={"changed": True}), "valid-key"),
            (request(inputs=["0" * 64]), "missing-object"),
            (request(parents=["future"]), "missing-parent"),
            (request("candidate.merge", parents=["existing"]), "bad-merge"),
            (request("operation.completed"), "terminal-without-start"),
            (request(unknown_field=True), "unknown-field"),
            (request(sequence=99), "reserved-field"),
            (request(), ""),
        ]
        original_bytes = (self.archive.root / "events" / "000000000001.json").read_bytes()
        for bad in invalid:
            with self.subTest(key=bad[1]), mock.patch.object(module, "_publish") as publish:
                with self.assertRaises(ArchiveError):
                    self.archive.append_many([valid, bad])
                publish.assert_not_called()
            self.assertEqual(self.archive.events(), [existing])
            self.assertEqual((self.archive.root / "events" / "000000000001.json").read_bytes(), original_bytes)

    def test_forward_references_are_rejected_before_publication(self):
        with self.assertRaisesRegex(ArchiveError, "missing parent"):
            self.archive.append_many([(request(id="child", parents=["future"]), "child"),
                                      (request(id="future"), "future")])
        self.assertEqual(self.archive.events(), [])

    def test_started_terminal_transitions_and_retries(self):
        entries = [(request("operation.started", id="start"), "start-key"),
                   (request("operation.started", id="start"), "start-key"),
                   (request("operation.completed", id="terminal", parents=["start"]), "terminal-key")]
        result = self.archive.append_many(entries)
        self.assertEqual(self.archive.append_many(entries), result)
        self.assertEqual(self.archive.validate()["incomplete_attempts"], [])
        self.assertEqual(len(self.archive.events()), 2)
        with mock.patch.object(module, "_publish") as publish:
            with self.assertRaisesRegex(ArchiveError, "unterminated start"):
                self.archive.append_many([(request(id="valid"), "valid"),
                    (request("operation.interrupted", parents=["start"]), "second-terminal")])
            publish.assert_not_called()

    def test_invalid_batch_transitions_leave_no_unresolved_attempt(self):
        start = (request("operation.started", id="start"), "start")
        for change in ({"run_id": "other-run"}, {"parents": []}):
            bad = request("operation.completed", parents=["start"])
            bad.update(change)
            with self.assertRaises(ArchiveError):
                self.archive.append_many([start, (bad, "end")])
            self.assertEqual(self.archive.events(), [])
        with self.assertRaisesRegex(ArchiveError, "already started"):
            self.archive.append_many([start, (request("operation.started"), "start-again")])
        self.assertEqual(self.archive.validate()["incomplete_attempts"], [])

    def test_typed_timeline_validation_is_preserved(self):
        with mock.patch.object(module, "_publish") as publish:
            with self.assertRaisesRegex(ArchiveError, "typed timeline"):
                self.archive.append_many([(request(), "valid"),
                    (request("unknown.timeline", payload={"timeline_version": 1}), "bad")])
            publish.assert_not_called()

    def test_crash_before_or_after_publication_resumes_exact_committed_prefix(self):
        entries = [(request("operation.started", id="start"), "start-key"),
                   (request(id="middle", parents=["start"]), "middle-key"),
                   (request("operation.completed", parents=["start", "middle"]), "terminal-key")]
        for after in (False, True):
            archive = Archive(self.base / ("after" if after else "before")).init()
            publish = module._publish
            calls = 0

            def interrupted(path, data):
                nonlocal calls
                calls += 1
                if calls == 2:
                    if after:
                        publish(path, data)
                    raise OSError("synthetic publication interruption")
                publish(path, data)

            with mock.patch.object(module, "_publish", side_effect=interrupted):
                with self.assertRaisesRegex(OSError, "synthetic publication"):
                    archive.append_many(entries)
            prefix = archive.events()
            prefix_bytes = {p.name: p.read_bytes() for p in (archive.root / "events").iterdir()}
            self.assertEqual(len(prefix), 2 if after else 1)
            self.assertEqual(len(archive.validate()["incomplete_attempts"]), 1)
            completed = archive.append_many(entries)
            self.assertEqual(completed[:len(prefix)], prefix)
            for name, data in prefix_bytes.items():
                self.assertEqual((archive.root / "events" / name).read_bytes(), data)
            self.assertEqual(archive.events(), completed)
            self.assertEqual(archive.append_many(entries), completed)
            self.assertEqual(archive.validate()["incomplete_attempts"], [])

    def test_concurrent_batches_share_replays_without_duplicates(self):
        context = multiprocessing.get_context("fork")
        processes = [context.Process(target=batch_writer, args=(self.archive.root, n)) for n in range(5)]
        for process in processes:
            process.start()
        for process in processes:
            process.join(20)
            self.assertFalse(process.is_alive())
            self.assertEqual(process.exitcode, 0)
        events = self.archive.events()
        self.assertEqual(len(events), 6)
        self.assertEqual([e["sequence"] for e in events], list(range(1, 7)))
        self.assertEqual(events[0]["id"], "shared")
        self.assertTrue(self.archive.validate()["ok"])

    def test_scoped_omissions_reserve_ids_and_keys_and_frontier(self):
        self.archive.append_many([(request(id="included"), "included-key"),
                                  (request(id="omitted"), "omitted-key")])
        self.archive.export(self.base / "bundle", ["included"])
        imported = Archive.import_bundle(self.base / "bundle", self.base / "imported")
        for bad in [(request(), "omitted-key"), (request(id="omitted"), "fresh-key")]:
            with mock.patch.object(module, "_publish") as publish:
                with self.assertRaises(ArchiveError):
                    imported.append_many([(request(id="valid"), "valid"), bad])
                publish.assert_not_called()
        events = imported.append_many([(request(id="next", parents=["included"]), "next-key")])
        self.assertEqual(events[0]["sequence"], 3)
        self.assertTrue(imported.validate()["ok"])

    def test_corrupt_unreferenced_object_still_blocks_batch(self):
        digest = self.archive.put(b"synthetic orphan")
        path = self.archive.root / "objects" / digest
        path.chmod(0o600)
        path.write_bytes(b"corrupted")
        with mock.patch.object(module, "_publish") as publish:
            with self.assertRaisesRegex(ArchiveError, "integrity"):
                self.archive.append_many([(request(), "new")])
            publish.assert_not_called()

    def test_empty_batch_is_a_read_free_no_op(self):
        with mock.patch.object(self.archive, "_lock") as lock:
            self.assertEqual(self.archive.append_many([]), [])
            lock.assert_not_called()

    def test_writer_shares_one_full_audit_across_batches_and_new_objects(self):
        with mock.patch.object(self.archive, "_audit", wraps=self.archive._audit) as audit:
            with self.archive.writer() as writer:
                first = writer.append(request("operation.started", id="start"), "start")
                artifact = writer.put(b"synthetic object stored after audit")
                second = writer.append(request(id="middle", parents=["start"], outputs=[artifact]), "middle")
                final = writer.append(request("operation.completed", parents=["start"]), "end")
                self.assertEqual(writer.append(request("operation.started", id="start"), "start"), first)
                self.assertEqual(audit.call_count, 1)
            with self.archive.writer() as next_writer:
                self.assertEqual(next_writer.append(request(id="middle", parents=["start"], outputs=[artifact]), "middle"), second)
            self.assertEqual(audit.call_count, 2)
        self.assertEqual(self.archive.events(), [first, second, final])
        self.assertEqual(self.archive.validate()["incomplete_attempts"], [])

    def test_empty_writer_never_audits_and_writer_expires_on_exit(self):
        with mock.patch.object(self.archive, "_audit", wraps=self.archive._audit) as audit:
            with self.archive.writer() as writer:
                self.assertEqual(writer.append_many([]), [])
                self.assertEqual(audit.call_count, 0)
        with self.assertRaisesRegex(ArchiveError, "closed"):
            writer.append(request(), "too-late")
        with self.assertRaisesRegex(ArchiveError, "closed"):
            writer.put(b"synthetic forbidden after exit")
        self.assertEqual(self.archive.events(), [])

    def test_writer_reads_and_writes_share_one_audit_with_defensive_reads(self):
        original = self.archive.append(request(id="first"), "first")
        with mock.patch.object(self.archive, "_audit", wraps=self.archive._audit) as audit:
            with self.archive.writer() as writer:
                read = writer.events()
                read[0]["payload"]["synthetic"] = "external mutation"
                digest = writer.put(b"verified source bytes")
                with writer.writer() as borrowed:
                    self.assertIs(borrowed, writer)
                    second = borrowed.append(request(id="second", outputs=[digest]), "second")
                self.assertEqual(writer.events(), [original, second])
                self.assertEqual(writer.get(digest), b"verified source bytes")
                self.assertEqual(audit.call_count, 1)
            with self.archive.writer() as fresh:
                self.assertEqual(len(fresh.events()), 2)
                self.assertEqual(audit.call_count, 2)
        for operation in (writer.events, lambda: writer.get(digest)):
            with self.assertRaisesRegex(ArchiveError, "closed"):
                operation()

    def test_failed_writer_read_poisoning_and_reaudit_after_release(self):
        digest = self.archive.put(b"original")
        path = self.archive.root / "objects" / digest
        with self.archive.writer() as writer:
            writer.events()
            path.chmod(0o600)
            path.write_bytes(b"changed outside cooperating writer")
            with self.assertRaisesRegex(ArchiveError, "digest mismatch"):
                writer.get(digest)
            with self.assertRaisesRegex(ArchiveError, "failed"):
                writer.events()
        with self.archive.writer() as fresh:
            with self.assertRaisesRegex(ArchiveError, "integrity"):
                fresh.events()

    def test_writer_invalid_batch_poisoning_requires_fresh_audit(self):
        with self.archive.writer() as writer:
            first = writer.append(request(id="first"), "first")
            with self.assertRaisesRegex(ArchiveError, "missing parent"):
                writer.append_many([(request(id="uncommitted"), "uncommitted"),
                                    (request(parents=["missing"]), "invalid")])
            with self.assertRaisesRegex(ArchiveError, "failed"):
                writer.append(request(), "cannot-use-tainted-memory")
            with self.assertRaisesRegex(ArchiveError, "failed"):
                writer.put(b"synthetic cannot write after error")
        self.assertEqual(self.archive.events(), [first])
        with self.archive.writer() as writer:
            resumed = writer.append(request(id="resumed", parents=["first"]), "resumed")
        self.assertEqual(self.archive.events(), [first, resumed])

    def test_writer_partial_publication_poisoning_and_exact_retry(self):
        entries = [(request(id="first"), "first"), (request(id="second", parents=["first"]), "second")]
        publish = module._publish
        calls = 0

        def interrupted(path, data):
            nonlocal calls
            publish(path, data)
            calls += 1
            if calls == 1:
                raise OSError("synthetic uncertain publication")

        with self.archive.writer() as writer:
            with mock.patch.object(module, "_publish", side_effect=interrupted):
                with self.assertRaises(OSError):
                    writer.append_many(entries)
            with self.assertRaisesRegex(ArchiveError, "failed"):
                writer.append_many(entries)
        prefix = self.archive.events()
        self.assertEqual(len(prefix), 1)
        with self.archive.writer() as writer:
            result = writer.append_many(entries)
        self.assertEqual(result[:1], prefix)
        self.assertEqual(self.archive.events(), result)

    def test_writer_returns_defensive_copies_of_verified_state(self):
        with self.archive.writer() as writer:
            first = writer.append(request("operation.started", id="start"), "start")
            first["bindings"]["method"].append("0" * 64)
            first["payload"]["synthetic"] = "caller mutation"
            final = writer.append(request("operation.completed", parents=["start"]), "end")
            replay = writer.append(request("operation.started", id="start"), "start")
            self.assertEqual(replay["bindings"]["method"], [])
            self.assertIs(replay["payload"]["synthetic"], True)
        self.assertEqual(final["sequence"], 2)
        self.assertTrue(self.archive.validate()["ok"])

    def test_writer_lock_blocks_other_cooperating_writers(self):
        started, finished = threading.Event(), threading.Event()
        failures = []

        def other_writer():
            started.set()
            try:
                Archive(self.archive.root).append(request(id="other"), "other")
            except BaseException as exc:
                failures.append(exc)
            finally:
                finished.set()

        with self.archive.writer() as writer:
            writer.append(request(id="first"), "first")
            thread = threading.Thread(target=other_writer)
            thread.start()
            self.assertTrue(started.wait(2))
            self.assertFalse(finished.wait(0.05))
            writer.append(request(id="second"), "second")
        thread.join(5)
        self.assertFalse(thread.is_alive())
        self.assertEqual(failures, [])
        self.assertEqual([e["id"] for e in self.archive.events()], ["first", "second", "other"])

    def test_writer_cannot_be_used_from_another_thread(self):
        failures = []
        with self.archive.writer() as writer:
            def other_thread():
                try:
                    writer.append(request(), "wrong-thread")
                except ArchiveError as exc:
                    failures.append(str(exc))
            thread = threading.Thread(target=other_thread)
            thread.start()
            thread.join(2)
            self.assertFalse(thread.is_alive())
            self.assertEqual(len(failures), 1)
            self.assertIn("another thread", failures[0])
            writer.append(request(id="owner"), "owner")
        self.assertEqual([e["id"] for e in self.archive.events()], ["owner"])


if __name__ == "__main__":
    unittest.main()
