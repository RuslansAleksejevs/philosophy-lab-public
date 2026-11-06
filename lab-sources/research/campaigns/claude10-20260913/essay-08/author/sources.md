# Sources — essay-08-author, draft-001

All retrievals were made during this stage via WebSearch/WebFetch. Where the hook performed a
separate direct HTTP download, I give the saved extraction path and state how much of that saved
text I actually read. Coverage labels: **full** = whole extracted text read; **excerpt** = named
line/section ranges read; **summary only** = only a model-generated summary of the page was
available; **unavailable** = retrieval failed.

Saved-source directory (absolute):
`/Users/ruslansaleksejevs/Documents/Claude Code/Philosophy Lab/batches/claude10-20260913/tasks/essay-08-author/sources/`
Paths below are given relative to that directory.

---

## A. Primary sources read directly

### A1. Friedman, Jane. “The Epistemic and the Zetetic.” *The Philosophical Review* 129(4) (2020): 501–536.
- Retrieved from: https://jfriedmanphilo.github.io/E&Z.pdf (author's preprint, dated 07|2020, marked “Forthcoming in the Philosophical Review. Please cite published version.”)
- Saved: `b980e05c3a1ebc845b19-8b2574081d1c.txt` (extracted text); metadata `b980e05c3a1ebc845b19-8b2574081d1c.json`; original PDF `b980e05c3a1ebc845b19-8b2574081d1c.original.pdf`
- Extraction method (per metadata): Poppler `pdftotext -layout`, page breaks retained, no OCR. HTTP 200, 184,938 bytes, content-type application/pdf.
- **Coverage: full.** Read lines 1–1569 (the entire extracted text, including references), in two reads (1–994, 995–1569).
- Locations used in the essay:
  - ZIP statement, preprint §3 p. 6 / p. 7 of extraction (lines 96–97, 235–236). Published-page attribution “p. 503” is **not** visible in the preprint; I take it from Thorstad 2022 §1, which quotes ZIP as “(Friedman 2020, p. 503)”. This is a corroborated second-hand page locator, not one I verified against the published article.
  - EPa / KPa, preprint §2 (lines 113–117) and §4.1 (lines 564–568).
  - EOa / KOa, preprint §4.2 (lines 715–718).
  - “There may well be parts of inquiry during which we don't quite have a clear question before our minds, but my focus for now is on determinately question-directed inquiry” — preprint pp. 9–10, lines 385–387.
  - “There's a kind of temporal parochialism…What's so special about the moment of belief formation?” — preprint p. 26, lines 1111–1113.
  - Clutter-avoidance disclaimer (irrelevant information “need not be clutter for us”), preprint §4.5, lines 962–975.
  - Grand Central / Chrysler Building case, preprint §2, lines 48–85.

### A2. Friedman, Jane. “Zetetic Epistemology.” In B. Reed and A. K. Flowerree (eds.), *Towards an Expansive Epistemology: Norms, Action, and the Social Sphere*. Routledge.
- Retrieved from: https://jfriedmanphilo.github.io/ZETEP.pdf (preprint dated 04|2020)
- Saved: `5289d4d1264df7925ea4-461a5b3164f9.txt`; metadata `5289d4d1264df7925ea4-461a5b3164f9.json`
- **Coverage: excerpt.** Read lines 1–700 of the extracted text: §1 Introduction, §2 The Course of Inquiry, §3 New Normative Questions (§§3.1 Opening Questions, 3.2 Active Investigation, 3.3 Closing Questions), and the first line of §4. **Not read:** §4 “Old Normative Answers?” onward, and the reference list.
- Locations used:
  - INQUIRY timeline, points A/B/C and phases 1–4, §2 (extraction lines 75–94).
  - “The discussion in this paper is going to be entirely focused on inquiries that have a focal question. That said, I don't mean to be committing to the claim that all inquiry is question-directed in this way.” — §2 n. 1 (lines 114–117).
  - “Q? is on one's research agenda at t iff one has an interrogative attitude towards Q? at t.” — §3.1 (lines 339–340).
  - Ignorance Norm described: “subjects shouldn't both know Q? at t and have an interrogative attitude towards Q? at t”, §3.1 (lines 431–434), attributed by Friedman to her 2017 paper.
  - “Might it come even earlier than A, before S has even really formulated a question they want to answer and is just poking around somewhat more aimlessly? I'm not sure there's a clear answer.” — §3.2 (lines 483–486).
  - Reference to I. J. Good (1967) as possibly relevant to norms for opening questions — §3.1 n. 12 (lines 450–456).
  - Herschel (1831) block quotation and Hintikka's “putting questions to nature” — §2 (lines 228–259, n. 7 at 247–251).
  - Hookway (2006) described as a contemporary precedent for “epistemology as a theory of inquiry” — §2 n. 5 (lines 196–200).

