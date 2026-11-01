[← Conversation record](../README.md)

# Snapshot receipts

| Record | Status |
| --- | --- |
| [Current snapshot: October 17, editorial 02](20261017-editorial-02.json) | Current counts and fixed source cutoffs; compressed native files read correctly |
| [Preservation verification](20261017-editorial-verification.json) | All 13,751 prior message objects and all 26 prior bundles preserved; 32 current bundles and 10,394 members verified |
| [Current text hashes](20261017-editorial-text-hashes.json) | Computed hashes added to 62 current message projections; source snapshots retained |
| [First editorial pass](20261017-editorial-01.json) | Superseded diagnostics: compressed files were initially treated as plain JSONL, producing false parser-gap counts |

The first pass added valid saved and visible messages; its compressed-file gap
counts were wrong. The second pass corrects those counts without deleting the
first report or changing any retained message. History bundles in the
[manifest](../bundles/manifest.json) preserve replaced files and earlier indexes.
