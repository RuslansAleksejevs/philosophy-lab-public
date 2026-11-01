[Archive guide](../../README.md) · [Submitted edition](../../../docs/submitted-edition.md)

# Submission and closeout conversations

This supplement adds **38 visible messages from two existing sessions** to the earlier 15,657-message export. The retained union is now **15,695 messages across 3,424 sessions**, including the eight previously labelled inherited copies.

The scan ran on **November 1, 2026, 12:07:03–12:07:28 UTC** (04:07 in Los Angeles). Each source has its own exact boundary and prefix hash. These later conversations include the final methodology corrections, submission confirmation, attachment verification and the start of repository closeout. Work after a source's cutoff is not implied to be included.

- [Session index and counts](INDEX.json)
- [Visible messages](visible-messages.tar.gz), stored as JSON by session
- [Per-source cutoffs](native-source-cutoffs.json.gz)
- [Preceding supplement](../20261101-release/README.md)

All earlier message objects remain unchanged. No new scientific review was run for this export. The scan examined 3,395 scoped non-internal native sources and excluded 342 internal-runtime sessions. It found no unavailable scoped source; this is not proof of full provider coverage. Unsupported tool bodies, hidden reasoning, native envelopes and attachments remain outside this visible-message supplement. Older gap and exclusion ledgers remain in place; the index records this scan's own counts.

Run `python3 -B tools/verify_submission_edition.py` from the repository root to check the complete retained union and its predecessor editions. Local collection may continue beyond this fixed snapshot.
