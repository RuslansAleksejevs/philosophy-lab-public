[Home](../../../README.md) · [Final three](../../../docs/current-selection.md) · [Selection tree](../../../docs/selection-tree.md)

# Final edition: texts, checks and submission record

**E050, E012 and E051 are the human-selected three.** The final edition adds their accepted revisions, final PDFs, abstracts and method reports while retaining every earlier file in the prepared repository, or an exact snapshot when a guide page changed.

| Stage | What happened | Exact record |
| --- | --- | --- |
| Targeted revisions | Three AI authors addressed the argument/source plan; separate critics checked the changes. E050's small grammar repair had its own scoped check. | [Acceptance](submission-revision-20261101/FINAL_RECEIPT.json) |
| Clearer prose | Three fresh authors rewrote the essays; three separate critics checked preservation and clarity. E050/E051 passed. E012 kept its minor-fix verdict plus a separately accepted exact wording repair. | [Accepted versions](prose-polish-20261101/SELECTION.json) · [Acceptance](prose-polish-20261101/FINAL_RECEIPT.json) |
| Final presentation | Clickable bibliography links, revised abstracts and method reports, refined typesetting; six PDFs and 44 pages checked. Essay wording stayed frozen. | [Acceptance](layout/FINAL_RECEIPT.json) · [Prepared-file record](layout/READY.json) · [PDF checks](layout/PDF_QA.json) · [Visual checks](layout/VISUAL_QA.json) |
| Submission report | Ruslan answered “Да, все три” when asked whether all three had been submitted. Platform receipts and exact upload hashes were not independently checked. | [Exact answer and source identity](SUBMISSION_CONFIRMATION.json) |
| Public edition | A separate public copy of the complete prepared tree was requested; the original repository stays private. | [Instruction](REQUEST.txt) · [Publication policy](../../../PUBLICATION.md) |

[Final manuscript/PDF register](../../../docs/release-state.json) · [Downloadable package](../../../submission/20261101/README.md)

## Earlier versions and full research records

The [research bundle](research-records.tar.gz) retains 423 revision/prose-stage files and 68 accepted canonical event records. Its [inventory](RESEARCH_IMPORT.json) records every file hash and distinguishes canonical objects from administrative copies. This includes prompts, source-access notes and cleaned passages, author outputs, full reviews, exact repairs, earlier manuscripts, technical records and the older presentation package. Declared local source originals and runtime caches remain excluded as documented in that inventory.

The [previous prose package](prior-prose-package.tar.gz) separately preserves the 47-page presentation before the final 44-page layout. Its internal snapshot lists exact files. Final scientific wording is unchanged between those two layouts. The [first November revisions](../../../essays/final-20261101/prior-revisions) remain separate from the later clarity rewrite.

Old acceptance files retain their original `submitted: false` and `github_updated: false` values: they describe those earlier stages. The later human confirmation and publication instruction update the current status without rewriting them.

## Recheck the edition

From the repository root, run:

```sh
python3 -B tools/verify_release_edition.py
```

The checker verifies the [complete release manifest](RELEASE_MANIFEST.json), final files, research and conversation bundles, preserved earlier pages, and local navigation. It then restores the preceding reading edition in a temporary directory and runs its original verification chain. An optional `--manifest-sha256` accepts an independently retained manifest fingerprint.

These integrity checks do not establish novelty or real-world validity. The scientific reviews retain their recorded source-access and scope limits. Conversation coverage has its own [dated boundary](../../../logs/updates/20261101-release/README.md); logging continues locally.
