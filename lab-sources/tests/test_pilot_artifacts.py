"""Synthetic-only tests; no real essay or native session content is accessed."""
import argparse
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import pilot_artifacts as pilot
from research_archive import Archive, ArchiveError


class PilotArtifactsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='synthetic-pilot-')
        self.root = Path(self.temp.name).resolve()
        self.source = self.root / 'synthetic.jsonl'
        self.directory = pilot.CAMPAIGN / 'essay-01'
        self.identity = {'session_id': 'synthetic-author', 'source_path': str(self.source),
                         'source_cwd': str(self.root), 'agent_path': '/root/essay_01'}
        self.write('LAB_PROFILE.json', json.dumps({'lab': {'kind': 'PHILOSOPHY_PROGRAM'}}))
        self.write('.lab/philosophy.json', json.dumps({'schema_version': 1,
                    'kernel': 'philosophy.v1', 'archive_format': 'research-archive.v1'}))
        self.write('methods/simple-v1.json', json.dumps({'id': 'synthetic', 'stages': pilot.rounds.STAGES}))
        for name in ['AGENTS.md', 'AGENT_POLICY.md', 'USER_PREFERENCES.md', 'workflows/ROUND.md', '.codex/config.toml']:
            self.write(name, 'Synthetic instructions\n')
        self.write(pilot.CAMPAIGN / 'AUTHOR_BRIEF.md', 'Synthetic brief\n')
        self.write(pilot.CAMPAIGN / 'campaign.json', '{"synthetic":true}\n')
        self.write(pilot.CAMPAIGN / 'OPERATIONS.md', 'Synthetic operations\n')
        self.write('scripts/pilot_artifacts.py', 'Synthetic helper snapshot\n')
        Archive(self.root / 'research/archive').init()

    def tearDown(self):
        self.temp.cleanup()

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return str(name)

    def native(self, text, role='assistant', phase='commentary', sid='synthetic-author'):
        meta = {'type': 'session_meta', 'payload': {'id': sid, 'cwd': str(self.root)}}
        item = {'type': 'response_item', 'timestamp': '2026-09-08T00:00:00Z',
                'payload': {'type': 'message', 'role': role, 'phase': phase,
                            'content': [{'type': 'output_text' if role == 'assistant' else 'input_text', 'text': text}]}}
        self.source.write_text(json.dumps(meta) + '\n' + json.dumps(item) + '\n')

    def marker(self, stage, digest):
        return f'[PILOT10:01:{stage} sha256={digest}]'

    def args(self, command, **extra):
        return argparse.Namespace(command=command, essay='01', agent_path='/root/essay_01', **extra)

    def test_exact_visible_marker_identity_and_hash(self):
        digest = 'a' * 64
        self.native(self.marker('question', digest))
        selected = pilot.marker_record(self.source, 'synthetic-author', self.root, '01', 'question', digest)
        self.assertEqual(selected['line'], 2)
        for sid, expected in [('wrong-session', digest), ('synthetic-author', 'b' * 64)]:
            with self.assertRaises(ArchiveError):
                pilot.marker_record(self.source, sid, self.root, '01', 'question', expected)
        self.native(self.marker('question', digest), phase='analysis')
        with self.assertRaises(ArchiveError):
            pilot.marker_record(self.source, 'synthetic-author', self.root, '01', 'question', digest)

    def test_paths_and_receipt_conflict(self):
        for name in ['research/campaigns/pilot10-20260908/essay-02/question.md', '../escape', '/tmp/escape']:
            with self.assertRaises(ArchiveError):
                pilot.own_file(self.root, '01', name)
        path = self.root / 'receipt.json'
        pilot.save_once(path, {'test': 1})
        pilot.save_once(path, {'test': 1})
        with self.assertRaises(ArchiveError):
            pilot.save_once(path, {'test': 2})

    def test_complete_canonical_cycle_and_identical_retry(self):
        with patch.object(pilot, 'discover', return_value=self.identity):
            pilot.process(self.root, self.args('init'))
        # Each synthetic record has its own source line, as native logs do.
        self.native('Synthetic start')
        author_lines = self.source.read_text()
        for stage in pilot.rounds.STAGES:
            path = self.write(self.directory / (stage + '.md'), 'Synthetic ' + stage + '\n')
            digest = pilot.sha((self.root / path).read_bytes())
            identity = dict(self.identity)
            args = self.args('record', stage=stage, file=path, source_note='Synthetic sources only', final_file=None)
            marker_text = self.marker(stage, digest)
            if stage == 'decision':
                args.final_file = self.write(self.directory / 'final.md', 'Synthetic final revised fixture\n')
                final_digest = pilot.sha((self.root / args.final_file).read_bytes())
                marker_text += '\n' + self.marker('final', final_digest)
            if stage == 'critique':
                identity['session_id'] = 'synthetic-critic'
                identity['agent_path'] = args.agent_path = '/root/critic_01'
                self.native(self.marker(stage, digest), sid='synthetic-critic')
            else:
                self.native(marker_text)
                author_lines += self.source.read_text().split('\n', 1)[1]
                self.source.write_text(author_lines)
            with patch.object(pilot, 'discover', return_value=identity):
                result = pilot.process(self.root, args)
                self.assertEqual(result, pilot.process(self.root, args))
        summary = {k: 'Synthetic fixture' for k in ('question', 'contribution', 'criticism', 'limitations',
                   'next_step', 'method_change', 'comparability', 'coverage_boundary')}
        summary['outcome'] = 'CONTINUE'
        path = self.write(self.directory / 'summary.json', json.dumps(summary))
        with patch.object(pilot, 'discover', return_value=self.identity):
            result = pilot.process(self.root, self.args('checkpoint', summary=path))
        self.assertEqual(result['final_candidate_event_id'], 'candidate:pilot10-01-decision')
        self.assertEqual(result['final_sha256'], final_digest)
        self.assertFalse((self.root / 'knowledge/resume.md').exists())
        archive = Archive(self.root / 'research/archive')
        self.assertTrue(archive.validate()['ok'])
        self.assertTrue(pilot.Timeline(archive).validate()['ok'])


if __name__ == '__main__':
    unittest.main()
