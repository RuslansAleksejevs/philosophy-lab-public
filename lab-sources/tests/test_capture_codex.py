"""Synthetic compatibility/adversarial tests; these are not real provider captures."""
import json
import os
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
from capture_codex import capture, resolve_session, reuse_existing_marker
from research_archive import Archive, ArchiveError

SESSION = "synthetic-session-0001"


def line(payload, record_type="response_item", metadata=None):
    record = {"timestamp": "2026-09-07T00:00:00Z", "ordinal": 0,
              "type": record_type, "payload": payload}
    if metadata is not None:
        record["metadata"] = metadata
    return (json.dumps(record, ensure_ascii=False) + "\n").encode()


def message(role, text, phase=None, kinds=None):
    payload = {"type": "message", "id": "m", "role": role,
               "content": [{"type": "input_text" if role == "user" else "output_text", "text": text}],
               "internal_chat_message_metadata_passthrough": {"content_item_kinds": kinds or ["user.text"]}}
    if phase:
        payload["phase"] = phase
    return line(payload)


class CaptureTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        # macOS /tmp is a symlink; use its canonical permitted temp location.
        self.root = Path(self.temp.name).resolve()
        self.source = self.root / "synthetic.jsonl"
        self.archive = self.root / "research/archive"
        self.identify_lab(self.root)
        self.head = line({"id": SESSION, "cwd": str(self.root),
                          "base_instructions": "SYNTHETIC_HIDDEN_SENTINEL"}, "session_meta")

    @staticmethod
    def identify_lab(root):
        root.mkdir(parents=True, exist_ok=True)
        (root / ".lab").mkdir(exist_ok=True)
        (root / "LAB_PROFILE.json").write_text(json.dumps({"lab": {"kind": "PHILOSOPHY_PROGRAM"}}))
        (root / ".lab/philosophy.json").write_text(json.dumps({"schema_version": 1, "kernel": "philosophy.v1", "archive_format": "research-archive.v1"}))

    def tearDown(self):
        self.temp.cleanup()

    def test_live_writer_capture_reuses_one_audit_and_rejects_wrong_or_expired_writer(self):
        self.source.write_bytes(self.head + message('assistant', 'Synthetic visible evidence', phase='commentary'))
        archive = Archive(self.archive).init()
        with patch.object(archive, '_audit', wraps=archive._audit) as audit:
            with archive.writer() as writer:
                writer.events()
                first = capture(self.archive, self.source, SESSION, self.root,
                                start_line=2, end_line=2, archive_writer=writer)
                again = capture(self.archive, self.source, SESSION, self.root,
                                start_line=2, end_line=2, archive_writer=writer)
                self.assertEqual(first, again)
                self.assertEqual(audit.call_count, 1)
                self.assertEqual(len(writer.events()), 2)
        with self.assertRaisesRegex(ArchiveError, 'closed'):
            capture(self.archive, self.source, SESSION, self.root,
                    start_line=2, end_line=2, archive_writer=writer)
        other = Archive(self.root / 'other-archive').init()
        with other.writer() as wrong:
            with self.assertRaisesRegex(ArchiveError, 'exact archive'):
                capture(self.archive, self.source, SESSION, self.root,
                        start_line=2, end_line=2, archive_writer=wrong)

    def test_explicit_historical_import_is_bounded_and_not_technical(self):
        target = self.root / 'target'
        self.identify_lab(target)
        self.source.write_bytes(self.head + message('user', 'Historical planning'))
        with self.assertRaises(ValueError):
            capture(target / 'research/archive', self.source, SESSION, self.root,
                    target_lab=target, historical_import=True)
        with self.assertRaises(ValueError):
            capture(target / 'research/archive', self.source, SESSION, self.root,
                    target_lab=target, historical_import=True, technical_transfer=True,
                    end_line=2)
        result = capture(target / 'research/archive', self.source, SESSION, self.root,
                         target_lab=target, historical_import=True, end_line=2)
        self.assertTrue(result['historical_import'])
        self.assertFalse(result['technical_transfer'])
        self.assertEqual(result['captured_records'], 1)

    def run_capture(self, records, **kwargs):
        self.source.write_bytes(self.head + b"".join(records))
        return capture(self.archive, self.source, SESSION, self.root, **kwargs)

    def test_original_bytes_visible_phase_exclusions_and_idempotence(self):
        records = [message("user", "Original αβ\nwith spaces  "),
                   message("assistant", "Visible response", phase="commentary"),
                   line({"type": "reasoning", "summary": "SYNTHETIC_HIDDEN_SENTINEL"}),
                   message("developer", "SYNTHETIC_HIDDEN_SENTINEL"),
                   message("user", "SYNTHETIC_HIDDEN_SENTINEL", kinds=["environments.environment_context"])]
        result = self.run_capture(records, end_line=6, run_id="round-1")
        self.assertEqual(result["status"], "BOUNDED_COMPLETE")
        arc = Archive(self.archive)
        events = arc.events()
        self.assertEqual([arc.get(e["outputs"][0]) for e in events if e["kind"] == "capture.raw_record"], records[:2])
        self.assertNotIn(b"SYNTHETIC_HIDDEN_SENTINEL", b"".join(p.read_bytes() for p in (self.archive / "objects").iterdir()))
        again = capture(self.archive, self.source, SESSION, self.root, end_line=6, run_id="round-1")
        self.assertEqual(result, again)
        self.assertEqual(len(arc.events()), 3)
        self.assertTrue(arc.validate()["ok"])

    def test_reviewed_visible_user_metadata_is_preserved_as_original_bytes(self):
        metadata = {
            "client_authored": False,
            "fallback_token_limit_override": 12000,
            "mcp_attribution": {
                "status": "attribution_error",
                "error_reason": "source attribution unavailable",
                "sources": [{"plugin_id": "codex-app-tools@openai-bundled",
                             "server_name": "codex_app",
                             "tool_name": "read_thread_terminal",
                             "first_turn_id": "01a0e1ac-7da2-7ee2-8c36-d9ca212dcb9a"}],
            },
            "retained_source": {"id": {"message_id": "message-0123456789",
                                         "role": "user", "turn_id": "turn-0123456789"},
                                "complete": True, "revision": "revision-0123456789abcdef"},
            "guardian_sources": [{"id": {"message_id": "message-0123456789",
                                           "role": "assistant", "turn_id": "turn-0123456789"},
                                  "complete": False, "revision": "revision-0123456789abcdef"}],
            "guardian_source_order_guidance": True,
        }
        raw = line({"type": "message", "id": "m", "role": "user",
                    "content": [{"type": "input_text", "text": "Visible request"}],
                    "internal_chat_message_metadata_passthrough": {"content_item_kinds": ["user.text"]}},
                   metadata=metadata)
        result = self.run_capture([raw], end_line=2)
        self.assertEqual(result["status"], "BOUNDED_COMPLETE")
        self.assertEqual(result["captured_records"], 1)
        event = next(e for e in Archive(self.archive).events() if e["kind"] == "capture.raw_record")
        self.assertEqual(Archive(self.archive).get(event["outputs"][0]), raw)

    def test_first_party_attribution_without_plugin_preserves_visible_original(self):
        metadata = {"client_authored": False, "mcp_attribution": {
            "status": "complete", "sources": [{"server_name": "openaiDeveloperDocs",
                "tool_name": "search_openai_docs", "first_turn_id": "turn-0123456789"}]}}
        raw = line({"type": "message", "id": "m", "role": "user",
                    "content": [{"type": "input_text", "text": "Visible authorization"}],
                    "internal_chat_message_metadata_passthrough": {"content_item_kinds": ["user.text"]}},
                   metadata=metadata)
        result = self.run_capture([raw], end_line=2)
        self.assertEqual(result["status"], "BOUNDED_COMPLETE")
        event = next(e for e in Archive(self.archive).events() if e["kind"] == "capture.raw_record")
        self.assertEqual(Archive(self.archive).get(event["outputs"][0]), raw)

    def test_first_party_attribution_still_rejects_missing_unknown_and_unsafe_fields(self):
        from capture_codex import valid_top_metadata
        source = {"server_name": "openaiDeveloperDocs", "tool_name": "search_openai_docs",
                  "first_turn_id": "turn-0123456789"}
        invalid = [{k: v for k, v in source.items() if k != required} for required in source]
        invalid += [dict(source, future_field="SYNTHETIC_HIDDEN_SENTINEL"),
                    dict(source, plugin_id=None), dict(source, plugin_id="<secret>"),
                    dict(source, server_name="<secret>"), dict(source, first_turn_id=12)]
        for candidate in invalid:
            with self.subTest(source=candidate):
                self.assertFalse(valid_top_metadata({"client_authored": False,
                    "mcp_attribution": {"status": "complete", "sources": [candidate]}}))

    def test_hidden_items_are_excluded_before_optional_metadata_validation(self):
        from capture_codex import classify
        unknown = {"unreviewed_future_field": "SYNTHETIC_HIDDEN_SENTINEL"}
        hidden = [
            line({"type": "reasoning", "summary": "SYNTHETIC_HIDDEN_SENTINEL"}, metadata=unknown),
            line({"type": "message", "id": "m", "role": "developer",
                  "content": [{"type": "output_text", "text": "SYNTHETIC_HIDDEN_SENTINEL"}]}, metadata=unknown),
        ]
        for raw in hidden:
            record = json.loads(raw)
            reason = classify(record, 2, set(), set())
            self.assertTrue(reason.startswith("excluded:"))
            self.assertNotIn("unknown_record_metadata", reason)
        result = self.run_capture(hidden, end_line=3)
        self.assertEqual(result["captured_records"], 0)
        self.assertNotIn("unknown_record_metadata", result["excluded_counts"])

    def test_unknown_top_level_message_metadata_remains_incomplete(self):
        raw = line({"type": "message", "id": "m", "role": "user",
                    "content": [{"type": "input_text", "text": "Visible request"}],
                    "internal_chat_message_metadata_passthrough": {"content_item_kinds": ["user.text"]}},
                   metadata={"client_authored": False, "user_input_order": 1,
                             "unreviewed_future_field": "SYNTHETIC_HIDDEN_SENTINEL"})
        result = self.run_capture([raw], end_line=2)
        self.assertEqual(result["status"], "INCOMPLETE")
        self.assertIn("unknown_record_metadata", result["excluded_counts"])
        self.assertEqual(result["captured_records"], 0)
        archive = Archive(self.archive)
        self.assertNotIn(b"SYNTHETIC_HIDDEN_SENTINEL",
                         b"".join(path.read_bytes() for path in (self.archive / "objects").iterdir()))

    def test_unknown_schema_partial_tail_and_unreviewed_tools_are_incomplete(self):
        call = line({"type": "function_call", "call_id": "c", "name": "sum", "arguments": "[1,2]"})
        result = self.run_capture([call, line({"type": "new_future_visible_record"}), b'{"unfinished":'], end_line=3)
        self.assertEqual(result["status"], "INCOMPLETE")
        self.assertIn("partial_tail_withheld", result["gaps"])
        self.assertIn("unknown_schema_records_withheld", result["gaps"])
        self.assertIn("unreviewed_tool_bodies_withheld", result["gaps"])
        self.assertEqual(result["captured_records"], 0)

    def test_reuse_existing_markers_binds_earliest_exact_line_without_source_read(self):
        marker_text = "[HUNDRED:selection-run:select-24 sha256=" + "a" * 64 + "]"
        def visible(text, timestamp):
            value = {"timestamp": timestamp, "ordinal": 0, "type": "response_item",
                     "payload": {"type": "message", "id": "m", "role": "assistant",
                                 "phase": "commentary", "content": [{"type": "output_text", "text": text}],
                                 "internal_chat_message_metadata_passthrough": {"content_item_kinds": []}}}
            return (json.dumps(value, ensure_ascii=False) + "\n").encode()

        self.source.write_bytes(self.head + visible(marker_text, "2026-09-09T00:00:01Z")
                                + visible(marker_text, "2026-09-09T00:00:02Z"))
        archive = Archive(self.archive).init()
        start = {"kind": "operation.started", "actor": {"id": "root", "role": "AI"},
                 "session_id": SESSION, "run_id": "selection-run", "operation_id": "round-selection-run",
                 "attempt_id": "attempt-1", "bindings": {"method": [], "instruction": [], "config": [], "input": []},
                 "parents": [], "payload": {"protocol": "philosophy-round.v1"}}
        archive.append(start, "test-round-start")
        prepared = {"kind": "hundred.prepared", "actor": {"id": "root", "role": "AI"},
                    "session_id": SESSION, "run_id": "selection-run", "operation_id": "round-selection-run",
                    "attempt_id": "attempt-1", "bindings": start["bindings"], "parents": [],
                    "timestamp": "2026-09-08T00:00:00Z",
                    "payload": {"request": {"stage": "select-24"}}}
        prepared = archive.append(prepared, "test-prepared")
        captured = capture(self.archive, self.source, SESSION, self.root, start_line=2, end_line=3,
                           run_id="codex:" + SESSION)
        raw_events = [e for e in archive.events() if e["kind"] == "capture.raw_record"]
        identity = {"session_id": SESSION, "source_cwd": str(self.root),
                    "selection": "exact-project-cwd", "session_kind": "primary_chat"}
        identity_event = archive.append({
            "kind": "capture.session_identified", "actor": {"id": "local-collector", "role": "tool"},
            "session_id": SESSION, "run_id": "collector:" + SESSION, "operation_id": "collector:" + SESSION,
            "attempt_id": "collector-v1", "parents": [], "inputs": [], "outputs": [],
            "bindings": {"method": [], "instruction": [], "config": [], "input": []}, "payload": identity,
        }, "test-session-identity")
        message_events = []
        for raw_event in raw_events:
            line_number = raw_event["payload"]["source_line"]
            message_events.append(archive.append({
                "kind": "collector.message", "actor": {"id": "local-collector", "role": "tool"},
                "session_id": SESSION, "run_id": "collector:" + SESSION,
                "operation_id": "collector:" + SESSION, "attempt_id": "collector-v1",
                "parents": [raw_event["id"]], "inputs": [], "outputs": [],
                "bindings": {"method": [], "instruction": [], "config": [], "input": []},
                "payload": {"source_line": line_number, "raw_event_id": raw_event["id"],
                            "role": "assistant", "phase": "commentary", "attachment_gaps": []},
            }, "test-message:" + str(line_number)))
        source_bytes = self.source.read_bytes()
        from hashlib import sha256
        from research_archive import canonical
        cursor = {"lines": 3, "offset": len(source_bytes), "observed_size": len(source_bytes),
                  "prefix_sha256": sha256(source_bytes).hexdigest(), "identity_hash": sha256(canonical(identity)).hexdigest(),
                  "gaps": []}
        archive.append({
            "kind": "collector.coverage", "actor": {"id": "local-collector", "role": "tool"},
            "session_id": SESSION, "run_id": "collector:" + SESSION,
            "operation_id": "collector:" + SESSION, "attempt_id": "collector-v1",
            "parents": [identity_event["id"]] + [e["id"] for e in message_events],
            "inputs": [], "outputs": [], "bindings": {"method": [], "instruction": [], "config": [], "input": []},
            "payload": {"cursor": cursor, "source_basename": self.source.name,
                        "whole_trace": "INCOMPLETE", "boundary": "synthetic test"},
        }, "test-collector-coverage")

        self.source.unlink()
        with archive.writer() as writer:
            first = reuse_existing_marker(self.archive, self.root, SESSION, "selection-run", marker_text,
                                          prepared["id"], archive_writer=writer)
            again = reuse_existing_marker(self.archive, self.root, SESSION, "selection-run", marker_text,
                                          prepared["id"], archive_writer=writer)
            self.assertEqual(first, again)
            self.assertEqual(first["selected_source_line"], 2)
            self.assertEqual(first["matching_source_lines"], [2, 3])
            coverage = next(e for e in writer.events() if e["id"] == first["coverage_event_id"])
            self.assertEqual(coverage["payload"]["status"], "BOUNDED_COMPLETE")
            self.assertTrue(all(eid in coverage["parents"] for eid in first["raw_event_ids"] + first["run_binding_ids"]))
        self.assertTrue(archive.validate()["ok"])

    def test_reviewed_pair_original_bytes_and_parent_link(self):
        pair = [line({"type": "custom_tool_call", "call_id": "c", "name": "exec", "input": "text(2+2)"}),
                line({"type": "custom_tool_call_output", "call_id": "c", "output": [{"type": "text", "text": "4"}]})]
        result = self.run_capture(pair, start_line=2, end_line=3, reviewed_tool_lines=[2, 3])
        self.assertEqual(result["status"], "BOUNDED_COMPLETE")
        arc = Archive(self.archive)
        events = arc.events()
        self.assertEqual(events[1]["parents"], [])
        self.assertEqual(events[2]["kind"], "capture.tool_link")
        self.assertEqual(events[2]["parents"], [events[0]["id"], events[1]["id"]])
        self.assertEqual([arc.get(e["outputs"][0]) for e in events[:2]], pair)

    def test_orphan_result_is_repairable_by_later_pair_without_rewriting(self):
        pair = [line({"type": "function_call", "call_id": "c", "name": "sum", "arguments": "[1,2]"}),
                line({"type": "function_call_output", "call_id": "c", "output": "3"})]
        first = self.run_capture(pair, start_line=3, end_line=3, reviewed_tool_lines=[3])
        self.assertEqual(first["status"], "INCOMPLETE")
        original = Archive(self.archive).events()[0]
        repaired = capture(self.archive, self.source, SESSION, self.root,
                           start_line=2, end_line=3, reviewed_tool_lines=[2, 3])
        self.assertEqual(repaired["status"], "BOUNDED_COMPLETE")
        archive = Archive(self.archive)
        self.assertEqual(archive.events()[0], original)
        self.assertEqual(len(repaired["tool_link_ids"]), 1)
        again = capture(self.archive, self.source, SESSION, self.root,
                        start_line=2, end_line=3, reviewed_tool_lines=[2, 3])
        self.assertEqual(repaired, again)
        self.assertTrue(archive.validate()["ok"])

    def test_native_timestamp_and_only_normalized_model_observations(self):
        context = line({"model": "synthetic-model-v1", "effort": "ultra",
                        "base_instructions": "SYNTHETIC_HIDDEN_SENTINEL",
                        "other_metadata": {"secret": "SYNTHETIC_HIDDEN_SENTINEL"}}, "turn_context")
        result = self.run_capture([context, message("assistant", "safe", phase="final_answer")], end_line=3)
        self.assertEqual(result["status"], "BOUNDED_COMPLETE")
        archive = Archive(self.archive)
        event = next(e for e in archive.events() if e["kind"] == "capture.raw_record")
        self.assertEqual(event["timestamp"], "2026-09-07T00:00:00Z")
        self.assertEqual(event["timestamp_source"], "supplied-event-time")
        self.assertEqual(event["model"]["value"], {"model": "synthetic-model-v1", "reasoning_effort": "ultra"})
        self.assertEqual(event["model"]["source_line"], 2)
        self.assertIn("thinking_duration_unavailable", result["limitations"])
        self.assertNotIn(b"SYNTHETIC_HIDDEN_SENTINEL", b"".join(p.read_bytes() for p in (self.archive / "objects").iterdir()))
        self.assertNotIn("other_metadata", json.dumps(archive.events()))

    def test_unknown_model_and_unsupported_effort_remain_explicit(self):
        self.run_capture([line({"model": "synthetic-model-v1", "effort": ["unsupported"]}, "turn_context"),
                          message("assistant", "safe", phase="final_answer"),
                          line({"effort": "high"}, "turn_context"),
                          message("assistant", "also safe", phase="final_answer")], end_line=5)
        events = [e for e in Archive(self.archive).events() if e["kind"] == "capture.raw_record"]
        self.assertIsNone(events[0]["model"]["value"]["reasoning_effort"])
        self.assertEqual(events[1]["model"]["status"], "unknown")

    def test_duplicate_keys_and_nonfinite_json_fail_before_archive_write(self):
        safe = message("assistant", "safe", phase="final_answer")
        duplicate = safe.replace(b'"payload": ', b'"payload": {"type":"reasoning","text":"SYNTHETIC_HIDDEN_SENTINEL"}, "payload": ', 1)
        for raw in (duplicate, safe.replace(b'"ordinal": 0', b'"ordinal": NaN')):
            with self.subTest(raw=raw), self.assertRaisesRegex(ValueError, "malformed complete"):
                self.run_capture([raw], end_line=2)
            self.assertFalse(self.archive.exists())

    def test_invalid_native_timestamp_withheld_as_unknown_schema(self):
        record = message("assistant", "safe", phase="final_answer").replace(b"2026-09-07T00:00:00Z", b"time-unknown")
        result = self.run_capture([record], end_line=2)
        self.assertEqual(result["status"], "INCOMPLETE")
        self.assertEqual(result["captured_records"], 0)

    def test_result_preceding_its_call_cannot_claim_complete_pairing(self):
        records = [line({"type": "function_call_output", "call_id": "c", "output": "3"}),
                   line({"type": "function_call", "call_id": "c", "name": "sum", "arguments": "[1,2]"})]
        result = self.run_capture(records, start_line=2, end_line=3, reviewed_tool_lines=[2, 3])
        self.assertEqual(result["status"], "INCOMPLETE")
        self.assertIn("selected_tool_results_without_preceding_selected_calls", result["gaps"])
        self.assertEqual(result["tool_link_ids"], [])

    def test_source_traversal_symlink_ancestor_and_special_file_rejected(self):
        self.source.write_bytes(self.head + message("user", "safe"))
        nested = self.root / "nested"
        nested.mkdir()
        alias = self.root / "directory-alias"
        alias.symlink_to(self.root, target_is_directory=True)
        fifo = self.root / "source-fifo"
        os.mkfifo(fifo)
        for source in (nested / ".." / self.source.name, alias / self.source.name, fifo):
            with self.subTest(source=source), self.assertRaises(ValueError):
                capture(self.archive, source, SESSION, self.root, end_line=2)
            self.assertFalse(self.archive.exists())

    def test_sensitive_call_result_is_blocked_even_when_only_result_selected(self):
        pair = [line({"type": "function_call", "call_id": "c", "name": "exec", "arguments": "cat ~/.codex/sessions/secret"}),
                line({"type": "function_call_output", "call_id": "c", "output": "SYNTHETIC_HIDDEN_SENTINEL"})]
        result = self.run_capture(pair, start_line=3, end_line=3, reviewed_tool_lines=[3])
        self.assertEqual(result["captured_records"], 0)
        self.assertEqual(result["excluded_counts"]["excluded:blocked_tool_call"], 1)
        self.assertNotIn(b"SYNTHETIC_HIDDEN_SENTINEL", b"".join(p.read_bytes() for p in (self.archive / "objects").iterdir()))

    def test_identity_cwd_and_symlink_fail_before_archive_write(self):
        self.source.write_bytes(self.head + message("user", "safe"))
        with self.assertRaisesRegex(ValueError, "identity"):
            capture(self.archive, self.source, "wrong", self.root)
        with self.assertRaisesRegex(ValueError, "exact target"):
            capture(self.archive, self.source, SESSION, self.root / "other")
        alias = self.root / "alias.jsonl"
        alias.symlink_to(self.source)
        with self.assertRaisesRegex(ValueError, "symlink"):
            capture(self.archive, alias, SESSION, self.root)
        self.assertFalse(self.archive.exists())

    def test_rewritten_line_cannot_reuse_delivery_identity(self):
        self.run_capture([message("user", "before")], end_line=2)
        self.source.write_bytes(self.head + message("user", "after"))
        with self.assertRaisesRegex(ArchiveError, "delivery key conflict"):
            capture(self.archive, self.source, SESSION, self.root, end_line=2)
        self.assertEqual(len(Archive(self.archive).events()), 2)

    def test_exact_sql_session_lookup_without_enumeration(self):
        db = self.root / "metadata.sqlite"
        connection = sqlite3.connect(db)
        connection.execute("CREATE TABLE threads (id TEXT, rollout_path TEXT, cwd TEXT)")
        connection.execute("INSERT INTO threads VALUES (?, ?, ?)", (SESSION, str(self.source), str(self.root)))
        connection.execute("INSERT INTO threads VALUES (?, ?, ?)", ("unrelated-id", "/private/never/read", "/unrelated"))
        connection.commit()
        connection.close()
        self.assertEqual(resolve_session(SESSION, self.root, db), self.source)
        with self.assertRaisesRegex(ValueError, "identity not found"):
            resolve_session("absent-session", self.root, db)

    def test_cross_project_technical_transfer_requires_explicit_exact_lab(self):
        target = self.root / "target-lab"
        self.identify_lab(target)
        archive = target / "research/archive"
        self.source.write_bytes(self.head + message("assistant", "Technical observation", phase="final_answer"))
        with self.assertRaisesRegex(ValueError, "explicit technical transfer"):
            capture(archive, self.source, SESSION, self.root, target_lab=target, end_line=2)
        result = capture(archive, self.source, SESSION, self.root, target_lab=target,
                         technical_transfer=True, start_line=2, end_line=2)
        self.assertTrue(result["technical_transfer"])
        self.assertEqual(result["status"], "BOUNDED_COMPLETE")
        with self.assertRaisesRegex(ValueError, "exact target"):
            capture(target / "wrong", self.source, SESSION, self.root, target_lab=target,
                    technical_transfer=True, end_line=2)
        (target / ".lab/philosophy.json").unlink()
        (target / ".lab/philosophy.json").symlink_to(self.root / ".lab/philosophy.json")
        with self.assertRaisesRegex(ValueError, "symlink"):
            capture(archive, self.source, SESSION, self.root, target_lab=target,
                    technical_transfer=True, end_line=2)

    def test_unknown_encrypted_field_never_enters_original_blob(self):
        result = self.run_capture([line({"type": "custom_tool_call_output", "call_id": "c",
                                       "output": "safe", "encrypted_content": "SYNTHETIC_HIDDEN_SENTINEL"})],
                                  end_line=2, reviewed_tool_lines=[2])
        self.assertEqual(result["captured_records"], 0)
        self.assertEqual(result["status"], "INCOMPLETE")

    def test_reviewed_automation_delivery_retains_origin_without_inventing_call_pair(self):
        raw = line({'type':'function_call_output','id':'fco_synthetic','name':'automation_update',
                    'namespace':'codex_app','output':'<heartbeat><automation_id>synthetic</automation_id>'
                    '<current_time_iso>2026-09-08T00:00:00Z</current_time_iso>'
                    '<instructions>Check the synthetic collector.</instructions></heartbeat>'})
        pending = self.run_capture([raw], end_line=2)
        self.assertEqual(pending['captured_records'], 0)
        self.assertEqual(pending['status'], 'INCOMPLETE')
        result = capture(self.archive,self.source,SESSION,self.root,end_line=2,reviewed_tool_lines=[2])
        self.assertEqual(result['status'], 'BOUNDED_COMPLETE')
        self.assertEqual(result['tool_link_ids'], [])
        event = next(e for e in Archive(self.archive).events() if e['kind']=='capture.raw_record')
        self.assertEqual(event['actor']['role'], 'tool')
        self.assertEqual(event['payload']['origin'], 'AUTOMATION')
        self.assertIsNone(event['payload']['call_id'])
        self.assertEqual(Archive(self.archive).get(event['outputs'][0]), raw)


if __name__ == "__main__":
    unittest.main()
