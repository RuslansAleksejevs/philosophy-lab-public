# Sources — essay-07-critic, critique of `draft-001.md`

This file records what I actually retrieved and read while verifying the dependency essay, and what I could not get. Coverage levels:

- **FULL** — I read the complete extracted text of the original source (saved locally by the download hook) and quoted from it directly.
- **PARTIAL** — I read a located portion of the original and quoted only from what I read.
- **UNAVAILABLE** — retrieval failed or the extraction was not usable. Where I nevertheless name such a work in the critique, I say through what I know it, and no criticism rests on unread text.

Saved-source paths are relative to the task folder `batches/claude10-20260913/tasks/essay-07-critic/`. The hook performs a separate direct HTTP retrieval after each WebFetch and reports the paths; `.original.*` files are the unmodified downloaded bytes, `.txt` is the hook's text extraction, `.json` is its retrieval metadata. I opened the `.json` metadata for items 1 and 6 below; for the others I record the paths exactly as the hook reported them without claiming to have inspected the metadata.

---

## FULL access

### 1. Daniel Weltman, "What Makes Requests Normative? The Epistemic Account Defended"

- *Ergo: An Open Access Journal of Philosophy* 9 (2023). DOI: 10.3998/ergo.3589. Author affiliation given as Ashoka University.
- URL retrieved: `https://journals.publishing.umich.edu/ergo/article/id/3589/print/`
- Saved: `sources/b827fc24793cc02acf2d-34973b981694.txt` (extraction), `sources/b827fc24793cc02acf2d-34973b981694.original.html`, `sources/b827fc24793cc02acf2d-34973b981694.json`
- Retrieval metadata (read): HTTP 200, `text/html`, 115,683 bytes, extraction `TEXT_EXTRACTED`, `raw_sha256` beginning `b827fc24793cc02acf2d7368…`. Method recorded as "HTML text nodes excluding head/script/style."
- Coverage: **FULL** — 712 lines of extracted text read across two passes (body §§1–6.2, then acknowledgements, all 45 endnotes, and the 43-item reference list).
- Note on access: my WebFetch call against this URL returned an Anubis bot-challenge page and produced no usable summary. The hook's separate direct retrieval of the same URL returned HTTP 200 with the full article. Everything I quote from Weltman comes from the hook's saved extraction, not from the WebFetch summary.
- Exact locations used in the critique:
  - Abstract: "a request does not create any reasons and thus does not have any special normative power."
  - §5.1: "when I request something, and someone acts on my request, I am to some extent responsible for this, whereas when someone acts on a wish, I am not"; "This is a big difference." Used in critique §7(c).
  - Endnote attached to §5.1 (34th note in sequence): "It is also a normatively important difference, but not in the sense of the normativity we are interested in when we ask why requests are normative." Used in critique §7(c) — the single most important unanswered objection I identify.
  - §5.2: "The epistemic account bites the bullet and says that in cases where requests cause us to attend to something, there is nothing normatively special about the request. The only normative strength is in the reasons that are attended to (which already exist) and the reasons to attend to those reasons (which also exist prior to the request)." Verifies the essay's §2 quotation.
  - Endnote 40 (40th in sequence), quoted in full: "It may technically have normative power insofar as you have more reason to attend to a reason brought to your attention, because (for instance) it would be rude to ignore someone's having brought it to your attention. But this normative power has nothing to do with the request being a request rather than any other action." Verifies the footnote on which the essay's whole project is built.
  - §6 Conclusion: "requests aren't normative. They are a red herring, normatively speaking."
  - §2: the four-condition summary of Enoch — "X must intend to give Y a reason, communicate this intention to Y, intend Y to recognize this intention, and intend Y's reason to depend on Y's recognition of X's intention (Enoch 2011: 15)" — and "When X robustly gives a reason, this happens via rendering true the antecedent of a conditional along the lines of 'if X asks Y to Z, Y has a reason to Z.'" Used in critique §9.
  - Endnote on Lewis's account (11th in sequence): "Gläser classes Enoch, Lewis, and Lance and Kukla together (along with some other views) because they all give what he calls a 'mere addition account' of requests (Gläser 2019: 32)"; and "because Gläser thinks requests do not give reasons, his account is compatible with mine, although I cannot show this here (Gläser 2019: 47)." This is the basis of critique §8.1, my highest-priority finding.
  - Endnote on Laskowski and Silver (6th in sequence): "Because Laskowski and Silver, unlike Cupit, use trust to explain the wrongness of certain requests rather than the normative force of those requests, their account supports the view I defend here." Used in critique §10.8.
  - Reference list: "Laskowski, N. G. and Kenneth Silver (2021). Wronging by Requesting. In Mark Timmons (Ed.), *Oxford Studies in Normative Ethics* (Vol. 11, 49–69)." Basis of the date discrepancy noted in critique §9.

