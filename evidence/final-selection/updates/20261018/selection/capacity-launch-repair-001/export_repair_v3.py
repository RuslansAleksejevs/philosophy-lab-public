#!/usr/bin/env python3
"""Explicit export-list derivative for accepted M12-N2/003 and M13-N2/002 replacements.

Ordinary accepted reviews use the frozen builder verifier. The replacement and
provenance paths come from the canonical resolver. Only named safe failure,
addendum and map metadata are added; no raw output or failed prose is exported.
"""
from pathlib import Path, PurePosixPath
from collections import Counter, defaultdict
import argparse
import importlib.util
import json
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
DEFAULT_RUN = HERE.parent
ROOT = DEFAULT_RUN.parents[1]
_spec = importlib.util.spec_from_file_location("capacity_frozen_export", ROOT / "runs/github-selection-20261018/build_final_receipt_files.py")
frozen = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(frozen)
SOURCE, MINIMUM_FIXED, TECHNICAL_FIXED = frozen.SOURCE, frozen.MINIMUM_FIXED, frozen.TECHNICAL_FIXED
NAMED, COUNT_KEYS = frozen.NAMED, frozen.COUNT_KEYS
require, checked, fingerprint = frozen.require, frozen.checked, frozen.fingerprint
metadata, pointer, frozen_queue = frozen.metadata, frozen.pointer, frozen.frozen_queue
from summary_repair_v3 import ATTEMPT_NUMBERS, LOGICAL_JOBS, checked_resolution, resolution_note


def resolve_job(job, run_dir, root, resolution):
    from resolver_repair import resolve_job as resolve
    return resolve(job, run_dir, root, resolution)


def accepted_review(root, job, input_event, resolution):
    run_dir = Path(root) / SOURCE
    resolved = resolve_job(job, run_dir, Path(root), resolution)
    expected_attempt = ATTEMPT_NUMBERS.get(job["id"], 1)
    require(resolved["attempt_number"] == expected_attempt, "Resolved attempt differs from two-replacement contract")
    expected_dir = run_dir / "results" / job["id"] / f"attempt-{expected_attempt:03}"
    require(Path(resolved["attempt"]) == expected_dir, "Resolved attempt directory differs")
    attempt_directory = str(expected_dir.relative_to(root)) + "/"
    archive_path = str(Path(resolved["archive_receipt"]).relative_to(root))
    capture_path = str(Path(resolved["capture_receipt"]).relative_to(root))
    if job["id"] not in LOGICAL_JOBS:
        require(archive_path == SOURCE + "results/" + job["id"] + "/ARCHIVE_RECEIPT.json" and capture_path == SOURCE + "results/" + job["id"] + "/CAPTURE_RECEIPT.json", "Ordinary receipt paths changed")
        result = frozen.accepted_review(root, job, input_event)
        result.update(attempt_directory=attempt_directory, capture_path=capture_path, attempt_number=1)
        return result
    exception = resolution["exceptions"][job["id"]]
    require(input_event == exception["input_event_id"], "Replacement must retain original input event")
    archive = metadata(root, archive_path)
    require(archive["status"] == "REVIEW_ARCHIVED", "Unaccepted or quarantined review: " + job["id"])
    require(archive.get("event_id") and archive.get("lineage_event_id") and archive["job_id"] == job["id"], "Incomplete archive identity")
    require(archive["input_event_id"] == input_event, "Review uses a different input event")
    require(archive["capture_status"] == "BOUNDED_VISIBLE_CAPTURE_ACCEPTED", "Capture not accepted")
    require(archive.get("accepted_attempt") == expected_attempt and archive.get("attempt_path") == str(expected_dir.relative_to(root)), "Replacement receipt attempt mismatch")
    require(archive.get("replacement_ready_event_id") == exception["ready_event_id"] and archive.get("failed_attempt_event_id") == exception["failed_attempt"]["event_id"], "Replacement recovery dependency mismatch")
    if job["id"] == "M12-N2":
        require(archive.get("local_launch_failure_event_id") == exception["local_launch_failure"]["event_id"], "Replacement receipt dropped local launch failure")
    require(archive["event_id"] == exception["accepted_attempt"]["event_id"] and archive["session_id"] == exception["accepted_attempt"]["session_id"], "Replacement receipt differs from accepted map")
    require(archive["session_id"] != exception["failed_attempt"]["session_id"], "Failed session cannot count as accepted replacement")
    bound = {r["path"]: r for r in archive["files"]}
    require(len(bound) == len(archive["files"]), "Duplicate replacement archive file")
    receipt_path = attempt_directory + "receipt.json"
    response_path = attempt_directory + "response.json"
    for name in [receipt_path, response_path]:
        checked(root, bound[name])
    receipt = metadata(root, receipt_path)
    require(receipt["status"] == "COMPLETE_LOCAL_PENDING_CANONICAL_ARCHIVE", "Local review was not complete")
    require(receipt["job_id"] == job["id"] and receipt["session_id"] == archive["session_id"], "Session/job identity mismatch")
    require(receipt["prompt_sha256"] == job["prompt_sha256"] and receipt["schema_sha256"] == job["schema_sha256"], "Assigned inputs differ")
    require(not receipt.get("quality_flags"), "Accepted review carries unresolved quality flags")
    require(receipt["outputs"][response_path] == bound[response_path]["sha256"], "Response not bound by local receipt")
    # The prose response is deliberately never parsed or evaluated here.
    return {"job_id": job["id"], "session_id": archive["session_id"], "role": job["role"], "event_id": archive["event_id"],
            "files": [fingerprint(root, archive_path), checked(root, bound[receipt_path]), checked(root, bound[response_path])],
            "archive": archive, "bound": bound, "attempt_directory": attempt_directory, "capture_path": capture_path, "attempt_number": expected_attempt}



