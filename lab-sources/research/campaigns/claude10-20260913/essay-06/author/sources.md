# Sources — essay-06-author, draft-001

All saved paths below are relative to the project root; the batch source directory is
`batches/claude10-20260913/tasks/essay-06-author/sources/`. Each retrieval has three
files with a shared prefix: `<prefix>.json` (extraction metadata), `<prefix>.txt`
(extracted text), `<prefix>.original.html` or `.original.pdf` (raw bytes).

Coverage vocabulary used below:
- **full** — I read the whole extracted text.
- **excerpt** — I read located portions of the extracted text and quote only from those.
- **summary** — I have only a WebFetch model summary of the page; the extracted text was
  saved but I did not read it myself.
- **unavailable** — no retrieval established; cited from background knowledge or from a
  second-hand report, and marked as such.

No OCR was available. No paywalled item was purchased or circumvented.

---

## A. Sources retrieved and read directly

### A1. John Stuart Mill, *On Liberty* (1859)

- Edition retrieved: Project Gutenberg EBook #34901 (release date 10 January 2011).
- URL: https://www.gutenberg.org/files/34901/34901-h/34901-h.htm
- Saved: `0e226c46af44b1006c61-2572164e914f.txt` / `.original.html` / `.json`
- Extraction: HTML text nodes, 357,814 bytes, HTTP 200, `TEXT_EXTRACTED`.
- **Coverage: excerpt.** Read extraction lines 1–40 (front matter), 2400–2539 (Ch. II),
  4180–4299 (end of Ch. IV), 4665–4800 and 4830–4969 (Ch. V).
- **Exact location of the passage used:** extraction lines 4689–4704, which carry the
  edition's own inline page markers `[Pg 194]` and `[Pg 195]`. The block quotation in
  §6 of the essay was transcribed from those lines and is verbatim, including
  "His voluntary choice is evidence that what he so chooses is desirable, or at the
  least endurable, to him" and "is thenceforth in a position which has no longer the
  presumption in its favour, that would be afforded by his voluntarily remaining in it."
- The follow-on quotation about "the necessities of life" is at extraction lines
  4704–4707, page marker `[Pg 195]`. Cited in the essay as p. 195. Verified.
- Also read but not quoted: Humboldt / dissoluble-engagements passage at lines
  4714–4728 (`[Pg 196]`–`[Pg 197]`), an abandoned line of development (see process.md).
- Note: page numbers cited in the essay are the page numbers of **this Gutenberg
  edition**, not of a standard scholarly edition. The essay's bibliography flags this
  by naming the edition. A reviser may wish to add canonical chapter/paragraph
  references (Ch. V, paras. 11–12) instead.

### A2. G. A. Cohen, "The Structure of Proletarian Unfreedom"

- *Philosophy & Public Affairs* 12(1) (Winter 1983): 3–33. JSTOR stable URL given in the
  scan: http://www.jstor.org/stable/2265026
- Retrieved from: https://www.uvm.edu/~fmagdoff/employment%20Jan.12.11/structure%20of%20proletarian%20unfreedom.pdf
- Saved: `9abebd04804e14208dd0-7cfe811ea8f0.txt` / `.original.pdf` / `.json`
- Extraction: Poppler `pdftotext -layout`, 3,849,609 bytes, HTTP 200, `TEXT_EXTRACTED`.
  The scan is a JSTOR page-image PDF with an embedded text layer; the text layer has
  frequent missing inter-word spaces (e.g. "AccordingtoKarlMarx"), so quotations were
  transcribed with spacing restored. No wording was altered.
- **Coverage: excerpt.** Read extraction lines 1–60 (masthead and opening), 255–374,
  375–449 (Sections VI–VIII).
