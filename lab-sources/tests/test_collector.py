"""Synthetic local collector integration fixtures; no native user data is read."""
import contextlib
import hashlib
import json
import multiprocessing
import os
from pathlib import Path
import shutil
import sqlite3
import sys
import tempfile
import types
import unittest
from unittest import mock

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import collector as module
from collector import Collector
from research_archive import Archive, ArchiveError
import research_archive

SESSION = "synthetic-session-0001"
TURN = "synthetic-turn-0001"


def line(payload, record_type="response_item", timestamp="2026-09-08T00:00:00Z"):
    return (json.dumps({"timestamp": timestamp, "type": record_type, "payload": payload},
                       ensure_ascii=False) + "\n").encode()


def message(role, text, phase=None, turn=TURN):
    payload = {"type": "message", "id": "synthetic-message", "role": role,
               "content": [{"type": "input_text" if role == "user" else "output_text", "text": text}],
               "internal_chat_message_metadata_passthrough": {"turn_id": turn}}
    if role == "user":
        payload["internal_chat_message_metadata_passthrough"]["content_item_kinds"] = ["user.text"]
    if phase:
        payload["phase"] = phase
    return line(payload)


def lifecycle(kind, **extra):
    return line({"type": kind, "turn_id": TURN, **extra}, "event_msg")


def lock_contender(root, output):
    try:
        report = Collector(root).collect()
        output.put(report["status"])
    except BlockingIOError:
        output.put("LOCKED")
    except Exception as exc:
        output.put(type(exc).__name__)


class CollectorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="synthetic-collector-")
        self.base = Path(self.temp.name).resolve()
        self.root = self.base / "Synthetic Philosophy Lab"
        self.root.mkdir()
        self.identify(self.root)
        (self.root / "scripts").mkdir()
        shutil.copyfile(SCRIPTS / "collector_source.py", self.root / "scripts/collector_source.py")
        (self.root / "collector").mkdir()
        self.db = self.base / "synthetic-state.sqlite"
        with contextlib.closing(sqlite3.connect(self.db)) as db:
            db.executescript("""
                CREATE TABLE threads (id TEXT PRIMARY KEY, rollout_path TEXT, cwd TEXT,
                    title TEXT, agent_nickname TEXT, agent_role TEXT, agent_path TEXT, source TEXT);
                CREATE TABLE thread_spawn_edges (parent_thread_id TEXT, child_thread_id TEXT);
            """)
            db.commit()
        self.config = {"schema_version": 1, "project_root": ".", "state_db": str(self.db),
                       "explicit_sessions": {}, "interval_seconds": 10}
        self.write_config()
        self.source = self.add_session(SESSION, self.root)
        self.archive = Archive(self.root / "research/archive").init()
        # Views have separate tests. This suite isolates durable orchestration.
        self.views = types.ModuleType("collector_views")
        self.views.refresh = mock.Mock()
        self.view_patch = mock.patch.dict(sys.modules, {"collector_views": self.views})
        self.view_patch.start()

    def tearDown(self):
        self.view_patch.stop()
        self.temp.cleanup()

    @staticmethod
    def identify(root):
        (root / ".lab").mkdir()
        (root / "LAB_PROFILE.json").write_text(json.dumps({"lab": {"kind": "PHILOSOPHY_PROGRAM"}}))
        (root / ".lab/philosophy.json").write_text(json.dumps({
            "schema_version": 1, "kernel": "philosophy.v1", "archive_format": "research-archive.v1"}))

    def write_config(self):
        (self.root / "collector/config.json").write_text(json.dumps(self.config))

    def add_session(self, sid, cwd, parent=None, nickname=None):
        path = self.base / (sid + ".jsonl")
        path.write_bytes(line({"id": sid, "cwd": str(cwd),
                               "base_instructions": "SYNTHETIC_HIDDEN_ENVELOPE"}, "session_meta"))
        with contextlib.closing(sqlite3.connect(self.db)) as db:
            db.execute("INSERT INTO threads VALUES (?,?,?,?,?,?,?,?)",
                       (sid, str(path), str(cwd), "Synthetic " + sid, nickname,
                        "critic" if nickname else None, "/root/critic" if nickname else "/root",
                        "subagent" if nickname else "cli"))
            if parent:
                db.execute("INSERT INTO thread_spawn_edges VALUES (?,?)", (parent, sid))
            db.commit()
        return path

    def add_bytes(self, data, path=None):
        with (path or self.source).open("ab") as stream:
            stream.write(data)

    def events(self, kind=None):
        return [e for e in self.archive.events() if kind is None or e["kind"] == kind]

    def cursor(self):
        return self.events("collector.coverage")[-1]["payload"]["cursor"]

    def assert_ok(self, report):
        self.assertEqual(report["status"], "RUNNING", report)
        self.assertEqual(report["sessions"][0]["status"], "CAUGHT_UP", report)

    def test_prompt_final_model_and_lifecycle_keep_originals_and_safe_metadata(self):
        prompt = message("user", "Synthetic prompt.\nExact second line.")
        final = message("assistant", "Synthetic answer.", "final")
        self.add_bytes(lifecycle("task_started") + prompt + line({
            "turn_id": TURN, "model": "synthetic-model", "effort": "ultra",
            "developer_instructions": "SYNTHETIC_HIDDEN_TURN_ENVELOPE"}, "turn_context") +
            final + lifecycle("task_complete", duration_ms=2500))
        report = Collector(self.root).collect()
        self.assert_ok(report)
        originals = [self.archive.get(e["outputs"][0]) for e in self.events("capture.raw_record")]
        self.assertEqual(originals, [prompt, final])
        messages = self.events("collector.message")
        self.assertEqual([e["payload"]["role"] for e in messages], ["user", "assistant"])
        observed = messages[-1]["payload"]["observed_model"]
        self.assertEqual(observed["value"], {"model": "synthetic-model", "reasoning_effort": "ultra"})
        self.assertEqual(messages[-1]["payload"]["turn_id"], TURN)
        self.assertEqual([e["payload"]["event_type"] for e in self.events("collector.lifecycle")],
                         ["task_started", "task_complete"])
        self.assertEqual(self.events("collector.lifecycle")[-1]["payload"]["duration_ms"], 2500)
        self.assertEqual(self.cursor()["counts"], {"assistant_final": 1, "user_prompts": 1})
        all_bytes = b"".join(p.read_bytes() for folder in ("objects", "events")
                             for p in (self.archive.root / folder).iterdir())
        self.assertNotIn(b"SYNTHETIC_HIDDEN", all_bytes)
        self.assertTrue(self.archive.validate()["ok"])

    def test_noop_does_not_append_events_or_refresh_views(self):
        self.add_bytes(message("user", "Synthetic prompt"))
        collector = Collector(self.root)
        self.assert_ok(collector.collect())
        original = self.events()
        self.views.refresh.reset_mock()
        with mock.patch.object(research_archive._ArchiveWriter, "append_many", side_effect=AssertionError("no-op append")):
            report = collector.collect()
        self.assert_ok(report)
        self.assertEqual(report["changed_sessions"], [])
        self.assertEqual(self.events(), original)
        self.views.refresh.assert_not_called()

    def test_restart_uses_canonical_cursor_and_ignores_damaged_runtime_cache(self):
        self.add_bytes(message("user", "Synthetic prompt") + message("assistant", "Synthetic final", "final"))
        self.assert_ok(Collector(self.root).collect())
        original = self.events()
        (self.root / "collector/runtime/cursor-cache.json").write_text("synthetic damaged disposable cache")
        restored = Collector(self.root)
        self.assert_ok(restored.collect())
        self.assertEqual(self.events(), original)
        self.assertEqual(restored.state[SESSION], self.cursor())

    def test_competing_commit_before_writer_acquisition_refreshes_exact_cursor(self):
        self.add_bytes(message('user', 'Synthetic concurrent prompt'))
        collector = Collector(self.root)
        original_writer = collector.archive.writer

        @contextlib.contextmanager
        def after_competing_commit():
            from capture_codex import capture
            result = capture(self.archive.root, self.source, SESSION, self.root,
                             start_line=2, end_line=2, run_id='synthetic-manual-capture')
            self.assertEqual(result['status'], 'BOUNDED_COMPLETE')
            self.add_bytes(message('assistant', 'Synthetic later final', 'final'))
            with original_writer() as writer:
                yield writer

        with mock.patch.object(collector.archive, 'writer', after_competing_commit):
            self.assert_ok(collector.collect())
        self.assertEqual(self.cursor()['counts'], {'user_prompts': 1, 'assistant_final': 1})
        self.assertEqual(len(self.events('capture.raw_record')), 2)
        self.assertTrue(self.archive.validate()['ok'])

    def test_commit_after_initial_snapshot_cannot_hide_behind_new_mtime(self):
        self.add_bytes(message('user', 'Synthetic initialization race'))
        original_lock = Archive._lock
        injected = False

        @contextlib.contextmanager
        def commit_after_unlock(archive, initializing=False):
            nonlocal injected
            with original_lock(archive, initializing=initializing):
                yield
            if not initializing and not injected:
                injected = True
                from capture_codex import capture
                result = capture(self.archive.root, self.source, SESSION, self.root,
                                 start_line=2, end_line=2, run_id='synthetic-init-race')
                self.assertEqual(result['status'], 'BOUNDED_COMPLETE')

        with mock.patch.object(Archive, '_lock', commit_after_unlock):
            collector = Collector(self.root)
        self.assertTrue(injected)
        self.add_bytes(message('assistant', 'Synthetic final after initialization', 'final'))
        self.assert_ok(collector.collect())
        self.assertEqual(self.cursor()['counts'], {'user_prompts': 1, 'assistant_final': 1})
        self.assertEqual(len(self.events('capture.raw_record')), 2)

    def test_partial_live_tail_then_completed_record_is_captured_once(self):
        self.add_bytes(message("user", "Synthetic prompt"))
        final = message("assistant", "Synthetic late final", "final")
        cut = len(final) // 2
        self.add_bytes(final[:cut])
        collector = Collector(self.root)
        self.assert_ok(collector.collect())
        cursor = self.cursor()
        self.assertEqual(cursor["counts"], {"user_prompts": 1})
        self.assertTrue(any(g["reason"] == "partial_live_tail" for g in cursor["gaps"]))
        self.assertEqual(cursor["offset"], self.source.stat().st_size - cut)
        self.add_bytes(final[cut:])
        self.assert_ok(Collector(self.root).collect())
        self.assertEqual(self.cursor()["counts"], {"user_prompts": 1, "assistant_final": 1})
        self.assertFalse(any(g["reason"] == "partial_live_tail" for g in self.cursor()["gaps"]))
        self.assertEqual(len(self.events("capture.raw_record")), 2)

    def test_truncation_keeps_last_committed_cursor_and_events(self):
        self.add_bytes(message("user", "Synthetic prompt"))
        collector = Collector(self.root)
        self.assert_ok(collector.collect())
        old_events, old_cursor = self.events(), self.cursor()
        self.source.write_bytes(self.source.read_bytes().splitlines(keepends=True)[0])
        report = collector.collect()
        self.assertEqual(report["status"], "ERROR")
        self.assertIn("truncated", report["sessions"][0]["error"])
        self.assertEqual(report["sessions"][0]["last_committed_cursor"], old_cursor)
        self.assertEqual(collector.state[SESSION], old_cursor)
        self.assertEqual(self.events(), old_events)

    def test_same_size_prefix_rewrite_keeps_last_committed_cursor(self):
        self.add_bytes(message("user", "Synthetic prompt AAA"))
        collector = Collector(self.root)
        self.assert_ok(collector.collect())
        old_events, old_cursor = self.events(), self.cursor()
        old_stat = self.source.stat()
        self.source.write_bytes(self.source.read_bytes().replace(b"AAA", b"BBB"))
        os.utime(self.source, ns=(old_stat.st_atime_ns, old_stat.st_mtime_ns + 1000000))
        report = collector.collect()
        self.assertEqual(report["status"], "ERROR")
        self.assertIn("prefix changed", report["sessions"][0]["error"])
        self.assertEqual(collector.state[SESSION], old_cursor)
        self.assertEqual(self.events(), old_events)

    def test_failed_archive_write_never_advances_cursor_and_restart_retries(self):
        self.add_bytes(message("user", "Synthetic prompt"))
        collector = Collector(self.root)
        with mock.patch.object(research_archive._ArchiveWriter, "append_many", side_effect=OSError("synthetic disk failure")):
            report = collector.collect()
        self.assertEqual(report["status"], "ERROR")
        self.assertNotIn(SESSION, collector.state)
        self.assertEqual(self.events(), [])
        self.assertFalse((self.root / "collector/runtime/cursor-cache.json").exists())
        restored = Collector(self.root)
        self.assert_ok(restored.collect())
        self.assertEqual(restored.state[SESSION]["counts"], {"user_prompts": 1})
        self.assertEqual(len(self.events("capture.raw_record")), 1)

    def test_failed_later_scan_preserves_prior_cursor_and_retries_only_new_records(self):
        self.add_bytes(message("user", "Synthetic prompt"))
        collector = Collector(self.root)
        self.assert_ok(collector.collect())
        old_events, old_cursor = self.events(), self.cursor()
        self.add_bytes(message("assistant", "Synthetic later final", "final"))
        with mock.patch.object(research_archive._ArchiveWriter, "append_many", side_effect=OSError("synthetic full disk")):
            report = collector.collect()
        self.assertEqual(report["status"], "ERROR")
        self.assertEqual(collector.state[SESSION], old_cursor)
        self.assertEqual(self.events(), old_events)
        self.assert_ok(Collector(self.root).collect())
        self.assertEqual(self.events()[:len(old_events)], old_events)
        self.assertEqual(len(self.events("capture.raw_record")), 2)
        self.assertEqual(self.cursor()["counts"], {"user_prompts": 1, "assistant_final": 1})

    def test_source_rewritten_during_projection_is_rejected_before_cursor_commit(self):
        self.add_bytes(message("user", "Synthetic mutable AAA"))
        collector = Collector(self.root)
        projection = module.project_record
        original_stat = self.source.stat()

        def rewrite(record, source_line, *args, **kwargs):
            if source_line == 2:
                self.source.write_bytes(self.source.read_bytes().replace(b"AAA", b"BBB"))
                os.utime(self.source, ns=(original_stat.st_atime_ns, original_stat.st_mtime_ns + 1000000))
            return projection(record, source_line, *args, **kwargs)

        with mock.patch.object(module, "project_record", side_effect=rewrite):
            report = collector.collect()
        self.assertEqual(report["status"], "ERROR")
        self.assertNotIn(SESSION, collector.state)
        self.assertEqual(self.events(), [])

    def test_source_appended_during_scan_is_captured_next_time(self):
        self.add_bytes(message("user", "Synthetic initial prompt"))
        collector = Collector(self.root)
        projection = module.project_record
        final = message("assistant", "Synthetic concurrently arriving final", "final")

        def append_later(record, source_line, *args, **kwargs):
            if source_line == 2:
                self.add_bytes(final)
            return projection(record, source_line, *args, **kwargs)

        with mock.patch.object(module, "project_record", side_effect=append_later):
            self.assert_ok(collector.collect())
        self.assertEqual(self.cursor()["counts"], {"user_prompts": 1})
        self.assert_ok(collector.collect())
        self.assertEqual(self.cursor()["counts"], {"user_prompts": 1, "assistant_final": 1})

    def test_partial_archive_publication_rebuilds_without_duplicates(self):
        self.add_bytes(message("user", "Synthetic prompt") + message("assistant", "Synthetic final", "final"))
        publish, calls = research_archive._publish, 0

        def fail_after_third_event(path, data):
            nonlocal calls
            publish(path, data)
            if path.parent.name == "events":
                calls += 1
                if calls == 3:
                    raise OSError("synthetic uncertain publication")

        with mock.patch.object(research_archive, "_publish", side_effect=fail_after_third_event):
            report = Collector(self.root).collect()
        self.assertEqual(report["status"], "ERROR")
        prefix = self.events()
        self.assertEqual(len(prefix), 3)
        self.assert_ok(Collector(self.root).collect())
        events = self.events()
        self.assertEqual(events[:3], prefix)
        self.assertEqual(len({e["delivery_key"] for e in events}), len(events))
        self.assertEqual(len(self.events("capture.raw_record")), 2)
        self.assertEqual(self.cursor()["counts"], {"user_prompts": 1, "assistant_final": 1})

    def test_two_processes_respect_single_collector_lock(self):
        self.add_bytes(message("user", "Synthetic prompt"))
        collector = Collector(self.root)
        context = multiprocessing.get_context("fork")
        output = context.Queue()
        with collector.lock():
            child = context.Process(target=lock_contender, args=(self.root, output))
            child.start()
            child.join(10)
            self.assertFalse(child.is_alive())
            self.assertEqual(child.exitcode, 0)
            self.assertEqual(output.get(timeout=2), "LOCKED")
        self.assertEqual(self.events(), [])
        self.assert_ok(Collector(self.root).collect())
        self.assert_ok(collector.collect())
        self.assertEqual(len(self.events("capture.raw_record")), 1)

    def test_native_wrong_id_or_cwd_rejected_before_any_capture(self):
        for header in ({"id": "synthetic-wrong-session", "cwd": str(self.root)},
                       {"id": SESSION, "cwd": str(self.base / "Other Project")}):
            with self.subTest(header=header):
                self.source.write_bytes(line(header, "session_meta") + message("user", "Synthetic prompt"))
                report = Collector(self.root).collect()
                self.assertEqual(report["status"], "ERROR")
                self.assertEqual(self.events(), [])

    def test_unrelated_cwd_is_not_collected_but_selected_child_is(self):
        unrelated = self.add_session("synthetic-unrelated-0001", self.base / "Unrelated Project")
        unrelated.write_bytes(b"SYNTHETIC_UNRELATED_SOURCE_MUST_NOT_BE_PARSED")
        child = self.add_session("synthetic-child-0001", self.base / "Child Working Directory",
                                 parent=SESSION, nickname="Socrates")
        self.add_bytes(message("assistant", "Synthetic child final", "final"), child)
        report = Collector(self.root).collect()
        self.assert_ok(report)
        self.assertEqual(report["discovered_sessions"], 2)
        identity = {e["session_id"]: e["payload"] for e in self.events("capture.session_identified")}
        self.assertEqual(set(identity), {SESSION, "synthetic-child-0001"})
        self.assertEqual(identity["synthetic-child-0001"]["parent_session_id"], SESSION)
        self.assertEqual(identity["synthetic-child-0001"]["agent_name"], "Socrates")
        self.assertEqual(identity["synthetic-child-0001"]["role"], "critic")

    def test_mixed_attachment_projects_human_text_and_marks_missing_original(self):
        payload = {"type": "message", "id": "mixed", "role": "user",
                   "content": [{"type": "input_text", "text": "Synthetic attachment prompt"},
                               {"type": "input_image", "image_url": "SYNTHETIC_ATTACHMENT_SECRET"}],
                   "internal_chat_message_metadata_passthrough": {
                       "content_item_kinds": ["user.text", "user.image"], "turn_id": TURN}}
        self.add_bytes(line(payload))
        report = Collector(self.root).collect()
        self.assert_ok(report)
        self.assertEqual(self.cursor()["counts"], {"user_prompts": 1})
        self.assertEqual(self.events("capture.raw_record"), [])
        projected = self.events("collector.message")[0]["payload"]
        self.assertEqual(projected["text"], "Synthetic attachment prompt")
        self.assertFalse(projected["retain_original"])
        self.assertIsNone(projected["raw_event_id"])
        self.assertIn("original_mixed_record_not_retained", projected["attachment_gaps"])
        self.assertEqual(self.cursor()["coverage"], "GAPS")
        self.assertNotIn("SYNTHETIC_ATTACHMENT_SECRET", json.dumps(self.events()))

    def test_completion_arriving_after_final_is_collected_on_later_scan(self):
        self.add_bytes(lifecycle("task_started") + message("user", "Synthetic prompt") +
                       message("assistant", "Synthetic final before completion metadata", "final"))
        collector = Collector(self.root)
        self.assert_ok(collector.collect())
        self.assertEqual(len(self.events("collector.lifecycle")), 1)
        prior_final = self.events("collector.message")[-1]
        self.add_bytes(lifecycle("task_complete", duration_ms=8123,
                                 started_at="2026-09-08T00:00:00Z",
                                 completed_at="2026-09-08T00:00:08.123Z"))
        self.assert_ok(collector.collect())
        completion = self.events("collector.lifecycle")[-1]
        self.assertEqual(completion["payload"]["turn_id"], prior_final["payload"]["turn_id"])
        self.assertEqual(completion["payload"]["duration_ms"], 8123)
        self.assertEqual(len(self.events("capture.raw_record")), 2)
        self.assertEqual(self.events("collector.message")[-1], prior_final)
        self.assertIsNone(self.cursor()["turn_id"])

    def test_review_exact_original_hash_captures_tools_without_dropping_pending_history(self):
        tool = line({"type": "function_call", "name": "synthetic_tool", "call_id": "synthetic-call",
                     "arguments": "SYNTHETIC_VISIBLE_TOOL_BODY"})
        self.add_bytes(message("user", "Synthetic prompt") + tool)
        collector = Collector(self.root)
        self.assert_ok(collector.collect())
        pending = self.events("collector.tool_pending")
        self.assertEqual(len(pending), 1)
        self.assertEqual(self.cursor()["pending_tools"], 1)
        self.assertNotIn("SYNTHETIC_VISIBLE_TOOL_BODY", json.dumps(self.events()))
        review = self.root / "collector/reviews" / (SESSION + ".json")
        review.parent.mkdir()
        review.write_text(json.dumps({"3": hashlib.sha256(tool).hexdigest()}))
        self.assert_ok(collector.collect())
        self.assertEqual(self.cursor()["pending_tools"], 0)
        self.assertEqual(self.events("collector.tool_pending"), pending)
        self.assertEqual(len(self.events("collector.tool_reviewed")), 1)
        raw_tools = [e for e in self.events("capture.raw_record") if e["payload"]["source_type"] == "function_call"]
        self.assertEqual(self.archive.get(raw_tools[0]["outputs"][0]), tool)

    def test_invalid_target_lab_identity_is_rejected(self):
        (self.root / "LAB_PROFILE.json").write_text(json.dumps({"lab": {"kind": "OTHER_PROJECT"}}))
        with self.assertRaises((ValueError, ArchiveError)):
            Collector(self.root)
        self.assertEqual(self.events(), [])

    def test_automation_gap_recovery_is_append_only_reviewed_and_not_a_human_prompt(self):
        heartbeat=line({'type':'function_call_output','id':'fco_synthetic','name':'automation_update',
                        'namespace':'codex_app','output':'<heartbeat><automation_id>synthetic</automation_id>'
                        '<current_time_iso>2026-09-08T00:00:00Z</current_time_iso>'
                        '<instructions>Check synthetic service.</instructions></heartbeat>'})
        self.add_bytes(heartbeat+message('user','Human prompt'))
        old=Collector(self.root);old.signature='synthetic-pre-heartbeat-adapter'
        project=module.project_record
        def previous_adapter(record,number,*args):
            if number==2:
                return {'kind':'gap','payload':{'reason':'unknown_payload_fields'}}
            return project(record,number,*args)
        with mock.patch.object(module,'project_record',side_effect=previous_adapter):
            first=old.collect()
        before=self.events()
        self.assertFalse(first['coverage_healthy'])
        self.assertTrue(first['attention'])
        current=Collector(self.root)
        pending=current.collect()
        self.assertTrue(pending['coverage_healthy'])
        self.assertEqual(self.cursor()['pending_tools'],1)
        self.assertEqual(self.cursor()['counts'],{'user_prompts':1,'automation_triggers':1})
        review=self.root/'collector/reviews'/(SESSION+'.json');review.parent.mkdir()
        review.write_text(json.dumps({'2':hashlib.sha256(heartbeat).hexdigest()}))
        recovered=current.collect()
        self.assertTrue(recovered['coverage_healthy'])
        self.assertEqual(self.cursor()['pending_tools'],0)
        self.assertEqual(self.events()[:len(before)],before)
        originals=self.events('capture.raw_record')
        self.assertEqual(len(originals),2)
        trigger=next(e for e in originals if e['payload']['source_line']==2)
        self.assertEqual(trigger['payload']['origin'],'AUTOMATION')
        self.assertIsNone(trigger['payload']['call_id'])
        self.assertEqual(self.archive.get(trigger['outputs'][0]),heartbeat)
        count=len(self.events())
        current.collect(reconcile=True)
        self.assertEqual(len(self.events()),count)
        self.assertEqual(self.cursor()['counts'],{'user_prompts':1,'automation_triggers':1})

    def test_unsupported_tool_schema_is_visible_without_claiming_missing_human_text(self):
        self.add_bytes(line({'type':'function_call_output','id':'unknown','name':'unknown',
                             'output':'SYNTHETIC_WITHHELD_TOOL_BODY'}))
        report=Collector(self.root).collect()
        session=report['sessions'][0]
        self.assertEqual(session['coverage'],'GAPS')
        self.assertEqual(session['text_coverage'],'TEXT_COMPLETE_THROUGH_CURSOR')
        self.assertEqual(session['tools_coverage'],'UNSUPPORTED_SCHEMA')
        self.assertFalse(report['coverage_healthy'])
        self.assertEqual(report['coverage_summary']['tool_schema_gap_count'],1)
        self.assertEqual(report['coverage_summary']['text_or_unknown_gap_count'],0)
        self.assertTrue(report['attention'])
        self.assertNotIn('SYNTHETIC_WITHHELD_TOOL_BODY',json.dumps(self.events()))

    def test_public_review_function_accepts_discovered_string_path_and_commits_exact_hash(self):
        from collector_review_tools import review
        tool=line({'type':'function_call','name':'synthetic','call_id':'synthetic-call','arguments':'safe synthetic input'})
        self.add_bytes(tool)
        collector=Collector(self.root);collector.collect()
        sha=hashlib.sha256(tool).hexdigest()
        result=review(self.root,SESSION,2,sha)
        self.assertEqual(result['sha256'],sha)
        collector.collect()
        self.assertEqual(self.cursor()['pending_tools'],0)
        raw=self.events('capture.raw_record')
        self.assertEqual(len(raw),1)
        self.assertEqual(self.archive.get(raw[0]['outputs'][0]),tool)


if __name__ == "__main__":
    unittest.main()
