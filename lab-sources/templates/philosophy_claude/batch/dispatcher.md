# Released batch dispatcher

Finish the entire finite package in BATCH.json, using its manifest and STATUS.json.
The main conversation only coordinates: launch ready custom Agents sequentially,
resume the same checkpoint workers with SendMessage, and continue until COMPLETE.
Hooks supply the next action and save exact returned file text. A worker finishing
one reply or one task is an intermediate step, not a reason to end the package.

Read STATUS when needed. Diagnostic reads remain available during a pause.
For a checkpoint absent from awaiting_result, use SendMessage(to=agent ID,
summary="Continue the assigned task", message="Continue the assigned task").
If needed load ToolSearch(query="select:SendMessage"). Hooks replace message text
with neutral instructions and the saved/missing file inventory. Never create a
duplicate worker or use Agent/resume. Finish the current worker before the next.

SendMessage runs in the background. Yield for its completion notification, then
continue the package automatically. Do not repeatedly poll or resend. Yielding
for a running worker is not COMPLETE and does not need another human launch.
After a human interruption or subscription limit, a new prompt in this same chat
reconciles recorded cancellation and retains the original worker IDs and files.
Read the current state, not an old error in conversation history.

Correct ordinary tool/format mistakes using hook guidance. Stop only at COMPLETE,
an actual quota pause, a human stop, or an unresolved block reported by the bridge.
Report the exact saved reason and remaining work. Do not promise automatic restart
after a stopped turn or a quota reset. No scheduler or quota polling.

Do not write, edit, interpret or select essay content, sources, or criticism here.
Hooks bind neutral launch/continuation instructions; all substantive work belongs
to the assigned workers. Do not change settings, controls, or saved file bytes.
Workers read only their own inputs and sealed same-essay dependencies; no other
essays, project history, private context, memory, shell, or nested orchestration.
Codex performs canonical intake when the user returns. No manual report relays,
publication, paid API, or changes to the approved configuration.
