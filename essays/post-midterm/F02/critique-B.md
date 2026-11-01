# F02 — Review B: literature, source accuracy, contribution boundary

## Assessment

**A defensible, narrow counterexample remains; the literature comparison needs substantial revision.** The manuscript usefully separates faultless response to retained information from the quality of retaining it. Its strongest feature is not a new information-loss theorem or retention norm, but a deliberately systematic case that blocks a particular appeal to accidentally successful reasoning. The principal missing predecessor is Richard Pettigrew's explicit accuracy-based treatment of forgetting. The numerical example also needs one independence assumption made explicit.

I read the complete anonymous draft, including its bibliography (draft.md, lines 1–191), verified every assigned input hash, independently searched, and consulted primary passages. I did not consult another review. Reading and retrieval boundaries are recorded in SOURCES_B.json and sources/. This is a finite audit, not a novelty certification.

## 1. Closest predecessors and what they take off the table

### 1.1 Pettigrew: a missing, directly relevant predecessor

Pettigrew's **“The cost of remembering” (3 February 2025)** explicitly evaluates forgetting by expected epistemic value, distinguishes that value from practical benefits, and weighs retention costs. Crucially, its Iona example stipulates credences obtained by conditioning an ur-prior on the evidence currently possessed: after forgetting, the agent returns to a less informative distribution. Thus evidence-relative conditioning and an accuracy-based objection to forgetting already coexist in the predecessor. It also supplies a Brier-score example. See “Evaluating forgettings,” “The value of forgetting,” and “An example,” especially extracted lines 20–24, 41–48, 53–66. [Primary text](https://richardpettigrew.substack.com/p/the-cost-of-remembering).

