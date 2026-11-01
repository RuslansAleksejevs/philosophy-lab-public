"""Proposed repository/tools/quote_sources.py; not installed in the repository.

Load additional quote sources while keeping q01-q61 on their original log route.
The caller keeps all existing role, message-hash, excerpt and date assertions.
Visible fragments prove retained text consistency, not full native-log capture.
"""
from pathlib import Path, PurePosixPath
import hashlib
import json


LEGACY_QUOTE_IDS = frozenset(f"q{n:02}" for n in range(1, 62))


def _sha(raw):
    return hashlib.sha256(raw).hexdigest()


def _path(root, name):
    logical = PurePosixPath(name)
    assert name and not logical.is_absolute() and ".." not in logical.parts
    p = Path(root) / str(logical)
    assert p.resolve().is_relative_to(Path(root).resolve()) and p.is_file()
    assert not p.is_symlink()
    return p


def _checked(root, name, expected_hash):
    raw = _path(root, name).read_bytes()
    assert _sha(raw) == expected_hash, (name, "quote source file changed")
    return raw


def load_quote_message(root, quote):
    """Return the single verified source message in the existing verifier shape."""
    root = Path(root)
    extra = quote.get("source_record")
    if quote["id"] in LEGACY_QUOTE_IDS:
        assert extra is None, "historical quote source cannot be redirected"
    if extra is None:
        # The original lookup route remains unchanged for every historical quote.
        doc = json.loads((root / "logs/codex/chats" / quote["session_id"] / "conversation.json").read_text())
        return next(m for m in doc["messages"] if m["source_line"] == quote["source_line"])

    if extra["kind"] == "conversation_snapshot":
        raw = _checked(root, extra["path"], extra["sha256"])
        doc = json.loads(raw)
        sid = doc.get("session_id") or doc.get("session", {}).get("session_id")
        assert sid == quote["session_id"]
        matches = [m for m in doc["messages"] if m["source_line"] == quote["source_line"]]
        assert len(matches) == 1, "quote source line must be unique"
        message = matches[0]
        assert message["role"] == "user"
        assert message.get("session_id", sid) == sid
        assert message["raw_sha256"] == extra["source_line_sha256"]
        assert _sha(message["text"].encode()) == message["text_sha256"]
        return message

    assert extra["kind"] == "visible_fragments", "unsupported quote source kind"
    raw = _checked(root, extra["manifest_path"], extra["manifest_sha256"])
    manifest = json.loads(raw)
    assert manifest["format"] == "quote-visible-fragments.v1"
    assert manifest["status"] == "EXACT_VISIBLE_JSON_STRING_FRAGMENTS"
    assert manifest["full_provider_capture"] is False
    matches = [r for r in manifest["records"] if r["id"] == extra["record_id"]]
    assert len(matches) == 1, "quote fragment record must be unique"
    record = matches[0]
    assert record["session_id"] == manifest["session_id"] == quote["session_id"]
    assert record["source_line"] == quote["source_line"] and record["role"] == "user"
    assert record["source_line_sha256"] == extra["source_line_sha256"]
    assert record["source_timestamp"]
    base = PurePosixPath(extra["manifest_path"]).parent
    chunks = []
    assert record["parts"], "empty fragment list"
    for part in record["parts"]:
        logical = PurePosixPath(part["path"])
        assert not logical.is_absolute() and ".." not in logical.parts
        token = _checked(root, str(base / logical), part["sha256"])
        assert len(token) == part["bytes"]
        text = json.loads(token)
        assert isinstance(text, str)
        chunks.append(text)
    text = "".join(chunks)
    assert _sha(text.encode()) == record["text_sha256"]
    return {"session_id": record["session_id"], "source_line": record["source_line"],
            "role": record["role"], "text": text, "text_sha256": record["text_sha256"],
            "source_timestamp": record["source_timestamp"], "raw_sha256": record["source_line_sha256"],
            "source_boundary": "Exact retained visible string fragments; full native envelope not exported."}
