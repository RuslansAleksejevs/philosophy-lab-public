# F02 — Argument and counterexample review

## Outcome and boundaries

**Outcome: potentially defensible, on the draft's explicitly restricted thesis.** The central example and conditional-expectation proof work under the intended joint probability model. They show that perfect fit to surviving evidence does not determine the expected accuracy of a retention policy. The principal unresolved issue is normative: why that difference supplies an *epistemic reason governing the policy*, rather than an epistemic benefit whose pursuit is governed by ordinary instrumental rationality. This is a major argumentative concern, not a demonstrated fatal flaw. No fatal objection to the restricted thesis was found.

I read the entire assigned `author/draft.md`, lines 1–191, including the bibliography at 177–191. All 22 listed input artifacts were SHA256-verified. Verification is not semantic reading: the source ledger was read in full; only the recorded ranges of four assigned source snapshots were consulted. No other review, global context, old role packet, external search, or new retrieval was used. Primary-source assessments below rely on those preserved tool-text excerpts, not publisher-original bytes or full-paper reading. Locations in the draft are physical file lines; primary-source `L` and `P` labels are inherited extraction coordinates, with `P` zero-based and not final journal pagination. `SOURCES_A.json` records the exact boundaries and inherited failed retrievals. No exhaustive novelty claim is made.

## 1. Charitable reconstruction

The thesis is not that forgotten evidence must still control belief, that every detail must be stored, or that time-slice epistemology is false. The draft expressly denies those conclusions (7, 123, 157, 163, 165). Its strongest formulation is:

> A retention policy may be reliably optimal at matching factual credences to the evidence it leaves available, yet needlessly worsen the accuracy prospects of a known ongoing inquiry. Consequently, policy assessment cannot be exhausted by its tendency to produce that kind of evidential fit.

The inferential structure is:

1. Separate the rationality of surviving credences from the quality of evidence management (11–19).
2. Construct Keep and Erase, both assigning the full conditional distribution given their respective retained information, with cost and interference differences excluded (23–57).
3. Show that source identity has no immediate effect on the target credence but matters after the scheduled inspection (35–55).
4. Establish an expected squared-error advantage for Keep: 0.07 against 0.08 (61–74).
5. Generalize the comparison to nested information sets: the expected squared-error difference is `E[(q-r)^2]` (78–97).
6. Conclude that any policy assessment determined solely by success at fitting surviving evidence cannot capture this difference (113–123).
7. Supply a normative bridge: a costless, presently foreseeable accuracy improvement within an ongoing inquiry gives an epistemic retention reason (127–135).
8. Distinguish that retention reason from a separate obligation not to misrepresent the capacities of a lossy summary (137–145, 175).

Steps 2–5 establish a descriptive/formal separation. Step 6 establishes the limitation of a specified evaluative reduction *if* the difference warrants epistemic policy criticism. Step 7 supplies that indispensable normative premise; it does not follow from the probability identity alone.

## 2. Formal checks and strengths

### The intended example checks out

With B's errors independent of A's condition, exact finite enumeration reproduces the table at 47–53: following a blue report, the post-inspection probabilities are `(0.5, 0.9, 0.7)` when A was faulty and `(1, 0.9, 0.95)` when A was sound. The total expected squared errors are exactly `7/100` and `2/25`, a difference of `1/100`. The same calculation holds conditional on a blue report by color symmetry. The preserved `sources/model-check.py` and its output make both assumptions and results inspectable.

The identity at 84–97 is correct: `S` is a function of `H`, so conditioning on `(S,Z)` is a coarsening of conditioning on `(H,Z)`. Since `q` is the latter conditional expectation of `X`, the cross term vanishes. Strict loss occurs precisely when `q` is not almost surely recoverable from `(S,Z)`. Equal present marginals do not entail equal future conditional probabilities. The draft does not commit that fallacy.

### The argument avoids several easy but bad criticisms

- Erase does not blindly retain an obsolete source belief. It correctly marginalizes, and the construction covers all factual propositions in the finite model (43, 55–57).
- The expected advantage is not confused with pointwise truth-closeness (74).
- Preserving a useful conditional structure instead of a literal label counts as preservation, not a counterexample (149–151).
- The local principle is a reason, not an unlimited duty to maximize aggregate accuracy; competing storage demands and costs are allowed (129–135, 165–167).
- The draft acknowledges both the familiar mathematics and antecedent work (99, 153); nothing in this review licenses an originality verdict.
- Its most distinctive explanatory payoff is that a justified warning about future revision need not lower current confidence (141–145).

## 3. Concerns ranked by severity

### A1. Major: the normative/classificatory bridge remains contestable

