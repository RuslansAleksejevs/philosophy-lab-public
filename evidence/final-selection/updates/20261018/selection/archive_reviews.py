#!/usr/bin/env python3
"""Archive a finite batch of finished selection reviews. Never starts a model.

Usage: python3 -B archive_reviews.py --batch individual-001 --ids M01-N1 M01-N2
Use --check-only for read-only verification, including exact-ID native reads.
Pair queues additionally require the explicit metadata documented below.
"""
from pathlib import Path
import argparse
import fcntl
import importlib.util
import json
import os
import re
import sys

sys.dont_write_bytecode = True
RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from research_archive import Archive
from capture_codex import capture, classify as capture_classify, regular_file, resolve_session
from essay_lineage import base_entry, index, append as append_lineage

spec = importlib.util.spec_from_file_location("selection_runner_for_archive", RUN / "runner.py")
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)
sha, strict, encode = runner.digest, runner.strict_json, runner.encode
BOUNDARY = ("Exact visible content.text JSON-string tokens from the native source, with "
            "source-line hashes. Unsupported message envelopes, injected context, hidden "
            "reasoning and runtime fields are excluded. This is bounded visible-fragment "
            "capture, not standard-adapter BOUNDED_COMPLETE or a full provider trace.")


class AcceptanceGap(ValueError):
    pass


def require(condition, reason):
    if not condition:
        raise AcceptanceGap(reason)


def read(path, root=ROOT):
    return runner.regular(path, root).read_bytes()


def load(path, root=ROOT):
    return strict(read(path, root))


def save_once(path, value, root=ROOT):
    """Immutable, exact replay only; never replace an earlier receipt."""
    data = encode(value)
    if path.exists():
        require(read(path, root) == data, "Existing record differs: " + path.name)
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    runner.save_new(path, value)


def string_token(raw, path):
    """Locate one actual JSON string token by its structural path, without reserializing."""
    text = raw.decode("utf-8")
    decoder = json.JSONDecoder()

    def skip(position):
        while position < len(text) and text[position].isspace():
            position += 1
        return position

    def locate(position, remaining):
        position = skip(position)
        value, end = decoder.raw_decode(text, position)
        if not remaining:
            require(isinstance(value, str) and text[position] == '"', "Selected value is not a JSON string")
            return text[position:end].encode("utf-8")
        target, rest = remaining[0], remaining[1:]
        cursor = skip(position + 1)
        if isinstance(target, str) and isinstance(value, dict):
            while cursor < end and text[cursor] != "}":
                key, after_key = decoder.raw_decode(text, cursor)
                colon = skip(after_key)
                require(text[colon] == ":", "Malformed object while selecting native token")
                start = skip(colon + 1)
                if key == target:
                    return locate(start, rest)
                _, cursor = decoder.raw_decode(text, start)
                cursor = skip(cursor)
                if text[cursor] == ",":
                    cursor = skip(cursor + 1)
        elif type(target) is int and isinstance(value, list):
            for number in range(len(value)):
                if number == target:
                    return locate(cursor, rest)
                _, cursor = decoder.raw_decode(text, cursor)
                cursor = skip(cursor)
                if text[cursor] == ",":
                    cursor = skip(cursor + 1)
        raise AcceptanceGap("Native text path absent")

    strict(raw)  # Reject duplicate keys/non-finite values before interpreting any path.
    return locate(0, path)


