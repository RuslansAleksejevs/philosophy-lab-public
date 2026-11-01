"""Bind root's future prepared pair batch; no writer, dispatch or pair selection.

Only main loads the real read-only archive. build_spec accepts an already verified
v2 resolution; its caller must use resolver_v2.load_resolution, not fabricate one.
"""
from pathlib import Path
import argparse
import importlib.util
import json
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
RUN = HERE.parent
ROOT = RUN.parents[1]
V2 = RUN / "capacity-resume-20261018/replacement-v2"
HELPER = ROOT / "runs/github-selection-20261018/archive_pair_ready.py"
spec = importlib.util.spec_from_file_location("pair_ready_original", HELPER)
A = importlib.util.module_from_spec(spec)
spec.loader.exec_module(A)
EXCEPTIONS = {"M12-N2", "M13-N2"}


def build_spec(root, run, preparation, coordinator, map_receipt, resolution,
               events, helper_inputs, extra_checks=()):
    root, run = Path(root), Path(run)
    prefix = str(run.relative_to(root)) + "/"
    def ref(name):
        return A.record(root, name)
    def doc(row):
        return A.decode(A.checked(root, row))
    def unique(rows):
        out = {}
        for row in rows:
            exact = ref(row["path"])
            A.require(all(exact[k] == row[k] for k in ("path", "sha256")), "Explicit artifact changed")
            A.require("bytes" not in row or exact["bytes"] == row["bytes"], "Byte count changed")
            A.require(row["path"] not in out or out[row["path"]] == exact, "Conflicting descriptors")
            out[row["path"]] = exact
        return list(out.values())
    old_ref = ref(prefix + "START_RECEIPT.json")
    old, prep, group = doc(old_ref), doc(preparation), doc(map_receipt)
    A.require(resolution["schema"] == "selection-capacity-resolution.v2" and set(resolution["exceptions"]) == EXCEPTIONS, "Both accepted replacement maps required")
    A.require(resolution["input_event_id"] == old["event_id"], "Original input event changed")
    A.require(group["status"] == "CAPACITY_REPLACEMENTS_COMPLETE_ARCHIVED" and group["event_id"] == resolution["map_event_id"], "Aggregate receipt differs")
    mapping = doc(group["map"])
    A.require(mapping["schema"] == "selection-capacity-map.v2" and set(mapping["attempt_map_receipts"]) == EXCEPTIONS, "Both per-job map receipts required")
    check_artifacts = unique([group["map"], *mapping["attempt_map_receipts"].values()])
    event = next(e for e in events if e["id"] == group["event_id"])
    A.require(event["kind"] == "research.selection.capacity_replacements.accepted" and event["run_id"] == run.name and event["payload"]["status"] == group["status"], "Actual aggregate event differs")
    A.require({r["sha256"] for r in check_artifacts} <= set(event["outputs"]), "Aggregate event does not bind all map artifacts")
    group_check = {"event_id": event["id"], "kind": event["kind"], "status_pointer": "/payload/status", "accepted_value": group["status"], "artifacts": check_artifacts}
    receipts, sessions = [], set()
    for i in range(1, 23):
        for role in A.ROLES:
            jid = f"M{i:02}-{role}"
            item = ref(prefix + "results/" + jid + "/ARCHIVE_RECEIPT.json")
            receipt = doc(item)
            A.require(receipt["job_id"] == jid and receipt["status"] == "REVIEW_ARCHIVED" and receipt["input_event_id"] == old["event_id"], "Missing accepted logical review")
            A.require(receipt["session_id"] not in sessions, "Duplicate accepted session")
            sessions.add(receipt["session_id"])
            if jid in EXCEPTIONS:
                selected = resolution["exceptions"][jid]
                A.require(receipt["accepted_attempt"] == 2 and receipt["event_id"] == selected["accepted_attempt"]["event_id"] and receipt["session_id"] == selected["accepted_attempt"]["session_id"], "Logical receipt does not select mapped attempt-002")
                A.require(receipt["session_id"] != selected["failed_attempt"]["session_id"], "Failed session cannot supply a review")
            else:
                A.require(receipt.get("accepted_attempt", 1) == 1, "Ordinary logical review must remain attempt-001")
            receipts.append(item)
    A.require(not (sessions & {x["failed_attempt"]["session_id"] for x in resolution["exceptions"].values()}), "Failed session reused by an accepted review")
    A.require(coordinator, "Root must supply its actual coordinator evidence")
    result = {"schema": "explicit-pair-ready-inputs.v1", "status": "ROOT_SELECTED_PAIR_INPUTS",
              "batch_id": prep["batch_id"], "coordinator_session_id": doc(ref(prefix + "AUTHORIZATION.json"))["session_id"],
              "old_start": old_ref, "preparation": preparation, "individual_review_receipts": receipts,
              "prior_pair_preparations": [r for r in prep["source_files"] if r["path"].endswith("/PAIR_PREPARATION.json")],
              "helper_inputs": unique([*helper_inputs, *resolution["evidence_files"], map_receipt]),
              "coordinator_artifacts": unique([*coordinator, map_receipt]),
              "check_events": [group_check, *extra_checks]}
    A.require(len({c["event_id"] for c in result["check_events"]}) == len(result["check_events"]), "Duplicate check event")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preparation", required=True, type=Path)
    parser.add_argument("--coordinator-artifact", required=True, action="append", type=Path)
    parser.add_argument("--map-receipt", type=Path, default=V2 / "ACCEPTED_ATTEMPTS_RECEIPT.json")
    parser.add_argument("--checks-file", type=Path, help="Optional JSON array of additional actual check-event specifications")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    output = args.output.absolute()
    A.require(output.is_relative_to(RUN) and ".." not in output.parts and not any(p.is_symlink() for p in (output, *output.parents)) and not output.exists(), "Use a new safe spec path inside selection run")
    def ref(path):
        return A.record(ROOT, str(Path(path).absolute().relative_to(ROOT)))
    sys.path[:0] = [str(V2), str(ROOT / "scripts")]
    from resolver_v2 import load_resolution
    from research_archive import Archive
    archive = Archive(ROOT / "research/archive")
    events = list(archive.events())
    resolution = load_resolution(ROOT, RUN, args.map_receipt.absolute(), events, archive.get)
    helper_paths = [HELPER, HELPER.with_name("test_archive_pair_ready.py"), HELPER.with_name("PAIR_READY_INTERFACE_RU.txt"),
                    HERE / "bind_pair_ready.py", HERE / "test_pair_ready_handoff.py", HERE / "PAIR_READY_AFTER_110_RU.txt", HERE / "pair-ready.spec.template.json", HERE / "HANDOFF_TESTS.json"]
    extra = A.decode(A.checked(ROOT, ref(args.checks_file))) if args.checks_file else []
    A.require(isinstance(extra, list), "Extra checks must be an explicit JSON array")
    result = build_spec(ROOT, RUN, ref(args.preparation), [ref(p) for p in args.coordinator_artifact], ref(args.map_receipt), resolution, events, [ref(p) for p in helper_paths], extra)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("xb") as stream:
        stream.write(A.encode(result))
    print(json.dumps({"status": "PAIR_SPEC_BOUND_LOCAL_CANONICAL_PAIR_ACCEPTANCE_NOT_RUN", "output": ref(output), "individual_receipts": 110, "archive_writes": 0, "model_calls": 0}))


if __name__ == "__main__":
    main()