- **Exact locations** (the scan preserves the journal's page numbers, rendered by the
  text layer as "9", "Io", "II", "I2" for 9, 10, 11, 12):
  - Two-temporal-indices claim: extraction lines 256–281 → article **p. 8**. Cited as
    p. 8 in the essay. Verified.
  - Ten people / one key / photoelectric devices: extraction lines 305–315 → **p. 9**.
    Cited as p. 9. Verified.
  - "even though necessarily at least nine will remain in the room, and in fact all
    will": extraction lines 350–352 → **p. 10**.
  - "though each is individually free to leave, he suffers with the rest from what I
    shall call collective unfreedom": extraction lines 407–409 → **p. 11**. Cited as
    p. 11. Verified.
  - "each is free only on condition that the others do not exercise their similarly
    conditional freedom": extraction lines 400–403 → **p. 11**. Cited as p. 11. Verified.
- **KNOWN ERROR IN draft-001 (§8f):** the essay attributes "necessarily at least nine
  will remain" to p. 9. It is on **p. 10**. The p. 9 text reads "It follows that,
  whatever happens, at least nine people will remain in the room." A reviser should
  either change the page to 10 or quote the p. 9 sentence instead.

### A3. *Stanford Encyclopedia of Philosophy*, "Coercion"

- URL: https://plato.stanford.edu/entries/coercion/
- Saved: `68958b608d7725bd5085-c18123c3ff4d.txt` / `.original.html` / `.json`
- Extraction: HTML text nodes, HTTP 200, `TEXT_EXTRACTED`.
- **Coverage: excerpt.** Read extraction lines 240–299 (table of contents), 1000–1109
  (§2.1.3 and §2.2), 1330–1449 (§2.3 end and §2.4).
- **Verified locations:**
  - Section titles "2.2 Threats and Baselines" (line 1057) and "2.4 Coercive Offers?"
    (line 1381) confirmed from the entry itself. The essay's citations to §2.2 and §2.4
    are therefore verified.
  - Baseline formulation "compared to the baseline, threats worsen the coercee's
    situation, while offers do not": lines 1070–1072.
  - Nozick's own unpursued questions about prior coercion restructuring what is
    possible, with the internal citation "Nozick 1969, 445–47": lines 1013–1027.
  - Wertheimer's *Coercion* described as setting "the current standard", with internal
    citation "Wertheimer 1987": lines 1336–1343.
  - Zimmerman's island case and the phrase "the appropriate baseline for evaluating the
    proposal is the state of affairs that the recipient would face in the absence of
    special interference by the proposal maker": lines 1414–1432.
  - "seems to be vested in the offerer's actions that prevent the recipient from
    improving her situation or finding better offers elsewhere": lines 1442–1447.
    Both quotations in essay §3 are verbatim from these lines.