def fragment(raw, visible):
    """Accept only known visible-message blocks; retain no unknown envelope bytes."""
    obj = strict(raw)
    payload = obj.get("payload", {})
    require(obj.get("type") == "response_item" and payload.get("type") == "message", "Unknown native message")
    role = payload.get("role")
    require(role == visible["role"] and role in {"user", "assistant"}, "Unknown native role")
    if role == "assistant":
        require(payload.get("phase") == visible.get("phase") and payload.get("phase") in {"commentary", "final", "final_answer"}, "Hidden/unknown assistant phase")
        require(payload.get("channel") not in {"analysis", "summary", "confidence"}, "Hidden assistant channel")
    content = payload.get("content")
    require(isinstance(content, list) and bool(content), "No visible native blocks")
    texts, tokens = [], []
    for number, item in enumerate(content):
        require(isinstance(item, dict) and {"type", "text"} <= set(item) and set(item) <= {"type", "text", "annotations", "logprobs"}, "Unsupported native content block")
        require(item.get("type") in ({"input_text", "text"} if role == "user" else {"output_text", "text"}) and isinstance(item.get("text"), str), "Unknown native text type")
        token = string_token(raw, ["payload", "content", number, "text"])
        require(strict(token) == item["text"], "Native token decoding mismatch")
        texts.append(item["text"])
        tokens.append(token)
    require("\n".join(texts) == visible["text"], "Native fragment differs from independently checked visible text")
    return tokens


def freeze_visible_fragments(session_id, expected_cwd, selections, destination):
    """Freeze selected known visible tokens before acquiring the canonical writer.

    selections: [{line, role, text, record_sha256, phase?}]. The source hash is
    mandatory. phase is required for assistant messages. Values of native
    passthrough/annotations/logprobs are never inspected or copied.
    Returns the saved JSON-serializable manifest; performs no archive/model call.
    """
    root, destination = Path(expected_cwd).absolute(), Path(destination).absolute()
    require(destination.is_relative_to(root) and ".." not in destination.parts, "Fragment destination outside authorized project")
    require(not any(p.is_symlink() for p in (destination, *destination.parents)), "Symlink fragment destination")
    require(isinstance(selections, list) and bool(selections), "No explicit visible selection")
    require(all(isinstance(x, dict) for x in selections), "Invalid visible selection")
    numbers = [x.get("line") for x in selections]
    require(all(type(n) is int and n >= 1 for n in numbers) and len(numbers) == len(set(numbers)), "Invalid/duplicate selected native lines")
    source = resolve_session(session_id, root)
    with regular_file(source) as stream:
        size = os.fstat(stream.fileno()).st_size
        require(size <= 64 * 1024 * 1024, "Native source exceeds bounded size")
        raw = stream.read(size)
        require(len(raw) == size and os.fstat(stream.fileno()).st_size == size, "Native source changed during fragment freeze")
    cutoff = raw.rfind(b"\n") + 1
    rows = raw[:cutoff].splitlines(keepends=True)
    require(rows and max(numbers) <= len(rows), "Selected line lacks complete original bytes")
    first = strict(rows[0])
    require(first.get("type") == "session_meta" and first.get("payload", {}).get("id") == session_id and first["payload"].get("cwd") == str(root), "Fragment source identity/cwd mismatch")
    records, pending = [], []
    for selected in selections:
        number = selected["line"]
        source_line = rows[number - 1]
        require(isinstance(selected.get("record_sha256"), str) and sha(source_line) == selected["record_sha256"], "Explicit native source-line hash mismatch")
        require(isinstance(selected.get("text"), str), "Expected visible plaintext missing")
        tokens = fragment(source_line, selected)
        parts = []
        for position, token in enumerate(tokens):
            path = destination / ("line-" + str(number) + "-part-" + str(position) + ".json-string.txt")
            pending.append((path, token))
            parts.append({"path": str(path.relative_to(root)), "sha256": sha(token), "bytes": len(token)})
        records.append({"source_line": number, "source_line_sha256": selected["record_sha256"],
                        "role": selected["role"], "phase": selected.get("phase"), "parts": parts,
                        "decoded_text_sha256": sha(selected["text"].encode()),
                        "expected_text_match": "EXACT", "capture_status": "EXACT_VISIBLE_JSON_STRING_FRAGMENTS"})
    manifest = {"format": "selection-visible-fragments.v1", "session_id": session_id,
                "status": "EXACT_VISIBLE_JSON_STRING_FRAGMENTS", "cwd_binding_verified": True,
                "records": records, "full_provider_capture": False, "boundary": BOUNDARY,
                "unselected_partial_tail_bytes": len(raw) - cutoff,
                "excluded_fields": ["internal_chat_message_metadata_passthrough", "annotations", "logprobs", "all other native envelope fields"]}
    destination.mkdir(parents=True, exist_ok=True)
    for path, token in pending:
        if path.exists():
            require(read(path, root) == token, "Existing native token differs")
        else:
            with path.open("xb") as out:
                out.write(token); out.flush(); os.fsync(out.fileno())
    save_once(destination / "manifest.json", manifest, root)
    return manifest


