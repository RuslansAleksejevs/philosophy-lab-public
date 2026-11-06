"""Synthetic native-record fixtures in temporary archives, never research data."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
import io
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import hundred_artifacts as h
from research_archive import Archive, ArchiveError, canonical


class HundredTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='synthetic-hundred-')
        self.root = Path(self.tmp.name).resolve()
        self.write('LAB_PROFILE.json', {'lab': {'kind': 'PHILOSOPHY_PROGRAM'}})
        self.write('.lab/philosophy.json', {'schema_version': 1, 'kernel': 'philosophy.v1', 'archive_format': 'research-archive.v1'})
        self.write('methods/synthetic.json', {'id': 'synthetic-hundred', 'stages': h.rounds.STAGES})
        for name in ('AGENTS.md', 'AGENT_POLICY.md', 'USER_PREFERENCES.md', 'workflows/ROUND.md', '.codex/config.toml'):
            self.write(name, 'Synthetic neutral configuration')
        self.write('campaign/essay/task.txt', 'Synthetic task')
        self.archive = Archive(self.root / 'research/archive').init()
        self.run = 'synthetic-hundred'
        self.author = 'synthetic-author-0001'

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, name, value):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(value.encode() if isinstance(value, str) else canonical(value))
        return name

    def initialize(self, w, topology='flexible', critics=0):
        request = {'run_id': self.run, 'entity': 'synthetic/essay-01', 'directory': 'campaign/essay',
                   'session_id': self.author, 'method': 'methods/synthetic.json',
                   'inputs': ['campaign/essay/task.txt'], 'requested': {'model': 'synthetic', 'effort': 'synthetic'},
                   'purpose': 'technical', 'topology': topology,
                   'requirements': {'minimum_independent_critiques': critics,
                                    'method_exemptions': {'critique': 'one-shot: no independent critique requested'} if critics == 0 else {}}}
        return h.init(self.root, w, request, canonical(request))

    def stage(self, w, name, kind, phase, parents=(), session=None, canonical_stage=None, candidate=None):
        session = session or self.author
        inputs = ['campaign/essay/task.txt'] + [
            {'path': p['path'], 'sha256': p['artifact_sha256'], 'from_event_id': p['stage_event_id']}
            for p in parents]
        task = {'run_id': self.run, 'stage': name, 'session_id': session, 'kind': kind, 'phase': phase,
                'inputs': inputs, 'parents': [p['stage_event_id'] for p in parents], 'summary': 'Synthetic ' + name}
        if phase == 'critique':
            task['independent'] = True
        if canonical_stage:
            task['canonical_stage'] = canonical_stage
        h.prepare(self.root, w, task, canonical(task))
        request = {'run_id': self.run, 'stage': name, 'artifact': self.write('campaign/essay/' + name + '.txt', 'Synthetic ' + name)}
        if candidate:
            request['candidate'] = {'parent_candidate_events': candidate}
        if phase == 'sources':
            source = self.write('campaign/essay/source.txt', 'Synthetic exact read source')
            request.update(source_manifest=self.write('campaign/essay/manifest.json', [
                {'citation': 'Synthetic source', 'path': source, 'read_status': 'excerpt'}]),
                source_note='Synthetic excerpt only; no actual research')
        if canonical_stage == 'decision':
            request['final_file'] = self.write('campaign/essay/final.txt', 'Synthetic final')
        _, plan, _ = h.state(w, self.run)
        marker = h.marker_for(self.run, name, h.snapshot(self.root, plan, request))
        source = self.root / (session + '.jsonl')
        if not source.exists():
            source.write_bytes(canonical({'type': 'session_meta', 'payload': {'id': session, 'cwd': str(self.root)}}).replace(b'\n', b'') + b'\n')
        record = {'timestamp': '2026-09-25T01:00:00Z', 'type': 'response_item',
                  'payload': {'type': 'message', 'role': 'assistant', 'phase': 'commentary',
                              'content': [{'type': 'output_text', 'text': marker}]}}
        with source.open('ab') as stream:
            stream.write(json.dumps(record).encode() + b'\n')
        result = h.record(self.root, w, request, canonical(request), source)
        result['path'] = request['artifact']
        result['record_request'] = request
        result['native_source'] = source
        return result

    def checkpoint(self, w, final):
        summary = {key: 'Synthetic bounded fixture' for key in
                   ('question', 'contribution', 'criticism', 'limitations', 'next_step', 'method_change', 'comparability', 'coverage_boundary')}
        summary['outcome'] = 'COMPLETE_TECHNICAL'
        request = {'run_id': self.run, 'summary': self.write('campaign/essay/checkpoint.json', summary),
                   'final_stage_event_id': final['stage_event_id']}
        return h.checkpoint(self.root, w, request, canonical(request))

    def test_one_shot_exact_sources_candidate_and_checkpoint_without_invented_critic(self):
        with patch.object(self.archive, '_audit', wraps=self.archive._audit) as audit:
            with self.archive.writer() as w, h.cached_events(w):
                self.initialize(w)
                idea = self.stage(w, 'arbitrary/idea-v1', 'idea', 'idea')
                sources = self.stage(w, 'read-1', 'origin', 'sources', [idea])
                draft = self.stage(w, 'one-shot', 'draft', 'draft', [idea, sources])
                self.assertEqual(h.validate(w, self.run, complete=False), [])
                cp = self.checkpoint(w, draft)
                self.assertEqual(h.validate(w, self.run), [])
                self.assertFalse(any(e['kind'] == 'round.stage' and e['payload'].get('stage') == 'critique' for e in w.events()))
                self.assertEqual(self.checkpoint(w, draft), cp)
                self.assertEqual(audit.call_count, 1)
        self.assertTrue(self.archive.validate()['ok'])

    def test_five_stage_two_independent_critics_branch_and_canonical_checkpoint(self):
        with self.archive.writer() as w, h.cached_events(w):
            self.initialize(w, topology='five-stage', critics=2)
            idea = self.stage(w, 'idea', 'idea', 'idea', canonical_stage='question')
            sources = self.stage(w, 'sources', 'origin', 'sources', [idea], canonical_stage='sources')
            draft = self.stage(w, 'draft', 'draft', 'draft', [idea, sources], canonical_stage='contribution')
            critic1 = self.stage(w, 'argument-check', 'critique', 'critique', [draft], session='synthetic-critic-0001', canonical_stage='critique')
            critic2 = self.stage(w, 'source-check', 'critique', 'critique', [draft], session='synthetic-critic-0002')
            revision = self.stage(w, 'branch/revision', 'revision', 'revision', [draft, critic1, critic2],
                                  session='synthetic-reviser-0001', canonical_stage='decision', candidate=[draft['candidate_event_id']])
            self.checkpoint(w, revision)
            self.assertEqual(h.validate(w, self.run), [])
            self.assertEqual(h.rounds.validate_round_history(w), [])

    def test_draft_gate_independence_tamper_and_native_marker(self):
        with self.archive.writer() as w, h.cached_events(w):
            self.initialize(w)
            task = {'run_id': self.run, 'stage': 'early-draft', 'session_id': self.author, 'kind': 'draft',
                    'phase': 'draft', 'inputs': ['campaign/essay/task.txt'], 'parents': [], 'summary': 'Synthetic draft'}
            with self.assertRaisesRegex(ArchiveError, 'archive idea'):
                h.prepare(self.root, w, task, canonical(task))
            idea = self.stage(w, 'idea', 'idea', 'idea')
            task.update(stage='critic', kind='critique', phase='critique', independent=True,
                        parents=[idea['stage_event_id']], inputs=[{'path': idea['path'], 'from_event_id': idea['stage_event_id']}])
            with self.assertRaisesRegex(ArchiveError, 'distinct actual session'):
                h.prepare(self.root, w, task, canonical(task))
            request = idea['record_request']
            self.assertEqual(h.record(self.root, w, request, canonical(request), idea['native_source'])['stage_event_id'], idea['stage_event_id'])
            self.write(idea['path'], 'Tampered synthetic artifact')
            with self.assertRaisesRegex(ArchiveError, 'immutable record conflict'):
                h.record(self.root, w, request, canonical(request), idea['native_source'])
            self.assertEqual(h.validate(w, self.run, complete=False), [])

    def test_offline_marker_never_opens_archive(self):
        init = {'run_id': self.run, 'directory': 'campaign/essay'}
        request = {'run_id': self.run, 'stage': 'offline',
                   'artifact': self.write('campaign/essay/offline.txt', 'Synthetic offline artifact')}
        self.write('campaign/essay/init.json', init)
        self.write('campaign/essay/record.json', request)
        output = io.StringIO()
        with patch.object(h, 'Archive', side_effect=AssertionError('offline must not open archive')), \
             patch.object(sys, 'argv', ['hundred_artifacts.py', 'marker', '--root', str(self.root),
                                       '--request', 'campaign/essay/record.json', '--init-request', 'campaign/essay/init.json']), \
             patch('sys.stdout', output):
            self.assertEqual(h.main(), 0)
        expected = h.marker_for(self.run, 'offline', h.snapshot(self.root, {'payload': {'request': init}}, request))
        self.assertEqual(output.getvalue().strip(), expected)

    def test_native_session_mismatch_and_missing_marker_do_not_create_evidence(self):
        with self.archive.writer() as w, h.cached_events(w):
            self.initialize(w)
            _, _, first = h.state(w, self.run)
            source = self.root / 'synthetic-wrong-native.jsonl'
            source.write_text(json.dumps({'type': 'session_meta', 'payload': {'id': 'wrong', 'cwd': str(self.root)}}) + '\n')
            before = len(w.events())
            with self.assertRaisesRegex(ArchiveError, 'session/cwd mismatch'):
                h.native_capture(self.root, w, first, self.author, '[Synthetic marker]', source)
            source.write_text(json.dumps({'type': 'session_meta', 'payload': {'id': self.author, 'cwd': str(self.root)}}) + '\n')
            with self.assertRaisesRegex(ArchiveError, 'exactly one real own commentary'):
                h.native_capture(self.root, w, first, self.author, '[Synthetic marker]', source)
            self.assertEqual(len(w.events()), before)

    def test_interrupted_stage_requires_replay_before_dependency(self):
        with self.archive.writer() as w, h.cached_events(w):
            self.initialize(w)
            real_append = h.lineage.append
            once = {'failed': False}
            def fail_after_stage(writer, entry, session, *args, **kwargs):
                if entry['kind'] == 'idea' and not once['failed']:
                    once['failed'] = True
                    raise OSError('synthetic interruption after durable stage')
                return real_append(writer, entry, session, *args, **kwargs)
            with patch.object(h.lineage, 'append', side_effect=fail_after_stage):
                with self.assertRaisesRegex(OSError, 'synthetic interruption'):
                    self.stage(w, 'interrupted', 'idea', 'idea')
            known, _, _ = h.state(w, self.run)
            partial = h.stage_event(known, self.run, 'interrupted', 'hundred.stage')
            with self.assertRaisesRegex(ArchiveError, 'incomplete'):
                h.ancestors(known, [partial['id']])
            request = partial['payload']['packet']['request']
            result = h.record(self.root, w, request, canonical(request), self.root / (self.author + '.jsonl'))
            self.assertEqual(result['stage_event_id'], partial['id'])
            self.assertEqual(h.validate(w, self.run, complete=False), [])


if __name__ == '__main__':
    unittest.main()
