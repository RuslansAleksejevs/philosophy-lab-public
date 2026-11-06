# Sources — essay-07-revision

This file records what I retrieved and read *in this revision stage*, and what I could not get. I did not inherit the author's or the critic's access claims: every quotation that survives into the final manuscript was re-verified here against a source I read myself, with two flagged exceptions recorded below.

Coverage levels:

- **FULL** — I read the complete extracted text of the original and quoted only from it.
- **PARTIAL** — I read a located portion of the original and quoted only from what I read.
- **SUMMARY ONLY** — I obtained a machine summary of the page, but no saved extraction of the source text. This is not a source; it is flagged wherever relied on.
- **UNAVAILABLE** — retrieval failed or produced no usable text.

Saved-source paths are relative to the task folder `batches/claude10-20260913/tasks/essay-07-revision/`. After each WebFetch the hook performs a separate direct HTTP retrieval and reports paths: `.original.*` is the unmodified downloaded bytes, `.txt` the extraction, `.json` the retrieval metadata. Where the WebFetch summary and the hook's retrieval disagreed — which happened repeatedly, in both directions — I worked from the saved extraction and say so.

---

## FULL access

### 1. Daniel Weltman, "What Makes Requests Normative? The Epistemic Account Defended"

- *Ergo: An Open Access Journal of Philosophy* 9 (2023). DOI 10.3998/ergo.3589. Author at Ashoka University.
- URL retrieved: `https://journals.publishing.umich.edu/ergo/article/id/3589/print/`
- Saved: `sources/8ed8788ba1e22037b487-90eb7a7eb8ba.txt`, `.original.html`, `.json`
- Retrieval metadata (read): HTTP 200, `text/html`, 115,683 bytes, extraction `TEXT_EXTRACTED`, `raw_sha256` beginning `8ed8788ba1e22037b487…`.
- Coverage: **FULL** — 712 lines of extraction, read across body §§1–6.2, all endnotes, acknowledgements and the 43-item reference list.
- Access note: my WebFetch call returned an Anubis bot-challenge page and produced no usable summary. The hook's separate retrieval of the same URL returned the full article. Everything quoted comes from the saved extraction.
- Exact locations used in the manuscript:
  - §6 (conclusion): "requests aren't normative. They are a red herring, normatively speaking."
  - Abstract: "a request does not create any reasons and thus does not have any special normative power."
  - §5.1: "So, when I request something, and someone acts on my request, I am to some extent responsible for this, whereas when someone acts on a wish, I am not." / "This is a big difference."
  - Note 34: "It is also a normatively important difference, but not in the sense of the normativity we are interested in when we ask why requests are normative. Similarly, if I accidentally reveal what cards I am holding in a game of bridge, I am less culpable than if I intentionally do so, but in each case the cards I reveal give my opponents identical reasons to play certain cards in order to win." This is the objection §4 of the manuscript answers, and the bridge analogy is the part I attack.
  - Note 40: "It may technically have normative power insofar as you have more reason to attend to a reason brought to your attention, because (for instance) it would be rude to ignore someone's having brought it to your attention. But this normative power has nothing to do with the request being a request rather than any other action."
  - §5.2: "The epistemic account bites the bullet and says that in cases where requests cause us to attend to something, there is nothing normatively special about the request. The only normative strength is in the reasons that are attended to (which already exist) and the reasons to attend to those reasons (which also exist prior to the request)."
  - §2: the four-item report of Enoch — "X must intend to give Y a reason, communicate this intention to Y, intend Y to recognize this intention, and intend Y's reason to depend on Y's recognition of X's intention (Enoch 2011: 15)" — and "When X robustly gives a reason, this happens via rendering true the antecedent of a conditional along the lines of 'if X asks Y to Z, Y has a reason to Z.'"
  - Note 12: "Gläser classes Enoch, Lewis, and Lance and Kukla together (along with some other views) because they all give what he calls a 'mere addition account' of requests (Gläser 2019: 32)"; and "because Gläser thinks requests do not give reasons, his account is compatible with mine, although I cannot show this here (Gläser 2019: 47)."
  - Note 6: "Because Laskowski and Silver, unlike Cupit, use trust to explain the wrongness of certain requests rather than the normative force of those requests, their account supports the view I defend here (while Cupit's account opposes my view)."
  - §1: Lance and Kukla quoted as holding that "acting as though the request was just evidence of the speaker's psychological desires" is a way of defying a request (Lance & Kukla 2013: 470).
  - Reference list: "Laskowski, N. G. and Kenneth Silver (2021). Wronging by Requesting. In Mark Timmons (Ed.), *Oxford Studies in Normative Ethics* (Vol. 11, 49–69)." This settles the date question the critic raised; I follow Weltman.

