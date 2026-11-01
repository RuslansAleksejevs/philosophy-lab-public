#!/usr/bin/env python3
"""Opt-in, bounded capture of original, reviewed visible Codex rollout records.

This is a filtered local import, not a provider request/response recorder.
"""
from __future__ import annotations

import argparse
from collections import Counter
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import stat
import sys
import xml.etree.ElementTree as ET

from research_archive import Archive, ArchiveError, _ArchiveWriter, canonical
from codex_rollout import regular_file, rollout_file

TOP_KEYS = {"timestamp", "ordinal", "type", "payload", "metadata"}
TOP_METADATA_KEYS = {
    "client_authored", "user_input_order", "mcp_attribution",
    "fallback_token_limit_override", "retained_source", "guardian_sources",
    "guardian_source_order_guidance",
}
MCP_ATTRIBUTION_KEYS = {"status", "sources", "error_reason"}
META_KEYS = {"turn_id", "create_time", "content_item_kinds"}
MESSAGE_META_KEYS = META_KEYS | {"content_item_metadata"}
COMMON_KEYS = {"type", "id", "internal_chat_message_metadata_passthrough"}
PAYLOAD_KEYS = {
    "message": COMMON_KEYS | {"role", "content", "phase", "channel", "status"},
    "function_call": COMMON_KEYS | {"name", "namespace", "arguments", "call_id", "status"},
    "custom_tool_call": COMMON_KEYS | {"name", "namespace", "input", "call_id", "status"},
    "function_call_output": COMMON_KEYS | {"call_id", "output"},
    "custom_tool_call_output": COMMON_KEYS | {"call_id", "output"},
}
CALL_TYPES = {"function_call", "custom_tool_call"}
OUTPUT_TYPES = {"function_call_output", "custom_tool_call_output"}
TOOL_TYPES = CALL_TYPES | OUTPUT_TYPES
KNOWN_OMISSIONS = {
    "session_meta", "world_state", "turn_context", "event_msg", "token_usage_record",
    "inter_agent_communication_metadata", "compacted",
}
# Deliberately conservative: original call/output bytes are retained or omitted,
# never redacted and then labelled original. Review cannot override this filter.
SENSITIVE_MARKERS = (
    ".codex/sessions", ".codex/state_", "base_instructions", "encrypted_content",
    "<system>", "<developer>", "<|im_start|>system", "<|im_start|>developer",
)


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def strict_json(value):
    """A parsed safe duplicate must never conceal unsafe original record bytes."""
    def pairs(items):
        result = {}
        for key, item in items:
            if key in result:
                raise ValueError("duplicate JSON key: " + key)
            result[key] = item
        return result
    def constant(value):
        raise ValueError("non-finite JSON constant: " + value)
    return json.loads(value, object_pairs_hook=pairs, parse_constant=constant)


def valid_timestamp(value):
    if not isinstance(value, str):
        return False
    try:
        return datetime.datetime.fromisoformat(value.replace("Z", "+00:00")).tzinfo is not None
    except ValueError:
        return False


def observed_model(payload, source_line):
    """Project two safe configuration scalars; never retain the runtime envelope."""
    if not isinstance(payload, dict):
        return {"status": "unknown", "reason": "native turn context is unavailable or unsupported"}
    model = payload.get("model")
    if not isinstance(model, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:/-]{0,199}", model):
        return {"status": "unknown", "reason": "native model identifier unavailable or unsupported"}
    effort = payload.get("effort")
    if not isinstance(effort, str) or effort not in {"none", "minimal", "low", "medium", "high", "xhigh", "max", "ultra"}:
        effort = None
    return {"status": "known", "value": {"model": model, "reasoning_effort": effort},
            "source": "native-turn-context-observation", "source_line": source_line,
            "boundary": "Reported local configuration; exact backend identity and thinking duration unverified"}


def resolve_session(session_id: str, expected_cwd: Path, state_db: Path | None = None) -> Path:
    """One bound-id metadata query; never enumerate tasks or scan session paths."""
    if not re.fullmatch(r"[A-Za-z0-9_-]{8,100}", session_id):
        raise ValueError("invalid session id")
    db = state_db or Path.home() / ".codex" / "state_5.sqlite"
    with regular_file(db):
        pass
    connection = sqlite3.connect(db.absolute().as_uri() + "?mode=ro", uri=True)
    try:
        rows = connection.execute(
            "SELECT id, rollout_path, cwd FROM threads WHERE id = ?", (session_id,)
        ).fetchall()
    finally:
        connection.close()
    if len(rows) != 1 or rows[0][0] != session_id:
        raise ValueError("exact session identity not found")
    if Path(rows[0][2]).absolute() != expected_cwd.absolute():
        raise ValueError("session database cwd does not match expected project")
    return Path(rows[0][1])


def text_blocks(value, types, *, completed_output=False):
    # Current completed assistant records add empty presentation arrays. Do not
    # extend tool outputs or user inputs, or accept annotation/logprob bodies.
    fields = {"type", "text"} | ({"annotations", "logprobs"} if completed_output else set())
    return (isinstance(value, list) and bool(value)
            and all(isinstance(c, dict) and {"type", "text"} <= set(c) <= fields
                    and c["type"] in types and isinstance(c["text"], str)
                    and all(c[key] == [] for key in ("annotations", "logprobs") if key in c)
                    for c in value))


def _safe_source_id(value):
    return isinstance(value, str) and re.fullmatch(r"[A-Za-z0-9_.:-]{8,200}", value) is not None


