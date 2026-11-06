# Claude Code terminal workflow

Default since the explicit user migration request on 2026-09-24. Codex prepares,
reviews, launches, resumes and collects a finite Claude CLI session. The user
never needs to open a separate Claude chat, move reports or maintain a folder
exchange. Output files are still necessary evidence; their presence is not the
old manual transport workflow. Installation makes no model call.

## Existing sessions and implementations

An existing authorized CLI session continues with its original recorded runner,
config and session ID. Do not overwrite bound scripts, active pointers, packets,
release reviews, partial files or native histories. Existing working CLI adapters
remain usable. Use the portable runner below for a new lab or when only the old
manual adapter was installed. Do not silently fall back to the manual bridge.
Legacy manual collection/recovery remains available for old returns only; never
relaunch an old manual job as if it were the same CLI session.

## New finite round

1. Agree on one exact task and necessary context. Author a local request from
   `templates/claude_terminal/request.json`. Fix explicit model/effort, required
   output names and selected files. The template is not authorization. One session
   is the default; additional sessions require a concrete research rationale.
2. Use a new private packet strictly below `/Users/Shared/math-research-cli/`
   and a neutral per-lab ID. Do not expose personal home paths, full laboratories,
   conversations, settings or native session histories. Review PDF/binary contents
   and source provenance separately; text screening is not anonymization.
3. Prepare locally:
   `python3 scripts/claude_terminal/claude_runner.py prepare REQUEST PACKET --research-draft`.
   Record exact target, inputs, hashes and privacy review in this laboratory.
4. On the user's instruction to run this agreed task, check CLI `preflight()` on
   the host, using the runner's sanitized environment. This checks flags and an
   existing first-party subscription; retain only sanitized observations.
   A sandbox login failure is not evidence that the user must log in again.
   Never use API keys, paid-overage activation or automatic model fallback.
5. Make an exact-byte local release review. `files` contains input_hashes,
   support_hashes, manifest.json SHA-256 and runner.py SHA-256. Record actual
   privacy_reviewed, reviewer, notes, live_test_approved, approval_source,
   subscription_auth_verified; research additionally requires research_approved,
   technical_acceptance, rules_checked and archive_approval_event. These attest
   completed checks and the existing user request, not a second approval ritual.
   Release with `python3 scripts/claude_terminal/claude_runner.py release PACKET REVIEW`.
6. Create a new local `runs/<round-id>/` record directory; write
   `runs/claude-terminal-active.json` with `packet` (absolute neutral path) and
   `record_directory` (lab-relative runs path). Never replace an active session
   without checking its completion/stop state and preserving the earlier pointer.
7. Start with `python3 scripts/claude_terminal/claude_cli_launch.py`.
   Check `--status` to confirm the real session and requested/observed model.
   No automatic background quota checking. Launching one finite process is not
   authorization to schedule further rounds.

## Interruption and collection

A quota/provider interruption preserves the exact session and partial files.
Resume only on user request using the same launch command; never create another
session to evade a quota. Explicit stop: `claude_runner.py stop PACKET`.
A later user resume permits `claude_cli_launch.py --resume-stopped`; never clear
STOP.json by hand. Uncertain launch or duplicate process requires inspection.

After the runner exits, collect with
`python3 scripts/claude_terminal/claude_runner.py collect PACKET NEW_LOCAL_QUARANTINE`.
This copies selected visible output, sources, configuration observations and
versioned artifacts into an immutable hash-bound collection. Never execute
returned code during ordinary intake. Use the laboratory's existing intake and
checkpoint/archive protocol. In mathematical labs claims remain UNKNOWN and
UNVERIFIED_EXTERNAL_OUTPUT / MODEL_INFERENCE until independent verification;
in other labs preserve their own honest candidate/assessment vocabulary.
Preparation and mechanical acceptance are not proof, novelty or human review.

File tools and optional public WebSearch/WebFetch are exposed, without Bash,
agents, plugins or MCP. Proposed calculations require explicit execution support;
never invent a successful test. Public-source retrieval is separate from the
model's WebFetch summary; record unavailable sources honestly. Account identity
and native restricted mode are not a VM or anonymity guarantee. No credentials,
private reasoning or arbitrary native transcript scans enter collected evidence.

For mathematical `research_checks: true`, source-status.json must have a nonempty
`sources` list with url, coverage (full/excerpt/summary/unavailable), note, and an
existing stage-relative artifact for full/excerpt. Do not force this mathematical
source contract on unrelated work: choose the actual task's acceptance criteria.

## Communication

Every proposed next action explicitly names Codex or Claude. End each workflow
status/result with very short `Codex: ...` and `Claude: ...` lines. State "no run
needed now" when appropriate. Distinguish process elapsed time from active
model computation and unverified findings from accepted results.

## Tests

`make claude-terminal-test` runs synthetic offline tests. No real model calls,
subscription changes or live-session migration occur during installation/tests.