def native_selection(source, proof, visible, prompt, job, root=ROOT):
    """Read one bounded identified source; prepare standard capture or safe fragments."""
    with regular_file(source) as stream:
        size = os.fstat(stream.fileno()).st_size
        require(size <= 64 * 1024 * 1024, "Native source exceeds bounded size")
        raw = stream.read(size)
        require(os.fstat(stream.fileno()).st_size == size and len(raw) == size and raw.endswith(b"\n"), "Native source changed or has a partial tail")
    rows = raw.splitlines(keepends=True)
    again = runner.native_records(rows, proof["session_id"], prompt, job, root)
    require(again[0] == proof and again[1] == visible, "Native proof changed between checks")
    require(proof["prompt_lines"][0] < proof["final_lines"][0], "Native final precedes assigned prompt")
    selected = []
    for item in visible:
        line = item["line"]
        require(1 <= line <= len(rows) and sha(rows[line - 1]) == item["record_sha256"], "Native line hash differs")
        tokens = fragment(rows[line - 1], item)
        reason = capture_classify(strict(rows[line - 1]), line, set(), set())
        selected.append({"line": line, "record_sha256": item["record_sha256"], "role": item["role"],
                         "phase": item.get("phase"), "mode": "standard" if reason is None else "exact-visible-fragment",
                         "adapter_exclusion": reason, "tokens": tokens})
    require(len([x for x in selected if x["role"] == "user"]) == 1, "Prompt capture is not unique")
    return selected


def public_selection(selected):
    return [{**{k: v for k, v in item.items() if k != "tokens"},
             "token_sha256": [sha(token) for token in item["tokens"]]} for item in selected]


def versions_for(job, mapping, root=ROOT):
    if job.get("phase") == "pair":
        candidates, order = job.get("pair_candidates"), job.get("ordered_blind_ids")
        require(isinstance(candidates, list) and len(candidates) == len(set(candidates)) == 2, "PAIR_ARCHIVE_EXTENSION_REQUIRED: pair_candidates must name two candidates")
        require(isinstance(order, list) and len(order) == len(set(order)) == 2, "PAIR_ARCHIVE_EXTENSION_REQUIRED: ordered_blind_ids must fix the two-text order")
        require(isinstance(job.get("expected_output"), dict) and job["expected_output"].get("pair_id"), "PAIR_ARCHIVE_EXTENSION_REQUIRED: expected_output.pair_id missing")
        require(set(order) == {mapping[c]["blind_id"] for c in candidates}, "Pair order/candidates mismatch")
        candidates = sorted(candidates, key=lambda c: order.index(mapping[c]["blind_id"]))
        require(job.get("rubric_file") and job.get("rubric_sha256"), "PAIR_ARCHIVE_EXTENSION_REQUIRED: exact pair rubric missing")
    else:
        require(job.get("phase") == "individual", "Unsupported review phase")
        candidates = [c for c, row in mapping.items() if row["blind_id"] == job.get("manuscript_id")]
        require(len(candidates) == 1, "Unknown individual blind ID")
    result = []
    for candidate in candidates:
        row = mapping[candidate]
        version = row["version"]
        require(sha(read(root / version["path"], root)) == version["sha256"], "Frozen assessed version changed")
        result.append({"candidate": candidate, "blind_id": row["blind_id"], "entry_id": row["assigned_entry"],
                       "sha256": version["sha256"], "path": version["path"], "entity": row["entity"], "assigned_event": row["assigned_event"]})
    return result


