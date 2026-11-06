"""Synthetic Claude-shaped records, not provider captures or live research."""
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from test_philosophy_bridge import BridgeFixture
import philosophy_bridge as bridge
import capture_claude as capture
from research_archive import ArchiveError


class ClaudeCaptureTests(BridgeFixture):
    def setUp(self):
        super().setUp()
        self.setup_job()
        self.session = 'synthetic-claude-session'
        bridge.claim(self.root, self.workspace, self.session, 'synthetic-attempt')
        self.source = self.root.parent / 'explicit-source.jsonl'

    def record(self, role, content, **extra):
        return {'type': role, 'cwd': str(self.workspace), 'sessionId': self.session,
                'timestamp': '2026-01-01T12:00:02Z' if role == 'assistant' else '2026-01-01T12:00:00Z',
                'message': {'role': role, 'content': content, **({'model': 'synthetic-model'} if role == 'assistant' else {})}, **extra}

    def source_records(self, records, tail=b''):
        raw = b''.join((json.dumps(r, ensure_ascii=False) + '\n').encode() for r in records) + tail
        self.source.write_bytes(raw)
        return raw

    def run_capture(self, **kwargs):
        return capture.capture(self.root, self.workspace, self.source, self.session, **kwargs)

    def test_exact_safe_fragments_survive_mixed_thinking_without_hidden_copy(self):
        self.source_records([self.record('user', 'Synthetic human request'), self.record('assistant', [
            {'type': 'thinking', 'thinking': 'SECRET_SYNTHETIC_REASONING', 'signature': 'secret'},
            {'type': 'text', 'text': 'Synthetic visible answer'}], effort='high')])
        result = self.run_capture(end_line=2)
        self.assertEqual(result['status'], 'BOUNDED_COMPLETE')
        self.assertEqual(result['captured_fragments'], 2)
        records = [e for e in self.archive.events() if e['kind'] == 'capture.raw_record']
        self.assertEqual(records[-1]['model']['value']['label'], 'synthetic-model')
        self.assertEqual(records[-1]['payload']['elapsed_since_latest_visible_user_seconds'], 2)
        self.assertEqual(self.archive.get(records[-1]['outputs'][0]), b'{"type": "text", "text": "Synthetic visible answer"}')
        for obj in (self.root / 'research/archive/objects').iterdir():
            self.assertNotIn(b'SECRET_SYNTHETIC_REASONING', obj.read_bytes())
        again = self.run_capture(end_line=2)
        self.assertEqual(result['coverage_event_id'], again['coverage_event_id'])

    def test_partial_live_tail_unknown_schema_and_tool_gaps(self):
        self.source_records([self.record('user', 'Synthetic request'), self.record('assistant', [
            {'type': 'tool_use', 'id': 'tool-1', 'name': 'Read', 'input': {'file_path': 'private'}}]),
            {'type': 'future-record', 'sessionId': self.session}], tail=b'{"partial":')
        result = self.run_capture()
        self.assertEqual(result['status'], 'INCOMPLETE')
        self.assertIn('partial_tail_withheld', result['gaps'])
        self.assertIn('tool_bodies_require_separate_explicit_safe_review', result['gaps'])
        self.assertEqual(result['captured_fragments'], 1)

    def test_wrong_session_cwd_unclaimed_source_and_symlink_fail(self):
        self.source_records([self.record('user', 'Synthetic request', sessionId='wrong')])
        with self.assertRaisesRegex(ArchiveError, 'session'): self.run_capture(end_line=1)
        self.source_records([self.record('user', 'Synthetic request', cwd=str(self.root))])
        with self.assertRaisesRegex(ArchiveError, 'cwd'): self.run_capture(end_line=1)
        self.source_records([self.record('user', 'Synthetic request')])
        with self.assertRaisesRegex(ArchiveError, 'claim'):
            capture.capture(self.root, self.workspace, self.source, 'unclaimed', end_line=1)
        link = self.source.parent / 'alias.jsonl'; link.symlink_to(self.source)
        with self.assertRaises(ArchiveError):
            capture.capture(self.root, self.workspace, link, self.session, end_line=1)

    def test_changed_original_cannot_replace_evidence(self):
        self.source_records([self.record('user', 'Original request')])
        first = self.run_capture(end_line=1)
        count = len(self.archive.events())
        self.source_records([self.record('user', 'Changed request')])
        with self.assertRaisesRegex(ArchiveError, 'fragment changed'): self.run_capture(end_line=1)
        self.assertEqual(count, len(self.archive.events()))
        self.assertTrue(first['raw_event_ids'])

    def test_native_metadata_drift_with_identical_text_is_not_silently_reused(self):
        record = self.record('assistant', [{'type': 'text', 'text': 'Same text'}])
        self.source_records([record])
        self.run_capture(end_line=1)
        record['message']['model'] = 'changed-model'
        self.source_records([record])
        with self.assertRaisesRegex(ArchiveError, 'fragment changed'): self.run_capture(end_line=1)

    def test_system_and_injected_context_never_captured(self):
        self.source_records([self.record('user', 'Synthetic request'),
            {'type': 'system', 'sessionId': self.session, 'content': 'SECRET_SYSTEM'},
            self.record('user', 'SECRET_CONTEXT', isMeta=True),
            self.record('assistant', [{'type': 'text', 'text': 'Answer'}], unexpected='SECRET_EXTRA')])
        result = self.run_capture(end_line=4)
        self.assertEqual(result['captured_fragments'], 1)
        self.assertEqual(result['status'], 'INCOMPLETE')
        for obj in (self.root / 'research/archive/objects').iterdir():
            self.assertNotIn(b'SECRET_', obj.read_bytes())

    def test_collection_reports_capture_coverage_without_claiming_authorship(self):
        self.source_records([self.record('user', 'Synthetic request'), self.record('assistant', [{'type': 'text', 'text': 'Synthetic answer'}])])
        report = self.run_capture(end_line=2)
        self.output('report.md', 'Synthetic report')
        result = bridge.collect(self.root, self.workspace, 'complete')
        self.assertEqual(result['source_coverage'], 'BOUNDED_COMPLETE')
        saved = next(e for e in self.archive.events() if e['id'] == result['event_id'])
        self.assertIn(report['coverage_event_id'], saved['parents'])
        self.assertFalse(saved['payload']['philosophical_status_promoted'])

    def test_injected_turn_companions_are_excluded_without_copying_bodies(self):
        self.source_records([self.record('user', 'Visible neutral request'),
            self.record('user', 'SECRET_COMPANION_STRING', isMeta=True, turnCompanion=True),
            self.record('user', [{'type': 'text', 'text': 'SECRET_COMPANION_BLOCK'}],
                        isMeta=True, turnCompanion=True),
            self.record('assistant', [{'type': 'text', 'text': 'Visible answer'}])])
        result = self.run_capture(end_line=4)
        self.assertEqual(result['status'], 'BOUNDED_COMPLETE')
        self.assertEqual(result['captured_fragments'], 2)
        self.assertIn({'reason': 'excluded_injected_turn_companion', 'count': 2}, result['exclusions'])
        for obj in (self.root / 'research/archive/objects').iterdir():
            self.assertNotIn(b'SECRET_COMPANION', obj.read_bytes())

    def test_turn_companion_exclusion_does_not_accept_unreviewed_shapes(self):
        cases = [
            self.record('user', 'SECRET_VARIANT', turnCompanion=True),
            self.record('user', 'SECRET_VARIANT', isMeta=True, turnCompanion='true'),
            self.record('user', 'SECRET_VARIANT', isMeta=1, turnCompanion=True),
            self.record('user', 'SECRET_VARIANT', isMeta=True, turnCompanion=False),
            self.record('user', 'SECRET_VARIANT', isMeta=True, turnCompanion=True, futureField=True),
            self.record('assistant', [{'type': 'text', 'text': 'SECRET_VARIANT'}],
                        isMeta=True, turnCompanion=True)]
        for item in cases:
            with self.subTest(keys=list(item), role=item['type']):
                self.source_records([item])
                result = self.run_capture(end_line=1)
                self.assertEqual(result['status'], 'INCOMPLETE')
                self.assertEqual(result['captured_fragments'], 0)
        for obj in (self.root / 'research/archive/objects').iterdir():
            self.assertNotIn(b'SECRET_VARIANT', obj.read_bytes())

    def test_reviewed_tool_pair_keeps_safe_originals_and_tool_result_is_not_human(self):
        self.source_records([
            self.record('user', 'Synthetic neutral launch'),
            self.record('assistant', [{'type': 'tool_use', 'id': 'call-1', 'name': 'Write',
                                      'input': {'file_path': 'output/draft-001.md', 'content': 'Synthetic draft'}}]),
            self.record('user', [{'type': 'tool_result', 'tool_use_id': 'call-1', 'content': 'Saved synthetic file'}])])
        first = self.run_capture(end_line=3)
        self.assertEqual(first['status'], 'INCOMPLETE')
        result = self.run_capture(end_line=3, reviewed_tool_lines=[2, 3])
        self.assertEqual(result['status'], 'BOUNDED_COMPLETE')
        events = [e for e in self.archive.events() if e['kind'] == 'capture.raw_record']
        self.assertEqual(events[0]['payload']['contribution_origin'], 'UNKNOWN')
        self.assertEqual(events[-1]['actor']['role'], 'tool')
        self.assertEqual(events[-1]['payload']['contribution_origin'], 'TOOL_OUTPUT')
        self.assertEqual(events[-1]['payload']['native_channel_role'], 'user')

    def test_review_does_not_override_hidden_markers_or_unexpected_fields(self):
        self.source_records([
            self.record('assistant', [{'type': 'tool_use', 'id': 'call-1', 'name': 'Read',
                                      'input': {'file_path': '.claude/projects/secret.jsonl'}}]),
            self.record('user', [{'type': 'tool_result', 'tool_use_id': 'call-1', 'content': 'Safe looking result'}]),
            self.record('assistant', [{'type': 'tool_use', 'id': 'call-2', 'name': 'Write',
                                      'input': {}, 'thinking': 'SECRET_REJECTED'}])])
        result = self.run_capture(end_line=3, reviewed_tool_lines=[1, 2, 3])
        self.assertEqual(result['captured_fragments'], 0)
        self.assertEqual(result['status'], 'INCOMPLETE')
        for obj in (self.root / 'research/archive/objects').iterdir():
            self.assertNotIn(b'SECRET_REJECTED', obj.read_bytes())

    def test_new_attempt_does_not_reuse_stale_coverage_or_collection_attribution(self):
        self.source_records([self.record('user', 'Synthetic request'), self.record('assistant', [{'type': 'text', 'text': 'Synthetic answer'}])])
        coverage_one = self.run_capture(end_line=2)
        self.output('report.md', 'Unchanged result bytes')
        first = bridge.collect(self.root, self.workspace, 'complete')
        self.assertEqual(first['source_coverage'], 'BOUNDED_COMPLETE')
        bridge.claim(self.root, self.workspace, self.session, 'attempt-two', resume=True)
        second = bridge.collect(self.root, self.workspace, 'complete')
        self.assertEqual(second['source_coverage'], 'NOT_CAPTURED')
        self.assertEqual(first['content_set_sha256'], second['content_set_sha256'])
        self.assertNotEqual(first['collection_id'], second['collection_id'])
        coverage_two = self.run_capture(end_line=2)
        self.assertNotEqual(coverage_one['coverage_event_id'], coverage_two['coverage_event_id'])
        third = bridge.collect(self.root, self.workspace, 'complete')
        self.assertEqual(third['source_coverage'], 'BOUNDED_COMPLETE')
        saved = next(e for e in self.archive.events() if e['id'] == third['event_id'])
        self.assertEqual(saved['attempt_id'], 'attempt-two')
        self.assertIn(coverage_two['coverage_event_id'], saved['parents'])
        self.assertNotIn(coverage_one['coverage_event_id'], saved['parents'])
        self.assertEqual(bridge.collect(self.root, self.workspace, 'complete')['event_id'], third['event_id'])

    def test_reviewed_direct_caller_pair_retains_exact_fragment_and_excludes_thinking(self):
        call = {'type': 'tool_use', 'id': 'direct-1', 'name': 'Write',
                'input': {'file_path': 'output/report.md', 'content': 'Synthetic report'},
                'caller': {'type': 'direct'}}
        self.source_records([
            self.record('assistant', [{'type': 'thinking', 'thinking': 'SECRET_DIRECT_REASONING'}, call]),
            self.record('user', [{'type': 'tool_result', 'tool_use_id': 'direct-1', 'content': 'Saved'}])])
        before = self.run_capture(end_line=2)
        self.assertEqual(before['status'], 'INCOMPLETE')
        result = self.run_capture(end_line=2, reviewed_tool_lines=[1, 2])
        self.assertEqual(result['status'], 'BOUNDED_COMPLETE')
        self.assertEqual(result['captured_fragments'], 2)
        known = {e['id']: e for e in self.archive.events()}
        native = self.archive.get(known[result['raw_event_ids'][0]]['outputs'][0])
        self.assertEqual(native, json.dumps(call, ensure_ascii=False).encode())
        self.assertEqual(known[before['coverage_event_id']]['payload']['status'], 'INCOMPLETE')
        for obj in (self.root / 'research/archive/objects').iterdir():
            self.assertNotIn(b'SECRET_DIRECT_REASONING', obj.read_bytes())

    def test_unknown_hidden_or_malformed_caller_blocks_call_and_result_even_after_review(self):
        for caller in (None, 'direct', True, {}, {'type': 'code_execution_20260120', 'tool_id': 'server-1'},
                       {'type': 'direct', 'signature': 'SECRET_CALLER'},
                       {'type': 'direct', 'extra': 'SECRET_CALLER'}, {'type': ['direct']}):
            with self.subTest(caller=caller):
                self.source_records([
                    self.record('assistant', [{'type': 'tool_use', 'id': 'bad-1', 'name': 'Read',
                                              'input': {'file_path': 'input/prompt.md'}, 'caller': caller}]),
                    self.record('user', [{'type': 'tool_result', 'tool_use_id': 'bad-1',
                                         'content': 'SECRET_PAIRED_RESULT'}])])
                result = self.run_capture(end_line=2, reviewed_tool_lines=[1, 2])
                self.assertEqual(result['status'], 'INCOMPLETE')
                self.assertEqual(result['captured_fragments'], 0)
                self.assertIn('reviewed_tool_bodies_blocked_by_safety_guard', result['gaps'])
        for obj in (self.root / 'research/archive/objects').iterdir():
            self.assertNotIn(b'SECRET_CALLER', obj.read_bytes())
            self.assertNotIn(b'SECRET_PAIRED_RESULT', obj.read_bytes())

    def test_internal_file_history_delta_is_excluded_without_retaining_its_body(self):
        records = [self.record('user', 'Synthetic neutral launch'),
                   {'type': 'file-history-delta', 'messageId': 'synthetic',
                    'backup': {'backupFileName': 'SECRET_INTERNAL_DELTA'},
                    'trackingPath': 'SECRET_INTERNAL_PATH'}]
        self.source_records(records)
        result = self.run_capture(end_line=2)
        self.assertEqual(result['status'], 'BOUNDED_COMPLETE')
        self.assertEqual(result['captured_fragments'], 1)
        self.assertIn({'reason': 'excluded_internal_file-history-delta', 'count': 1}, result['exclusions'])
        records.append({'type': 'file-history-delta-future', 'body': 'SECRET_UNKNOWN_DELTA'})
        self.source_records(records)
        self.assertEqual(self.run_capture(end_line=3)['status'], 'INCOMPLETE')
        for obj in (self.root / 'research/archive/objects').iterdir():
            self.assertNotIn(b'SECRET_INTERNAL_', obj.read_bytes())
            self.assertNotIn(b'SECRET_UNKNOWN_DELTA', obj.read_bytes())


