"""Synthetic archive-to-view acceptance tests; no real conversation fixtures."""
import json
from pathlib import Path
import re
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from collector_views import refresh
from research_archive import Archive
from unittest.mock import patch
import chat_inventory


SID = "synthetic-view-primary"
CHILD = "synthetic-view-child"
UNKNOWN = {"status": "unknown", "reason": "synthetic observation not yet present"}


def stamp(seconds):
    return "2026-09-08T00:00:%06.3fZ" % seconds


def model(name="synthetic-model", effort="medium", line=3):
    return {"status": "known", "value": {"model": name, "reasoning_effort": effort},
            "source_line": line, "source": "synthetic-turn-context"}


class CollectorViewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="synthetic-collector-view-")
        self.root = Path(self.temp.name).resolve()
        self.archive = Archive(self.root / "research/archive").init()
        self.sequence = 0
        self.identity()

    def tearDown(self):
        self.temp.cleanup()

    def append(self, kind, payload, sid=SID, time=0, **kwargs):
        self.sequence += 1
        request = {"kind": kind, "session_id": sid, "run_id": "synthetic-view-run",
                   "operation_id": "synthetic-view-operation", "attempt_id": "synthetic-view-attempt",
                   "actor": {"id": "synthetic-view-test", "role": "test"},
                   "timestamp": stamp(time), "payload": payload, **kwargs}
        return self.archive.append(request, "synthetic-view-%d" % self.sequence)

    def identity(self, sid=SID, kind="primary_chat", title="Synthetic chat", project="Philosophy Lab"):
        return self.append("capture.session_identified", {
            "session_id": sid, "title": title, "source_project": project,
            "source_cwd": str(self.root), "session_kind": kind,
            "parent_session_id": SID if kind == "subagent" else None,
            "agent_name": "Socrates" if kind == "subagent" else None,
            "role": "default" if kind == "subagent" else None}, sid=sid)

    def lifecycle(self, event_type, line, turn="turn-1", time=0, sid=SID, **extra):
        return self.append("collector.lifecycle", {"session_id": sid, "source_line": line,
            "turn_id": turn, "event_type": event_type, "source_timestamp": stamp(time), **extra},
            sid=sid, time=time)

    def observe_model(self, line, turn="turn-1", time=0, observed=None, sid=SID):
        return self.append("collector.model", {"session_id": sid, "source_line": line,
            "turn_id": turn, "source_timestamp": stamp(time), "observed_model": observed or model(line=line)},
            sid=sid, time=time)

    def message(self, role, text, line, turn="turn-1", phase=None, time=0,
                observed=None, sid=SID, projected=False, blocks=None, companion=True):
        blocks = blocks if blocks is not None else [text]
        raw = None
        if not projected:
            item = {"type": "message", "role": role,
                    "content": [{"type": "input_text" if role == "user" else "output_text", "text": text}
                                for text in blocks],
                    "internal_chat_message_metadata_passthrough": {
                        "turn_id": turn, "content_item_kinds": ["user.text"] if role == "user" else []}}
            if phase is not None:
                item["phase"] = phase
            native = {"timestamp": stamp(time), "type": "response_item", "payload": item}
            original_bytes = (json.dumps(native, ensure_ascii=False, indent=None) + "\n").encode()
            digest = self.archive.put(original_bytes)
            raw = self.append("capture.raw_record", {"format": "codex-visible-selection.v1", "source_line": line, "raw_sha256": digest,
                              "source_type": "message", "source_timestamp": stamp(time)},
                              sid=sid, time=time, outputs=[digest], model=observed or UNKNOWN)
        if companion or projected:
            payload = {"session_id": sid, "source_line": line, "source_timestamp": stamp(time),
                       "turn_id": turn, "role": role, "phase": phase,
                       "observed_model": observed or UNKNOWN, "retain_original": not projected,
                       "raw_event_id": raw["id"] if raw else None,
                       "attachment_gaps": ["attachment_body_not_captured"] if projected else []}
            if projected:
                payload.update(text=text, text_blocks=blocks)
            self.append("collector.message", payload, sid=sid, time=time,
                        parents=[raw["id"]] if raw else [])
        return raw

    def coverage(self, line, sid=SID, **kwargs):
        cursor = {"lines": line, "committed_at": stamp(40), "pending_tools": 2,
                  "gaps": [], "exclusions": {"hidden_reasoning": 1}, **kwargs}
        return self.append("collector.coverage", {"cursor": cursor,
                          "text_status": "TEXT_COMPLETE_THROUGH_CURSOR"}, sid=sid, time=40)

    def load(self, filename="turns.json", sid=SID):
        return json.loads((self.root / "research/views/chats" / sid / filename).read_text())

    def test_turn_keeps_multiple_prompts_and_visible_responses_in_source_order(self):
        self.lifecycle("task_started", 2, time=1)
        self.message("user", "Initial prompt", 3, time=1.1)
        self.observe_model(4, time=1.2)
        self.message("assistant", "Working", 5, phase="commentary", time=2)
        self.message("user", "Steering during the same turn", 6, time=3)
        self.message("assistant", "Final answer", 7, phase="final_answer", time=6)
        self.lifecycle("task_complete", 8, time=6.5, duration_ms=5500)
        self.coverage(8)
        summary = refresh(self.root, self.archive)
        turns = self.load()["turns"]
        self.assertEqual(len(turns), 1)
        turn = turns[0]
        self.assertEqual([m["text"] for m in turn["messages"]],
                         ["Initial prompt", "Working", "Steering during the same turn", "Final answer"])
        self.assertEqual([m["source_line"] for m in turn["messages"]], [3, 5, 6, 7])
        self.assertEqual(turn["status"], "COMPLETED")
        self.assertEqual(turn["duration_ms"], 5500)
        self.assertEqual(turn["time_to_first_visible_ms"], 1000)
        self.assertTrue(turn["final_answer_present"])
        self.assertEqual(summary["sessions"][0]["counts"],
                         {"user_prompts": 2, "assistant_commentary": 1, "assistant_final": 1})
        self.assertEqual(turn["messages"][0]["origin"], "HUMAN")
        self.assertEqual(turn["messages"][1]["origin"], "AI")

    def test_late_native_completion_updates_existing_turn_without_rewriting_archive(self):
        self.lifecycle("task_started", 2, time=1)
        self.message("user", "Prompt", 3, time=1.1)
        self.message("assistant", "Completed visible answer", 4, phase="final", time=5)
        self.coverage(4)
        refresh(self.root, self.archive)
        first = self.load()["turns"][0]
        self.assertEqual(first["status"], "ONGOING")
        self.assertIsNone(first["duration_ms"])
        originals = {p.name: p.read_bytes() for p in (self.archive.root / "events").iterdir() if p.name.endswith(".json")}
        self.lifecycle("task_complete", 5, time=5.5, duration_ms=4500)
        self.coverage(5)
        refresh(self.root, self.archive)
        turn = self.load()["turns"][0]
        self.assertEqual(turn["status"], "COMPLETED")
        self.assertEqual(turn["duration_ms"], 4500)
        self.assertEqual(turn["ended_at"], stamp(5.5))
        self.assertEqual(len(turn["messages"]), 2)
        for filename, content in originals.items():
            self.assertEqual((self.archive.root / "events" / filename).read_bytes(), content)

    def test_interruption_records_zero_final_and_unknown_duration(self):
        self.lifecycle("task_started", 2, time=1)
        self.message("user", "Interrupted request", 3, time=1.1)
        self.message("assistant", "Work in progress", 4, phase="commentary", time=2)
        self.lifecycle("turn_aborted", 5, time=3, reason="interrupted")
        refresh(self.root, self.archive)
        turn = self.load()["turns"][0]
        self.assertEqual(turn["status"], "INTERRUPTED")
        self.assertEqual(turn["reason"], "interrupted")
        self.assertFalse(turn["final_answer_present"])
        self.assertIsNone(turn["duration_ms"])
        text = (self.root / "research/views/chats" / SID / "conversation.md").read_text()
        self.assertIn("Статус: INTERRUPTED; финальный ответ: нет", text)
        self.assertIn("Длительность: UNKNOWN", text)

    def test_model_arriving_after_prompt_applies_to_its_turn_not_the_next(self):
        self.lifecycle("task_started", 2, time=1)
        self.message("user", "First turn", 3, time=1.1)
        self.observe_model(4, observed=model(effort="medium", line=4), time=1.2)
        self.message("assistant", "First answer", 5, phase="final", time=2)
        self.lifecycle("task_complete", 6, time=2.5, duration_ms=1500)
        self.lifecycle("task_started", 7, turn="turn-2", time=3)
        self.message("user", "Second turn", 8, turn="turn-2", time=3.1)
        self.observe_model(9, turn="turn-2", observed=model("synthetic-new-model", "ultra", 9), time=3.2)
        self.message("assistant", "Second answer", 10, turn="turn-2", phase="final", time=4)
        refresh(self.root, self.archive)
        turns = self.load()["turns"]
        self.assertEqual([turn["turn_id"] for turn in turns], ["turn-1", "turn-2"])
        for turn, name, effort in ((turns[0], "synthetic-model", "medium"),
                                  (turns[1], "synthetic-new-model", "ultra")):
            self.assertEqual(turn["model"]["value"], {"model": name, "reasoning_effort": effort})
            self.assertTrue(all(message["model"]["value"] == turn["model"]["value"] for message in turn["messages"]))

    def test_raw_message_and_collector_companion_count_as_one_with_exact_original_link(self):
        raw = self.message("user", "  Exact Russian: привет\nwith trailing space  ", 3)
        self.message("assistant", "Answer", 4, phase="final")
        summary = refresh(self.root, self.archive)
        self.assertEqual(summary["sessions"][0]["counts"], {"user_prompts": 1, "assistant_final": 1})
        messages = self.load("conversation.json")["messages"]
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0]["text"], "  Exact Russian: привет\nwith trailing space  ")
        self.assertEqual(messages[0]["raw_sha256"], raw["payload"]["raw_sha256"])
        directory = self.root / "research/views/chats" / SID
        for filename, expected in (("conversation.md", 2), ("prompts.md", 1)):
            links = re.findall(r"\[Оригинальная запись\]\(([^)]+)\)", (directory / filename).read_text())
            self.assertEqual(len(links), expected)
            for link in links:
                path = (directory / link).resolve()
                self.assertEqual(path.parent, self.archive.root / "objects")
                self.assertTrue(path.is_file())
                self.assertEqual(json.loads(path.read_bytes())["type"], "response_item")

    def test_projected_attachment_text_is_visible_and_never_claims_original(self):
        text = "Text next to an unavailable attachment.\n\n```\ncode fence\n```"
        self.message("user", text, 3, projected=True)
        self.coverage(3, gaps=[{"source_line": 3, "reason": "attachment_body_not_captured"}])
        summary = refresh(self.root, self.archive)
        messages = self.load("conversation.json")["messages"]
        self.assertEqual(messages[0]["text"], text)
        self.assertFalse(messages[0]["retain_original"])
        self.assertEqual(messages[0]["attachment_gaps"], ["attachment_body_not_captured"])
        self.assertEqual(len(summary["sessions"][0]["gaps"]), 1)
        rendered = (self.root / "research/views/chats" / SID / "conversation.md").read_text()
        self.assertIn(text, rendered)
        self.assertIn("Сохранена проекция текста", rendered)
        self.assertNotIn("[Оригинальная запись]", rendered)
        self.assertIn("````text", rendered)

    def test_subagent_user_role_is_not_attributed_to_human(self):
        self.identity(sid=CHILD, kind="subagent", title="Socrates — critique")
        self.message("user", "Parent assignment or inherited prompt", 3, sid=CHILD)
        self.message("assistant", "Critique", 4, phase="final", sid=CHILD)
        summary = refresh(self.root, self.archive)
        messages = self.load("conversation.json", sid=CHILD)["messages"]
        self.assertEqual(messages[0]["origin"], "UNKNOWN_DISPATCH_OR_INHERITED")
        self.assertEqual(messages[1]["origin"], "AI")
        self.assertEqual(summary["session_kinds"], {"subagent": 1, "primary_chat": 1})
        child = next(item for item in summary["sessions"] if item["session_id"] == CHILD)
        self.assertEqual(child["parent_session_id"], SID)
        self.assertEqual(child["agent_name"], "Socrates")
        self.assertEqual(child["role"], "default")

    def test_automation_metadata_remains_separate_from_human_prompts(self):
        self.message('user','Human instruction',3)
        metadata={'source_line':5,'origin':'AUTOMATION','automation_id':'synthetic',
                  'delivery_type':'automation_heartbeat','call_id':None}
        self.append('collector.tool_pending',dict(metadata,review_status='PENDING'))
        self.append('collector.tool_reviewed',dict(metadata,raw_event_id='synthetic-reviewed-reference'))
        summary=refresh(self.root,self.archive)
        self.assertEqual(summary['sessions'][0]['counts'],{'user_prompts':1,'automation_triggers':1})
        self.assertEqual(len(self.load('prompts.json')['messages']),1)
        triggers=self.load('turns.json')['automation_triggers']
        self.assertEqual(len(triggers),1)
        self.assertEqual(triggers[0]['origin'],'AUTOMATION')

    def test_detected_empty_session_counts_and_rename_changes_display_not_id(self):
        self.identity(sid=CHILD, kind="subagent", title="Old display name", project="Historical Factory")
        first = refresh(self.root, self.archive)
        self.assertEqual(first["session_count"], 2)
        child = next(item for item in first["sessions"] if item["session_id"] == CHILD)
        self.assertEqual(child["counts"], {})
        self.assertEqual(child["text_coverage"], "NOT_AUDITED")
        self.identity(sid=CHILD, kind="subagent", title="New display name", project="Historical Factory")
        second = refresh(self.root, self.archive)
        self.assertEqual(second["session_count"], 2)
        child = next(item for item in second["sessions"] if item["session_id"] == CHILD)
        self.assertEqual(child["title"], "New display name")
        self.assertEqual(second["projects"], {"Historical Factory": 1, "Philosophy Lab": 1})
        self.assertEqual(self.load(sid=CHILD)["session"]["session_id"], CHILD)

    def test_raw_only_history_survives_and_multiple_text_blocks_are_exact(self):
        self.message("user", "unused", 3, blocks=["α  ", "\nβ\n"], companion=False)
        refresh(self.root, self.archive)
        message = self.load("prompts.json")["messages"][0]
        self.assertEqual(message["text"], "α  \nβ\n")
        self.assertEqual(message["turn_id"], "turn-1")
        self.assertIsNotNone(message["raw_sha256"])
        text = (self.root / "research/views/chats" / SID / "prompts.md").read_text()
        self.assertIn("α  \nβ\n", text)

    def test_repeat_refresh_is_stable_and_writes_expected_portable_filenames(self):
        self.message("user", "Prompt", 3)
        self.message("assistant", "Answer", 4, phase="final")
        self.coverage(4)
        refresh(self.root, self.archive)
        directory = self.root / "research/views/chats" / SID
        self.assertEqual({path.name for path in directory.iterdir()},
                         {"turns.json", "conversation.json", "prompts.json", "conversation.md", "prompts.md"})
        before = {path: (path.read_bytes(), path.stat().st_mtime_ns) for path in (self.root / "research/views").rglob("*") if path.is_file()}
        refresh(self.root, self.archive)
        for path, (content, mtime) in before.items():
            self.assertEqual(path.read_bytes(), content)
            self.assertEqual(path.stat().st_mtime_ns, mtime)
        self.assertTrue(self.archive.validate()["ok"])

    def mixed_provider_records(self):
        self.message('user', 'Codex neutral human request', 3)
        sid = 'synthetic-claude-provider'
        fragments = [
            ('message', 'user', 'UNKNOWN', 'Synthetic AI-prepared launch'),
            ('message', 'assistant', 'AI_PROVIDER_RESPONSE', {'type': 'text', 'text': 'Synthetic visible Claude reply'}),
            ('tool_call', 'assistant', 'AI_PROVIDER_RESPONSE', {'type': 'tool_use', 'id': 'tool-1', 'name': 'Write', 'input': {'content': 'Synthetic file'}}),
            ('tool_result', 'tool', 'TOOL_OUTPUT', {'type': 'tool_result', 'tool_use_id': 'tool-1', 'content': 'Saved'}),
        ]
        raw_digests = set()
        for index, (source_type, role, origin, fragment) in enumerate(fragments, 1):
            digest = self.archive.put(json.dumps(fragment).encode()); raw_digests.add(digest)
            self.append('capture.raw_record', {'format': 'claude-visible-fragments.v1',
                'source_line': index, 'source_fragment': '0', 'raw_sha256': digest,
                'source_type': source_type, 'contribution_origin': origin, 'job_id': 'synthetic-job',
                'workspace': '/synthetic/claude-job', 'full_original_record_retained': False},
                sid=sid, actor={'id': 'claude:' + role, 'role': role}, outputs=[digest])
        digest = self.archive.put(json.dumps({'selected_range': [1, 4], 'status': 'BOUNDED_COMPLETE', 'gaps': []}).encode())
        self.append('capture.coverage', {'format': 'claude-visible-fragments.v1', 'job_id': 'synthetic-job',
                    'workspace': '/synthetic/claude-job', 'status': 'BOUNDED_COMPLETE', 'gaps': [],
                    'report_sha256': digest}, sid=sid, outputs=[digest])
        self.append('bridge.return.collected', {'protocol': 'philosophy-claude-bridge.v1', 'job_id': 'synthetic-job',
                    'workspace': '/synthetic/claude-job', 'collection_id': 'synthetic-collection',
                    'claim_event_id': 'synthetic-bound-claim', 'source_coverage': 'BOUNDED_COMPLETE'}, sid=sid)
        return sid, raw_digests

    def test_mixed_provider_raw_records_have_separate_metadata_inventory(self):
        sid, raw_digests = self.mixed_provider_records()
        summary = refresh(self.root, self.archive)
        self.assertEqual(summary['session_count'], 1)
        self.assertEqual(summary['sessions'][0]['counts']['user_prompts'], 1)
        external = summary['provider_inventory']['sessions']
        self.assertEqual(len(external), 1)
        row = external[0]
        self.assertEqual(row['session_id'], sid)
        self.assertEqual(row['provider'], 'CLAUDE')
        self.assertEqual(row['job_id'], 'synthetic-job')
        self.assertEqual(row['counts']['raw_fragments'], 4)
        self.assertEqual(row['counts']['user_role_message_fragments'], 1)
        self.assertNotIn('user_prompts', row['counts'])
        self.assertEqual(row['contribution_origins']['UNKNOWN'], 1)
        self.assertEqual(row['coverage_reports'][0]['selected_range'], [1, 4])
        self.assertEqual(len(row['returns']), 1)
        self.assertEqual({r['raw_sha256'] for r in row['originals']}, raw_digests)
        self.assertFalse((self.root / 'research/views/chats' / sid).exists())
        second = refresh(self.root, self.archive, changed_sessions={SID})
        self.assertEqual(second['provider_inventory'], summary['provider_inventory'])

    def test_legacy_inventory_and_transcript_export_do_not_parse_claude_fragments(self):
        sid, raw_digests = self.mixed_provider_records()
        events, validation = self.archive.events(), self.archive.validate()
        original_get = self.archive.get
        def get(digest):
            if digest in raw_digests: self.fail('Claude original body must not be parsed by Codex inventory')
            return original_get(digest)
        # Archive integrity audit legitimately reads all object bytes to hash
        # them. The assertion concerns the inventory's semantic body reads.
        with patch.object(self.archive, 'events', return_value=events), patch.object(self.archive, 'validate', return_value=validation), patch.object(self.archive, 'get', side_effect=get):
            report = chat_inventory.inventory(self.archive)
            self.assertEqual(report['session_count_with_raw_records'], 1)
            self.assertEqual(report['provider_inventory']['sessions'][0]['session_id'], sid)
            chat_inventory.write_transcripts(self.archive, self.root / 'research/views', report)
        self.assertFalse((self.root / 'research/views/chats' / sid).exists())

    def test_unknown_provider_is_visible_as_metadata_and_its_body_never_read(self):
        digest = self.archive.put(b'UNKNOWN_PROVIDER_BODY_NOT_TO_BE_PARSED')
        self.append('capture.raw_record', {'format': 'future-provider.v99', 'raw_sha256': digest,
                    'source_line': 1}, sid='synthetic-future', outputs=[digest])
        events = self.archive.events()
        original_get = self.archive.get
        def get(value):
            if value == digest: self.fail('Unknown provider original body was read')
            return original_get(value)
        with patch.object(self.archive, 'get', side_effect=get):
            report = refresh(self.root, self.archive, events=events)
            row = report['provider_inventory']['sessions'][0]
            self.assertEqual(row['provider'], 'UNKNOWN')
            self.assertEqual(row['status'], 'UNSUPPORTED_FORMAT_METADATA_ONLY')
            self.assertEqual(row['counts']['raw_fragments'], 1)
            self.assertEqual(row['originals'][0]['raw_sha256'], digest)
        self.assertNotIn('UNKNOWN_PROVIDER_BODY_NOT_TO_BE_PARSED', json.dumps(report))

    def unsupported_original(self, line=3, data=None, companion=True):
        sentinel='UNSUPPORTED_ORIGINAL_MUST_NOT_RENDER'
        data=data if data is not None else (json.dumps({
            'timestamp':stamp(1),'ordinal':None,'type':'response_item',
            'payload':{'type':'message','role':'user','content':[{'type':'input_text','text':sentinel}],
                       'internal_chat_message_metadata_passthrough':{'content_item_kinds':['user.text']}}})+'\n').encode()
        digest=self.archive.put(data)
        raw=self.append('capture.raw_record',{'format':'codex-visible-selection.v1',
            'source_line':line,'raw_sha256':digest,'source_type':'message'},outputs=[digest],model=UNKNOWN)
        if companion:
            self.append('collector.message',{'source_line':line,'role':'user','raw_event_id':raw['id'],
                'text':sentinel,'turn_id':'turn-1','source_timestamp':stamp(1)},parents=[raw['id']])
        return raw,data

    def assert_no_rejected_body(self, sentinel='UNSUPPORTED_ORIGINAL_MUST_NOT_RENDER'):
        for path in (self.root/'research/views').rglob('*'):
            if path.is_file(): self.assertNotIn(sentinel,path.read_text(),str(path))

    def test_unsupported_old_original_and_companion_become_one_view_gap_without_archive_change(self):
        raw,data=self.unsupported_original()
        self.message('assistant','Still readable',4,phase='final')
        self.identity(sid=CHILD,kind='subagent')
        self.message('assistant','Another chat still renders',2,sid=CHILD,phase='final')
        self.coverage(4)
        before=self.archive.events()
        report=refresh(self.root,self.archive)
        row=next(s for s in report['sessions'] if s['session_id']==SID)
        self.assertEqual(row['view_status'],'GAPS')
        self.assertEqual(row['text_coverage'],'TEXT_COMPLETE_THROUGH_CURSOR')
        self.assertEqual(row['counts'],{'assistant_final':1})
        self.assertEqual(row['view_gaps'],[{'raw_event_id':raw['id'],'source_line':3,
            'reason':'unsupported_or_invalid_codex_original','body_rendered':False}])
        self.assertEqual(report['view_gap_count'],1)
        self.assertEqual(report['sessions_with_view_gaps'],1)
        self.assertEqual(self.load('conversation.json')['messages'][0]['text'],'Still readable')
        self.assertEqual(self.load('conversation.json',sid=CHILD)['messages'][0]['text'],
                         'Another chat still renders')
        self.assertIn('Пробелы отображения: 1',
                      (self.root/'research/views/chats'/SID/'conversation.md').read_text())
        self.assert_no_rejected_body()
        self.assertEqual(self.archive.events(),before)
        self.assertEqual(self.archive.get(raw['payload']['raw_sha256']),data)

    def test_invalid_json_and_duplicate_keys_are_view_gaps_without_body(self):
        data=b'{"UNSUPPORTED_ORIGINAL_MUST_NOT_RENDER": '
        self.unsupported_original(line=3,data=data,companion=False)
        self.unsupported_original(line=4,data=b'{"type":"response_item","type":"hidden"}',companion=True)
        report=refresh(self.root,self.archive)
        self.assertEqual(report['view_gap_count'],2)
        self.assertEqual(self.load('conversation.json')['messages'],[])
        self.assert_no_rejected_body()

    def test_missing_or_non_raw_reference_is_gap_and_never_uses_companion_text(self):
        identity=self.identity()
        for line,reference in [(3,'event-missing-original'),(4,identity['id'])]:
            self.append('collector.message',{'source_line':line,'role':'user','raw_event_id':reference,
                'text':'UNSUPPORTED_ORIGINAL_MUST_NOT_RENDER','turn_id':'turn-1'})
        report=refresh(self.root,self.archive)
        self.assertEqual(report['view_gap_count'],2)
        self.assertEqual(self.load('conversation.json')['messages'],[])
        self.assertTrue(all(g['reason']=='invalid_or_missing_raw_reference'
                            for g in report['sessions'][0]['view_gaps']))
        self.assert_no_rejected_body()

    def test_unreadable_object_becomes_gap_while_other_messages_render(self):
        raw,_=self.unsupported_original(companion=True)
        self.message('assistant','Readable',4,phase='final')
        events=self.archive.events();original_get=self.archive.get
        def get(digest):
            if digest==raw['payload']['raw_sha256']:raise OSError('UNSUPPORTED_ORIGINAL_MUST_NOT_RENDER')
            return original_get(digest)
        with patch.object(self.archive,'get',side_effect=get):report=refresh(self.root,self.archive,events=events)
        self.assertEqual(report['view_gap_count'],1)
        self.assertEqual(self.load('conversation.json')['messages'][0]['text'],'Readable')
        self.assert_no_rejected_body()

    def test_old_view_cache_is_rebuilt_even_when_changed_session_set_is_empty(self):
        self.unsupported_original()
        path=self.root/'research/views';path.mkdir(parents=True)
        (path/'chats.json').write_text(json.dumps({'sessions':[{'session_id':SID,'counts':{},
            'view_status':'RENDERED'}]}))
        report=refresh(self.root,self.archive,changed_sessions=set())
        self.assertEqual(report['view_gap_count'],1)
        self.assertEqual(report['sessions'][0]['view_schema_version'],2)
        self.assert_no_rejected_body()


if __name__ == "__main__":
    unittest.main()
