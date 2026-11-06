## User pause — 2026-09-20

Competition work is paused. The user has NOT sent the last continuation prompt.
All launch/resume instructions below are historical and inactive. Preserve seven
complete essays, the eighth author result and the eighth critic's partial work.
12/20 stages are sealed; stored IN_PROGRESS is not proof of a running process.
See docs/BRIDGE_REDESIGN_HANDOFF_2026-09-20_RU.md from the project root.
Bridge reconsideration comes first; competition needs explicit user resumption.

## Historical quota recovery handoff — 2026-09-15

Seven essays complete, eighth author complete: 12/20 sealed stages. The eighth
critic af243389a25ba1b17 stopped at a provider quota error; its partial record is
preserved. Quota/missing-result race repaired, original worker ready to resume.
Continue that critic with SendMessage, then revision 08 and full chains 09–10.
506 tests and real replay pass; live remainder not yet launched after this repair.
Evidence: runs/claude10-quota-race-repair-20260915/. Previous entries are historical.

## Format recovery handoff — 2026-09-15 05:40Z

Critic 07 completed; revision 07 returned a template plus real result together.
Six essays complete, ten stages sealed. Resume the same revision agent
(a0829183e1cca81cb) to resolve its own ambiguous delivery, then finish 08–10.
Original response and all previous files retained. No Codex content selection.
499 tests and real native replay pass. Installation: runs/claude10-ambiguous-repair-20260915/repair-receipt.json.
No new live launch after this repair yet. Earlier handoffs below are historical.

## Recovery handoff — 2026-09-15

Six complete essays; essay-07-author complete, essay-07-critic interrupted.
Nine of twenty stages sealed. Resume a1ac8a4f98486c922 with SendMessage, then
seventh revision and complete chains 08–10. No restarting finished tasks.
Repair installation is evidenced by runs/claude10-interruption-repair-20260915/repair-receipt.json.
496 local tests and the real cancellation replay pass; no new provider run yet.
One manual prompt in the existing Claude chat, then Codex intake on «готово».
Historical status entries below remain historical, not current instructions.

# Current handoff — Claude ten essays

Reviewed request and installation evidence: runs/claude10-packet-20260913/.
Research packet: claude10-20260913, 20 tasks for 10 independent essays.
01–05: author only. 06–10: author, fresh critic, fresh revision context.
All requested claude-opus-5 / xhigh. English, clear engaging natural prose.
No topics or philosophical sources assigned by Codex. No old series resumed.

The 86-file research packet is a passive copy under prepared-packets/claude10-20260913
in the permanent Claude folder. Its nested BATCH.json is a future activation file;
it is not the workspace pointer. Do not ask Claude to execute this staged copy.
Only batch-xhigh-probe-20260913 is to be active after probe-install.json exists.
User sends: Execute the active BATCH.json and stop at its final status.

After user returns: inspect the probe's local status and exact native child records;
collect and canonically archive the observed result. Verify check.txt is READY plus
newline and every observed child model/effort is claude-opus-5 / xhigh. Preserve
failure honestly. If verified, append the native evidence/configuration observation
and update the capability view with both previously verified low and new xhigh.
Never synthesize the missing child observation from parent xhigh.
Then close the probe and install the already reviewed research request/review with
claude_batch.install under the existing technical run. Recheck bytes and archive
coverage before handing off the one research launch prompt. No further settings
question is required. Do not regenerate or change the reviewed packet silently.

On research completion or interruption, collect the complete visible bounded
journal, original source bytes and all output versions. Assemble each essay's
HISTORY.md and configuration observations from actual evidence; never infer UI
mode or provider internals. Keep this Codex-only history out of worker inputs.
Technical acceptance is separate from philosophical evaluation. No substantive
Codex feedback into this lineage. No publication or paid API authorized.

## Successor status — 2026-09-13T20:09Z

The xhigh probe is COMPLETE 1/1, natively verified, canonically collected and CLOSED.
The research packet is now INSTALLED and ACTIVE, no provider launch performed.
All 86 installed files match the reviewed copy. research-install.json is the
installation receipt; probe-intake.json and xhigh-capability-receipt.json bind
verification. The earlier probe instructions above are completed history.
Next user launch is the research packet claude10-20260913. After user returns,
collect that packet, not the closed probe. All essay workers remain fresh even
when the technical dispatcher conversation is reused.

