# Source-stage check: idea-080, sources-001

- `source-manifest.json` is a JSON array. Every source record has exactly the
  assigned keys `citation`, `read_status`, and `path`.
- The full source is the 25-page Oxford Research Archive accepted manuscript by
  Zofia Stemplowska. Its exact bytes are saved at the manifest path and its
  SHA-256 is `f86e418558f7bc2dac1392fc82dcdd99e3b1615839470a4af37f003c04509f3c`.
- Feinberg is only an indexed page-308 excerpt; the direct PDF returned 403.
- Cohen and Samp is an excerpt from an author-content online text display, not a
  saved full-page byte copy. The covered sections and time window are recorded.
- Angela M. Smith is metadata only; the publisher abstract is paraphrased and the
  inaccessible chapter is not treated as read.
- Search strings, relevant result URLs, access failures, and the distinction
  between primary text and metadata/snippets are recorded in `search-log.json`.
- Source coverage is bounded. No claim of exhaustive novelty search is made.
- No argument test, manuscript, or essay checkpoint was created.
