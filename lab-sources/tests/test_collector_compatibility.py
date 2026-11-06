"""Synthetic renderer-only signature adoption; never reads real sessions."""
import json
from pathlib import Path
import sys
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import collector as module
from collector import Collector
from research_archive import ArchiveError
import test_collector as fixtures
from test_collector import message


def encoded(value):
    return (json.dumps(value, sort_keys=True) + '\n').encode()


class CompatibilityContractTests(unittest.TestCase):
    def setUp(self):
        self.old = {name: ('old bytes: ' + name).encode() for name in module.CAPTURE_VERSION_ORDER}
        self.old_sha = module.digest(b''.join(k.encode() + b'\0' + v for k, v in self.old.items()))
        self.collector_sha = module.digest(self.old['scripts/collector.py'])
        self.patches = [mock.patch.object(module, 'COMPATIBLE_CAPTURE_SIGNATURE', self.old_sha),
                        mock.patch.object(module, 'COMPATIBLE_COLLECTOR_SHA256', self.collector_sha)]
        for patch in self.patches:
            patch.start(); self.addCleanup(patch.stop)
        self.current = dict(self.old)
        self.current['scripts/collector.py'] = b'audited compatibility predicate only'
        self.current['scripts/collector_views.py'] = b'audited renderer repair'
        self.manifest = {'schema_version': 1, 'purpose': 'renderer-only-compatibility-20261031',
                         'from_signature': self.old_sha, 'from_collector_sha256': self.collector_sha,
                         'current_files': {n: module.digest(self.current[n]) for n in
                                           ('scripts/collector.py', 'scripts/collector_views.py')}}
        self.current[module.COMPATIBILITY_PATH] = encoded(self.manifest)
        self.objects = {module.digest(v): v for v in self.old.values()}
        self.archive = mock.Mock()
        self.archive.get.side_effect = self.objects.__getitem__
        self.event = {'id': 'synthetic-old-version', 'kind': 'collector.version',
                      'session_id': 'synthetic-source-session',
                      'payload': {'signature': self.old_sha,
                                  'files': {k: module.digest(v) for k, v in self.old.items()}},
                      'outputs': list(self.objects)}
        self.index = {'collector-version:' + self.old_sha: self.event}

    def check(self, manifest=None, current=None):
        return module.capture_compatibility(self.manifest if manifest is None else manifest,
                                            self.current if current is None else current,
                                            self.index, self.archive)

    def test_exact_old_objects_and_only_two_audited_changes_enable_alias(self):
        parsed = module.parse_capture_compatibility(encoded(self.manifest))
        self.assertEqual(parsed, self.manifest)
        result = self.check()
        self.assertTrue(result['active'])
        self.assertEqual(result['from_signature'], self.old_sha)
        self.assertEqual(self.archive.get.call_count, len(module.CAPTURE_VERSION_ORDER))

    def test_every_capture_or_config_change_disables_alias(self):
        for name in module.CAPTURE_VERSION_ORDER:
            with self.subTest(name=name):
                changed = {**self.current, name: b'unapproved changed bytes'}
                self.assertFalse(self.check(current=changed)['active'])
        self.assertFalse(self.check(current={**self.current, 'scripts/extra.py': b'extra'})['active'])

    def test_stale_or_wrong_transition_never_gets_alias(self):
        for change in ({'from_signature': '0' * 64}, {'from_collector_sha256': '1' * 64}):
            self.assertFalse(self.check({**self.manifest, **change})['active'])
        self.index.clear()
        self.assertFalse(self.check()['active'])

    def test_old_signature_is_rebuilt_from_objects_not_trusted_from_payload(self):
        self.objects[module.digest(self.old['scripts/capture_codex.py'])] = b'wrong stored bytes'
        self.assertFalse(self.check()['active'])

    def test_old_version_requires_exact_file_set_and_referenced_objects(self):
        self.event['outputs'].pop()
        self.assertFalse(self.check()['active'])
        self.event['outputs'] = list(self.objects)
        self.event['payload']['files']['scripts/unknown.py'] = '2' * 64
        self.assertFalse(self.check()['active'])

    def test_archive_corruption_is_not_downgraded_to_compatibility(self):
        self.archive.get.side_effect = ArchiveError('corrupt synthetic object')
        with self.assertRaises(ArchiveError):
            self.check()

    def test_malformed_manifest_fails_closed(self):
        invalid = [[], None, {}, {**self.manifest, 'extra': True},
                   {**self.manifest, 'schema_version': True},
                   {**self.manifest, 'from_signature': 'bad'},
                   {**self.manifest, 'current_files': {}},
                   {**self.manifest, 'purpose': 'general compatibility'}]
        for value in invalid:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    module.parse_capture_compatibility(encoded(value))


