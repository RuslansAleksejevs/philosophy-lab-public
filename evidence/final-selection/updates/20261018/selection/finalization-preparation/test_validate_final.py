"""Synthetic-only acceptance tests: generated placeholder bytes, no real inputs."""
from pathlib import Path
import copy
import tempfile
import unittest

import validate_final as v
import finalize_scaffold as scaffold


class Fixture:
    def __init__(self, root):
        self.root = Path(root); self.run = self.root / 'runs' / 'synthetic-selection'
        self.run.mkdir(parents=True)
        self.events, self.objects, self.serial = [], {}, 0
        self.bindings = {'method': ['synthetic-bound-method']}
        self.mapping, self.allocation, self.jobs = {}, [], []
        self.gap = self.event('capture.coverage', payload={'status': 'INCOMPLETE'})
        for i, cid in enumerate(sorted(v.IDS), 1):
            art = self.file(f'texts/{cid}.txt', f'SYNTHETIC UTF8 {cid} — only fixture\r\n'.encode())
            version = {**art, 'current': True, 'variant': 'fixture'}
            entryid = f'{cid}:assigned'
            assigned = self.event('essay.lineage.entry', payload={'entry': {'id': entryid, 'entity': cid,
                                'kind': 'selection', 'artifacts': [art]}})
            self.mapping[cid] = {'blind_id': f'M{i:02d}', 'version': version, 'assigned_event': assigned['id'],
                                 'assigned_entry': entryid, 'entity': cid}
            self.allocation.append({'candidate': cid, 'blind_id': f'M{i:02d}', 'version': version, 'profiles': ['profile-a', 'profile-b']})
            for role in ('N1', 'N2', 'N3', 'J1', 'J2'):
                jid = f'M{i:02d}-{role}'
                prompt = self.file('packets/' + jid + '.txt', ('SYNTHETIC prompt ' + jid).encode())
                schema = self.file('schema.json', b'{"type":"object"}')
                self.jobs.append({'id': jid, 'phase': 'individual', 'manuscript_id': f'M{i:02d}', 'role': role,
                                  'profile_id': 'neutral' if role.startswith('N') else 'profile-' + ('a' if role == 'J1' else 'b'),
                                  **v.SETTINGS, 'prompt_file': prompt['path'], 'prompt_sha256': prompt['sha256'],
                                  'schema_file': schema['path'], 'schema_sha256': schema['sha256']})
        protected = [self.file(f'protected/{i}.txt', f'original fixture {i}'.encode()) for i in range(42)]
        order = sorted(v.IDS, key=lambda cid: v.sha(('reading-order-v1:' + cid).encode()))
        frozen = [self.file('ALLOCATION.json', {'rows': self.allocation}), self.file('PROTECTED_VERSIONS.json', {'files': protected}),
                  self.file('READING_ORDER.json', {'candidate_order': order}), self.file('queue.json', {'jobs': self.jobs}),
                  self.file('METHOD.json', {'synthetic': True}), self.file('RUBRIC.txt', b'SYNTHETIC neutral rubric')]
        inputs = self.event('research.selection.inputs.accepted', outputs=[x['sha256'] for x in frozen])
        self.question = self.event('research.selection.stage', parents=[inputs['id']], payload={'stage': 'question'})
        mapping = self.file('LINEAGE_INPUTS.json', self.mapping)
        self.ready = self.event('research.selection.ready', parents=[inputs['id'], self.question['id']], outputs=[mapping['sha256']])
        self.start = {'status': 'SELECTION_INPUTS_ARCHIVED', 'event_id': self.ready['id'], 'input_event_id': inputs['id'],
                      'question_stage_event': self.question['id'], 'preserved_standard_capture_gap': self.gap['id'],
                      'bindings': self.bindings, 'files': frozen}
        self.file('START_RECEIPT.json', self.start)
        self.reviews = [self.review(j, self.start) for j in self.jobs]
        decisions = []
        for i, cid in enumerate(sorted(v.IDS)):
            evidence = [r['event_id'] for r in self.reviews if r['candidate'] == cid]
            decisions.append({'candidate_id': cid, 'version': self.mapping[cid]['version'],
                              'selection': 'main' if i < 8 else 'wildcard' if i < 10 else 'outside',
                              'reason_ru': ['Это искусственный текст для проверки структуры итогового решения.',
                                            'Его содержание не является оценкой настоящего философского эссе.'],
                              'evidence_event_ids': evidence})
        selected = {d['candidate_id'] for d in decisions if d['selection'] != 'outside'}
        entries = []
        for i, cid in enumerate([cid for cid in order if cid in selected], 1):
            data = (self.root / self.mapping[cid]['version']['path']).read_bytes()
            entries.append({'candidate_id': cid, **self.file(f'reading/{i:02d}.md', data)})
        index = self.file('reading/INDEX.md', v.index_bytes())
        self.plan = {'schema': 'selection-final-plan.v1', 'run_id': self.run.name, 'decisions': decisions, 'pair_batches': [],
                     'reading': {'directory': str((self.run / 'reading').relative_to(self.root)), 'entries': entries, 'index_file': index['path']}}
        self.attest()

    def file(self, name, data):
        path = self.run / name
        path.parent.mkdir(parents=True, exist_ok=True)
        data = data if isinstance(data, bytes) else v.encode(data)
        path.write_bytes(data)
        digest = v.sha(data); self.objects[digest] = data
        return {'path': str(path.relative_to(self.root)), 'sha256': digest, 'bytes': len(data)}

    def event(self, kind, parents=None, outputs=None, payload=None, session='fixture-coordinator', inputs=None):
        self.serial += 1
        if kind == 'essay.lineage.entry':
            payload['entry']['workflow'] = self.run.name
            data = v.encode(payload['entry']); digest = v.sha(data); self.objects[digest] = data
            payload['entry_sha256'] = digest
            outputs = (outputs or []) + [digest]
        e = {'id': f'event-synthetic-{self.serial}', 'kind': kind, 'run_id': self.run.name, 'bindings': self.bindings,
             'parents': parents or [], 'outputs': outputs or [], 'inputs': inputs or [], 'payload': payload or {}, 'session_id': session}
        if kind == 'essay.lineage.entry': e['run_id'] = 'essay-lineage'
        self.events.append(e)
        return e

    def review(self, job, start):
        jid = job['id']; sid = 'fresh-' + jid
        if job['phase'] == 'individual':
            cids = [cid for cid, row in self.mapping.items() if row['blind_id'] == job['manuscript_id']]
            expected = {'review_id': jid, 'profile_id': job['profile_id'], 'manuscript_id': job['manuscript_id']}
        else:
            cids = sorted(job['pair_candidates'], key=lambda cid: job['ordered_blind_ids'].index(self.mapping[cid]['blind_id']))
            expected = job['expected_output']
        versions = [{'candidate': cid, 'blind_id': self.mapping[cid]['blind_id'], 'entry_id': self.mapping[cid]['assigned_entry'],
                     'sha256': self.mapping[cid]['version']['sha256'], 'path': self.mapping[cid]['version']['path'],
                     'entity': cid, 'assigned_event': self.mapping[cid]['assigned_event']} for cid in cids]
        output = self.file(f'results/{jid}/attempt-001/final.json', {**expected, 'read_complete': True})
        token = v.sha(b'"Synthetic visible final"'); self.objects[token] = b'"Synthetic visible final"'
        selection = {'line': 1, 'record_sha256': 'a' * 64, 'role': 'assistant', 'phase': 'final_answer', 'token_sha256': [token]}
        fragment = self.event('research.selection.visible_fragment.captured', parents=[start['event_id']], outputs=[token], payload=selection, session=sid)
        capture = {'session_id': sid, 'evidence_events': [fragment['id']], 'selection': [selection],
                   'records': [{'line': 1, 'mode': 'exact-visible-fragment', 'event_id': fragment['id'], 'token_sha256': [token]}]}
        capsha = v.sha(v.encode(capture)); self.objects[capsha] = v.encode(capture)
        rubric = job.get('rubric_sha256') or v.sha((self.run / 'RUBRIC.txt').read_bytes())
        ev = self.event('research.selection.review.completed', parents=[start['event_id'], fragment['id']] + [x['assigned_event'] for x in versions],
                        outputs=[output['sha256'], capsha], inputs=[job['prompt_sha256'], rubric], session=sid,
                        payload={'status': 'REVIEW_ARCHIVED', 'job_id': jid, 'phase': job['phase'], 'files': [output],
                                 'versions': versions, 'capture_sha256': capsha, 'response': {**expected, 'read_complete': True}})
        entryid = jid + ':evaluation'
        entry = {'id': entryid, 'kind': 'evaluation', 'parents': [x['entry_id'] for x in versions], 'evidence': [ev['id']],
                 'assessment': {'versions': [{'entry_id': x['entry_id'], 'sha256': x['sha256']} for x in versions],
                                'judge': {'requested': {'role': job['role'], 'profile_id': job['profile_id'], **v.SETTINGS},
                                          'observed': [{**v.SETTINGS, 'alternate_effort': None}]},
                                'prompt_sha256': job['prompt_sha256'], 'rubric_sha256': rubric}}
        le = self.event('essay.lineage.entry', parents=[ev['id']], payload={'entry': entry})
        self.file(f'results/{jid}/ARCHIVE_RECEIPT.json', {'status': 'REVIEW_ARCHIVED', 'job_id': jid, 'event_id': ev['id'],
                  'lineage_event_id': le['id'], 'lineage_entry_id': entryid, 'files': [output], 'capture_sha256': capsha,
                  'session_id': sid, 'input_event_id': start['event_id']})
        return {'event_id': ev['id'], 'candidate': cids[0], 'lineage_event_id': le['id']}

    def attest(self):
        artifact = self.file('PLAIN_LANGUAGE_CHECK.json', {'decisions_sha256': v.sha(v.encode(self.plan['decisions'])),
                             'concrete_plain_ru_2_to_3_sentences_each': True})
        ev = self.event('research.selection.language_check', parents=[r['event_id'] for r in self.reviews], outputs=[artifact['sha256']])
        self.plan['plain_language_review'] = {'artifact': artifact, 'event_id': ev['id']}

    def pair(self, pid='P01', cids=None):
        cids = cids or sorted(v.IDS)[:2]; mids = [self.mapping[x]['blind_id'] for x in cids]
        prefix = 'pairs/' + pid
        jobs, frozen = [], []
        for i, role in enumerate(('N1', 'N2', 'N3', 'J1', 'J2')):
            jid = pid + '-' + role
            prompt = self.file(prefix + '/' + jid + '.txt', b'SYNTHETIC pair prompt')
            schema = self.file(prefix + '/schema.json', {'type': 'object'})
            rubric = self.file(prefix + '/rubric.txt', b'SYNTHETIC pair rubric')
            frozen += [prompt, schema, rubric]
            job = {'id': jid, 'phase': 'pair', 'pair_candidates': cids, 'ordered_blind_ids': mids if i % 2 == 0 else mids[::-1],
                   'role': role, 'profile_id': role, **v.SETTINGS, 'expected_output': {'review_id': jid, 'pair_id': pid, 'profile_id': role}}
            for kind, art in [('prompt', prompt), ('schema', schema), ('rubric', rubric)]:
                job[kind + '_file'], job[kind + '_sha256'] = art['path'], art['sha256']
            jobs.append(job)
        queue = self.file(prefix + '/queue.json', {'jobs': jobs}); frozen.append(queue)
        ready = self.event('research.selection.ready', parents=[self.ready['id']] + [r['event_id'] for r in self.reviews], outputs=[x['sha256'] for x in frozen])
        start = {'status': 'SELECTION_INPUTS_ARCHIVED', 'event_id': ready['id'], 'bindings': self.bindings, 'files': frozen}
        self.file(prefix + '/START_RECEIPT.json', start)
        self.plan['pair_batches'].append({'queue': prefix + '/queue.json', 'input_receipt': prefix + '/START_RECEIPT.json'})
        self.reviews += [self.review(j, start) for j in jobs]
        return ready, jobs

    def validate(self):
        return v.validate(self.root, self.run, self.plan, self.events, self.objects.__getitem__)


class AcceptanceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.f = Fixture(self.temp.name)

    def test_complete_no_pairs(self):
        report = self.f.validate()
        self.assertEqual((report['individual_reviews'], report['pairs'], report['protected_unchanged']), (110, 0, 42))

    def test_complete_pair_and_immutable_initial_queue(self):
        before = (self.f.run / 'queue.json').read_bytes()
        self.f.pair()
        self.assertEqual(self.f.validate()['pair_reviews'], 5)
        self.assertEqual((self.f.run / 'queue.json').read_bytes(), before)

    def test_candidate_substitution(self):
        self.f.plan['decisions'][0]['candidate_id'] = 'E999'
        with self.assertRaisesRegex(v.Invalid, 'exact 22'): self.f.validate()

    def test_version_metadata_substitution(self):
        self.f.plan['decisions'][0]['version'] = {**self.f.plan['decisions'][0]['version'], 'variant': 'changed'}
        with self.assertRaisesRegex(v.Invalid, 'metadata changed'): self.f.validate()

    def test_reading_byte_mutation(self):
        p = self.f.root / self.f.plan['reading']['entries'][0]['path']; p.write_bytes(p.read_bytes().replace(b'\r\n', b'\n'))
        with self.assertRaisesRegex(v.Invalid, 'File changed'): self.f.validate()

    def test_reading_order_and_labels(self):
        self.f.plan['reading']['entries'].reverse()
        with self.assertRaisesRegex(v.Invalid, 'Reading order'): self.f.validate()
        self.f.plan['reading']['entries'].reverse()
        self.f.file('reading/INDEX.md', v.index_bytes() + b'Wildcard score: 5\n')
        with self.assertRaisesRegex(v.Invalid, 'only neutral'): self.f.validate()

    def test_protected_mutation(self):
        self.f.file('protected/0.txt', b'changed')
        with self.assertRaisesRegex(v.Invalid, 'File changed'): self.f.validate()

    def test_unaccepted_review_not_zero(self):
        p = self.f.run / 'results' / self.f.jobs[0]['id'] / 'ARCHIVE_RECEIPT.json'
        d = v.strict(p.read_bytes()); d['status'] = 'QUARANTINED_REVIEW_ARCHIVED_MISSING'; p.write_bytes(v.encode(d))
        with self.assertRaisesRegex(v.Invalid, 'quarantined'): self.f.validate()

    def test_local_receipt_cannot_invent_event(self):
        self.f.events = [e for e in self.f.events if e['id'] != self.f.reviews[0]['event_id']]
        with self.assertRaisesRegex(v.Invalid, 'Missing actual'): self.f.validate()

    def test_observed_config(self):
        lineage = next(e for e in self.f.events if e['id'] == self.f.reviews[0]['lineage_event_id'])
        lineage['payload']['entry']['assessment']['judge']['observed'][0]['model'] = 'substituted'
        data = v.encode(lineage['payload']['entry']); digest = v.sha(data); self.f.objects[digest] = data
        lineage['payload']['entry_sha256'] = digest; lineage['outputs'].append(digest)
        with self.assertRaisesRegex(v.Invalid, 'Observed model'): self.f.validate()

    def test_capture_token_corruption(self):
        digest = v.sha(b'"Synthetic visible final"'); self.f.objects[digest] = b'not original'
        with self.assertRaisesRegex(v.Invalid, 'object hash'): self.f.validate()

    def test_standard_capture_reused_raw_needs_run_binding(self):
        jid = self.f.jobs[0]['id']
        receipt_path = self.f.run / 'results' / jid / 'ARCHIVE_RECEIPT.json'
        receipt = v.strict(receipt_path.read_bytes())
        cap = v.strict(self.f.objects[receipt['capture_sha256']])
        raw = next(e for e in self.f.events if e['id'] == cap['records'][0]['event_id'])
        rawbytes = b'{"type":"synthetic-visible-message"}\n'
        rawsha = v.sha(rawbytes); self.f.objects[rawsha] = rawbytes
        raw.update(kind='capture.raw_record', run_id='codex:synthetic-session', outputs=[rawsha],
                   payload={'source_line': 1, 'raw_sha256': rawsha})
        binding = self.f.event('capture.run_binding', parents=[raw['id']])
        result = {'raw_event_ids': [raw['id']], 'status': 'BOUNDED_COMPLETE'}
        result_data = v.encode(result); result_sha = v.sha(result_data); self.f.objects[result_sha] = result_data
        coverage = self.f.event('capture.coverage', parents=[raw['id'], binding['id']], outputs=[result_sha],
                                payload={'status': 'BOUNDED_COMPLETE', 'report_sha256': result_sha})
        self.f.events.remove(binding); self.f.events.remove(coverage)
        position = self.f.events.index(raw) + 1
        self.f.events[position:position] = [binding, coverage]
        cap['selection'][0]['record_sha256'] = rawsha
        cap['records'] = [{'mode': 'standard', 'line': 1, 'capture': {**result, 'coverage_event_id': coverage['id']}}]
        cap['evidence_events'] = [raw['id'], binding['id'], coverage['id']]
        review = next(e for e in self.f.events if e['id'] == receipt['event_id'])
        review['parents'] += [binding['id'], coverage['id']]
        def bind_capture():
            data = v.encode(cap); digest = v.sha(data); self.f.objects[digest] = data
            review['payload']['capture_sha256'] = digest; review['outputs'].append(digest)
            receipt['capture_sha256'] = digest; receipt_path.write_bytes(v.encode(receipt))
        bind_capture()
        self.assertEqual(self.f.validate()['individual_reviews'], 110)
        cap['evidence_events'].remove(binding['id']); bind_capture()
        with self.assertRaisesRegex(v.Invalid, 'lacks current-run binding'): self.f.validate()

    def test_pair_requires_prior_110_events(self):
        ready, _ = self.f.pair(); ready['parents'].pop()
        with self.assertRaisesRegex(v.Invalid, 'precede accepted'): self.f.validate()

    def test_pair_limit_ten_and_duplicate_pair(self):
        ids = sorted(v.IDS)
        for i in range(10): self.f.pair(f'P{i+1:02d}', [ids[0], ids[i+1]])
        self.assertEqual(self.f.validate()['pair_reviews'], 50)
        self.f.pair('P11', [ids[0], ids[11]])
        with self.assertRaisesRegex(v.Invalid, 'ceiling'): self.f.validate()

    def test_duplicate_pair_across_immutable_batches(self):
        self.f.pair('P01'); self.f.pair('P02')
        with self.assertRaisesRegex(v.Invalid, 'Duplicate pair'): self.f.validate()

    def test_fresh_session_reuse(self):
        first, second = self.f.reviews[:2]
        sid = next(e['session_id'] for e in self.f.events if e['id'] == first['event_id'])
        other = next(e['session_id'] for e in self.f.events if e['id'] == second['event_id'])
        for e in self.f.events:
            if e['session_id'] == other: e['session_id'] = sid
        jid = self.f.jobs[1]['id']; path = self.f.run / 'results' / jid / 'ARCHIVE_RECEIPT.json'
        receipt = v.strict(path.read_bytes()); receipt['session_id'] = sid
        capture = v.strict(self.f.objects[receipt['capture_sha256']]); capture['session_id'] = sid
        data = v.encode(capture); newsha = v.sha(data); self.f.objects[newsha] = data
        ev = next(e for e in self.f.events if e['id'] == second['event_id'])
        ev['outputs'].append(newsha); ev['payload']['capture_sha256'] = newsha
        receipt['capture_sha256'] = newsha; path.write_bytes(v.encode(receipt))
        with self.assertRaisesRegex(v.Invalid, 'fresh session reused'): self.f.validate()

    def test_external_run_and_path_escape(self):
        self.f.plan['plain_language_review']['artifact']['path'] = '../outside.json'
        with self.assertRaisesRegex(v.Invalid, 'Path escapes'): self.f.validate()

    def test_extra_attempt_is_preserved_blocker(self):
        (self.f.run / 'results' / self.f.jobs[0]['id'] / 'attempt-002').mkdir()
        with self.assertRaisesRegex(v.Invalid, 'Extra or missing attempt'): self.f.validate()

    def test_ratio_and_short_reasons(self):
        self.f.plan['decisions'][0]['selection'] = 'wildcard'
        with self.assertRaisesRegex(v.Invalid, '8 main'): self.f.validate()
        self.f.plan['decisions'][0]['selection'] = 'main'
        self.f.plan['decisions'][0]['reason_ru'] = ['Хорошо.', 'Нравится.']
        with self.assertRaisesRegex(v.Invalid, 'Russian sentence'): self.f.validate()

    def test_plain_check_cannot_be_stale(self):
        self.f.plan['decisions'][0]['reason_ru'][0] += ' Новая отдельная мысль.'
        with self.assertRaisesRegex(v.Invalid, 'stale'): self.f.validate()

    def test_both_review_blocks_required(self):
        self.f.plan['decisions'][0]['evidence_event_ids'] = self.f.plan['decisions'][0]['evidence_event_ids'][:3]
        with self.assertRaisesRegex(v.Invalid, 'both individual'): self.f.validate()

    def test_scaffold_preserves_gap_and_requires_actual_stages(self):
        report = self.f.validate(); c = v.Check(self.f.root, self.f.run, self.f.events, self.f.objects.__getitem__)
        artifact = self.f.file('source-summary.txt', b'SYNTHETIC administrative artifact')
        request = scaffold.stage_request(c, report, 'sources', 'fixture-coordinator', [artifact], report['review_event_ids'])
        self.assertEqual(request['event']['kind'], 'research.selection.stage')
        self.assertEqual(request['event']['parents'][0], self.f.question['id'])
        with self.assertRaisesRegex(v.Invalid, 'Stage order'):
            scaffold.stage_request(c, report, 'decision', 'fixture-coordinator', [artifact], report['review_event_ids'])
        plan_artifact = self.f.file('FINAL_PLAN.json', self.f.plan)
        validation_artifact = self.f.file('FINAL_VALIDATION.json', report)
        with self.assertRaisesRegex(v.Invalid, 'Exactly five'):
            scaffold.final_request(c, report, 'fixture-coordinator', plan_artifact, validation_artifact, {}, self.f.gap['id'], [])

    def test_export_manifest_missing_local_file(self):
        c = v.Check(self.f.root, self.f.run, self.f.events, self.f.objects.__getitem__)
        artifact = self.f.file('export/accepted.txt', b'SYNTHETIC export')
        (self.f.root / artifact['path']).unlink()
        with self.assertRaisesRegex(v.Invalid, 'local file or stored object missing'):
            scaffold.checked_export_files(c, [artifact])

    def test_export_manifest_wrong_hash_or_length(self):
        c = v.Check(self.f.root, self.f.run, self.f.events, self.f.objects.__getitem__)
        artifact = self.f.file('export/accepted.txt', b'SYNTHETIC export')
        with self.assertRaisesRegex(v.Invalid, 'File changed'):
            scaffold.checked_export_files(c, [{**artifact, 'sha256': '0' * 64}])
        with self.assertRaisesRegex(v.Invalid, 'bytes differ'):
            scaffold.checked_export_files(c, [{**artifact, 'bytes': artifact['bytes'] + 1}])

    def test_export_manifest_missing_or_fake_stored_object(self):
        c = v.Check(self.f.root, self.f.run, self.f.events, self.f.objects.__getitem__)
        artifact = self.f.file('export/accepted.txt', b'SYNTHETIC export')
        del self.f.objects[artifact['sha256']]
        with self.assertRaisesRegex(v.Invalid, 'stored object missing'):
            scaffold.checked_export_files(c, [artifact])
        self.f.objects[artifact['sha256']] = b'counterfeit stored bytes'
        with self.assertRaisesRegex(v.Invalid, 'object hash mismatch'):
            scaffold.checked_export_files(c, [artifact])

    def test_export_manifest_does_not_scan_run(self):
        c = v.Check(self.f.root, self.f.run, self.f.events, self.f.objects.__getitem__)
        allowed = self.f.file('export/accepted.txt', b'SYNTHETIC accepted')
        self.f.file('export/private-unlisted.txt', b'SYNTHETIC unlisted')
        self.assertEqual(scaffold.checked_export_files(c, [allowed]), [allowed])
        with self.assertRaisesRegex(v.Invalid, 'Duplicate export path'):
            scaffold.checked_export_files(c, [allowed, allowed])

    def test_full_finite_acceptance_and_preserved_core_gap(self):
        report = self.f.validate()
        plan_artifact = self.f.file('FINAL_PLAN.json', self.f.plan)
        validation_artifact = self.f.file('FINAL_VALIDATION.json', report)
        def checker(): return v.Check(self.f.root, self.f.run, self.f.events, self.f.objects.__getitem__)
        for stage in v.STAGES[1:]:
            art = self.f.file('stages/' + stage + '.txt', ('SYNTHETIC stage ' + stage).encode())
            artifacts = [art] + ([plan_artifact] if stage == 'decision' else [])
            req = scaffold.stage_request(checker(), report, stage, 'fixture-coordinator', artifacts, report['review_event_ids'])['event']
            decision_event = self.f.event(req['kind'], parents=req['parents'], outputs=req['outputs'], payload=req['payload'])
        lineages = {}
        for d in self.f.plan['decisions']:
            cid = d['candidate_id']
            review_parents = [next(e['payload']['entry']['id'] for e in self.f.events if e['id'] == r['lineage_event_id']) for r in self.f.reviews if r['candidate'] == cid]
            entry = {'id': cid + ':final-selection', 'kind': 'selection', 'entity': cid,
                     'parents': [self.f.mapping[cid]['assigned_entry']] + review_parents, 'evidence': [decision_event['id']],
                     'artifacts': [self.f.mapping[cid]['version']], 'decision': {'action': d['selection'], 'reason': d['reason_ru']}}
            event = self.f.event('essay.lineage.entry', parents=[decision_event['id']], payload={'entry': entry})
            lineages[cid] = event['id']
        cp = self.f.event('checkpoint', parents=[self.f.gap['id']], payload={'capture_status': 'INCOMPLETE', 'truth_status': 'NOT_CERTIFIED'})
        gate = self.f.event('research.selection.completion_gates', parents=[decision_event['id']], payload={'synthetic': True})
        export_files = [plan_artifact, validation_artifact, {k: self.f.plan['reading']['entries'][0][k] for k in ('path', 'sha256', 'bytes')}]
        def final_request(**kwargs):
            return scaffold.final_request(checker(), report, 'fixture-coordinator', plan_artifact, validation_artifact, lineages, cp['id'], [gate['id']], files=export_files, **kwargs)
        request = final_request()
        req = request['event']
        end = self.f.event(req['kind'], parents=req['parents'], outputs=req['outputs'], payload=req['payload'])
        receipt = scaffold.receipt_from_actual_event(checker(), end['id'])
        self.assertEqual(receipt['status'], 'SELECTION_COMPLETE_BOUNDED')
        self.assertEqual(receipt['core_capture_status'], 'INCOMPLETE')
        self.assertEqual(receipt['scope'], 'finite_selection_only')
        self.assertEqual(receipt['remaining_selection_work'], 0)
        self.assertNotIn('remaining_requested_work', receipt)
        self.assertFalse(receipt['goal_completion_claimed'])
        self.assertEqual(receipt['pending_goal_steps'], ['project_state_update', 'private_github_update', 'collector_restore'])
        self.assertEqual(receipt['files'], export_files)
        self.assertTrue({f['sha256'] for f in export_files} <= set(end['outputs']))
        self.assertEqual(final_request(pending_goal_steps=['private_github_update'])['event']['payload']['pending_goal_steps'], ['private_github_update'])
        self.assertFalse(final_request(pending_goal_steps=[])['event']['payload']['goal_completion_claimed'])
        with self.assertRaisesRegex(v.Invalid, 'actual selection acceptance gate'):
            scaffold.final_request(checker(), report, 'fixture-coordinator', plan_artifact, validation_artifact, lineages, cp['id'], [])
        with self.assertRaisesRegex(v.Invalid, 'Missing actual canonical event'):
            scaffold.final_request(checker(), report, 'fixture-coordinator', plan_artifact, validation_artifact, lineages, cp['id'], ['fake-github-event'])
        removed = export_files[-1]['sha256']; end['outputs'].remove(removed)
        with self.assertRaisesRegex(v.Invalid, 'not bound by actual final event outputs'):
            scaffold.receipt_from_actual_event(checker(), end['id'])
        end['outputs'].append(removed)
        cp['payload']['capture_status'] = 'BOUNDED_COMPLETE'
        with self.assertRaisesRegex(v.Invalid, 'gap must remain'):
            scaffold.final_request(checker(), report, 'fixture-coordinator', plan_artifact, validation_artifact, lineages, cp['id'], [gate['id']])


if __name__ == '__main__':
    unittest.main()
