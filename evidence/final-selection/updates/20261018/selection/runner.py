"""Finite fresh Codex reviews. No model calls occur on import or during tests.

Inputs are frozen by START_RECEIPT.json. Local completion is not canonical
acceptance. Each job gets one attempt; every existing attempt is preserved.
"""
from pathlib import Path
import argparse
import concurrent.futures
import datetime
import fcntl
import hashlib
import json
import math
import os
import re
import shutil
import sqlite3
import subprocess
import threading
import time
import uuid
import xml.etree.ElementTree as ET

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[1]
COMPLETE = "COMPLETE_LOCAL_PENDING_CANONICAL_ARCHIVE"
QUARANTINED = "QUARANTINED_LOCAL_PENDING_CANONICAL_ARCHIVE"
FAILED = "FAILED_PRESERVED_NO_RETRY"
EFFORTS = {"none", "minimal", "low", "medium", "high", "xhigh", "max", "ultra"}
STYLE = "# AGENTS.md instructions\n\n<INSTRUCTIONS>\nВ чатах отвечай мне краток и говори по делу! И используй язык попроще, старайся обьяснять простыми словами и емко\n</INSTRUCTIONS>\n"


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def strict_json(text):
    def pairs(rows):
        out = {}
        for key, value in rows:
            if key in out:
                raise ValueError("Duplicate JSON key: " + key)
            out[key] = value
        return out
    def bad(value):
        raise ValueError("Non-finite JSON number: " + value)
    def floating(value):
        result = float(value)
        if not math.isfinite(result):
            bad(value)
        return result
    return json.loads(text, object_pairs_hook=pairs, parse_constant=bad, parse_float=floating)


def encode(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode()


def save_new(path, value):
    path = Path(path)
    with path.open("xb") as out:
        out.write(encode(value)); out.flush(); os.fsync(out.fileno())


def replace_status(path, value):
    temporary = path.with_name("." + path.name + "." + uuid.uuid4().hex)
    save_new(temporary, value)
    os.replace(temporary, path)


def regular(path, root=ROOT):
    path = Path(path).absolute()
    if not path.is_relative_to(root.absolute()) or ".." in path.parts:
        raise ValueError("File outside bound root")
    if any(p.is_symlink() for p in (path, *path.parents)) or not path.is_file():
        raise ValueError("Missing/nonregular/symlink file: " + str(path))
    return path


def bound_path(name, root=ROOT):
    return regular(Path(name) if Path(name).is_absolute() else root / name, root)


def safe_error(value):
    text = str(value)
    text = re.sub(r"(?i)(bearer\s+)[\w.\-]+", r"\1[REDACTED]", text)
    text = re.sub(r"\bsk-[\w\-]{12,}\b", "[REDACTED]", text)
    text = re.sub(r"\beyJ[A-Za-z0-9_\-]{15,}\.[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+\b", "[REDACTED]", text)
    return text[:20000]


def safe_label(value):
    return value if isinstance(value, str) and re.fullmatch(r"[A-Za-z0-9_.:-]{1,100}", value) else "UNSUPPORTED"


def sanitized_env(source=None):
    source = os.environ if source is None else source
    allowed = {"PATH", "HOME", "TMPDIR", "USER", "LOGNAME", "SHELL", "LANG", "LC_ALL", "LC_CTYPE", "TERM", "TZ"}
    return {key: value for key, value in source.items() if key in allowed}


def check_job(job):
    required = {"id", "model", "effort", "service_tier", "prompt_file", "prompt_sha256", "schema_file", "schema_sha256"}
    if not isinstance(job, dict) or not required <= set(job):
        raise ValueError("Job lacks required fields")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,119}", job["id"]):
        raise ValueError("Unsafe job ID")
    if not re.fullmatch(r"gpt-[A-Za-z0-9_.-]+", job["model"]) or job["effort"] not in EFFORTS:
        raise ValueError("Invalid requested configuration")
    if job["service_tier"] != "default":
        raise ValueError("Only Standard service_tier=default is allowed")
    if "expected_output" in job and not isinstance(job["expected_output"], dict):
        raise ValueError("expected_output must be an object")
    for field in ("prompt_sha256", "schema_sha256"):
        if not re.fullmatch(r"[a-f0-9]{64}", job[field]):
            raise ValueError("Invalid input digest")


