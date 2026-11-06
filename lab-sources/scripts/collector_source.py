#!/usr/bin/env python3
"""Read-only scoped discovery and safe projections for the local collector.

Discovery reads metadata from the native SQLite database, never message bodies
or rollout directories. A discovered pathname is not an authorization to read
it: the caller must use ``regular_file`` and check its first session_meta ID/cwd.

``project_record`` never returns arbitrary native envelopes. Original bytes may
be retained only when its text payload has ``retain_original=True``. Tools are
metadata-only review candidates; projected attachment text is explicitly not an
original record. Parse input bytes with capture_codex.strict_json first.
"""
from __future__ import annotations

import copy
import datetime
import hashlib
import json
import math
from pathlib import Path
import re
import sqlite3

from capture_codex import (CALL_TYPES, OUTPUT_TYPES, PAYLOAD_KEYS, TOP_KEYS,
                           classify, observed_model, regular_file, valid_timestamp, automation_heartbeat)

SESSION_ID = re.compile(r"[A-Za-z0-9_-]{8,100}\Z")
UNKNOWN_MODEL = {"status": "unknown", "reason": "no model observation for this turn"}
USER_ATTACHMENTS = {"user.image", "user.file", "user.audio", "user.video"}
EXCLUDED_EVENTS = {
    "token_count", "agent_reasoning", "agent_reasoning_delta",
    "agent_reasoning_raw_content", "agent_reasoning_raw_content_delta",
    "agent_message", "agent_message_delta", "user_message",
    "item_completed", "thread_settings_applied",
}


def _path(value, label):
    if not isinstance(value, (str, Path)) or not str(value):
        raise ValueError(label + " must be a path")
    result = Path(value)
    if not result.is_absolute() or ".." in result.parts:
        raise ValueError(label + " must be absolute without parent traversal")
    return result


def _scalar(value, limit=1000):
    return value if isinstance(value, str) and len(value) <= limit else None


def _identifier(value):
    return value if isinstance(value, str) and SESSION_ID.fullmatch(value) else None


def _safe_model(value):
    """Do not trust persisted cursor metadata to contain a safe native envelope."""
    if not isinstance(value, dict) or value.get("status") != "known":
        return copy.deepcopy(UNKNOWN_MODEL)
    observed = value.get("value")
    if not isinstance(observed, dict):
        return copy.deepcopy(UNKNOWN_MODEL)
    line = value.get("source_line")
    if type(line) is not int or line < 1:
        return copy.deepcopy(UNKNOWN_MODEL)
    return observed_model({"model": observed.get("model"),
                           "effort": observed.get("reasoning_effort")}, line)


def _milliseconds(value):
    return (not isinstance(value, bool) and isinstance(value, (int, float))
            and (not isinstance(value, float) or math.isfinite(value))
            and 0 <= value <= 2 ** 63 - 1)


def _lifecycle_time(value):
    """Project observed native epoch seconds or zoned ISO without guessing units.

    Numeric seconds are the inspected native task lifecycle schema, distinct
    from duration_ms. Millisecond-looking epochs exceed datetime bounds and are
    rejected, not heuristically divided. The source value/unit remains visible.
    """
    if valid_timestamp(value):
        return {"value": value, "unit": "iso8601-with-timezone", "normalized_utc":
                datetime.datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(datetime.timezone.utc).isoformat(),
                "source": "native-task-lifecycle"}
    if (isinstance(value, bool) or not isinstance(value, (int, float))
            or (isinstance(value, float) and not math.isfinite(value))):
        return None
    try:
        stamp = datetime.datetime.fromtimestamp(value, datetime.timezone.utc).isoformat()
    except (OverflowError, OSError, ValueError):
        return None
    return {"value": value, "unit": "unix-seconds", "normalized_utc": stamp,
            "precision": "one-second" if isinstance(value, int) else "fractional-seconds-as-recorded",
            "source": "native-task-lifecycle"}


def _chunks(values, size=500):
    values = list(values)
    for start in range(0, len(values), size):
        yield values[start:start + size]


def _native_source(value):
    """Only a small observed source label; never return a serialized envelope."""
    if isinstance(value, str) and re.fullmatch(r"[A-Za-z0-9_.-]{1,100}", value):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except (ValueError, TypeError):
            return None
        if isinstance(parsed, dict) and "subagent" in parsed:
            return "subagent"
    return None


