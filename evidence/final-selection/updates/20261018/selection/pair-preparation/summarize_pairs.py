"""Mechanical pair summary from complete accepted local evidence; no archive API.

Uses the frozen runner's input gate/schema validator and existing summary's safe
file/JSON readers. Native logs are not reopened. Canonical event IDs are reported,
not independently audited here. No pair selection, ranking or new verdict.
"""
from pathlib import Path
from collections import Counter
import argparse
import importlib.util
import json
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
RUN = HERE.parent


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec); spec.loader.exec_module(value)
    return value


R = module('pair_summary_frozen_runner', RUN / 'runner.py')
S = module('pair_summary_file_checks', RUN / 'summary-preparation/summarize_reviews.py')
need, read, load, strict, digest = S.need, S.read, S.load, S.strict, S.digest
ROLES = ('N1', 'N2', 'N3', 'J1', 'J2')
BOUNDARY = 'Local accepted receipts and exact bound bytes verified; canonical events referenced, not re-audited. Every response retained. Counts describe recorded verdicts only; no ranking, pair choice or selection.'


def descriptor(path, root):
    data = read(path, root)
    return {'path': str(Path(path).relative_to(root)), 'sha256': digest(data), 'bytes': len(data)}


def inputs(run, queue_file, input_receipt):
    root = run.parents[1]
    queue_path = R.run_file(queue_file, run); receipt_path = R.run_file(input_receipt, run)
    need(queue_path.parent == receipt_path.parent and queue_path.name == 'queue.json', 'Use one exact pair batch queue/input receipt')
    start, jobs = R.gate(run, root, str(queue_path), str(receipt_path))
    queue = load(queue_path, root)
    need(start.get('phase') == 'pair' and start.get('batch_id') == queue.get('batch_id') and queue.get('run_id') == run.name, 'Pair batch identity mismatch')
    need(5 <= len(jobs) <= 50 and len(jobs) % 5 == 0, 'One batch requires 1..10 complete pairs')
    frozen = {x['path']: x for x in start['files']}
    def bound(path, expected=None):
        ref = descriptor(path, root); recorded = frozen.get(ref['path'])
        need(recorded and recorded['sha256'] == ref['sha256'] and ('bytes' not in recorded or recorded['bytes'] == ref['bytes']), 'Input not frozen or changed: ' + path.name)
        need(expected is None or expected == ref['sha256'], 'Assigned input hash differs')
        return ref
    allocation_path = run / 'ALLOCATION.json'; bound(allocation_path)
    allocation = load(allocation_path, root)['rows']
    candidates = {x['candidate']: x['blind_id'] for x in allocation}
    need(len(candidates) == len(allocation) == len(set(candidates.values())), 'Ambiguous candidate/blind mapping')
    groups = {}; schemas = {}; prompts = set(); pair_keys = set()
    for job in jobs:
        pid, role = job.get('pair_id'), job.get('role')
        need(job.get('phase') == 'pair' and role in ROLES and isinstance(pid, str) and job['id'] == pid + '-' + role, 'Pair job identity differs')
        need(job['expected_output'] == {'review_id': job['id'], 'pair_id': pid, 'profile_id': job['profile_id']}, 'Expected output identity differs')
        need((job['model'], job['effort'], job['service_tier']) == ('gpt-6-astra', 'ultra', 'default'), 'Pair configuration changed')
        pair = job['pair_candidates']; order = job['ordered_blind_ids']
        need(isinstance(pair, list) and len(pair) == len(set(pair)) == 2 and set(pair) <= candidates.keys(), 'Unknown/duplicate pair candidates')
        need(isinstance(order, list) and len(order) == 2 and set(order) == {candidates[c] for c in pair}, 'A/B order does not match pair candidates')
        need(job['prompt_file'] not in prompts, 'Prompt reused by another pair job'); prompts.add(job['prompt_file'])
        for field in ('prompt', 'schema', 'rubric'):
            bound(root / job[field + '_file'], job[field + '_sha256'])
        schemas[job['id']] = load(root / job['schema_file'], root)
        groups.setdefault(pid, []).append(job)
    for pid, members in groups.items():
        need(len(members) == 5 and {j['role'] for j in members} == set(ROLES), 'Each pair needs exactly three neutral and two profile reviews')
        pair = members[0]['pair_candidates']; key = tuple(sorted(pair))
        need(key not in pair_keys and all(j['pair_candidates'] == pair for j in members), 'Duplicate pair or inconsistent candidate set'); pair_keys.add(key)
        by_role = {j['role']: j for j in members}
        need(all(by_role[r]['profile_id'] == 'neutral' for r in ROLES[:3]), 'Neutral profile identity changed')
        profiles = [by_role[r]['profile_id'] for r in ROLES[3:]]
        need(len(set(profiles)) == 2 and all(isinstance(p, str) and p and p != 'neutral' for p in profiles), 'Two distinct profile identities required')
        need(sum(j['ordered_blind_ids'][0] == candidates[pair[0]] for j in members) in (2, 3), 'Unbalanced A/B order')
        need(by_role['J1']['ordered_blind_ids'][0] != by_role['J2']['ordered_blind_ids'][0], 'Profile A/B order must be opposite')
    return root, start, jobs, groups, candidates, schemas, {'queue': descriptor(queue_path, root), 'input_receipt': descriptor(receipt_path, root), 'allocation': descriptor(allocation_path, root)}