def prepare_job(job, mapping, run_dir=RUN, root=ROOT):
    attempt = run_dir / "results" / job["id"] / "attempt-001"
    receipt = load(attempt / "receipt.json", root)
    require(receipt.get("status") in {runner.COMPLETE, runner.QUARANTINED}, "Only finished local reviews are supported; failed/unfinished attempt requires root repair")
    runner.existing_disposition(job, run_dir, root)  # Checks recorded hashes and requested settings.
    outputs = receipt.get("outputs")
    require(isinstance(outputs, dict) and bool(outputs), "Output hash manifest absent")
    expected = {root / name for name in outputs}
    actual = set(attempt.iterdir())
    require(actual == expected | {attempt / "receipt.json"}, "Unexpected/unbound file inside finished attempt")
    required = {"launch.json", "native-check.json", "native-visible.json", "stderr.json", "visible-events.jsonl", "final.txt"}
    require(required <= {p.name for p in expected}, "Required visible evidence missing")
    files = [{"path": str(p.relative_to(root)), "sha256": sha(read(p, root)), "bytes": p.stat().st_size} for p in sorted(actual)]
    prompt, schema = runner.check_inputs(job, root)
    sid = receipt.get("session_id")
    require(isinstance(sid, str) and re.fullmatch(r"[A-Za-z0-9_-]{8,100}", sid), "Missing exact native session identity")
    launch = load(attempt / "launch.json", root)
    require(launch.get("job_id") == job["id"] and launch.get("prompt_sha256") == job["prompt_sha256"] and launch.get("schema_sha256") == job["schema_sha256"], "Launch identity differs")
    argv = launch.get("argv")
    require(isinstance(argv, list) and argv and argv == runner.command(job, attempt, root, executable=argv[0]), "Launch command differs from bound runner")
    require(launch.get("argv_sha256") == sha(json.dumps(argv, separators=(",", ":")).encode()) and receipt.get("argv") == argv, "Launch command digest differs")
    proof, visible, finals = runner.inspect_native(sid, prompt.decode(), job, root)
    require(not proof["isolation_failures"], "Native isolation/configuration check failed")
    require(load(attempt / "native-check.json", root) == proof, "Saved native proof differs from current source")
    require(load(attempt / "native-visible.json", root) == {"session_id": sid, "records": visible}, "Saved native visible capture differs")
    events = [strict(line) for line in read(attempt / "visible-events.jsonl", root).splitlines()]
    require(all(isinstance(e, dict) and not e.get("unexpected") for e in events), "Unexpected CLI event in finished review")
    require([e.get("thread_id") for e in events if e.get("type") == "thread.started"] == [sid], "CLI session identity mismatch")
    completed = len([e for e in events if e.get("type") == "turn.completed"]) == 1
    errors = [e["message"] for e in events if e.get("type") in {"error", "turn.failed"}]
    stderr = load(attempt / "stderr.json", root)
    require(isinstance(stderr.get("lines"), list) and all(isinstance(x, str) for x in stderr["lines"]), "Malformed stderr capture")
    require(stderr.get("exit_code") == receipt.get("cli_exit_code"), "CLI exit code mismatch")
    status, flags, value = runner.classify(finals, stderr["lines"], read(attempt / "final.txt", root).decode(), schema, errors, completed, stderr["exit_code"], job)
    require(status == receipt["status"] and flags == receipt.get("quality_flags"), "Local verdict does not reproduce")
    if status == runner.COMPLETE:
        require(value == load(attempt / "response.json", root), "Accepted response differs from native final")
        require(isinstance(value.get("reason_ru"), list) and len(value["reason_ru"]) >= 2 and all(isinstance(x, str) and x.strip() for x in value["reason_ru"]), "Concrete rationale absent")
        require(value.get("read_complete") is True, "Full reading not confirmed")
        require(("verdict" if job.get("phase") == "pair" else "recommendation") in value, "PAIR_ARCHIVE_EXTENSION_REQUIRED: verdict/recommendation absent")
    else:
        require(not (attempt / "response.json").exists(), "Quarantined review must not carry accepted response.json")
    versions = versions_for(job, mapping, root)
    source = resolve_session(sid, root)
    selected = native_selection(source, proof, visible, prompt.decode(), job, root)
    return {"job": job, "receipt": receipt, "files": files, "proof": proof, "value": value,
            "versions": versions, "source": source, "selected": selected}


