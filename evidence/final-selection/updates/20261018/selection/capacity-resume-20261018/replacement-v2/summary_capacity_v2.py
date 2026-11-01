#!/usr/bin/env python3
"""Versioned summary for the two accepted capacity replacements, M12-N2/002 and M13-N2/002.

Ordinary 108 jobs use the frozen verifier. The narrow replacement verifier below
preserves its checks with explicit resolved paths and replacement lineage only.
No models, archive writer, candidate decisions or modification of frozen files.
"""
from pathlib import Path
import argparse
import importlib.util
import json
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
DEFAULT_RUN = HERE.parents[1]
ROOT = DEFAULT_RUN.parents[1]
LOGICAL_JOBS = frozenset({"M12-N2", "M13-N2"})
_spec = importlib.util.spec_from_file_location("capacity_frozen_summary", DEFAULT_RUN / "summary-preparation/summarize_reviews.py")
frozen = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(frozen)
need, read, load, strict, digest = frozen.need, frozen.read, frozen.load, frozen.strict, frozen.digest
json_schema, aggregate = frozen.json_schema, frozen.aggregate
ROLES, METRICS, COMPLETE = frozen.ROLES, frozen.METRICS, frozen.COMPLETE
BOUNDARY = ("The required set remains 110 accepted logical reviews; two earlier capacity failures are retained separately and are not reviews. "
            "Ordinary verification and the 60/40 calculation are unchanged. The supplied resolution must come "
            "from load_resolution with actual canonical events. No ranking or selection.")


def resolve_job(job, run_dir, root, resolution):
    from resolver_v2 import resolve_job as resolve
    return resolve(job, run_dir, root, resolution)


def checked_resolution(resolution):
    need(isinstance(resolution, dict) and resolution.get("schema") == "selection-capacity-resolution.v2", "Explicit two-job v2 resolution required")
    need(isinstance(resolution.get("exceptions"), dict) and set(resolution["exceptions"]) == LOGICAL_JOBS, "Exactly M12-N2 and M13-N2 exceptions required")
    for key in ("input_event_id", "map_event_id"):
        need(isinstance(resolution.get(key), str) and resolution[key], "Missing canonical group resolution event")
    failed_sessions, accepted_sessions, failed_events, accepted_events = [], [], [], []
    for jid, item in resolution["exceptions"].items():
        need(isinstance(item, dict) and item.get("logical_job_id") == jid, "Per-job resolution identity differs")
        need(item.get("input_event_id") == resolution["input_event_id"], "Replacement changed original input event")
        for key in ("ready_event_id", "map_event_id"):
            need(isinstance(item.get(key), str) and item[key], "Missing per-job canonical event")
        for key in ("failed_attempt", "accepted_attempt"):
            need(isinstance(item.get(key), dict) and all(isinstance(item[key].get(k), str) and item[key][k] for k in ("event_id", "session_id")), "Missing preserved/accepted attempt identity")
        failed_sessions.append(item["failed_attempt"]["session_id"])
        accepted_sessions.append(item["accepted_attempt"]["session_id"])
        failed_events.append(item["failed_attempt"]["event_id"])
        accepted_events.append(item["accepted_attempt"]["event_id"])
    need(len(set(failed_sessions + accepted_sessions)) == 4, "Two failures and two accepted replacements must have four distinct sessions")
    need(len(set(failed_events + accepted_events)) == 4, "Failed and accepted attempts must remain separate events")
    return resolution


def resolution_note(resolution):
    return {"logical_job_ids": sorted(LOGICAL_JOBS), "accepted_attempt_number": 2,
            "map_event_id": resolution["map_event_id"], "input_event_id": resolution["input_event_id"],
            "exceptions": {jid: {"map_event_id": item["map_event_id"], "ready_event_id": item["ready_event_id"],
                                 "preserved_failed_event_id": item["failed_attempt"]["event_id"],
                                 "accepted_event_id": item["accepted_attempt"]["event_id"]}
                           for jid, item in sorted(resolution["exceptions"].items())}}


