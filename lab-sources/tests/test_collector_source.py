"""Synthetic scoped-discovery and projection tests; no real chat fixtures."""
import copy
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from collector_source import discover_sessions, project_record


SID = "synthetic-session-0001"
STAMP = "2026-09-08T00:00:00.001Z"
SENTINEL = "SYNTHETIC_HIDDEN_DO_NOT_CAPTURE"


def record(payload, typ="response_item"):
    return {"type": typ, "timestamp": STAMP, "payload": payload}


def user(text="visible prompt", kinds=None):
    return record({"type": "message", "role": "user",
                   "content": [{"type": "input_text", "text": text}],
                   "internal_chat_message_metadata_passthrough": {
                       "turn_id": "turn-1", "content_item_kinds": kinds or ["user.text"]}})


def assistant(phase="final", text="visible answer"):
    return record({"type": "message", "role": "assistant", "phase": phase,
                   "content": [{"type": "output_text", "text": text}]})


def project(value, **kwargs):
    return project_record(value, kwargs.get("line", 7), SID,
                          kwargs.get("current_turn", "turn-1"), kwargs.get("current_model", {}))


class DiscoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve()
        self.lab = self.root / "Philosophy Lab"
        self.history = self.root / "History Lab"
        self.private = self.root / "Private"
        self.db = self.root / "metadata.sqlite"
        self.conn = sqlite3.connect(self.db)
        self.conn.execute("CREATE TABLE threads (id TEXT PRIMARY KEY, rollout_path TEXT, cwd TEXT, name TEXT, title TEXT, agent_nickname TEXT, agent_role TEXT, agent_path TEXT, source TEXT, first_user_message TEXT)")
        self.conn.execute("CREATE TABLE thread_spawn_edges (parent_thread_id TEXT, child_thread_id TEXT, status TEXT)")

    def tearDown(self):
        self.conn.close()
        self.temp.cleanup()

    def add(self, sid, cwd, **kwargs):
        self.conn.execute("INSERT INTO threads VALUES (?,?,?,?,?,?,?,?,?,?)", (
            sid, str(self.root / (sid + ".jsonl")), str(cwd), kwargs.get("name"),
            kwargs.get("title", "Title " + sid), kwargs.get("nickname"),
            kwargs.get("role"), kwargs.get("agent_path"), kwargs.get("source", "cli"), SENTINEL))
        self.conn.commit()

    def edge(self, parent, child):
        self.conn.execute("INSERT INTO thread_spawn_edges VALUES (?,?,?)", (parent, child, "running"))
        self.conn.commit()

    def discover(self, explicit=None):
        return discover_sessions(self.db, self.lab, explicit or {})

    def test_exact_scope_explicit_history_recursive_agents_and_titles(self):
        self.add("primary-lab", self.lab, name="Renamed main", title="Old title")
        self.add("historical-main", self.history)
        self.add("cross-cwd-agent", self.history, nickname="Socrates", role="default", agent_path="/root/critic")
        self.add("grandchild-agent", self.private, source='{"subagent":{"thread_spawn":{"secret":"' + SENTINEL + '"}}}')
        self.add("private-sibling", self.private)
        self.add("nested-project", self.lab / "child")
        self.edge("primary-lab", "cross-cwd-agent")
        self.edge("cross-cwd-agent", "grandchild-agent")
        selected = self.discover({"historical-main": str(self.history)})
        indexed = {row["session_id"]: row for row in selected}
        self.assertEqual(set(indexed), {"primary-lab", "historical-main", "cross-cwd-agent", "grandchild-agent"})
        self.assertEqual(indexed["primary-lab"]["title"], "Renamed main")
        agent = indexed["cross-cwd-agent"]
        self.assertEqual((agent["session_kind"], agent["parent_session_id"], agent["agent_name"], agent["role"]),
                         ("subagent", "primary-lab", "Socrates", "default"))
        self.assertEqual(indexed["grandchild-agent"]["selection"], "descendant-of-selected-session")
        self.assertEqual(indexed["historical-main"]["source_project"], "History Lab")
        self.assertNotIn(SENTINEL, json.dumps(selected))

    def test_database_reads_metadata_columns_only(self):
        self.add("primary-lab", self.lab)
        self.add("private-main", self.private)
        original_connect = sqlite3.connect
        reads = []

        def connect(*args, **kwargs):
            connection = original_connect(*args, **kwargs)
            def authorizer(action, table, column, database, trigger):
                if action == sqlite3.SQLITE_READ:
                    reads.append((table, column))
                    if column == "first_user_message":
                        return sqlite3.SQLITE_DENY
                return sqlite3.SQLITE_OK
            connection.set_authorizer(authorizer)
            return connection

        before = self.db.read_bytes()
        with patch("collector_source.sqlite3.connect", connect):
            self.assertEqual(len(self.discover()), 1)
        self.assertNotIn(("threads", "first_user_message"), reads)
        self.assertEqual(self.db.read_bytes(), before)

    def test_guardian_and_unknown_native_other_are_metadata_only_without_source_reads(self):
        self.add('guardian-runtime', self.lab, source=json.dumps({'subagent': {'other': 'guardian'}}))
        self.add('future-runtime', self.lab, source=json.dumps({'subagent': {'other': 'future-review-runtime'}}))
        self.add('malformed-runtime', self.lab, source=json.dumps({'subagent': {'other': {'private': SENTINEL}}}))
        self.add('normal-spawn', self.lab, nickname='Socrates', source=json.dumps({'subagent': {'thread_spawn': {'parent_thread_id': 'primary-lab'}}}))
        # These rollout paths do not exist. Classification must use only the
        # database metadata, before any attempt to open an internal runtime.
        result = {row['session_id']: row for row in self.discover()}
        for sid in ('guardian-runtime', 'future-runtime', 'malformed-runtime'):
            self.assertEqual(result[sid]['session_kind'], 'internal_runtime')
            self.assertEqual(result[sid]['collection_policy'], 'EXCLUDED_INTERNAL_RUNTIME')
            self.assertIn('only metadata inventory', result[sid]['collection_policy_reason'])
        self.assertEqual(result['guardian-runtime']['native_source_subtype'], 'guardian')
        self.assertEqual(result['future-runtime']['native_source_subtype'], 'future-review-runtime')
        self.assertEqual(result['malformed-runtime']['native_source_subtype'], 'UNKNOWN_NATIVE_OTHER_SUBTYPE')
        self.assertEqual(result['normal-spawn']['session_kind'], 'subagent')
        self.assertNotIn('collection_policy', result['normal-spawn'])
        self.assertNotIn(SENTINEL, json.dumps(result))

    def test_ambiguous_runtime_and_spawn_metadata_fails_closed(self):
        self.add('ambiguous-runtime', self.lab, source=json.dumps({'subagent': {
            'other': 'guardian', 'thread_spawn': {'parent_thread_id': 'primary-lab'}}}))
        result = self.discover()[0]
        self.assertEqual(result['session_kind'], 'internal_runtime')
        self.assertEqual(result['collection_policy'], 'EXCLUDED_INTERNAL_RUNTIME')
        self.assertIn('ambiguous', result['collection_policy_reason'])

    def test_local_agent_with_external_parent_does_not_select_parent_or_siblings(self):
        self.add("external-parent", self.private)
        self.add("local-agent", self.lab)
        self.add("private-sibling", self.private)
        self.edge("external-parent", "local-agent")
        self.edge("external-parent", "private-sibling")
        rows = self.discover()
        self.assertEqual([row["session_id"] for row in rows], ["local-agent"])
        self.assertEqual(rows[0]["parent_session_id"], "external-parent")
        self.assertEqual(rows[0]["session_kind"], "subagent")

    def test_missing_explicit_wrong_cwd_and_traversal_fail(self):
        self.add("historical-main", self.history)
        for explicit in ({"missing-session": str(self.history)},
                         {"historical-main": str(self.lab)},
                         {"historical-main": str(self.history / ".." / "other")},
                         {"x' OR 1=1": str(self.history)}):
            with self.subTest(explicit=explicit), self.assertRaises(ValueError):
                self.discover(explicit)

    def test_selected_missing_descendant_is_an_error(self):
        self.add("primary-lab", self.lab)
        self.edge("primary-lab", "missing-agent")
        with self.assertRaisesRegex(ValueError, "descendant metadata unavailable"):
            self.discover()

    def test_cycles_and_conflicting_parents_fail(self):
        self.add("primary-lab", self.lab)
        self.add("agent-child", self.lab)
        self.edge("primary-lab", "agent-child")
        self.edge("agent-child", "primary-lab")
        with self.assertRaisesRegex(ValueError, "cyclic"):
            self.discover()
        self.conn.execute("DELETE FROM thread_spawn_edges WHERE child_thread_id='primary-lab'")
        self.conn.commit()
        self.edge("other-parent", "agent-child")
        with self.assertRaisesRegex(ValueError, "conflicting"):
            self.discover()

    def test_missing_edge_schema_is_not_silently_complete(self):
        self.conn.execute("DROP TABLE thread_spawn_edges")
        self.conn.commit()
        with self.assertRaisesRegex(ValueError, "thread_spawn_edges"):
            self.discover()

    def test_database_symlink_is_rejected(self):
        alias = self.root / "alias.sqlite"
        alias.symlink_to(self.db)
        with self.assertRaisesRegex(ValueError, "symlink"):
            discover_sessions(alias, self.lab, {})