def command(job, attempt, root=ROOT, executable=None):
    check_job(job)
    executable = executable or shutil.which("codex")
    if not executable:
        raise ValueError("Codex CLI unavailable")
    config = {
        "model_provider": "openai", "forced_login_method": "chatgpt",
        "model_reasoning_effort": job["effort"], "service_tier": "default",
        "project_doc_max_bytes": 0, "memories.use_memories": False,
        "memories.generate_memories": False, "web_search": "disabled",
        "features.shell_tool": False, "features.multi_agent": False,
        "hide_agent_reasoning": True, "approval_policy": "never",
    }
    argv = [executable, "exec", "--ignore-user-config", "--skip-git-repo-check",
            "--sandbox", "read-only", "--cd", str(root), "--model", job["model"],
            "--json", "--color", "never", "--output-last-message", str(attempt / "final.txt")]
    for key, value in config.items():
        argv += ["-c", key + "=" + json.dumps(value)]
    return argv + ["-"]  # Schema is inside the frozen prompt; no native schema retry route.


def neutral_environment(text, root=ROOT):
    if text.startswith(STYLE):
        text = text[len(STYLE):]
    if not text.startswith("<environment_context>"):
        return False
    try:
        node = ET.fromstring(text)
    except ET.ParseError:
        return False
    if node.attrib or [x.tag for x in node] != ["cwd", "shell", "current_date", "timezone", "filesystem"]:
        return False
    if node.findtext("cwd") != str(root) or node.findtext("shell") != "zsh" or node.findtext("timezone") != "America/Los_Angeles":
        return False
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", node.findtext("current_date") or ""):
        return False
    expected = ET.fromstring("<filesystem><workspace_roots><root>" + str(root) + "</root></workspace_roots><permission_profile type=\"managed\"><file_system type=\"restricted\"><entry access=\"read\"><special>:root</special></entry></file_system></permission_profile></filesystem>")
    def signature(element):
        return element.tag, sorted(element.attrib.items()), (element.text or "").strip(), (element.tail or "").strip(), tuple(signature(x) for x in element)
    return signature(node.find("filesystem")) == signature(expected)


def native_records(lines, sid, prompt, job, root=ROOT):
    """Pure allowlisted extraction; never retain reasoning or runtime envelopes."""
    configs, matched, neutral, others, calls, finals, visible, identities = [], [], [], [], [], [], [], []
    for number, raw in enumerate(lines, 1):
        if isinstance(raw, str):
            raw = raw.encode()
        obj = strict_json(raw)
        payload = obj.get("payload", {})
        if not isinstance(payload, dict):
            raise ValueError("Unsupported native payload")
        kind = obj.get("type")
        if kind == "session_meta":
            identities.append({"line": number, "id": payload.get("id"), "cwd": payload.get("cwd")})
        if kind == "turn_context":
            configs.append({"line": number, "model": payload.get("model"), "effort": payload.get("effort") or payload.get("reasoning_effort"),
                            "alternate_effort": payload.get("reasoning_effort"), "service_tier": payload.get("service_tier")})
        if kind != "response_item":
            continue
        if payload.get("type") not in {"message", "reasoning"}:
            calls.append({"line": number, "type": safe_label(payload.get("type")), "name": safe_label(payload.get("name"))})
        if payload.get("type") != "message":
            continue
        content = payload.get("content", [])
        if not isinstance(content, list):
            raise ValueError("Unsupported native message content")
        recognized = all(isinstance(x, dict) and x.get("type") in {"input_text", "output_text", "text"} and isinstance(x.get("text"), str) for x in content)
        text = "\n".join(x["text"] for x in content) if recognized else None
        role, phase = payload.get("role"), payload.get("phase")
        if role == "user":
            if text is not None and text.rstrip() == prompt.rstrip():
                matched.append(number)
                visible.append({"line": number, "record_sha256": digest(raw), "role": "user", "text": text})
            elif text is not None and neutral_environment(text.rstrip(), root):
                neutral.append({"line": number, "record_sha256": digest(raw)})
            else:
                others.append({"line": number, "record_sha256": digest(raw), "characters": len(text) if text is not None else None})
        if role == "assistant" and phase in {"commentary", "final", "final_answer"}:
            if text is None:
                raise ValueError("Unsupported visible native message")
            record = {"line": number, "record_sha256": digest(raw), "timestamp": obj.get("timestamp"), "role": role, "phase": phase, "text": text}
            visible.append(record)
            if phase in {"final", "final_answer"}:
                finals.append(record)
    proof = {"session_id": sid, "identity": identities, "configurations": configs, "prompt_lines": matched,
             "prompt_sha256": digest(prompt.encode()), "prompt_match_rule": "Identical Unicode text except optional trailing whitespace removed by CLI; original packet hash retained.",
             "native_prompt_sha256": [digest(x["text"].encode()) for x in visible if x["role"] == "user"],
             "neutral_runtime": neutral, "other_user_metadata": others,
             "tool_calls": calls, "final_lines": [x["line"] for x in finals],
             "service_tier_boundary": "Explicit CLI default; absent native tier remains unobserved.",
             "capture_boundary": "Exact recognized visible text and allowlisted configuration only. No internal envelopes, hidden reasoning or backend attestation."}
    failures = []
    if not identities or any(x["id"] != sid or x["cwd"] != str(root) for x in identities):
        failures.append("NATIVE_IDENTITY_MISMATCH")
    if len(matched) != 1 or others or calls:
        failures.append("NATIVE_INPUT_OR_TOOL_ISOLATION_FAILED")
    if not configs or any(x["model"] != job["model"] or x["effort"] != job["effort"] or
                          (x["alternate_effort"] is not None and x["alternate_effort"] != job["effort"]) for x in configs):
        failures.append("NATIVE_MODEL_OR_EFFORT_MISMATCH")
    if any(x["service_tier"] not in {None, "default"} for x in configs):
        failures.append("NATIVE_SERVICE_TIER_MISMATCH")
    proof["isolation_failures"] = failures
    return proof, visible, finals