def replacement_lineage_id(run_dir, job):
    # Failed attempt-001 never produced an evaluation entry. Keep logical ID.
    return run_dir.name + ":" + job["id"] + ":evaluation-v1"


def verify_replacement_job(job, start, schema, run_dir, root, resolution):
    need(job["id"] in LOGICAL_JOBS, "Only the two explicit v2 replacements are supported")
    exception = resolution["exceptions"][job["id"]]
    resolved = resolve_job(job, run_dir, root, resolution)
    need(resolved["attempt_number"] == 2, "Replacement must select attempt-002")
    attempt = Path(resolved["attempt"])
    need(attempt == run_dir / "results" / job["id"] / "attempt-002", "Wrong replacement attempt path")
    base = {"job_id": job["id"], "manuscript_id": job["manuscript_id"], "role": job["role"], "profile_id": job["profile_id"]}
    archive_path = Path(resolved["archive_receipt"])
    if not archive_path.exists():
        if (attempt / "failure.json").exists():
            status = "FAILED_MISSING"
        elif (attempt / "receipt.json").exists():
            local = load(attempt / "receipt.json", root)
            status = "QUARANTINED_MISSING" if local.get("status", "").startswith("QUARANTINED") else "LOCAL_ONLY_NOT_ARCHIVED"
        else:
            status = "UNFINISHED_MISSING" if attempt.exists() else "NOT_STARTED_MISSING"
        return {**base, "status": status, "accepted": False}, None
    archive = load(archive_path, root)
    need(archive.get("job_id") == job["id"], "Archive receipt belongs to another job")
    if archive.get("status") == "QUARANTINED_REVIEW_ARCHIVED_MISSING":
        return {**base, "status": "QUARANTINED_MISSING", "accepted": False,
                "archive_receipt": str(archive_path.relative_to(root)), "event_id": archive.get("event_id")}, None
    need(archive.get("status") == "REVIEW_ARCHIVED", "Unknown archive acceptance status")
    need(archive.get("input_event_id") == start["event_id"] == exception["input_event_id"], "Review bound to a different input acceptance")
    need(archive.get("accepted_attempt") == 2 and archive.get("attempt_path") == str(attempt.relative_to(root)), "Replacement receipt attempt mismatch")
    need(archive.get("replacement_ready_event_id") == exception["ready_event_id"] and archive.get("failed_attempt_event_id") == exception["failed_attempt"]["event_id"], "Replacement receipt is missing actual recovery dependencies")
    for key in ("event_id", "lineage_event_id", "lineage_entry_id", "session_id"):
        need(isinstance(archive.get(key), str) and bool(archive[key]), "Missing accepted evidence reference: " + key)
    need(archive["lineage_entry_id"] == replacement_lineage_id(run_dir, job), "Evaluation lineage identity mismatch")
    need(archive["event_id"] == exception["accepted_attempt"]["event_id"] and archive["session_id"] == exception["accepted_attempt"]["session_id"], "Replacement differs from canonical attempt resolution")
    need(archive["session_id"] != exception["failed_attempt"]["session_id"], "Failed and replacement sessions must differ")
    files = archive.get("files")
    need(isinstance(files, list) and bool(files), "Missing archive output manifest")
    bound = {}
    for item in files:
        path = root / item["path"]
        need(path.parent == attempt and path not in bound, "Duplicate or wrong-attempt archived file")
        data = read(path, root)
        need(digest(data) == item["sha256"] and len(data) == item["bytes"], "Archived file hash/size mismatch: " + path.name)
        bound[path] = item["sha256"]
    need(set(attempt.iterdir()) == set(bound), "Extra/unbound attempt files")
    required = {"receipt.json", "response.json", "native-check.json", "native-visible.json", "launch.json", "stderr.json", "visible-events.jsonl", "final.txt"}
    need(required <= {p.name for p in bound}, "Required accepted evidence file missing")
    receipt = load(attempt / "receipt.json", root)
    need(receipt.get("status") == COMPLETE and receipt.get("job_id") == job["id"] and receipt.get("session_id") == archive["session_id"], "Local receipt identity/status mismatch")
    need(receipt.get("quality_flags") == [] and receipt.get("visible_final_count") == 1, "Review has unresolved quality/final-count flags")
    for recorded, requested in (("prompt_sha256", "prompt_sha256"), ("schema_sha256", "schema_sha256"), ("requested_model", "model"), ("requested_effort", "effort"), ("requested_service_tier", "service_tier")):
        need(receipt.get(recorded) == job[requested], "Accepted review configuration/input mismatch")
    outputs = receipt.get("outputs", {})
    need({root / p for p in outputs} == set(bound) - {attempt / "receipt.json"}, "Local/archive manifests differ")
    need(all(bound[root / p] == h for p, h in outputs.items()), "Local/archive output hashes differ")
    proof = load(attempt / "native-check.json", root)
    need(proof.get("session_id") == archive["session_id"] and proof.get("prompt_sha256") == job["prompt_sha256"], "Native proof identity/input mismatch")
    need(proof.get("isolation_failures") == [] and proof.get("tool_calls") == [] and proof.get("other_user_metadata") == [], "Native isolation gap")
    need(len(proof.get("prompt_lines", [])) == 1 and len(proof.get("final_lines", [])) == 1, "Native prompt/final coverage gap")
    observed = proof.get("configurations", [])
    need(observed and all(x.get("model") == job["model"] and x.get("effort") == job["effort"] and x.get("service_tier") in {None, job["service_tier"]} for x in observed), "Native model/effort mismatch")
    capture_bytes = read(Path(resolved["capture_receipt"]), root)
    need(digest(capture_bytes) == archive.get("capture_sha256"), "Bounded capture receipt hash mismatch")
    capture = strict(capture_bytes)
    need(capture.get("status") == "BOUNDED_VISIBLE_CAPTURE_ACCEPTED" and capture.get("session_id") == archive["session_id"] and capture.get("evidence_events"), "Bounded capture acceptance missing")
    value = load(attempt / "response.json", root)
    json_schema(value, schema)
    for key, target in (("review_id", job["id"]), ("manuscript_id", job["manuscript_id"]), ("profile_id", job["profile_id"]), ("read_complete", True)):
        need(type(value.get(key)) is type(target) and value[key] == target, "Response identity/full-reading mismatch")
    need(value == strict(read(attempt / "final.txt", root)), "Response/native final-file mismatch")
    need(all(type(value["scores"][m]) is int and 1 <= value["scores"][m] <= 5 for m in METRICS), "Invalid required score")
    originality = value["scores"]["originality"]
    need(originality is None or (type(originality) is int and 1 <= originality <= 5), "Invalid originality score")
    need(isinstance(value.get("reason_ru"), list) and 2 <= len(value["reason_ru"]) <= 3 and all(isinstance(s, str) and s.strip() for s in value["reason_ru"]), "Missing concrete Russian rationale")
    need(value.get("recommendation") in {"shortlist", "borderline", "outside"}, "Invalid recommendation")
    evidence = {"attempt_number": 2, "attempt_resolution_event_id": resolution["map_event_id"], "preserved_failed_event_id": exception["failed_attempt"]["event_id"],
                "archive_receipt": str(archive_path.relative_to(root)), "archive_receipt_sha256": digest(read(archive_path, root)),
                "event_id": archive["event_id"], "lineage_event_id": archive["lineage_event_id"], "lineage_entry_id": archive["lineage_entry_id"],
                "session_id": archive["session_id"], "response_file": str((attempt / "response.json").relative_to(root)),
                "response_sha256": bound[attempt / "response.json"], "prompt_sha256": job["prompt_sha256"], "schema_sha256": job["schema_sha256"],
                "capture_sha256": archive["capture_sha256"], "capture_evidence_events": capture["evidence_events"]}
    return {**base, "status": "ACCEPTED_VERIFIED", "accepted": True, "evidence": evidence}, {"role": job["role"], "profile_id": job["profile_id"], "response": value, "evidence": evidence}



