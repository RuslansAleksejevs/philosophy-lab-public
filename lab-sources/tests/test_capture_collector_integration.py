"""Synthetic collector/round integration; no actual essay or provider evidence."""
import copy
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from capture_codex import capture
from collector import Collector
import philosophy_round as rounds
from research_archive import Archive, ArchiveError


AUTHOR = 'synthetic-integration-author'
CRITIC = 'synthetic-integration-critic'
RUN = 'synthetic-integration-round'


def native(payload, kind='response_item'):
    return (json.dumps({'timestamp': '2026-09-08T02:00:00Z', 'type': kind,
                        'payload': payload}, ensure_ascii=False) + '\n').encode()


def message(text, role='assistant'):
    return native({'type': 'message', 'role': role, 'phase': 'final' if role == 'assistant' else None,
                   'content': [{'type': 'output_text' if role == 'assistant' else 'input_text', 'text': text}],
                   'internal_chat_message_metadata_passthrough': {'content_item_kinds': ['user.text']}})


class CollectorCaptureIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='synthetic-capture-collector-')
        self.root = Path(self.temp.name).resolve()
        self.write('LAB_PROFILE.json', {'lab': {'kind': 'PHILOSOPHY_PROGRAM'}})
        self.write('.lab/philosophy.json', {'schema_version': 1, 'kernel': 'philosophy.v1',
                                          'archive_format': 'research-archive.v1'})
        self.write('methods/simple-v1.json', {'id': 'synthetic-method', 'stages': rounds.STAGES})
        for name in ('AGENTS.md', 'AGENT_POLICY.md', 'USER_PREFERENCES.md', 'workflows/ROUND.md'):
            self.write(name, 'Synthetic instructions only\n')
        self.write('.codex/config.toml', '# synthetic configuration\n')
        self.sources = {}
        for sid, texts in ((AUTHOR, ['Question', 'Sources', 'Contribution', 'Decision']),
                           (CRITIC, ['Critique'])):
            source = self.root / (sid + '.jsonl')
            source.write_bytes(native({'id': sid, 'cwd': str(self.root)}, 'session_meta') +
                               b''.join(message('Synthetic ' + text) for text in texts))
            self.sources[sid] = source
        db = self.root / 'native.sqlite'
        connection = sqlite3.connect(db)
        connection.execute('CREATE TABLE threads (id TEXT PRIMARY KEY, rollout_path TEXT, cwd TEXT, name TEXT)')
        connection.execute('CREATE TABLE thread_spawn_edges (parent_thread_id TEXT, child_thread_id TEXT)')
        for sid, source in self.sources.items():
            connection.execute('INSERT INTO threads VALUES (?,?,?,?)', (sid, str(source), str(self.root), sid))
        connection.execute('INSERT INTO thread_spawn_edges VALUES (?,?)', (AUTHOR, CRITIC))
        connection.commit(); connection.close()
        self.write('collector/config.json', {'schema_version': 1, 'project_root': '.', 'state_db': str(db),
                                            'interval_seconds': 10, 'explicit_sessions': {}})
        self.archive = Archive(self.root / 'research/archive').init()

    def tearDown(self):
        self.temp.cleanup()

    def write(self, name, value):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(json.dumps(value).encode() if isinstance(value, dict) else value.encode())
        return name

    def collect(self):
        result = Collector(self.root).collect()
        self.assertEqual(result['status'], 'RUNNING')
        self.assertEqual(result['discovered_sessions'], 2)
        return result

    def start(self, run=RUN):
        return rounds.start(self.root, self.archive, run, AUTHOR, 'technical', 'methods/simple-v1.json', [])

    def capture(self, line=2, sid=AUTHOR, run=RUN, end=None, reviewed=()):
        return capture(self.archive.root, self.sources[sid], sid, self.root,
                       start_line=line, end_line=end or line, run_id=run,
                       reviewed_tool_lines=reviewed)

    def originals(self):
        return [event for event in self.archive.events() if event['kind'] == 'capture.raw_record']

    def test_collector_first_round_capture_reuses_bytes_and_adds_exact_idempotent_binding(self):
        self.collect()
        originals = copy.deepcopy(self.originals())
        first = self.start()
        before = self.archive.events()
        raw = next(e for e in originals if e['session_id'] == AUTHOR and e['payload']['source_line'] == 2)
        artifact = self.write('notes/question.md', 'Synthetic Question\n')
        with self.assertRaisesRegex(ArchiveError, 'exact run binding required'):
            rounds.record(self.root, self.archive, RUN, 'question', artifact, AUTHOR, [raw['id']])
        result = self.capture()
        self.assertEqual(result['raw_event_ids'], [raw['id']])
        self.assertEqual(result['status'], 'BOUNDED_COMPLETE')
        binding = next(e for e in self.archive.events() if e['id'] == result['run_binding_event_ids'][0])
        self.assertEqual(binding['parents'], [raw['id'], first['id']])
        self.assertEqual(binding['bindings'], first['bindings'])
        self.assertEqual(binding['payload']['original_run_id'], 'codex:' + AUTHOR)
        self.assertEqual(binding['payload']['selected_run_id'], RUN)
        self.assertEqual(self.originals(), originals)
        self.assertEqual(self.archive.events()[:len(before)], before)
        snapshot = self.archive.events()
        self.assertEqual(self.capture(), result)
        self.assertEqual(self.archive.events(), snapshot)
        stage = rounds.record(self.root, self.archive, RUN, 'question', artifact, AUTHOR, [raw['id']])
        self.assertIn(binding['id'], stage['parents'])
        self.assertEqual(rounds.validate_round_history(self.archive), [])

    def test_full_round_and_checkpoint_accept_bound_reused_originals_for_author_and_critic(self):
        self.collect(); self.start()
        coverages = {}
        for stage, sid, line in [('question', AUTHOR, 2), ('sources', AUTHOR, 3),
                                 ('contribution', AUTHOR, 4), ('critique', CRITIC, 2), ('decision', AUTHOR, 5)]:
            report = self.capture(line=line, sid=sid)
            coverages[sid] = report['coverage_event_id']
            artifact = self.write('notes/' + stage + '.md', 'Synthetic ' + stage + '\n')
            rounds.record(self.root, self.archive, RUN, stage, artifact, sid, report['raw_event_ids'],
                          'Synthetic retrieval; no actual source.' if stage == 'sources' else '')
        coverages[AUTHOR] = self.capture(line=2, end=5)['coverage_event_id']
        summary = self.write('notes/checkpoint.json', {
            'question': 'Synthetic question', 'outcome': 'COMPLETE_TECHNICAL', 'contribution': 'Synthetic integration',
            'criticism': 'Separate synthetic critic source', 'limitations': 'Not actual research',
            'next_step': 'No research action', 'method_change': 'No change', 'comparability': 'Synthetic fixture',
            'coverage_boundary': 'Selected synthetic original records'})
        checkpoint = rounds.checkpoint(self.root, self.archive, RUN, summary, list(coverages.values()))
        self.assertEqual(checkpoint['payload']['capture_status'], 'BOUNDED_COMPLETE')
        self.assertEqual(rounds.validate_round_history(self.archive), [])
        self.assertTrue(self.archive.validate()['ok'])
        self.assertEqual(len(self.originals()), 5)

    def test_repeated_selection_for_another_round_keeps_original_first_run(self):
        self.collect(); self.start()
        first = self.capture()
        self.start('synthetic-second-round')
        second = self.capture(run='synthetic-second-round')
        self.assertEqual(first['raw_event_ids'], second['raw_event_ids'])
        self.assertNotEqual(first['run_binding_event_ids'], second['run_binding_event_ids'])
        self.assertTrue(all(e['run_id'].startswith('codex:') for e in self.originals()))

    def test_original_rewrite_is_rejected_without_replacing_archived_record(self):
        self.collect(); self.start()
        original = self.archive.events()
        source = self.sources[AUTHOR]
        source.write_bytes(source.read_bytes().replace(b'Synthetic Question', b'Changed question'))
        with self.assertRaisesRegex(ArchiveError, 'original capture identity or bytes mismatch'):
            self.capture()
        self.assertEqual(self.archive.events(), original)

    def test_invalid_binding_cannot_launder_raw_record_into_stage(self):
        self.collect(); first = self.start()
        raw = next(e for e in self.originals() if e['session_id'] == AUTHOR)
        artifact = self.write('notes/question.md', 'Synthetic Question\n')
        sha = raw['payload']['raw_sha256']
        self.archive.append({'kind': 'capture.run_binding', 'actor': {'id': 'synthetic-test', 'role': 'tool'},
            'session_id': AUTHOR, 'run_id': RUN, 'operation_id': 'synthetic-invalid-binding',
            'attempt_id': 'synthetic-invalid-binding', 'parents': [raw['id'], first['id']],
            'inputs': [sha], 'bindings': first['bindings'],
            'payload': {'raw_event_id': raw['id'], 'raw_sha256': sha,
                        'source_line': raw['payload']['source_line'] + 1, 'source_session_id': AUTHOR,
                        'original_run_id': raw['run_id'], 'selected_run_id': RUN,
                        'round_start_event_id': first['id']}}, 'synthetic-invalid-binding')
        with self.assertRaisesRegex(ArchiveError, 'exact run binding required'):
            rounds.record(self.root, self.archive, RUN, 'question', artifact, AUTHOR, [raw['id']])

    def test_history_validator_requires_binding_as_stage_parent(self):
        self.collect(); first = self.start()
        report = self.capture()
        sha = self.archive.put(b'Synthetic question\n')
        event = rounds.envelope(first, 'round.stage', parents=[first['id']] + report['raw_event_ids'],
            payload={'stage': 'question', 'artifact_sha256': sha, 'source_note': '',
                     'artifact_name': 'question.md', 'contribution_origin': 'AI'})
        event['outputs'] = [sha]
        self.archive.append(event, 'synthetic-forged-unbound-stage')
        errors = rounds.validate_round_history(self.archive)
        self.assertTrue(any('invalid captured stage provenance' in error for error in errors))

    def test_concurrent_collector_original_is_reused_after_delivery_conflict(self):
        self.start()
        original_append = Archive.append
        injected = []

        def race(archive, request, delivery_key):
            if request['kind'] == 'capture.raw_record' and not injected:
                concurrent = copy.deepcopy(request)
                concurrent['id'] = 'collector-synthetic-concurrent-original'
                concurrent['run_id'] = 'codex:' + AUTHOR
                injected.append(original_append(archive, concurrent, delivery_key))
            return original_append(archive, request, delivery_key)

        with patch.object(Archive, 'append', race):
            report = self.capture()
        self.assertEqual(report['raw_event_ids'], [injected[0]['id']])
        self.assertEqual(len(self.originals()), 1)
        self.assertEqual(len(report['run_binding_event_ids']), 1)

    def test_reviewed_tool_pair_can_be_reused_in_second_run_without_link_conflict(self):
        source = self.sources[AUTHOR]
        source.write_bytes(native({'id': AUTHOR, 'cwd': str(self.root)}, 'session_meta') +
            native({'type': 'function_call', 'name': 'synthetic', 'call_id': 'synthetic-call', 'arguments': '1+1'}) +
            native({'type': 'function_call_output', 'call_id': 'synthetic-call', 'output': '2'}))
        first = self.capture(line=2, end=3, reviewed=(2, 3), run='synthetic-original-run')
        second = self.capture(line=2, end=3, reviewed=(2, 3), run='synthetic-reuse-run')
        self.assertEqual(first['raw_event_ids'], second['raw_event_ids'])
        self.assertEqual(first['tool_link_ids'], second['tool_link_ids'])
        self.assertEqual(len(second['run_binding_event_ids']), 2)
        self.assertEqual(second, self.capture(line=2, end=3, reviewed=(2, 3), run='synthetic-reuse-run'))


if __name__ == '__main__':
    unittest.main()