def _valid_retained_source(value):
    if (not isinstance(value, dict) or set(value) != {"id", "complete", "revision"}
            or type(value.get("complete")) is not bool or not _safe_source_id(value.get("revision"))):
        return False
    identity = value.get("id")
    return (isinstance(identity, dict) and set(identity) == {"message_id", "role", "turn_id"}
            and isinstance(identity.get("role"), str)
            and identity.get("role") in {"user", "assistant"}
            and _safe_source_id(identity.get("message_id"))
            and _safe_source_id(identity.get("turn_id")))


def valid_top_metadata(value):
    """Validate observed non-content metadata; it is never projected as text."""
    if (not isinstance(value, dict) or not set(value) <= TOP_METADATA_KEYS
            or type(value.get("client_authored")) is not bool):
        return False
    if "user_input_order" in value and (type(value["user_input_order"]) is not int
                                         or not 0 <= value["user_input_order"] <= 1_000_000):
        return False
    if "fallback_token_limit_override" in value:
        limit = value["fallback_token_limit_override"]
        if type(limit) is not int or not 1 <= limit <= 1_000_000_000:
            return False
    attribution = value.get("mcp_attribution")
    if attribution is not None:
        if (not isinstance(attribution, dict) or not set(attribution) <= MCP_ATTRIBUTION_KEYS
                or not isinstance(attribution.get("status"), str)
                or not re.fullmatch(r"[A-Za-z0-9_-]{1,80}", attribution["status"])):
            return False
        if "error_reason" in attribution:
            reason = attribution["error_reason"]
            if (not isinstance(reason, str) or not re.fullmatch(r"[A-Za-z0-9 _.,:;()/'-]{1,256}", reason)):
                return False
        sources = attribution.get("sources", [])
        if not isinstance(sources, list) or len(sources) > 32:
            return False
        for source in sources:
            if (not isinstance(source, dict)
                    or not {"server_name", "tool_name", "first_turn_id"} <= set(source)
                    or not set(source) <= {"plugin_id", "connector_id", "server_name", "tool_name", "first_turn_id"}
                    or any(not isinstance(source.get(key), str) for key in source)
                    or ("plugin_id" in source and not re.fullmatch(
                        r"[A-Za-z0-9._@/-]{1,200}", source["plugin_id"]))
                    or not re.fullmatch(r"[A-Za-z0-9_-]{1,200}", source["server_name"])
                    or not (re.fullmatch(r"[A-Za-z0-9_-]{1,200}", source["tool_name"])
                            or ("connector_id" in source and len(source["tool_name"]) <= 200
                                and re.fullmatch(r"[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+", source["tool_name"])))
                    or not re.fullmatch(r"[A-Za-z0-9_-]{8,100}", source["first_turn_id"])):
                return False
            if "connector_id" in source and (
                    "plugin_id" in source or source["server_name"] != "codex_apps"
                    or not re.fullmatch(r"connector_[0-9a-f]{32}", source["connector_id"])):
                return False
    if "retained_source" in value and not _valid_retained_source(value["retained_source"]):
        return False
    if "guardian_sources" in value:
        sources = value["guardian_sources"]
        if (not isinstance(sources, list) or len(sources) > 64
                or any(not _valid_retained_source(source) for source in sources)):
            return False
    if ("guardian_source_order_guidance" in value
            and type(value["guardian_source_order_guidance"]) is not bool):
        return False
    return True


def automation_heartbeat(payload):
    """Recognize the observed scheduler delivery, which has no native call ID.

    This is automation-originated input, not a human message or the result of
    an inferred tool call. Return metadata only; the body still needs review.
    """
    if (not isinstance(payload, dict) or payload.get("type") != "function_call_output"
            or payload.get("name") != "automation_update" or payload.get("namespace") != "codex_app"
            or "call_id" in payload
            or not set(payload) <= PAYLOAD_KEYS["function_call_output"] | {"name", "namespace"}
            or not isinstance(payload.get("id"), str)
            or not re.fullmatch(r"fco_[A-Za-z0-9_-]{1,196}", payload["id"])):
        return None
    body = payload.get("output")
    if (not isinstance(body, str) or len(body) > 100000 or "<!" in body or "<?" in body):
        return None
    try:
        root = ET.fromstring(body)
    except (ET.ParseError, ValueError):
        return None
    if (root.tag != "heartbeat" or root.attrib or (root.text or "").strip()
            or [child.tag for child in root] != ["automation_id", "current_time_iso", "instructions"]
            or any(child.attrib or len(child) or (child.tail or "").strip() for child in root)):
        return None
    automation_id, scheduled_at, instruction = (child.text for child in root)
    if (not isinstance(automation_id, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,200}", automation_id)
            or not valid_timestamp(scheduled_at) or not isinstance(instruction, str) or not instruction.strip()
            or any(marker in instruction for marker in SENSITIVE_MARKERS)):
        return None
    return {"origin": "AUTOMATION", "delivery_type": "automation_heartbeat",
            "automation_id": automation_id, "scheduled_at": scheduled_at,
            "native_record_id": payload["id"], "call_link_status": "NOT_APPLICABLE_AUTOMATION_TRIGGER"}


