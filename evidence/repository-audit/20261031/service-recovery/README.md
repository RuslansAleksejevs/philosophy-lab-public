# Collector service recovery

The second, separately recorded recovery attempt passed all 14 checks on
2026-11-01T00:18:48.433652+00:00. PID 43236 completed a normal poll under the
exact source signature in CONTRACT.json. Its snapshot ends at canonical event
728142; all 21 required sessions were caught up.

The earlier attempt, PID 40522, was stopped after a measured performance
problem: rebuilding two whole-archive indexes for each source. Its 167 current
cursors and canonical events through 601238 were preserved. The reviewed
two-index correction passed 706 full-project tests. Audit, fsync, source and
privacy rules stayed in place; no signature compatibility was added. The
second normal start therefore performed ordinary replay under the new code.

This proves one observed completed poll, not complete provider-log export.
The proof retains 1166 source gaps, 1 view gaps,
and 90704 pending tool records. These are distinct from
source read errors (zero); pending tools are not automatically lost text.
Historical gaps were not cleared by the service-health result.

Prior start/stop receipts and the bounded [timing evidence](timing/FINDINGS_RU.md)
preserve both attempts. The [performance repair](../performance-repair/MANIFEST.json)
binds reviewed code, installation and full checks. Raw runtime caches, status
inventories, native bodies and scientific response bodies are not copied here.
The service was left running; no second completed poll was required.