- **UNVERIFIED:** the essay's bibliography gives the entry as "Anderson, Scott. 2023."
  The author name and year were not confirmed from the retrieved text (I did not read
  the entry's header or copyright block). A reviser should confirm or replace with
  "*SEP*, entry 'Coercion', accessed via the saved capture."

### A4. *Stanford Encyclopedia of Philosophy*, "Dynamic Choice"

- URL: https://plato.stanford.edu/entries/dynamic-choice/
- Saved: `62757450323609bfdddd-1be082dbc820.txt` / `.original.html` / `.json`
- Extraction: HTML text nodes, HTTP 200, `TEXT_EXTRACTED`.
- **Coverage: excerpt.** Read extraction lines 255–384 (TOC and §1.1), 420–559 (§1.1 end,
  §1.2), 640–789 (intransitivity section, money pump, self-torturer).
- **Verified locations:**
  - Statement of Quinn's self-torturer, including "The device has 1001 settings",
    "the increments in current are so small that the self-torturer cannot tell the
    difference between adjacent settings", the $10,000 per advance, the no-permanent-
    return condition, and the preference for *s*+1 over *s* alongside the preference
    for 0 over 1000: extraction lines 752–776. The entry attributes the case to
    "Quinn (1993)".
  - Money pump attributed to "Donald Davidson, J. McKinsey, and Patrick Suppes (1955)":
    extraction lines 701–712; worked example lines 713–747.
- **UNVERIFIED:** the essay cites this material as "Andreou 2023, §1.4". The entry's
  visible TOC fragment I read (lines 255–290) listed only §§2.1–2.4, 3, 4 and the
  sub-headings "1.1 Incommensurable Alternatives" and "1.2 Time-Biased Preferences".
  I did **not** verify that the self-torturer sits in §1.4, nor the author's name or the
  entry year. A reviser should confirm the section number and authorship or cite the
  entry without a section number.

### A5. Japa Pallikkathayil, "Consent and the Formula of Humanity"

- Retrieved from: https://philosophy.northwestern.edu/community/nustep/07/Consent.pdf
- Saved: `e169e892fe4022b4ebc3-22758f090fbe.txt` / `.original.pdf` / `.json`
- Extraction: Poppler `pdftotext -layout`, 181,169 bytes, HTTP 200, `TEXT_EXTRACTED`.
  (The WebFetch summariser could not parse the PDF; the separately saved extraction
  parsed cleanly and is what I read.)
- **Coverage: excerpt.** Read extraction lines 1–200, covering the abstract and the
  whole of Section I up to Korsgaard's response.
- **Exact location used:** the Korsgaard criterion, quoted by Pallikkathayil as
  "you treat someone as a mere means whenever you treat him in a way to which he could
  not possibly consent (G 430).", is at extraction lines 61–63, in Section I, with her
  note 5 giving the Korsgaard reference. The essay §6 quotes this **as quoted in
  Pallikkathayil** and says so.
- Also read: the block quotation from Korsgaard on force, coercion and deception
  (lines 83–87), and Pallikkathayil's four Kantian cases of permissible force
  (lines 91–105). Not used; see process.md.
- **UNVERIFIED:** this is an undated working copy hosted in a conference archive. I did
  not establish a publication venue, year, or page numbers, and the essay's bibliography
  accordingly describes it as a manuscript from that archive. A reviser should check
  whether a published version exists and cite that instead.

---

## B. Source retrieved but read only as a model summary

### B1. *Stanford Encyclopedia of Philosophy*, "The Ethics of Manipulation"

- URL: https://plato.stanford.edu/entries/ethics-manipulation/
  (An earlier attempt at https://plato.stanford.edu/entries/manipulation/ returned
  HTTP 404; the slug was corrected.)
- Saved: `97aee1e89ebead3d4f4b-4d4db5168f86.txt` / `.original.html` / `.json`
- Extraction: HTML text nodes, HTTP 200, `TEXT_EXTRACTED`.
- **Coverage: summary.** I opened the saved extraction but the first 120 lines were
  navigation boilerplate only, and I did not locate and read the substantive sections.
  My working content for this entry is the WebFetch model summary, which reported:
  the bypassing-reason account; Susser, Roessler and Nissenbaum's "hidden influence"
  where targets are "not consciously aware of" it and "couldn't easily become aware of"
  it; Noggle's trickery/faulty-mental-states account; the pressure account; Barnhill's
  account; and — the point I lean on — that the reviewed accounts "focus on individual
  acts or influences" and that no account explicitly treats manipulation as a property
  of extended sequences.
- **UNVERIFIED:** the essay cites "Noggle 2022, §2.1" and "§2.2". Neither the section
  numbers, nor the author, nor the year were confirmed against the saved text. The
  short phrases placed in quotation marks in essay §3 ("could not easily become aware
  of") come from the summary, not from my own reading of the entry. **A reviser should
  either verify these against the saved extraction or downgrade them to paraphrase.**
  This is the weakest citation in the manuscript and I flag it deliberately.

### B2. *Stanford Encyclopedia of Philosophy*, "Informed Consent"

- URL: https://plato.stanford.edu/entries/informed-consent/
- Saved: `04ed0fcb8eee755001f3-0704d161aed1.txt` / `.original.html` / `.json`
- Extraction: HTML text nodes, 116,389 bytes, HTTP 200, `TEXT_EXTRACTED`.
- **Coverage: summary.** I read the metadata file but not the extracted text. My working
  content is the WebFetch summary, which reported the three validity conditions
  (capacity; disclosure and understanding; voluntariness, including freedom from
  "coercion, undue inducement, and problematic pressure"), the "moral magic" framing,
  and the list of frequently cited theorists (Beauchamp and Childress; Wertheimer;
  Manson and O'Neill; Dougherty, Hurd, Feinberg).
- **UNVERIFIED:** the essay cites "Eyal 2019, §1". Author, year and section number are
  all from background knowledge, not from the retrieval. Same recommendation as B1.
- Used in essay §1 only, for the uncontroversial list of synchronic validity conditions.

---

## C. Works cited but not retrieved (unavailable)

None of the following was read in this session. Each is cited in the essay only for a
claim that is either (i) reported by a source I did read, or (ii) general and
uncontroversial. No quotation in the manuscript is attributed to any of them except the
Wood phrase noted below, which is a known defect.

| Work | Status | Basis for the essay's use |
|---|---|---|
| Warren Quinn, "The Puzzle of the Self-Torturer", *Philosophical Studies* 59 (1990): 79–90; repr. *Morality and Action* (CUP 1993) | **unavailable** — Springer link (https://link.springer.com/article/10.1007/BF00368392) is paywalled; a PhilArchive secondary paper and a course handout both failed to retrieve (see §D) | Case description taken entirely from A4 (SEP "Dynamic Choice"), which is cited alongside. No Quinn quotation appears in the essay. |
| Derek Parfit, *Reasons and Persons* (OUP 1984) | **unavailable** | Cited once, in essay §4 and §9, for imperceptible-contribution cases. The chapter reference "ch. 3" is from background knowledge and is **unverified**; a web search result associated the relevant discussion with the "Five Mistakes in Moral Mathematics" material. No quotation. |
| Alan Wertheimer, *Coercion* (Princeton 1987) | **unavailable**; existence, title and date verified via A3 (SEP "Coercion", extraction lines 1336–1343) | Listed in the bibliography; no substantive claim rests on it beyond what A3 reports. |
| Alan Wertheimer, *Exploitation* (Princeton 1996) | **unavailable**; publisher and year from background knowledge, **unverified** | Source of the nonworseness claim. My knowledge of the claim's content and of Wertheimer's authorship of it comes from WebSearch result summaries (see §E), which stated that the claim is "usually defined as the claim that a transaction, no matter how exploitative, cannot be worse than its absence, as articulated by Alan Wertheimer", and that Wertheimer himself came to reject it. The essay says "standardly credited to" rather than asserting the attribution flatly. |
| Allen Wood, "Exploitation", *Social Philosophy and Policy* 12(2) (1995) | **unavailable** | **KNOWN DEFECT IN draft-001 (§3):** the essay puts in quotation marks, attributed to Wood, the words "not because of the exploiter's act, but because background conditions deny the exploited acceptable alternatives". That wording came from a WebSearch **result summary paraphrasing** a third paper, not from Wood's text. It must not stand as a quotation. A reviser should de-quote it, attribute the thought to the exploitation literature generally, or delete it. Flagged for the critic. |
| David Zimmerman, "Coercive Wage Offers", *Philosophy & Public Affairs* 10(2) (1981) | **unavailable** | View reported and quoted **from A3**, which the essay cites for it. Volume/issue/pages are from background knowledge and are **unverified**. |
| Robert Nozick, "Coercion" (1969) | **unavailable** | Baseline account reported from A3. A3 itself cites "Nozick 1969, 445–47" (verified). The bibliography's volume title, editors and page span 440–72 are from background knowledge and are **unverified**. |
| Davidson, McKinsey and Suppes (1955) | **unavailable** | Money-pump attribution verified from A4, extraction line 702. Journal, volume and pages in the bibliography are from background knowledge and are **unverified**. |
| Christine Korsgaard, *Creating the Kingdom of Ends* (CUP 1996) | **unavailable** | Quoted only as quoted in A5, and the essay says so. Korsgaard's own pagination not accessed. |

---

## D. Failed retrievals (recorded honestly; no source established)

1. https://philarchive.org/archive/PORWARv2 — Porter, "What's a rational self-torturer
   to do?" — **HTTP 403 Forbidden.** Sought for a verbatim statement of Quinn's case.
2. http://rdoody.com/Self-torturer%20Puzzle%20handout.pdf — first attempt refused
   because the URL used `http`; retried as `https://rdoody.com/...` and failed with
   **"certificate has expired"**. No text obtained either time.
3. https://philarchive.org/archive/LAINPA — Arto Laitinen, "Normative Powers, Agency,
   and Time" — **HTTP 403 Forbidden.** This is the retrieval I most regret losing: it is
   the closest published work to the essay's topic that I identified, and I cannot rule
   out overlap with my §7 principles. Recorded as an open priority risk in process.md.
4. https://plato.stanford.edu/entries/manipulation/ — **HTTP 404.** Corrected to the
   `ethics-manipulation` slug (B1).
5. Springer page for Quinn 1990 — not fetched; search results indicated no shareable
   full text and institutional access would be required. Not attempted further.

No attempt was made to bypass any paywall, and no access was purchased.

---

## E. Web searches run (provenance of leads and of the priority check)

Search-result summaries are **not** sources and nothing in the manuscript rests on them
except the two items explicitly flagged above (Wertheimer's nonworseness claim; the Wood
phrase). Queries, in order:

1. `Warren Quinn "The Puzzle of the Self-Torturer" 1990 Philosophical Studies pdf`
2. `consent sequence of small steps "each step" permissible whole impermissible philosophy incremental`
3. `Wertheimer "nonworseness claim" exploitation mutually beneficial consensual Zwolinski`
4. `philosophy "salami tactics" OR "incrementalism" moral wrong "no single step" gradual erosion consent manipulation`
5. `Parfit "harmless torturers" imperceptible harms "Reasons and Persons" five mistakes in moral mathematics`
6. `"normative power" consent "over time" diachronic agency "path dependence" philosophy article`
7. `philosophy consent justification "baseline" outside options endogenous employer erodes alternatives exploitation "reservation" argument`
8. `Nozick "Coercion" 1969 moralized baseline normal expected course of events consent voluntariness Cohen "voluntary" proletarian`

Searches 2, 4, 6 and 7 were run as priority checks on the essay's thesis. Search 2
returned only general consent theory and the searcher explicitly reported that the
results "don't specifically address the incremental or 'sequence of small steps' problem".
Search 4 returned only popular and political-science treatments of salami tactics, no
philosophical treatment. Search 7 surfaced the exploitation literature's standing
assumption that the victim's want of alternatives is a background condition the exploiter
finds rather than makes. I regard these as weak evidence of novelty, not proof; see the
unresolved-risk entry in process.md.

---

## F. Summary of corrections owed to draft-001

For the critic and any reviser, in priority order:

1. **§3, Wood quotation.** Remove the quotation marks and the attribution, or replace
   with an accurate citation. The wording is not verified as Wood's.
2. **§8f, Cohen page.** "necessarily at least nine will remain" is on p. 10, not p. 9.
3. **Section numbers and authorship for the three SEP entries.** "Eyal 2019 §1",
   "Noggle 2022 §2.1/§2.2" and "Andreou 2023 §1.4" are unverified; only the two
   *Coercion* section numbers (§2.2, §2.4) were confirmed against the saved text.
4. **Bibliographic details** for Nozick 1969, Zimmerman 1981, Davidson–McKinsey–Suppes
   1955, Wertheimer 1996 and Wood 1995 are from background knowledge and should be
   checked before any use beyond this lab.
5. **Mill pagination** is edition-specific (Gutenberg #34901); consider adding
   chapter-and-paragraph references.