def inspect_native(sid, prompt, job, root=ROOT):
    database = Path.home() / ".codex" / "state_5.sqlite"
    with sqlite3.connect(database.as_uri() + "?mode=ro", uri=True) as connection:
        rows = connection.execute("SELECT id, rollout_path, cwd FROM threads WHERE id = ?", (sid,)).fetchall()
    if len(rows) != 1 or rows[0][0] != sid or rows[0][2] != str(root):
        raise ValueError("Native identity/cwd unavailable or different")
    source = regular(Path(rows[0][1]), Path.home() / ".codex")
    if source.stat().st_size > 64 * 1024 * 1024:
        raise ValueError("Native capture exceeds bounded size")
    with source.open("rb") as stream:
        raw = stream.read()
    if not raw.endswith(b"\n"):
        raise ValueError("Partial native tail; preserve without rerun")
    return native_records(raw.splitlines(keepends=True), sid, prompt, job, root)


def validate(value, schema, original=None, location="$"):
    """Strict supported JSON Schema subset; unsupported keywords fail closed."""
    original = schema if original is None else original
    if isinstance(schema, bool):
        if not schema:
            raise ValueError(location + ": false schema")
        return
    known = {"$schema", "$id", "$defs", "definitions", "$ref", "title", "description", "default", "examples", "type", "enum", "const", "required", "properties", "additionalProperties", "minProperties", "maxProperties", "items", "minItems", "maxItems", "uniqueItems", "minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum", "multipleOf", "minLength", "maxLength", "pattern", "allOf", "anyOf", "oneOf", "not"}
    if not isinstance(schema, dict) or set(schema) - known:
        raise ValueError(location + ": unsupported schema keyword")
    if "$ref" in schema:
        reference = schema["$ref"]
        if not isinstance(reference, str) or not reference.startswith("#/"):
            raise ValueError("Only local schema references are supported")
        target = original
        for part in reference[2:].split("/"):
            target = target[part.replace("~1", "/").replace("~0", "~")]
        validate(value, target, original, location)
    for mode in ("allOf", "anyOf", "oneOf"):
        if mode in schema:
            outcomes = []
            for option in schema[mode]:
                try:
                    validate(value, option, original, location); outcomes.append(True)
                except ValueError:
                    outcomes.append(False)
            if not ((mode == "allOf" and all(outcomes)) or (mode == "anyOf" and any(outcomes)) or (mode == "oneOf" and sum(outcomes) == 1)):
                raise ValueError(location + ": " + mode)
    if "not" in schema:
        try:
            validate(value, schema["not"], original, location)
        except ValueError:
            pass
        else:
            raise ValueError(location + ": forbidden schema")
    checks = {"object": lambda x: isinstance(x, dict), "array": lambda x: isinstance(x, list), "string": lambda x: isinstance(x, str),
              "integer": lambda x: type(x) is int, "number": lambda x: type(x) in {int, float} and math.isfinite(x), "boolean": lambda x: type(x) is bool, "null": lambda x: x is None}
    types = schema.get("type")
    if types is not None:
        types = [types] if isinstance(types, str) else types
        if not types or any(t not in checks for t in types) or not any(checks[t](value) for t in types):
            raise ValueError(location + ": wrong type")
    def equal(a, b):
        return type(a) is type(b) and a == b
    if "enum" in schema and not any(equal(value, x) for x in schema["enum"]):
        raise ValueError(location + ": wrong enum")
    if "const" in schema and not equal(value, schema["const"]):
        raise ValueError(location + ": wrong const")
    if isinstance(value, dict):
        if set(schema.get("required", [])) - set(value):
            raise ValueError(location + ": missing required field")
        if not schema.get("minProperties", 0) <= len(value) <= schema.get("maxProperties", math.inf):
            raise ValueError(location + ": property count")
        properties = schema.get("properties", {})
        for key, item in value.items():
            if key in properties:
                validate(item, properties[key], original, location + "." + key)
            elif schema.get("additionalProperties") is False:
                raise ValueError(location + ": extra property")
            elif isinstance(schema.get("additionalProperties"), dict):
                validate(item, schema["additionalProperties"], original, location + "." + key)
    if isinstance(value, list):
        if not schema.get("minItems", 0) <= len(value) <= schema.get("maxItems", math.inf):
            raise ValueError(location + ": array length")
        if schema.get("uniqueItems") and len({json.dumps(x, sort_keys=True) for x in value}) != len(value):
            raise ValueError(location + ": duplicate array item")
        for index, item in enumerate(value):
            validate(item, schema.get("items", {}), original, location + "[" + str(index) + "]")
    if isinstance(value, str):
        if not schema.get("minLength", 0) <= len(value) <= schema.get("maxLength", math.inf):
            raise ValueError(location + ": string length")
        if "pattern" in schema and re.search(schema["pattern"], value) is None:
            raise ValueError(location + ": pattern mismatch")
    if type(value) in {int, float}:
        if not math.isfinite(value) or value < schema.get("minimum", -math.inf) or value > schema.get("maximum", math.inf):
            raise ValueError(location + ": numeric bounds")
        if value <= schema.get("exclusiveMinimum", -math.inf) or value >= schema.get("exclusiveMaximum", math.inf):
            raise ValueError(location + ": exclusive numeric bounds")
        if "multipleOf" in schema and not math.isclose(value / schema["multipleOf"], round(value / schema["multipleOf"])):
            raise ValueError(location + ": multipleOf")