### 2. Peter Schaber, "The Reason-Giving Force of Requests"

- *Ethical Theory and Moral Practice* 24:2 (2021), 431–442. DOI: 10.1007/s10677-021-10174-8. Open access (CC BY 4.0), Universität Zürich. Accepted 16 March 2021.
- URL retrieved: `https://d-nb.info/1233159097/34` (publisher PDF via Deutsche Nationalbibliothek)
- Saved: `sources/79d7693953f884a2198e-c62d673ad221.txt` (extraction), plus the `.json` metadata and original PDF reported by the hook at the same stem.
- Coverage: **FULL** — 588 lines of extracted text, the complete article including all 11 footnotes, acknowledgements and the reference list.
- Note on access: as with Weltman, my WebFetch summary was useless (it saw only PDF structure). The hook's separate retrieval produced a clean `pdftotext`-style extraction, which is what I read.
- Exact locations used:
  - §4: "The reasons requests create have always the same weight." Plus the partner/neighbour case and its diagnosis: "The normative difference that obtains between the two has to do with normative weight the request-independent reasons have that are in play in such situations." Verifies the essay's §2 report and grounds critique §2.
  - §4: "A reason is non-obligatory if it would not be blameworthy for one not to act on it, and obligatory if it would be blameworthy not to act on it" (with n. 7: "I am using here the same conception of obligatoriness as Lewis does in his paper"). This is the deontic category the essay never engages; critique §2.
  - §4: "Requests create non-obligatory reasons in a robust sense. However, they can create obligatory reasons in a non-robust sense, by triggering conditional obligations." Grounds critique §1 (Schaber's requests already multi-task).
  - §3: "They only create reasons if they are respectful with respect to their form as well as their content." Used in critique §10.1 on the validity/permissibility conflation.
  - §2, quoting Raz 1986: 36: "It would be wrong to regard requests as mere communication of information … It is possible … to tell a person that, while I would like him to do something for me, I am not asking and am not going to ask him to do it." Verifies the essay's n. 10 and supplies the better test case I propose in critique §7.
  - §2 n. 3, quoting Lance and Kukla 2013: 460: "it is essential to the notion of a request that this reason is not an obligation." Verifies the essay's n. 4.
  - §6, quoting Enoch 2011: 15: conditions (i)–(iii). Verifies the essay's §2 paraphrase.
  - §5, quoting Lewis 2018: 12, 13, 11, 14: "places sufficient discretionary value"; "these are attitudes that one is not obliged to hold"; the Carrie/Anita case. Verifies the essay's §2.
  - n. 1: "Gläser, on the other hand, argues that requests do not create additional reasons, they rather put the requestees under an obligation see Gläser (2019: 42)." Second independent basis for critique §8.1.
  - n. 2, quoting Lewis 2018: 2: "A request is an attempt by an addressor to create and communicate a non-obligatory reason for the addresse(s) to perform an action." (Schaber's text has the typo "addresse(s)"; the essay silently normalises to "addressee(s)".)
  - n. 8: "For other reasons why requests could be duties see Cupit (1994) and also Gläser (2019)." Basis of my objection to classing Cupit as a Weight Model theorist (critique §2).

### 3. Kenta Sekine, "In Defence of Second-Order Reasons"

- *Canadian Journal of Law & Jurisprudence* 39:1 (February 2026), 200–223. DOI: 10.1017/cjlj.2026.10062. Open Access, CC BY 4.0. Author at University College London; funded by AHRC grant 2387877.
- URL retrieved: `https://www.cambridge.org/core/journals/canadian-journal-of-law-and-jurisprudence/article/in-defence-of-secondorder-reasons/D56F92244ED38017F40338C7869A9121`
- Saved: `sources/0c6fe39d533fb4dbe79d-65798475a74d.txt` (extraction, 3,982 lines), `sources/0c6fe39d533fb4dbe79d-65798475a74d.json`
- Coverage: **FULL** — read the abstract, §§1–6 and the reference notes (I read notes 1–45 in the numbered list; the remaining notes are further citations of the same works). The site displayed a "Temporary Disruption" banner but served the complete article text.
- Why it matters: this is the source the author did not have, and it is decisive for T3. Exact locations used:
  - §1: "Like all reasons for action, they think, second-order reasons are either positive or negative: They are either reasons for acting for certain reasons, or reasons against acting for certain reasons." Establishes that "positive second-order reason" is the settled term, contrary to the essay's "has no settled name" (critique §8.2).
  - §3 and Figure 1: the four-type typology (A/B contingent, C/D constitutive) of positive second-order reasons, applied to Markovits's reward-seeker/altruist and Arpaly's Ron/Huck Finn cases. Shows the "empty slot" is furnished.
  - §5: the Pub/Pub\*, School/School\* pairs.
  - n. 3: "Joseph Raz, 'Postscript to the Second Edition: Rethinking exclusionary reasons' in *Practical Reason and Norms*, 2nd ed (Oxford University Press, 1990) 178." Basis of my point that the essay cites the 1990 edition at p. 39 while ignoring the postscript in that very volume (critique §8.2).
  - n. 6: the survey of challenges to second-order reasons, from which I drew the bibliographic details for **Michael S. Moore**, *S. Cal. L. Rev.* 62:3&4 (1989) 827; **Stephen R. Perry**, ibid. 913; **Donald Regan**, ibid. 995; **Larry Alexander**, *Philosophical Topics* 18:1 (1990) 5; **Heidi Hurd**, *Yale L.J.* 100:6 (1991) 1611; **Frederick Schauer**, *Playing by the Rules* (OUP 1991); **Emran Mian**, *Can. J.L. & Jur.* 15:1 (2002) 99; **Stephen Darwall, "Authority and Reasons: Exclusionary and Second-Personal," *Ethics* 120:2 (2010) 257**; **Daniel Whiting, "Against Second-Order Reasons," *Noûs* 51:2 (2017) 398**; **Noam Gur**, *Legal Directives and Practical Reasons* (OUP 2018); Raz's replies in *S. Cal. L. Rev.* 62 (1989) 1153 and *Ethics* 120:2 (2010) 279; and Raz, "Exclusionary Reasons" (SSRN, 2021).
  - n. 6 also supplies the correct publication details for the essay's Piller source: **Christian Piller, "Kinds of Practical Reasons: Attitude-Related Reasons and Exclusionary Reasons," in Sofia Miguens, João Alberto Pinto and Carlos E. Mauro (eds.), *Analyses: Proceedings of the 2nd National Meeting for Analytic Philosophy* (University of Porto Press, 2006), 98.** The essay lists it as an undated author's manuscript; critique §9.
  - n. 11: **N. P. Adams**, *Philosophical Studies* 178:1 (2021) 235; **Sophie Keeling, "Responding to second-order reasons," *Philosophy and Phenomenological Research* 109:3 (2024) 799**; **Ezequiel Monti, "(Really) defending exclusionary reasons," *Jurisprudence* 15:1 (2024) 48**; **Kenneth M. Ehrenberg, "How exclusionary reasons guide," *Jurisprudence* 15:1 (2024) 71**.
- Confirmed absence: the term "inclusionary" does not occur in this article. So Sekine neither supports nor refutes the essay's n. 7 disclaimer about the label; he refutes the claim about the category.

---

## PARTIAL access

### 4. Thomas Reid, *Essays on the Intellectual Powers of Man*

- Essay I, ch. 8, "Of Social Operations of Mind." First published 1785. Edition scanned: the abridged edition edited by A. D. Woozley (Macmillan, 1941); the chapter occupies pp. 48–51 of that edition.
- URL retrieved: `https://archive.org/stream/essaysontheintel007938mbp/essaysontheintel007938mbp_djvu.txt`
- Saved: `sources/2d1fea95a4b6e51e02b5-26c2f439b39a.txt` (extraction), `sources/2d1fea95a4b6e51e02b5-26c2f439b39a.json`
- Coverage: **PARTIAL** — I read Essay I ch. 8 complete (lines 5460–5595 of my extraction, running from the chapter heading to the start of Essay II), plus surrounding context to fix the boundaries. I did not read the rest of the work. My line numbers coincide with those the author reports, which indicates we have the same scan.
- Note on access: the WebFetch summary saw only the editor's preface and could not locate the chapter; I read the saved extraction directly at the relevant offset.
- Verification performed — all four of the essay's Reid quotations are exact:
  - "such operations as necessarily suppose an intercourse with some other intelligent being" — confirmed.
  - "when he asks information, or receives it; when he bears testimony, or receives the testimony of another; when he asks a favour, or accepts one; when he gives a command to his servant, or receives one from a superior; when he plights his faith in a promise or contract" — confirmed verbatim.
  - "They suppose understanding and will; but they suppose something more which is neither understanding nor will; that is, society with other intelligent beings" — confirmed.
  - "To ask a question is as simple an operation as to judge or to reason; yet it is neither judgment nor reasoning, nor simple apprehension, nor is it any composition of these" — confirmed.
  - "in the divisions that have been made of the mind's operations, the social have been omitted, and thereby thrown behind the curtain" — confirmed.
- Also confirmed: the editor's footnote recording that ch. 7 was omitted from the abridgement ("The whole of this chapter has been omitted, as Reid does little in it but confuse psychological with logical divisions"), and the running heads placing the chapter at pp. 48–51. The author's caveats about the abridgement and its pagination are accurate.
- Unused material I noticed: the chapter closes with "In all languages the second person of verbs, the pronoun of the second person, and the vocative case in nouns, are appropriated to the expression of social operations of mind." This would support the essay's second-personal claims and is not quoted.

---

## UNAVAILABLE

Each of the following was sought during this review and could not be read. I used no unauthorised re-uploads.

1. **David Enoch, "Giving Practical Reasons," *Philosophers' Imprint* 11:4 (2011), 1–22.** Attempted `https://quod.lib.umich.edu/cgi/p/pod/dod-idx/giving-practical-reasons.pdf?c=phimp;idno=3521354.0011.004;format=pdf` and the SSRN delivery URL `https://papers.ssrn.com/sol3/Delivery.cfm/SSRN_ID2607025_code357518.pdf?abstractid=2607025&mirid=1`; both returned HTTP 403 with no body. Known to me only through Schaber §6 and Weltman §§1–3, which I read in full. Critique §9 reports the one discrepancy between those two reports.
2. **James H. P. Lewis, "The Discretionary Normativity of Requests," *Philosophers' Imprint* 18:20 (2018), 1–16.** Attempted `https://philarchive.org/archive/LEWTDN` twice; HTTP 403 both times, although a search index shows the PDF's first page ("volume 18, no. 20 – september 2018"), so the file is present and the block is at the server. Known to me only through Schaber §5 and Weltman §2.
3. **Micha Gläser, "The Normative Structure of Request," in M. Timmons (ed.), *Oxford Studies in Normative Ethics* vol. 9 (OUP, 2019), 29–49.** An apparently open-access copy exists in the Zurich repository at `https://www.zora.uzh.ch/server/api/core/bitstreams/84384f2c-57a3-4f7f-8f8c-c7ad297ab67e/content`. The hook's retrieval returned HTTP 200 but the body was an Anubis JavaScript proof-of-work challenge page, not the article. Saved (as evidence of the block, not as a source): `sources/eca3c58bab6a93007f00-fd9f4e7e0797.txt`, `sources/eca3c58bab6a93007f00-fd9f4e7e0797.json` (metadata read: 4,398 bytes, `text/html`, HTTP 200). Everything I say about Gläser in critique §8.1 comes from Weltman's and Schaber's explicit reports, both of which I read in full and both of which I quote. I flagged the ZORA URL in the critique as a lead for the author, explicitly as an untested lead.
4. **Ulrike Heuer, "The Point of Exclusionary Reasons."** Retrieved `https://www.law.columbia.edu/sites/default/files/2023-08/heuer_the_point_of_exclusionary_reasons_1.pdf`; the hook saved a file at `sources/cc786d74c3ba44fd09b6-2200c101fc7c.txt` / `.json`, but the WebFetch extraction returned only PDF stream objects and no readable text, and I did not read the saved extraction. No OCR available. Not relied on anywhere in the critique.
5. **"Varieties of Second-Personal Reason," *Erkenntnis* (2024), DOI 10.1007/s10670-024-00798-4.** `https://link.springer.com/content/pdf/10.1007/s10670-024-00798-4.pdf` returned HTTP 303 to a Springer identity-provider authorisation endpoint; I did not follow the cross-host redirect. A file stem `sources/f06c35c910729aede469-a24cf550b67f` was reported by the hook for the redirect response. Not read, not cited in the critique. I note it here only because it is on-topic and the author may want it.
6. **Stephen Darwall, "Authority and Reasons: Exclusionary and Second-Personal," *Ethics* 120:2 (2010), 257–278**, and **Darwall, *The Second-Person Standpoint* (Harvard, 2006)**. Not retrieved. Located via search (journals.uchicago.edu, PhilPapers `DARAAR`); no accessible full text found. Bibliographic details in the critique come from Sekine's n. 6, which I read. I make no claim about Darwall's arguments beyond the general characterisation that his account explains obligation via second-personal address and accountability — a characterisation I flag in the critique as the reason the author *should* read him, not as a finding about what he says.
7. **Joseph Raz, *Practical Reason and Norms* (1975; 2nd ed. 1990)** and ***The Morality of Freedom* (1986).** Books; not retrieved. I did not independently verify the p. 39 definition the essay quotes through Piller, so the author's flag on that citation chain stands unresolved. I did establish, from Sekine n. 3, that the 1990 edition contains a postscript at p. 178 rethinking exclusionary reasons.
8. **Lance and Kukla (2013); Cupit (1994); Laskowski and Silver (2021/2022); Monti (2021); Mossé (forthcoming); Ullmann-Margalit (1983).** None retrieved by me. Where the critique mentions them it is explicitly through Weltman's or Schaber's quotations, which I read.

---

## Material consulted but not treated as a source

- Web-search result summaries were used only to locate candidate URLs and to fix bibliographic details such as volume, issue and year. No criticism in `critique.md` rests on a search snippet. In particular, a search summary offered a description of Gläser's positive view; I did not use it, and my §8.1 rests entirely on the Weltman and Schaber passages quoted above.
- A search snippet containing the phrase "exclusionary and inclusionary reasons" prompted my check of the Sekine article. Sekine turned out not to use the term. I therefore leave the essay's n. 7 claim about the label's currency unverified in either direction, and say so in the critique.
- Binary PDFs written by the WebFetch tool into its own `tool-results` directory (for the Schaber and Heuer retrievals) were not opened; I worked from the hook's saved extractions.
- I did not read the Stanford Encyclopedia or any other reference work for this review.

---

## Dependency artefacts read

- `batches/claude10-20260913/tasks/essay-07-author/output/draft-001.md` — complete manuscript, 202 lines including all ten endnotes.
- `batches/claude10-20260913/tasks/essay-07-author/output/sources.md` — complete.
- `batches/claude10-20260913/tasks/essay-07-author/output/process.md` — complete.

I first attempted `essay.md` and `essay-001.md`; neither exists, and the read was declined. The manuscript filename is `draft-001.md`, as `process.md` §8 records.

---

## Assigned inputs read

- `batches/claude10-20260913/tasks/essay-07-critic/input/task.md`
- `batches/claude10-20260913/tasks/essay-07-critic/input/NEUTRAL_BRIEF.md`
- `batches/claude10-20260913/tasks/essay-07-critic/input/RULES.md`