def verify_files(files, root=ROOT):
    for item in files:
        data = read(root / item["path"], root)
        require(sha(data) == item["sha256"] and len(data) == item["bytes"], "Output changed during acceptance")


def capture_job(w, item, input_event, run_dir=RUN, root=ROOT):
    job, sid = item["job"], item["receipt"]["session_id"]
    cache = run_dir / "results" / job["id"] / "CAPTURE_RECEIPT.json"
    selection = public_selection(item["selected"])
    if cache.exists():
        prior = load(cache, root)
        require(prior.get("session_id") == sid and prior.get("selection") == selection, "Existing capture receipt differs")
        return prior
    records, evidence = [], []
    for selected in item["selected"]:
        number = selected["line"]
        if selected["mode"] == "standard":
            result = capture(root / "research/archive", item["source"], sid, root,
                             start_line=number, end_line=number, run_id=run_dir.name, archive_writer=w)
            require(result["status"] == "BOUNDED_COMPLETE" and result["captured_records"] == 1 and result["raw_records"][0]["sha256"] == selected["record_sha256"], "Standard native capture has a gap; root repair required")
            records.append({"mode": "standard", "line": number, "capture": result})
            evidence += [result["coverage_event_id"]] + result["raw_event_ids"] + result.get("run_binding_event_ids", [])
        else:
            hashes = [w.put(token) for token in selected["tokens"]]
            descriptor = {k: v for k, v in selected.items() if k != "tokens"}
            descriptor.update(token_sha256=hashes, boundary=BOUNDARY, status="EXACT_VISIBLE_JSON_STRING_FRAGMENTS")
            ev = w.append({"kind": "research.selection.visible_fragment.captured", "actor": {"id": "selection-capture", "role": "tool"},
                           "session_id": sid, "run_id": run_dir.name, "operation_id": "selection-fragment:" + sid + ":" + str(number),
                           "attempt_id": "visible-fragment-v1", "parents": [input_event], "outputs": hashes,
                           "payload": descriptor}, run_dir.name + ":fragment:" + sid + ":" + str(number))
            records.append({"mode": "exact-visible-fragment", "line": number, "event_id": ev["id"], **descriptor})
            evidence.append(ev["id"])
    result = {"status": "BOUNDED_VISIBLE_CAPTURE_ACCEPTED", "session_id": sid, "selection": selection,
              "records": records, "evidence_events": list(dict.fromkeys(evidence)), "boundary": BOUNDARY,
              "full_provider_capture": False, "standard_adapter_complete_for_all_records": all(x["mode"] == "standard" for x in item["selected"])}
    save_once(cache, result, root)
    return result