def actual_quota(detail):
    text = str(detail).lower()
    return any(x in text for x in ("quota", "rate limit", "rate_limit", "usage limit", "usage_limit", "limit reached", "credit balance", "credits exhausted", "overage", "http 429", "status 429"))


def known_transport(detail):
    text = str(detail).lower()
    return not actual_quota(text) and any(x in text for x in ("websocket closed by server before response.completed", "incomplete response returned, reason: max_output_tokens", "stream disconnected before completion"))


def visible_event(event):
    """Never forward raw unknown bodies or reasoning events to disk."""
    kind = event.get("type")
    if kind == "thread.started":
        return {"type": kind, "thread_id": event.get("thread_id")}
    if kind in {"turn.started", "turn.completed"}:
        result = {"type": kind}
        if kind == "turn.completed":
            usage = event.get("usage", {})
            result["usage"] = {k: v for k, v in usage.items() if k in {"input_tokens", "output_tokens", "cached_input_tokens"} and type(v) is int and v >= 0} if isinstance(usage, dict) else {}
        return result
    if kind in {"error", "turn.failed"}:
        error = event.get("error", {})
        message = event.get("message") or (error.get("message") if isinstance(error, dict) else None)
        return {"type": kind, "message": safe_error(message or "Unrecognized error without safe message")}
    if kind in {"item.started", "item.updated", "item.completed"}:
        item = event.get("item", {})
        if not isinstance(item, dict):
            return {"type": kind, "unexpected": True}
        if item.get("type") in {"reasoning", "reasoning_summary"}:
            return None
        if item.get("type") == "agent_message" and isinstance(item.get("text"), str):
            return {"type": kind, "item": {"type": "agent_message", "id": item.get("id"), "text": item["text"]}}
        return {"type": kind, "excluded_item_type": safe_label(item.get("type")), "unexpected": True}
    return {"type": safe_label(kind), "unexpected": True}