class ProjectionTests(unittest.TestCase):
    def test_known_tool_images_are_metadata_only_review_candidates(self):
        import base64
        from capture_codex import classify
        uri='data:image/png;base64,'+base64.b64encode(SENTINEL.encode()).decode()
        value=record({'type':'custom_tool_call_output','call_id':'call-image','output':[
            {'type':'input_text','text':'Synthetic visible tool caption'},
            {'type':'input_image','image_url':uri,'detail':'original'}]})
        result=project(value)
        self.assertEqual(result['kind'],'tool_pending')
        self.assertEqual(result['payload']['image_count'],1)
        self.assertEqual(result['payload']['body_capture_policy'],'SEPARATE_MEDIA_REVIEW_REQUIRED')
        serialized=json.dumps(result)
        for private in (SENTINEL,uri,'Synthetic visible tool caption'):
            self.assertNotIn(private,serialized)
        # Metadata recognition must not authorize full native image retention.
        self.assertIsNotNone(classify(value,7,{7},set()))
        for block in ({'type':'input_image','image_url':uri,'unknown':SENTINEL},
                      {'type':[],'image_url':uri},
                      {'type':{},'image_url':uri},
                      {'type':'input_image','image_url':'https://example.invalid/private'},
                      {'type':'input_image','image_url':uri,'detail':'unknown'},
                      {'type':'input_image','image_url':uri,'detail':[]},
                      {'type':'input_image','image_url':{'url':uri}}):
            modified=copy.deepcopy(value);modified['payload']['output'][1]=block
            self.assertEqual(project(modified)['kind'],'gap')

    def test_visible_text_preserved_with_metadata_and_no_mutation(self):
        value = user("spaces  \nрусский")
        before = copy.deepcopy(value)
        result = project(value)
        self.assertEqual(value, before)
        self.assertEqual(result["kind"], "text")
        self.assertEqual(result["payload"]["text"], "spaces  \nрусский")
        self.assertEqual(result["payload"]["turn_id"], "turn-1")
        self.assertEqual(result["payload"]["source_timestamp"], STAMP)
        self.assertTrue(result["payload"]["retain_original"])
        for phase in ("commentary", "final", "final_answer"):
            self.assertEqual(project(assistant(phase))["kind"], "text")

    def test_hidden_reasoning_roles_and_context_never_project_bodies(self):
        hidden = [assistant("analysis", SENTINEL),
                  record({"type": "reasoning", "summary": SENTINEL}),
                  record({"type": "message", "role": "system", "content": SENTINEL}),
                  record({"type": "message", "role": "developer", "content": SENTINEL}),
                  user(SENTINEL, ["environments.environment_context"]),
                  record({"type": "agent_reasoning", "text": SENTINEL}, "event_msg"),
                  record({"secret": SENTINEL}, "world_state")]
        for value in hidden:
            with self.subTest(value_type=value["type"]):
                result = project(value)
                self.assertEqual(result["kind"], "excluded")
                self.assertNotIn(SENTINEL, json.dumps(result))

    def test_lifecycle_projects_only_known_fields_and_tracks_current_turn(self):
        start = project(record({"type": "task_started", "turn_id": "turn-2", "secret": SENTINEL}, "event_msg"))
        self.assertEqual(start["next_turn"], "turn-2")
        self.assertEqual(start["next_model"]["status"], "unknown")
        complete = project(record({"type": "task_complete", "turn_id": "turn-1", "duration_ms": 14377,
                                   "last_agent_message": SENTINEL}, "event_msg"))
        self.assertEqual(complete["payload"]["duration_ms"], 14377)
        self.assertIsNone(complete["next_turn"])
        self.assertNotIn(SENTINEL, json.dumps([start, complete]))
        interrupted = project(record({"type": "turn_aborted", "turn_id": "turn-1", "reason": "interrupted"}, "event_msg"))
        self.assertEqual(interrupted["payload"]["reason"], "interrupted")
        self.assertIsNone(interrupted["next_turn"])
        older = project(record({"type": "task_complete", "turn_id": "older-turn"}, "event_msg"))
        self.assertEqual(older["next_turn"], "turn-1")

    def test_invalid_lifecycle_data_is_gap(self):
        for duration in (-1, True, "100", float("nan"), float("inf"), 2 ** 10000):
            result = project(record({"type": "task_complete", "turn_id": "turn-1", "duration_ms": duration}, "event_msg"))
            self.assertEqual(result["kind"], "gap")
        for value in ({"type": "task_started", "turn_id": []},
                      {"type": "task_complete", "turn_id": "t", "completed_at": "unknown"},
                      {"type": "new_lifecycle_record"}):
            self.assertEqual(project(record(value, "event_msg"))["kind"], "gap")

    def test_native_epoch_seconds_and_reported_first_token_metric_are_explicit(self):
        result = project(record({"type": "task_complete", "turn_id": "turn-1",
            "started_at": 1788834346, "completed_at": 1788834361, "duration_ms": 14377,
            "time_to_first_token_ms": 5767, "last_agent_message": SENTINEL}, "event_msg"))
        self.assertEqual(result["kind"], "lifecycle")
        payload = result["payload"]
        self.assertEqual(payload["started_at"], "2026-09-08T02:25:46+00:00")
        self.assertEqual(payload["completed_at"], "2026-09-08T02:26:01+00:00")
        self.assertEqual(payload["lifecycle_time_observations"]["started_at"]["value"], 1788834346)
        self.assertEqual(payload["lifecycle_time_observations"]["started_at"]["unit"], "unix-seconds")
        self.assertEqual(payload["lifecycle_time_observations"]["started_at"]["precision"], "one-second")
        self.assertEqual(payload["duration_ms"], 14377)
        self.assertEqual(payload["time_to_first_token_ms"], 5767)
        self.assertEqual(payload["time_to_first_token_source"], "native-task-lifecycle-reported-metric")
        self.assertNotIn(SENTINEL, json.dumps(result))
        iso = project(record({"type": "task_started", "turn_id": "turn-1",
                              "started_at": "2026-09-07T19:25:46-07:00"}, "event_msg"))
        self.assertEqual(iso["payload"]["started_at"], "2026-09-08T02:25:46+00:00")
        self.assertEqual(iso["payload"]["lifecycle_time_observations"]["started_at"]["unit"], "iso8601-with-timezone")

    def test_unsupported_epoch_units_and_bad_first_token_metrics_are_gaps(self):
        for value in (True, "1788834346", 1788834346000, float("inf"), {}, None):
            result = project(record({"type": "task_started", "turn_id": "turn-1", "started_at": value}, "event_msg"))
            self.assertEqual(result["kind"], "gap")
        for value in (True, -1, "500", float("nan")):
            result = project(record({"type": "task_complete", "turn_id": "turn-1", "time_to_first_token_ms": value}, "event_msg"))
            self.assertEqual(result["kind"], "gap")

    def test_native_item_mirrors_and_settings_envelopes_are_excluded_without_bodies(self):
        for subtype in ("item_completed", "thread_settings_applied"):
            result = project(record({"type": subtype, "item": SENTINEL, "settings": {"hidden": SENTINEL}}, "event_msg"))
            self.assertEqual(result["kind"], "excluded")
            self.assertNotIn(SENTINEL, json.dumps(result))

    def test_model_observations_safe_and_reset_between_turns(self):
        value = record({"turn_id": "turn-2", "model": "gpt-test", "effort": "ultra", "base_instructions": SENTINEL}, "turn_context")
        result = project(value)
        self.assertEqual(result["kind"], "model")
        self.assertEqual(result["next_model"]["value"], {"model": "gpt-test", "reasoning_effort": "ultra"})
        self.assertEqual(result["next_turn"], "turn-2")
        self.assertNotIn(SENTINEL, json.dumps(result))
        shown = project(assistant(), current_model=dict(result["next_model"], malicious=SENTINEL))
        self.assertNotIn(SENTINEL, json.dumps(shown))
        self.assertEqual(shown["payload"]["observed_model"]["status"], "known")
        reset = project(record({"type": "task_started", "turn_id": "turn-3"}, "event_msg"), current_model=result["next_model"])
        self.assertEqual(reset["next_model"]["status"], "unknown")

    def test_tools_are_review_metadata_without_body(self):
        call = record({"type": "function_call", "name": "calculate", "call_id": "call-1", "arguments": SENTINEL})
        result = project(call)
        self.assertEqual(result["kind"], "tool_pending")
        self.assertEqual(result["payload"]["name"], "calculate")
        self.assertEqual(len(result["payload"]["canonical_record_sha256"]), 64)
        self.assertNotIn(SENTINEL, json.dumps(result))
        output = record({"type": "function_call_output", "call_id": "call-1", "output": SENTINEL})
        self.assertEqual(project(output)["kind"], "tool_pending")
        call["payload"]["arguments"] = "base_instructions " + SENTINEL
        self.assertEqual(project(call)["kind"], "excluded")
        self.assertNotIn(SENTINEL, json.dumps(project(call)))

    def test_automation_heartbeat_is_metadata_with_distinct_origin_and_no_call_id(self):
        value = record({'type':'function_call_output','id':'fco_synthetic','name':'automation_update',
                        'namespace':'codex_app','output':'<heartbeat><automation_id>synthetic</automation_id>'
                        '<current_time_iso>2026-09-08T00:00:00Z</current_time_iso>'
                        '<instructions>'+SENTINEL+'</instructions></heartbeat>'})
        result = project(value)
        self.assertEqual(result['kind'], 'tool_pending')
        self.assertEqual(result['payload']['origin'], 'AUTOMATION')
        self.assertIsNone(result['payload']['call_id'])
        self.assertNotIn(SENTINEL,json.dumps(result))
        mutations = []
        for key, item in [('namespace','other'),('name','other'),('id','unknown'),
                          ('encrypted_content',SENTINEL),('call_id',None)]:
            changed=copy.deepcopy(value);changed['payload'][key]=item;mutations.append(changed)
        for body in ['<!DOCTYPE heartbeat [<!ENTITY x "secret">]>'+value['payload']['output'],
                     value['payload']['output'].replace(SENTINEL,'&lt;system&gt;hidden'),
                     value['payload']['output'].replace(SENTINEL,'<nested>hidden</nested>'),
                     value['payload']['output'].replace('<heartbeat>','<heartbeat extra="x">')]:
            changed=copy.deepcopy(value);changed['payload']['output']=body;mutations.append(changed)
        for changed in mutations:
            with self.subTest(keys=sorted(changed['payload'])):
                rejected=project(changed)
                self.assertEqual(rejected['kind'],'gap')
                self.assertEqual(rejected['payload']['surface'],'tools')
                self.assertNotIn(SENTINEL,json.dumps(rejected))

    def test_mixed_user_attachment_retains_only_text_with_explicit_gaps(self):
        value = user("Explain this picture", ["user.text", "user.image"])
        value["payload"]["content"].append({"type": "input_image", "image_url": SENTINEL})
        value["metadata"] = {"client_authored": False,
                             "fallback_token_limit_override": 12000,
                             "mcp_attribution": {"status": "attribution_error",
                                                "error_reason": "source attribution unavailable"}}
        result = project(value)
        self.assertEqual(result["kind"], "text")
        self.assertEqual(result["payload"]["text"], "Explain this picture")
        self.assertFalse(result["payload"]["retain_original"])
        self.assertIn("attachment_body_not_captured", result["payload"]["attachment_gaps"])
        self.assertNotIn(SENTINEL, json.dumps(result))
        self.assertNotIn("attribution_error", json.dumps(result))

    def test_mixed_attachment_type_must_match_declared_user_media(self):
        value = user("Explain this", ["user.text", "user.image"])
        value["payload"]["content"].append({"type": "input_image", "image_url": SENTINEL})
        value["payload"]["internal_chat_message_metadata_passthrough"]["content_item_kinds"] = ["user.text", "user.file"]
        result = project(value)
        self.assertEqual(result["kind"], "gap")
        self.assertNotIn(SENTINEL, json.dumps(result))

    def test_missing_or_unsupported_user_provenance_is_gap(self):
        values = [user(kinds=["user.unknown_future_attachment"]),
                  user(kinds=["user.text", "environments.environment_context"])]
        absent = user()
        del absent["payload"]["internal_chat_message_metadata_passthrough"]
        values.append(absent)
        for value in values:
            with self.subTest(value=value):
                result = project(value)
                self.assertEqual(result["kind"], "gap")
                self.assertNotIn(SENTINEL, json.dumps(result))

    def test_attachment_only_user_send_is_countable_without_retaining_attachment(self):
        value = user(kinds=["user.image"])
        value['payload']['content'] = [{'type': 'input_image', 'data': SENTINEL}]
        result = project(value)
        self.assertEqual(result['kind'], 'text')
        self.assertEqual(result['payload']['role'], 'user')
        self.assertEqual(result['payload']['text'], '')
        self.assertEqual(result['payload']['text_blocks'], [])
        self.assertFalse(result['payload']['retain_original'])
        self.assertIn('attachment_only_prompt_no_text', result['payload']['attachment_gaps'])
        self.assertIn('attachment_body_not_captured', result['payload']['attachment_gaps'])
        self.assertNotIn(SENTINEL, json.dumps(result))

    def test_session_metadata_projects_agent_identity_without_hidden_envelope(self):
        value = record({"id": SID, "cwd": "/some/project", "base_instructions": SENTINEL,
                        "source": {"subagent": {"thread_spawn": {"parent_thread_id": "parent-session",
                            "agent_nickname": "Socrates", "agent_role": "default", "task": SENTINEL}}}}, "session_meta")
        result = project(value)
        self.assertEqual(result["kind"], "agent_metadata")
        self.assertEqual(result["payload"]["parent_session_id"], "parent-session")
        self.assertEqual(result["payload"]["agent_nickname"], "Socrates")
        self.assertNotIn(SENTINEL, json.dumps(result))

    def test_unknown_and_malformed_records_never_claim_success(self):
        examples = [[], {}, record({"type": ["malformed"]}), record({"type": "future-message"}),
                    record({"type": "message", "role": "assistant", "phase": "new-phase", "content": []}),
                    {"type": [], "timestamp": STAMP, "payload": {}},
                    dict(user(), hidden=SENTINEL), dict(user(), timestamp="no-zone")]
        for value in examples:
            with self.subTest(value=value):
                result = project(value)
                self.assertEqual(result["kind"], "gap")
                self.assertNotIn(SENTINEL, json.dumps(result))


if __name__ == "__main__":
    unittest.main()
