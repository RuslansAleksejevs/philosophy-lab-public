"""Synthetic regressions for inspected October 2026 visible-message extensions."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from capture_codex import capture, classify, valid_top_metadata
from collector_source import project_record, UNKNOWN_MODEL
from research_archive import Archive

SESSION = 'synthetic-current-schema-0001'
SENTINEL = 'SYNTHETIC_HIDDEN_SENTINEL'


def record(role='user'):
    payload = {'type': 'message', 'id': 'message-0123456789', 'role': role,
               'content': [{'type': 'input_text' if role == 'user' else 'output_text',
                            'text': 'Visible authorization' if role == 'user' else 'Visible answer'}],
               'internal_chat_message_metadata_passthrough': {
                   'turn_id': 'turn-0123456789', 'create_time': 1793450000,
                   'content_item_kinds': ['user.text'] if role == 'user' else ['unknown']}}
    if role == 'user':
        payload['internal_chat_message_metadata_passthrough']['content_item_metadata'] = [
            {'provenance': {'type': 'user'}}]
    else:
        payload.update(status='completed', phase='final_answer')
        payload['content'][0].update(annotations=[], logprobs=[])
    return {'timestamp': '2026-10-31T10:00:00Z', 'ordinal': 1,
            'type': 'response_item', 'payload': payload,
            'metadata': {'client_authored': False, 'user_input_order': 1,
                         'mcp_attribution': {'status': 'complete', 'sources': [{
                             'connector_id': 'connector_' + 'a' * 32,
                             'server_name': 'codex_apps', 'tool_name': 'github.get_repo',
                             'first_turn_id': 'turn-0123456789'}]}}}


class CurrentVisibleSchemaTests(unittest.TestCase):
    def test_current_messages_project_only_visible_text_and_preserve_exact_raw(self):
        records = [record(), record('assistant')]
        for i, item in enumerate(records, 2):
            projected = project_record(item, i, SESSION, None, UNKNOWN_MODEL)
            self.assertEqual(projected['kind'], 'text')
            self.assertTrue(projected['payload']['retain_original'])
            self.assertEqual(projected['payload']['text'], item['payload']['content'][0]['text'])
            self.assertNotIn('connector_id', json.dumps(projected))
            self.assertNotIn('content_item_metadata', json.dumps(projected))
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            (root / '.lab').mkdir()
            (root / 'LAB_PROFILE.json').write_text(json.dumps({'lab': {'kind': 'PHILOSOPHY_PROGRAM'}}))
            (root / '.lab/philosophy.json').write_text(json.dumps({'schema_version': 1,
                'kernel': 'philosophy.v1', 'archive_format': 'research-archive.v1'}))
            def encode(x): return (json.dumps(x, ensure_ascii=False) + '\n').encode()
            head = encode({'timestamp': '2026-10-31T10:00:00Z', 'type': 'session_meta',
                           'payload': {'id': SESSION, 'cwd': str(root)}})
            source = root / 'current.jsonl'; raws = [encode(x) for x in records]
            source.write_bytes(head + b''.join(raws))
            archive_path = root / 'research/archive'
            result = capture(archive_path, source, SESSION, root, start_line=2, end_line=3)
            self.assertEqual(result['status'], 'BOUNDED_COMPLETE')
            self.assertEqual(result['captured_records'], 2)
            archive = Archive(archive_path)
            originals = [archive.get(e['outputs'][0]) for e in archive.events()
                         if e['kind'] == 'capture.raw_record']
            self.assertEqual(originals, raws)
            self.assertEqual(result, capture(archive_path, source, SESSION, root, start_line=2, end_line=3))
            self.assertTrue(archive.validate()['ok'])

    def test_context_provenance_never_becomes_human_text(self):
        for kinds in [['agents_md.instructions'], ['environments.environment_context'],
                      ['additional_content.codex_apps_open_page'],
                      ['user.text', 'agents_md.instructions']]:
            item = record(); p = item['payload']; p['content'][0]['text'] = SENTINEL
            p['internal_chat_message_metadata_passthrough'].update(
                content_item_kinds=kinds,
                content_item_metadata=[{'provenance': {'type': 'harness', 'hook': False}}] * len(kinds))
            self.assertEqual(classify(item, 2, set(), set()), 'excluded:non_user_text_context')
            projected = project_record(item, 2, SESSION, None, UNKNOWN_MODEL)
            # A mixed user/context item stays an explicit unsupported gap;
            # context-only records are excluded. Neither may expose a body.
            self.assertEqual(projected['kind'], 'gap' if 'user.text' in kinds else 'excluded')
            self.assertNotIn(SENTINEL, json.dumps(projected))

    def test_unseen_or_malformed_user_provenance_fails_closed(self):
        bad = [None, [], [{'provenance': {'type': 'harness'}}],
               [{'provenance': {'type': 'user', 'hook': False}}],
               [{'provenance': {'type': 'user'}, 'extra': SENTINEL}],
               [{'provenance': {'type': 'user', 'extra': SENTINEL}}],
               [{'provenance': {'type': 'user'}}] * 2]
        for value in bad:
            item = record(); item['payload']['internal_chat_message_metadata_passthrough']['content_item_metadata'] = value
            self.assertEqual(classify(item, 2, set(), set()), 'unknown_metadata_value')
        item = record('assistant')
        item['payload']['internal_chat_message_metadata_passthrough']['content_item_metadata'] = [{'provenance': {'type': 'user'}}]
        self.assertEqual(classify(item, 2, set(), set()), 'unknown_metadata_value')

    def test_status_and_empty_arrays_are_assistant_completed_only(self):
        for status in ['in_progress', 'failed', None, 1]:
            item = record('assistant'); item['payload']['status'] = status
            self.assertIsNotNone(classify(item, 2, set(), set()))
        item = record(); item['payload']['status'] = 'completed'
        self.assertEqual(classify(item, 2, set(), set()), 'unknown_message_status')
        for key in ['annotations', 'logprobs']:
            for value in [None, {}, [SENTINEL], [{'text': SENTINEL}]]:
                item = record('assistant'); item['payload']['content'][0][key] = value
                self.assertEqual(classify(item, 2, set(), set()), 'unknown_assistant_content')
            item = record(); item['payload']['content'][0][key] = []
            self.assertEqual(classify(item, 2, set(), set()), 'unknown_user_content')
        item = record('assistant'); del item['payload']['status']
        self.assertEqual(classify(item, 2, set(), set()), 'unknown_assistant_content')

    def test_internal_roles_analysis_unknown_fields_still_withheld(self):
        for role in ['system', 'developer']:
            item = record('assistant'); item['payload']['role'] = role
            self.assertTrue(classify(item, 2, set(), set()).startswith('excluded:'))
        item = record('assistant'); item['payload']['phase'] = 'analysis'
        self.assertEqual(classify(item, 2, set(), set()), 'excluded:non_visible_assistant_phase')
        for target in ['payload', 'block', 'metadata']:
            item = record('assistant')
            selected = {'payload': item['payload'], 'block': item['payload']['content'][0],
                        'metadata': item['metadata']}[target]
            selected['unreviewed'] = SENTINEL
            self.assertIsNotNone(classify(item, 2, set(), set()))
            self.assertNotIn(SENTINEL, json.dumps(project_record(item, 2, SESSION, None, UNKNOWN_MODEL)))

    def test_connector_attribution_is_bounded_not_arbitrary_metadata(self):
        base = record()['metadata']
        self.assertTrue(valid_top_metadata(base))
        for patch in [{'connector_id': SENTINEL}, {'connector_id': None},
                      {'server_name': 'other_server'}, {'plugin_id': 'also-present'},
                      {'tool_name': 'github.'}, {'tool_name': 'github.get.repo'},
                      {'tool_name': 'github.get repo'}, {'tool_name': 'github.' + 'x' * 200},
                      {'unreviewed': SENTINEL}]:
            bad = copy.deepcopy(base); bad['mcp_attribution']['sources'][0].update(patch)
            self.assertFalse(valid_top_metadata(bad), patch)

    def test_new_message_extensions_do_not_expand_reviewed_tool_payloads(self):
        item = record(); item['payload'] = {'type': 'function_call_output', 'call_id': 'call-1',
            'output': [{'type': 'output_text', 'text': SENTINEL, 'annotations': [], 'logprobs': []}]}
        self.assertEqual(classify(item, 2, {2}, set()), 'unknown_tool_output_shape')
        item['payload']['output'] = 'visible tool response'
        item['payload']['internal_chat_message_metadata_passthrough'] = {
            'content_item_kinds': ['user.text'], 'content_item_metadata': [{'provenance': {'type': 'user'}}]}
        self.assertEqual(classify(item, 2, {2}, set()), 'unknown_metadata_fields')


if __name__ == '__main__':
    unittest.main()