class CompatibilityCollectorTests(unittest.TestCase):
    def setUp(self):
        self.fx = fixtures.CollectorTests()
        self.fx.setUp(); self.addCleanup(self.fx.tearDown)
        self.fx.add_bytes(message('user', 'Exact original user text'))
        self.old = Collector(self.fx.root)
        self.old.collect()
        self.cursor = self.fx.cursor()
        self.original_events = self.fx.events()
        self.old_sha = self.old.signature
        self.collector_sha = module.digest(self.old.version_files['scripts/collector.py'])
        for patch in [mock.patch.object(module, 'COMPATIBLE_CAPTURE_SIGNATURE', self.old_sha),
                      mock.patch.object(module, 'COMPATIBLE_COLLECTOR_SHA256', self.collector_sha)]:
            patch.start(); self.addCleanup(patch.stop)
        self.manifest = {'schema_version': 1, 'purpose': 'renderer-only-compatibility-20261031',
                         'from_signature': self.old_sha, 'from_collector_sha256': self.collector_sha,
                         'current_files': {n: module.digest(self.old.version_files[n]) for n in
                                           ('scripts/collector.py', 'scripts/collector_views.py')}}
        self.manifest_path = self.fx.root / module.COMPATIBILITY_PATH
        self.manifest_path.write_bytes(encoded(self.manifest))

    def test_unchanged_source_adopts_once_without_read_or_projection_or_cursor_change(self):
        new = Collector(self.fx.root)
        self.assertTrue(new.capture_compatibility['active'])
        self.assertNotEqual(new.signature, self.old_sha)
        with mock.patch.object(module, 'project_record', side_effect=AssertionError('must not reproject')):
            with mock.patch('codex_rollout.RolloutFile.logical_stat', side_effect=AssertionError('must not reread')):
                self.assertEqual(new.collect()['status'], 'RUNNING')
                self.assertEqual(new.collect()['status'], 'RUNNING')
        self.assertEqual(self.fx.cursor(), self.cursor)
        self.assertEqual(self.fx.events()[:len(self.original_events)], self.original_events)
        self.assertEqual(len(self.fx.events()), len(self.original_events) + 2)
        migration = self.fx.events('collector.capture_compatibility')
        self.assertEqual(len(migration), 1)
        self.assertEqual(migration[0]['payload']['whole_trace'], 'INCOMPLETE')
        version = self.fx.events('collector.version')[-1]
        manifest_sha = module.digest(self.manifest_path.read_bytes())
        self.assertEqual(version['payload']['files'][module.COMPATIBILITY_PATH], manifest_sha)
        self.assertIn(manifest_sha, version['outputs'])
        self.assertEqual(self.fx.archive.get(manifest_sha), self.manifest_path.read_bytes())
        restarted = Collector(self.fx.root)
        restarted.collect()
        self.assertEqual(len(self.fx.events()), len(self.original_events) + 2)

    def test_only_new_tail_is_projected_and_original_capture_stays_identical(self):
        raw_before = self.fx.events('capture.raw_record')
        text_before = self.fx.events('collector.message')
        self.fx.add_bytes(message('assistant', 'New visible tail', phase='final'))
        new = Collector(self.fx.root)
        with mock.patch.object(module, 'project_record', wraps=module.project_record) as projector:
            self.assertEqual(new.collect()['status'], 'RUNNING')
            self.assertEqual(projector.call_count, 1)
        self.assertEqual(self.fx.events('capture.raw_record')[:len(raw_before)], raw_before)
        self.assertEqual(len(self.fx.events('capture.raw_record')), len(raw_before) + 1)
        self.assertEqual(len(self.fx.events('collector.message')), len(text_before) + 1)
        self.assertEqual(self.fx.cursor()['signature'], new.signature)
        self.assertEqual(self.fx.cursor()['counts'], {'user_prompts': 1, 'assistant_final': 1})

    def test_stale_manifest_preserves_ordinary_strict_reset(self):
        self.manifest['current_files']['scripts/collector.py'] = 'f' * 64
        self.manifest_path.write_bytes(encoded(self.manifest))
        new = Collector(self.fx.root)
        self.assertFalse(new.capture_compatibility['active'])
        with mock.patch.object(module, 'project_record', wraps=module.project_record) as projector:
            new.collect()
            self.assertEqual(projector.call_count, 2)
        self.assertEqual(len(self.fx.events('collector.capture_compatibility')), 0)
        self.assertEqual(len(self.fx.events('capture.raw_record')), 1)

    def test_review_change_and_explicit_reconcile_still_reset(self):
        for reconcile in (False, True):
            with self.subTest(reconcile=reconcile):
                review = self.fx.root / 'collector/reviews' / (self.cursor_session() + '.json')
                if not reconcile:
                    review.parent.mkdir(parents=True, exist_ok=True)
                    review.write_text(json.dumps({'99': '0' * 64}))
                new = Collector(self.fx.root)
                with mock.patch.object(module, 'project_record', wraps=module.project_record) as projector:
                    new.collect(reconcile=reconcile)
                    self.assertEqual(projector.call_count, 2)

    def cursor_session(self):
        return self.fx.events('collector.coverage')[0]['session_id']


if __name__ == '__main__':
    unittest.main()