### 2. Peter Schaber, "The Reason-Giving Force of Requests"

- *Ethical Theory and Moral Practice* 24:2 (2021), 431–442. DOI 10.1007/s10677-021-10174-8. Open access (CC BY 4.0), University of Zurich. Accepted 16 March 2021.
- URL retrieved: `https://d-nb.info/1233159097/34` (publisher PDF via the Deutsche Nationalbibliothek)
- Saved: `sources/79d7693953f884a2198e-4f6c50255ee0.txt`, `.original.pdf`, `.json`
- Retrieval metadata (read): HTTP 200, `application/pdf`, 265,334 bytes, extraction by `pdftotext -layout`, `raw_sha256` beginning `79d7693953f884a2198e…`. This hash stem matches the one recorded independently by the author and the critic, so all three stages worked from the same bytes.
- Coverage: **FULL** — 588 lines, complete article including all footnotes and references.
- Access note: the WebFetch summary saw only PDF structure and was useless; I read the hook's extraction.
- Exact locations used:
  - §4: "A reason is non-obligatory if it would not be blameworthy for one not to act on it, and obligatory if it would be blameworthy not to act on it," with n. 7: "I am using here the same conception of obligatoriness as Lewis does in his paper." This is the deontic category on which Horn 3 turns.
  - §4: "Requests create non-obligatory reasons in a robust sense. However, they can create obligatory reasons in a non-robust sense, by triggering conditional obligations." Evidence that Schaber's requests already multi-task, which is why the dilemma is an incompleteness argument.
  - §4: "The reasons requests create have always the same weight," and the partner/neighbour diagnosis in terms of "normative weight the request-independent reasons have that are in play in such situations." Verified that Schaber nowhere calls the weight small; my predecessor's "modest" was an interpolation.
  - §3: "They only create reasons if they are respectful with respect to their form as well as their content." The success-condition reading of standing that the manuscript rejects.
  - §2: "Requests are acts of second-personal address."
  - §2, quoting Raz 1986: 36: "It would be wrong to regard requests as mere communication of information … It is possible … to tell a person that, while I would like him to do something for me, I am not asking and am not going to ask him to do it"; and Raz 1986: 37: "This account explains why one might request even when one knows that the other person knows of one's need and of one's desire for help." Both are used in the Disclaimed-Request Test.
  - §2, Schaber's own gloss: John may say "I want you to read my draft (your comments are always so helpful) but I am not going to ask you."
  - §2, quoting Raz 1975: 83: "A person who makes a request intends his making the request to be a reason for the recipient to comply with it."
  - n. 3, quoting Lance and Kukla 2013: 460: "The output of a successful request is that the target now has a specific sort of reason to do what was requested, but it is essential to the notion of a request that this reason is not an obligation. An imperative has failed in its pragmatic function if the target does not acknowledge that she has an obligation to act as ordered."
  - n. 1: "Gläser, on the other hand, argues that requests do not create additional reasons, they rather put the requestees under an obligation see Gläser (2019: 42)."
  - n. 8: "For other reasons why requests could be duties see Cupit (1994) and also Gläser (2019)." The basis for dropping Cupit from the Weight Model.
  - §5, quoting Lewis 2018: 11, 12: "places sufficient discretionary value"; "these are attitudes that one is not obliged to hold."

### 3. Michael S. Moore, "Requiem for a Concept: Exclusionary Reasons"

