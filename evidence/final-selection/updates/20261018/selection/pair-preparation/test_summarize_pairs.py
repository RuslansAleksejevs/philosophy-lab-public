"""Synthetic full50 pair evidence; never opens actual reviews or manuscripts."""
from pathlib import Path
import copy
import itertools
import json
import shutil
import tempfile
import unittest
import summarize_pairs as s
import test_prepare_pairs as p


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(s.R.encode(value))


def rebind_job(root, run, jid):
    lane = run / 'results' / jid; attempt = lane / 'attempt-001'
    local = s.load(attempt / 'receipt.json', root)
    local['outputs'] = {str(f.relative_to(root)): s.digest(f.read_bytes()) for f in attempt.iterdir() if f.name != 'receipt.json'}
    save(attempt / 'receipt.json', local)
    archive = s.load(lane / 'ARCHIVE_RECEIPT.json', root)
    archive['files'] = [s.descriptor(f, root) for f in sorted(attempt.iterdir())]
    archive['capture_sha256'] = s.digest((lane / 'CAPTURE_RECEIPT.json').read_bytes())
    save(lane / 'ARCHIVE_RECEIPT.json', archive)


def fixture():
    f = p.Pairs(); f.setUp()
    pairs = [f.pair(i + 1, ids) for i, ids in enumerate(list(itertools.combinations(f.bodies, 2))[:10])]
    prep = f.generate(pairs)
    run, root = f.run, f.root; batch = run / 'pair-batches/pairs-001'
    queue = s.load(batch / 'queue.json', root)
    for name in ('runner.py', 'test_runner.py'):
        (run / name).write_bytes((s.RUN / name).read_bytes())
    refs = s.load(run / 'START_RECEIPT.json', root)['files'] + prep['files'] + prep['source_files']
    refs += [s.descriptor(run / n, root) for n in ('runner.py', 'test_runner.py')]
    refs = {x['path']: s.descriptor(root / x['path'], root) for x in refs}
    save(batch / 'START_RECEIPT.json', {'status': 'SELECTION_INPUTS_ARCHIVED', 'phase': 'pair', 'batch_id': 'pairs-001', 'event_id': 'TEST_ONLY_PAIR_READY', 'files': list(refs.values())})
    for i, job in enumerate(queue['jobs']):
        lane = run / 'results' / job['id']; attempt = lane / 'attempt-001'; sid = 'TEST_ONLY_PAIR_SESSION_' + str(i)
        response = {'review_id': job['id'], 'pair_id': job['pair_id'], 'profile_id': job['profile_id'], 'read_complete': True,
                    'thesis_a': 'TEST_ONLY original thesis A', 'thesis_b': 'TEST_ONLY original thesis B',
                    'comparison': {k: 'TEST_ONLY exact comparison ' + k for k in ('argument', 'significance', 'originality')},
                    'concerns_a': [{'location': 'TEST_ONLY §1', 'reason': 'TEST_ONLY dissent kept verbatim', 'reply': 'TEST_ONLY reply'}], 'concerns_b': [],
                    'verdict': ('A', 'A', 'tie', 'B', 'neither')[i % 5], 'confidence': 'medium',
                    'reason_ru': ['Первое искусственное предложение объясняет условный довод.', 'Второе искусственное предложение сохраняет разногласие.'], 'limits': ['TEST_ONLY unresolved limit']}
        for name in ('response.json', 'final.txt'): save(attempt / name, response)
        proof = {'session_id': sid, 'prompt_sha256': job['prompt_sha256'], 'isolation_failures': [], 'tool_calls': [], 'other_user_metadata': [],
                 'prompt_lines': [3], 'final_lines': [8], 'configurations': [{'model': job['model'], 'effort': job['effort'], 'service_tier': job['service_tier']}]}
        save(attempt / 'native-check.json', proof)
        for name in ('launch.json', 'native-visible.json', 'stderr.json', 'visible-events.jsonl'): save(attempt / name, {'TEST_ONLY': True})
        save(lane / 'CAPTURE_RECEIPT.json', {'status': 'BOUNDED_VISIBLE_CAPTURE_ACCEPTED', 'session_id': sid, 'evidence_events': ['TEST_ONLY_CAPTURE_' + str(i)]})
        save(attempt / 'receipt.json', {'status': s.R.COMPLETE, 'job_id': job['id'], 'session_id': sid, 'quality_flags': [], 'visible_final_count': 1,
             'prompt_sha256': job['prompt_sha256'], 'schema_sha256': job['schema_sha256'], 'requested_model': job['model'], 'requested_effort': job['effort'], 'requested_service_tier': job['service_tier']})
        save(lane / 'ARCHIVE_RECEIPT.json', {'status': 'REVIEW_ARCHIVED', 'capture_status': 'BOUNDED_VISIBLE_CAPTURE_ACCEPTED', 'job_id': job['id'], 'session_id': sid,
             'input_event_id': 'TEST_ONLY_PAIR_READY', 'event_id': 'TEST_ONLY_REVIEW_' + str(i), 'lineage_event_id': 'TEST_ONLY_LINEAGE_' + str(i), 'lineage_entry_id': run.name + ':' + job['id'] + ':evaluation-v1'})
        rebind_job(root, run, job['id'])
    return f


