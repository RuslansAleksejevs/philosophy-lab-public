# Tool-log coverage at the frozen export cutoffs

All **37 bundles, 13,118 members and 119 loose JSON files** passed this metadata/hash audit. The 1,938 exported reviewed Codex tool fragments match exact native session IDs, line numbers and record hashes. Their 81 frozen source prefixes (312,705,990 bytes) were independently rehashed. Native bodies were not parsed, printed or copied.

The frozen native scan classified 84,799 records as generic `tool_pending`. They are function/custom-tool calls and their results; it did not preserve a full per-type histogram. The export contains 967 custom calls, 951 custom outputs, 8 function calls and 12 function outputs. Old conversation/turn bundles retain aggregate pending counters, not additional per-tool identities. The remaining **82,861 have unverified exact export coverage**. This is **not a count of lost records**: indirect copies in unstructured text were not searched.

Two exclusions must stay separate: **1,145 sensitive tool-body records** in the native scan, versus **12 previously archived tool fragments** withheld by current export validation. These are different populations; their overlap is unmeasured, and 12 is not the total native exclusion count.

The retained visible conversation has its own verification. A complete service/provider trace is not certified. This report precedes the final verification delta and does not change any source, capture policy or repository file.

See `REPORT.json`, `EXACT_TOOL_IDENTITIES.json`, `BUNDLE_AND_INDEX_AUDIT.json`, `NATIVE_PREFIX_VERIFICATION.json` and `SCOPE_CLARIFICATION.json` for bound evidence.
