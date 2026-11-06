"""Synthetic temporary jobs only. No model/provider interaction or real lab writes."""
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import philosophy_bridge as bridge
import philosophy_round as rounds
from research_archive import Archive, ArchiveError


class BridgeFixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='synthetic-philosophy-bridge-')
        self.root = Path(self.tmp.name).resolve() / 'lab'
        self.root.mkdir()
        self.write('LAB_PROFILE.json', {'lab': {'kind': 'PHILOSOPHY_PROGRAM'}})
        self.write('.lab/philosophy.json', {'synthetic': True})
        self.write('.codex/config.toml', '# synthetic\n')
        self.write('methods/simple-v1.json', {'id': 'synthetic', 'stages': rounds.STAGES})
        for name in ('AGENTS.md', 'AGENT_POLICY.md', 'USER_PREFERENCES.md', 'workflows/ROUND.md'):
            self.write(name, 'Synthetic instructions\n')
        shutil.copytree(ROOT / 'templates/philosophy_claude', self.root / 'templates/philosophy_claude')
        self.archive = Archive(self.root / 'research/archive').init()
        rounds.start(self.root, self.archive, 'synthetic-run', 'synthetic-root', 'technical', 'methods/simple-v1.json', [])
        self.workspace = self.root.parent / 'external' / 'synthetic-job'
        self.request = {'job_id': 'synthetic-job', 'essay_id': 'synthetic-essay', 'run_id': 'synthetic-run',
                        'stage': 'technical', 'prompt': 'Synthetic smoke fixture; no philosophical contribution.'}

    def tearDown(self): self.tmp.cleanup()

    def write(self, name, data):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(data, dict): data = json.dumps(data)
        if isinstance(data, str): data = data.encode()
        path.write_bytes(data)
        return path

    def setup_job(self):
        result = bridge.prepare(self.root, self.request)
        bridge.activate(self.root, self.request['job_id'], self.workspace)
        return result

    def output(self, name, content):
        path = self.workspace / 'output' / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        return path