**Locations:** 59, 103, 123, 127–135, 159–163, 173–175.

A lower expected squared error establishes an epistemic benefit under the chosen metric. It does not, without a further premise, establish a distinctively epistemic reason governing a voluntary retention action. The draft's argument at 133 is that accuracy is the entire basis of the preference and that rewards, reputation, promises, and effects on others can be removed. This is substantive support, but a rival can agree that Keep improves an epistemically valuable outcome while classifying the reason to choose it as an instrumental reason to advance an adopted inquiry. The same rival can regard an instrument as epistemically better without treating its purchase or storage as governed by a fundamental epistemic action norm.

That rival need not deny any probability calculation, recommend Erase, or insist on reduced present confidence. Its position is: factual epistemic rationality is exhausted by evidential fit; action rationality concerns which epistemic benefits to pursue. The absence of monetary or social rewards does not alone exclude this explanation.

**Strongest reply available in the draft:** the thesis concerns epistemic *assessment*, not only fundamental requirements of belief. Keep and Erase can differ in epistemic merit even when an instrumental theory explains the choice. Lines 123 and 163 explicitly permit a present, instrumental explanation. This makes the restricted thesis plausible and considerably narrows the disagreement.

**What would defeat or narrow it:** if 'epistemic reason governing retention' is defined so narrowly that it excludes reasons to advance an inquiry's accuracy, the formal result survives but the proposed epistemic norm is not established. Conversely, if policy merit includes truth-directed instrumental merit, the restricted conclusion follows naturally, but it is no longer a refutation of a theory confined to rationality of factual attitudes. The draft needs a clear account of which of these claims its opponent denies. This is a missing argumentative bridge, not a demand to adopt consequentialism or introduce an unlimited accuracy duty.

### A2. Uncertain, potentially major for dialectical reach: the target must really be a fit-only policy reduction

**Locations:** 107–123, especially 111, 113, 119, 123; 159–163.

The source evidence supports the existence of the derivative-fit strategy. Hedden's *Mental Processes and Synchronicity*, §4, extracted `L321–335` and `L355–371`, describes evaluating reasoning patterns by their tendency to improve evidential fit. Note 15 (`L415–430`) addresses lucky fit after dropping a belief. The draft fairly distinguishes the alternative truth-grounding picture in note 14 (`L384–398`).

However, the same §4 gives ordinary expected-utility/instrumental rationality a role in deciding whether and how to deploy reasoning (`L311–316`; note 13 at `L378–383`), and note 15 also offers a different account of evidence (`L431–439`). These qualifications matter because Keep/Erase are voluntary policies selected in advance, not merely inference forms. A defender can say: derivative fit norms evaluate inference quality, while present instrumental requirements evaluate the choice to destroy useful information. That theory need not demand that *every* criticism of voluntary evidence management pass through fit.

The draft anticipates much of this at 159 and 163, so this is not a charge that it falsely claims to overthrow all of Hedden's position. Rather, its sound counterexample concerns a specially defined exhaustive reduction, and the consulted excerpts alone do not establish that Hedden endorses that reduction for the whole category of epistemic policy assessment.

**What would settle it:** identify an explicit exhaustive claim covering retention policies, or keep the conclusion conditional on that reduction. A fit-only account cannot distinguish these policies by fit; a fit-plus-instrumental account can. If the latter is permitted as one of the essay's own solutions, the case diagnoses a limit of one explanatory component rather than defeats the overall theory.

Podgorski's §§3 and 8 provide a genuine predecessor: see extracted `L94–105` and `L399–413` in the preserved excerpts. His broader argument for diachronic norms is not thereby established, and the draft properly avoids depending on it.

### A3. Minor, but necessary for the displayed derivation: independence of B's errors is underspecified

**Locations:** 25–33, 45–53, 61–74.

The text states that B is 0.9 accurate symmetrically, and that A's condition is independent of token color and sensor selection. It does not explicitly say that B's reliability is independent of A's condition. Marginal 0.9 reliability does not establish the constant 0.9 B row after the inspection. An 'independent inspection' that reports A's condition need not make that condition independent of B's errors.

**Countermodel:** B is perfect when A is sound and a fair random reporter when A is faulty, with its random report generated independently of the token. Its marginal reliability is still `0.8×1 + 0.2×0.5 = 0.9` for either color. A's stipulated independence from token and selector is unchanged, and inspection reveals only A's condition. But after the inspection the blue-report probability is 0.5 for either source when A is faulty, and 1 for either when A is sound. The label is now redundant. Keep and Erase both have expected squared error 0.05.

