#!/usr/bin/env python3
"""Versioned, narrow checkpoint finalizer for a bound v2 stage-name mismatch.

This does not edit a v2 plan or stage. It recognizes only the documented
``critique-001`` -> ``critic-001`` label equivalence when the archived stage is
actually phase/kind ``critique`` and independently recorded. It writes an
append-only correction, then the ordinary checkpoint and binding records.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
import sys

import hundred_artifacts_v2 as v2
import philosophy_round as rounds
from research_archive import Archive, ArchiveError, _read, sha

PROTOCOL = "hundred-checkpoint-alias.v3"
ALLOWED_ALIAS = {
    "required_stage": "critique-001",
    "actual_stage": "critic-001",
    "phase": "critique",
    "kind": "critique",
    "independent": True,
}


def resolve_required_stages(required, stages, aliases):
    """Resolve exact labels plus the one explicitly reviewed v2 alias."""
    by_name = {}
    for event in stages:
        name = event["payload"].get("stage")
        by_name.setdefault(name, []).append(event)

    resolutions = []
    for name in required:
        exact = by_name.get(name, [])
        if exact:
            if len(exact) != 1:
                raise ArchiveError("conflicting exact required stages: " + name)
            resolutions.append({"required_stage": name, "actual_stage": name,
                                "event_id": exact[0]["id"], "resolution": "exact"})
            continue

        matches = [a for a in aliases if a.get("required_stage") == name]
        if not matches:
            raise ArchiveError("required method stage is missing: " + name)
        if len(matches) != 1 or matches[0] != ALLOWED_ALIAS:
            raise ArchiveError("unsupported or ambiguous stage alias: " + name)
        alias = matches[0]
        candidates = by_name.get(alias["actual_stage"], [])
        candidates = [event for event in candidates
                      if event["payload"].get("phase") == alias["phase"]
                      and event["payload"].get("kind") == alias["kind"]
                      and event["payload"].get("independent") is alias["independent"]]
        if len(candidates) != 1:
            raise ArchiveError("stage alias lacks exactly one matching independent critique")
        resolutions.append({"required_stage": name, "actual_stage": alias["actual_stage"],
                            "event_id": candidates[0]["id"], "resolution": "documented-semantic-alias",
                            "phase": alias["phase"], "kind": alias["kind"],
                            "independent": alias["independent"]})
    return resolutions


def checkpoint(root, writer, request, request_bytes):
    run = v2.ident(request["run_id"])
    known, plan, first = v2.state(writer, run)
    if plan["payload"]["protocol"] != v2.PROTOCOL:
        raise ArchiveError("alias finalizer accepts only the exact bound v2 protocol")
    plan_request = plan["payload"]["request"]
    requirements = plan_request["requirements"]
    if plan_request.get("topology") != "flexible":
        raise ArchiveError("this narrow alias finalizer supports only flexible v2 runs")

    errors = v2.validate(writer, run, complete=False)
    if errors:
        raise ArchiveError("v2 stage validation failed: " + "; ".join(errors))

    stages = [event for event in known.values()
              if event["run_id"] == run and event["kind"] == "hundred.stage"]
    resolutions = resolve_required_stages(requirements["required_stages"], stages,
                                          request.get("stage_aliases", []))
    final = known.get(request["final_stage_event_id"])
    if final not in stages or final["payload"].get("phase") not in ("final", "revision", "draft"):
        raise ArchiveError("select one exact final manuscript stage")
    family = v2.ancestors(known, [final["id"]])
    critics = {event["session_id"] for event in family
               if event["payload"].get("phase") == "critique"
               and event["payload"].get("independent") is True}
    if len(critics) < requirements["minimum_independent_critiques"]:
        raise ArchiveError("selected final omits required independent critics")

    summary_path = rounds.local(root, request["summary"])
    if not summary_path.is_relative_to(rounds.local(root, plan_request["directory"])):
        raise ArchiveError("checkpoint summary must belong to the entity")
    summary_bytes = _read(summary_path)
    summary = json.loads(summary_bytes)
    correction_note_path = rounds.local(root, request["correction_note"])
    correction_note_bytes = _read(correction_note_path)
    for key in ("question", "outcome", "contribution", "criticism", "limitations",
                "next_step", "method_change", "comparability", "coverage_boundary"):
        v2.nonempty(summary.get(key), "checkpoint " + key)
    if summary["outcome"] not in ("CONTINUE", "REVISE", "SET_ASIDE", "COMPLETE_TECHNICAL"):
        raise ArchiveError("unsupported checkpoint outcome")
    if summary["outcome"] == "COMPLETE_TECHNICAL" and first["payload"]["purpose"] != "technical":
        raise ArchiveError("technical outcome requires technical purpose")

    existing_cp = [event for event in known.values()
                   if event["run_id"] == run and event["kind"] == "checkpoint"]
    existing_binding = [event for event in known.values()
                        if event["run_id"] == run and event["kind"] == "hundred.checkpoint_binding"]
    if existing_cp or existing_binding:
        raise ArchiveError("checkpoint already exists; do not apply the alias finalizer twice")
    v2.open_run(known, first)

    aliases = request.get("stage_aliases", [])
    correction_body = {
        "protocol": PROTOCOL,
        "run_id": run,
        "plan_event_id": plan["id"],
        "required_stages": requirements["required_stages"],
        "resolutions": resolutions,
        "reason": request["reason"],
        "scope": "Mechanical required-stage label correction only; no manuscript, method or critic content changed.",
    }
    correction_outputs = [writer.put(request_bytes), writer.put(correction_note_bytes),
                         writer.put(_read(summary_path)),
                         writer.put(_read(Path(__file__).resolve()))]
    correction = rounds.envelope(first, "correction", session=request["session_id"], role="tool",
        parents=[plan["id"]] + [r["event_id"] for r in resolutions], payload=correction_body)
    correction["outputs"] = correction_outputs
    correction = writer.append(correction, "hundred-stage-label-correction:" + run)
    known[correction["id"]] = correction

    coverage = v2.unique(event["payload"]["capture"]["coverage_event_id"] for event in stages)
    old = next((event for event in known.values()
                if event["run_id"] == run and event["kind"] == "checkpoint"), None)
    checkpoint_event = rounds.envelope(first, "checkpoint",
        parents=[first["id"]] + [event["id"] for event in stages] + coverage + [correction["id"]],
        payload={"protocol": PROTOCOL,
                 "research_date": dt.datetime.now(dt.timezone.utc).date().isoformat(),
                 "summary": summary, "capture_status": "BOUNDED_COMPLETE",
                 "purpose": first["payload"]["purpose"], "truth_status": "NOT_CERTIFIED",
                 "topology": "flexible", "method_exemptions": requirements["method_exemptions"],
                 "final_stage_event_id": final["id"]})
    checkpoint_event["outputs"] = [writer.put(summary_bytes)]
    if old:
        if (old["outputs"] != checkpoint_event["outputs"]
                or old["parents"] != checkpoint_event["parents"]
                or old["payload"].get("final_stage_event_id") != final["id"]):
            raise ArchiveError("immutable checkpoint conflict")
        checkpoint_event = old
    else:
        checkpoint_event = writer.append(checkpoint_event, "checkpoint:" + run)
    known[checkpoint_event["id"]] = checkpoint_event

    writer.append(rounds.envelope(first, "operation.completed",
        parents=[first["id"], checkpoint_event["id"], correction["id"]],
        payload={"checkpoint": checkpoint_event["id"], "outcome": summary["outcome"],
                 "scope": "Selected manuscript workflow complete under bound method; no truth or eligibility certificate"}),
        "round-terminal:" + run)

    binding = rounds.envelope(first, "hundred.checkpoint_binding",
        parents=[checkpoint_event["id"], plan["id"]] + [event["id"] for event in stages]
                + [correction["id"]],
        payload={"protocol": PROTOCOL, "checkpoint_event_id": checkpoint_event["id"],
                 "final_stage_event_id": final["id"],
                 "method_exemptions": requirements["method_exemptions"],
                 "stage_label_resolutions": resolutions,
                 "correction_event_id": correction["id"]})
    writer.append(binding, "hundred-checkpoint-binding:" + run)

    final_errors = v2.validate(writer, run, complete=True)
    if final_errors:
        raise ArchiveError("post-checkpoint v2 validation failed: " + "; ".join(final_errors))
    return {"protocol": PROTOCOL, "run_id": run, "ok": True,
            "correction_event_id": correction["id"],
            "checkpoint_event_id": checkpoint_event["id"],
            "final_stage_event_id": final["id"],
            "coverage_event_ids": coverage,
            "stage_label_resolutions": resolutions,
            "validation": {"complete": True, "ok": True, "errors": []}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--request", required=True)
    parser.add_argument("--receipt")
    args = parser.parse_args()
    root = args.root.absolute()
    try:
        request_path = rounds.local(root, args.request)
        request_bytes = _read(request_path)
        request = json.loads(request_bytes)
        if request.get("protocol") != PROTOCOL:
            raise ArchiveError("request must bind the exact alias-finalizer protocol")
        if request.get("stage_aliases") != [ALLOWED_ALIAS]:
            raise ArchiveError("request must contain only the reviewed exact critique label alias")
        if not isinstance(request.get("reason"), str) or not request["reason"].strip():
            raise ArchiveError("correction reason is required")
        with Archive(root / "research/archive").writer() as writer, v2.cached_events(writer):
            result = checkpoint(root, writer, request, request_bytes)
        rendered = json.dumps(result, sort_keys=True, ensure_ascii=False) + "\n"
        if args.receipt:
            receipt_path = rounds.local(root, args.receipt)
            receipt_path.parent.mkdir(parents=True, exist_ok=True)
            receipt_path.write_text(rendered, encoding="utf-8")
        print(rendered, end="")
        return 0
    except (ValueError, KeyError, OSError, TypeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, sort_keys=True), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
