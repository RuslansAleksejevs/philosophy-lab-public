"""Synthetic archive only; exercises real lineage API and mechanical restart."""
from pathlib import Path
from contextlib import contextmanager
import copy
import sys
import tempfile
import unittest
from unittest.mock import patch

import validate_final as v
import closure_writer as closure
from test_validate_final import Fixture

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'scripts'))
import essay_lineage
from research_archive import Archive
import philosophy_round


class MemoryArchive:
    def __init__(self, fixture):
        self.records = copy.deepcopy(fixture.events)
        self.objects = dict(fixture.objects)
        self.opens = 0; self.depth = 0; self.fail_after_key = None
        self.checkpoint_calls = 0

    @contextmanager
    def writer(self):
        if self.depth: raise AssertionError('Unexpected nested outer writer')
        self.opens += 1; self.depth += 1
        try: yield self
        finally: self.depth -= 1

    def events(self): return copy.deepcopy(self.records)
    def get(self, digest): return self.objects[digest]
    def put(self, data):
        if self.depth != 1: raise AssertionError('Write outside single writer')
        digest = v.sha(data); self.objects[digest] = data
        return digest

    def append(self, request, key):
        if self.depth != 1: raise AssertionError('Append outside single writer')
        request = copy.deepcopy(request)
        old = next((e for e in self.records if e.get('delivery_key') == key), None)
        digest = v.sha(v.encode(request))
        if old:
            v.require(old['request_sha256'] == digest, 'Synthetic delivery key conflict')
            return copy.deepcopy(old)
        ids = {e['id'] for e in self.records}
        v.require(set(request.get('parents', [])) <= ids, 'Synthetic missing parent')
        for output in request.get('outputs', []):
            v.require(v.sha(self.get(output)) == output, 'Synthetic missing/damaged output object')
        event = {**request, 'id': 'event-closure-' + str(len(self.records)), 'delivery_key': key,
                 'request_sha256': digest, 'timestamp': '2026-10-18T12:00:00+00:00'}
        event.setdefault('parents', []); event.setdefault('outputs', []); event.setdefault('inputs', [])
        self.records.append(event)
        if self.fail_after_key == key:
            self.fail_after_key = None
            raise RuntimeError('Synthetic failure after committed prefix')
        return copy.deepcopy(event)


def checkpoint_api(root, writer, run, summary_path, coverage, incomplete=False):
    """Faithful small checkpoint contract; intentionally no real derived-file writes."""
    if incomplete is not True: raise AssertionError('Checkpoint must remain incomplete')
    writer.checkpoint_calls += 1
    first = next(e for e in writer.events() if e['kind'] == 'operation.started' and e['run_id'] == run)
    summary_data = (Path(root) / summary_path).read_bytes(); summary = v.strict(summary_data)
    common = {'actor': {'id': first['session_id'], 'role': 'AI'}, 'session_id': first['session_id'],
              'run_id': run, 'operation_id': first['operation_id'], 'attempt_id': first['attempt_id'], 'bindings': first['bindings']}
    cp = writer.append({**common, 'kind': 'checkpoint', 'parents': [first['id']] + coverage,
                        'outputs': [writer.put(summary_data)], 'payload': {'protocol': 'philosophy-checkpoint.v1',
                        'summary': summary, 'capture_status': 'INCOMPLETE', 'purpose': 'research', 'truth_status': 'NOT_CERTIFIED'}}, 'checkpoint:' + run)
    writer.append({**common, 'kind': 'operation.interrupted', 'parents': [first['id'], cp['id']],
                   'payload': {'checkpoint': cp['id'], 'outcome': summary['outcome'],
                               'scope': 'Recorded workflow completion, never philosophical truth'}}, 'round-terminal:' + run)
    return cp


class ClosureTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.f = Fixture(self.tmp.name)
        for e in self.f.events:
            e['timestamp'] = '2026-10-18T11:00:00+00:00'
            if e['kind'] == 'essay.lineage.entry': e['payload']['protocol'] = essay_lineage.PROTOCOL
        first = self.f.event('operation.started', payload={'protocol': 'philosophy-round.v1', 'purpose': 'research'})
        first.update(operation_id='round-' + self.f.run.name, attempt_id='fixture-attempt', timestamp='2026-10-18T10:00:00+00:00')
        self.f.events.remove(first); self.f.events.insert(0, first)
        self.f.start['run_start_event'] = first['id']; self.f.file('START_RECEIPT.json', self.f.start)
        self.gate = self.f.event('research.selection.selection_gate', parents=[r['event_id'] for r in self.f.reviews])
        self.plan_input = self.f.file('closure-input/PLAN_INPUT.json', self.f.plan)
        self.summary = self.f.file('closure-input/CHECKPOINT_SUMMARY.json', {k: ('CONTINUE' if k == 'outcome' else 'Synthetic administrative checkpoint scope only.') for k in closure.SUMMARY_FIELDS})
        stages = {}
        for name in v.STAGES[1:]:
            artifact = self.f.file('closure-input/' + name + '.txt', ('Synthetic root-provided ' + name).encode())
            stages[name] = {'files': [artifact], 'evidence_event_ids': [r['event_id'] for r in self.f.reviews]}
        self.req = {'schema': 'selection-closure-request.v1', 'run_id': self.f.run.name,
                    'session_id': first['session_id'], 'plan_input': self.plan_input,
                    'outputs': {k: str((self.f.run / name).relative_to(self.f.root)) for k, name in
                                [('final_plan', 'closure/FINAL_PLAN.json'), ('validation_report', 'closure/FINAL_VALIDATION.json'), ('final_receipt', 'FINAL_RECEIPT.json')]},
                    'stages': stages, 'selection_gate_event_ids': [self.gate['id']],
                    'checkpoint': {'summary': self.summary, 'coverage_event_ids': [self.f.gap['id']]},
                    'coordinator_configuration': {'requested': 'Synthetic no model', 'observed': 'Synthetic no model'},
                    'export_files': [self.summary], 'export_generated': ['final_plan', 'validation_report', 'closure_request'],
                    'pending_goal_steps': ['private_github_update', 'collector_restore']}
        self.path = self.f.run / 'closure-input/REQUEST.json'
        self.save_request()
        self.archive = MemoryArchive(self.f)

    def save_request(self): self.path.write_bytes(v.encode(self.req))

    def run_writer(self, allow=False, checkpoint=checkpoint_api):
        return closure.execute(self.f.root, self.f.run, self.path, self.archive,
                               allow_checkpoint_derived_updates=allow, lineage_api=essay_lineage, checkpoint_api=checkpoint)

    def add_checkpoint(self):
        with self.archive.writer() as writer:
            checkpoint_api(self.f.root, writer, self.f.run.name, self.summary['path'], [self.f.gap['id']], incomplete=True)
        self.archive.opens = 0; self.archive.checkpoint_calls = 0

    def test_existing_checkpoint_idempotent_single_writer(self):
        self.add_checkpoint()
        before = self.path.read_bytes(); input_plan = (self.f.root / self.plan_input['path']).read_bytes()
        receipt = self.run_writer()
        count = len(self.archive.records)
        self.assertEqual(self.archive.opens, 1)
        self.assertEqual(self.archive.checkpoint_calls, 0)
        self.assertEqual(receipt['scope'], 'finite_selection_only')
        self.assertFalse(receipt['goal_completion_claimed'])
        self.assertEqual(len(receipt['files']), 4)
        self.assertEqual(self.run_writer(), receipt)
        self.assertEqual(len(self.archive.records), count)
        self.assertEqual(self.archive.opens, 2)
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual((self.f.root / self.plan_input['path']).read_bytes(), input_plan)

    def test_checkpoint_missing_requires_explicit_permission_before_writes(self):
        count = len(self.archive.records); objects = dict(self.archive.objects)
        with self.assertRaisesRegex(v.Invalid, 'allow-checkpoint-derived-updates'): self.run_writer()
        self.assertEqual(len(self.archive.records), count)
        self.assertEqual(self.archive.objects, objects)
        self.assertFalse((self.f.run / 'FINAL_RECEIPT.json').exists())

    def test_create_language_event_and_allowed_standard_checkpoint(self):
        plan = copy.deepcopy(self.f.plan); plan['plain_language_review']['event_id'] = None
        self.req['plan_input'] = self.f.file('closure-input/NEW_PLAN_INPUT.json', plan)
        self.save_request()
        receipt = self.run_writer(allow=True)
        final_plan = v.strict((self.f.root / self.req['outputs']['final_plan']).read_bytes())
        eid = final_plan['plain_language_review']['event_id']
        event = next(e for e in self.archive.records if e['id'] == eid)
        self.assertEqual(event['kind'], 'research.selection.language_check')
        self.assertIsNone(v.strict((self.f.root / self.req['plan_input']['path']).read_bytes())['plain_language_review']['event_id'])
        self.assertEqual(self.archive.checkpoint_calls, 1)
        count = len(self.archive.records)
        self.assertEqual(self.run_writer(allow=True), receipt)
        self.assertEqual(self.archive.checkpoint_calls, 1)
        self.assertEqual(len(self.archive.records), count)

    def test_resume_after_committed_stage_prefix(self):
        self.add_checkpoint()
        self.archive.fail_after_key = self.f.run.name + ':bounded-stage:critique'
        with self.assertRaisesRegex(RuntimeError, 'committed prefix'): self.run_writer()
        self.assertFalse((self.f.run / 'FINAL_RECEIPT.json').exists())
        receipt = self.run_writer()
        stages = [e['payload']['stage'] for e in self.archive.records if e['kind'] == 'research.selection.stage']
        self.assertEqual(stages, list(v.STAGES))
        self.assertEqual(receipt['remaining_selection_work'], 0)
        lineages = [e for e in self.archive.records if e['kind'] == 'essay.lineage.entry' and e['payload']['entry']['id'].endswith(':final-selection-v1')]
        self.assertEqual(len(lineages), 22)

    def test_atomic_publication_before_and_after_link_failure(self):
        target = self.f.run / 'atomic' / 'artifact.json'
        with patch.object(closure.os, 'fsync', side_effect=OSError('synthetic fsync interruption')):
            with self.assertRaises(OSError): closure.save_once(target, b'complete bytes')
        self.assertFalse(target.exists())
        calls = []
        original_fsync = closure.os.fsync
        def second_fsync_fails(fd):
            calls.append(fd)
            if len(calls) == 2: raise OSError('synthetic directory fsync interruption')
            return original_fsync(fd)
        with patch.object(closure.os, 'fsync', side_effect=second_fsync_fails):
            with self.assertRaises(OSError): closure.save_once(target, b'complete bytes')
        self.assertEqual(target.read_bytes(), b'complete bytes')
        closure.save_once(target, b'complete bytes')
        with self.assertRaisesRegex(v.Invalid, 'preserved'):
            closure.save_once(target, b'different bytes')
        self.assertEqual(target.read_bytes(), b'complete bytes')

    def test_resume_repeats_checkpoint_after_terminal_but_before_api_return(self):
        failed = []
        def interrupted_api(*args, **kwargs):
            cp = checkpoint_api(*args, **kwargs)
            if not failed:
                failed.append(True)
                raise RuntimeError('synthetic derived refresh failed after terminal')
            return cp
        with self.assertRaisesRegex(RuntimeError, 'after terminal'):
            self.run_writer(allow=True, checkpoint=interrupted_api)
        self.assertFalse((self.f.run / 'FINAL_RECEIPT.json').exists())
        self.assertFalse(any(e['kind'] == 'research.selection.closure.checkpoint_api_returned' for e in self.archive.records))
        receipt = self.run_writer(allow=True, checkpoint=interrupted_api)
        self.assertEqual(self.archive.checkpoint_calls, 2)
        for kind in ('checkpoint', 'operation.interrupted', 'research.selection.closure.checkpoint_api_returned'):
            self.assertEqual(sum(e['kind'] == kind for e in self.archive.records), 1)
        marker = next(e for e in self.archive.records if e['kind'] == 'research.selection.closure.checkpoint_api_returned')
        self.assertIn(marker['id'], receipt['parent_event_ids'])

    def test_changed_request_cannot_replace_accepted_closure(self):
        self.add_checkpoint(); self.run_writer()
        before = (self.f.run / 'FINAL_RECEIPT.json').read_bytes(); count = len(self.archive.records)
        self.req['pending_goal_steps'] = []; self.save_request()
        with self.assertRaisesRegex(v.Invalid, 'delivery key conflict'): self.run_writer()
        self.assertEqual(len(self.archive.records), count)
        self.assertEqual((self.f.run / 'FINAL_RECEIPT.json').read_bytes(), before)

    def test_conflicting_local_output_is_preserved(self):
        self.add_checkpoint()
        path = self.f.root / self.req['outputs']['final_plan']; path.parent.mkdir(); path.write_bytes(b'old preserved content')
        with self.assertRaisesRegex(v.Invalid, 'Existing artifact differs'): self.run_writer()
        self.assertEqual(path.read_bytes(), b'old preserved content')
        self.assertFalse((self.f.run / 'FINAL_RECEIPT.json').exists())

    def test_fake_gate_or_missing_export_fails_before_event(self):
        self.add_checkpoint(); count = len(self.archive.records)
        self.req['selection_gate_event_ids'] = ['fake-event']; self.save_request()
        with self.assertRaisesRegex(v.Invalid, 'Missing actual canonical event'): self.run_writer()
        self.assertEqual(len(self.archive.records), count)
        self.req['selection_gate_event_ids'] = [self.gate['id']]
        self.req['export_files'] = [{'path': str((self.f.run / 'missing.txt').relative_to(self.f.root)), 'sha256': '0' * 64, 'bytes': 0}]
        self.save_request()
        with self.assertRaises(FileNotFoundError): self.run_writer()
        self.assertEqual(len(self.archive.records), count)

    def test_incompatible_checkpoint_is_not_rewritten(self):
        self.add_checkpoint(); count = len(self.archive.records)
        cp = next(e for e in self.archive.records if e['kind'] == 'checkpoint')
        cp['payload']['capture_status'] = 'BOUNDED_COMPLETE'
        with self.assertRaisesRegex(v.Invalid, 'checkpoint incompatible'): self.run_writer(allow=True)
        self.assertEqual(len(self.archive.records), count)
        self.assertEqual(cp['payload']['capture_status'], 'BOUNDED_COMPLETE')

    def real_synthetic_archive(self, existing_checkpoint):
        # All records/objects are placeholders generated by Fixture. Never opens
        # this repository's research/archive or any actual manuscript/review.
        if existing_checkpoint: self.add_checkpoint()
        bindings = {key: [] for key in ('method', 'instruction', 'config', 'input')}
        self.f.start['bindings'] = bindings
        start_artifact = self.f.file('START_RECEIPT.json', self.f.start)
        self.archive.objects[start_artifact['sha256']] = (self.f.root / start_artifact['path']).read_bytes()
        archive = Archive(self.f.root.resolve() / 'synthetic-archive-only').init()
        with archive.writer() as writer:
            for digest, data in self.archive.objects.items(): self.assertEqual(writer.put(data), digest)
            for old in self.archive.records:
                request = {k: copy.deepcopy(value) for k, value in old.items() if k not in ('delivery_key', 'request_sha256')}
                request['bindings'] = bindings
                request.setdefault('actor', {'id': 'synthetic-fixture', 'role': 'tool'})
                request.setdefault('operation_id', 'fixture-' + old['id'])
                request.setdefault('attempt_id', 'fixture-' + old['id'])
                writer.append(request, old.get('delivery_key', 'fixture:' + old['id']))
        return archive

    def test_real_archive_api_in_temporary_synthetic_directory(self):
        archive = self.real_synthetic_archive(existing_checkpoint=True)
        receipt = closure.execute(self.f.root, self.f.run, self.path, archive, lineage_api=essay_lineage)
        self.assertEqual(receipt['status'], 'SELECTION_COMPLETE_BOUNDED')
        count = len(archive.events())
        self.assertEqual(closure.execute(self.f.root, self.f.run, self.path, archive, lineage_api=essay_lineage), receipt)
        self.assertEqual(len(archive.events()), count)
        self.assertTrue(archive.validate()['ok'])

    def test_real_core_checkpoint_api_only_with_explicit_derived_flag(self):
        archive = self.real_synthetic_archive(existing_checkpoint=False)
        before = len(archive.events())
        with self.assertRaisesRegex(v.Invalid, 'allow-checkpoint-derived-updates'):
            closure.execute(self.f.root, self.f.run, self.path, archive, lineage_api=essay_lineage,
                            checkpoint_api=philosophy_round.checkpoint)
        self.assertEqual(len(archive.events()), before)
        # Exercise the real checkpoint event API; suppress only its unrelated
        # biography/knowledge renderers inside this disposable synthetic lab.
        with patch.object(essay_lineage, 'backfill') as backfill, patch.object(essay_lineage, 'render') as render, patch.object(philosophy_round, 'refresh') as refresh:
            receipt = closure.execute(self.f.root, self.f.run, self.path, archive, lineage_api=essay_lineage,
                                      checkpoint_api=philosophy_round.checkpoint, allow_checkpoint_derived_updates=True)
            self.assertEqual((backfill.call_count, render.call_count, refresh.call_count), (1, 1, 1))
            self.assertEqual(Path(backfill.call_args.args[0]), self.f.root.resolve())
        self.assertEqual(receipt['core_capture_status'], 'INCOMPLETE')
        cp = next(e for e in archive.events() if e['kind'] == 'checkpoint')
        self.assertEqual(cp['payload']['summary']['outcome'], 'CONTINUE')
        self.assertEqual(cp['payload']['purpose'], 'research')
        self.assertIn(self.f.gap['id'], cp['parents'])
        self.assertTrue(archive.validate()['ok'])


if __name__ == '__main__': unittest.main()