### A3. Peirce, Charles Sanders. “The Fixation of Belief.” *Popular Science Monthly* 12 (November 1877): 1–15.
- Retrieved from: https://arquivo.bocc.ubi.pt/pag/peirce-charles-fixation-belief.pdf (two-column reset of the 1877 text; public domain)
- Saved: `5041c378ded8b4404661-fcbb2a7cb458.txt`; metadata `5041c378ded8b4404661-fcbb2a7cb458.json`
- **Coverage: excerpt.** Read extraction lines 100–279, which cover the end of §II, all of §III, all of §IV, and the opening of §V. **Not read:** §I, most of §II, and §§V(remainder)–VI.
- Locations used (all §IV unless noted): “The irritation of doubt causes a struggle to attain a state of belief. I shall term this struggle inquiry, though it must be admitted that this is sometimes not a very apt designation”; “the sole object of inquiry is the settlement of opinion”; and numbered point 1: “the mere putting of a proposition into the interrogative form does not stimulate the mind to any struggle after belief. There must be a real and living doubt, and without this all discussion is idle.” The method-of-tenacity discussion I rely on in §5.3 of the essay is at the start of §V.
- Note: the two-column reset carries no *Popular Science Monthly* page numbers in the extraction, so my citations are by Peirce's roman-numeral section, not by page.

### A4. Aristotle. *Metaphysics*, Book III (Beta), trans. W. D. Ross.
- Retrieved from: https://classics.mit.edu/Aristotle/metaphysics.3.iii.html (The Internet Classics Archive)
- Saved: `96e35a925f2bd0c85c6d-8874bea01037.txt`; metadata `96e35a925f2bd0c85c6d-8874bea01037.json`
- **Coverage: excerpt.** Read extraction lines 1–119. Most of that is site navigation boilerplate; the substantive text begins at line 107 and I read through line 119, which contains the whole passage I quote. **Not read:** the remainder of Book III.
- Text verified verbatim: “for those who wish to get clear of difficulties it is advantageous to discuss the difficulties well… it is not possible to untie a knot of which one does not know… people who inquire without first stating the difficulties are like those who do not know where they [have to go]”.
- **Accuracy flag.** The retrieved page carries no Bekker numbers. The locator “995a24–33” in draft-001 is supplied from standard reference practice and is **not verified against the retrieved text**. A revision should either drop it in favour of “*Metaphysics* III.1, opening” or verify it against a Bekker-numbered edition.
- A first attempt using `http://classics.mit.edu/...` was refused by the tool for not being HTTPS; the HTTPS retry succeeded.

### A5. Plato. *Meno*, trans. Benjamin Jowett.
- Retrieved from: https://classics.mit.edu/Plato/meno.html (The Internet Classics Archive)
- Saved: `3596a8b0d246a579d565-4b789c61551d.txt`; metadata `3596a8b0d246a579d565-4b789c61551d.json`
- **Coverage: excerpt.** Read four windows of the extracted text: lines 560–629, 740–819, 890–979, plus a WebFetch-generated summary of the whole dialogue. The window at lines 890–979 contains the passages I quote.
- Text verified verbatim: the torpedo-fish simile, including “I perplex others, not because I am clear, but because I am utterly perplexed myself” (line 934–935); Meno's challenge, “And how will you enquire, Socrates, into that which you do not know? What will you put forth as the subject of enquiry? And if you find what you want, how will you ever know that this is the thing which you did not know?” (lines 941–944); and Socrates' restatement, “man cannot enquire either about that which he knows, or about that which he does not know” (lines 947–951).
- **Accuracy flag.** The retrieved page carries no Stephanus numbers. The locators “80c” and “80d” in draft-001 are supplied from standard reference practice and are **not verified against the retrieved text**.

### A6. Thorstad, David. “There Are No Epistemic Norms of Inquiry.” *Synthese* 200(410) (2022).
- Retrieved from: https://www.dthorstad.com/_files/ugd/74503b_1f092eaa7c7942beb5b0d1b6836cff90.pdf (penultimate draft)
- Saved: `47dcb72b138a2289bf89-3a897f492950.txt`; metadata `47dcb72b138a2289bf89-3a897f492950.json`
- **Coverage: excerpt.** Read extraction lines 1–180: abstract, §1 Introduction, and roughly the first five of the six clarifying remarks in §2. **Not read:** §§3–7, including the three arguments in detail and the Gibbardian positive picture. My essay cites only the §1 thesis statement and does not attribute to Thorstad any argument I have not read.
- Locations used: abstract; and §1 opening, “There are no epistemic norms of inquiry. We have no epistemic duties to open inquiry and no epistemic duties to close it.”
- Also used for corroboration of the published page locator for ZIP (§1, quoting “Friedman 2020, p. 503”).
- An earlier attempt at https://philarchive.org/archive/THOTAN-5 returned HTTP 403.

