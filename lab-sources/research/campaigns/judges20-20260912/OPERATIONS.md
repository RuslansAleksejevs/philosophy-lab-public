# Evidence and stage operations

Only read this neutral file, AUTHOR_BRIEF.md, your own task and your own essay
folder. Assigned judge profiles are supplied only to the corresponding critic.
Do not inspect the campaign index to learn other essays' content.

The coordinator supplies your exact agent path and essay number. Authors initialize before research:
`python3 -B scripts/judges20_artifacts.py init --essay NN --agent-path /root/author_NN`
For an existing author session, inspect your own identity.json instead of
starting again after a configuration change. This helper serializes starts.
Reviewers do not initialize: use the essay's existing round and your own actual
reviewer session in the relevant record/review/sources-extra command.

For each stage, write its artifact once, compute SHA-256, then emit exactly one
visible commentary message `[JUDGES20:NN:STAGE sha256=DIGEST]`. The marker is an
authorship attestation to exact bytes, not hidden reasoning. Then run:

`python3 -B scripts/judges20_artifacts.py record --essay NN --agent-path PATH --stage STAGE --file research/campaigns/judges20-20260912/essay-NN/FILE`

Required ordered stages:
1. question.md: chosen question and initial contribution plan, rejected angles.
2. sources.md: precise reading record and research limitations. Save actual
   source text/files used under sources/ and list each in source-manifest.json.
   Record with a nonempty `--source-note` describing actual retrieval coverage.
3. draft.md: complete first essay. Record as contribution, then stop and report.
4. critique.md: first critic's named-judge review, recorded by that critic.
   The second critic writes review-2.md, emits marker stage `review2`, then calls:
   `python3 -B scripts/judges20_artifacts.py review --essay NN --agent-path /root/reviewer2_NN --file research/campaigns/judges20-20260912/essay-NN/review-2.md --profile PROFILE_PATH`
5. decision.md: author answers both critics and records defended changes,
   disagreement, limitations and reopen triggers. final.md is separate, with its
   own `[JUDGES20:NN:final sha256=DIGEST]` marker. Record decision with
   `--final-file research/campaigns/judges20-20260912/essay-NN/final.md`.

All written source files are archived at the sources boundary. A new source
read during review/revision needs a new exact source-manifest entry and the
`sources-extra` command before dependent work. Manifest format is a JSON list
of objects with path (own essay relative path), url, title, accessed_at, read_status
(full|excerpt|metadata|unavailable), and locators. Only existing actually saved
files may have a path; unavailable items omit it. Never copy hidden reasoning.

For sources-extra, first compute the exact manifest SHA-256 and emit one visible
commentary marker `[JUDGES20:NN:sources_extra sha256=DIGEST]`. Then run:
`python3 -B scripts/judges20_artifacts.py sources-extra --essay NN --agent-path PATH --manifest research/campaigns/judges20-20260912/essay-NN/OWN_MANIFEST.json`
Wait for the successful source_event_id before dependent review/revision. A
retry of unchanged bytes reuses the existing marker; do not emit it twice.

Write author-notes.json after the final containing title, one-sentence thesis,
contribution, strongest objection, originality_limitations, open_questions,
sources, and style. Write HISTORY.md recording versions, roles and evidence
receipts without invented metadata. Save rejected drafts separately.

Write checkpoint.json with nonempty question, outcome (CONTINUE, REVISE or
SET_ASIDE), contribution, criticism, limitations, next_step, method_change,
comparability, coverage_boundary. Then:
`python3 -B scripts/judges20_artifacts.py checkpoint --essay NN --agent-path /root/author_NN --summary research/campaigns/judges20-20260912/essay-NN/checkpoint.json`

The helper captures exact visible markers and binds originals to this run; the
automatic collector separately retains recognized visible conversation text and
metadata. Tool bodies need explicit safe review. Neither mechanism promises a
complete provider trace. Derived views are rebuilt only by the coordinator.