**Consequence:** draft §5's modest retention principle should not be presented as an independently distinctive contribution. Its marginally invisible, delayed loss and explicit application against a dispositional fit-reduction remain differences from this consulted example. Add the comparison in §§3–5, not merely a generic acknowledgment of information value. The longer *The Value of Information and the Epistemology of Inquiry* was discoverable, and its author-supplied research abstract explicitly includes forgetting, but repeated full-PDF retrievals failed; I do not claim to have checked that manuscript's complete treatment. [Author's research abstract](https://richardpettigrew.github.io/).

### 1.2 Aevyra: overlap extends beyond the theorem

The attribution at draft line 99 is accurate. Aevyra's §§4.1–4.3 give factorization/fiber conditions for future revision; §6.2 specifically treats equal report texts with different provenance and source withdrawal, allows equivalent statistics instead of literal identifiers, and distinguishes information failure from evaluator failure. §§4.3 and 6.4 also discuss narrowing a promise and explicitly reporting degradation. Consulted locations: lines 181–206, 274–292. [Primary manuscript](https://aevyra.github.io/ledger-of-will/).

**Consequence:** both the current-answer/future-response distinction and much of the honest-limitation proposal in draft §5 have close, already acknowledged antecedents. The essay should map its source-label example to that criterion explicitly: histories with the same report merge, while inspection-conditioned full-history targets differ. What it adds is an argument about the explanatory limits of evidential-fit assessment, not the discovery that provenance can have future epistemic use. The webpage identifies version 4.0, dated 25 September 2026; that is a page-reported date, not an independently established priority history.

### 1.3 Alvarez: related, but not a direct normative predecessor

The citation is real and aptly qualified. The consulted §9 explicitly disclaims inventing future distinguishability/sufficiency; its conclusion concerns evidence needed for continued learning despite equal present predictions. The examples concern specified learning computations, not a theory of epistemic reasons. Its mathematical theorems were not audited in full. Consulted locations: HTML lines 308–334; abstract/version metadata lines 8–28. [Primary preprint](https://arxiv.org/html/2610.13881v1).

**Consequence:** keep the limited comparison. Neither this citation nor its technical vocabulary establishes the essay's normative conclusion. The identity in draft §3 is independently correct and explicitly unoriginal; there is no need to lean on these recent manuscripts as its mathematical authority.

### 1.4 Podgorski and Schwarz: distinguish the broader controversy

Podgorski already separates norms on processes from norms on attitudes (§3) and identifies the moving-evidence problem (§8, PDF pp. 11–12, lines 399–413). The draft acknowledges this predecessor accurately. Its advantage over his time-lag cases is granting immediate, correct adjustment rather than contesting what must be believed during a transition. [Primary paper](https://philpapers.org/archive/PODART.pdf).

Schwarz's *Dynamic Rationality and Disproportionate Belief* (2025), especially the author manuscript's concluding discussion of “Apples,” argues for preserving information against a time-slice view while recognizing resource-sensitive forgetting (PDF pp. 16–18, lines 617–649). His broader project disputes evidential proportionality itself; this essay grants proportionality and evaluates retention separately. This is a relevant alternative, **not** an established anticipation of the sensor argument. Add a short contrast rather than imply that the only alternatives are Hedden's reply and traditional forgotten-evidence cases. [Primary manuscript](https://www.umsu.de/papers/disproportionate.pdf).

## 2. Load-bearing attribution audit

- **Hedden 2015, §1/n. 3:** accurate. The scope distinction between what to believe, basing, and agents is explicit (preprint p. 3, lines 74–86). The draft does not refute that limited project. [Author-linked text](https://11243971-2fc2-4a01-b59f-e247f0f3c35e.filesusr.com/ugd/0f1e81_e6793e3d37ee403e9af45b0f45805987.pdf).
- **Hedden 2016, §4/nn. 14–15:** the draft's summaries are accurate. Note 14 recognizes a separate truth-grounded route; note 15 invokes a lucky fit-preserving belief deletion. But its second half also offers evidence understood as what one is in a position to know (lines 431–439). §4 treats voluntary deployment through instrumental rationality (lines 311–316, 378–383). The draft should acknowledge these passages explicitly, not only n. 14. [Author-linked text](https://11243971-2fc2-4a01-b59f-e247f0f3c35e.filesusr.com/ugd/0f1e81_66deef15afa74c87be6935ee9f277371.pdf).
- **Dogramaci 2015, §3.3, pp. 670–671:** accurate, including the important caveat that his narrow epistemically evaluative practice excludes criticism of forgetting. The essay can use a broader sense of epistemic reason, but should not suggest that identifying an accuracy-related cognitive defect alone defeats his semantic account. Consulted lines 905–952. [Primary text](https://www.sinandogramaci.net/Sinan_Dogramaci/_____files/Dogramaci,%20Forget%20and%20Forgive.pdf).
- **Weatherson, introduction/§1:** accurate about historical evidence and rationality versus wisdom (preprint lines 0–40, 85–110). Relevant prose was checked through the assigned, hash-verified capture after fresh full-text retrieval failed. The bibliography's unresolved publication dating/page range is incomplete rather than a demonstrated attribution error. Do not silently replace preprint pagination with journal pages. [Assigned primary link](https://philpapers.org/archive/WEAMBA.pdf).

**Established attribution error:** none in the inspected load-bearing passages. **Quotation error:** none found; the draft makes no substantive verbatim quotations from these sources. Section locators are generally appropriate, but preprint and final-journal pagination must remain distinguished.

## 3. Does the crucial inference work?

### 3.1 The numerical result works under the intended model

An independent finite enumeration reproduces the table and expected squared losses: Keep = 0.07, Erase = 0.08, gap = 0.01. The conditional-expectation identity is correct because the retained information with the disclosure is a coarsening of the original information with that disclosure. It compares expectations under a common model, not outcome-by-outcome accuracy. See sources/19-check-sensor.py and 20-check-sensor-results.json.

**Make this assumption explicit:** B's report error is independent of A's operating condition, conditional on the token color. The stated marginal 0.9 reliability of B does not alone imply that B stays at 0.9 after inspecting A. “Independent inspection” need not imply independence of sensor errors.

For example, let B also be perfect when A is sound and a fair reporter when A is faulty. B is still 0.9 reliable for either color before inspection, and the stated independences of A's condition from color and source selection still hold. But after inspection both sources support the same probability: 0.5 or 1. Keep and Erase then both have expected loss 0.05. This is an **under-specification under a literal marginal reading**, not an arithmetic refutation of the intended example. One added independence sentence repairs it.

### 3.2 The anti-reduction conclusion is conditional on the evaluative target

The example defeats this specific thesis: every epistemic difference between the policies is exhausted by their success at matching **the information each policy itself leaves available**. Correct conditioning makes both succeed; a separately accepted accuracy reason distinguishes them.

It does not establish that a policy which always fits retained evidence is defective by the fit norm's own lights. Nor does it show that fit norms were intended to exhaust inquiry, agency, and informational quality. The draft largely respects this distinction. It should make the indispensable additional premise explicit: avoidable expected accuracy loss in the ongoing inquiry supplies an epistemic reason, rather than merely a task-relative instrumental reason. Removing money and reputation does not settle every dispute about the boundaries of epistemic normativity.

The external-report variant at line 157 is useful but changes the comparison: the recipient need never have known the erased identity. It cleanly isolates information quality, but a separate claim is needed to locate responsibility for choosing the poorer channel. Do not treat that variant alone as a counterexample about the recipient's irrational forgetting.

### 3.3 Keep the marginal claim narrow

The label has no immediate value **for the marginal credence in p**, not no immediate epistemic value whatsoever. Retaining it already yields more information about the source and joint propositions. Thus the delayed inspection is needed to make its value for this fixed question visible, not to create every epistemic difference between the policies. Draft lines 74, 121, and 153 mostly say the narrower thing; retain those qualifications throughout.

## 4. Required changes and contribution after revision

1. Add Pettigrew as a direct normative predecessor, distinguishing his explicit fit-preserving forgetting example from the delayed, equal-marginal sensor construction.
2. Compare the limitation-reporting proposal with Aevyra's scope/degradation provisions. Do not reserve the overlap acknowledgment for the theorem alone.
3. State B's conditional independence and retain the common-model, expectation-only qualifications.
4. State the narrow reduction being rejected as a claim, and distinguish it from an evidentialist account of permissible beliefs or a synchronic account of choice.
5. Address the source's own evidence-availability and instrumental routes. Clarify what complete deletion is supposed to remove, including recoverable conditional information.
6. Contrast Schwarz briefly; resolve bibliographic details only after checking an accessible final record.

**What remains:** a clear philosophical deployment of familiar information value against a particular dispositional rescue, using a cheap provenance bit whose relevance to a fixed question emerges only after an anticipated audit. The all-inputs fit stipulation sharpens the usual lucky-success discussion. That is a plausible local contribution, not an established new retention norm, new mathematical result, general defeat of time-slice epistemology, or certified priority claim.

## Evidence limits

No complete reading of every cited work is claimed. Primary texts, not surveys or search summaries, ground the substantive comparisons above. Pettigrew's longer manuscript, Blackwell's original full text, final Weatherson metadata, and some direct PDF/page retrievals remained inaccessible. Search results and failed attempts are preserved, including no-match results and shell DNS failures. A returned screenshot reference without visible image bytes was not treated as visual page inspection. Incidental author-page/search biographical material was not used; no CV or biography was intentionally opened. These limits leave the exact priority of the combined argument unresolved.