### A7. Thorstad, David. “Norms of Inquiry.” *Philosophical Topics* 51(2) (2023): 135–160.
- Retrieved from: https://www.dthorstad.com/_files/ugd/74503b_990643d44e0346b48512731ed5cf1ae5.pdf
- Saved: `5ce69a5030bdee705924-c0313fbf3a7c.txt`; metadata `5ce69a5030bdee705924-c0313fbf3a7c.json`
- **Coverage: excerpt.** Read extraction lines 1–70: abstract and the opening of §1. **Not read:** §§2–6, i.e. the substance of his reason-responsiveness account.
- Used only for background orientation (that a general account of rational inquiry is a live project, and Thorstad's survey of proposed norms). draft-001 lists it in the bibliography but makes no substantive claim about its content; a revision could either cite it substantively after fuller reading or drop it.

### A8. Woodard, Elise. “Why Double-Check?” *Episteme* 21(2) (2024): 644–667.
- Retrieved from: https://elisewoodard.org/s/Woodard-Why-Double-Check-42222.pdf, which 302-redirected to https://static1.squarespace.com/static/5b48d1e9aa49a1fd7c5f40e1/t/6262e440dae5a73566f0e25e/1650648129059/Woodard+-+Why+Double-Check+4.22.22.pdf (author preprint dated 22 April 2022)
- Saved: `f30b3529bbdc2dcbf030-758b510b1840.txt`; metadata `f30b3529bbdc2dcbf030-758b510b1840.json`. A second metadata stub, `f30b3529bbdc2dcbf030-11b4ecb8d4a6.json`, was reported for the same fetch sequence; I did not read it. **Path caveat:** the hook's path notices arrived interleaved with a concurrent (failed) fetch, so I verified by opening the file and confirming its first line reads “Why Double-Check?∗ / Elise Woodard / April 22, 2022”.
- **Coverage: excerpt.** Read extraction lines 1–120: abstract, §1 Introduction, and the opening of §2.1. **Not read:** §§2.2–5.
- Locations used: the abstract's list of goods sought by double-checking (certainty, epistemic resilience, sensitivity to error); the §1 statement of the Synchronic Compatibility Thesis and paper structure; and the epigraph-style block of opposing quotations in §1, which is where I obtained the Friedman 2017 formulation of the ignorance norm.

### A9. Roussos, Joe. “Awareness Revision and Belief Extension.” Forthcoming in *Australasian Journal of Philosophy*.
- Retrieved from: https://joeroussos.org/wp-content/uploads/2024/03/ARaBE_AJP_Accepted.pdf (pre-copy-editing accepted version)
- Saved: `6c454f0fd03e280247d8-11dbd9f37a3a.txt`; metadata `6c454f0fd03e280247d8-11dbd9f37a3a.json`
- **Coverage: excerpt.** Read extraction lines 1–90: abstract and the opening of §1 Introduction. **Not read:** the formal model in §§2–5.
- Locations used, all §1: “in Bayesian models all resolutions of uncertainty take place by updating pre-existing beliefs. Agents must have priors for propositions to learn about them at later stages and so Bayesianism leaves no room for agents to learn about genuinely new states of affairs”; and the distinction between *awareness revision* and *belief extension*, with the claim that Reverse Bayesianism is a proposal about the latter. My §4 argument relies on exactly these two points and on nothing in the unread formal sections.

---

## B. Cited at second hand (not consulted directly)

These appear in draft-001 with an explicit second-hand marker in the bibliography or in a note.

- **Friedman, Jane. 2017. “Why Suspend Judging?” *Noûs* 51(2): 302–326.** The ignorance-norm formulation quoted in the essay (“If one knows the answer to some question at some time then one ought not to be investigating that question, or inquiring into it further… at that time”, cited to p. 131) is taken from Woodard's §1 quotation block. Note that Woodard's page reference “131” does not match the *Noûs* 51(2) pagination given above; Friedman's 2017 ignorance-norm paper is plausibly a different item in her bibliography. **This is an unresolved citation discrepancy** and must be checked before the essay is treated as accurate. I have flagged it rather than silently repairing it.
- **Good, I. J. 1967. “On the Principle of Total Evidence.”** Known only through Friedman 2020b n. 12. The essay's use is limited to the claim that value-of-information machinery is a live candidate for norms of question-choice, which is what Friedman's note supports.
- **Harman, Gilbert. 1986. *Change in View*.** Known through Friedman 2020a §4.5 and Thorstad 2022 §1 (clutter avoidance).
- **Herschel, John. 1831. *A Preliminary Discourse on the Study of Natural Philosophy*.** Known only as the long quotation in Friedman 2020b §2. **Flag:** it appears in draft-001's bibliography but is not cited in the body; a revision should remove it or use it.
- **Hookway, Christopher (2006, 2007).** Known only through Friedman's citations (2020a nn. 11, 31; 2020b n. 5). Mentioned in draft-001's note 2 as unconsulted.
- **Dewey, *Logic: The Theory of Inquiry*; Collingwood on question and answer; Laudan, *Progress and Its Problems*.** Not consulted. Named in draft-001 note 2 as acknowledged but unread predecessors; no claim about their content is made.
- **Hintikka's interrogative model.** Known only through Friedman 2020b n. 7. Not cited in draft-001.

---

## C. Attempted and unavailable

- **Steele, Katie, and H. Orri Stefánsson. 2021. “Belief Revision for Growing Awareness.” *Mind* 130(520): 1207–1232.** https://philpapers.org/archive/STEBRF-6.pdf — HTTP 403. **Unavailable.** Listed in draft-001's bibliography with an explicit “not consulted directly; access blocked” marker. Roussos was used in its place for the awareness-growth point.
- **de Canson, Chloé. “The Nature of Awareness Growth.”** https://philarchive.org/archive/DECTNO-3 — HTTP 403. **Unavailable.** Not cited.
- **Falbo, Arianna. “The Zetetic.”** https://philarchive.org/archive/FALTZY — HTTP 403. **Unavailable.** This was wanted as a survey of the zetetic turn; its absence means my characterisation of the state of that literature rests on Friedman and Thorstad alone. Not cited.
- **Thorstad, “There Are No Epistemic Norms of Inquiry”** at https://philarchive.org/archive/THOTAN-5 — HTTP 403; obtained instead from the author's site (A6).
- **Friedman, “The Epistemic and the Zetetic”** at https://philosophersannual.org/40articles/friedman-theepistemic.pdf — retrieved and saved as `34ac72d5c70c92660528-08d63533d37f.txt` / `.json`, but **not read**, since it duplicates A1. Recorded here for completeness.
- **Project Gutenberg ebook 25412** (https://www.gutenberg.org/cache/epub/25412/pg25412.txt) was fetched on a guess that it was a Peirce collection. It is in fact C. J. Ellicott, *Addresses on the Revised Version of Holy Scripture* (1901). Saved as `f217f73e02beb3584e8a-cda9dd349193.txt` / `.json`. **Irrelevant; discarded; not used.**

---

## D. Search records (no full-source status)

WebSearch result pages were consulted for locating PDFs only. Their summaries are **not** treated as sources, and no claim in draft-001 rests on them. Queries run: Friedman “The Epistemic and the Zetetic”; Thorstad “There are no epistemic norms of inquiry”; Friedman “Zetetic Epistemology” + ignorance norm; Peirce “The Fixation of Belief” full text; Steele & Stefánsson “Belief Revision for Growing Awareness”; awareness growth + Bayesian conditionalisation; Woodard “Why double-check?”.

---

## E. Accuracy register for the critic

Items a reviewer should check before the manuscript is treated as citation-accurate:

1. Friedman 2017 page locator “131” vs. the *Noûs* 51(2): 302–326 pagination (see §B). Most likely the quotation is from a different Friedman 2017 item in Woodard's bibliography.
2. Bekker locator for the *Metaphysics* III.1 passage (see A4).
3. Stephanus locators 80c/80d for *Meno* (see A5).
4. Mixed pagination in draft-001's Friedman 2020a citations: preprint pages for quoted text, published page 503 for ZIP. Draft note 1 states this, but a revision should normalise to published pagination if the published article can be obtained.
5. Herschel 1831 listed but uncited (see §B).
6. Thorstad 2023 listed on the strength of abstract and §1 only (see A7).
7. No source was obtained for the general remark in draft-001 §2 that anomalies in the sciences are often named before a resolving question can be formulated. It is offered there as a general observation with an explicit disclaimer that no historical claim is being made beyond it. A revision should either support it with a history-of-science source or cut it.