def _internal_runtime_source(value):
    """Classify native subagent.other from metadata, without opening its file.

    Guardian and future ``other`` runtime sources are not conversation/authoring
    agents. Their composite prompts may contain privileged context, so an
    unrecognized subtype is still excluded rather than treated as a new chat.
    """
    if not isinstance(value, str):
        return None
    try:
        source = json.loads(value)
    except (ValueError, TypeError):
        return None
    agent = source.get('subagent') if isinstance(source, dict) else None
    if not isinstance(agent, dict) or 'other' not in agent:
        return None
    subtype = agent['other']
    if not isinstance(subtype, str) or not re.fullmatch(r'[A-Za-z0-9_.:-]{1,100}', subtype):
        subtype = 'UNKNOWN_NATIVE_OTHER_SUBTYPE'
    return {
        'collection_policy': 'EXCLUDED_INTERNAL_RUNTIME',
        'native_source_subtype': subtype,
        'collection_policy_reason': ('native subagent.other runtime; only metadata inventory is permitted'
                                     if 'thread_spawn' not in agent else
                                     'ambiguous native runtime/spawn metadata; content excluded'),
    }


def discover_sessions(db: Path, project_root: Path,
                      explicit_sessions: dict[str, str]) -> list[dict]:
    """Discover exact-project sessions, exact authorized IDs and descendants.

    Explicit values are expected original cwd paths, not display project names.
    Unknown explicit IDs or broken required metadata raise ValueError, so the
    caller cannot silently report complete discovery. Descendants are included
    only through observed native thread_spawn_edges, including cross-cwd agents.
    The returned source paths are validated by the caller immediately at use.
    """
    db = _path(db, "database")
    project_root = _path(project_root, "project root")
    if not isinstance(explicit_sessions, dict):
        raise ValueError("explicit sessions must map IDs to expected cwd")
    expected = {}
    for sid, cwd in explicit_sessions.items():
        if not _identifier(sid):
            raise ValueError("invalid explicit session ID")
        expected[sid] = str(_path(cwd, "explicit expected cwd"))
    with regular_file(db):
        pass
    connection = sqlite3.connect(db.as_uri() + "?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    try:
        connection.execute("PRAGMA query_only = ON")
        connection.execute("BEGIN")
        columns = {row[1] for row in connection.execute("PRAGMA table_info(threads)")}
        edge_columns = {row[1] for row in connection.execute("PRAGMA table_info(thread_spawn_edges)")}
        if not {"id", "rollout_path", "cwd"} <= columns:
            raise ValueError("unsupported threads metadata schema")
        if not {"parent_thread_id", "child_thread_id"} <= edge_columns:
            raise ValueError("unsupported thread_spawn_edges metadata schema")
        optional = ("name", "title", "agent_nickname", "agent_role", "agent_path", "source")
        selected = ["id", "rollout_path", "cwd"] + [key for key in optional if key in columns]
        select = "SELECT " + ", ".join(selected) + " FROM threads"

        rows = {}

        def add(result):
            for row in result:
                item = dict(row)
                sid = item["id"]
                if not _identifier(sid):
                    raise ValueError("selected session has invalid ID")
                if sid in rows and item != rows[sid]:
                    raise ValueError("conflicting selected session metadata")
                _path(item["cwd"], "selected source cwd")
                _path(item["rollout_path"], "selected source path")
                rows[sid] = item

        add(connection.execute(select + " WHERE cwd = ?", (str(project_root),)))
        for chunk in _chunks(expected):
            add(connection.execute(select + " WHERE id IN (" + ",".join("?" for _ in chunk) + ")", chunk))
        for sid, cwd in expected.items():
            if sid not in rows:
                raise ValueError("explicit session identity not found: " + sid)
            if str(Path(rows[sid]["cwd"])) != cwd:
                raise ValueError("explicit session cwd mismatch: " + sid)

        frontier = set(rows)
        checked = set()
        parents = {}
        while frontier:
            checked.update(frontier)
            children = set()
            for chunk in _chunks(sorted(frontier)):
                marks = ",".join("?" for _ in chunk)
                # Incoming edges identify project-local agents even if their
                # parent has another cwd; they never cause parent traversal.
                edges = connection.execute(
                    "SELECT parent_thread_id, child_thread_id FROM thread_spawn_edges "
                    "WHERE parent_thread_id IN (" + marks + ") OR child_thread_id IN (" + marks + ")",
                    chunk + chunk)
                for edge in edges:
                    parent, child = edge
                    if not _identifier(parent) or not _identifier(child) or parent == child:
                        raise ValueError("invalid selected spawn edge")
                    if child in parents and parents[child] != parent:
                        raise ValueError("conflicting selected agent parents")
                    parents[child] = parent
                    if parent in frontier:
                        children.add(child)
            missing = children - rows.keys()
            for chunk in _chunks(sorted(missing)):
                add(connection.execute(select + " WHERE id IN (" + ",".join("?" for _ in chunk) + ")", chunk))
            if missing - rows.keys():
                raise ValueError("selected descendant metadata unavailable: " + ",".join(sorted(missing - rows.keys())))
            frontier = children - checked
        for sid in rows:
            visited = set()
            parent = sid
            while parent in parents:
                if parent in visited:
                    raise ValueError("cyclic selected spawn ancestry")
                visited.add(parent)
                parent = parents[parent]

        result = []
        for sid, row in sorted(rows.items()):
            parent = parents.get(sid)
            source = _native_source(row.get("source"))
            internal_runtime = _internal_runtime_source(row.get('source'))
            agent_path = _scalar(row.get("agent_path"))
            role = _scalar(row.get("agent_role"))
            nickname = _scalar(row.get("agent_nickname"))
            is_agent = bool(parent or source == "subagent" or nickname or
                            (agent_path and agent_path != "/root"))
            result.append({
                "session_id": sid, "source_path": row["rollout_path"],
                "source_cwd": row["cwd"], "source_project": Path(row["cwd"]).name,
                "title": _scalar(row.get("name")) or _scalar(row.get("title")),
                "session_kind": "internal_runtime" if internal_runtime else "subagent" if is_agent else "primary_chat",
                "parent_session_id": parent, "agent_name": nickname,
                "role": role, "agent_path": agent_path, "source": source,
                "metadata_source": "native-threads-database",
                "selection": ("explicit-session" if sid in expected else
                              "exact-project-cwd" if row["cwd"] == str(project_root) else
                              "descendant-of-selected-session"),
                **(internal_runtime or {}),
            })
        return result
    except sqlite3.Error as exc:
        raise ValueError("native metadata database unavailable or incompatible") from exc
    finally:
        connection.close()


def _mixed_user_projection(record):
    """Recover text only when every provenance kind denotes human input."""
    payload = record.get("payload")
    if not isinstance(payload, dict) or payload.get("type") != "message" or payload.get("role") != "user":
        return None
    if not set(payload) <= PAYLOAD_KEYS["message"]:
        return None
    meta = payload.get("internal_chat_message_metadata_passthrough")
    if not isinstance(meta, dict):
        return None
    kinds = meta.get("content_item_kinds")
    if (not isinstance(kinds, list) or not kinds or any(not isinstance(k, str) for k in kinds)
            or not set(kinds) <= ({"user.text"} | USER_ATTACHMENTS)):
        return None
    if not set(kinds) & USER_ATTACHMENTS:
        return None
    contents = payload.get("content")
    if not isinstance(contents, list):
        return None
    texts = []
    omitted = ["attachment_body_not_captured"]
    for block in contents:
        if not isinstance(block, dict) or not isinstance(block.get("type"), str):
            return None
        if block["type"] == "input_text":
            if ("user.text" not in kinds or set(block) != {"type", "text"}
                    or not isinstance(block.get("text"), str)):
                return None
            texts.append(block["text"])
        else:
            # Attachment bytes, URLs, paths and metadata are deliberately not
            # projected. Recognize the user-media type against its provenance
            # tag so a tool/result block cannot be mistaken for an upload.
            attachment_kind = {
                "input_image": "user.image", "input_file": "user.file",
                "input_audio": "user.audio", "input_video": "user.video",
            }.get(block["type"])
            if attachment_kind is None or attachment_kind not in kinds:
                return None
            if block["type"] == "input_image":
                keys = set(block)
                if keys not in ({"type", "image_url"}, {"type", "image_url", "detail"},
                                {"type", "data"}):
                    return None
                image_value = block.get("image_url", block.get("data"))
                if not isinstance(image_value, str):
                    return None
                if "detail" in block:
                    detail = block["detail"]
                    if not isinstance(detail, str) or detail not in {"auto", "low", "high", "original"}:
                        return None
            elif len(block) > 16 or any(not isinstance(key, str) or len(key) > 64 for key in block):
                return None
    # Validate metadata/scalars with the established classifier using a safe
    # synthetic text-only shape, not by changing the record retained as original.
    safe = dict(record, payload=dict(payload))
    safe["payload"]["content"] = [{"type": "input_text", "text": text} for text in (texts or [''])]
    safe["payload"]["internal_chat_message_metadata_passthrough"] = dict(meta, content_item_kinds=["user.text"])
    if classify(safe, 1, set(), set()) is not None:
        return None
    gaps = omitted + ["original_mixed_record_not_retained"]
    if not texts:
        gaps.append("attachment_only_prompt_no_text")
    return {"text": "\n".join(texts), "text_blocks": texts,
            "attachment_gaps": sorted(set(gaps)),
            "attachment_kinds": sorted(set(kinds) & USER_ATTACHMENTS)}


def _tool_image_count(body):
    """Recognize inspected mixed tool images for metadata only, never capture.

    URLs, captions and encoded image bytes are deliberately not returned. The
    native capture classifier continues to reject these full mixed originals;
    selected media require their own explicit safe artifact capture.
    """
    if not isinstance(body, list) or not body:
        return None
    count = 0
    for block in body:
        if not isinstance(block, dict) or not isinstance(block.get('type'), str):
            return None
        if block.get('type') in {'text', 'input_text', 'output_text'}:
            if set(block) != {'type', 'text'} or not isinstance(block['text'], str):
                return None
        elif block.get('type') == 'input_image':
            if (not {'type', 'image_url'} <= set(block)
                    or set(block) - {'type', 'image_url', 'detail'}
                    or not isinstance(block['image_url'], str)
                    or not re.fullmatch(r'data:image/(?:png|jpeg|webp);base64,[A-Za-z0-9+/=]+', block['image_url'])
                    or ('detail' in block and (not isinstance(block['detail'], str)
                                              or block['detail'] not in {'auto', 'low', 'high', 'original'}))):
                return None
            count += 1
        else:
            return None
    return count or None


def project_record(record: dict, line: int, session_id: str,
                   current_turn: str | None, current_model: dict) -> dict:
    """Return {kind, payload, next_turn, next_model} without hidden envelopes.

    All payloads have source_line/session_id and, when valid, source_timestamp.
    Text payloads have role, phase, text, text_blocks, turn_id, observed_model,
    retain_original and attachment_gaps. The caller owns raw-byte hashing and
    persistence. A ``gap`` is unsupported/lost accessible data; an ``excluded``
    is an intentional hidden/non-authoring surface. Tool digests use canonical
    JSON and are only metadata; review must bind exact original-byte hashes.
    """
    if type(line) is not int or line < 1 or not _identifier(session_id):
        raise ValueError("invalid projection source identity")
    if current_turn is not None and (not isinstance(current_turn, str) or not current_turn or len(current_turn) > 200):
        raise ValueError("invalid persisted current turn")
    next_turn = current_turn
    next_model = _safe_model(current_model)
    base = {"session_id": session_id, "source_line": line}
    if isinstance(record, dict) and valid_timestamp(record.get("timestamp")):
        base["source_timestamp"] = record["timestamp"]

    def result(kind, **values):
        return {"kind": kind, "payload": dict(base, **values),
                "next_turn": next_turn, "next_model": copy.deepcopy(next_model)}

    if (not isinstance(record, dict) or not set(record) <= TOP_KEYS
            or not valid_timestamp(record.get("timestamp"))
            or ("ordinal" in record and type(record["ordinal"]) is not int)):
        return result("gap", reason="unknown_record_metadata_or_shape")
    payload = record.get("payload")
    if not isinstance(payload, dict):
        return result("gap", reason="unknown_payload_shape")
    typ = record.get("type")
    subtype = payload.get("type")
    if not isinstance(typ, str) or (subtype is not None and not isinstance(subtype, str)):
        return result("gap", reason="unknown_record_type_shape")

    if typ == "turn_context":
        turn = payload.get("turn_id")
        if turn is not None and (not isinstance(turn, str) or not turn or len(turn) > 200):
            return result("gap", reason="invalid_turn_context_id")
        if turn:
            next_turn = turn
        next_model = observed_model(payload, line)
        return result("model", turn_id=next_turn, observed_model=copy.deepcopy(next_model))
    if typ == "event_msg":
        if subtype in {"task_started", "task_complete", "turn_aborted"}:
            turn = payload.get("turn_id", current_turn)
            if not isinstance(turn, str) or not turn or len(turn) > 200:
                return result("gap", reason="invalid_lifecycle_turn_id")
            values = {"event_type": subtype, "turn_id": turn}
            for key in ("duration_ms", "time_to_first_token_ms"):
                if key in payload:
                    if not _milliseconds(payload[key]):
                        return result("gap", reason="invalid_lifecycle_" + ("duration" if key == "duration_ms" else "first_token_time"))
                    values[key] = payload[key]
            if "time_to_first_token_ms" in values:
                values["time_to_first_token_source"] = "native-task-lifecycle-reported-metric"
                values["time_to_first_token_boundary"] = "Reported local metric; token surface and hidden thinking duration unverified"
            for key in ("started_at", "completed_at"):
                if key in payload:
                    observation = _lifecycle_time(payload[key])
                    if observation is None:
                        return result("gap", reason="invalid_lifecycle_timestamp")
                    values[key] = observation["normalized_utc"]
                    values.setdefault("lifecycle_time_observations", {})[key] = observation
            if isinstance(payload.get("reason"), str) and payload["reason"] in {"interrupted", "cancelled", "canceled", "error"}:
                values["reason"] = payload["reason"]
            if subtype == "task_started":
                next_turn = turn
                next_model = copy.deepcopy(UNKNOWN_MODEL)
            elif current_turn is None or current_turn == turn:
                next_turn = None
            return result("lifecycle", **values)
        if subtype in EXCLUDED_EVENTS:
            return result("excluded", reason="noncanonical_or_hidden_event:" + subtype)
        return result("gap", reason="unknown_event_message_type")
    if typ == "session_meta":
        fields = {}
        for key in ("agent_nickname", "agent_role", "agent_path"):
            value = _scalar(payload.get(key))
            if value is not None:
                fields[key] = value
        source = payload.get("source")
        if isinstance(source, dict):
            agent = source.get("subagent")
            spawn = agent.get("thread_spawn") if isinstance(agent, dict) else None
            if isinstance(spawn, dict):
                parent = _identifier(spawn.get("parent_thread_id"))
                if parent:
                    fields["parent_session_id"] = parent
                for key in ("agent_nickname", "agent_role", "agent_path"):
                    value = _scalar(spawn.get(key))
                    if value is not None:
                        fields[key] = value
        return result("agent_metadata", **fields)
    if typ in {"world_state", "token_usage_record", "compacted", "inter_agent_communication_metadata"}:
        return result("excluded", reason="nonvisible_envelope:" + typ)

    reason = classify(record, line, set(), set())
    if typ == "response_item" and subtype == "message":
        role = payload.get("role")
        turn = payload.get("internal_chat_message_metadata_passthrough", {})
        turn = turn.get("turn_id", current_turn) if isinstance(turn, dict) else current_turn
        if turn is not None and (not isinstance(turn, str) or not turn or len(turn) > 200):
            return result("gap", reason="invalid_message_turn_id")
        if reason is None:
            blocks = [block["text"] for block in payload["content"]]
            return result("text", role=role, phase=payload.get("phase", payload.get("channel")),
                          text="\n".join(blocks), text_blocks=blocks, turn_id=turn,
                          observed_model=copy.deepcopy(next_model), retain_original=True,
                          attachment_gaps=[])
        mixed = _mixed_user_projection(record)
        if mixed is not None:
            return result("text", role="user", phase=None, turn_id=turn,
                          observed_model=copy.deepcopy(next_model), retain_original=False, **mixed)
        if role == "user" and reason == "excluded:non_user_text_context":
            meta = payload.get("internal_chat_message_metadata_passthrough", {})
            kinds = meta.get("content_item_kinds") if isinstance(meta, dict) else None
            if (not isinstance(kinds, list) or not kinds
                    or any(isinstance(k, str) and k.startswith("user.") for k in kinds)):
                return result("gap", reason="user_prompt_content_or_origin_unsupported", turn_id=turn,
                              surface="user_prompts_and_attachments")
    if typ == "response_item" and subtype in CALL_TYPES | OUTPUT_TYPES:
        image_count = (_tool_image_count(payload.get('output'))
                       if subtype in OUTPUT_TYPES and reason == 'unknown_tool_output_shape' else None)
        if reason == "withheld:tool_body_not_reviewed" or image_count is not None:
            canonical = json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode()
            values = {"record_type": subtype, "call_id": payload.get("call_id"),
                      "canonical_record_sha256": hashlib.sha256(canonical).hexdigest(),
                      "turn_id": current_turn, "review_status": "PENDING"}
            if image_count is not None:
                values.update(image_count=image_count, body_capture_policy='SEPARATE_MEDIA_REVIEW_REQUIRED')
            heartbeat = automation_heartbeat(payload)
            if heartbeat:
                values.update(heartbeat)
                values["turn_id"] = payload.get("internal_chat_message_metadata_passthrough", {}).get("turn_id", current_turn)
            for key in ("name", "namespace", "status"):
                if isinstance(payload.get(key), str):
                    values[key] = payload[key]
            return result("tool_pending", **values)
    if reason and reason.startswith("excluded:"):
        return result("excluded", reason=reason)
    return result("gap", reason=reason or "unsupported_record_projection",
                  surface="tools" if typ == "response_item" and subtype in CALL_TYPES | OUTPUT_TYPES else "text_or_unknown")
