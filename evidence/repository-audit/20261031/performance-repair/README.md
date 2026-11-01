# Removing repeated archive scans

The first normal recovery attempt exposed a scaling problem: even a small
source took about 6–8 seconds. Every batch rebuilt a delivery-key map and an
event-ID set over the whole archive. That attempt was stopped and retained;
it was not recorded as a completed successful poll.

The repair keeps those two indices in memory and updates them after accepted
changes. Full archive audits, event validation, failure poisoning, defensive
copies, canonical file/directory fsync and per-source cursor-cache persistence
remain in place. The capture rules and compatibility policy were not widened.
A new signature requires another ordinary native replay; earlier events and
raw records remain preserved.

The candidate passed 150 tests, including 10 new regression tests and 140 tests
also present in the project suite. The full project checks were then run against
the installed code. These counts overlap and must not be added as distinct tests.
The exact results and source hashes are in [MANIFEST.json](MANIFEST.json).

The code and test copies retain their original lab-relative dependencies; this
folder is an evidence snapshot, not a standalone installation. Earlier source
bytes are under `before/`, installed bytes under `current/`. The subsequent
[service recovery](../service-recovery/README.md) separately records the actual
normal start, completed poll, source gaps and observed performance. Code review
and synthetic tests alone do not establish a live speedup or complete log coverage.