def canonical_capture_check(report, events, w):
    require(report.get("evidence_events") and all(e in events for e in report["evidence_events"]), "Capture evidence absent from canonical archive")
    selection = {x["line"]: x for x in report["selection"]}
    for record in report["records"]:
        selected = selection[record["line"]]
        if record["mode"] == "exact-visible-fragment":
            ev = events[record["event_id"]]
            require(ev["kind"] == "research.selection.visible_fragment.captured" and ev["session_id"] == report["session_id"] and ev["outputs"] == selected["token_sha256"], "Canonical fragment binding mismatch")
            require(all(ev["payload"].get(k) == selected[k] for k in ("line", "record_sha256", "role", "phase", "token_sha256")), "Canonical fragment metadata mismatch")
            for digest in record["token_sha256"]:
                require(sha(w.get(digest)) == digest, "Fragment object hash mismatch")
        else:
            result = record["capture"]
            ev = events[result["coverage_event_id"]]
            require(ev["kind"] == "capture.coverage" and ev["payload"]["status"] == "BOUNDED_COMPLETE", "Canonical standard capture mismatch")
            retained_report = strict(w.get(ev["payload"]["report_sha256"]))
            require(retained_report == {k: v for k, v in result.items() if k != "coverage_event_id"}, "Standard capture report differs from canonical object")
            require(len(result["raw_event_ids"]) == 1, "Standard capture did not bind exactly one record")
            original = events[result["raw_event_ids"][0]]
            require(original["kind"] == "capture.raw_record" and original["session_id"] == report["session_id"] and original["payload"]["source_line"] == selected["line"] and original["payload"]["raw_sha256"] == selected["record_sha256"], "Captured native record mismatch")
            require(sha(w.get(selected["record_sha256"])) == selected["record_sha256"], "Captured original object mismatch")


