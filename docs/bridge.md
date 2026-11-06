[Home](../README.md) · [Read](current-selection.md) · [Method](method.md) · [History](timeline.md) · [Archive](../logs/README.md)

# Building the Codex–Claude bridge

The bridge let Codex coordinate research and preserve its record while Claude wrote, criticized, or revised in separate assigned contexts. We wanted to use both subscriptions with little manual relaying. Getting a reply across was easy compared with keeping the right inputs, saved files, and completion status connected.

After several designs, a small runner launching fresh CLI sessions from file packets made that connection simpler. The history includes Claude-only, Codex-only, and mixed manuscript lineages.

**Key dates:** September 12 — persistent bridge accepted; September 20 — simple CLI runner and live smoke test; October 14 — separate Claude C2/C5 repair cycle closed. The [timeline](timeline.md) distinguishes requests, tests, and accepted outputs.

## Four designs, one recurring problem

| Stage | What we tried | What it taught us |
| --- | --- | --- |
| Manual packets | Separate folders and a human handoff | Every extra relay made coordination harder |
| Persistent entry point | A stable `CURRENT` pointer to the assigned packet | A prepared packet is not a running job; stale contexts need explicit handling |
| AI dispatcher | A parent delegated work to child agents | A child could not write the report that its completion hook required |
| Direct CLI queue | A small program launched fresh main sessions from file packets | Direct file output removed much of the fragile text relay |

The dispatcher restriction led us to introduce JSON transport. That brought truncated output, callbacks, partial delivery, and format variation. We had treated a restriction of that child-worker setup as a broader transport problem. The later runner used main sessions that could write files directly.

We also considered existing tools. Superset was installed after a misunderstanding and then rolled back; Sendbird was inspected but not installed. The simpler final design emerged from this history.

## Continue without duplicating completed work

The runner distinguished quota exhaustion, cancellation, error, unknown outcome, and successful completion. It retained session identity for continuation and skipped accepted work. When generation succeeded but import failed, recovery meant repairing the archive around the existing response.

Output faults such as excessive length, an empty file, or invalid JSON could receive up to three corrective continuations after the initial run. This allowance covered output repair only; quota exhaustion had a separate stopping path. Repairs remained in the history because even shortening a text could change its claim.

## Verify delivery and access

Small live tests exercised file inputs, delivery of the exact preceding-stage outputs, controlled interruption, and same-session resume. A separate test covered HTML and PDF access. The record distinguishes these live checks from local unit tests and replay of saved output.

Source access needed content checks as well as successful requests. A fetch could return a summary, an HTTP success could contain an error page, and an available image could remain unread. Each case required its own description of what reached the researcher.

The same principle applied to settings. Requested model, observed model, native reasoning effort, selected UI mode, and actual agent launches became separate observations. An `xhigh` setting alone could not identify “Ultracode.” One essay's change from Opus 5 to 5.5 remained visible in its history.

## A saved draft can miss its critic

In [Claude essay 09, now E021](../essays/E021/README.md), drafts 002 and 003 were saved, but the declared critic and editor inputs still used draft 001. The existence of a newer file had not changed the assigned dependency. Its history therefore records both the saved versions and the version delivered for review.

That is the bridge's methodological consequence: transport determines which manuscript and evidence a researcher works on. The record documents using both subscriptions and repairing their coordination; subscription-cost savings were not measured in a controlled comparison. The later [direct Claude branch](post-midterm.md#the-separate-claude-branch) continued this history with its own local capture and repair cycle.

**Evidence:** [Detailed method index](methodology-index.md#building-the-codexclaude-bridge), [source conversations](../logs/README.md), and [essay biographies](../essays/README.md). [Decision map →](decisions.md)
