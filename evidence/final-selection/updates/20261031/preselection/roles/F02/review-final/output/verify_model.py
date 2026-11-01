"""Independent finite enumeration of the manuscript's stipulated sensor model."""
from fractions import Fraction as F
from collections import defaultdict
from pathlib import Path
import json


def states(shared_condition=False):
    result = []
    for x in (0, 1):
        for source in ("A", "B"):
            for sound in (0, 1):
                for report in (0, 1):
                    if source == "A" or shared_condition:
                        likelihood = F(int(report == x)) if sound else F(1, 2)
                    else:
                        likelihood = F(9, 10) if report == x else F(1, 10)
                    mass = F(1, 2) * F(1, 2) * (F(4, 5) if sound else F(1, 5)) * likelihood
                    if mass:
                        result.append(dict(x=x, source=source, sound=sound, report=report, mass=mass))
    assert sum(s["mass"] for s in result) == 1
    return result


def posteriors(worlds, fields):
    mass = defaultdict(F)
    blue_mass = defaultdict(F)
    for s in worlds:
        key = tuple(s[k] for k in fields)
        mass[key] += s["mass"]
        blue_mass[key] += s["mass"] * s["x"]
    return {key: blue_mass[key] / value for key, value in mass.items()}


def loss(worlds, fields, estimates):
    return sum(s["mass"] * (estimates[tuple(s[k] for k in fields)] - s["x"]) ** 2 for s in worlds)


def classification_accuracy(worlds, fields, estimates):
    return sum(s["mass"] * (int(estimates[tuple(s[k] for k in fields)] >= F(1, 2)) == s["x"]) for s in worlds)


worlds = states()
h = ("source", "report")
s = ("report",)
hz = ("source", "report", "sound")
sz = ("report", "sound")
before_keep = posteriors(worlds, h)
before_erase = posteriors(worlds, s)
q = posteriors(worlds, hz)
r = posteriors(worlds, sz)
for key, value in before_keep.items():
    assert value == before_erase[(key[1],)]
assert before_erase[(1,)] == F(9, 10)
assert (q[("A", 1, 0)], q[("A", 1, 1)]) == (F(1, 2), F(1))
assert (q[("B", 1, 0)], q[("B", 1, 1)]) == (F(9, 10), F(9, 10))
assert (r[(1, 0)], r[(1, 1)]) == (F(7, 10), F(19, 20))
keep_loss = loss(worlds, hz, q)
erase_loss = loss(worlds, sz, r)
gap = sum(w["mass"] * (q[tuple(w[k] for k in hz)] - r[tuple(w[k] for k in sz)]) ** 2 for w in worlds)
assert keep_loss == F(7, 100)
assert erase_loss == F(8, 100)
assert erase_loss - keep_loss == gap == F(1, 100)
assert loss(worlds, h, before_keep) == loss(worlds, s, before_erase) == F(9, 100)
assert classification_accuracy(worlds, hz, q) == classification_accuracy(worlds, sz, r) == F(9, 10)
source_after = defaultdict(F)
report_condition_mass = defaultdict(F)
for w in worlds:
    key = (w["report"], w["sound"])
    report_condition_mass[key] += w["mass"]
    if w["source"] == "A":
        source_after[key] += w["mass"]
assert all(source_after[key] / mass == F(1, 2) for key, mass in report_condition_mass.items())

alternative = states(shared_condition=True)
aq = posteriors(alternative, hz)
ar = posteriors(alternative, sz)
assert loss(alternative, hz, aq) == loss(alternative, sz, ar) == F(5, 100)

result = {
    "method": "Exact Fraction arithmetic; enumerated joint distribution, not copied posterior inputs",
    "positive_probability_states": len(worlds),
    "before_squared_loss_both": "9/100",
    "after_squared_loss_keep": str(keep_loss),
    "after_squared_loss_erase": str(erase_loss),
    "expected_squared_posterior_difference": str(gap),
    "after_classification_accuracy_both": "9/10",
    "source_A_given_report_and_inspection": "1/2 in every positive-probability state",
    "blue_posteriors": {"A_faulty": "1/2", "A_sound": "1", "B_faulty": "9/10", "B_sound": "9/10", "erased_faulty": "7/10", "erased_sound": "19/20"},
    "shared_condition_alternative_squared_loss_both": "1/20",
    "all_assertions_passed": True,
    "limitations": "Verifies the stipulated finite model only; not empirical sensor performance or the normative value of the score."
}
Path(__file__).with_name("MODEL_CHECK.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
print(json.dumps(result, ensure_ascii=False, indent=2))
