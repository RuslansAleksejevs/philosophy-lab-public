"""Exact finite checks for F02 author repair; no random sampling or external input."""
from fractions import Fraction as F
from itertools import product
from collections import defaultdict
from pathlib import Path
import json


def base_model(shared_condition=False):
    rows = []
    for x, source, sound, report in product((0, 1), ('A', 'B'), (0, 1), (0, 1)):
        pa = F(4, 5) if sound else F(1, 5)
        if source == 'A' or shared_condition:
            pr = F(int(report == x)) if sound else F(1, 2)
        else:
            pr = F(9, 10) if report == x else F(1, 10)
        weight = F(1, 2) * F(1, 2) * pa * pr
        if weight:
            rows.append({'x': x, 'source': source, 'sound': sound,
                         'report': report, 'weight': weight})
    assert sum(row['weight'] for row in rows) == 1
    return rows


def posterior(rows, keys):
    masses, positives = defaultdict(F), defaultdict(F)
    for row in rows:
        key = tuple(row[k] for k in keys)
        masses[key] += row['weight']
        positives[key] += row['weight'] * row['x']
    return {key: positives[key] / mass for key, mass in masses.items()}


def loss(rows, keys):
    post = posterior(rows, keys)
    return sum(row['weight'] * (post[tuple(row[k] for k in keys)] - row['x'])**2
               for row in rows)


def event_probability(rows, event, condition):
    subset = [row for row in rows if condition(row)]
    return (sum(row['weight'] for row in subset if event(row)) /
            sum(row['weight'] for row in subset))


rows = base_model()
assert len(rows) == 14
before_keys = ('source', 'report')
summary_keys = ('report',)
full_keys = ('source', 'report', 'sound')
after_summary_keys = ('report', 'sound')
a, b = posterior(rows, before_keys), posterior(rows, summary_keys)
assert all(a[(src, report)] == b[(report,)]
           for src, report in product(('A', 'B'), (0, 1)))
q, r = posterior(rows, full_keys), posterior(rows, after_summary_keys)
expected_table = {
    ('A', 1, 0): F(1, 2), ('A', 1, 1): F(1),
    ('B', 1, 0): F(9, 10), ('B', 1, 1): F(9, 10),
}
assert all(q[key] == value for key, value in expected_table.items())
assert r[(1, 0)] == F(7, 10) and r[(1, 1)] == F(19, 20)
keep_loss, erase_loss = loss(rows, full_keys), loss(rows, after_summary_keys)
variance = sum(row['weight'] *
               (q[tuple(row[k] for k in full_keys)] -
                r[tuple(row[k] for k in after_summary_keys)])**2 for row in rows)
assert loss(rows, before_keys) == loss(rows, summary_keys) == F(9, 100)
assert keep_loss == F(7, 100) and erase_loss == F(2, 25)
assert erase_loss - keep_loss == variance == F(1, 100)

# If no disclosure takes place, the current posterior already remains the final answer.
no_disclosure_gap = loss(rows, summary_keys) - loss(rows, before_keys)
assert no_disclosure_gap == 0

# Added sufficient-condition check: replace the inspection by an independent
# 75%-reliable report of the token. Its likelihoods depend only on x.
independent_rows = []
for row in rows:
    for new_report in (0, 1):
        likelihood = F(3, 4) if new_report == row['x'] else F(1, 4)
        independent_rows.append(dict(row, new_report=new_report,
                                     weight=row['weight'] * likelihood))
ind_full_keys = ('source', 'report', 'new_report')
ind_summary_keys = ('report', 'new_report')
ind_q = posterior(independent_rows, ind_full_keys)
ind_r = posterior(independent_rows, ind_summary_keys)
assert all(ind_q[(src, old, new)] == ind_r[(old, new)]
           for src, old, new in product(('A', 'B'), (0, 1), (0, 1)))
ind_keep_loss = loss(independent_rows, ind_full_keys)
ind_erase_loss = loss(independent_rows, ind_summary_keys)
assert ind_keep_loss == ind_erase_loss == F(9, 112)

# The actual inspection violates that condition in exactly the stated way.
source_specific = {}
for src in ('A', 'B'):
    source_specific[src] = event_probability(
        rows, lambda row: row['sound'] == 1,
        lambda row, src=src: row['x'] == 0 and row['report'] == 1 and row['source'] == src)
assert source_specific == {'A': F(0), 'B': F(4, 5)}

# Unchanged caveats from the original manuscript.
classification = {}
for name, keys in [('Keep', full_keys), ('Erase', after_summary_keys)]:
    post = posterior(rows, keys)
    classification[name] = sum(
        row['weight'] for row in rows
        if int(post[tuple(row[k] for k in keys)] >= F(1, 2)) == row['x'])
assert classification == {'Keep': F(9, 10), 'Erase': F(9, 10)}
shared = base_model(shared_condition=True)
assert loss(shared, full_keys) == loss(shared, after_summary_keys) == F(1, 20)

out = {
    'status': 'PASS',
    'method': 'Exact rational enumeration; supplemented by the analytic conditional-expectation and Bayes arguments in revision.md §3.',
    'positive_probability_states': len(rows),
    'initial_probability_preservation_all_histories': True,
    'before_keep_loss': str(loss(rows, before_keys)),
    'before_erase_loss': str(loss(rows, summary_keys)),
    'after_keep_loss': str(keep_loss),
    'after_erase_loss': str(erase_loss),
    'loss_gap_equals_expected_squared_posterior_gap': str(variance),
    'no_disclosure_loss_gap': str(no_disclosure_gap),
    'independent_future_report_control': {
        'reliability': '3/4', 'equal_posteriors_for_every_history': True,
        'keep_loss': str(ind_keep_loss), 'erase_loss': str(ind_erase_loss)},
    'actual_inspection_probability_sound_given_red_token_blue_report': {
        source: str(value) for source, value in source_specific.items()},
    'classification_correctness': {name: str(value) for name, value in classification.items()},
    'shared_condition_control_loss_both': '1/20',
    'limitation': 'Checks the stipulated finite models and new mathematical clarification, not empirical feasibility, normative truth, novelty, or all literature.'
}
Path(__file__).with_name('MODEL_CHECK.json').write_text(json.dumps(out, indent=2) + '\n')
print(json.dumps(out, indent=2))
