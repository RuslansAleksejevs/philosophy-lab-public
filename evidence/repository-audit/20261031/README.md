# Conversation recovery and research history

The October 31 audit compared the previous GitHub edition with available native conversation sources, canonical visible records, Claude collection manifests, and later acceptance files. It found real omissions; a successful earlier upload had not meant that all later conversations were included. The final retained union now contains **15,302 messages across 3,407 indexed sessions**, preserving all 14,939 morning messages and adding 363 source identities, including eight labelled inherited copies.

- [Final visible-log supplement](../../../logs/updates/20261031-final-verification/MANIFEST.json): 20 accepted scientific results, the coordinator closure and 386 accepted public web fragments. Its [source cutoffs](../../../logs/updates/20261031-final-verification/native-source-cutoffs.json) were fixed during November 1 00:25:07–00:25:28 UTC, still October 31 in Los Angeles. All 3,378 scoped non-internal native sources were available; 324 internal-runtime sources were not opened.
- [Recovered conversations and reviewed tool fragments](../../../logs/updates/20261031-complete-visible/README.md): 1,059 newly retained messages, with all 13,880 earlier message objects preserved.
- [Later receipts and transport records](../../../logs/updates/20261031-late-receipts/README.md): 582 additional exact files.
- [Milestone sources](history/milestones.json): the documented beginning on September 7 and later turning points, using source dates instead of repository-import dates.
- [Competition recheck at 23:14 UTC](COMPETITION_RECHECK_2314Z.json): the same 23 named judges, the three-essay/6,000-word limits, anonymity and methodology requirements, and the October 31 23:59 AoE deadline remain stated on the official pages.
- [Authorship evidence](history/authorship.json): Codex, Claude, mixed lineages, and the distinction between AI prose and retained quotations.
- [Old local branch check](history/git-history.json): all 131 files from the separate preparation commit already survive in the existing main history.
- [Morning native-format gaps](gap-review/README.md): all 430 classified, with no additional unique visible text found within that set. The final supplement includes the eight missing inherited session/line identities as labelled copies.
- [Tool-log coverage](tool-coverage/README.md): all 37 bundles present in that morning audit checked; 1,938 exact tool identities confirmed, with remaining coverage uncertainty and exclusions stated separately.
- [Additional tool comparison](tool-coverage-followup/README.md): 15,456 records in 81 frozen source prefixes were compared by call identity and exact content. No further unambiguous match was established; repeated two-byte content is not counted as recovered logs.
- [Parser repair](parser-repair/README.md): the narrow current-message-format fix and its checks.
- [Completed collector recovery](service-recovery/README.md): the normal pass completed all 14 operational checks, including all 21 required sessions; its separate snapshot retains 1,166 gaps, 90,704 pending tool records and one view gap.
- [Collector scaling repair](performance-repair/README.md): two repeated index rebuilds were removed; archive validation, durable writes and capture rules remain unchanged. Installed code passed the full project checks; live recovery has a separate receipt. A [matched-source timing sample](PERFORMANCE_COMPARISON.json) found a median interval of 0.390 seconds versus 7.708 seconds for the same 30 source prefixes; this is not a controlled benchmark or the duration of a full collector pass.

[HISTORICAL_VIEW.json](HISTORICAL_VIEW.json) binds the earlier bytes of every replaced file. Original essay versions, earlier evidence packages, prior bundles, and disagreements remain available. Git history has not been reconstructed or backdated.

The [conversation guide](../../../logs/README.md) distinguishes the final export's **1,210 gap entries and 89,972 generic pending tool records** from the earlier service snapshot. Different scopes and cutoffs explain the separate counts; neither generic tool count is a total of lost records. The global bundle manifest now lists 37 files; one separate late bundle and two final supplemental bundles make 40 unique bundle files. The morning 37-bundle audit remains unchanged historical evidence.

Accepted scientific responses and visible conversation text retain exact bytes. Approved signed AWS URLs are omitted only from public web-output copies; the final supplement binds their policy, original source hashes and omission ledger. This mechanical projection is not a new review or a complete provider trace.

Run `python3 -B tools/verify_rebuilt_edition.py --require-final-delta --final-manifest-sha256 06d4104af94acdd6093b33ff76328874febec631f93d7f50aed8f726fa95f9b2` from the repository root to verify the retained earlier edition, final union, repair snapshots, and current local links.