## Rate-limit interruption and recovery — 2026-09-13

Three generation-only essays are sealed and copied without changes into
essay-01/author through essay-03/author. Independently checked exact native
fragments, output bytes, model/effort and word counts; no content review.
Canonical interrupted intake: runs/claude10-recovery-20260913/intake-before.json.
Fourth native agent ab6ab88a2a319634f stopped on an explicit rate_limit service
record. All visible child tool calls have terminal results; no pending receipts
or saved manuscript. User's later continuation hit the bridge's saved halt.

Recovery records an explicitly Codex-created interruption checkpoint, not a
worker-authored JSON checkpoint. It permits SendMessage to the same native agent.
It does not fabricate a draft or restart the worker. The service error remains
in the original log; a narrow runtime correction records synthetic API errors
separately from actual model/effort observations. Bound runtime/manifest changes
are preserved by bridge.batch.repaired, with the original preparation and intake
as parents. Future collection resolves this explicit repair chain.

After recovered-status.json confirms success, the user may send in the SAME chat:
Continue the active BATCH.json. First resume essay-04-author from its saved
checkpoint with SendMessage, then complete all remaining tasks. Do not restart
completed tasks. Codex does not launch the provider itself.
Evidence and code: runs/claude10-recovery-20260913/. Original bound philosophical
instructions and all three final manuscripts remain unchanged. New runtime is
locally tested; live continuation after this rate limit remains to be observed.

## Fourth essay completed; fifth PDF-cache recovery — 2026-09-13

Same fourth agent resumed successfully and produced its final (4723 measured
word units). Exact native fragments/model/effort/output bytes verified and
originals copied to essay-04/author. First four generation-only essays complete.
Fifth agent a6b67a1d98e2b3b41 blocked on Read of a provider WebFetch PDF cache.
Its PDF is byte-identical to its assigned archived original. New reviewed runtime
routes only such verified aliases to the assigned original, preserving pages;
unassigned files remain denied. Sources, manifests and instructions are not
substantively changed. New repair event supersedes the prior bound repair.
See runs/claude10-pdf-recovery-20260913/ for intake, review and recovery receipts.
After recovered-status.json exists: ask the user to continue the SAME dispatcher,
first essay-05-author through SendMessage, then all remaining tasks. No new worker
for essay 05, no regeneration of completed essays. Live PDF alias read after this
patch remains pending; local tests cover owned and foreign PDF cases.

## Fifth manuscript transport checkpoint — 2026-09-14

The PDF alias recovery ran; essay 05 returned a complete manuscript and sources,
but its final process.md JSON string/envelope was incomplete. Original text is
preserved; no closing quotes/content invented. New runtime retains strictly decoded
complete file strings as a checkpoint and resumes only missing/new files. Exact
same fifth agent, four sealed essays unchanged. See
runs/claude10-text-recovery-20260914/recovered-status.json and intake-checkpoint.json.
Next manual prompt: continue essay-05-author through SendMessage, returning only
missing/new files, then run the remaining batch. Native output union keeps prior
file bytes and rejects changed versions under the same name. On next «готово»,
collect the same active packet with the three explicit repair events in its chain.

## User discussion pause — 2026-09-14T02:33Z

User explicitly states the latest Claude continuation prompt has NOT been sent.
Pause launch/continuation instructions while discussing the unsuccessful overall
one-launch workflow and researching existing orchestration products. No model
launch or automatic continuation. Four sealed essays plus the fifth manuscript
and sources at a transport checkpoint remain preserved. Do not confuse passing
component tests with successful end-to-end campaign operation.

## Superset cancelled; existing bridge planning — 2026-09-14

User clarified that acceptance did not mean migration to an extra application.
Superset installation and 33 app-created paths removed from active locations,
processes stopped; reversible backup outside research inputs. Receipt:
`runs/superset-rollback-20260914/receipt.json`. No bridge implementation changes
or Claude launches happened during the aborted setup. User requests a plan for
simplifying the existing bridge and using completion of this series as the live
acceptance run. Four sealed essays; fifth manuscript/sources saved, process report
incomplete; remaining five require author, critic, revision. Keep launch paused
while planning, preserve existing bound bytes and all native settings evidence.