- Paper for the Conference in Tribute to the Philosophy of Joseph Raz, Yeoh Tiong Lay Centre for Politics, Philosophy and Law, King's College London, 27 October 2023. Author: Charles R. Walgreen University Chair, University of Illinois.
- URL retrieved: `https://www.kcl.ac.uk/c-ppl/assets/inaugural-lecture-series/michael-s-moore-requiem-for-a-concept-exclusionary-reasons.pdf`
- Saved: `sources/824e56697497b41045d1-51abd5065965.txt`, `.json`
- Coverage: **PARTIAL** — I read §§1–2 and the accompanying footnotes (roughly the first fifth of the lecture), covering the definition, the catalogue of phenomena Raz took exclusionary reasons to explain, and the three-way classification of that catalogue. I did not read §§3–5, where Moore distinguishes senses of the phrase and mounts his own attack, and I make no claim about his conclusion.
- Access note: the WebFetch summary could not decode the PDF; the hook's extraction is clean and is what I read.
- Why it matters: this is the source the earlier stages did not have for the *received* Razian view of requests. Exact locations used:
  - §2: "an exclusionary reason is a reason not to act for certain reasons."
  - §2: "Two such items are threats and requests. Here the concept of an exclusionary reason is useful but not because it is part of the nature of such things to give exclusionary reasons; rather, the concept is illuminating about threats and requests because it is the absence of exclusionary reasons … that is illuminating."
  - §2: "unlike a promise, say, or an order issued by one in authority, a mere request does not preclude one from weighing the pros and cons of doing the action requested." Quoted in the manuscript as "exactly half the story."
  - Notes 27–28: both give "Id., p. 83" — i.e. Raz, *Practical Reason and Norms*, p. 83 — corroborating where Raz discusses threats and requests.
  - Note 2: confirms the existence and title of "Postscript to the Second Edition: Rethinking Exclusionary Reasons" in the 1990 edition, and quotes Raz at p. 196 calling the thesis of the widespread use of exclusionary reasons "the only novel thesis this book advanced."

---

## PARTIAL access

### 4. Christian Piller, "Kinds of Practical Reasons: Attitude-Related Reasons and Exclusionary Reasons"

- In Sofia Miguens, João Alberto Pinto and Carlos E. Mauro (eds.), *Analyses: Proceedings of the 2nd National Meeting for Analytic Philosophy*, Faculdade de Letras da Universidade do Porto, 2006, 98–105. (The critic's correction to the author's "undated author's manuscript" is right; I confirmed the volume, publisher, year and page range by search, and the text itself by retrieval.)
- URL retrieved: `https://www-users.york.ac.uk/~cjp7/Recent%20and%20Forthcoming/Attitude-RelatedReasonsandExclusionaryReasons.pdf`
- Saved: `sources/2e22e3a0e2ced16f449e-336c245e55dd.txt`, `.json`
- Coverage: **PARTIAL** — I read §§1–2 (attitude-related reasons; the exposition of exclusionary reasons, the contrast with outweighing and undermining, and the tired-investor case). I did not read the later sections.
- Access note: the WebFetch summary could not decode the PDF; I read the hook's extraction. The saved stem matches the author's, so we read the same file.
- Exact locations used:
  - §2: "Exclusionary reasons are reasons of a higher level. Raz calls them second-order reasons: 'A second-order reason is any reason to act or to refrain from acting for a reason. An exclusionary reason is a second-order reason to refrain from acting for some reason.' (Raz, 1990, 39)". This is the citation chain the author asked a critic to check; I have now read Piller's text directly and can confirm that Piller says this. I have **not** read Raz's book, so the chain is verified at one remove only, and the manuscript says so.
  - §2, on Raz's first illustrative case: the agent's refusal "is based on a reason not to consider the merits of the offer." This is the sentence the manuscript uses to show that a reason about deliberative *uptake* is doing work inside Raz's own motivating example while being classified as a reason not to act *for* a reason.

### 5. Thomas Reid, *Essays on the Intellectual Powers of Man*