def build(spec, root, resolution):
    root = Path(root).resolve()
    checked_resolution(resolution)
    require(spec["schema"] == "explicit-selection-final-files.v1" and spec["status"] == "ROOT_SELECTED_FINAL_INPUTS", "Unbound input specification")
    require(set(spec["named_outputs"]) == NAMED, "Provide each named final artifact explicitly")
    require(set(spec["count_fields"]) == COUNT_KEYS, "All actual count mappings are required")
    require(not spec["include_review_provenance"] or spec["include_review_evidence"], "Review provenance requires the review evidence layer")
    require(spec["named_outputs"]["decisions"]["path"] == SOURCE + "DECISIONS.json", "DECISIONS path differs")
    require(spec["named_outputs"]["final_plan"]["path"] == SOURCE + "FINAL_PLAN.json", "FINAL_PLAN path differs")
    files, categories = {}, defaultdict(set)
    def add(name, kind, expected=None):
        ref = checked(root, expected) if expected else fingerprint(root, name)
        require(ref["path"] == name, "Explicit path mismatch")
        if name in files:
            require(files[name] == ref, "Conflicting source fingerprint")
        files[name] = ref
        categories[kind].add(name)
    require(isinstance(resolution.get("evidence_files"), list) and resolution["evidence_files"], "Explicit safe recovery metadata required")
    group_evidence = {ref["path"]: ref for ref in resolution["evidence_files"]}
    require(len(group_evidence) == len(resolution["evidence_files"]), "Duplicate group recovery metadata")
    for item in resolution["exceptions"].values():
        require(isinstance(item.get("evidence_files"), list) and item["evidence_files"], "Both exceptions require safe recovery metadata")
        for ref in item["evidence_files"]:
            require(group_evidence.get(ref["path"]) == ref, "Group export omitted or changed per-job recovery metadata")
    metadata_paths = set()
    for ref in resolution["evidence_files"]:
        require(isinstance(ref, dict) and {"path", "sha256", "bytes"} <= set(ref), "Recovery metadata needs exact path/hash/bytes")
        require(type(ref["bytes"]) is int and ref["bytes"] >= 0, "Recovery metadata byte count must be a nonnegative integer")
        require(ref["path"] not in metadata_paths, "Duplicate recovery evidence path")
        metadata_paths.add(ref["path"])
        leaf = PurePosixPath(ref["path"]).name.lower()
        require(not any(token in leaf for token in ("stdout", "stderr", "native-visible", "visible-events")), "Raw/native/stdout/stderr recovery metadata excluded")
        add(ref["path"], "capacity_recovery_evidence", ref)
    for name in MINIMUM_FIXED:
        add(SOURCE + name, "minimum_required")
    for key, ref in spec["named_outputs"].items():
        add(ref["path"], "minimum_required", ref)
    def value(field):
        m = spec[field] if field == "selected_ids_field" else spec["count_fields"][field]
        ref = spec["named_outputs"][m["input"]]
        return pointer(metadata(root, ref["path"]), m["pointer"])
    selected = value("selected_ids_field")
    require(isinstance(selected, list) and 1 <= len(selected) <= 10 and len(set(selected)) == len(selected), "Invalid accepted reading set")
    reading = spec["reading"]
    require(len(reading) == len(selected) and {r["candidate_id"] for r in reading} == set(selected), "Reading set differs")
    for r in reading:
        add(r["source"]["path"], "minimum_required", r["source"])
    individual = spec["individual"]
    require(individual["queue"]["path"] == SOURCE + "queue.json" and individual["input_receipt"]["path"] == SOURCE + "START_RECEIPT.json", "Wrong individual queue/input receipt")
    jobs, start = frozen_queue(root, individual["queue"], individual["input_receipt"])
    expected_ids = {f"M{i:02}-{role}" for i in range(1, 23) for role in ["N1", "N2", "N3", "J1", "J2"]}
    require({j["id"] for j in jobs} == expected_ids and all(j["phase"] == "individual" for j in jobs), "Exactly the fixed 110 individual jobs are required")
    for j in jobs:
        require(j["id"] == j["manuscript_id"] + "-" + j["role"], "Job role/manuscript identity mismatch")
    accepted = [accepted_review(root, j, start["event_id"], resolution) for j in jobs]
    pair_spec = spec["pairs"]
    pair_jobs, pair_results, pair_ids = [], [], set()
    if pair_spec["mode"] == "EXPLICIT_ACCEPTED_PAIR_QUEUE":
        pair_jobs, pair_start = frozen_queue(root, pair_spec["queue"], pair_spec["input_receipt"])
        require(pair_jobs and all(j["phase"] == "pair" for j in pair_jobs), "Pair queue missing or ambiguous")
        groups = defaultdict(list)
        for j in pair_jobs:
            groups[j["expected_output"]["pair_id"]].append(j)
        pair_ids = set(groups)
        require(1 <= len(pair_ids) <= 10 and not ({j["id"] for j in pair_jobs} & expected_ids), "Pair IDs or ceiling invalid")
        for members in groups.values():
            require(Counter(j["role"] for j in members) == Counter({"N1": 1, "N2": 1, "N3": 1, "J1": 1, "J2": 1}), "Each pair needs the accepted 3:2 roles")
        pair_results = [accepted_review(root, j, pair_start["event_id"], resolution) for j in pair_jobs]
        add(pair_spec["queue"]["path"], "minimum_required", pair_spec["queue"])
        add(pair_spec["input_receipt"]["path"], "minimum_required", pair_spec["input_receipt"])
        require(set(pair_spec["method_inputs"]) == {"method", "allocation", "rubric", "schema"}, "Map the frozen pair method/allocation/rubric/schema explicitly")
        pair_bound = {x["path"]: x["sha256"] for x in pair_start["files"]}
        for ref in pair_spec["method_inputs"].values():
            require(pair_bound[ref["path"]] == ref["sha256"], "Pair method input not frozen")
            add(ref["path"], "minimum_required", ref)
    else:
        require(pair_spec["mode"] == "EXPLICIT_NO_PAIRS", "An explicit actual pair disposition is required")
    all_reviews = accepted + pair_results
    require(len({r["session_id"] for r in all_reviews}) == len(all_reviews), "Review session reused")
    require(not ({item["failed_attempt"]["session_id"] for item in resolution["exceptions"].values()} & {r["session_id"] for r in all_reviews}), "Failed session cannot enter accepted counts")
    actual = {"accepted_individual_reviews": len(accepted), "accepted_neutral_individual": sum(r["role"].startswith("N") for r in accepted), "accepted_profile_individual": sum(r["role"].startswith("J") for r in accepted), "actual_pairs": len(pair_ids), "accepted_pair_reviews": len(pair_results)}
    for key, observed in actual.items():
        mapped = value(key)
        require(type(mapped) is int and mapped == observed, "Final summary disagrees with accepted receipts: " + key)
    for r in all_reviews:
        # Always bind the acceptance metadata. Responses/local receipts are an
        # explicitly selected export layer, not an implicit archive-file walk.
        add(r["files"][0]["path"], "accepted_review_receipts", r["files"][0])
        if spec["include_review_evidence"]:
            for ref in r["files"][1:]:
                add(ref["path"], "optional_review_evidence", ref)
            if spec["include_review_provenance"]:
                for leaf in ["launch.json", "native-check.json", "final.txt"]:
                    name = r["attempt_directory"] + leaf
                    add(name, "optional_review_evidence", r["bound"][name])
                capture_name = r["capture_path"]
                add(capture_name, "optional_review_evidence", {"path": capture_name, "sha256": r["archive"]["capture_sha256"]})
    if spec["include_technical_files"]:
        for name in TECHNICAL_FIXED:
            add(SOURCE + name, "recommended_technical_evidence")
    # Fragment finals need their separate accepted manifest binding. This helper
    # does not manufacture it from ARCHIVE_RECEIPT or export native envelopes.
    require(not spec.get("agent_fragment_sources"), "Use a separately accepted explicit fragment contract; see FINAL_RECEIPT_INPUTS_RU.txt")
    require(SOURCE + "FINAL_RECEIPT.json" not in files, "Do not include a circular self-hash")
    return {"schema": "proposed-selection-final-receipt-files.v1", "status": "CANDIDATE_FILES_REQUIRING_ROOT_ACCEPTANCE", "files": sorted(files.values(), key=lambda r: r["path"]),
            "categories": {k: sorted(v) for k, v in categories.items()}, "accepted_review_counts_verified": actual, "preserved_failed_attempts": 3, "preserved_capacity_failures": 2, "preserved_local_launch_failures": 1, "failed_provider_review_slots": 2, "attempt_resolution": resolution_note(resolution),
            "boundary": "A proposed file list, not canonical acceptance and not permission to publish. Only exact named files and fixed queue IDs were used. The two failed capacity attempts and one local launch failure are retained as explicit safe metadata and are not counted as reviews. No review prose was interpreted; no native sessions, external full sources, or tool bodies were exported."}



def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--map-receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve(); run_dir = root / SOURCE
    sys.path.insert(0, str(root / "scripts"))
    from research_archive import Archive
    from resolver_repair import load_resolution
    archive = Archive(root / "research/archive")
    resolution = load_resolution(root, run_dir, args.map_receipt.resolve(), archive.events(), archive.get)
    result = build(json.loads(args.spec.read_text()), root, resolution)
    output = args.output.resolve()
    require(output.is_relative_to(root) and not output.exists(), "Output must be new and inside repository")
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x") as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(json.dumps({"status": result["status"], "files": len(result["files"]), "counts": result["accepted_review_counts_verified"], "preserved_failed_attempts": 3, "preserved_capacity_failures": 2, "preserved_local_launch_failures": 1, "failed_provider_review_slots": 2}))


if __name__ == "__main__": main()