def summarize(run_dir, resolution):
    run_dir = Path(run_dir).absolute()
    boundary = BOUNDARY
    try:
        checked_resolution(resolution)
        root, start, allocation, jobs, schema = frozen.inputs(run_dir)
    except (ValueError, KeyError, TypeError, OSError) as exc:
        return {"status": "INVALID_INPUTS_COVERAGE_ONLY", "summary_generated": False, "errors": [str(exc)], "boundary": boundary}, None
    coverage, accepted, sessions = [], {}, {}
    for job in jobs:
        try:
            if job["id"] in LOGICAL_JOBS:
                item, review = verify_replacement_job(job, start, schema, run_dir, root, resolution)
            else:
                item, review = frozen.verify_job(job, start, schema, run_dir, root)
            if review is not None:
                sid = review["evidence"]["session_id"]
                need(sid not in {item["failed_attempt"]["session_id"] for item in resolution["exceptions"].values()}, "Failed native session reused by accepted review")
                need(sid not in sessions, "Native session reused by another review")
                sessions[sid] = job["id"]
                accepted[job["id"]] = review
            coverage.append(item)
        except (ValueError, KeyError, TypeError, OSError) as exc:
            coverage.append({"job_id": job["id"], "manuscript_id": job["manuscript_id"], "role": job["role"], "profile_id": job["profile_id"],
                             "status": "INVALID_EVIDENCE_MISSING", "accepted": False, "errors": [str(exc)]})
    count = sum(x["accepted"] for x in coverage)
    counts = {status: sum(x["status"] == status for x in coverage) for status in sorted({x["status"] for x in coverage})}
    full = count == 110
    report = {"status": "COMPLETE_110_ACCEPTED" if full else "INCOMPLETE_COVERAGE_ONLY", "summary_generated": full,
              "expected_reviews": 110, "accepted_reviews": count, "preserved_failed_attempts": 2, "attempt_resolution": resolution_note(resolution), "missing_reviews": 110 - count, "status_counts": counts,
              "input_event_id": start["event_id"], "jobs": coverage, "boundary": boundary,
              "rule": "No score means, ranking, recommendations or concerns are emitted until all 110 reviews are accepted and verified."}
    if not full:
        return report, None
    rows = []
    for row in allocation:
        reviews = [accepted[row["blind_id"] + "-" + role] for role in ROLES]
        rows.append({"candidate": row["candidate"], "blind_id": row["blind_id"], "version": row["version"],
                     "metrics": aggregate(reviews), "reviews": reviews})
    summary = {"status": "COMPLETE_22_DESCRIPTIVE_SUMMARY", "candidate_count": 22, "review_count": 110, "preserved_failed_attempts": 2, "attempt_resolution": resolution_note(resolution),
               "order": "Frozen ALLOCATION row order; not score order or ranking.",
               "formula": "0.6 * mean(N1,N2,N3) + 0.4 * mean(J1,J2); equal one-fifth influence per complete review.",
               "originality_policy": "Any null makes that group's originality mean unknown and makes the combined originality unknown. No zero substitution, partial-group averaging or weight redistribution.",
               "rows": rows, "boundary": boundary}
    return report, summary



def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, default=DEFAULT_RUN)
    parser.add_argument("--map-receipt", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    run_dir = args.run_dir.resolve(); root = run_dir.parents[1]
    sys.path.insert(0, str(root / "scripts"))
    from research_archive import Archive
    from resolver_v2 import load_resolution
    archive = Archive(root / "research/archive")
    resolution = load_resolution(root, run_dir, args.map_receipt.resolve(), archive.events(), archive.get)
    coverage, summary = summarize(run_dir, resolution)
    frozen.write_outputs(args.output_dir, coverage, summary)
    print(json.dumps({k: v for k, v in coverage.items() if k not in {"jobs", "boundary", "rule"}}, ensure_ascii=False))


if __name__ == "__main__": main()
