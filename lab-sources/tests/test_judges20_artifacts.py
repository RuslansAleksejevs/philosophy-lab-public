"""Synthetic-only tests; no real essay or native session content is accessed."""
import argparse
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import judges20_artifacts as pilot
from research_archive import Archive, ArchiveError


class JudgesArtifactsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='synthetic-pilot-')
        self.root = Path(self.temp.name).resolve()
        self.source = self.root / 'synthetic.jsonl'
        self.directory = pilot.CAMPAIGN / 'essay-51'
        self.identity = {'session_id': 'synthetic-author', 'source_path': str(self.source),
                         'source_cwd': str(self.root), 'agent_path': '/root/author_51'}
        self.write('LAB_PROFILE.json', json.dumps({'lab': {'kind': 'PHILOSOPHY_PROGRAM'}}))
        self.write('.lab/philosophy.json', json.dumps({'schema_version': 1,
                    'kernel': 'philosophy.v1', 'archive_format': 'research-archive.v1'}))
        self.write('methods/judges-v1.json', json.dumps({'id': 'synthetic', 'stages': pilot.rounds.STAGES}))
        for name in ['AGENTS.md', 'AGENT_POLICY.md', 'USER_PREFERENCES.md', 'workflows/ROUND.md', '.codex/config.toml']:
            self.write(name, 'Synthetic instructions\n')
        self.write(pilot.CAMPAIGN / 'AUTHOR_BRIEF.md', 'Synthetic brief\n')
        self.write(pilot.CAMPAIGN / 'campaign.json', '{"synthetic":true}\n')
        self.write(pilot.CAMPAIGN / 'OPERATIONS.md', 'Synthetic operations\n')
        self.write('scripts/judges20_artifacts.py', 'Synthetic helper snapshot\n')
        self.write(self.directory / 'author-task.txt', 'Synthetic task')
        self.write(self.directory / 'source-manifest.json', '[]')
        for name in ('RULES_SUMMARY.md', 'rules.html', 'faq.html'):
            self.write('research/judges/20260912/competition/' + name, 'Synthetic rules')
        self.profile = self.write('research/judges/20260912/profiles/synthetic-v1.md', 'Synthetic judge evidence')
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
        return f'[JUDGES20:51:{stage} sha256={digest}]'

    def args(self, command, **extra):
        return argparse.Namespace(command=command, essay='51', agent_path='/root/author_51', **extra)

    def test_exact_visible_marker_identity_and_hash(self):
        digest = 'a' * 64
        self.native(self.marker('question', digest))
        selected = pilot.marker_record(self.source, 'synthetic-author', self.root, '51', 'question', digest)
        self.assertEqual(selected['line'], 2)
        for sid, expected in [('wrong-session', digest), ('synthetic-author', 'b' * 64)]:
            with self.assertRaises(ArchiveError):
                pilot.marker_record(self.source, sid, self.root, '51', 'question', expected)
        self.native(self.marker('question', digest), phase='analysis')
        with self.assertRaises(ArchiveError):
            pilot.marker_record(self.source, 'synthetic-author', self.root, '51', 'question', digest)

    def test_paths_and_receipt_conflict(self):
        for name in ['research/campaigns/judges20-20260912/essay-52/question.md', '../escape', '/tmp/escape']:
            with self.assertRaises(ArchiveError):
                pilot.own_file(self.root, '51', name)
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
            args = self.args('record', stage=stage, file=path, source_note='Synthetic sources only', final_file=None, profile=self.profile)
            marker_text = self.marker(stage, digest)
            if stage == 'decision':
                review_path = self.write(self.directory / 'review-2.md', 'Synthetic second independent judge review')
                review_digest = pilot.sha((self.root / review_path).read_bytes())
                self.native(self.marker('review2', review_digest), sid='synthetic-reviewer2')
                second = dict(self.identity, session_id='synthetic-reviewer2', agent_path='/root/reviewer2_51')
                second_args = self.args('review', file=review_path, profile=self.profile)
                second_args.agent_path = second['agent_path']
                with patch.object(pilot, 'discover', return_value=second):
                    second_result = pilot.process(self.root, second_args)
                    self.assertEqual(second_result, pilot.process(self.root, second_args))
                args.final_file = self.write(self.directory / 'final.md', 'Synthetic final revised fixture\n')
                final_digest = pilot.sha((self.root / args.final_file).read_bytes())
                marker_text += '\n' + self.marker('final', final_digest)
            if stage == 'critique':
                identity['session_id'] = 'synthetic-critic'
                identity['agent_path'] = args.agent_path = '/root/reviewer1_51'
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
        self.assertEqual(result['final_candidate_event_id'], 'candidate:judges20-51-decision')
        self.assertEqual(result['final_sha256'], final_digest)
        self.assertFalse((self.root / 'knowledge/resume.md').exists())
        archive = Archive(self.root / 'research/archive')
        self.assertTrue(archive.validate()['ok'])
        self.assertTrue(pilot.Timeline(archive).validate()['ok'])
        events=archive.events()
        stages={e['payload']['stage']:e for e in events if e['kind']=='round.stage'}
        second=next(e for e in events if e['kind']=='round.judge_review')
        checkpoint=next(e for e in events if e['kind']=='checkpoint')
        self.assertIn(second['id'],stages['decision']['parents'])
        self.assertIn(stages['decision']['id'],checkpoint['parents'])
        for stage,key in [('sources','source_snapshot_event_id'),('critique','profile_event_id')]:
            receipt=json.loads((self.root/self.directory/(stage+'.receipt.json')).read_text())
            self.assertIn(receipt[key],stages[stage]['parents'])
        with patch.object(archive,'events',wraps=archive.events) as reads:
            self.assertEqual(pilot.rounds.validate_round_history(archive),[])
            self.assertEqual(reads.call_count,1)

    def test_complete_cycle_through_single_writer_per_command(self):
        process = pilot.process
        def locked(root, args):
            archive = Archive(root / 'research/archive')
            with patch.object(archive, '_audit', wraps=archive._audit) as audit:
                with archive.writer() as writer:
                    result = process(root, args, archive=writer)
                self.assertEqual(audit.call_count, 1)
                return result
        with patch.object(pilot, 'process', side_effect=locked):
            self.test_complete_canonical_cycle_and_identical_retry()

    def test_copied_first_critic_receipt_cannot_replace_second_review(self):
        original=pilot.process
        def substitute(root,args,*pos,**kw):
            if args.command=='review':
                prior=(root/self.directory/'critique.receipt.json').read_bytes()
                (root/self.directory/'review2.receipt.json').write_bytes(prior)
                return {'synthetic':'copied-first-critic'}
            return original(root,args,*pos,**kw)
        with patch.object(pilot,'process',side_effect=substitute), self.assertRaisesRegex(ArchiveError,'canonical second review'):
            self.test_complete_canonical_cycle_and_identical_retry()
        events=Archive(self.root/'research/archive').events()
        self.assertFalse(any(e['kind']=='checkpoint' for e in events))
        self.assertFalse(any(e['kind']=='round.stage' and e['payload']['stage']=='decision' for e in events))

    def test_second_reviewer_cannot_reuse_first_critic_session(self):
        original=pilot.process
        def substitute(root,args,*pos,**kw):
            if args.command=='review':
                wrong=dict(self.identity,session_id='synthetic-critic',agent_path='/root/reviewer2_51')
                with patch.object(pilot,'discover',return_value=wrong):
                    return original(root,args,*pos,**kw)
            return original(root,args,*pos,**kw)
        with patch.object(pilot,'process',side_effect=substitute), self.assertRaisesRegex(ArchiveError,'distinct from author and first critic'):
            self.test_complete_canonical_cycle_and_identical_retry()

    def test_second_review_receipt_cannot_claim_first_critic_capture(self):
        original=pilot.process; changed=False
        def substitute(root,args,*pos,**kw):
            nonlocal changed
            value=original(root,args,*pos,**kw)
            if args.command=='review' and not changed:
                path=root/self.directory/'review2.receipt.json';receipt=json.loads(path.read_text())
                receipt['captures']=json.loads((root/self.directory/'critique.receipt.json').read_text())['captures']
                path.write_text(json.dumps(receipt));changed=True
            return value
        with patch.object(pilot,'process',side_effect=substitute), self.assertRaisesRegex(ArchiveError,'receipt capture differs'):
            self.test_complete_canonical_cycle_and_identical_retry()

    def test_second_review_receipt_cannot_name_another_profile(self):
        original=pilot.process; changed=False
        def substitute(root,args,*pos,**kw):
            nonlocal changed
            value=original(root,args,*pos,**kw)
            if args.command=='review' and not changed:
                path=root/self.directory/'review2.receipt.json';receipt=json.loads(path.read_text())
                receipt['profile_event_id']=json.loads((root/self.directory/'critique.receipt.json').read_text())['profile_event_id']
                path.write_text(json.dumps(receipt));changed=True
            return value
        with patch.object(pilot,'process',side_effect=substitute), self.assertRaisesRegex(ArchiveError,'invalid exact judge profile'):
            self.test_complete_canonical_cycle_and_identical_retry()

    def test_second_review_can_reuse_exact_collector_original_with_explicit_run_binding(self):
        original=pilot.bind_marker
        def precollect(root,archive,identity,essay,stage,digest,run):
            if stage=='review2':
                source=Path(identity['source_path'])
                observed=pilot.marker_record(source,identity['session_id'],root,essay,stage,digest)
                pilot.capture.capture(archive.root,source,identity['session_id'],root,
                    start_line=observed['line'],end_line=observed['line'],run_id='synthetic-prior-import')
            return original(root,archive,identity,essay,stage,digest,run)
        with patch.object(pilot,'bind_marker',side_effect=precollect):
            self.test_complete_canonical_cycle_and_identical_retry()


if __name__ == '__main__':
    unittest.main()
