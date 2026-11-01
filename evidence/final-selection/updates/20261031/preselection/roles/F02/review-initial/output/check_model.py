"""Independent exact enumeration of the manuscript's stipulated finite model."""
from collections import defaultdict
from fractions import Fraction as F
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent

def model(shared_condition=False):
    rows = []
    for x in (0, 1):
        for sensor in ("A", "B"):
            for sound, p_sound in ((False, F(1, 5)), (True, F(4, 5))):
                if sensor == "A" or shared_condition:
                    reliability = F(1) if sound else F(1, 2)
                else:
                    reliability = F(9, 10)
                for report in (0, 1):
                    prob = F(1, 4) * p_sound * (reliability if report == x else 1-reliability)
                    if prob:
                        rows.append(dict(x=x, sensor=sensor, sound=sound, report=report, prob=prob))
    assert sum(r["prob"] for r in rows) == 1
    return rows

def posterior(rows, keys):
    mass, blue = defaultdict(F), defaultdict(F)
    for row in rows:
        key = tuple(row[k] for k in keys)
        mass[key] += row["prob"]
        blue[key] += row["prob"] * row["x"]
    return {key: blue[key]/mass[key] for key in mass}, mass

def score(rows, keys):
    probs, mass = posterior(rows, keys)
    loss = sum(row["prob"] * (probs[tuple(row[k] for k in keys)]-row["x"])**2 for row in rows)
    correctness = sum(mass[key]*max(p,1-p) for key,p in probs.items())
    return loss, correctness, probs

rows = model()
before_keep = score(rows, ("report", "sensor"))
before_erase = score(rows, ("report",))
after_keep = score(rows, ("report", "sensor", "sound"))
after_erase = score(rows, ("report", "sound"))
assert before_keep[0] == before_erase[0] == F(9, 100)
assert after_keep[0] == F(7, 100)
assert after_erase[0] == F(8, 100)
assert after_keep[1] == after_erase[1] == F(9, 10)
gap = sum(row["prob"] * (after_keep[2][(row["report"], row["sensor"], row["sound"])] - after_erase[2][(row["report"], row["sound"])])**2 for row in rows)
assert gap == after_erase[0]-after_keep[0] == F(1, 100)

table = {
    "A_faulty": after_keep[2][(1, "A", False)],
    "A_sound": after_keep[2][(1, "A", True)],
    "B_faulty": after_keep[2][(1, "B", False)],
    "B_sound": after_keep[2][(1, "B", True)],
    "erased_faulty": after_erase[2][(1, False)],
    "erased_sound": after_erase[2][(1, True)],
}
assert list(table.values()) == [F(1,2),F(1),F(9,10),F(9,10),F(7,10),F(19,20)]
alternate = model(shared_condition=True)
assert score(alternate,("report","sensor","sound"))[0] == score(alternate,("report","sound"))[0] == F(1,20)
result = {
    "method": "Exact enumeration with fractions, not simulation",
    "positive_probability_states": len(rows),
    "before_keep_loss": str(before_keep[0]),
    "before_erase_loss": str(before_erase[0]),
    "after_keep_loss": str(after_keep[0]),
    "after_erase_loss": str(after_erase[0]),
    "loss_gap": str(gap),
    "after_classification_correctness_both": str(after_keep[1]),
    "blue_report_posterior_table": {k: str(v) for k,v in table.items()},
    "alternate_shared_condition_loss_both": "1/20",
    "status": "PASS",
    "scope": "Arithmetic and finite-model consistency only; no empirical or normative validation"
}
(OUT / "MODEL_CHECK.json").write_text(json.dumps(result,indent=2)+"\n")
print(json.dumps(result,indent=2))