def classify(record, line_number, reviewed_tools, blocked_calls):
    if not isinstance(record, dict) or not set(record) <= TOP_KEYS:
        return "unknown_record_shape"
    if not valid_timestamp(record.get("timestamp")) or ("ordinal" in record and type(record["ordinal"]) is not int):
        return "unknown_record_metadata"
    typ = record.get("type")
    if isinstance(typ, str) and typ in KNOWN_OMISSIONS:
        return "excluded:" + typ
    if typ != "response_item":
        return "unknown_record_type"
    payload = record.get("payload")
    if not isinstance(payload, dict):
        return "unknown_payload_shape"
    subtype = payload.get("type")
    if not isinstance(subtype, str):
        return "unknown_response_item_type"
    if subtype in {"reasoning", "agent_message"}:
        return "excluded:" + subtype
    # Hidden/internal roles and reasoning never reach metadata validation or
    # archival selection. Their bodies remain excluded even if the host adds
    # unrelated metadata fields to the same record.
    if subtype == "message":
        role = payload.get("role")
        if not isinstance(role, str):
            return "unknown_payload_scalar"
        if role not in {"user", "assistant"}:
            return "excluded:message_role:" + role
        # Context injections remain excluded even when their current provenance
        # metadata differs from ordinary user input. Never retain their bodies.
        context_meta = payload.get("internal_chat_message_metadata_passthrough", {})
        if (role == "user" and isinstance(context_meta, dict)
                and isinstance(context_meta.get("content_item_kinds"), list)
                and context_meta["content_item_kinds"] != ["user.text"]):
            return "excluded:non_user_text_context"
    # Validate this bounded set of metadata shapes only after known hidden
    # surfaces are excluded. The exact metadata bytes are retained only as
    # part of an otherwise eligible visible record and are never projected.
    if "metadata" in record and not valid_top_metadata(record["metadata"]):
        return "unknown_record_metadata"
    if subtype not in PAYLOAD_KEYS:
        return "unknown_response_item_type"
    heartbeat = automation_heartbeat(payload)
    allowed = PAYLOAD_KEYS[subtype] | ({"name", "namespace"} if heartbeat else set())
    if not set(payload) <= allowed:
        return "unknown_payload_fields"
    for field in ("id", "role", "phase", "channel", "status", "name", "namespace", "call_id"):
        if field in payload and payload[field] is not None and not isinstance(payload[field], str):
            return "unknown_payload_scalar"
    meta = payload.get("internal_chat_message_metadata_passthrough", {})
    if not isinstance(meta, dict) or not set(meta) <= (MESSAGE_META_KEYS if subtype == "message" else META_KEYS):
        return "unknown_metadata_fields"
    if ("turn_id" in meta and not isinstance(meta["turn_id"], str)) or ("create_time" in meta and not isinstance(meta["create_time"], (int, float))):
        return "unknown_metadata_value"
    if "content_item_kinds" in meta and (not isinstance(meta["content_item_kinds"], list) or any(not isinstance(k, str) for k in meta["content_item_kinds"])):
        return "unknown_metadata_value"
    if subtype == "message":
        role = payload.get("role")
        if role not in {"user", "assistant"}:
            return "excluded:message_role:" + str(role)
        if "content_item_metadata" in meta and (
                role != "user" or meta.get("content_item_kinds") != ["user.text"]
                or meta["content_item_metadata"] != [{"provenance": {"type": "user"}}]):
            return "unknown_metadata_value"
        if "status" in payload and (role != "assistant" or payload["status"] != "completed"):
            return "unknown_message_status"
        if role == "user":
            if meta.get("content_item_kinds") != ["user.text"]:
                return "excluded:non_user_text_context"
            if not text_blocks(payload.get("content"), {"input_text"}):
                return "unknown_user_content"
        else:
            phase = payload.get("phase", payload.get("channel"))
            if phase == "analysis" or payload.get("channel") == "analysis":
                return "excluded:non_visible_assistant_phase"
            if phase not in {"commentary", "final", "final_answer"}:
                return "unknown_assistant_phase"
            if not text_blocks(payload.get("content"), {"output_text"},
                               completed_output=payload.get("status") == "completed"):
                return "unknown_assistant_content"
        return None
    call_id = payload.get("call_id")
    if not heartbeat and (not isinstance(call_id, str) or not call_id):
        return "unknown_tool_call_id"
    if not heartbeat and call_id in blocked_calls:
        return "excluded:blocked_tool_call"
    if subtype in CALL_TYPES:
        body = payload.get("arguments" if subtype == "function_call" else "input")
        if not isinstance(body, str) or not isinstance(payload.get("name"), str):
            return "unknown_tool_call_shape"
    else:
        body = payload.get("output")
        if not isinstance(body, str) and not text_blocks(body, {"text", "input_text", "output_text"}):
            return "unknown_tool_output_shape"
        if not isinstance(body, str):
            body = "\n".join(item["text"] for item in body)
    if any(marker in body for marker in SENSITIVE_MARKERS):
        return "excluded:sensitive_tool_body"
    if line_number not in reviewed_tools:
        return "withheld:tool_body_not_reviewed"
    return None


def existing_original(events, session_id, line, raw, record):
    """Reuse an exact captured native record without replacing its provenance."""
    key = f"codex-visible-v1:{session_id}:{line}"
    candidates = [e for e in events if e['delivery_key'] == key or
                  (e['kind'] == 'capture.raw_record' and e['session_id'] == session_id
                   and e['payload'].get('source_line') == line)]
    if not candidates:
        return None
    if len(candidates) != 1:
        raise ArchiveError('conflicting original capture identities for session/source line')
    event = candidates[0]
    sha = digest(raw)
    payload = record['payload']
    expected_role = payload.get('role', 'tool' if payload['type'] in OUTPUT_TYPES else 'assistant')
    if (event['kind'] != 'capture.raw_record' or event['session_id'] != session_id
            or event['payload'].get('source_line') != line
            or event['payload'].get('raw_sha256') != sha or event['outputs'] != [sha]
            or event['payload'].get('source_type') != payload['type']
            or event['payload'].get('call_id') != payload.get('call_id')
            or event['timestamp'] != record['timestamp']
            or event['actor']['role'] != expected_role
            or event['payload'].get('cwd_binding_verified') is not True):
        raise ArchiveError('delivery key conflict: original capture identity or bytes mismatch')
    return event