def verify_job(job, start, schema, run, root):
    lane = run / 'results' / job['id']; attempt = lane / 'attempt-001'
    need({p.name for p in lane.glob('attempt-*')} == {'attempt-001'}, 'Only the accepted ordinary attempt-001 is supported')
    archive_path = lane / 'ARCHIVE_RECEIPT.json'; archive = load(archive_path, root)
    need(archive.get('status') == 'REVIEW_ARCHIVED' and archive.get('capture_status') == 'BOUNDED_VISIBLE_CAPTURE_ACCEPTED', 'Pair review/capture is not accepted')
    need(archive.get('job_id') == job['id'] and archive.get('input_event_id') == start['event_id'] and archive.get('accepted_attempt', 1) == 1, 'Accepted pair identity/input differs')
    for key in ('event_id', 'lineage_event_id', 'lineage_entry_id', 'session_id'):
        need(isinstance(archive.get(key), str) and archive[key], 'Missing accepted evidence reference: ' + key)
    need(archive['lineage_entry_id'] == run.name + ':' + job['id'] + ':evaluation-v1', 'Pair lineage identity differs')
    bound = {}
    for ref in archive['files']:
        path = root / ref['path']; need(path.parent == attempt and path not in bound, 'Duplicate/wrong-attempt archive file')
        exact = descriptor(path, root)
        need(ref['sha256'] == exact['sha256'] and ref['bytes'] == exact['bytes'], 'Archived pair evidence changed: ' + path.name)
        bound[path] = exact
    required = {'receipt.json', 'response.json', 'final.txt', 'native-check.json', 'native-visible.json', 'launch.json', 'stderr.json', 'visible-events.jsonl'}
    need(set(attempt.iterdir()) == set(bound) and required <= {p.name for p in bound}, 'Missing/extra/unbound attempt files')
    local = load(attempt / 'receipt.json', root)
    need(local.get('status') == R.COMPLETE and local.get('job_id') == job['id'] and local.get('session_id') == archive['session_id'], 'Local completion differs')
    need(local.get('quality_flags') == [] and local.get('visible_final_count') == 1, 'Unresolved local quality/final-count flags')
    for recorded, requested in (('prompt_sha256', 'prompt_sha256'), ('schema_sha256', 'schema_sha256'), ('requested_model', 'model'), ('requested_effort', 'effort'), ('requested_service_tier', 'service_tier')):
        need(local.get(recorded) == job[requested], 'Local configuration/input differs')
    need(local.get('outputs') == {r['path']: r['sha256'] for p, r in bound.items() if p.name != 'receipt.json'}, 'Local/archive file manifests differ')
    proof = load(attempt / 'native-check.json', root)
    need(proof.get('session_id') == archive['session_id'] and proof.get('prompt_sha256') == job['prompt_sha256'], 'Native identity/input differs')
    need(all(proof.get(k) == [] for k in ('isolation_failures', 'tool_calls', 'other_user_metadata')), 'Native isolation/tool gap')
    need(len(proof.get('prompt_lines', [])) == len(proof.get('final_lines', [])) == 1, 'Native prompt/final coverage gap')
    observed = proof.get('configurations')
    need(isinstance(observed, list) and observed and all(x.get('model') == job['model'] and x.get('effort') == job['effort'] and x.get('service_tier') in (None, job['service_tier']) for x in observed), 'Observed model/effort/tier differs')
    capture_ref = descriptor(lane / 'CAPTURE_RECEIPT.json', root)
    need(capture_ref['sha256'] == archive.get('capture_sha256'), 'Capture receipt changed')
    capture = load(lane / 'CAPTURE_RECEIPT.json', root)
    need(capture.get('status') == 'BOUNDED_VISIBLE_CAPTURE_ACCEPTED' and capture.get('session_id') == archive['session_id'] and capture.get('evidence_events'), 'Bounded capture not accepted')
    response = load(attempt / 'response.json', root); R.validate(response, schema)
    need(response.get('read_complete') is True, 'Incomplete pair reading')
    need(all(type(response.get(k)) is type(v) and response[k] == v for k, v in job['expected_output'].items()), 'Pair response identity differs')
    need(response == load(attempt / 'final.txt', root), 'Response/final mismatch')
    need(2 <= len(response['reason_ru']) <= 3 and all(x.strip() for x in response['reason_ru']), 'Empty pair rationale')
    evidence = {'archive_receipt': descriptor(archive_path, root), 'capture_receipt': capture_ref,
                'response': bound[attempt / 'response.json'], 'final': bound[attempt / 'final.txt'], 'local_receipt': bound[attempt / 'receipt.json'],
                **{k: archive[k] for k in ('event_id', 'lineage_event_id', 'lineage_entry_id', 'session_id')}, 'capture_event_ids': capture['evidence_events']}
    return response, evidence


