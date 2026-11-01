# Archive maintenance — October 31, 2026

The [preparation supplement](../../final-selection/updates/20261031/README.md) restores the accepted evidence absent from the previous GitHub edition. It includes the 270 missing author/reviewer output files and twelve later completion records. Manuscripts, reviews and earlier acceptance decisions retain their exact original bytes.

The collector repair reads exact `.jsonl.zst` siblings, validates compressed frames, retains uncompressed record positions and verifies the previously committed byte prefix. It does not decompress unchanged sources on every poll. Unsupported formats, attachments and unreviewed tool bodies remain explicit coverage limitations. [Implementation and tests](reports/IMPLEMENTATION_REPORT.json) · [Source snapshots](CODE_MANIFEST.json).

Current project summaries can now appear above the historical round/checkpoint in the local archive-derived navigation. This does not rewrite the old interrupted checkpoint or certify complete provider capture.

A stale [policy hash binding](reports/POLICY_BINDING_REPAIR.json) was also repaired: the October 13 preference text was already authorized and preserved, but three derived metadata files still referred to its older digest. Only five derived hash fields changed; permission text and policy semantics did not.

The [official-rules comparison](reports/COMPARISON.json) found no changes to the October competition pages or the 23-person judge list. The proposed next research stage is independent verification of the ten essays, followed by a recommended three and two reserves presented in short cards. That stage and submission were not launched by this maintenance work.

Run `python3 tools/verify_current_edition.py` from the repository root. It checks the sealed October edition using five explicitly [preserved editorial originals](HISTORICAL_VIEW.json), then checks current links and the new evidence. Historical evidence and its original verifier are unchanged.

The full archive integrity check and all 683 tests passed ([verification](reports/TECHNICAL_CHECKS.json)). All 709 files bound by the accepted final-selection receipt retain their original bytes ([preservation check](reports/PRESERVATION_CHECK.json)).

The exact [user maintenance request](reports/USER_REQUEST.txt) is retained in its original Russian wording.

The first source pass preserved 3,355 updated cursors but stopped while rendering an older unsupported record ([original failure](reports/FIRST_PASS_FAILURE.json)). The renderer now records an explicit display gap without emitting the rejected body. An [exact compatibility transition](reports/COMPATIBILITY_REVIEW.json) preserves those verified cursors and avoids duplicate capture. The final source code passed all **699 tests** ([final code checks](reports/FINAL_CODE_TESTS.json)); the earlier required checks remain preserved separately.

The restarted collector service completed its own successful poll, verified against its new launchd process ID ([live recovery](reports/SERVICE_RECOVERY.json)). Operational source-read errors are zero; the report separately retains historical schema and tool-review gaps.
