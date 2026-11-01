"""Use the same checked visible sources for newly added timeline decisions."""
import json
from pathlib import Path
from quote_sources import load_quote_message


def load_timeline_message(root, event):
    source = event["source"]
    if "source_record" not in source:
        # Exact historical lookup; existing role/hash/time assertions stay outside.
        doc = json.loads((Path(root) / "logs/codex/chats" / source["session_id"] / "conversation.json").read_text())
        return next(m for m in doc["messages"] if m["source_line"] == source["source_line"])
    return load_quote_message(root, {"id": "timeline-" + event["id"],
                                    "session_id": source["session_id"],
                                    "source_line": source["source_line"],
                                    "source_record": source["source_record"]})
