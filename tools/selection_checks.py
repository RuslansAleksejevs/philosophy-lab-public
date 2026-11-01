"""Additional edition checks; historical checks remain in verify_edition.py."""
from pathlib import Path, PurePosixPath
import hashlib
import json

PREFIX = "evidence/final-selection/updates/20261018"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def file(root, name):
    p = PurePosixPath(name)
    assert name and not p.is_absolute() and ".." not in p.parts
    target = Path(root) / str(p)
    assert target.resolve().is_relative_to(Path(root).resolve()) and target.is_file()
    assert not target.is_symlink()
    return target


def checked(root, row):
    raw = file(root, row["path"]).read_bytes()
    assert sha(raw) == row["sha256"], row["path"]
    if "bytes" in row:
        assert len(raw) == row["bytes"], row["path"]
    return raw


def read(root, name):
    return json.loads(file(root, name).read_text())


def pointer(doc, ptr):
    assert ptr.startswith("/")
    for key in ptr[1:].split("/"):
        key = key.replace("~1", "/").replace("~0", "~")
        doc = doc[int(key)] if isinstance(doc, list) else doc[key]
    return doc


def verify_fragment_logs(root, name, final_bound):
    manifest = read(root, name)
    assert manifest["schema"] == "edition-exact-visible-fragments.v1"
    assert manifest["full_native_capture"] is False
    identities = set()
    for r in manifest["messages"]:
        identity = (r["session_id"], r["source_line"])
        assert identity not in identities
        identities.add(identity)
        assert r["role"] in {"user", "assistant"}
        if r["role"] == "assistant":
            assert r["phase"] in {"final", "final_answer"}
            assert r["origin"] == "AI_FINAL_RESPONSE"
        else:
            assert r["origin"] == "HUMAN"
            assert identity in {
                ("01a1496a-7b42-7a11-b00a-11d33df80222", 4828),
                ("01a1496a-7b42-7a11-b00a-11d33df80222", 4882),
            }
        text_parts = []
        assert r["parts"]
        for p in r["parts"]:
            text = json.loads(checked(root, p))
            assert isinstance(text, str)
            text_parts.append(text)
        text = "".join(text_parts)
        assert sha(text.encode()) == r["text_sha256"]
        assert file(root, r["text_path"]).read_text() == text
        proof = json.loads(checked(root, r["evidence_manifest"]))
        original = pointer(proof, r["evidence_record_pointer"])
        assert proof["session_id"] == r["session_id"]
        for key in ["source_line", "source_line_sha256", "role"]:
            assert original[key] == r[key]
        assert original.get("phase") == r.get("phase")
        assert original["decoded_text_sha256"] == r["text_sha256"]
        assert [(p["sha256"], p["bytes"]) for p in original["parts"]] == [(p["sha256"], p["bytes"]) for p in r["parts"]]
        if r["role"] == "assistant":
            acceptance = json.loads(checked(root, r["acceptance_receipt"]))
            assert final_bound[r["acceptance_receipt"]["source_path"]] == r["acceptance_receipt"]["sha256"]
            assert acceptance["status"] == r["acceptance_status"]
            assert acceptance.get("event_id")
            bound = {x["path"]: x["sha256"] for x in acceptance["files"]}
            assert bound[r["evidence_manifest"]["source_path"]] == r["evidence_manifest"]["sha256"]
        else:
            authorization = json.loads(checked(root, r["authorization"]))
            for proof in [r["evidence_manifest"], r["authorization"]]:
                assert final_bound[proof["source_path"]] == proof["sha256"]
            item = pointer(authorization, r["authorization_pointer"])
            assert authorization["session_id"] == r["session_id"]
            assert item["role"] == "user" and item["text"] == text
            assert item["source_line"] == r["source_line"]
            assert item["source_line_sha256"] == r["source_line_sha256"]
            assert item["timestamp"] == r["source_timestamp"]
    return len(identities)


def verify_selection_update(root):
    root = Path(root)
    contract = read(root, PREFIX + "/verification-contract.json")
    history = json.loads(checked(root, contract["historical_baseline"]))
    assert len(history["quotes"]) == 61 and len(history["timeline_events"]) == 42
    for name, key, previous in [("docs/quotes.json", "quotes", history["quotes"]),
                                ("docs/timeline.json", "events", history["timeline_events"])]:
        rows = read(root, name)[key]
        assert len({r["id"] for r in rows}) == len(rows)
        current = {r["id"]: r for r in rows}
        assert all(current.get(r["id"]) == r for r in previous), name
    receipt = json.loads(checked(root, contract["final_receipt"]))
    assert receipt["status"] == contract["accepted_status"]
    assert receipt["event_id"] == contract["accepted_event_id"]
    selection = json.loads(checked(root, contract["selection_manifest"]))
    selected = pointer(selection, contract["selected_ids_pointer"])
    manifest = read(root, PREFIX + "/manifest.json")
    assert selected == manifest["selected_ids"]
    assert len(selected) == len(set(selected)) and 1 <= len(selected) <= 10
    if len(selected) != 10:
        assert contract.get("accepted_shortfall_explanation")
    bound = {r["path"]: r["sha256"] for r in receipt["files"]}
    assert bound[contract["selection_manifest"]["source_path"]] == contract["selection_manifest"]["sha256"]
    decisions = contract["decisions"]
    assert bound[decisions["source_path"]] == decisions["sha256"]
    checked(root, decisions)
    versions = manifest["versions"]
    assert len(versions) == 22 and len({v["id"] for v in versions}) == 22
    by_id = {v["id"]: v for v in versions}
    assert set(selected) <= set(by_id)
    for v in versions:
        raw = file(root, v["repository_path"]).read_bytes()
        assert sha(raw) == v["sha256"] and len(raw) == v["bytes"]
        assert v["selected_for_reading"] == (v["id"] in selected)
    reading = manifest["reading"]
    assert len(reading) == len(selected)
    assert {r["candidate_id"] for r in reading} == set(selected)
    assert [r["number"] for r in reading] == list(range(1, len(reading) + 1))
    for r in reading:
        raw = checked(root, r)
        assert sha(raw) == by_id[r["candidate_id"]]["sha256"]
        assert bound[r["source_path"]] == r["sha256"]
    method = json.loads(checked(root, contract["method"]))
    assert bound[contract["method"]["source_path"]] == contract["method"]["sha256"]
    assert method["ratio"]["neutral"] == .6 and method["ratio"]["named_judge"] == .4
    assert method["ratio"]["per_manuscript"] == {"neutral": 3, "named_judge": 2}
    for item in manifest["imports"]:
        checked(root, item)
    fragments = verify_fragment_logs(root, contract["fragment_logs"], bound) if contract.get("fragment_logs") else 0
    return {"selection_candidates": 22, "reading_count": len(reading), "exact_fragment_messages": fragments,
            "old_quotes_preserved": 61, "old_timeline_events_preserved": 42}