## Existing bridge build authorized — 2026-09-14

User approved implementation, explicitly warned of the approaching five-hour
Claude subscription limit, and reserved packet preparation for a subsequent
request. Built opt-in gradual-v1 in the local compiler/runtime only. No active
campaign files, worker prompts, native sessions, model or UI settings changed.
WAITING_FOR_QUOTA preserves outputs and IDs without polling or scheduled spending;
explicit same-chat continuation requests recovery after reset. Unknown launch ID
still requires mechanical reconciliation to prevent a duplicate. See
`docs/CLAUDE_GRADUAL_RECOVERY.md` and `runs/claude-bridge-simplify-20260914/`.
Before activation: review exact successor controls/input bytes, record the repair
binding using the existing append-only chain, and preserve four sealed results plus
the fifth checkpoint. Do not prepare or launch the new packet before user request.

## Gradual packet installed — 2026-09-14

User explicitly requested packet preparation. Installed 19 changed files; 67
unchanged, including all started-task inputs and agent definitions/settings.
Unstarted task prompts replace repeat-all-files text with single-file checkpoints.
Official rules/FAQ rechecked and archived. Existing output hashes unchanged, same
parent and fifth agent. No provider launch. Current UI not observed; prior UI
evidence remains separate from native effort. Receipt/state:
runs/claude10-gradual-packet-20260914/. Next: same Claude chat, reread CLAUDE.md
and BATCH.json, continue. On ready, collect and verify through existing repair chain.

## Routine tool recovery installed — 2026-09-14

A Read of the fifth worker’s own absent process.md caused the bridge’s incorrect
global halt. The worker still returned the full file in its native final response.
Repair event event-75bb738443024760b60a02825d34bf02 supersedes the gradual packet
binding. Exact native recovery sealed essay-05-author without another provider call.
Five generation-only essays are now complete; remaining work is author, critic and
revision for essays 06–10 (15 stages). No previous output or started input changed.
Current UI observed Opus 5 / Ultracode; child native settings remain separately
verified. No model, effort, agent policy, privacy scope or source helper changed.

Correctable tool refusals now preserve the batch. Own missing-file reads are normal
failures with receipts; continuation includes saved/missing filenames. Wrong-scope
operations remain denied, finite recovery bounds remain, and quota pauses do not
become format failures. A local replay recovered the real response; 460 tests pass.
Live completion of the remaining work is still pending. Same-chat manual launch:
read current CLAUDE.md/BATCH.json/STATUS and continue the ready task essay-06-author.
Do not relaunch essays 01–05. See runs/claude10-tolerant-repair-20260914/.

## Capture recovery after sixth revision — 2026-09-14

The new run sealed essay-06-author and essay-06-critic. Quota wait was recorded
at 11:06:49Z; the human Try again at 18:37:19Z requested resume and the same
critic completed. The later revision halted on two Read EOF warnings mistaken
for hidden instructions. The recovery replay also exposed an intermediate JSON
example incorrectly treated as a delivered output. Both capture errors are fixed.
Exact real final-001.md recovered as the same revision worker’s checkpoint; no
provider call or substantive Codex rewrite. Its 7340-word count exceeds 6000;
the same Claude receives a neutral new-numbered-final correction instruction.
Five essays complete, sixth still in revision, four not started. 7 of 20 stages
sealed. Same-chat manual resume must continue essay-06-revision through SendMessage
(not start essay-06-author again), then all remaining tasks. 466 tests passed.
See runs/claude10-read-diagnostic-repair-20260914/ for exact reviews and receipts.

## Envelope recovery installed — 2026-09-14, after 23:19Z halt

Native source report lacked status. Files are now separated from optional metadata,
with absent worker claims and local derived transport status logged separately.
Selected_final alias accepted without editing its original record; resolved length
correction no longer repeats. Exact sources.md restored, final-002.md is 5862 words
excluding bibliography. Only process.md remains for the same sixth revision agent.
Then finish all stages for essays 07–10. Seven stages sealed, five essays complete.
Repair event event-ea1c7a0f8f834985867ee47138823fc4; evidence and current launch prompt
in runs/claude10-envelope-repair-20260914/. Worker inputs and settings unchanged.
478 local tests, including four full synthetic chains; live remainder still pending.