if __name__ == '__main__': unittest.main()

class PublicPdfGuardTests(unittest.TestCase):
    def test_exact_public_pdf_exemption_keeps_other_runtime_and_secret_guards(self):
        p='/tmp/.claude/projects/bound/session/tool-results/webfetch-123-abc.pdf'
        b={'type':'tool_use','id':'read','name':'Read','input':{'file_path':p}}
        self.assertFalse(capture.safe_reviewed_tool(b))
        self.assertTrue(capture.safe_reviewed_tool(b,[p]))
        for bad in [p+'/other', p.replace('session/','unrelated/'), '/tmp/.codex/sessions/private.jsonl']:
            changed={**b,'input':{'file_path':bad}}
            self.assertFalse(capture.safe_reviewed_tool(changed,[p]))
        self.assertFalse(capture.safe_reviewed_tool({**b,'input':{'file_path':p,'text':'<system-reminder>secret'}},[p]))

    def test_pdf_location_hash_and_symlink_are_checked(self):
        import tempfile
        with tempfile.TemporaryDirectory() as temp:
            temp=str(Path(temp).resolve())
            source=Path(temp)/'session.jsonl'
            p=Path(temp)/'session/tool-results/webfetch-123-abc.pdf'
            p.parent.mkdir(parents=True);p.write_bytes(b'%PDF-synthetic fixture')
            hashes={str(p):capture.sha(p.read_bytes())}
            self.assertEqual(capture.validate_public_pdfs(source,'session',hashes),(str(p),))
            with self.assertRaises(ArchiveError):capture.validate_public_pdfs(source,'other',hashes)
            with self.assertRaises(ArchiveError):capture.validate_public_pdfs(source,'session',{str(p):'0'*64})
            p.unlink();p.symlink_to(source)
            with self.assertRaises(ArchiveError):capture.validate_public_pdfs(source,'session',hashes)

class DenialCaptureTests(ClaudeCaptureTests):
    def test_known_denial_retains_visible_failure_and_rejects_unknown_values(self):
        call=self.record('assistant',[{'type':'tool_use','id':'x','name':'Chapter','input':{}}])
        result=self.record('user',[{'type':'tool_result','tool_use_id':'x','is_error':True,'content':'Permission denied.'}],toolDenialKind='permission-rule')
        self.source_records([call,result])
        captured=self.run_capture(end_line=2,reviewed_tool_lines=[1,2])
        self.assertEqual(captured['status'],'BOUNDED_COMPLETE')
        self.assertEqual(captured['captured_fragments'],2)
        result['toolDenialKind']='future-secret-type'
        self.source_records([call,result])
        captured=self.run_capture(end_line=2,reviewed_tool_lines=[1,2])
        self.assertEqual(captured['status'],'INCOMPLETE')