class PhilosophyBridgeTests(BridgeFixture):
    def test_empty_partial_and_no_report_artifacts_are_preserved(self):
        self.setup_job()
        empty = bridge.collect(self.root, self.workspace)
        self.assertEqual(empty['status'], 'INCOMPLETE')
        self.output('draft-001.md', 'Synthetic interrupted draft')
        result = bridge.collect(self.root, self.workspace)
        self.assertNotEqual(empty['content_set_sha256'], result['content_set_sha256'])
        self.assertEqual((Path(result['path']) / 'artifacts/draft-001.md').read_text(), 'Synthetic interrupted draft')
        with self.assertRaises(ArchiveError): bridge.collect(self.root, self.workspace, 'complete')

    def test_completed_return_repeat_and_invalid_metadata(self):
        self.setup_job()
        self.output('report.md', 'Synthetic final report')
        self.output('metadata.json', '{broken')
        result = bridge.collect(self.root, self.workspace, 'complete')
        again = bridge.collect(self.root, self.workspace, 'complete')
        self.assertEqual(result['event_id'], again['event_id'])
        saved = next(e for e in self.archive.events() if e['id'] == result['event_id'])
        self.assertEqual(saved['payload']['metadata']['status'], 'INVALID_PRESERVED_INERT')
        self.assertEqual(saved['payload']['source_coverage'], 'NOT_CAPTURED')
        self.assertFalse(saved['payload']['code_executed'])
        self.assertTrue(self.archive.validate()['ok'])

    def test_input_drift_wrong_job_and_cross_essay_lineage_fail(self):
        self.setup_job()
        path = self.workspace / 'input/prompt.md'; path.chmod(0o600); path.write_text('Drift')
        with self.assertRaisesRegex(ArchiveError, 'inputs changed'): bridge.collect(self.root, self.workspace)
        other = {**self.request, 'job_id': 'other', 'essay_id': 'other-essay', 'parent_job_id': 'synthetic-job'}
        with self.assertRaisesRegex(ArchiveError, 'cross-essay'): bridge.prepare(self.root, other)

    def test_metadata_wrong_job_rejected_and_manuscript_never_overwritten(self):
        self.setup_job()
        path = self.output('draft-001.md', 'Version one')
        bridge.collect(self.root, self.workspace)
        path.write_text('Changed in place')
        with self.assertRaisesRegex(ArchiveError, 'overwritten'): bridge.collect(self.root, self.workspace)
        path.write_text('Version one')
        self.output('draft-002.md', 'Version two')
        second = bridge.collect(self.root, self.workspace)
        self.output('metadata.json', '{"job_id":"wrong"}')
        with self.assertRaisesRegex(ArchiveError, 'different job'): bridge.collect(self.root, self.workspace)
        self.assertTrue((Path(second['path']) / 'artifacts/draft-001.md').exists())

    def test_symlink_hardlink_and_unsafe_request_paths(self):
        self.setup_job()
        outside = self.write('outside.txt', 'Never followed')
        (self.workspace / 'output/link.md').symlink_to(outside)
        with self.assertRaises(ArchiveError): bridge.collect(self.root, self.workspace)
        (self.workspace / 'output/link.md').unlink()
        import os
        os.link(outside, self.workspace / 'output/link.md')
        with self.assertRaises(ArchiveError): bridge.collect(self.root, self.workspace)
        for label in ('../escape', '/absolute', '.hidden', 'a/../escape', 'a\\b'):
            with self.subTest(label=label), self.assertRaises(ArchiveError):
                bridge.prepare(self.root, {**self.request, 'job_id': 'unsafe', 'selected_inputs': [{'source': 'outside.txt', 'label': label}]})

    def test_job_id_and_leaf_are_immutable(self):
        first = self.setup_job()
        self.assertEqual(bridge.prepare(self.root, self.request)['event_id'], first['event_id'])
        with self.assertRaisesRegex(ArchiveError, 'immutable'):
            bridge.prepare(self.root, {**self.request, 'prompt': 'Changed prompt'})
        bridge.prepare(self.root, {**self.request, 'job_id': 'second-job'})
        with self.assertRaisesRegex(ArchiveError, 'different job'):
            bridge.activate(self.root, 'second-job', self.workspace)

    def test_claim_resume_is_idempotent_and_context_not_reused(self):
        self.setup_job()
        first = bridge.claim(self.root, self.workspace, 'synthetic-session', 'attempt-1')
        self.assertEqual(bridge.claim(self.root, self.workspace, 'synthetic-session', 'attempt-1'), first)
        with self.assertRaises(ArchiveError): bridge.claim(self.root, self.workspace, 'synthetic-session', 'attempt-2')
        resumed = bridge.claim(self.root, self.workspace, 'synthetic-session', 'attempt-2', True)
        self.assertEqual(bridge.claim(self.root, self.workspace, 'synthetic-session', 'attempt-2', True), resumed)
        bridge.prepare(self.root, {**self.request, 'job_id': 'critic-job', 'stage': 'critic', 'parent_job_id': 'synthetic-job'})
        second = self.workspace.parent / 'critic-job'
        bridge.activate(self.root, 'critic-job', second)
        with self.assertRaisesRegex(ArchiveError, 'reuse across jobs'):
            bridge.claim(self.root, second, 'synthetic-session', 'critic-attempt')

    def test_after_commit_publication_failure_recovers_derived_copy(self):
        self.setup_job()
        self.output('report.md', 'Synthetic report')
        with mock.patch.object(bridge, 'publish_directory', side_effect=OSError('synthetic interruption')):
            with self.assertRaises(OSError): bridge.collect(self.root, self.workspace, 'complete')
        result = bridge.collect(self.root, self.workspace, 'complete')
        self.assertEqual(result['status'], 'ALREADY_COLLECTED')
        copies = list((self.root / 'research/bridge/returns/synthetic-job').glob('*/collection.json'))
        self.assertEqual(len(copies), 1)

    def test_runtime_decoration_ignored_but_collisions_blocked(self):
        self.setup_job()
        self.output('report.md', 'Synthetic report')
        self.output('.DS_Store', 'Synthetic Finder decoration')
        self.output('.claude/runtime', 'Must not copy')
        self.output('.cc-writes/runtime', 'Desktop bookkeeping must not copy')
        self.output('source.html', '<p>Inert synthetic source</p>')
        self.output('paper.body', 'Inert source bytes with provider filename')
        result = bridge.collect(self.root, self.workspace, 'complete')
        self.assertFalse((Path(result['path']) / 'artifacts/.claude').exists())
        self.assertFalse((Path(result['path']) / 'artifacts/.cc-writes').exists())
        self.assertTrue((Path(result['path']) / 'artifacts/source.html').is_file())
        # macOS may use a case-insensitive volume, so emulate the directory
        # inventory a case-sensitive source can legitimately present.
        original = bridge.os.listdir
        def inventory(path):
            if Path(path) == self.workspace / 'output': return ['REPORT.md', 'report.md']
            return original(path)
        with mock.patch.object(bridge.os, 'listdir', side_effect=inventory):
            with self.assertRaisesRegex(ArchiveError, 'collision'): bridge.collect(self.root, self.workspace)

    def test_changed_file_during_multi_file_snapshot_fails(self):
        self.setup_job()
        first = self.output('a.md', 'A')
        self.output('b.md', 'B')
        original = bridge.read_file
        def read(path, maximum=bridge.MAX_FILE):
            data = original(path, maximum)
            if Path(path) == self.workspace / 'output/b.md': first.write_text('Mutated after its read')
            return data
        with mock.patch.object(bridge, 'read_file', side_effect=read):
            with self.assertRaisesRegex(ArchiveError, 'changed during tree'): bridge.collect(self.root, self.workspace)

    def test_web_off_is_explicit_and_input_topology_checked_before_archive_write(self):
        self.request['public_web'] = False
        self.setup_job()
        settings = json.loads((self.workspace / '.claude/settings.json').read_text())
        self.assertIn('WebFetch', settings['permissions']['deny'])
        self.assertNotIn('WebFetch', settings['permissions']['allow'])
        self.write('one.txt', 'Selected synthetic input')
        count = len(self.archive.events())
        with self.assertRaisesRegex(ArchiveError, 'topology collision'):
            bridge.prepare(self.root, {**self.request, 'job_id': 'bad-topology', 'selected_inputs': [
                {'source': 'one.txt', 'label': 'a'}, {'source': 'one.txt', 'label': 'a/b'}]})
        self.assertEqual(len(self.archive.events()), count)

    def test_explicit_same_lock_batch_uses_one_audit(self):
        original = self.archive._audit
        with mock.patch.object(self.archive, '_audit', wraps=original) as audit:
            with self.archive.writer() as writer:
                bridge.prepare(self.root, self.request, archive_writer=writer)
                bridge.activate(self.root, self.request['job_id'], self.workspace, archive_writer=writer)
                bridge.claim(self.root, self.workspace, 'synthetic-session', 'attempt-1', archive_writer=writer)
                self.output('report.md', 'Synthetic report')
                bridge.collect(self.root, self.workspace, 'complete', archive_writer=writer)
            self.assertEqual(audit.call_count, 1)

    def test_one_job_cannot_activate_or_replay_claim_in_second_leaf(self):
        self.setup_job()
        claim = bridge.claim(self.root, self.workspace, 'session-a', 'attempt-a')
        second = self.workspace.parent / 'second-leaf'
        with self.assertRaisesRegex(ArchiveError, 'another workspace'):
            bridge.activate(self.root, self.request['job_id'], second)
        self.assertFalse(second.exists())
        shutil.copytree(self.workspace, second)
        with self.assertRaisesRegex(ArchiveError, 'activated workspace binding'):
            bridge.claim(self.root, second, 'session-a', 'attempt-a')
        with self.assertRaisesRegex(ArchiveError, 'activated workspace binding'):
            bridge.collect(self.root, second)
        self.output('report.md', 'Correct leaf output')
        result = bridge.collect(self.root, self.workspace, 'complete')
        saved = next(e for e in self.archive.events() if e['id'] == result['event_id'])
        self.assertEqual(saved['session_id'], 'session-a')
        self.assertEqual(saved['attempt_id'], 'attempt-a')
        self.assertEqual(saved['payload']['claim_event_id'], claim['event_id'])

    def test_conflicting_legacy_claim_binding_stops_collection(self):
        self.setup_job()
        claim = bridge.claim(self.root, self.workspace, 'session-a', 'attempt-a')
        previous = next(e for e in self.archive.events() if e['id'] == claim['event_id'])
        request = {k: previous[k] for k in ('kind', 'actor', 'session_id', 'run_id', 'operation_id', 'attempt_id', 'bindings', 'parents', 'outputs', 'payload')}
        request.update(session_id='session-b', attempt_id='attempt-b')
        request['payload'] = {**request['payload'], 'workspace': str(self.workspace.parent / 'wrong-leaf')}
        self.archive.append(request, 'synthetic-legacy-invalid-claim')
        self.output('report.md', 'Correct leaf output')
        with self.assertRaisesRegex(ArchiveError, 'conflicting historical claim'):
            bridge.collect(self.root, self.workspace, 'complete')
        with self.assertRaisesRegex(ArchiveError, 'claim history conflicts'):
            bridge.claim(self.root, self.workspace, 'session-a', 'attempt-a')

    def test_foreign_coverage_cannot_certify_same_job_output(self):
        self.setup_job()
        claimed = bridge.claim(self.root, self.workspace, 'session-a', 'attempt-a')
        start = rounds.start_record(self.archive, 'synthetic-run')
        for n, (workspace, session, attempt) in enumerate([
            (str(self.workspace), 'wrong-session', 'attempt-a'),
            (str(self.workspace), 'session-a', 'wrong-attempt'),
            (str(self.workspace.parent / 'wrong-leaf'), 'session-a', 'attempt-a')]):
            self.archive.append(bridge.event(start, 'capture.coverage', self.request['job_id'],
                {'job_id': self.request['job_id'], 'workspace': workspace, 'status': 'BOUNDED_COMPLETE'},
                parents=[claimed['event_id']], session=session, attempt=attempt), 'synthetic-foreign-coverage-' + str(n))
        self.output('report.md', 'Correct leaf output')
        result = bridge.collect(self.root, self.workspace, 'complete')
        self.assertEqual(result['source_coverage'], 'NOT_CAPTURED')

    def test_settings_use_current_documented_file_and_fork_rules(self):
        settings = json.loads((self.root / 'templates/philosophy_claude/settings.json').read_text())
        rules = settings['permissions']
        self.assertIn('Edit(/output/**)', rules['allow'])
        self.assertFalse(any(x.startswith('Write(') for x in rules['allow'] + rules['deny']))
        self.assertIn('Agent(fork)', rules['deny'])
        self.assertEqual(settings['env']['CLAUDE_CODE_FORK_SUBAGENT'], '0')
        self.assertEqual(rules['defaultMode'], 'default')


if __name__ == '__main__': unittest.main()
