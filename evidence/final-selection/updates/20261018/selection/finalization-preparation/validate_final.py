"""Read-only finite selection acceptance. Never chooses essays or writes archive events.

Paths in FINAL_PLAN are repository-relative, except pair_batches queue/input_receipt,
which are run-relative. Canonical events must come from an audited Archive snapshot.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re
import sys

IDS = frozenset('E009 E036 E047 E050 E055 E074 E078 E079 E100 E012 E037 E039 E041 E086 E098 F01 F02 F03 F04 F05 F06 S02'.split())
SETTINGS = {'model': 'gpt-6-astra', 'effort': 'ultra', 'service_tier': 'default'}
STAGES = ('question', 'sources', 'contribution', 'critique', 'decision')
ROLES = {'N1', 'N2', 'N3', 'J1', 'J2'}


class Invalid(ValueError):
    pass


def require(test, message):
    if not test:
        raise Invalid(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def encode(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')) + '\n').encode()


def strict(data):
    def pairs(items):
        out = {}
        for key, value in items:
            require(key not in out, 'Duplicate JSON key: ' + key)
            out[key] = value
        return out
    return json.loads(data, object_pairs_hook=pairs,
                      parse_constant=lambda x: (_ for _ in ()).throw(Invalid('Nonfinite JSON')))


def index_bytes(count=10):
    return ('# Тексты для чтения\n\n' + ''.join(
        f'{i}. [Текст {i:02d}]({i:02d}.md)\n' for i in range(1, count + 1))).encode()


class Check:
    def __init__(self, root, run_dir, events, get_object):
        self.root, self.run = Path(root).resolve(), Path(run_dir).resolve()
        require(self.run.is_relative_to(self.root), 'Run outside repository')
        self.events = {e['id']: e for e in events}
        require(len(self.events) == len(events), 'Duplicate canonical event ID')
        self.positions = {e['id']: i for i, e in enumerate(events)}
        self.get_object = get_object
        self.checked_files = {}

    def path(self, name, base=None):
        require(isinstance(name, str) and name and not Path(name).is_absolute(), 'Relative path required')
        base = Path(base or self.root).resolve()
        path = base / name
        require(path.resolve().is_relative_to(base), 'Path escapes its scope')
        require(not any(p.is_symlink() for p in [path, *path.parents] if p.is_relative_to(base)), 'Symlink input forbidden')
        return path

    def read(self, name, digest=None, base=None):
        path = self.path(name, base)
        data = path.read_bytes()
        actual = sha(data)
        require(digest is None or digest == actual, 'File changed: ' + name)
        self.checked_files[str(path.relative_to(self.root))] = actual
        return data

    def load(self, name, base=None):
        return strict(self.read(name, base=base))

    def obj(self, digest):
        require(isinstance(digest, str) and re.fullmatch('[0-9a-f]{64}', digest), 'Bad object hash')
        data = self.get_object(digest)
        require(sha(data) == digest, 'Canonical object hash mismatch')
        return data

    def event(self, eid, kind=None, allow_external_raw=False):
        require(eid in self.events, 'Missing actual canonical event: ' + str(eid))
        e = self.events[eid]
        lineage = e['kind'] == 'essay.lineage.entry' and e.get('run_id') == 'essay-lineage' and e['payload']['entry'].get('workflow') == self.run.name
        external_raw = allow_external_raw and e['kind'] == 'capture.raw_record'
        require(e.get('run_id') == self.run.name or lineage or external_raw, 'Event belongs to another run: ' + eid)
        require(kind is None or e['kind'] == kind, 'Wrong event kind: ' + eid)
        for parent in e.get('parents', []):
            require(parent in self.events and self.positions[parent] < self.positions[eid], 'Missing or forward archive dependency')
        if e['kind'] == 'essay.lineage.entry':
            digest = e['payload']['entry_sha256']
            require(digest in e['outputs'] and strict(self.obj(digest)) == e['payload']['entry'], 'Lineage object mismatch')
        return e

    def ancestors(self, eid):
        result, pending = set(), [eid]
        while pending:
            current = pending.pop()
            if current in result:
                continue
            require(current in self.events, 'Missing ancestor')
            result.add(current)
            for parent in self.events[current].get('parents', []):
                require(parent in self.events and self.positions[parent] < self.positions[current], 'Invalid event ordering')
                pending.append(parent)
        return result

    def bound(self, name, manifest, event):
        path = str(self.path(name, self.run).relative_to(self.root))
        matches = [r for r in manifest if r['path'] == path]
        require(len(matches) == 1, 'Input not uniquely frozen: ' + name)
        data = self.read(path, matches[0]['sha256'])
        require(sha(data) in event.get('outputs', []), 'Input missing from canonical event outputs')
        require(self.obj(sha(data)) == data, 'Frozen canonical bytes mismatch')
        return strict(data) if name.endswith('.json') else data

    def capture(self, receipt, review):
        digest = receipt['capture_sha256']
        require(digest == review['payload']['capture_sha256'] and digest in review['outputs'], 'Capture binding mismatch')
        cap = strict(self.obj(digest))
        require(cap['session_id'] == review['session_id'], 'Capture session mismatch')
        evidence = set(cap['evidence_events'])
        require(evidence and evidence <= set(review['parents']), 'Capture is not a review dependency')
        for eid in evidence:
            self.event(eid, allow_external_raw=True)
        selected = {r['line']: r for r in cap['selection']}
        require(len(selected) == len(cap['selection']) == len(cap['records']), 'Capture selection cardinality')
        for rec in cap['records']:
            row = selected[rec['line']]
            if rec['mode'] == 'exact-visible-fragment':
                ev = self.event(rec['event_id'], 'research.selection.visible_fragment.captured')
                require(ev['id'] in evidence and ev['session_id'] == cap['session_id'], 'Fragment evidence/session mismatch')
                require(ev['outputs'] == row['token_sha256'] == rec['token_sha256'], 'Fragment token binding')
                require(all(ev['payload'].get(k) == row[k] for k in ('line', 'record_sha256', 'role', 'phase', 'token_sha256')), 'Fragment metadata mismatch')
                for digest in rec['token_sha256']:
                    self.obj(digest)
            else:
                require(rec['mode'] == 'standard', 'Unknown capture mode')
                result = rec['capture']
                ev = self.event(result['coverage_event_id'], 'capture.coverage')
                require(ev['id'] in evidence and ev['payload']['status'] == 'BOUNDED_COMPLETE', 'Incomplete standard capture')
                require(strict(self.obj(ev['payload']['report_sha256'])) == {k: v for k, v in result.items() if k != 'coverage_event_id'}, 'Standard capture report mismatch')
                require(len(result['raw_event_ids']) == 1, 'Standard raw record count')
                raw = self.event(result['raw_event_ids'][0], 'capture.raw_record', allow_external_raw=True)
                require(raw['session_id'] == cap['session_id'] and raw['payload']['source_line'] == row['line'] and raw['payload']['raw_sha256'] == row['record_sha256'], 'Native capture mismatch')
                if raw['run_id'] != self.run.name:
                    require(any(self.events[e]['kind'] == 'capture.run_binding' and self.events[e]['run_id'] == self.run.name and raw['id'] in self.events[e]['parents'] for e in evidence), 'Reused native record lacks current-run binding')
                self.obj(row['record_sha256'])

    def review(self, job, start, mapping):
        jid = job['id']
        require(re.fullmatch('[A-Za-z0-9_-]+', jid), 'Unsafe job ID')
        require(all(job.get(k) == v for k, v in SETTINGS.items()), 'Wrong requested model/effort/tier')
        for field in ('prompt', 'schema'):
            self.read(job[field + '_file'], job[field + '_sha256'])
        receipt = self.load(f'results/{jid}/ARCHIVE_RECEIPT.json', self.run)
        require(receipt['status'] == 'REVIEW_ARCHIVED' and receipt['job_id'] == jid, 'Missing/quarantined review: ' + jid)
        ev = self.event(receipt['event_id'], 'research.selection.review.completed')
        p = ev['payload']
        require(p['status'] == 'REVIEW_ARCHIVED' and p['job_id'] == jid and p['phase'] == job['phase'], 'Accepted review identity mismatch')
        require(ev['bindings'] == start['bindings'] and receipt['input_event_id'] == start['event_id'] and start['event_id'] in ev['parents'], 'Review input lineage mismatch')
        require(receipt['session_id'] == ev['session_id'], 'Receipt/native session mismatch')
        require(receipt['files'] == p['files'] and p['files'], 'Output manifest mismatch')
        for f in p['files']:
            data = self.read(f['path'], f['sha256'])
            require(f['sha256'] in ev['outputs'] and self.obj(f['sha256']) == data, 'Review output not canonically retained')
        individual = job['phase'] == 'individual'
        cids = [c for c, x in mapping.items() if x['blind_id'] == job['manuscript_id']] if individual else job['pair_candidates']
        require(len(cids) == (1 if individual else 2) and len(set(cids)) == len(cids) and set(cids) <= IDS, 'Review candidate scope')
        if not individual:
            require(set(job['ordered_blind_ids']) == {mapping[c]['blind_id'] for c in cids}, 'Pair order scope')
            cids = sorted(cids, key=lambda c: job['ordered_blind_ids'].index(mapping[c]['blind_id']))
        versions = [{'candidate': c, 'blind_id': mapping[c]['blind_id'], 'entry_id': mapping[c]['assigned_entry'],
                     'sha256': mapping[c]['version']['sha256'], 'path': mapping[c]['version']['path'],
                     'entity': mapping[c]['entity'], 'assigned_event': mapping[c]['assigned_event']} for c in cids]
        require(p['versions'] == versions, 'Review assessed wrong version/order')
        require({v['assigned_event'] for v in versions} <= set(ev['parents']), 'Assigned version not a dependency')
        expected = job.get('expected_output') or {'review_id': jid, 'manuscript_id': job['manuscript_id'], 'profile_id': job['profile_id']}
        response = p['response']
        require(response.get('read_complete') is True and all(response.get(k) == v for k, v in expected.items()), 'Incomplete or misidentified accepted response')
        self.capture(receipt, ev)
        le = self.event(receipt['lineage_event_id'], 'essay.lineage.entry')
        entry = le['payload']['entry']
        require(entry['id'] == receipt['lineage_entry_id'] and entry['kind'] == 'evaluation' and ev['id'] in entry['evidence'], 'Evaluation lineage mismatch')
        require(entry['parents'] == [v['entry_id'] for v in versions], 'Evaluation lineage parents mismatch')
        ass = entry['assessment']
        require(ass['versions'] == [{'entry_id': v['entry_id'], 'sha256': v['sha256']} for v in versions], 'Assessment version mismatch')
        requested = {'profile_id': job['profile_id'], 'role': job['role'], **SETTINGS}
        require(ass['judge']['requested'] == requested and ass['prompt_sha256'] == job['prompt_sha256'], 'Assessment configuration mismatch')
        observed = ass['judge']['observed']
        require(observed and all(x.get('model') == SETTINGS['model'] and x.get('effort') == SETTINGS['effort'] and x.get('alternate_effort') in (None, SETTINGS['effort']) and x.get('service_tier') in (None, 'default') for x in observed), 'Observed model/effort/tier mismatch')
        rubric = job.get('rubric_sha256') if not individual else sha(self.read('RUBRIC.txt', base=self.run))
        require(ass['rubric_sha256'] == rubric and set([rubric, job['prompt_sha256']]) <= set(ev['inputs']), 'Review rubric binding mismatch')
        return {'job': job, 'event_id': ev['id'], 'lineage_event_id': le['id'], 'session_id': ev['session_id'], 'candidates': cids}


def validate(root, run_dir, plan, events, get_object):
    c = Check(root, run_dir, events, get_object)
    require(plan['schema'] == 'selection-final-plan.v1' and plan['run_id'] == c.run.name, 'Final plan identity')
    start = c.load('START_RECEIPT.json', c.run)
    require(start['status'] == 'SELECTION_INPUTS_ARCHIVED', 'Initial inputs not accepted')
    ready = c.event(start['event_id'], 'research.selection.ready')
    inputs = c.event(start['input_event_id'], 'research.selection.inputs.accepted')
    require(inputs['id'] in ready['parents'] and ready['bindings'] == inputs['bindings'] == start['bindings'], 'Initial ready/input binding mismatch')
    question = c.event(start['question_stage_event'], 'research.selection.stage')
    require(question['payload']['stage'] == 'question' and question['id'] in ready['parents'], 'Original question stage absent')
    gap = c.event(start['preserved_standard_capture_gap'], 'capture.coverage')
    require(gap['payload']['status'] == 'INCOMPLETE', 'Original adapter gap must remain INCOMPLETE')
    allocation = c.bound('ALLOCATION.json', start['files'], inputs)['rows']
    protected = c.bound('PROTECTED_VERSIONS.json', start['files'], inputs)['files']
    reading_order = c.bound('READING_ORDER.json', start['files'], inputs)['candidate_order']
    queue = c.bound('queue.json', start['files'], inputs)['jobs']
    c.bound('METHOD.json', start['files'], inputs)
    c.bound('RUBRIC.txt', start['files'], inputs)
    mapping_data = c.read('LINEAGE_INPUTS.json', base=c.run)
    require(sha(mapping_data) in ready['outputs'] and c.obj(sha(mapping_data)) == mapping_data, 'Assigned lineage map is not frozen')
    mapping = strict(mapping_data)
    rows = {r['candidate']: r for r in allocation}
    require(len(allocation) == len(rows) == 22 and set(rows) == set(mapping) == IDS, 'Exact 22 candidate IDs required')
    require(len({r['blind_id'] for r in allocation}) == 22, 'Blind IDs reused')
    for cid, row in rows.items():
        require(row['version'] == mapping[cid]['version'] and row['blind_id'] == mapping[cid]['blind_id'], 'Allocation/version map mismatch')
        v = row['version']; c.read(v['path'], v['sha256'])
        assigned = c.event(mapping[cid]['assigned_event'], 'essay.lineage.entry')['payload']['entry']
        require(assigned['id'] == mapping[cid]['assigned_entry'] and assigned['entity'] == mapping[cid]['entity'], 'Assigned entry identity mismatch')
        require(any(a['sha256'] == v['sha256'] and a['path'] == v['path'] for a in assigned['artifacts']), 'Assigned exact version missing')
    require(len(protected) == len({r['path'] for r in protected}) == 42, 'Exactly 42 protected files required')
    for f in protected:
        c.read(f['path'], f['sha256'])
    require(len(queue) == 110 and all(j['phase'] == 'individual' for j in queue), 'Exactly 110 individual jobs required')
    reviews = [c.review(j, start, mapping) for j in queue]
    for cid, row in rows.items():
        jobs = [r['job'] for r in reviews if r['candidates'] == [cid]]
        roles = [j['role'] for j in jobs]
        require(len(jobs) == 5 and set(roles) == ROLES, 'Individual 3N/2J coverage mismatch')
        require({j['profile_id'] for j in jobs if j['role'].startswith('J')} == set(row['profiles']) and len(set(row['profiles'])) == 2, 'Assigned profiles mismatch')
    individual_events = {r['event_id'] for r in reviews}
    pair_jobs, pair_sets, pair_ids = [], set(), set()
    for batch in plan['pair_batches']:
        bstart = c.load(batch['input_receipt'], c.run)
        require(bstart['status'] == 'SELECTION_INPUTS_ARCHIVED', 'Pair inputs not archived')
        br = c.event(bstart['event_id'], 'research.selection.ready')
        require(individual_events <= c.ancestors(br['id']), 'Pair inputs precede accepted individual evidence')
        require(start['event_id'] in c.ancestors(br['id']) and bstart['bindings'] == br['bindings'], 'Pair initial-input lineage mismatch')
        # Pair ready may bind the queue itself or depend on an inputs event that binds it.
        data = c.read(batch['queue'], base=c.run)
        digest = sha(data)
        rel = str(c.path(batch['queue'], c.run).relative_to(c.root))
        require(any(x['path'] == rel and x['sha256'] == digest for x in bstart['files']), 'Pair queue not frozen')
        require(any(digest in c.events[e].get('outputs', []) for e in c.ancestors(br['id'])) and c.obj(digest) == data, 'Pair queue not canonically bound')
        jobs = strict(data)['jobs']
        require(jobs and all(j['phase'] == 'pair' for j in jobs), 'Wrong pair queue phase')
        groups = {}
        for j in jobs:
            groups.setdefault(j['expected_output']['pair_id'], []).append(j)
            for k in ('prompt', 'schema', 'rubric'):
                require(any(f['path'] == j[k + '_file'] and f['sha256'] == j[k + '_sha256'] for f in bstart['files']), 'Pair input not frozen')
                c.read(j[k + '_file'], j[k + '_sha256'])
        for pid, group in groups.items():
            pair = frozenset(group[0]['pair_candidates'])
            require(pid not in pair_ids and pair not in pair_sets and len(pair) == 2, 'Duplicate pair across batches')
            pair_ids.add(pid); pair_sets.add(pair)
            require(len(group) == 5 and all(frozenset(j['pair_candidates']) == pair for j in group), 'Pair must have five jobs for exact same texts')
            roles = [j['role'] for j in group]
            require(set(roles) == ROLES, 'Pair 3N/2J coverage mismatch')
            named = [j for j in group if j['role'].startswith('J')]
            require(len({j['profile_id'] for j in named}) == 2 and named[0]['ordered_blind_ids'] == list(reversed(named[1]['ordered_blind_ids'])), 'Pair profile/order imbalance')
            first = [j['ordered_blind_ids'][0] for j in group]
            require(sorted(first.count(x) for x in set(first)) == [2, 3], 'Pair A/B assignment imbalance')
        pair_jobs += jobs
        reviews += [c.review(j, bstart, mapping) for j in jobs]
    require(len(pair_sets) <= 10 and len(pair_jobs) == 5 * len(pair_sets) <= 50, 'Pair ceiling exceeded')
    jobids = {r['job']['id'] for r in reviews}
    require(len(jobids) == len(reviews) == len({r['session_id'] for r in reviews}), 'Job or fresh session reused')
    archived_reviews = [e for e in c.events.values() if e.get('run_id') == c.run.name and e['kind'] in ('research.selection.review.completed', 'research.selection.review.quarantined')]
    require(len(archived_reviews) == len(reviews) and {e['id'] for e in archived_reviews} == {r['event_id'] for r in reviews}, 'Unaccounted or duplicate archived review attempt')
    result_dir = c.run / 'results'
    require({p.name for p in result_dir.iterdir() if p.is_dir()} == jobids, 'Unaccounted started result directory')
    for jid in jobids:
        require({p.name for p in (result_dir / jid).glob('attempt-*')} == {'attempt-001'}, 'Extra or missing attempt')
    decisions = plan['decisions']
    byid = {d['candidate_id']: d for d in decisions}
    require(len(decisions) == len(byid) == 22 and set(byid) == IDS, 'Decision register must contain exact 22 IDs')
    selections = [d['selection'] for d in decisions]
    require(selections.count('main') == 8 and selections.count('wildcard') == 2 and selections.count('outside') == 12, 'Exactly 8 main + 2 wildcard + 12 outside required')
    for cid, d in byid.items():
        require(d['version'] == rows[cid]['version'], 'Decision version metadata changed')
        reason = d['reason_ru']
        require(isinstance(reason, list) and 2 <= len(reason) <= 3 and all(isinstance(s, str) and len(s.strip()) >= 30 and len(re.findall('[А-Яа-яЁё]', s)) >= 15 and s.rstrip().endswith(('.', '!', '?')) for s in reason), 'Need 2–3 substantive Russian sentence fields')
        evidence = set(d['evidence_event_ids'])
        for eid in evidence:
            c.event(eid)
        cited = [r for r in reviews if r['event_id'] in evidence and cid in r['candidates']]
        require({'N', 'J'} <= {r['job']['role'][0] for r in cited if r['job']['phase'] == 'individual'}, 'Decision needs evidence from both individual blocks')
    selected = {d['candidate_id'] for d in decisions if d['selection'] != 'outside'}
    order = sorted(IDS, key=lambda cid: sha(('reading-order-v1:' + cid).encode()))
    require(reading_order == order, 'Precommitted reading order changed')
    expected = [cid for cid in order if cid in selected]
    reading = plan['reading']; directory = c.path(reading['directory'])
    require(directory.is_relative_to(c.run), 'Reading package outside run')
    entries = reading['entries']
    require([r['candidate_id'] for r in entries] == expected, 'Reading order or selection mismatch')
    require(len(entries) == 10, 'Reading package count')
    for i, row in enumerate(entries, 1):
        target = c.path(row['path'])
        require(target == directory / f'{i:02d}.md', 'Reading names must be neutral 01.md…10.md')
        v = rows[row['candidate_id']]['version']
        require(row['sha256'] == v['sha256'] and c.read(row['path'], row['sha256']) == c.read(v['path'], v['sha256']), 'Reading bytes changed')
    require(c.path(reading['index_file']) == directory / 'INDEX.md', 'Neutral reading index location required')
    require(c.read(reading['index_file']) == index_bytes(), 'Reading index must contain only neutral links')
    require({p.name for p in directory.iterdir()} == {'INDEX.md'} | {f'{i:02d}.md' for i in range(1, 11)}, 'Extra files/labels in reading directory')
    language = plan['plain_language_review']
    attestation_bytes = c.read(language['artifact']['path'], language['artifact']['sha256'])
    attestation = strict(attestation_bytes)
    require(attestation.get('decisions_sha256') == sha(encode(decisions)) and attestation.get('concrete_plain_ru_2_to_3_sentences_each') is True, 'Coordinator plain-language review missing or stale')
    lev = c.event(language['event_id'])
    require(language['artifact']['sha256'] in lev['outputs'] and c.obj(language['artifact']['sha256']) == attestation_bytes, 'Language review is not canonically bound')
    require({e for d in decisions for e in d['evidence_event_ids']} <= c.ancestors(lev['id']), 'Decisions were not bound after cited archive evidence')
    return {'status': 'FINAL_PACKAGE_VALIDATED_BOUNDED', 'run_id': c.run.name,
            'plan_canonical_sha256': sha(encode(plan)), 'decisions_sha256': sha(encode(decisions)), 'individual_reviews': 110, 'pairs': len(pair_sets),
            'pair_reviews': len(pair_jobs), 'selected': {'main': 8, 'wildcard': 2}, 'protected_unchanged': 42,
            'reading_order': expected, 'review_event_ids': [r['event_id'] for r in reviews],
            'review_lineage_event_ids': [r['lineage_event_id'] for r in reviews],
            'plain_language_event_id': lev['id'], 'initial_ready_event_id': ready['id'],
            'question_stage_event_id': start['question_stage_event'], 'preserved_gap_event_id': gap['id'],
            'bindings': start['bindings'], 'checked_files': c.checked_files,
            'boundary': 'Mechanical completeness and exact bytes verified; plain/concrete reasons are an explicit coordinator assertion. No philosophical winner or novelty certification. Original core INCOMPLETE gap preserved.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', required=True)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument('--run-dir', type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args()
    root = args.root.resolve()
    sys.path.insert(0, str(root / 'scripts'))
    from research_archive import Archive
    archive = Archive(root / 'research/archive')
    plan_bytes = Path(args.plan).read_bytes()
    plan = strict(plan_bytes)
    report = validate(root, args.run_dir, plan, archive.events(), archive.get)
    report['plan_sha256'] = sha(plan_bytes)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