def bind_original_to_run(archive, original, run_id, round_start):
    """Append selection for a new run; the original author/run/time stay intact."""
    p = original['payload']
    key = 'codex-run-binding-v1:' + digest((original['id'] + '\n' + run_id).encode())
    parents = [original['id']]
    bindings = {key: [] for key in ('method', 'instruction', 'config', 'input')}
    if round_start:
        parents.append(round_start['id'])
        bindings = round_start['bindings']
    return archive.append({
        'kind': 'capture.run_binding', 'actor': {'id': 'codex-capture-adapter', 'role': 'tool'},
        'session_id': original['session_id'], 'run_id': run_id,
        'operation_id': 'codex-run-binding:' + digest(key.encode())[:40], 'attempt_id': 'capture-v1',
        'parents': parents, 'inputs': [p['raw_sha256']], 'outputs': [], 'bindings': bindings,
        'payload': {'raw_event_id': original['id'], 'raw_sha256': p['raw_sha256'],
                    'source_line': p['source_line'], 'source_session_id': original['session_id'],
                    'original_run_id': original['run_id'], 'selected_run_id': run_id,
                    'round_start_event_id': round_start['id'] if round_start else None,
                    'boundary': 'Explicit evidence selection for this run; original authorship, generation run and time are unchanged'}
    }, key)


