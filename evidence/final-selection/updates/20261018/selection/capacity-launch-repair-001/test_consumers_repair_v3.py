"""Synthetic consumer checks only; no real review/archive/provider reads or calls."""
from pathlib import Path
from types import SimpleNamespace, ModuleType
import copy
import importlib.util
import sys
import tempfile
import unittest
from unittest.mock import patch

import summary_repair_v3 as S
import export_repair_v3 as E

OLD = S.DEFAULT_RUN / 'capacity-resume-20261018/replacement-v2'
sys.path.insert(0, str(OLD))
spec = importlib.util.spec_from_file_location('test_only_previous_fixture', OLD / 'test_consumers_v2.py')
previous = importlib.util.module_from_spec(spec)
spec.loader.exec_module(previous)
sys.path.remove(str(OLD))

# Load only the validator's pure failure-accounting helper. This explicit test
# boundary must never consult the actual canonical store.
stub = ModuleType('resolver_repair')
stub.ROOT, stub.RUN, stub.HERE = S.ROOT, S.DEFAULT_RUN, S.HERE
stub.JOBS = ('M12-N2', 'M13-N2')
def forbidden_resolution(*args, **kwargs):
    raise AssertionError('TEST_ONLY: actual resolution is forbidden')
stub.load_resolution = forbidden_resolution
with patch.dict(sys.modules, {'resolver_repair': stub}):
    spec = importlib.util.spec_from_file_location('test_only_repair_validator', S.HERE / 'validate_repair_v5.py')
    V = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(V)


class Fixture(previous.Fixture):
    def __init__(self, root):
        super().__init__(root)
        self.resolution['schema'] = 'selection-capacity-resolution.v3'
        lane = self.run / 'results/M12-N2'
        (lane / 'attempt-002').rename(lane / 'attempt-003')
        def moved(name):
            return name.replace('/M12-N2/attempt-002/', '/M12-N2/attempt-003/')
        receipt = self.load('results/M12-N2/attempt-003/receipt.json')
        receipt['outputs'] = {moved(k): v for k, v in receipt['outputs'].items()}
        receipt_ref = self.put('results/M12-N2/attempt-003/receipt.json', receipt)
        archive = self.load('results/M12-N2/ARCHIVE_RECEIPT.json')
        archive['accepted_attempt'] = 3
        archive['attempt_path'] = str((lane / 'attempt-003').relative_to(self.root))
        archive['files'] = [{**f, 'path': moved(f['path'])} for f in archive['files']]
        archive['files'] = [receipt_ref if f['path'] == receipt_ref['path'] else f for f in archive['files']]
        local_files = [self.put('results/M12-N2/attempt-002/' + name, value) for name, value in (
            ('launch.json', {'TEST_ONLY': 'local CLI launch'}),
            ('failure.json', {'TEST_ONLY': 'initialization failed', 'session_id': None}),
            ('stderr.json', {'TEST_ONLY': 'opaque local diagnostic'}),
            ('visible-events.jsonl', b''))]
        local = {'event_id': 'TEST_ONLY_LOCAL_LAUNCH_FAILURE', 'session_id': None, 'files': local_files,
                 'path': str((lane / 'attempt-002').relative_to(self.root))}
        archive['local_launch_failure_event_id'] = local['event_id']
        self.put('results/M12-N2/ARCHIVE_RECEIPT.json', archive)
        item = self.resolution['exceptions']['M12-N2']
        item['local_launch_failure'] = local
        item['accepted_attempt']['files'] = archive['files']
        safe = local_files[:2] + [self.put('capacity-launch-repair-001/ADDENDUM.json', {'TEST_ONLY': 'fixed 003 repair'})]
        item['evidence_files'] += safe
        self.resolution['evidence_files'] += safe
        for jid, item in self.resolution['exceptions'].items():
            number = S.ATTEMPT_NUMBERS[jid]
            item['accepted_attempt'].update(number=number, path=str((self.run / 'results' / jid / f'attempt-{number:03}').relative_to(self.root)))

    def resolved(self, job, run_dir, root, resolution):
        self.assert_scope(run_dir, root, resolution)
        number = S.ATTEMPT_NUMBERS.get(job['id'], 1)
        lane = Path(run_dir) / 'results' / job['id']
        return {'attempt': lane / f'attempt-{number:03}', 'attempt_number': number,
                'archive_receipt': lane / 'ARCHIVE_RECEIPT.json', 'capture_receipt': lane / 'CAPTURE_RECEIPT.json'}


class ConsumerTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix='TEST_ONLY-launch-repair-consumers-')
        self.addCleanup(tmp.cleanup)
        self.f = Fixture(tmp.name)
        for module in (S, E):
            mocked = patch.object(module, 'resolve_job', side_effect=self.f.resolved)
            mocked.start(); self.addCleanup(mocked.stop)

    def summary(self): return S.summarize(self.f.run, self.f.resolution)
    def export(self): return E.build(self.f.export_spec(), self.f.root, self.f.resolution)

    def test_110_votes_three_preserved_failures_and_unchanged_60_40(self):
        preserved = {str(p): p.read_bytes() for jid, number in [('M12-N2', 1), ('M12-N2', 2), ('M13-N2', 1)]
                     for p in (self.f.run / 'results' / jid / f'attempt-{number:03}').iterdir()}
        report, summary = self.summary()
        self.assertEqual((report['accepted_reviews'], report['missing_reviews']), (110, 0))
        for value in (report, summary):
            self.assertEqual((value['preserved_failed_attempts'], value['preserved_capacity_failures'], value['preserved_local_launch_failures'], value['failed_provider_review_slots']), (3, 2, 1, 2))
        self.assertEqual(summary['review_count'], 110)
        self.assertEqual(len({r['evidence']['session_id'] for row in summary['rows'] for r in row['reviews']}), 110)
        for jid, number in S.ATTEMPT_NUMBERS.items():
            evidence = next(x['evidence'] for x in report['jobs'] if x['job_id'] == jid)
            self.assertEqual(evidence['attempt_number'], number)
            self.assertIn(f'/{jid}/attempt-{number:03}/', evidence['response_file'])
        self.assertEqual(summary['rows'][0]['metrics'], S.frozen.aggregate(summary['rows'][0]['reviews']))
        self.assertTrue(all(Path(p).read_bytes() == data for p, data in preserved.items()))

    def test_summary_uses_frozen_verifier_for_exactly_108_ordinary_jobs(self):
        with patch.object(S.frozen, 'verify_job', wraps=S.frozen.verify_job) as ordinary:
            report, _ = self.summary()
        self.assertEqual(report['accepted_reviews'], 110)
        self.assertEqual(ordinary.call_count, 108)
        self.assertFalse({c.args[0]['id'] for c in ordinary.call_args_list} & S.LOGICAL_JOBS)

    def test_missing003_never_uses_failed002(self):
        (self.f.run / 'results/M12-N2/attempt-003/response.json').unlink()
        self.f.put('results/M12-N2/attempt-002/response.json', {'TEST_ONLY': 'cannot count'})
        report, summary = self.summary()
        self.assertEqual(report['accepted_reviews'], 109); self.assertIsNone(summary)
        with self.assertRaises(ValueError): self.export()

    def test_ordinary001_validation_remains_strict(self):
        self.f.put('results/M01-N1/attempt-001/final.txt', b'TEST_ONLY changed bytes')
        report, summary = self.summary()
        self.assertEqual(report['accepted_reviews'], 109); self.assertIsNone(summary)

    def test_export_uses003_002_and_all_safe_local_failure_metadata(self):
        result = self.export()
        paths = {x['path'] for x in result['files']}
        self.assertEqual(result['preserved_failed_attempts'], 3)
        self.assertEqual(result['accepted_review_counts_verified']['accepted_individual_reviews'], 110)
        for jid, number in S.ATTEMPT_NUMBERS.items():
            self.assertIn(E.SOURCE + f'results/{jid}/attempt-{number:03}/response.json', paths)
        self.assertTrue({f['path'] for f in self.f.resolution['evidence_files']} <= paths)
        self.assertFalse(any(Path(p).name in {'stderr.json', 'visible-events.jsonl', 'native-visible.json'} for p in paths))
        self.assertNotIn(E.SOURCE + 'results/M12-N2/attempt-002/response.json', paths)

    def test_local_failure_dependency_cannot_be_dropped(self):
        name = 'results/M12-N2/ARCHIVE_RECEIPT.json'
        archive = self.f.load(name); del archive['local_launch_failure_event_id']; self.f.put(name, archive)
        report, summary = self.summary()
        self.assertEqual(report['accepted_reviews'], 109); self.assertIsNone(summary)
        with self.assertRaises(ValueError): self.export()

    def test_wrong_attempt_or_fake_local_session_rejected(self):
        for modify in ('number', 'session'):
            resolution = copy.deepcopy(self.f.resolution)
            item = resolution['exceptions']['M12-N2']
            if modify == 'number': item['accepted_attempt']['number'] = 2
            else: item['local_launch_failure']['session_id'] = 'TEST_ONLY_INVENTED_SID'
            with self.assertRaises(ValueError): S.checked_resolution(resolution)

    def test_group_export_must_include_safe_local_failure_metadata(self):
        self.f.resolution['evidence_files'] = [f for f in self.f.resolution['evidence_files'] if '/attempt-002/' not in f['path']]
        with self.assertRaisesRegex(ValueError, 'omitted'): self.export()

    def failure_checker(self):
        events = [{'id': item['failed_attempt']['event_id'], 'kind': 'research.selection.transport_failure', 'run_id': self.f.run.name}
                  for item in self.f.resolution['exceptions'].values()]
        events.append({'id': 'TEST_ONLY_LOCAL_LAUNCH_FAILURE', 'kind': 'research.selection.local_launch_failure', 'run_id': self.f.run.name})
        return SimpleNamespace(run=self.f.run, events={e['id']: e for e in events})

    def test_validator_separates_capacity_and_local_failures(self):
        checker = self.failure_checker()
        self.assertEqual(V.check_failure_history(checker, self.f.resolution, {j['id'] for j in self.f.jobs}), 'TEST_ONLY_LOCAL_LAUNCH_FAILURE')
        checker.events['TEST_ONLY_LOCAL_LAUNCH_FAILURE']['kind'] = 'research.selection.transport_failure'
        with self.assertRaises(ValueError): V.check_failure_history(checker, self.f.resolution, S.LOGICAL_JOBS)

    def test_validator_rejects_unaccounted_failure_or_fourth_attempt(self):
        checker = self.failure_checker()
        checker.events['extra'] = {'id': 'extra', 'kind': 'research.selection.local_launch_failure', 'run_id': self.f.run.name}
        with self.assertRaises(ValueError): V.check_failure_history(checker, self.f.resolution, S.LOGICAL_JOBS)
        del checker.events['extra']
        (self.f.run / 'results/M12-N2/attempt-004').mkdir()
        with self.assertRaises(ValueError): V.check_failure_history(checker, self.f.resolution, S.LOGICAL_JOBS)


if __name__ == '__main__': unittest.main()
