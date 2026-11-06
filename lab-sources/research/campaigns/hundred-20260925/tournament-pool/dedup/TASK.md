# Audit the sealed 120-idea tournament pool

Read ../DEDUP_TASK.md and the campaign FRESH_DISPATCH_V2.md. Your exact candidate
packet is candidate-inputs.json, ordered by numeric idea ID. It contains exact
individual file paths, hashes, projection event IDs, lineage IDs and candidate
event IDs. Do not inspect the generators' unrelated process files or other lab essays.

Initialize your fresh run with your actual native session, bind this task, the
duplicate criterion in ../DEDUP_TASK.md and candidate-inputs.json. Prepare kind
evaluation / phase evaluation with all 120 projection events as direct parents
and all exact individual idea files as inputs using from_event_id. Only after
preparation succeeds, read and compare all 120 actual proposals in fixed order.

To make coverage reviewable, give every idea a short question/thesis/mechanism
fingerprint in a JSON inventory, then save duplicate clusters, partial overlaps,
retained IDs and replacement slots with concrete textual reasons. Use semantic
comparison, not keyword overlap or exact-string matching. No quality ranking,
new argument, replacement idea or literature verification is assigned. Retain
all IDs when there is no demonstrated substantive duplication. Ambiguous cases
should be named rather than silently subtracted.

Record the actual evaluation with assessment.versions naming all 120 individual
lineage IDs and hashes, assessment.order their exact presentation order, the
prepared task and duplicate-criterion hashes, requested Astra/ultra and actually
observed settings if accessible. Save Russian HISTORY.md with the real coverage
and limitations. Emit the exact native marker once, then record and return the
receipt and report. This intermediate audit has no final essay/checkpoint; use
the existing validate(..., complete=False) API if you validate the run. Root will
commission any replacements and subsequent philosophical selection.
