"""Explicit v4 final validator for exactly two canonical capacity replacements.

Static derivative of the frozen v2 validate function. Every original final-package
check remains, with two bound exceptions and separate failure accounting.
"""
from pathlib import Path
import argparse
import json
import re
import sys
from resolver_v2 import ROOT, RUN, JOBS, load_resolution
sys.path.insert(0, str(RUN / 'finalization-preparation'))
from validate_final import Check, Invalid, IDS, SETTINGS, ROLES, require, strict, encode, sha, index_bytes

def validate(root, run_dir, plan, events, get_object, *, map_receipt):
    events = list(events)
    resolution = load_resolution(root, run_dir, map_receipt, events, get_object)
    c = Check(root, run_dir, events, get_object)
    for item in resolution['evidence_files'] + [f for value in resolution['exceptions'].values() for f in value['failed_attempt']['files']]:
        c.read(item['path'], item['sha256'])
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
    require({x['accepted_attempt']['event_id'] for x in resolution['exceptions'].values()} <= {r['event_id'] for r in reviews}, 'Mapped replacement absent from110')
    require(not ({x['failed_attempt']['session_id'] for x in resolution['exceptions'].values()} & {r['session_id'] for r in reviews}), 'Failed SID reused as accepted review')
    failures = [e for e in c.events.values() if e.get('run_id') == c.run.name and e['kind'] == 'research.selection.transport_failure']
    require(len(failures)==2 and {e['id'] for e in failures} == {x['failed_attempt']['event_id'] for x in resolution['exceptions'].values()}, 'Unaccounted transport failure')
    for jid in jobids:
        allowed = {'attempt-001', 'attempt-002'} if jid in JOBS else {'attempt-001'}
        require({p.name for p in (result_dir / jid).glob('attempt-*')} == allowed, 'Extra or missing attempt')
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
    return {'status': 'FINAL_PACKAGE_VALIDATED_BOUNDED', 'validator': 'capacity-v4',
            'preserved_failed_attempts': 2, 'replacement_map_event_id': resolution['map_event_id'],
            'replacement_ready_event_ids': [x['ready_event_id'] for x in resolution['exceptions'].values()], 'failed_attempt_event_ids': [x['failed_attempt']['event_id'] for x in resolution['exceptions'].values()], 'run_id': c.run.name,
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
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--map-receipt', type=Path, required=True)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--run-dir', type=Path, default=RUN)
    args = parser.parse_args()
    sys.path.insert(0, str(args.root / 'scripts'))
    from research_archive import Archive
    archive = Archive(args.root / 'research/archive')
    report = validate(args.root, args.run_dir, strict(args.plan.read_bytes()), archive.events(), archive.get, map_receipt=args.map_receipt)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__': main()