def classify(finals, stderr, cli_final, schema, errors=(), completed=True, exit_code=0, job=None):
    flags = []
    if any("retrying sampling request" in line.lower() or "reconnecting..." in line.lower() for line in stderr) or errors:
        flags.append("INTERNAL_RETRY_OR_TRANSPORT_ERROR")
    if len(finals) != 1:
        flags.append("VISIBLE_FINAL_COUNT_" + str(len(finals)))
    if not completed or exit_code:
        flags.append("INCOMPLETE_TURN")
    value = None
    if not flags:
        try:
            value = strict_json(finals[0]["text"])
            validate(value, schema)
            if strict_json(cli_final) != value:
                raise ValueError("Native/file final mismatch")
            if isinstance(value, dict) and value.get("read_complete") is False:
                raise ValueError("Incomplete reading claim")
            if job is not None and isinstance(value, dict):
                expected = job.get("expected_output", {"review_id": job["id"], **{k: job[k] for k in ("manuscript_id", "profile_id") if k in job}})
                for key, target in expected.items():
                    if key not in value or type(value[key]) is not type(target) or value[key] != target:
                        raise ValueError("Response identity mismatch: " + key)
        except (ValueError, KeyError, TypeError, RecursionError, OverflowError, ZeroDivisionError) as exc:
            flags.append("INVALID_SCHEMA_OR_FINAL: " + safe_error(exc))
    return (QUARANTINED, flags, None) if flags else (COMPLETE, [], value)


def check_inputs(job, root=ROOT):
    check_job(job)
    prompt = bound_path(job["prompt_file"], root).read_bytes()
    schema_bytes = bound_path(job["schema_file"], root).read_bytes()
    if digest(prompt) != job["prompt_sha256"] or digest(schema_bytes) != job["schema_sha256"]:
        raise ValueError("Frozen job input changed")
    return prompt, strict_json(schema_bytes)


def run_file(name, run_dir=RUN):
    path = Path(name) if Path(name).is_absolute() else run_dir / name
    return regular(path, run_dir)


def gate(run_dir=RUN, root=ROOT, queue_file="queue.json", input_receipt="START_RECEIPT.json"):
    receipt = strict_json(run_file(input_receipt, run_dir).read_bytes())
    if receipt.get("status") != "SELECTION_INPUTS_ARCHIVED" or not receipt.get("event_id") or not isinstance(receipt.get("files"), list):
        raise ValueError("Canonical input receipt missing or wrong")
    files = {}
    for item in receipt["files"]:
        path = bound_path(item["path"], root)
        if path in files or digest(path.read_bytes()) != item["sha256"]:
            raise ValueError("Bound file duplicate or drift: " + str(path))
        files[path] = item["sha256"]
    queue_path = run_file(queue_file, run_dir)
    required = {queue_path, regular(run_dir / "runner.py", root), regular(run_dir / "test_runner.py", root)}
    jobs = strict_json(queue_path.read_bytes())["jobs"]
    seen = set()
    for job in jobs:
        check_job(job)
        if job["id"] in seen:
            raise ValueError("Duplicate job ID")
        seen.add(job["id"])
        check_inputs(job, root)
        for field in ("prompt", "schema"):
            path = bound_path(job[field + "_file"], root)
            required.add(path)
            if files.get(path) != job[field + "_sha256"]:
                raise ValueError("Job bytes absent from canonical input receipt")
    if not required <= set(files):
        raise ValueError("Runner/tests/queue not bound by input receipt")
    return receipt, jobs


def existing_disposition(job, run_dir=RUN, root=ROOT):
    directory = run_dir / "results" / job["id"]
    attempt = directory / "attempt-001"
    if not attempt.exists():
        return None
    if attempt.is_symlink() or not attempt.is_dir():
        raise ValueError("Unsafe existing attempt")
    for name in ("receipt.json", "failure.json"):
        if (attempt / name).exists():
            receipt = strict_json(regular(attempt / name, root).read_bytes())
            if receipt.get("job_id") != job["id"] or receipt.get("prompt_sha256") != job["prompt_sha256"]:
                raise ValueError("Existing attempt identity/input differs")
            for recorded, requested in (("schema_sha256", "schema_sha256"), ("requested_model", "model"), ("requested_effort", "effort"), ("requested_service_tier", "service_tier")):
                if receipt.get(recorded) != job[requested]:
                    raise ValueError("Existing attempt configuration/schema differs")
            for path, expected in receipt.get("outputs", {}).items():
                actual = bound_path(path, root)
                if actual.parent != attempt or digest(actual.read_bytes()) != expected:
                    raise ValueError("Existing output drift")
            archive = directory / "ARCHIVE_RECEIPT.json"
            if archive.exists():
                acceptance = strict_json(regular(archive, root).read_bytes())
                if acceptance.get("event_id") and receipt.get("status") == COMPLETE:
                    return {"job_id": job["id"], "status": "SKIPPED_ACCEPTED", "session_id": receipt.get("session_id")}
            return {"job_id": job["id"], "status": "SKIPPED_" + receipt["status"], "session_id": receipt.get("session_id")}
    return {"job_id": job["id"], "status": "SKIPPED_UNFINISHED_NO_RETRY"}


