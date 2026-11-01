# Review of the 430 remaining log gaps

All 430 records were inspected at frozen cutoffs. The 29 source prefixes matched their SHA-256 hashes.

| Classification | Records |
| --- | ---: |
| Tool calls and results, not reviewed for export | 289 |
| Context carried under the user role | 43 |
| Large, complete internal `item_completed` events | 13 |
| Developer tool declarations | 7 |
| Goal lifecycle events | 2 |
| Inherited visible messages | 76 |
| **Total** | **430** |

**No missing unique visible text was found among these gaps.** The 76 inherited messages contain 32 distinct role/text pairs, all retained in the export. Of those records, 68 also exist under the same session and source line. Eight inherited identity copies are pending the final delta; their texts remain in the original conversations.

[GAP_REVIEW.json](GAP_REVIEW.json) lists the decision and source identities. [GAP_SHAPES.json](GAP_SHAPES.json) contains metadata shapes and source hashes; [VISIBLE_OVERLAP.json](VISIBLE_OVERLAP.json) records the text-hash matches. No native envelopes, hidden context bodies, or tool bodies are included.

The [activity counts](ACTIVITY_SOURCE_COUNTS.json) describe the frozen 14,939-message snapshot, before that final delta. File hashes are in [MANIFEST.json](MANIFEST.json). This audit does not claim complete provider coverage.