def summarize(run, queue_file, input_receipt):
    run = Path(run).absolute()
    try:
        root, start, jobs, groups, candidates, schemas, sources = inputs(run, queue_file, input_receipt)
    except (ValueError, KeyError, TypeError, OSError) as exc:
        return {'status': 'INVALID_INPUTS_COVERAGE_ONLY', 'summary_generated': False, 'errors': [str(exc)], 'boundary': BOUNDARY}, None, None
    coverage = []; accepted = {}; sessions = set(); review_events = set()
    for job in jobs:
        try:
            response, evidence = verify_job(job, start, schemas[job['id']], run, root)
            need(evidence['session_id'] not in sessions and evidence['event_id'] not in review_events, 'Duplicate accepted session/review event')
            sessions.add(evidence['session_id']); review_events.add(evidence['event_id'])
            accepted[job['id']] = (response, evidence)
            coverage.append({'job_id': job['id'], 'status': 'ACCEPTED_VERIFIED'})
        except (ValueError, KeyError, TypeError, OSError) as exc:
            coverage.append({'job_id': job['id'], 'status': 'UNACCEPTED_OR_INVALID', 'errors': [str(exc)]})
    complete = len(accepted) == len(jobs)
    report = {'status': 'COMPLETE_PAIR_BATCH_ACCEPTED' if complete else 'INCOMPLETE_COVERAGE_ONLY', 'summary_generated': complete,
              'batch_id': start['batch_id'], 'expected_reviews': len(jobs), 'accepted_reviews': len(accepted), 'missing_reviews': len(jobs) - len(accepted),
              'input_event_id': start['event_id'], 'sources': sources, 'jobs': coverage, 'boundary': BOUNDARY}
    if not complete: return report, None, None
    rows = []; file_rows = []
    for pid, members in groups.items():
        pair = members[0]['pair_candidates']; counts = {group: {**{c: 0 for c in pair}, 'tie': 0, 'neither': 0} for group in ('neutral', 'profile')}
        reviews = []; files = []
        for job in sorted(members, key=lambda j: ROLES.index(j['role'])):
            response, evidence = accepted[job['id']]
            labels = {label: {'blind_id': blind, 'candidate_id': next(c for c in pair if candidates[c] == blind)} for label, blind in zip(('A', 'B'), job['ordered_blind_ids'])}
            raw = response['verdict']; mapped = labels[raw]['candidate_id'] if raw in ('A', 'B') else raw
            counts['neutral' if job['role'].startswith('N') else 'profile'][mapped] += 1
            reviews.append({'job_id': job['id'], 'role': job['role'], 'profile_id': job['profile_id'], 'labels': labels,
                            'recorded_verdict': raw, 'mapped_verdict': mapped, 'response': response, 'evidence': evidence})
            files.append({'job_id': job['id'], 'role': job['role'], 'profile_id': job['profile_id'], 'labels': labels,
                          **{key: evidence[key] for key in ('response', 'final', 'archive_receipt')}})
        total = {key: counts['neutral'][key] + counts['profile'][key] for key in counts['neutral']}
        rows.append({'pair_id': pid, 'candidate_ids': pair, 'neutral_reviews': 3, 'profile_reviews': 2,
                     'recorded_verdict_counts': {**counts, 'total': total}, 'different_recorded_verdicts': len({r['mapped_verdict'] for r in reviews}) > 1, 'reviews': reviews})
        file_rows.append({'pair_id': pid, 'candidate_ids': pair, 'full_response_files': files})
    summary = {'status': 'COMPLETE_PAIR_DESCRIPTIVE_SUMMARY', 'batch_id': start['batch_id'], 'pair_count': len(groups), 'review_count': len(jobs),
               'neutral_reviews': len(groups) * 3, 'profile_reviews': len(groups) * 2, 'input_event_id': start['event_id'], 'sources': sources,
               'order': 'Frozen queue first-pair order; roles N1,N2,N3,J1,J2. No ranking.', 'rows': rows, 'boundary': BOUNDARY}
    index = {'status': 'COMPLETE_PAIR_RESPONSE_FILE_LIST', 'batch_id': start['batch_id'], 'input_event_id': start['event_id'], 'pairs': file_rows}
    return report, summary, index


def write_outputs(output, run, report, summary, index):
    output, run = Path(output).absolute(), Path(run).absolute()
    need(output.is_relative_to(run) and '..' not in output.parts and not any(p.is_symlink() for p in (output, *output.parents)) and not output.exists(), 'Use a new safe output directory inside selection run')
    need((summary is None) == (index is None) and bool(report['summary_generated']) == (summary is not None), 'Partial summary cannot be emitted')
    output.mkdir(parents=True)
    values = {'coverage.json': report}
    if summary is not None: values.update({'summary.json': summary, 'pair-response-files.json': index})
    for name, value in values.items():
        with (output / name).open('xb') as stream: stream.write(R.encode(value))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-dir', type=Path, default=RUN)
    parser.add_argument('--queue', required=True)
    parser.add_argument('--input-receipt', required=True)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args(); result = summarize(args.run_dir, args.queue, args.input_receipt)
    write_outputs(args.output, args.run_dir, *result)
    print(json.dumps({k: result[0][k] for k in ('status', 'summary_generated', 'accepted_reviews', 'expected_reviews') if k in result[0]}))
    if not result[0]['summary_generated']: raise SystemExit(2)


if __name__ == '__main__': main()