- Essay I, ch. 8, "Of Social Operations of Mind." First published 1785; edition scanned is the abridgement edited by A. D. Woozley (Macmillan, 1941), where the chapter occupies pp. 48–51.
- URL retrieved: `https://archive.org/stream/essaysontheintel007938mbp/essaysontheintel007938mbp_djvu.txt`
- Saved: `sources/e961713fca60d9562cf9-05202f0e5788.txt`, `.json`
- Coverage: **PARTIAL** — I read Essay I ch. 8 complete (lines 5460–5595 of the extraction, from the chapter heading to the start of Essay II), plus surrounding context. I did not read the rest of the work.
- Access note: the WebFetch summary saw only the editor's front matter; I read the saved extraction at the relevant offset. My line numbers coincide with those reported by both earlier stages, so all three worked from the same scan.
- Verification performed — every Reid quotation used in this stage was checked word by word against the extraction: "such operations as necessarily suppose an intercourse with some other intelligent being"; the list beginning "when he asks information, or receives it"; "They suppose understanding and will; but they suppose something more which is neither understanding nor will; that is, society with other intelligent beings"; "To ask a question is as simple an operation as to judge or to reason; yet it is neither judgment nor reasoning, nor simple apprehension, nor is it any composition of these"; and "in the divisions that have been made of the mind's operations, the social have been omitted, and thereby thrown behind the curtain."
- Also read and used in the longer versions of the manuscript: "In all languages the second person of verbs, the pronoun of the second person, and the vocative case in nouns, are appropriated to the expression of social operations of mind." The critic noted this passage as unused by the author; I used it in `final-001` and cut it in the condensations for length.
- Caveats carried forward honestly: this is an abridged edition (the editor's footnote confirming that ch. 7 was omitted is present in the scan), the pagination is Woozley's rather than that of the standard editions, and the text is uncorrected OCR of a 1941 printing. I normalised nothing beyond line-break hyphenation when quoting.

### 6. Daniel Whiting, "Against Second-Order Reasons" — repository record

- *Noûs* 51:2 (June 2017), 398–420. DOI 10.1111/nous.12138. ISSN 1468-0068.
- URL retrieved: `https://eprints.soton.ac.uk/383023`
- Saved: `sources/b12b4cb2fd4bc6208aa8-ccd0c43f7be8.txt`, `.original.html`, `.json` (HTTP 200, `text/html`, 33,216 bytes)
- Coverage: **PARTIAL** — I read the University of Southampton repository record, which supplies the complete abstract and full bibliographic details. I did **not** read the article. No full text was available from the record.
- Location used: the abstract, which states that the paper "explores the idea that there are second-order normative reasons (not) to φ for or on the basis of certain first-order normative reasons," and that Whiting challenges "the view that there are second-order reasons so understood." I use this for two things only: that the positive/negative pairing is the standard framing of the category (so my predecessor's claim that the positive species is unnamed was wrong), and that the coherence of the category is under live attack.
- Access note: my WebFetch call to this URL returned HTTP 403; the hook's separate retrieval returned HTTP 200 with the record. This asymmetry recurred and is worth recording as a methodological fact.

---

## SUMMARY ONLY — flagged, and treated as less than a source

### 7. Kenta Sekine, "In Defence of Second-Order Reasons"

- *Canadian Journal of Law & Jurisprudence* 39:1 (February 2026), 200–223. DOI 10.1017/cjlj.2026.10062. Open Access, CC BY 4.0. Author at University College London.
- URL attempted: `https://www.cambridge.org/core/journals/canadian-journal-of-law-and-jurisprudence/article/in-defence-of-secondorder-reasons/D56F92244ED38017F40338C7869A9121`
- The WebFetch tool returned a substantive machine summary of the article; the hook's separate direct retrieval of the same URL **failed**, and the hook recorded "Direct source download unavailable." There is therefore **no saved extraction** of this article in my source folder, and I did not read its text.
- Further attempts: `https://philarchive.org/archive/SEKIDO` (HTTP 403 from WebFetch, no usable hook retrieval) and `https://philpapers.org/archive/SEKIDO.pdf` (HTTP 403).
- What I take from the summary, and no more: that Sekine defines second-order reasons as "reasons to act (or not to act) for certain reasons," that positive ones support acting for particular first-order reasons; that he offers a fourfold typology of positive second-order reasons along two dimensions (whether basic and further values coincide; whether the relation is contingent or constitutive); and that he reconstructs Whiting's Credit Argument as a reductio. The manuscript cites him for the *existence and shape* of the typology, never for wording, and note 6 of `final-005` says that I obtained only a machine summary.
- The critic read this article in full and quoted it verbatim. I have not repeated that verification, and I do not rely on the critic's quotation as if it were my own reading. My claim about the category rests on Whiting's abstract, which I did read.

---

## UNAVAILABLE

Each of the following was sought in this stage and could not be read. I used no unauthorised re-uploads; two are noted below specifically because I found them and declined.

1. **Micha Gläser, "The Normative Structure of Request," in M. Timmons (ed.), *Oxford Studies in Normative Ethics* vol. 9 (OUP, 2019), 29–49.** DOI 10.1093/oso/9780198846253.003.0002. This was the critic's first priority and I made four attempts: the legacy Zurich repository page `https://www.zora.uzh.ch/id/eprint/175965/`, the new entities URL `https://www.zora.uzh.ch/entities/publication/d9e181b3-0d11-49b8-b435-f21502d6f299`, a search for an alternative host, and the Oxford Academic chapter route. The Zurich retrievals returned HTTP 200 with a 2,266-byte Anubis proof-of-work challenge page rather than the article; the saved evidence of the block (not a source) is `sources/c74bed4817235a909b70-ee8b13e36389.txt` / `.json` and `sources/17a27bf61815eca534b9-bef4b299abc6.*`. Everything the manuscript says about Gläser comes from Weltman's n. 12 and Schaber's n. 1, both of which I read in full and both of which I quote. Search summaries offered a description of his positive view (Kant, Anscombe on testimony, a principle obliging requester and requestee to harmonise their ends); I did **not** use this, because a search snippet is not a source, and the manuscript makes no claim about the content of his positive account beyond the two published reports.
2. **David Enoch, "Giving Practical Reasons," *Philosophers' Imprint* 11:4 (2011), 1–22.** Not retrieved in this stage; known through Weltman §2 and Schaber §6, which agree except on the condition-count, a discrepancy the manuscript notes.
3. **James H. P. Lewis, "The Discretionary Normativity of Requests," *Philosophers' Imprint* 18:20 (2018), 1–16.** Not retrieved; known through Schaber §5 and Weltman §2.
4. **Joseph Raz, *Practical Reason and Norms* (1975; 2nd edn. 1990)** and ***The Morality of Freedom* (1986).** Books, not retrieved. Quoted at 1990: 39 through Piller (whose text I read), and at 1975: 83 and 1986: 36–37 through Schaber (whose text I read). A complete text of *Practical Reason and Norms* is posted on a document-sharing site; I located it and did not use it, following the same policy the author adopted for Lance and Kukla. The postscript at pp. 178ff. is therefore still unread by anyone in this lineage, and the manuscript says so.
5. **Mark Lance and Rebecca (Quill) Kukla, "Leave the Gun; Take the Cannoli!", *Ethics* 123:3 (2013), 456–478.** Not retrieved. The two sentences used are quoted through Schaber n. 3 and Weltman §1, both read in full here.
6. **N. G. Laskowski and Kenneth Silver, "Wronging by Requesting," *Oxford Studies in Normative Ethics* vol. 11 (OUP, 2021), 49–69.** Not retrieved; described only as Weltman reports it.
7. **Geoffrey Cupit, "How Requests (and Promises) Create Obligations," *Philosophical Quarterly* 44 (1994), 439–455.** Not retrieved. Precisely because I have not read him, he is now *removed* from the Weight Model list rather than characterised.
8. **Stephen Darwall, "Authority and Reasons: Exclusionary and Second-Personal," *Ethics* 120:2 (2010), 257–278**, and **Joseph Raz, "On Respect, Authority, and Neutrality: A Response," *Ethics* 120:2 (2010), 279–301.** Not retrieved; no accessible full text found. Bibliographic details confirmed by search. The manuscript cites the exchange to mark an unpaid debt and makes no claim about its arguments.
9. **Benjamin Kiesewetter, "Exclusionary Reasons and the Balancing View of Ought."** `https://philarchive.org/archive/KIEERA` returned HTTP 403 and no hook retrieval. On-topic and not used.
10. **David Shoemaker, "Attributability, Answerability, and Accountability," *Ethics* 121:3 (2011), 602–632.** Not retrieved; bibliographic details confirmed by search. Cited only to gloss my narrower use of "answerability," a point the critic rightly raised.

---

## Material consulted but not treated as a source

- Web-search result summaries were used to locate candidate URLs and to fix bibliographic details (Piller's volume and pagination; Whiting's pages and DOI; Darwall's and Raz's pages; Shoemaker's pages; the Raz postscript's page range; the Gläser DOI). No philosophical claim in the manuscript rests on a search snippet. The one place where a snippet offered substantive content — Gläser's abstract — I deliberately declined to use.
- Binary PDFs written by the WebFetch tool into its own `tool-results` directory (for the Schaber, Piller and Moore retrievals) were not opened; I worked from the hook's saved extractions.
- I did not open the Stanford Encyclopedia or any other reference work.

## Dependency artefacts read

- `batches/claude10-20260913/tasks/essay-07-author/output/draft-001.md`, `sources.md`, `process.md` — all complete.
- `batches/claude10-20260913/tasks/essay-07-critic/output/critique.md`, `sources.md`, `process.md` — all complete. I first attempted `critique-001.md` and `review-001.md`; neither exists, and the reads were declined. The filename is `critique.md`, which the critic's own `sources.md` records.

## Assigned inputs read

- `batches/claude10-20260913/tasks/essay-07-revision/input/task.md`
- `batches/claude10-20260913/tasks/essay-07-revision/input/NEUTRAL_BRIEF.md`
- `batches/claude10-20260913/tasks/essay-07-revision/input/RULES.md`
