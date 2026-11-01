# Visible-message parser repair

The current message format added a completed-status field, empty annotation arrays, and narrowly defined provenance metadata. The earlier strict parser excluded these otherwise visible messages. The repair accepts only the observed shapes and continues to reject unknown metadata and internal context.

The [source manifest](MANIFEST.json) retains the code and regression checks. The [real-source preflight](REAL_SOURCE_PREFLIGHT.json) checks the exact visible records in a bounded prefix of the current conversation. This is distinct from restarting the background service or resolving every historical capture gap.
