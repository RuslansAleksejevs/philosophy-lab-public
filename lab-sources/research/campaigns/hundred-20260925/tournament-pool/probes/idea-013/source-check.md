# Source packet checks: idea-013 / sources-001

- `source-note.md`, `source-manifest.json`, `search-log.json`, and this file are present and nonempty.
- The manifest is a JSON array. Each `excerpt` entry points to a file under this probe’s `sources/` directory and includes a SHA-256 digest of that saved excerpt file.
- Four primary-source records are included. Three have bounded source text available; Parfit 1984 is explicitly limited to a search-indexed excerpt. No downloaded full PDF is represented as locally captured.
- Exact search queries are retained in `search-log.json`. Exact printed pages/sections read or surfaced are listed there, with “metadata,” “excerpt,” and “unavailable” kept distinct.
- Search failures and restrictions are preserved: Sen/Harvard HTTP 405, direct curl DNS failure, Lisbon CAS redirect, Sen 1993 JSTOR restriction, Google Books no page preview, and restricted full text for Parfit’s 1984 book.
- The source note records the collector coverage gap reported by the coordinating root: this session is CAUGHT_UP, `text_coverage=GAPS`, and `tools_coverage=UNSUPPORTED_SCHEMA`. A complete native text/tool trace is not established.
- Requested model/effort is recorded as gpt-6-luna / xhigh. The native configuration is unverified in this context; the session UUID does not prove model or effort.
- This packet does not make an originality, novelty, comprehensive literature, argument-validity, model-comparison, or essay-completion claim. No argumentative probe, formal model, manuscript, or checkpoint is included.
