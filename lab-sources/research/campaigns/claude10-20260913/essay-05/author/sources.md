# Sources and coverage

Coverage vocabulary: **full** = whole work read; **excerpt** = specified portions of the retrieved text read directly; **summary** = only an abstract, publisher description, encyclopedia gloss or automated page summary read; **unavailable** = not obtained, or obtained but not readable by me.

All saved paths are relative to the task folder `batches/claude10-20260913/tasks/essay-05-author/`. Files under `sources/` were written by the local download hook, not by me.

---

## A. Directly retrieved and read

### A1. Garrett Cullity, "The Free Rider Problem," *Stanford Encyclopedia of Philosophy*
- URL requested and final: https://plato.stanford.edu/entries/free-rider/
- HTTP 200; content type text/html; 117,646 bytes; captured 2026-09-13T23:52:57Z (per hook metadata)
- Saved: `sources/8128bdca4367ff0e57ad-26266279193d.original.html`, `sources/8128bdca4367ff0e57ad-26266279193d.txt`, metadata `sources/8128bdca4367ff0e57ad-26266279193d.json`
- raw_sha256: 8128bdca4367ff0e57ad014b3317d4afdab696d610ec5801ed11a53a181b3b1e
- Extraction method (per metadata): HTML text nodes excluding head/script/style
- **Coverage: excerpt.** Lines read directly from the saved text: 300–559, 700–1029, 1290–1619. This covers the article roadmap, §1 (collective action problems), §2.2–§2.4 (Hobbes, Hume, twentieth-century developments), the second half of §3.3 (public goods features, common-pool vs. club goods, collective production of private goods), §4 (solving free rider problems, Ostrom), and the opening of §5/§5.1.
- Exact locations used in the essay: §1 (definition of a collective action problem); §3.3 (nonrivalness; Ostrom & Ostrom 1977 common-pool goods; Buchanan 1965 club goods; "All that is needed is the perception that one can receive the good without having contributed to producing it"); §4 (Ostrom's six conditions).
- **Provenance caveat:** the author attribution "Garrett Cullity (Australian National University)" comes from the WebFetch page summary. The byline was not present in the portions of extracted text I read directly. Treat authorship as reported-but-not-independently-verified by me.

### A2. John Stuart Mill, *On Liberty*
- URL requested and final: https://www.gutenberg.org/cache/epub/34901/pg34901.txt
- HTTP 200; content type text/plain; 331,189 bytes; captured 2026-09-14T02:12:23Z
- Project Gutenberg eBook #34901, Walter Scott Publishing Co., Ltd. edition (identification from the fetched file's front matter, as reported by the page summary)
- Saved: `sources/cfc8de9ac48709ef8e66-06c8c985c38f.original.txt`, `sources/cfc8de9ac48709ef8e66-06c8c985c38f.txt`, metadata `sources/cfc8de9ac48709ef8e66-06c8c985c38f.json`
- raw_sha256: cfc8de9ac48709ef8e66922b32bac51335c883082e4da24251e1290816df904c
- Extraction method (per metadata): decoded source text, no AI summary
- **Coverage: excerpt.** Lines read directly: 1250–1579 and 1620–1919. This spans the later part of Chapter 2 from the utility-of-opinion discussion through the Socrates/Marcus Aurelius examples, the "second division of the argument," and the dead-dogma material.
- Exact quotations used in the essay, all from Chapter 2, with saved-text line numbers:
  - "if it is not fully, frequently, and fearlessly discussed, it will be held as a dead dogma, not a living truth" — line 1674–1675
  - "abides as a prejudice, a belief independent of, and proof against, argument"; "This is not knowing the truth." — lines 1690–1692
  - "That simple minds, having been taught the obvious grounds of the truths inculcated on them, may trust to authority for the rest… may repose in the assurance that all those which have been raised have been or can be answered, by those who are specially trained to the task." — lines 1777–1782
  - "received passively, not actively" — line 1870
  - "the creed remains as it were outside the mind, encrusting and petrifying it" — lines 1879–1880
- Note: because this is a Gutenberg plain-text edition, I cite by chapter rather than by print pagination, which the file does not carry.

### A3. "Legal Positivism," *Stanford Encyclopedia of Philosophy*
- URL requested and final: https://plato.stanford.edu/entries/legal-positivism/
- HTTP 200; content type text/html; 86,747 bytes; captured 2026-09-14T02:12:24Z
- First published 3 January 2003; substantive revision 10 October 2025 (read at saved-text line 199)
- Saved: `sources/41138bd9a434272c5363-5fac38d08107.original.html`, `sources/41138bd9a434272c5363-5fac38d08107.txt`, metadata `sources/41138bd9a434272c5363-5fac38d08107.json`
- raw_sha256: 41138bd9a434272c5363541f0123fc2bf43694487a3032394cb648f821e5951c
- **Coverage: excerpt.** Lines read directly: 160–201, 200–269, 470–561, 560–759. This covers the opening statement of positivism, the table of contents, the Kelsen discussion, and §2 ("The Existence and Sources of Law") through the start of §3.
- Exact quotations used in the essay, all from §2, with saved-text line numbers:
  - rule of recognition as "a social rule that exists only because it is actually practiced, that is, used to guide conduct" — lines 534–536
  - internal point of view: officials "use it as a standard for guiding and evaluating their own and others' behavior, and this use is displayed in their conduct and speech, including the resort to various forms of social pressure to support the rule and the ready application of normative terms such as 'duty' and 'obligation' when invoking it" — lines 552–557
  - "Ordinary subjects' contribution to the existence of law may therefore amount to no more than passive compliance, and in an extreme case perhaps less than this." — lines 600–602
  - "this division of labor is not a normatively neutral fact about law; it is politically charged, for it sets up the possibility of law becoming remote from the life of a society, a hazard to which Hart is acutely alert (1961 [2012: 117]…)" — lines 621–625
- **Provenance caveat:** the entry's byline was not captured in the extracted text at the positions I read, so I cite the entry by title and revision date rather than by author. This is deliberate, not an oversight.

---

## B. Retrieved but not readable, or summary-only

### B1. Unidentified PDF on moral testimony pessimism and authenticity (Oxford ORA)
- URL requested and final: https://ora.ox.ac.uk/objects/uuid:6640a8de-57c9-4709-80af-2c51b446b388/files/m8c25bbfcb78c49535d9af4f66a574602
- HTTP 200; application/pdf; 312,983 bytes; captured 2026-09-13T23:53:32Z; extracted with Poppler `pdftotext -layout`
- Saved: `sources/447f58e82fd1bf430b23-8f28c9af7de5.original.pdf`, `sources/447f58e82fd1bf430b23-8f28c9af7de5.txt`, metadata `sources/447f58e82fd1bf430b23-8f28c9af7de5.json`
- raw_sha256: 447f58e82fd1bf430b23d191cbaa4682a94e631370680f16c3d44f419ac6a988
- **Coverage: unavailable.** The file was downloaded and text was extracted, but my attempt to read the extracted text returned a harness halt rather than content, and I did not retry. The WebFetch summarizer separately failed to decode the PDF. **Author and title remain unidentified, and nothing from this source is cited, quoted or relied on anywhere in the essay.** A search result listed the URL under the title "Moral Testimony Pessimism and the Uncertain Value of Authenticity," but I did not confirm this against the file.

### B2. Paulina Sliwa, "In Defense of Moral Testimony," *Philosophical Studies* 158(2) (March 2012): 175–195, DOI 10.1007/s11098-012-9887-6
- Repository record: https://dspace.mit.edu/handle/1721.1/106221 (MIT Open Scholarship; author's final manuscript)
- Saved (mapping inferred from call order, metadata JSON not read): `sources/6837f3007af01942c1a1-5072d3792214.txt` and `.json`
- **Coverage: summary.** I read the repository record's abstract and citation block only: "Moral testimony has been getting a bad name in the recent literature. It has been argued that while testimony is a perfectly fine source for nonmoral belief, there's something wrong with basing one's moral beliefs on it. This paper argues that the bad name is undeserved: Moral testimony isn't any more problematic than nonmoral testimony."
- **The article's full text was not obtained.** Two routes failed: https://dspace.mit.edu/openaccess-disseminate/1721.1/106221 (HTTP 404) and https://dspace.mit.edu/bitstream/handle/1721.1/106221/11098_2012_Article_9887.pdf (HTTP 405). My characterisation of Sliwa's position in §2 of the essay rests on this abstract plus the overview at B3, not on her text, and no words are quoted from her.

### B3. "Moral Testimony," *1000-Word Philosophy: An Introductory Anthology* (6 March 2014)
- URL: https://1000wordphilosophy.com/2014/03/06/moral-testimony/
- Saved (mapping inferred from call order, metadata JSON not read): `sources/e3b646c4799e4b41be50-4027c02e5084.txt` and `.json`
- **Coverage: summary.** This is an introductory overview, not a primary source, and I treat it as such: it was used only to corroborate the shape of the pessimist/optimist dispute and the standard reference list (Hills 2009, Jones 1999, Sliwa 2012, Hopkins 2007, Nickel 2001, McGrath 2009, Driver 2006, Kvanvig 2003, Kukla 2006, Thomas 1998, Wolff 1970). No claim in the essay rests on it alone.

---

## C. Sought and not obtained

Each of the following was attempted and failed; nothing from them is cited as read.

| Work | URL attempted | Result |
|---|---|---|
| R. M. Farley, "Realism about Moral Deference" | https://philarchive.org/archive/FARRAM-3 | HTTP 403 |
| David Enoch, "A Defense of Moral Deference" | https://www.kcl.ac.uk/law/research/D-Enoch,-A-Defense-of-Moral-Deference.doc | HTTP 404 |
| David Enoch, "A Defense of Moral Deference" | https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2601807 | HTTP 403 |
| Max Lewis, "The New Puzzle of Moral Deference" | https://blogs.kent.ac.uk/futureofnormativity/files/2018/06/The-New-Puzzle-of-Moral-Deference-The-Future-of-Normativity.pdf | HTTP 404 |
| Alison Hills, "Moral Testimony and Moral Epistemology" | https://philpapers.org/rec/HILMTA | HTTP 403 |
| Paulina Sliwa, "In Defense of Moral Testimony" (full text) | two MIT DSpace routes, see B2 | HTTP 404, 405 |

No OCR was available, and no paywalled copy was purchased, requested or otherwise obtained.

---

## D. Cited in the essay without direct access

These works are cited because the argument engages positions that are theirs. I did not read any of them for this essay. Where a citation is corroborated by a source I did read, I say so; where it rests on my background knowledge alone, I flag it as unverified.

**Corroborated by an accessed source.**
- Hart, *The Concept of Law* (1961; 3rd edn. 2012), pp. 116–117 — every claim I make about Hart is routed through, and attributed to, the *SEP* "Legal Positivism" entry (A3). I quote the encyclopedia, never Hart directly.
- Ostrom & Ostrom 1977; Buchanan 1965; Olson 1965; Ostrom 1990; Ostrom 2010 — all cited via Cullity's entry (A1), and marked as such in the essay's works-cited list.
- Sliwa 2012 — see B2 (abstract read).
- Hills 2009 (*Ethics* 120(1): 94–127); Enoch 2014 (*Journal of Philosophy* 111(5): 229–258); Wiland 2021 (OUP) — bibliographic details corroborated by search-result metadata, including the Philosophy Documentation Center identifier `jphil_2014_0111_0005_0229_0258` for Enoch. Substantive characterisations in the essay rest on published abstracts and the OUP description, **not** on the texts: Hills on the knowledge/understanding distinction; Enoch on deference as risk-minimisation; Wiland on adviser and advised forming a joint agent. I attribute these at that level of generality and quote none of them.
- Kagan 2011, *Philosophy & Public Affairs* 39(2): 105–141 — details confirmed by search, article not read.

**Unverified bibliographic details (background knowledge only).**
- Hills 2013, *Philosophy Compass* 8(6), DOI 10.1111/phc3.12040 — DOI seen in search results; pagination not confirmed.
- Hopkins 2007, *PPR* 74(3): 611–634.
- Jones 1999, *Journal of Philosophy* 96(2): 55–78.
- Nickel 2001, *Ethical Theory and Moral Practice* 4(3): 253–266.
- McGrath 2009, *Philosophical Perspectives* 23: 321–344.
- Parfit 1984, *Reasons and Persons*, Oxford: Clarendon Press.
- Wolff 1970, *In Defense of Anarchism*.

For each of these the essay's use is a general placement in the debate, not a specific textual claim. Readers should verify volume and page details independently.

---

## E. Rules text consulted

`input/RULES.md` records that the official competition rules and FAQ at https://www.zacharygoodsell.com/ai-philosophy-competition-rules and https://www.zacharygoodsell.com/ai-philosophy-competition-faq were downloaded and read on 2026-09-13 UTC, with originals preserved in the local technical archive. I did not re-fetch them; I relied on the constraints as recorded in that file (6000-word maximum excluding bibliography, no minimum).
