# Additional fixed-scope tool-log equality check

No additional tool-record identity was confirmed. The previous 1,938 exact native identities remain valid.

This pass checked the same 37 bundles, 13,118 members and 119 loose JSON files against only the previously frozen 81 native prefixes: 312,705,990 bytes, 66,194 lines and 15,456 generic `tool_pending` records. The 15,456 are a subset of the earlier 84,799 records across 3,355 sources.

| Check | Result |
| --- | ---: |
| Previous identities with source line and exact native-record hash | 1,938 |
| Also corroborated by unique SID + call ID + tool type + equal payload core | 1,934 |
| Previous records without an explicit `call_id` | 4 |
| Additional exact identities | 0 |
| Additional records with content-only equality | 36 |
| Additional unambiguous content matches | 0 |

All 36 additional content-only matches come from one shared two-byte string, found at 68 exported locations. It is repeated across 36 native records. This does **not** establish that those 36 records were transferred: only that the same very short string exists in both places. No substantive log contents are printed in these reports.

The four records without `call_id` keep their earlier exact source-line/hash proof. Their absence from the alternative call-ID check does not subtract them from the 1,938 verified records.

The 81-prefix type counts are 6,010 custom calls, 6,098 custom outputs, 1,672 function calls and 1,676 function outputs. These counts must not be presented as the composition of all 84,799 records.

Matching used complete allowlisted payload cores, complete literal body strings and complete UTF-8 non-JSON members. It did not use substring, fuzzy or semantic matching, reconstruct quotations, or infer identities from repeated text. Hidden reasoning and system/developer contexts were skipped. The report does not prove that differently formatted indirect copies do not exist.

The earlier remainder of 82,861 records remains **UNKNOWN coverage, not proven loss**. This follow-up does not expand the native source set, change the previous eight-file tool-coverage package, export any bodies, take a new cutoff, run a service/provider, or open a canonical writer. Per-hash example locations are capped at 12; group occurrence and identity counts are complete within this equality scope.
