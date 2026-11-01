#!/usr/bin/env python3
"""Verify individual review receipts and summarize only a complete 110-review set.

No model calls, archive writes/reads, candidate choices or ranks. Standalone
manuscript files are not opened; frozen packet bytes are hashed, not interpreted.
All reads are local input/receipt/review files. Output folders are new only.
"""
from pathlib import Path
from fractions import Fraction
import argparse
import hashlib
import json
import math
import re

DEFAULT_RUN = Path(__file__).resolve().parent.parent
ROLES = ("N1", "N2", "N3", "J1", "J2")
METRICS = ("overall", "argument", "significance")
COMPLETE = "COMPLETE_LOCAL_PENDING_CANONICAL_ARCHIVE"
HEX = re.compile(r"[a-f0-9]{64}")


class InvalidEvidence(ValueError):
    pass


def need(condition, message):
    if not condition:
        raise InvalidEvidence(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def strict(data):
    def pairs(items):
        out = {}
        for key, value in items:
            need(key not in out, "Duplicate JSON key: " + key)
            out[key] = value
        return out
    def constant(value):
        raise InvalidEvidence("Non-finite JSON number")
    result = json.loads(data, object_pairs_hook=pairs, parse_constant=constant)
    def finite(value):
        if isinstance(value, dict):
            for item in value.values():
                finite(item)
        elif isinstance(value, list):
            for item in value:
                finite(item)
        elif type(value) is float:
            need(math.isfinite(value), "Non-finite JSON number")
    finite(result)
    return result


def read(path, root):
    path, root = Path(path).absolute(), Path(root).absolute()
    need(path.is_relative_to(root) and ".." not in path.parts, "Path outside the bound project")
    need(not any(p.is_symlink() for p in (path, *path.parents)) and path.is_file(), "Missing or unsafe file: " + path.name)
    return path.read_bytes()


def load(path, root):
    return strict(read(path, root))


def json_schema(value, schema, location="$"):
    """The narrow vocabulary used by the frozen individual-review schema."""
    allowed = {"type", "required", "properties", "additionalProperties", "items", "minItems", "maxItems", "enum", "minimum", "maximum"}
    need(isinstance(schema, dict) and set(schema) <= allowed, "Unsupported review schema")
    kinds = {"object": lambda x: isinstance(x, dict), "array": lambda x: isinstance(x, list),
             "string": lambda x: isinstance(x, str), "integer": lambda x: type(x) is int,
             "boolean": lambda x: type(x) is bool, "null": lambda x: x is None}
    types = schema.get("type")
    if types is not None:
        types = [types] if isinstance(types, str) else types
        need(isinstance(types, list) and types and all(t in kinds for t in types) and any(kinds[t](value) for t in types), "Wrong type at " + location)
    if "enum" in schema:
        need(any(type(value) is type(x) and value == x for x in schema["enum"]), "Invalid enum at " + location)
    if isinstance(value, dict):
        need(set(schema.get("required", [])) <= set(value), "Missing required review field at " + location)
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            need(set(value) <= set(properties), "Unknown review field at " + location)
        for key, item in value.items():
            if key in properties:
                json_schema(item, properties[key], location + "." + key)
    if isinstance(value, list):
        need(schema.get("minItems", 0) <= len(value) <= schema.get("maxItems", math.inf), "Invalid array size at " + location)
        for item in value:
            json_schema(item, schema.get("items", {}), location + "[]")
    if type(value) is int:
        need(schema.get("minimum", -math.inf) <= value <= schema.get("maximum", math.inf), "Score outside bounds at " + location)


def inputs(run_dir):
    run_dir = Path(run_dir).absolute()
    root = run_dir.parents[1]
    start = load(run_dir / "START_RECEIPT.json", root)
    need(start.get("status") == "SELECTION_INPUTS_ARCHIVED" and start.get("event_id"), "Input acceptance receipt missing")
    frozen = {}
    for item in start["files"]:
        path = root / item["path"]
        need(path not in frozen and isinstance(item.get("sha256"), str) and HEX.fullmatch(item["sha256"]), "Duplicate/invalid frozen input")
        frozen[path] = item["sha256"]
    for name in ("queue.json", "ALLOCATION.json", "review-schema.json"):
        path = run_dir / name
        need(path in frozen and digest(read(path, root)) == frozen[path], "Unbound/changed " + name)
    queue = load(run_dir / "queue.json", root)
    allocation = load(run_dir / "ALLOCATION.json", root)["rows"]
    schema = load(run_dir / "review-schema.json", root)
    jobs = queue["jobs"]
    need(len(jobs) == 110 and len({j["id"] for j in jobs}) == 110, "Expected 110 unique individual jobs")
    need(len(allocation) == 22 and len({r["candidate"] for r in allocation}) == 22 and len({r["blind_id"] for r in allocation}) == 22, "Expected 22 unique candidates and blinded IDs")
    need(queue.get("run_id") == run_dir.name, "Queue/run identity mismatch")
    seen_prompts = set()
    for row in allocation:
        group = [j for j in jobs if j.get("manuscript_id") == row["blind_id"]]
        need(len(group) == 5 and {j.get("role") for j in group} == set(ROLES), "Each manuscript needs exactly N1,N2,N3,J1,J2")
        need(len(row["profiles"]) == len(set(row["profiles"])) == 2, "Two distinct assigned profiles required")
        for job in group:
            need(job.get("phase") == "individual" and job["id"] == row["blind_id"] + "-" + job["role"], "Job identity/phase mismatch")
            expected_profile = "neutral" if job["role"].startswith("N") else row["profiles"][int(job["role"][1]) - 1]
            need(job.get("profile_id") == expected_profile, "Assigned profile mismatch")
            need(job["prompt_file"] not in seen_prompts, "Duplicate prompt path")
            seen_prompts.add(job["prompt_file"])
            for field in ("prompt", "schema"):
                path = root / job[field + "_file"]
                need(frozen.get(path) == job[field + "_sha256"] and digest(read(path, root)) == job[field + "_sha256"], "Frozen prompt/schema mismatch")
            need(job["schema_sha256"] == frozen[run_dir / "review-schema.json"], "Individual schema differs")
    need(len(seen_prompts) == 110, "Unassigned or extra jobs")
    return root, start, allocation, jobs, schema


def verify_job(job, start, schema, run_dir, root):
    lane = run_dir / "results" / job["id"]
    attempt = lane / "attempt-001"
    base = {"job_id": job["id"], "manuscript_id": job["manuscript_id"], "role": job["role"], "profile_id": job["profile_id"]}
    archive_path = lane / "ARCHIVE_RECEIPT.json"
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
    need(archive.get("input_event_id") == start["event_id"], "Review bound to a different input acceptance")
    for key in ("event_id", "lineage_event_id", "lineage_entry_id", "session_id"):
        need(isinstance(archive.get(key), str) and bool(archive[key]), "Missing accepted evidence reference: " + key)
    need(archive["lineage_entry_id"] == run_dir.name + ":" + job["id"] + ":evaluation-v1", "Evaluation lineage identity mismatch")
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
    capture_bytes = read(lane / "CAPTURE_RECEIPT.json", root)
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
    evidence = {"archive_receipt": str(archive_path.relative_to(root)), "archive_receipt_sha256": digest(read(archive_path, root)),
                "event_id": archive["event_id"], "lineage_event_id": archive["lineage_event_id"], "lineage_entry_id": archive["lineage_entry_id"],
                "session_id": archive["session_id"], "response_file": str((attempt / "response.json").relative_to(root)),
                "response_sha256": bound[attempt / "response.json"], "prompt_sha256": job["prompt_sha256"], "schema_sha256": job["schema_sha256"],
                "capture_sha256": archive["capture_sha256"], "capture_evidence_events": capture["evidence_events"]}
    return {**base, "status": "ACCEPTED_VERIFIED", "accepted": True, "evidence": evidence}, {"role": job["role"], "profile_id": job["profile_id"], "response": value, "evidence": evidence}


def mean_complete(values):
    return None if any(v is None for v in values) else Fraction(sum(values), len(values))


def aggregate(reviews):
    need(len(reviews) == 5 and {r["role"] for r in reviews} == set(ROLES), "Cannot aggregate incomplete/duplicate roles")
    by_role = {r["role"]: r for r in reviews}
    result = {}
    for metric in (*METRICS, "originality"):
        neutral = [by_role[r]["response"]["scores"][metric] for r in ROLES[:3]]
        profile = [by_role[r]["response"]["scores"][metric] for r in ROLES[3:]]
        n, j = mean_complete(neutral), mean_complete(profile)
        combined = None if n is None or j is None else Fraction(3, 5) * n + Fraction(2, 5) * j
        result[metric] = {"neutral_mean": None if n is None else float(n), "profile_mean": None if j is None else float(j),
                          "combined_60_40": None if combined is None else float(combined),
                          "neutral_known": sum(v is not None for v in neutral), "neutral_required": 3,
                          "profile_known": sum(v is not None for v in profile), "profile_required": 2}
    return result


def summarize(run_dir=DEFAULT_RUN):
    run_dir = Path(run_dir).absolute()
    boundary = "Local accepted receipts and all bound file hashes verified. Referenced canonical events are reported, not reread or independently re-audited. No ranking or selection."
    try:
        root, start, allocation, jobs, schema = inputs(run_dir)
    except (ValueError, KeyError, TypeError, OSError) as exc:
        return {"status": "INVALID_INPUTS_COVERAGE_ONLY", "summary_generated": False, "errors": [str(exc)], "boundary": boundary}, None
    coverage, accepted, sessions = [], {}, {}
    for job in jobs:
        try:
            item, review = verify_job(job, start, schema, run_dir, root)
            if review is not None:
                sid = review["evidence"]["session_id"]
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
              "expected_reviews": 110, "accepted_reviews": count, "missing_reviews": 110 - count, "status_counts": counts,
              "input_event_id": start["event_id"], "jobs": coverage, "boundary": boundary,
              "rule": "No score means, ranking, recommendations or concerns are emitted until all 110 reviews are accepted and verified."}
    if not full:
        return report, None
    rows = []
    for row in allocation:
        reviews = [accepted[row["blind_id"] + "-" + role] for role in ROLES]
        rows.append({"candidate": row["candidate"], "blind_id": row["blind_id"], "version": row["version"],
                     "metrics": aggregate(reviews), "reviews": reviews})
    summary = {"status": "COMPLETE_22_DESCRIPTIVE_SUMMARY", "candidate_count": 22, "review_count": 110,
               "order": "Frozen ALLOCATION row order; not score order or ranking.",
               "formula": "0.6 * mean(N1,N2,N3) + 0.4 * mean(J1,J2); equal one-fifth influence per complete review.",
               "originality_policy": "Any null makes that group's originality mean unknown and makes the combined originality unknown. No zero substitution, partial-group averaging or weight redistribution.",
               "rows": rows, "boundary": boundary}
    return report, summary


def write_outputs(destination, coverage, summary):
    destination = Path(destination).absolute()
    need(".." not in destination.parts and not any(p.is_symlink() for p in (destination, *destination.parents)), "Unsafe output directory")
    need(not destination.exists(), "Output directory already exists; choose a new snapshot name")
    destination.mkdir(parents=True)
    outputs = {"coverage.json": coverage}
    if summary is not None:
        need(coverage.get("accepted_reviews") == 110 and coverage.get("summary_generated") is True, "Incomplete set cannot emit a summary")
        outputs["summary.json"] = summary
    for name, value in outputs.items():
        with (destination / name).open("x", encoding="utf-8") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
            stream.write("\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, default=DEFAULT_RUN)
    parser.add_argument("--output-dir", type=Path, required=True, help="New directory for this immutable coverage/summary snapshot")
    args = parser.parse_args()
    coverage, summary = summarize(args.run_dir)
    write_outputs(args.output_dir, coverage, summary)
    print(json.dumps({k: v for k, v in coverage.items() if k not in {"jobs", "boundary", "rule"}}, ensure_ascii=False))


if __name__ == "__main__":
    main()