def reuse_existing_marker(archive_root: Path, expected_cwd: Path, session_id: str,
                          run_id: str, marker_text: str, prepared_event_id: str,
                          *, archive_writer: _ArchiveWriter, adapter_driver: Path | None = None):
    """Bind one exact archived visible marker without rescanning a large rollout.

    The collector must already have retained the original selected message and a
    stable coverage boundary that includes it. This path considers only those
    archived visible records, chooses the earliest exact marker after the exact
    prepared event, and records the selection rule plus its limitations.
    """
    target = Path(expected_cwd).absolute()
    archive_root = Path(archive_root).absolute()
    if archive_root != target / "research" / "archive":
        raise ArchiveError("archive must be the exact target laboratory research/archive")
    if any(".." in path.parts for path in (archive_root, target)):
        raise ArchiveError("project and archive paths may not contain parent traversal")
    if not isinstance(archive_writer, _ArchiveWriter) or archive_writer.root.absolute() != archive_root:
        raise ArchiveError("capture writer must be a live capability for this exact archive")
    if not isinstance(marker_text, str) or not marker_text.startswith(f"[HUNDRED:{run_id}:") or not marker_text.endswith("]"):
        raise ArchiveError("exact run-bound marker required")
    with regular_file(target / "LAB_PROFILE.json") as profile_stream:
        profile = strict_json(profile_stream.read())
    with regular_file(target / ".lab" / "philosophy.json") as marker_stream:
        lab_marker = strict_json(marker_stream.read())
    if (not isinstance(profile, dict) or not isinstance(profile.get("lab"), dict)
            or profile["lab"].get("kind") != "PHILOSOPHY_PROGRAM"):
        raise ArchiveError("capture target must be an identified philosophy laboratory")
    if (not isinstance(lab_marker, dict) or lab_marker.get("schema_version") != 1
            or lab_marker.get("kernel") != "philosophy.v1"
            or lab_marker.get("archive_format") != "research-archive.v1"):
        raise ArchiveError("capture target philosophy marker is invalid")

    events = archive_writer.events()
    prepared = [e for e in events if e["id"] == prepared_event_id]
    if (len(prepared) != 1 or prepared[0]["kind"] != "hundred.prepared"
            or prepared[0]["run_id"] != run_id or prepared[0]["session_id"] != session_id):
        raise ArchiveError("exact prior prepared stage is required")
    prepared_event = prepared[0]
    task = prepared_event["payload"].get("request", {})
    if not marker_text.startswith(f"[HUNDRED:{run_id}:{task.get('stage')} sha256="):
        raise ArchiveError("marker does not identify the exact prepared stage")

    identities = [e for e in events if e["kind"] == "capture.session_identified"
                  and e["session_id"] == session_id
                  and e["payload"].get("source_cwd") == str(target)
                  and e["payload"].get("selection") == "exact-project-cwd"]
    if not identities:
        raise ArchiveError("exact project-cwd session identity is not archived")
    matching = []
    for event in events:
        if (event["kind"] != "capture.raw_record" or event["session_id"] != session_id
                or event["actor"]["role"] != "assistant"
                or event["payload"].get("source_type") != "message"
                or event["payload"].get("cwd_binding_verified") is not True):
            continue
        raw = archive_writer.get(event["payload"]["raw_sha256"])
        record = strict_json(raw)
        if classify(record, event["payload"]["source_line"], set(), set()) is not None:
            continue
        payload = record.get("payload", {})
        if (payload.get("role") != "assistant"
                or payload.get("phase", payload.get("channel")) != "commentary"):
            continue
        text = "\n".join(item["text"] for item in payload["content"])
        if marker_text in text.splitlines():
            exact = existing_original(events, session_id, event["payload"]["source_line"], raw, record)
            if exact is None or exact["id"] != event["id"]:
                raise ArchiveError("selected marker is not the exact retained original")
            matching.append((event["payload"]["source_line"], event, raw))
    if not matching:
        raise ArchiveError("no exact archived commentary record matches this prepared marker")
    prepared_at = datetime.datetime.fromisoformat(prepared_event["timestamp"].replace("Z", "+00:00"))
    eligible = [item for item in matching
                if datetime.datetime.fromisoformat(item[1]["timestamp"].replace("Z", "+00:00")) > prepared_at]
    if not eligible:
        raise ArchiveError("no matching marker original follows its prepared stage")
    eligible.sort(key=lambda item: item[0])
    line_number, original, raw = eligible[0]

    linked_messages = [e for e in events if e["kind"] == "collector.message"
                       and e["session_id"] == session_id
                       and e["payload"].get("source_line") == line_number
                       and e["payload"].get("raw_event_id") == original["id"]
                       and original["id"] in e["parents"]]
    if len(linked_messages) != 1:
        raise ArchiveError("collector must link the exact visible message to its raw original")
    message_event = linked_messages[0]

    coverages = []
    for event in events:
        if event["kind"] != "collector.coverage" or event["session_id"] != session_id:
            continue
        payload = event["payload"]
        cursor = payload.get("cursor", {})
        if (payload.get("source_basename") != original["payload"].get("source_basename")
                or line_number > cursor.get("lines", 0)
                or message_event["id"] not in event["parents"]
                or cursor.get("observed_size") != cursor.get("offset")
                or original["payload"].get("source_basename") != payload.get("source_basename")):
            continue
        if any(gap.get("source_line") == line_number for gap in cursor.get("gaps", [])):
            continue
        matching_identities = [i for i in identities
                               if digest(canonical(i["payload"])) == cursor.get("identity_hash")]
        if not matching_identities:
            continue
        coverages.append((cursor.get("lines", 0), event, cursor, matching_identities[-1]))
    if not coverages:
        raise ArchiveError("no stable collector boundary covers the exact marker without a line gap")
    coverages.sort(key=lambda item: (item[0], item[1].get("sequence", 0)))
    _, collector_coverage, cursor, identity_event = coverages[-1]

    starts = [e for e in events if e["run_id"] == run_id and e["kind"] == "operation.started"]
    if len(starts) != 1:
        raise ArchiveError("exactly one philosophy round start is required for run binding")
    binding = bind_original_to_run(archive_writer, original, run_id, starts[0])

    method_bytes = Path(__file__).read_bytes()
    method_sha = archive_writer.put(method_bytes)
    driver_sha = None
    if adapter_driver is not None:
        driver_path = Path(adapter_driver).absolute()
        if not driver_path.is_relative_to(target):
            raise ArchiveError("adapter driver must be saved inside the exact target laboratory")
        with regular_file(driver_path) as driver_stream:
            driver_sha = archive_writer.put(driver_stream.read())
    report = {
        "format": "codex-visible-selection.v1", "capture_status": "filtered_selection",
        "adapter": "capture_codex.reuse_existing_marker.v1", "adapter_sha256": method_sha,
        "adapter_driver_sha256": driver_sha,
        "session_id": session_id, "run_id": run_id,
        "source_basename": original["payload"]["source_basename"],
        "cwd_binding_verified": True, "target_identity_verified": True,
        "technical_transfer": False, "source_snapshot_bytes": cursor["observed_size"],
        "source_complete_bytes": cursor["offset"],
        "source_snapshot_sha256": cursor["prefix_sha256"],
        "partial_tail_bytes": cursor["observed_size"] - cursor["offset"],
        "complete_source_lines": cursor["lines"], "selected_range": [line_number, line_number],
        "reviewed_tool_lines": [], "captured_records": 1, "excluded_counts": {},
        "coverage_gaps": [], "status": "BOUNDED_COMPLETE", "gaps": [], "exclusions": [],
        "limitations": ["whole_provider_trace_incomplete", "only_one_exact_visible_record_reused",
                        "collector_snapshot_is_the_source_boundary; rollout_was_not_rescanned",
                        "duplicate_exact_markers_preserved; earliest post-prepare source line selected"],
        "full_provider_capture": False,
        "raw_records": [{"source_line": line_number, "sha256": original["payload"]["raw_sha256"],
                         "bytes": len(raw)}],
        "raw_event_ids": [original["id"]], "tool_link_ids": [],
        "run_binding_event_ids": [binding["id"]],
        "matching_marker_records": [{"event_id": e["id"], "source_line": n}
                                    for n, e, _ in eligible],
        "selected_original_event_id": original["id"],
        "collector_message_event_id": message_event["id"],
        "collector_coverage_event_id": collector_coverage["id"],
        "session_identity_event_id": identity_event["id"],
    }
    encoded_report = (json.dumps(report, sort_keys=True, ensure_ascii=False, indent=2) + "\n").encode()
    report_sha = archive_writer.put(encoded_report)
    bindings = starts[0].get("bindings", {key: [] for key in ("method", "instruction", "config", "input")})
    coverage = archive_writer.append({
        "kind": "capture.coverage", "actor": {"id": "codex-capture-adapter", "role": "tool"},
        "session_id": session_id, "run_id": run_id,
        "operation_id": "codex-capture-report:" + report_sha, "attempt_id": "capture-reuse-v1",
        "parents": [original["id"], message_event["id"], collector_coverage["id"],
                    identity_event["id"], binding["id"]],
        "inputs": [method_sha] + ([driver_sha] if driver_sha else []), "outputs": [report_sha],
        "bindings": bindings,
        "payload": {"capture_status": "filtered_selection", "report_sha256": report_sha,
                    "status": "BOUNDED_COMPLETE", "gaps": [], "exclusions": []},
    }, delivery_key="codex-visible-report-v1:" + report_sha)
    report["coverage_event_id"] = coverage["id"]
    return {"raw_event_ids": [original["id"]], "coverage_event_id": coverage["id"],
            "run_binding_ids": [binding["id"]], "timestamp": original["timestamp"],
            "marker": marker_text, "selected_source_line": line_number,
            "matching_source_lines": [n for n, _, _ in eligible],
            "collector_coverage_event_id": collector_coverage["id"]}