**Assessment:** this defeats the claim that the displayed table follows from the explicitly listed marginal assumptions alone. It does not defeat the proposed existential counterexample: a B sensor with independent noise is coherent and very plausibly intended. An explicit independence assumption suffices. Severity is minor because the repair adds a natural model specification rather than changes the philosophical argument.

### A4. Minor scope issue: accuracy advantage is not strict for every inquiry standard

**Locations:** 17, 59–74, 123, 129, 133–135, 153.

The example proves a strict advantage for squared-error credal accuracy. It does not prove a strict advantage for every standard of accurately answering the token question. If the inquiry's declared output is only a color classification, scored 1 for correct and 0 for incorrect, both policies have optimal expected success 0.9. After a blue report, all posterior probabilities are at least 0.5; the source label never changes which color is the best answer. Exact enumeration verifies the tie.

**Assessment:** this is a counterexample to an unrestricted claim that Keep necessarily improves every task standard, not to the draft's displayed squared-error claim. The draft explicitly introduces a particular measure (61) and a credence task, so it already has a defensible response. The broader language about answering the same question (133) should be understood relative to that measure. A defender who cares only about correct categorical answers has not been given a strict reason by this numerical comparison alone. Establishing that credal accuracy itself matters is the relevant normative step; requiring a separate proof for every scoring rule would be excessive.

### A5. Minor: the external-record variant preserves the information result but changes the historical objection

**Locations:** 155–157; compare 37–43, 113–119.

A recipient who never acquired the deleted label is in an informationally poorer state, but is not an example of that recipient losing previously possessed evidence. This variant neutralizes disputes about whether a recipient retains historical evidence through memory, while shifting the retention choice to the sender or archive manager. It therefore independently supports the information-management point, not a direct counterexample to every theory of the forgetful person's evidence.

**What would matter:** a historical theory may count earlier evidence as normatively available even when it is computationally irretrievable; then Erase need not satisfy that theory's evidential-fit standard. The draft expressly restricts application to genuine loss (157), which is the appropriate response. The counterexample is conditional on the stipulated notion of availability, not evidence that all memory theories must accept it.

### A6. Minor: the disclosure norm is a separate normative claim, not another consequence of the identity

**Locations:** 137–145, 175.

The mathematics shows which later probability the reduced record supports. It does not by itself entail a communication obligation. That requires an additional premise about not inviting unsupported uses of a record. The draft offers such a rationale at 139 and sensibly exempts already-informed users. Still, Erase already retains its limitations and updates correctly (41–43), so the original case does not itself contain a misleading presentation.

**Assessment:** the disclosure discussion is a valuable corollary about responsible use, but logically independent of the retention comparison. Adequate disclosure can coexist with an avoidably inferior policy. The draft correctly says that a warning does not restore the lost distinction (141); this should remain a separate reason, not a claimed repair of A1.

## 4. What does not defeat the thesis

Several possible objections are already answered or are merely boundary cases:

- If the audit is cancelled, or the retained summary is sufficient for every relevant disclosure, strict future loss disappears. That narrows the norm's antecedent; it is not a counterexample to it (97, 149–151, 165).
- If storage imposes a competing cost, the retention reason can be outweighed (131, 137). The case intentionally excludes that condition.
- In individual outcomes Erase can be closer to the truth. For example, a blue B report about a red token followed by A's faulty inspection gives squared errors 0.81 under Keep and 0.49 under Erase. The draft expressly claims only an expected advantage (74), so this is not a fatal objection.
- Realistic mistakes, distraction, or model uncertainty can reverse a real-world recommendation. They do not make the stipulated exact policy incoherent, and the draft acknowledges these limits (119, 167).
- Adding a full Bayesian state that retains source-sensitive conditional responses eliminates erasure of the relevant information. It changes the case rather than rebuts the loss result (149).

## 5. Reasoned conclusion, with dissent preserved

The strongest established result is a clean non-equivalence: **perfect response to retained information is compatible with avoidable loss of future credal accuracy.** Any evaluation that is invariant whenever evidential-fit performance is identical must miss that loss. The draft earns this conclusion rather than merely asserting that more memory is better.

The principal dissent is also serious: an epistemic benefit of keeping a record may be pursued under ordinary instrumental rationality without extending epistemic requirements beyond beliefs. The draft partly accepts this route, which protects its modest conclusion but weakens a polemical interpretation of its criticism of Hedden. A theory that never claimed exhaustive fit-only assessment is not refuted.

I would therefore retain the essay for further development, not set it aside. The formal model needs an explicit B-independence clause; the philosophical argument needs sharper separation between epistemic policy merit, reasons for voluntary action, and the narrow explanatory reduction being rejected. The valuable remaining insight is that current confidence, future revisability, and honest disclosure can come apart—even when every surviving factual credence is correctly proportioned.
