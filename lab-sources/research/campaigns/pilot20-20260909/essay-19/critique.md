# Critique of What a Checked Proof Has Not Yet Told Us

## Reconstruction and verdict

The draft distinguishes a valid formal derivation, identification of its formula with an intended theorem, and entitlement to use that theorem. Its central argument is that evidence insensitive to an identified translation error cannot by itself answer that error. The pointwise/uniform convergence example demonstrates how impeccable checking can establish a true proposition under a misleading name. A targeted counterexample or definition inspection addresses the mistake; repeating a derivation check does not.

The example and the restricted argument are sound. The essay is readable, cautious about testimony, and avoids claiming that informal reasoning is intrinsically superior. It merits revision rather than rejection. Its chief weakness is philosophical yield: once all its qualifications are accepted, the main norm risks becoming the truism that relevant evidence must be relevant. A stronger contribution could distinguish warrant for a particular use from warrant for full representational identity. That distinction would also repair an important overstatement.

## Most consequential revisions

### 1. Separate full equivalence from sufficient warrant for an advertised use

The draft sometimes treats correspondence to the intended concept as what must be established before export. But full identity is stronger than many uses require. Suppose a predicate named “uniform convergence” means uniform convergence at a specified exponential rate. It is not equivalent to ordinary uniform convergence: many genuinely uniform sequences fail its extra requirement. Nevertheless, a checked proof of this stronger predicate can warrant the ordinary conclusion by a justified implication. A contrast exposing their nonequivalence would undermine a claim of exact translation while leaving this use entirely secure.

Conversely, even an erroneous pointwise predicate gives enough information for some intended uses: on a finite domain, pointwise convergence implies uniform convergence by taking the maximum of finitely many thresholds. The same quantifier-order mistake that defeats export on [0,1) need not defeat export in that setting. Thus a live difference in interpretation is not yet a live defeater for every use.

Revise the three-claim account to distinguish exact correspondence, sufficient implication for a specific conclusion, and accidental truth of that conclusion. State the norm relative to a proposed inference or use. The challenger should specify what inference fails, not merely exhibit different extensions. This is already suggested by the draft's word “consequential,” but the consequences need to enter the argument rather than remain a qualifier.

### 2. Do not slide from compatibility to evidential neutrality

The opening says a misinterpretation surviving a check as readily as the intended interpretation limits the check's force. Later passages sometimes use the weaker idea that the same success is compatible with both possibilities. Compatibility does not establish equal evidential support. For example, passing a difficult development may be much more likely for a careful team, and careful teams may also be less likely to mistranslate definitions. A success may then reduce rational concern about translation without directly inspecting it.

The draft explicitly concedes this process-reliability possibility. Make that concession control the thesis throughout. Distinguish (a) an operation whose output is stipulated to be unchanged between specified alternatives with relevant background fixed, (b) evidence merely consistent with both alternatives, and (c) a complete audit including human or AI interpretation. Only (a) supports the clean non-discrimination conclusion. No numerical probability model is necessary, but a statement of conditional equal informativeness would prevent an invalid inference.

Also distinguish ruling an alternative out deductively from reducing its credibility enough for warranted reliance. “Excluded,” “answered,” and “discharged” currently move between these standards. A norm for defending a categorical statement that a particular error was checked is easier to justify than a necessary condition on all knowledge.

### 3. State a challenge threshold with a real stopping condition

“Salient, credible, and consequential” does useful work, but is underexplained. A reader could make any familiar definition salient merely by naming a possible typo. The example shows how a challenge can be tested, not what obliges an expert community to spend time answering it.

A defensible narrow rule: a challenge identifies a plausible mismatch in the actual dependency chain, explains which intended inference it threatens, and is not already answered by accessible evidence that the claimant has adequate reason to trust. The response may point to that existing evidence. This preserves testimony and prevents every newly articulated possibility from cancelling settled warrant. Treat this as a proposal requiring defense, not an automatic consequence of the elementary counterexample.

## Originality and significance

The manuscript rightly abandons novelty for the verification/validation distinction. Its existing practical comparator is closer than the draft reports. The math-commons document linked from the README already discusses independently grounded instances, consequences not used as design targets, shared blind spots, and wrong-object counterexamples. See [VERIFICATION_VALIDATION.md](https://github.com/math-commons/formalization-assurance/blob/main/VERIFICATION_VALIDATION.md), “The validation ladder” and “Operational vs categorical specifications.” This makes a claim to novelty for contrasts or dependence awareness especially weak.

The draft can still contribute a clear philosophical account of why assurance must be indexed to a challenge and intended use. But it should present that as the developed argument, identify where it goes beyond practical audit advice, and avoid suggesting that a familiar engineering distinction becomes novel simply by being called epistemic. My focused search does not establish priority or lack of it; engagement with general theories of relevant alternatives and evidential relevance remains a gap. Do not add ornamental citations without reading them.

## Source accuracy and mathematical correctness

[Adams's primary PDF](https://jfr.unibo.it/article/download/4576/5722/17565), §3.1.2, printed p.10, and §4.3, pp.18–19, supports the draft's attribution concerning wrong statements and dependency review. The DOI open failed, but the direct PDF succeeded.

[Avigad's manuscript](https://www.andrew.cmu.edu/user/avigad/Papers/understanding2.pdf), §3.1, supports the claim about recognizing mathematical and logical structure. Correct the reference locator: the concluding explicit claim appears on manuscript p.9, not pp.7–8. It is background here and does not independently support the proposed norm.

The convergence calculations are correct. Choosing positive n avoids division by zero, and the constructed x defeats any threshold. No mechanized demonstration is claimed or needed for this conceptual example. Clarify at the start that f is a proposed limit, since “have limit f” anticipates the property being discussed.

## Readability and precise editorial advice

Keep the early statement of the question and the single substantial mathematical example. Display the two quantifier orders compactly alongside the prose if helpful; do not add another lengthy teaching section. “Export,” “interpretive assurance,” and “naked fact of derivability” can become “use,” “confidence in the translation,” and “successful proof check.” There is no serious artificial scene-setting.

The closing section and several objection replies repeat that evidence must address the remaining question. Trim those repetitions and use the space to defend the use-relative distinction and challenge threshold. Do not expand to the word ceiling. The strongest revised essay would explain a narrower result with sharper conditions, not advertise a universal new requirement.

## Boundaries

I reviewed only this essay's question, source assessment, source notes and draft, plus neutral campaign instructions. I independently accessed the specified primary passages and additional math-commons documentation; no comprehensive literature review, empirical study, proof-assistant run, judge impersonation or final independent review was performed. This critique is an AI contribution to this essay only. Retrieval coverage and discovery gaps are preserved in sources/critic/retrieval-notes.md.
