# Preserved output for this exact job

Write bounded regular files only under output/. Never use links or overwrite
an earlier artifact. Number drafts, critiques, responses, revisions and progress
files separately. Required final files are listed in manifest.json; report.md
is always required for a completed job. Partial work is collectable without it.

Preserve the actual draft and criticisms, including rejected suggestions and
the author's reasons. Each source citation needs a public URL/bibliographic
identifier and an exact usable locator. A report must distinguish claims,
evidence, interpretation, originality uncertainty and remaining disagreement.

Optional metadata.json is an object with any of job_id, observed_model,
observed_effort, session_id, started_at, finished_at, response_wall_seconds,
status and limitations. Use UNKNOWN when unavailable. This sidecar is a
provider/agent report, not trusted native telemetry. An invalid sidecar will be
preserved without being treated as metadata. No credentials or hidden thoughts.

Saving files does not establish complete conversation coverage. Codex imports
explicitly selected safe visible records separately and reports all omissions.
No returned artifact automatically counts as a completed philosophy round,
verified argument, eligible submission, or faithful simulation of a judge.

## Length and handoff

Never certify a manuscript's length from tokens, line counts or sampled paragraphs.
Use an available exact local word counter and state its boundary and method.
If none is available, save the manuscript once, state LENGTH_CHECK_REQUIRED in
the report and stop for Codex's deterministic count. Do not spend repeated full
rewrites guessing whether it fits. This is a technical check, not a request for
human philosophical input. Preserve each later correction as a new numbered file.

End with the exact job ID, role/stage and reason for stopping (completed,
length check, source archive, interruption, or other blocker). File creation,
canonical archival acceptance and publication permission are different states.