def capture(archive_root: Path, source: Path, session_id: str, expected_cwd: Path,
            *, start_line: int = 1, end_line: int | None = None,
            reviewed_tool_lines=(), run_id: str | None = None, target_lab: Path | None = None,
            technical_transfer: bool = False, historical_import: bool = False,
            max_bytes: int = 64 * 1024 * 1024, archive_writer=None):
    if start_line < 1 or (end_line is not None and end_line < start_line):
        raise ValueError("invalid source line range")
    if max_bytes < 1:
        raise ValueError("max_bytes must be positive")
    target = (target_lab or expected_cwd).absolute()
    if any(".." in path.parts for path in (archive_root, expected_cwd, target)):
        raise ValueError("project and archive paths may not contain parent traversal")
    cross_root = target != expected_cwd.absolute()
    if technical_transfer and historical_import:
        raise ValueError("choose technical transfer or explicitly authorized historical import")
    if cross_root and not (technical_transfer or historical_import):
        raise ValueError("cross-project capture requires explicit technical transfer")
    if cross_root and end_line is None:
        raise ValueError("technical transfer requires an explicit closed line range")
    if archive_root.absolute() != target / "research" / "archive":
        raise ValueError("archive must be the exact target laboratory research/archive")
    with regular_file(target / "LAB_PROFILE.json") as profile_stream:
        profile = strict_json(profile_stream.read())
    with regular_file(target / ".lab" / "philosophy.json") as marker_stream:
        marker = strict_json(marker_stream.read())
    if (not isinstance(profile, dict) or not isinstance(profile.get("lab"), dict)
            or profile["lab"].get("kind") != "PHILOSOPHY_PROGRAM"):
        raise ValueError("capture target must be an identified philosophy laboratory")
    if (not isinstance(marker, dict) or marker.get("schema_version") != 1
            or marker.get("kernel") != "philosophy.v1"
            or marker.get("archive_format") != "research-archive.v1"):
        raise ValueError("capture target philosophy marker is invalid")
    reviewed = set(reviewed_tool_lines)
    if any(not isinstance(n, int) or n < start_line or (end_line is not None and n > end_line) for n in reviewed):
        raise ValueError("reviewed tool lines must be within selected range")
    with rollout_file(source, max_bytes=max_bytes) as stream:
        source_basename = stream.logical_name
        before = stream.logical_stat()
        if before.st_size > max_bytes:
            raise ValueError("source exceeds bounded capture size")
        snapshot = stream.read(before.st_size)
        after = stream.logical_stat()
    if len(snapshot) != before.st_size or after.st_size < before.st_size:
        raise ValueError("source truncated during snapshot")
    cutoff = snapshot.rfind(b"\n") + 1
    complete = snapshot[:cutoff]
    raw_lines = complete.splitlines(keepends=True)
    if not raw_lines:
        raise ValueError("source has no complete session metadata record")
    first = strict_json(raw_lines[0])
    if not isinstance(first, dict):
        raise ValueError("invalid session metadata record")
    meta = first.get("payload", {})
    if not isinstance(meta, dict):
        raise ValueError("invalid session metadata payload")
    if first.get("type") != "session_meta" or meta.get("id") != session_id:
        raise ValueError("source session identity mismatch")
    if not isinstance(meta.get("cwd"), str) or Path(meta["cwd"]).absolute() != expected_cwd.absolute():
        raise ValueError("source cwd does not match expected project")
    records = []
    for line_number, raw in enumerate(raw_lines, 1):
        try:
            record = strict_json(raw)
        except (ValueError, UnicodeError) as exc:
            raise ValueError(f"malformed complete JSONL record at line {line_number}") from exc
        records.append((line_number, raw, record))
    upper = min(end_line or len(records), len(records))
    if start_line > len(records) or (end_line is not None and end_line > len(records)):
        raise ValueError("selected range extends past complete source records")
    # Safety checks consider all call metadata in this exact source so a reviewed
    # result cannot bypass a blocked call situated before the selected range.
    blocked = set()
    model_at_line = {}
    model = {"status": "unknown", "reason": "no preceding native model observation"}
    for number, _, record in records:
        payload = record.get("payload", {}) if isinstance(record, dict) else {}
        if isinstance(record, dict) and record.get("type") == "turn_context":
            model = observed_model(payload, number)
        model_at_line[number] = model
        if isinstance(payload, dict) and payload.get("type") in CALL_TYPES:
            why = classify(record, number, {number}, set())
            if why:
                blocked.add(payload.get("call_id"))
    selected, excluded = [], Counter()
    selected_call_ids, selected_output_ids = set(), set()
    outputs_without_preceding_calls = False
    for number, raw, record in records[start_line - 1:upper]:
        why = classify(record, number, reviewed, blocked)
        if why:
            excluded[why] += 1
            continue
        selected.append((number, raw, record))
        payload = record["payload"]
        if payload["type"] in CALL_TYPES:
            selected_call_ids.add(payload["call_id"])
        elif payload["type"] in OUTPUT_TYPES and not automation_heartbeat(payload):
            selected_output_ids.add(payload["call_id"])
            if payload["call_id"] not in selected_call_ids:
                outputs_without_preceding_calls = True
    gaps = []
    limitations = ["provider_request_envelopes_unavailable", "future_records_not_captured",
                   "excluded_runtime_and_hidden_records", "no_claim_of_full_provider_capture",
                   "model_is_reported_configuration_not_backend_attestation", "thinking_duration_unavailable"]
    if any(automation_heartbeat(record["payload"]) for _, _, record in selected):
        limitations.append("automation_trigger_is_replayed_input_without_native_call_link_not_new_human_authorship")
    if start_line > 1 or upper < len(records):
        limitations.append("bounded_range_omits_other_source_records")
    if end_line is None:
        gaps.append("live_source_snapshot_not_finalized")
    if len(snapshot) != cutoff:
        gaps.append("partial_tail_withheld")
    if after.st_size > before.st_size:
        gaps.append("source_grew_during_snapshot")
    if any(key.startswith("unknown") for key in excluded):
        gaps.append("unknown_schema_records_withheld")
    if any(key in {"excluded:sensitive_tool_body", "excluded:blocked_tool_call"} for key in excluded):
        gaps.append("sensitive_tool_bodies_withheld")
    if any(key.startswith("withheld") for key in excluded):
        gaps.append("unreviewed_tool_bodies_withheld")
    if selected_call_ids - selected_output_ids:
        gaps.append("selected_tool_calls_without_selected_results")
    if selected_output_ids - selected_call_ids:
        gaps.append("selected_tool_results_without_selected_calls")
    elif outputs_without_preceding_calls:
        gaps.append("selected_tool_results_without_preceding_selected_calls")
    report = {
        "format": "codex-visible-selection.v1", "session_id": session_id,
        "source_basename": source_basename, "cwd_binding_verified": True,
        "target_identity_verified": True, "technical_transfer": bool(cross_root and technical_transfer),
        "source_snapshot_bytes": len(snapshot), "source_complete_bytes": cutoff,
        "source_snapshot_sha256": digest(snapshot), "partial_tail_bytes": len(snapshot) - cutoff,
        "complete_source_lines": len(records), "selected_range": [start_line, upper],
        "reviewed_tool_lines": sorted(reviewed), "captured_records": len(selected),
        "excluded_counts": dict(sorted(excluded.items())), "coverage_gaps": gaps,
        "status": "INCOMPLETE" if gaps else "BOUNDED_COMPLETE",
        "gaps": gaps, "exclusions": [{"reason": k, "count": v} for k, v in sorted(excluded.items())],
        "limitations": limitations,
        "capture_status": "filtered_selection", "full_provider_capture": False,
        "raw_records": [{"source_line": n, "sha256": digest(raw), "bytes": len(raw)} for n, raw, _ in selected],
    }
    if archive_writer is not None:
        if not isinstance(archive_writer, _ArchiveWriter) or archive_writer.root.absolute() != archive_root.absolute():
            raise ArchiveError('capture writer must be a live capability for this exact archive')
        archive_writer._ensure_open()
        archive = archive_writer
    else:
        archive = Archive(archive_root)
        archive.init()
    if historical_import:
        report["historical_import"] = True
    run_id = run_id or "codex:" + session_id
    report["run_id"] = run_id
    raw_event_ids = []
    run_binding_ids = []
    stored_events = archive.events()
    starts = [e for e in stored_events if e['run_id'] == run_id and e['kind'] == 'operation.started'
              and e['payload'].get('protocol') == 'philosophy-round.v1']
    if len(starts) > 1:
        raise ArchiveError('run has conflicting philosophy round starts')
    round_start = starts[0] if starts else None
    calls = {}
    tool_pairs = []
    bindings = {key: [] for key in ("method", "instruction", "config", "input")}
    for number, raw, record in selected:
        sha = digest(raw)
        payload = record["payload"]
        role = payload.get("role", "tool" if payload["type"] in OUTPUT_TYPES else "assistant")
        stored = existing_original(stored_events, session_id, number, raw, record)
        request = {
            "kind": "capture.raw_record", "actor": {"id": "codex:" + role, "role": role},
            "timestamp": record["timestamp"], "model": model_at_line[number],
            "session_id": session_id, "run_id": run_id,
            "operation_id": f"codex-source-line:{session_id}:{number}", "attempt_id": "capture-v1",
            "parents": [],
            "inputs": [], "outputs": [sha], "bindings": bindings,
            "payload": {"format": report["format"], "source_basename": source_basename,
                        "source_line": number, "raw_sha256": sha,
                        "source_type": payload["type"], "call_id": payload.get("call_id"),
                        "source_timestamp": record["timestamp"],
                        "source_timestamp_provenance": "local-native-record; clock not independently attested",
                        "cwd_binding_verified": True},
        }
        heartbeat = automation_heartbeat(payload)
        if heartbeat:
            request["payload"].update(heartbeat)
        if stored is None:
            archive.put(raw)
            try:
                stored = archive.append(request, delivery_key=f"codex-visible-v1:{session_id}:{number}")
            except ArchiveError:
                # A concurrently running collector may have committed the same
                # exact original after our metadata snapshot. Reuse only after
                # the same verification, and propagate every other conflict.
                stored = existing_original(archive.events(), session_id, number, raw, record)
                if stored is None:
                    raise
            stored_events.append(stored)
        if archive.get(sha) != raw:
            raise ArchiveError('original byte verification failed')
        if stored['run_id'] != run_id:
            run_binding_ids.append(bind_original_to_run(archive, stored, run_id, round_start)['id'])
        raw_event_ids.append(stored["id"])
        if payload["type"] in CALL_TYPES:
            calls[payload["call_id"]] = stored["id"]
        elif payload["type"] in OUTPUT_TYPES and not heartbeat and payload["call_id"] in calls:
            tool_pairs.append((payload["call_id"], calls[payload["call_id"]], stored["id"]))
    tool_link_ids = []
    for call_id, call_event, output_event in tool_pairs:
        pair_sha = digest((call_event + "\n" + output_event).encode())
        link_request = {
            "kind": "capture.tool_link", "actor": {"id": "codex-capture-adapter", "role": "tool"},
            "session_id": session_id, "run_id": run_id,
            "operation_id": "codex-tool-link:" + pair_sha, "attempt_id": "capture-v1",
            "parents": [call_event, output_event], "inputs": [], "outputs": [], "bindings": bindings,
            "payload": {"call_id": call_id, "call_event_id": call_event, "output_event_id": output_event,
                        "boundary": "Native call-ID correspondence; no claim of tool correctness"},
        }
        link_key = 'codex-tool-link-v1:' + pair_sha
        # Correspondence is a property of originals, not of their later use in
        # a round. Preserve an existing link's first run just like the originals.
        links = [e for e in archive.events() if e['delivery_key'] == link_key]
        if links:
            link = links[0]
            if (link['kind'] != 'capture.tool_link' or link['session_id'] != session_id
                    or link['parents'] != [call_event, output_event]
                    or link['payload'].get('call_id') != call_id
                    or link['payload'].get('call_event_id') != call_event
                    or link['payload'].get('output_event_id') != output_event):
                raise ArchiveError('tool correspondence identity conflict')
        else:
            link = archive.append(link_request, delivery_key=link_key)
        tool_link_ids.append(link["id"])
    report["raw_event_ids"] = raw_event_ids
    report["tool_link_ids"] = tool_link_ids
    if run_binding_ids:
        report["run_binding_event_ids"] = run_binding_ids
    encoded_report = (json.dumps(report, sort_keys=True, ensure_ascii=False, indent=2) + "\n").encode()
    sha = archive.put(encoded_report)
    coverage = archive.append({
        "kind": "capture.coverage", "actor": {"id": "codex-capture-adapter", "role": "tool"},
        "session_id": session_id, "run_id": run_id, "operation_id": "codex-capture-report:" + sha,
        "attempt_id": "capture-v1", "parents": raw_event_ids + tool_link_ids + run_binding_ids, "inputs": [], "outputs": [sha],
        "bindings": bindings, "payload": {"capture_status": "filtered_selection", "report_sha256": sha,
                                             "status": report["status"], "gaps": gaps,
                                             "exclusions": report["exclusions"]},
    }, delivery_key="codex-visible-report-v1:" + sha)
    report["coverage_event_id"] = coverage["id"]
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--source", type=Path, help="Exact local rollout; never a directory")
    identity = parser.add_mutually_exclusive_group(required=True)
    identity.add_argument("--session-id")
    identity.add_argument("--current", action="store_true", help="Explicit opt-in to current thread exact-ID lookup")
    parser.add_argument("--expected-cwd", type=Path, required=True, help="Explicit exact authorized project root; factory use is only a technical demonstration")
    parser.add_argument("--target-lab", type=Path, help="Exact target philosophy laboratory; defaults to expected cwd")
    parser.add_argument("--technical-transfer", action="store_true", help="Explicitly allow a bounded technical capture from expected cwd into target lab")
    parser.add_argument("--historical-import", action="store_true", help="Explicit user-authorized import of this exact historical session; requires a closed range for cross-project import")
    parser.add_argument("--run-id", help="Bind this capture to the authorized local round run")
    parser.add_argument("--start-line", type=int, default=1)
    parser.add_argument("--end-line", type=int)
    parser.add_argument("--reviewed-tool-lines", default="", help="Comma-separated exact tool record lines whose bodies were reviewed")
    parser.add_argument("--max-bytes", type=int, default=64 * 1024 * 1024)
    args = parser.parse_args(argv)
    session_id = os.environ.get("CODEX_THREAD_ID") if args.current else args.session_id
    if not session_id:
        parser.error("current CODEX_THREAD_ID is unavailable; supply exact --session-id")
    try:
        reviewed = [int(item) for item in args.reviewed_tool_lines.split(",") if item]
        source = args.source or resolve_session(session_id, args.expected_cwd)
        result = capture(args.archive, source, session_id, args.expected_cwd,
                         start_line=args.start_line, end_line=args.end_line,
                         reviewed_tool_lines=reviewed, run_id=args.run_id, target_lab=args.target_lab,
                         technical_transfer=args.technical_transfer,
                         historical_import=args.historical_import, max_bytes=args.max_bytes)
    except (ValueError, OSError, sqlite3.Error) as exc:
        parser.exit(2, f"capture failed: {exc}\n")
    print(json.dumps(result, sort_keys=True, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
