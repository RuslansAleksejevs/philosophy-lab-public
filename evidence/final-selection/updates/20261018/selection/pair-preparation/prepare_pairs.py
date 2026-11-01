"""Mechanically prepare preselected pairs; never select pairs, launch or archive.

PAIR_PLAN: {batch_id, pairs:[{pair_id, candidate_ids:[id,id], rationale,
profiles:[slug,slug], order_by_role:{N1:[A_id,B_id], N2:..., N3:..., J1:..., J2:...}}]}.
Output is a new immutable pair-batches/<batch_id> directory. Root must archive
its inputs and create the explicit input receipt before any reviewer dispatch.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import fcntl
import hashlib
import json
import os
import re

HERE = Path(__file__).resolve().parent
RUN = HERE.parent
ROOT = RUN.parents[1]
ROLES = ("N1", "N2", "N3", "J1", "J2")
PROFILE_NAMES = ("profile-v1.md", "source-evidence.md", "evidence-packet.md", "source-packet.md", "baseline-profile-20260912.md")


def require(value, message):
    if not value:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def encode(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode()


def load(data):
    def pairs(rows):
        result = {}
        for key, value in rows:
            require(key not in result, "Duplicate JSON key")
            result[key] = value
        return result
    return json.loads(data, object_pairs_hook=pairs)


def read(path, root=ROOT):
    path = Path(path).absolute()
    require(path.is_relative_to(root) and ".." not in path.parts, "Path outside project")
    require(not any(p.is_symlink() for p in (path, *path.parents)) and path.is_file(), "Missing or unsafe file: " + str(path))
    return path.read_bytes()


def write_new(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as out:
        out.write(data); out.flush(); os.fsync(out.fileno())


def file_record(path, data, root):
    return {"path": str(path.relative_to(root)), "sha256": sha(data), "bytes": len(data)}


def prior_batches(run_dir, root):
    pairs, pair_ids, jobs, manifests = set(), set(), set(), []
    base = run_dir / "pair-batches"
    if not base.exists():
        return pairs, pair_ids, jobs, manifests
    require(not base.is_symlink(), "Unsafe pair-batches directory")
    for directory in sorted(base.iterdir()):
        require(directory.is_dir() and not directory.is_symlink(), "Unexpected item in pair-batches")
        path = directory / "PAIR_PREPARATION.json"
        data = read(path, root)
        manifest = load(data)
        require(manifest.get("status") == "PAIR_PACKETS_PREPARED_NOT_ARCHIVED", "Unknown prior preparation status")
        for entry in manifest["files"]:
            require(sha(read(root / entry["path"], root)) == entry["sha256"], "Prior prepared file changed")
        require(manifest["jobs"] == 5 * len(manifest["pairs"]), "Prior pair job count differs")
        for entry in manifest["pairs"]:
            key = tuple(sorted(entry["candidate_ids"]))
            require(len(key) == 2 and key[0] != key[1] and key not in pairs and entry["pair_id"] not in pair_ids, "Duplicate prior pair")
            pairs.add(key); pair_ids.add(entry["pair_id"])
            for role in ROLES:
                jid = entry["pair_id"] + "-" + role
                require(jid not in jobs, "Duplicate prior job")
                jobs.add(jid)
        manifests.append(file_record(path, data, root))
    require(len(pairs) <= 10 and len(jobs) <= 50, "Existing pair ceiling exceeded")
    return pairs, pair_ids, jobs, manifests


def validate_plan(plan, candidates, profiles, prior):
    require(isinstance(plan, dict) and set(plan) == {"batch_id", "pairs"}, "Plan must contain only batch_id and pairs")
    require(isinstance(plan["batch_id"], str) and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,60}", plan["batch_id"]), "Unsafe batch_id")
    require(isinstance(plan["pairs"], list) and 1 <= len(plan["pairs"]) <= 10, "Plan requires 1–10 pairs")
    keys, identities, jobs = (set(x) for x in prior[:3])
    for pair in plan["pairs"]:
        require(isinstance(pair, dict) and set(pair) == {"pair_id", "candidate_ids", "rationale", "profiles", "order_by_role"}, "Pair fields differ from interface")
        pid, ids, judges, orders = pair["pair_id"], pair["candidate_ids"], pair["profiles"], pair["order_by_role"]
        require(isinstance(pid, str) and re.fullmatch(r"P[0-9]{2,3}", pid) and pid not in identities, "Invalid/reused pair_id")
        require(isinstance(ids, list) and len(ids) == 2 and all(isinstance(x, str) and x in candidates for x in ids) and len(set(ids)) == 2, "Pair must name two distinct frozen candidate IDs")
        key = tuple(sorted(ids))
        require(key not in keys, "Unordered pair already prepared")
        require(isinstance(pair["rationale"], str) and pair["rationale"].strip(), "Root rationale required")
        require(isinstance(judges, list) and len(judges) == 2 and len(set(judges)) == 2 and all(x in profiles for x in judges), "Two distinct frozen profiles required")
        require(isinstance(orders, dict) and set(orders) == set(ROLES), "An A/B order is required for all five roles")
        for role in ROLES:
            order = orders[role]
            require(isinstance(order, list) and len(order) == 2 and set(order) == set(ids), "Order must be an exact permutation of this pair")
            jid = pid + "-" + role
            require(jid not in jobs, "Review ID reused")
            jobs.add(jid)
        count = sum(orders[role][0] == ids[0] for role in ROLES)
        require(count in (2, 3), "A/B assignments must balance 3:2")
        require(orders["J1"][0] != orders["J2"][0], "The two profile roles require opposite A/B order")
        keys.add(key); identities.add(pid)
    require(len(keys) <= 10 and len(jobs) <= 50, "Cumulative ceiling is 10 distinct pairs / 50 reviews")


def source_state(run_dir, root):
    start_path = run_dir / "START_RECEIPT.json"
    start_bytes = read(start_path, root)
    start = load(start_bytes)
    require(start.get("status") == "SELECTION_INPUTS_ARCHIVED" and start.get("event_id"), "Initial inputs must already be archived")
    frozen = {str((root / item["path"]).absolute()): item["sha256"] for item in start["files"]}
    sources = [file_record(start_path, start_bytes, root)]
    def original(name):
        path = run_dir / name
        data = read(path, root)
        require(frozen.get(str(path)) == sha(data), "Initial frozen file absent or changed: " + name)
        sources.append(file_record(path, data, root))
        return data
    allocation = load(original("ALLOCATION.json"))["rows"]
    candidates = {row["candidate"]: row for row in allocation}
    require(len(candidates) == len(allocation), "Duplicate candidate allocation")
    queue = load(original("queue.json"))["jobs"]
    profile_sources = {}
    for job in queue:
        profile = job.get("profile_id")
        if profile == "neutral" or job.get("phase") != "individual":
            continue
        require(isinstance(profile, str) and re.fullmatch(r"[a-z][a-z0-9_]*", profile), "Unsafe profile slug")
        expected_dir = root / "research/judges/20261007" / profile
        files = [x for x in job["input_sources"] if (root / x["path"]).parent == expected_dir and Path(x["path"]).name in PROFILE_NAMES]
        require(any(Path(x["path"]).name == "profile-v1.md" for x in files), "Frozen profile-v1.md missing")
        files = sorted(files, key=lambda x: PROFILE_NAMES.index(Path(x["path"]).name))
        if profile in profile_sources:
            require(profile_sources[profile] == files, "Profile materials differ between original jobs")
        profile_sources[profile] = files
    return candidates, profile_sources, original("RUBRIC.txt"), frozen, sources, start["event_id"]


def prepare(plan_path, output_dir=None, run_dir=RUN, root=ROOT, template_dir=HERE):
    run_dir, root, template_dir = Path(run_dir).absolute(), Path(root).absolute(), Path(template_dir).absolute()
    require(run_dir.is_relative_to(root) and template_dir.is_relative_to(run_dir), "Invalid generator location")
    plan_path = Path(plan_path).absolute()
    require(plan_path.is_relative_to(run_dir), "PAIR_PLAN must be inside the run directory")
    plan_bytes = read(plan_path, root)
    plan = load(plan_bytes)
    # This is a local preparation lock, never the canonical archive writer.
    with (template_dir / ".prepare.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        candidates, profiles, common, frozen, sources, initial_event = source_state(run_dir, root)
        prior = prior_batches(run_dir, root)
        validate_plan(plan, candidates, profiles, prior)
        destination = run_dir / "pair-batches" / plan["batch_id"]
        if output_dir is not None:
            requested = Path(output_dir)
            requested = requested.absolute() if requested.is_absolute() else run_dir / requested
            require(requested == destination, "Output must be pair-batches/<batch_id> inside this run")
        require(not destination.exists() and not destination.is_symlink(), "Never overwrite an existing prepared batch")
        schema_path = template_dir / "pair-schema.template.json"
        template_path = template_dir / "pair-rubric.template.txt"
        schema_bytes, template_bytes = read(schema_path, root), read(template_path, root)
        schema = load(schema_bytes)
        rubric = common + b"\n\n" + template_bytes
        generated = {"PAIR_PLAN.json": plan_bytes, "pair-schema.json": schema_bytes, "PAIR_RUBRIC.txt": rubric}
        source_map = {x["path"]: x for x in sources + prior[3]}
        for path in (plan_path, template_dir / "prepare_pairs.py", schema_path, template_path):
            data = read(path, root); source_map[str(path.relative_to(root))] = file_record(path, data, root)
        manuscripts, profile_texts = {}, {}
        for pair in plan["pairs"]:
            for cid in pair["candidate_ids"]:
                if cid in manuscripts:
                    continue
                row = candidates[cid]; mid = row["blind_id"]
                require(re.fullmatch(r"M[0-9]{2}", mid), "Unsafe blind manuscript ID")
                path = run_dir / "blind" / (mid + ".md")
                data = read(path, root)
                require(frozen.get(str(path)) == sha(data) == row["version"]["sha256"], "Frozen full manuscript/version changed")
                data.decode("utf-8")  # Validate encoding without normalizing or rewriting any bytes.
                manuscripts[cid] = (mid, path, data)
                source_map[str(path.relative_to(root))] = file_record(path, data, root)
            for profile in pair["profiles"]:
                if profile in profile_texts:
                    continue
                pieces = []
                for item in profiles[profile]:
                    path = root / item["path"]; data = read(path, root)
                    require(sha(data) == item["sha256"], "Frozen profile material changed")
                    data.decode("utf-8")
                    pieces.append(("SOURCE-GROUNDED PROFILE MATERIAL " + path.name + "\n").encode() + data)
                    source_map[item["path"]] = file_record(path, data, root)
                profile_texts[profile] = (b"You are an AI reviewer informed by the following sourced profile, not the actual person. Approximate the evidenced intellectual approach, but give no bonus for doctrinal agreement. Apply the same depth and common criteria as a neutral reviewer. Do not treat profile preferences as factual proof.\n" + b"\n\n".join(pieces))
        jobs, summary = [], []
        for pair in plan["pairs"]:
            pid = pair["pair_id"]
            summary.append({key: pair[key] for key in ("pair_id", "candidate_ids", "profiles", "order_by_role")})
            for role in ROLES:
                profile = "neutral" if role.startswith("N") else pair["profiles"][int(role[1]) - 1]
                jid = pid + "-" + role
                ordered = [manuscripts[cid] for cid in pair["order_by_role"][role]]
                persona = (b"No named judge persona. Apply the common criteria without adopting any particular philosopher's preferences." if profile == "neutral" else profile_texts[profile])
                identity = ("\n\nReview identity: " + jid + "\nPair identity: " + pid + "\nProfile identity: " + profile + "\nText A identity: " + ordered[0][0] + "\nText B identity: " + ordered[1][0] + "\n\n").encode()
                prompt = rubric + identity + persona + b"\n\nREQUIRED PAIR JSON SCHEMA\n" + json.dumps(schema, ensure_ascii=False).encode() + b"\n"
                spans = []
                for label, (mid, path, data) in zip(("A", "B"), ordered):
                    prompt += ("\nFULL MANUSCRIPT " + label + " (" + mid + ") — BEGIN\n").encode()
                    start = len(prompt)
                    prompt += data
                    spans.append({"label": label, "blind_id": mid, "start_byte": start, "end_byte": len(prompt), "sha256": sha(data), "bytes": len(data)})
                    require(prompt[start:len(prompt)] == data, "Literal manuscript-byte preservation failed")
                    prompt += ("\nFULL MANUSCRIPT " + label + " — END\n").encode()
                prompt_name = "packets/" + jid + ".txt"
                generated[prompt_name] = prompt
                inputs = [file_record(path, data, root) for _, path, data in ordered]
                if profile != "neutral":
                    inputs += [source_map[x["path"]] for x in profiles[profile]]
                jobs.append({"id": jid, "phase": "pair", "pair_id": pid, "role": role, "profile_id": profile,
                             "model": "gpt-6-astra", "effort": "ultra", "service_tier": "default",
                             "pair_candidates": pair["candidate_ids"], "ordered_blind_ids": [x[0] for x in ordered],
                             "expected_output": {"review_id": jid, "pair_id": pid, "profile_id": profile},
                             "prompt_file": str((destination / prompt_name).relative_to(root)), "prompt_sha256": sha(prompt),
                             "schema_file": str((destination / "pair-schema.json").relative_to(root)), "schema_sha256": sha(schema_bytes),
                             "rubric_file": str((destination / "PAIR_RUBRIC.txt").relative_to(root)), "rubric_sha256": sha(rubric),
                             "input_sources": inputs, "manuscript_spans": spans})
        generated["queue.json"] = encode({"run_id": run_dir.name, "batch_id": plan["batch_id"], "status": "PREPARED_NOT_DISPATCHED", "jobs": jobs})
        records = [file_record(destination / name, data, root) for name, data in generated.items()]
        report = {"status": "PAIR_PACKETS_PREPARED_NOT_ARCHIVED", "prepared_at": datetime.now(timezone.utc).isoformat(),
                  "batch_id": plan["batch_id"], "initial_input_event": initial_event, "plan_sha256": sha(plan_bytes),
                  "pairs": summary, "jobs": len(jobs), "cumulative_pairs": len(prior[0]) + len(summary), "cumulative_jobs": len(prior[2]) + len(jobs),
                  "files": records, "source_files": list(source_map.values()), "model_calls": 0, "archive_writes": 0,
                  "boundary": "Root selected pairs/profiles/order. Rationale retained only in plan. Full frozen manuscript bytes included literally; no old reviews/scores/history supplied. No ready receipt is created."}
        destination.mkdir(parents=True, exist_ok=False)
        for name, data in generated.items():
            write_new(destination / name, data)
        write_new(destination / "PAIR_PREPARATION.json", encode(report))
        return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    report = prepare(args.plan, args.output_dir)
    print(json.dumps({k: report[k] for k in ("status", "batch_id", "jobs", "cumulative_pairs", "cumulative_jobs")}))


if __name__ == "__main__":
    main()