def teardown(process, stderr_thread=None, terminate=False, timeout=5):
    """Reap the process and finish stderr before publishing terminal files."""
    forced = False
    if terminate and process.poll() is None:
        process.terminate()
    try:
        code = process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        forced = True
        process.kill()
        code = process.wait(timeout=timeout)
    if stderr_thread is not None:
        stderr_thread.join(timeout=timeout)
        if stderr_thread.is_alive():
            raise RuntimeError("Stderr thread still alive; terminal capture unavailable")
    if process.poll() is None:
        raise RuntimeError("Child process is not confirmed stopped")
    return code, forced


class Dispatcher:
    def __init__(self, run_dir=RUN, root=ROOT):
        self.run_dir, self.root = Path(run_dir), Path(root)
        self.stop = threading.Event()
        self.lock = threading.Lock()
        self.launch_lock = threading.Lock()
        self.seen_sessions = set()

    def stopped(self):
        return self.stop.is_set() or (self.run_dir / "STOP.json").exists()

    def event(self, record):
        with self.lock:
            with (self.run_dir / "dispatch.jsonl").open("a") as out:
                out.write(json.dumps({"at": now(), **record}, ensure_ascii=False) + "\n"); out.flush(); os.fsync(out.fileno())

    def fail_stop(self, reason, job_id):
        record = {"at": now(), "job_id": job_id, "reason": safe_error(reason), "automatic_retry": False}
        with self.launch_lock:
            self.stop.set()
            with self.lock:
                try:
                    save_new(self.run_dir / "STOP.json", record)
                except FileExistsError:
                    pass
        self.event({"event": "stop", **record})

    def launch_process(self, argv):
        # The same lock makes a stop effective either before or after Popen,
        # never between the final stop check and the actual process launch.
        with self.launch_lock:
            if self.stopped():
                return None
            return subprocess.Popen(argv, cwd=self.root, env=sanitized_env(), stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    def register_session(self, sid):
        with self.lock:
            if not isinstance(sid, str) or not re.fullmatch(r"[A-Za-z0-9_-]{8,100}", sid) or sid in self.seen_sessions:
                raise ValueError("Missing, invalid or reused native session ID")
            self.seen_sessions.add(sid)

    def run_one(self, job):
        existing = existing_disposition(job, self.run_dir, self.root)
        if existing:
            return existing
        if self.stopped():
            return {"job_id": job["id"], "status": "NOT_STARTED_STOP"}
        attempt = self.run_dir / "results" / job["id"] / "attempt-001"
        sid, process, thread = None, None, None
        started, monotonic = now(), time.monotonic()
        stderr, errors, usage, fatal = [], [], [], []
        metadata = {"job_id": job["id"], "started_at": started, "prompt_sha256": job["prompt_sha256"], "schema_sha256": job["schema_sha256"],
                    "requested_model": job["model"], "requested_effort": job["effort"], "requested_service_tier": job["service_tier"]}
        try:
            prompt, schema = check_inputs(job, self.root)
            attempt.mkdir(parents=True, exist_ok=False)
            argv = command(job, attempt, self.root)
            metadata.update(argv=argv, argv_sha256=digest(json.dumps(argv, separators=(",", ":")).encode()), auth="Forced ChatGPT subscription; environment allowlist; no API keys")
            save_new(attempt / "launch.json", metadata)
            if self.stopped():
                save_new(attempt / "not-launched.json", {**metadata, "status": "NOT_STARTED_STOP"})
                return {"job_id": job["id"], "status": "NOT_STARTED_STOP"}
            process = self.launch_process(argv)
            if process is None:
                save_new(attempt / "not-launched.json", {**metadata, "status": "NOT_STARTED_STOP"})
                return {"job_id": job["id"], "status": "NOT_STARTED_STOP"}
            self.event({"event": "job.started", "job_id": job["id"]})
            def abort(reason):
                fatal.append(safe_error(reason))
                try:
                    self.fail_stop(reason, job["id"])
                finally:
                    if process.poll() is None:
                        process.terminate()
            def drain_stderr():
                try:
                    for line in process.stderr:
                        safe = safe_error(line); stderr.append(safe)
                        if actual_quota(safe):
                            abort("ACTUAL_QUOTA: " + safe)
                        elif "retrying sampling request" in safe.lower() and not known_transport(safe):
                            abort("UNKNOWN_INTERNAL_RETRY: " + safe)
                except BaseException as exc:
                    abort("STDERR_CAPTURE_FAILURE: " + safe_error(exc))
            thread = threading.Thread(target=drain_stderr, daemon=True)
            thread.start()
            process.stdin.write(prompt.decode()); process.stdin.close()
            completed = False
            with (attempt / "visible-events.jsonl").open("x") as out:
                for line in process.stdout:
                    try:
                        event = strict_json(line)
                        visible = visible_event(event)
                    except (ValueError, TypeError, AttributeError):
                        abort("Malformed stdout event; body excluded"); continue
                    if visible is None:
                        continue
                    out.write(json.dumps(visible, ensure_ascii=False) + "\n"); out.flush()
                    if visible.get("unexpected"):
                        abort("Unexpected tool/event; body excluded")
                    if visible["type"] == "thread.started":
                        if sid is not None:
                            abort("Multiple thread.started events")
                        sid = visible["thread_id"]; self.register_session(sid)
                        self.event({"event": "job.session", "job_id": job["id"], "session_id": sid})
                    if visible["type"] in {"error", "turn.failed"}:
                        errors.append(visible["message"])
                        if actual_quota(visible["message"]) or not known_transport(visible["message"]):
                            abort(visible["message"])
                    if visible["type"] == "turn.completed":
                        if completed:
                            abort("Multiple completed turns")
                        completed = True; usage.append(visible.get("usage", {}))
                out.flush(); os.fsync(out.fileno())
            exit_code, forced = teardown(process, thread)
            if forced:
                raise ValueError("Child required forced termination after output closed")
            save_new(attempt / "stderr.json", {"lines": stderr, "exit_code": exit_code})
            if fatal:
                raise ValueError("Stopped after unsafe/unknown event: " + "; ".join(fatal))
            if not sid or (exit_code != 0 and not errors and not any(known_transport(x) for x in stderr)):
                raise ValueError("Unclassified CLI exit or missing identity")
            check_inputs(job, self.root)
            proof, visible, finals = inspect_native(sid, prompt.decode(), job, self.root)
            save_new(attempt / "native-check.json", proof)
            save_new(attempt / "native-visible.json", {"session_id": sid, "records": visible})
            if proof["isolation_failures"]:
                raise ValueError("; ".join(proof["isolation_failures"]))
            final_file = attempt / "final.txt"
            raw_final = regular(final_file, self.root).read_text() if final_file.exists() else ""
            status, flags, value = classify(finals, stderr, raw_final, schema, errors, completed, exit_code, job)
            if value is not None:
                save_new(attempt / "response.json", value)
            receipt = {**metadata, "status": status, "completed_at": now(), "elapsed_seconds": time.monotonic() - monotonic,
                       "session_id": sid, "quality_flags": flags, "usage_observed": usage, "cli_exit_code": exit_code,
                       "internal_sampling_retry_count": sum("retrying sampling request" in x.lower() for x in stderr),
                       "visible_final_count": len(finals), "model_call_count": "Unknown; CLI sessions and observed internal retries are separate.",
                       "outputs": {str(p.relative_to(self.root)): digest(regular(p, self.root).read_bytes()) for p in sorted(attempt.iterdir()) if p.is_file()},
                       "archive_boundary": "Local only; canonical output event and receipt required before dependent reading."}
            save_new(attempt / "receipt.json", receipt)
            self.event({"event": "job.finished", "job_id": job["id"], "status": status, "session_id": sid})
            return {"job_id": job["id"], "status": status, "session_id": sid}
        except BaseException as exc:
            stop_error = None
            try:
                self.fail_stop(exc, job["id"])
            except BaseException as failure:
                stop_error = safe_error(failure)
            process_state = {"process_stopped": process is None, "stderr_drained": thread is None}
            if process is not None:
                try:
                    code, killed = teardown(process, thread, terminate=True)
                    process_state = {"process_stopped": True, "stderr_drained": True, "exit_code": code, "forced_kill": killed}
                except BaseException as failure:
                    process_state = {"process_stopped": process.poll() is not None, "stderr_drained": thread is None or not thread.is_alive(), "error": safe_error(failure)}
            attempt.mkdir(parents=True, exist_ok=True)
            failure = {**metadata, "status": FAILED, "ended_at": now(), "elapsed_seconds": time.monotonic() - monotonic,
                       "session_id": sid, "error": safe_error(exc), "automatic_retry": False, "process_state": process_state,
                       "stop_record_error": stop_error}
            if not (attempt / "stderr.json").exists():
                save_new(attempt / "stderr.json", {"lines": list(stderr), "error_messages": errors, "complete": process_state["stderr_drained"]})
            save_new(attempt / "failure.json", failure)
            return {"job_id": job["id"], "status": FAILED, "session_id": sid, "error": safe_error(exc), "process_state": process_state}

    def run(self, ids, workers, queue_file="queue.json", input_receipt="START_RECEIPT.json"):
        if not 1 <= workers <= 3:
            raise ValueError("Workers must be between 1 and 3")
        with (self.run_dir / "dispatch.lock").open("a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            receipt, jobs = gate(self.run_dir, self.root, queue_file, input_receipt)
            by_id = {job["id"]: job for job in jobs}
            if len(ids) != len(set(ids)) or set(ids) - set(by_id):
                raise ValueError("Unknown or duplicate requested IDs")
            prior_sessions = {}
            for path in sorted((self.run_dir / "results").glob("*/attempt-001/launch.json")):
                for name in ("receipt.json", "failure.json"):
                    file = path.parent / name
                    if file.exists():
                        sid = strict_json(regular(file, self.root).read_bytes()).get("session_id")
                        if sid:
                            if sid in prior_sessions and prior_sessions[sid] != path.parent:
                                raise ValueError("A session ID was reused across prior jobs")
                            if sid not in prior_sessions:
                                self.register_session(sid)
                                prior_sessions[sid] = path.parent
            pending, finished, active = [], [], {}
            for jid in ids:
                existing = existing_disposition(by_id[jid], self.run_dir, self.root)
                if existing:
                    finished.append(existing)
                    if existing["status"] in {"SKIPPED_UNFINISHED_NO_RETRY", "SKIPPED_" + FAILED}:
                        self.fail_stop("Prior incomplete/failed attempt requires explicit disposition", jid)
                else:
                    pending.append(by_id[jid])
            started = now()
            def snapshot(status):
                replace_status(self.run_dir / "process.json", {"status": status, "pid": os.getpid(), "started_at": started, "updated_at": now(),
                    "input_event_id": receipt["event_id"], "queue_file": str(run_file(queue_file, self.run_dir).relative_to(self.root)),
                    "input_receipt": str(run_file(input_receipt, self.run_dir).relative_to(self.root)), "workers": workers, "selected_ids": ids,
                    "pending_ids": [x["id"] for x in pending], "active_ids": [x["id"] for x in active.values()], "finished": finished})
            snapshot("RUNNING")
            with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
                while pending or active:
                    while pending and len(active) < workers and not self.stopped():
                        job = pending.pop(0); active[pool.submit(self.run_one, job)] = job
                    snapshot("STOPPING_PRESERVING_IN_FLIGHT" if self.stopped() else "RUNNING")
                    if not active:
                        break
                    ready, _ = concurrent.futures.wait(active, timeout=1, return_when=concurrent.futures.FIRST_COMPLETED)
                    for future in ready:
                        job = active.pop(future)
                        result = future.result(); finished.append(result)
                        print(json.dumps(result, ensure_ascii=False), flush=True)
            status = "STOPPED_PRESERVED" if self.stopped() else "SUBSET_COMPLETE_LOCAL_PENDING_CANONICAL_ARCHIVE"
            if any("process_state" in row and not (row["process_state"].get("process_stopped") and row["process_state"].get("stderr_drained")) for row in finished):
                status = "STOPPED_PROCESS_STATE_UNKNOWN"
            snapshot(status)
            return {"status": status, "finished": len(finished), "pending": len(pending)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ids", nargs="+", required=True, help="Finite IDs, separated by spaces or commas")
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--queue", default="queue.json", help="Immutable queue file inside this run directory")
    parser.add_argument("--input-receipt", default="START_RECEIPT.json", help="Its canonical input receipt inside this run directory")
    args = parser.parse_args()
    ids = [part for value in args.ids for part in value.split(",") if part]
    dispatcher = Dispatcher()
    try:
        print(json.dumps(dispatcher.run(ids, args.workers, args.queue, args.input_receipt)), flush=True)
    except BaseException as exc:
        dispatcher.fail_stop("DISPATCHER_FAILURE: " + safe_error(exc), "dispatcher")
        raise


if __name__ == "__main__":
    main()