def accept_batch(ids, batch, queue="queue.json", input_receipt="START_RECEIPT.json", check_only=False, run_dir=RUN, root=ROOT):
    require(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,70}", batch), "Unsafe batch name")
    start, jobs = runner.gate(run_dir, root, queue, input_receipt)
    by_id = {j["id"]: j for j in jobs}
    require(ids and len(ids) == len(set(ids)) and set(ids) <= set(by_id), "Unknown, duplicate or empty job selection")
    mapping_path = run_dir / "LINEAGE_INPUTS.json"
    mapping = load(mapping_path, root)
    required_code = [run_dir / "archive_reviews.py", run_dir / "CAPTURE_METHOD.md", run_dir / "test_archive_reviews.py"]
    frozen = {str(root / x["path"]): x["sha256"] for x in start["files"]}
    for path in required_code:
        require(frozen.get(str(path)) == sha(read(path, root)), "Archive code/method/tests not bound by the input receipt")
    items = [prepare_job(by_id[jid], mapping, run_dir, root) for jid in ids]
    require(len({x["receipt"]["session_id"] for x in items}) == len(items), "Native session reused across selected reviews")
    if check_only:
        return {"status": "CHECK_ONLY_PASSED_NO_ARCHIVE_WRITES", "jobs": ids,
                "fallback_records": sum(s["mode"] != "standard" for x in items for s in x["selected"])}
    plan = {"schema": "selection-review-archive-batch.v1", "batch": batch, "job_ids": ids,
            "queue_file": str((run_dir / queue).relative_to(root)), "queue_sha256": sha(read(run_dir / queue, root)),
            "input_event_id": start["event_id"], "lineage_inputs_sha256": sha(read(mapping_path, root)),
            "archiver_inputs": [{"path": str(p.relative_to(root)), "sha256": sha(read(p, root))} for p in required_code],
            "jobs": [{"id": x["job"]["id"], "files": x["files"], "selection": public_selection(x["selected"])} for x in items]}
    folder = run_dir / "archive-batches"
    plan_path = folder / (batch + ".plan.json")
    save_once(plan_path, plan, root)
    with Archive(root / "research/archive").writer() as w:
        events = {e["id"]: e for e in w.events()}
        require(start["event_id"] in events and events[start["event_id"]]["kind"] == "research.selection.ready", "Canonical ready event absent")
        require(sha(read(mapping_path, root)) in events[start["event_id"]]["outputs"], "Lineage map not bound by ready event")
        known = index(events.values())
        for item in items:
            for version in item["versions"]:
                parent = known.get(version["entry_id"])
                require(parent and parent["id"] == version["assigned_event"] and parent["payload"]["entry"]["entity"] == version["entity"], "Assigned lineage parent mismatch")
                require(any(a["sha256"] == version["sha256"] for a in parent["payload"]["entry"]["artifacts"]), "Exact version not bound to assigned parent")
            item["capture"] = capture_job(w, item, start["event_id"], run_dir, root)
        events = {e["id"]: e for e in w.events()}
        known = index(events.values())
        results, parents = [], []
        for item in items:
            verify_files(item["files"], root)
            canonical_capture_check(item["capture"], events, w)
            job, receipt = item["job"], item["receipt"]
            sid = receipt["session_id"]
            for f in item["files"]:
                require(w.put(read(root / f["path"], root)) == f["sha256"], "Canonical output object mismatch")
            prompt_sha = w.put(read(root / job["prompt_file"], root))
            rubric_path = root / job["rubric_file"] if job.get("phase") == "pair" else run_dir / "RUBRIC.txt"
            rubric_sha = sha(read(rubric_path, root))
            require(frozen.get(str(rubric_path)) == rubric_sha, "Rubric not frozen by input receipt")
            if job.get("phase") == "pair":
                require(rubric_sha == job["rubric_sha256"], "Pair rubric hash mismatch")
            w.put(read(rubric_path, root))
            cap_sha = w.put(encode(item["capture"]))
            accepted = receipt["status"] == runner.COMPLETE
            status = "REVIEW_ARCHIVED" if accepted else "QUARANTINED_REVIEW_ARCHIVED_MISSING"
            ev = w.append({"kind": "research.selection.review.completed" if accepted else "research.selection.review.quarantined",
                           "actor": {"id": sid, "role": "AI"}, "session_id": sid, "run_id": run_dir.name,
                           "operation_id": run_dir.name + ":" + job["id"], "attempt_id": "review-v1",
                           "timestamp": receipt["completed_at"], "parents": list(dict.fromkeys([start["event_id"]] + [v["assigned_event"] for v in item["versions"]] + item["capture"]["evidence_events"])),
                           "bindings": start["bindings"], "inputs": [prompt_sha, rubric_sha],
                           "outputs": [f["sha256"] for f in item["files"]] + [cap_sha],
                           "payload": {"status": status, "job_id": job["id"], "phase": job.get("phase"), "files": item["files"],
                                       "versions": item["versions"], "capture_sha256": cap_sha, "quality_flags": receipt["quality_flags"],
                                       "response": item["value"], "boundary": item["capture"]["boundary"]}}, run_dir.name + ":" + job["id"] + ":review-archive-v1")
            events[ev["id"]] = ev
            entity = item["versions"][0]["entity"] if len(item["versions"]) == 1 else run_dir.name + "/pair/" + job["expected_output"]["pair_id"]
            entry = base_entry(run_dir.name + ":" + job["id"] + ":evaluation-v1", entity, "evaluation" if accepted else "cli_attempt",
                               "Свежий отзыв по точной назначенной версии; доводы и ограничения сохранены." if accepted else "Попытка сохранена как пропущенный отзыв: проверка приёмки не пройдена; благоприятный ответ не выбирался.")
            entry.update(parents=[v["entry_id"] for v in item["versions"]], evidence=[ev["id"]], occurred_at=receipt["completed_at"],
                         actor="Fresh Codex review " + sid, workflow=run_dir.name,
                         configuration={"requested": {"model": job["model"], "effort": job["effort"], "service_tier": job["service_tier"]}, "observed": item["proof"]["configurations"]},
                         artifacts=[{"path": f["path"], "sha256": f["sha256"], "role": "review-output"} for f in item["files"]],
                         gaps=[BOUNDARY, "Reported model configuration is not backend attestation. Source correctness and exhaustive novelty were not independently checked by this archive adapter."])
            if accepted:
                entry["assessment"] = {"versions": [{"entry_id": v["entry_id"], "sha256": v["sha256"]} for v in item["versions"]],
                                       "judge": {"requested": {"profile_id": job["profile_id"], "role": job.get("role"), **entry["configuration"]["requested"]}, "observed": item["proof"]["configurations"]},
                                       "rubric_sha256": rubric_sha, "prompt_sha256": prompt_sha,
                                       "order": [v["entry_id"] for v in item["versions"]],
                                       "verdict": item["value"]["verdict" if job.get("phase") == "pair" else "recommendation"],
                                       "rationale": item["value"]["reason_ru"], "round": run_dir.name, "scores": item["value"].get("scores"),
                                       "ordered_blind_ids": [v["blind_id"] for v in item["versions"]]}
            else:
                entry["attempt"] = {"job_id": job["id"], "status": status, "quality_flags": receipt["quality_flags"], "session_id": sid}
            lev = append_lineage(w, entry, sid, known, events)
            output = {"status": status, "job_id": job["id"], "session_id": sid, "event_id": ev["id"],
                      "lineage_event_id": lev["id"], "lineage_entry_id": entry["id"], "files": item["files"],
                      "capture_sha256": cap_sha, "capture_status": item["capture"]["status"], "input_event_id": start["event_id"]}
            receipt_path = run_dir / "results" / job["id"] / "ARCHIVE_RECEIPT.json"
            save_once(receipt_path, output, root)
            w.put(read(receipt_path, root))
            results.append(output)
            parents.extend([ev["id"], lev["id"]])
        inputs = [w.put(read(plan_path, root)), w.put(read(mapping_path, root))] + [w.put(read(p, root)) for p in required_code]
        ev = w.append({"kind": "research.selection.review_batch.accepted", "actor": {"id": "selection-archive", "role": "tool"},
                       "session_id": "selection-archive", "run_id": run_dir.name, "operation_id": run_dir.name + ":archive-batch:" + batch,
                       "attempt_id": "batch-v1", "parents": list(dict.fromkeys(parents)), "inputs": inputs,
                       "outputs": [w.put(encode(x)) for x in results],
                       "payload": {"batch": batch, "job_ids": ids, "accepted": [x["job_id"] for x in results if x["status"] == "REVIEW_ARCHIVED"],
                                   "quarantined_missing": [x["job_id"] for x in results if x["status"] != "REVIEW_ARCHIVED"], "model_calls": 0}}, run_dir.name + ":archive-batch:" + batch)
        result = {"status": "REVIEW_BATCH_ARCHIVED", "batch": batch, "event_id": ev["id"], "jobs": results}
        save_once(folder / (batch + ".receipt.json"), result, root)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ids", nargs="+", required=True)
    parser.add_argument("--batch", required=True)
    parser.add_argument("--queue", default="queue.json")
    parser.add_argument("--input-receipt", default="START_RECEIPT.json")
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    ids = [part for value in args.ids for part in value.split(",") if part]
    try:
        if args.check_only:
            result = accept_batch(ids, args.batch, args.queue, args.input_receipt, True)
        else:
            with (RUN / "archive-reviews.lock").open("a") as lock:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                result = accept_batch(ids, args.batch, args.queue, args.input_receipt)
        print(json.dumps({k: v for k, v in result.items() if k != "jobs"}, ensure_ascii=False), flush=True)
    except BaseException as exc:
        if not args.check_only:
            report = {"status": "ARCHIVE_GAP_ROOT_REPAIR_REQUIRED", "batch": args.batch, "job_ids": ids,
                      "error": runner.safe_error(exc), "automatic_retry": False, "at": runner.now()}
            path = RUN / "archive-batches" / ("gap-" + sha(encode(report))[:20] + ".json")
            save_once(path, report)
            if not (RUN / "STOP.json").exists():
                save_once(RUN / "STOP.json", report)
        raise


if __name__ == "__main__":
    main()