class PairSummary(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.base = fixture()
    @classmethod
    def tearDownClass(cls): cls.base.tearDown()
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='TEST_ONLY-pair-summary-'); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve(); shutil.copytree(self.base.root, self.root, dirs_exist_ok=True)
        self.run = self.root / self.base.run.relative_to(self.base.root)
        self.batch = self.run / 'pair-batches/pairs-001'
        self.lane = self.run / 'results/P01-N1'; self.attempt = self.lane / 'attempt-001'
    def summarize(self): return s.summarize(self.run, 'pair-batches/pairs-001/queue.json', 'pair-batches/pairs-001/START_RECEIPT.json')
    def blocked(self, count=None):
        report, summary, index = self.summarize()
        self.assertFalse(report['summary_generated']); self.assertIsNone(summary); self.assertIsNone(index)
        self.assertNotIn('TEST_ONLY dissent', json.dumps(report)); self.assertNotIn('recorded_verdict_counts', report)
        if count is not None: self.assertEqual(report['accepted_reviews'], count)
        return report
    def alter_response(self, mutate):
        value = s.load(self.attempt / 'response.json', self.root); mutate(value)
        save(self.attempt / 'response.json', value); save(self.attempt / 'final.txt', value)
        rebind_job(self.root, self.run, 'P01-N1')

    def test_full50_maps_reversed_A_B_and_preserves_every_dissent(self):
        report, summary, index = self.summarize()
        self.assertEqual((report['accepted_reviews'], summary['pair_count'], summary['neutral_reviews'], summary['profile_reviews']), (50, 10, 30, 20))
        row = summary['rows'][0]; a, b = row['candidate_ids']
        self.assertEqual([x['mapped_verdict'] for x in row['reviews']], [a, b, 'tie', a, 'neither'])
        self.assertEqual(row['recorded_verdict_counts']['neutral'], {a: 1, b: 1, 'tie': 1, 'neither': 0})
        self.assertEqual(row['recorded_verdict_counts']['profile'], {a: 1, b: 0, 'tie': 0, 'neither': 1})
        self.assertTrue(row['different_recorded_verdicts'])
        for item in row['reviews']:
            self.assertEqual(item['response'], s.load(self.root / item['evidence']['response']['path'], self.root))
        self.assertEqual(len(index['pairs']), 10)
        self.assertEqual(len(index['pairs'][0]['full_response_files']), 5)
        self.assertEqual([x['pair_id'] for x in summary['rows']], ['P' + str(i).zfill(2) for i in range(1, 11)])

    def test_missing_or_nonaccepted_review_emits_no_partial_summary(self):
        path = self.lane / 'ARCHIVE_RECEIPT.json'; original = path.read_bytes(); path.unlink(); self.blocked(49)
        path.write_bytes(original); value = s.load(path, self.root); value['status'] = 'QUARANTINED_REVIEW_ARCHIVED_MISSING'; save(path, value); self.blocked(49)

    def test_changed_bound_response_or_capture_blocks_summary(self):
        path = self.attempt / 'response.json'; original = path.read_bytes(); path.write_bytes(original + b' '); self.blocked(49)
        path.write_bytes(original); save(self.lane / 'CAPTURE_RECEIPT.json', {'TEST_ONLY': 'changed'}); self.blocked(49)

    def test_identity_incomplete_reading_and_ref_schema_are_checked(self):
        original = (self.attempt / 'response.json').read_bytes()
        for mutate in (lambda x: x.update(read_complete=False), lambda x: x.update(pair_id='P99'), lambda x: x['concerns_a'][0].update(reply=123)):
            self.alter_response(mutate); self.blocked(49)
            (self.attempt / 'response.json').write_bytes(original); (self.attempt / 'final.txt').write_bytes(original); rebind_job(self.root, self.run, 'P01-N1')

    def test_duplicate_session_cannot_add_vote(self):
        sid = s.load(self.run / 'results/P01-N2/ARCHIVE_RECEIPT.json', self.root)['session_id']
        for path in (self.lane / 'ARCHIVE_RECEIPT.json', self.lane / 'CAPTURE_RECEIPT.json', self.attempt / 'receipt.json', self.attempt / 'native-check.json'):
            value = s.load(path, self.root); value['session_id'] = sid; save(path, value)
        rebind_job(self.root, self.run, 'P01-N1'); self.blocked(49)

    def test_extra_physical_attempt_and_unbound_file_rejected(self):
        extra = self.lane / 'attempt-002'; extra.mkdir(); self.blocked(49); extra.rmdir()
        (self.attempt / 'extra.txt').write_text('TEST_ONLY unexpected'); self.blocked(49)

    def test_frozen_A_B_queue_cannot_change(self):
        path = self.batch / 'queue.json'; queue = s.load(path, self.root); queue['jobs'][0]['ordered_blind_ids'].reverse(); save(path, queue)
        self.assertEqual(self.blocked()['status'], 'INVALID_INPUTS_COVERAGE_ONLY')

    def test_invalid_pair_mapping_rejected_even_when_fixture_rebound(self):
        path = self.batch / 'queue.json'; queue = s.load(path, self.root); queue['jobs'][0]['ordered_blind_ids'] = ['M01', 'M01']; save(path, queue)
        receipt_path = self.batch / 'START_RECEIPT.json'; receipt = s.load(receipt_path, self.root)
        receipt['files'] = [s.descriptor(path, self.root) if r['path'] == str(path.relative_to(self.root)) else r for r in receipt['files']]; save(receipt_path, receipt)
        self.assertEqual(self.blocked()['status'], 'INVALID_INPUTS_COVERAGE_ONLY')

    def test_outputs_new_only_and_partial_has_coverage_only(self):
        values = self.summarize(); destination = self.run / 'summaries/pairs-synthetic'; s.write_outputs(destination, self.run, *values)
        self.assertEqual({p.name for p in destination.iterdir()}, {'coverage.json', 'summary.json', 'pair-response-files.json'})
        before = {p.name: p.read_bytes() for p in destination.iterdir()}
        with self.assertRaises(ValueError): s.write_outputs(destination, self.run, *values)
        self.assertEqual({p.name: p.read_bytes() for p in destination.iterdir()}, before)
        (self.lane / 'ARCHIVE_RECEIPT.json').unlink(); values = self.summarize(); partial = self.run / 'summaries/pairs-partial'; s.write_outputs(partial, self.run, *values)
        self.assertEqual({p.name for p in partial.iterdir()}, {'coverage.json'})


if __name__ == '__main__': unittest.main(verbosity=2)
