# When a Second Proof Is Not a Second Safeguard

A conclusion can remain rationally believable after one argument for it has failed. Another argument may establish it. Sometimes the new argument can do more: it can help restore warranted trust in the old one. But restoration has a cost when the old argument is then presented as an independent safeguard. If its present certification depends essentially on the new argument, it cannot automatically protect us against losing that very support.

This essay distinguishes three achievements: preserving a conclusion, certifying a particular derivation, and securing a fallback that remains usable if another ground fails. They often occur together, which makes their separation easy to miss. Yet a successful replacement proof can accomplish the first without the second, and can accomplish both without the third. The resulting norm is a constraint on present deductive endorsement: one should not assign an argument more independence than its current warrant supports.

The claim concerns a specific use of logical reasoning, not an irreducible kind of mental state. A *derivation* here is a specified sequence or structure of purported inferences from stated premises. To *endorse* it for a deductive purpose is presently to treat it as establishing its conclusion from those premises. A historical mistake, an unused document and a conjectural heuristic need not be endorsed in this sense. The relevant question is what work the agent is now entitled to make the derivation do.

## 1. Keeping a conclusion while rejecting a derivation

An engineer accepts three premises about a device: either circuit P or circuit Q is active; if P is active, the indicator is lit; and if Q is active, the indicator is lit. The conclusion that the indicator is lit follows by considering the two cases.

Her written derivation instead selects P from the disjunction and applies the conditional about P. She does not introduce P as a temporary supposition inside an argument by cases. She claims to have established it. A colleague supplies the obvious objection: Q could be active while P is inactive.

Assume that P is in fact active and that a reliable measurement independently establishes this. The engineer has good grounds for every proposition she believes. When the colleague explains the proper argument by cases, she also recognizes that the three original premises entail the conclusion. Nothing requires her to abandon belief in the lit indicator. But neither the measurement nor the alternative argument, simply by securing the conclusion, makes her original selection of P valid.

Formally, let Γ = {p ∨ q, p → s, q → s}. In classical propositional logic Γ entails s, but Γ does not entail p. The assignment p false, q true and s true makes every member of Γ true and p false. Independent evidence for p does not eliminate that countervaluation. It can instead justify adding p to the premises of a new argument. The argument by cases offers a different repair: it eliminates dependence on p altogether.

These repairs matter differently when circumstances change. If the measurement becomes unavailable, the argument that adds p loses its observational support, while the argument by cases can remain intact. The corrected conclusion is the same; the resources required to establish it are not.

There is nothing unprecedented about diagnosing the original error. Evershed's invalidity norms restrict deductive methods even when the conclusion has other support. Apply such a norm locally to the transition from the disjunction to p and it gives the appropriate verdict. No additional bridge principle is needed for that diagnosis. The example establishes a distinction on which the further argument relies; it is not itself an advance over his account. [Evershed 2021, §§4–6](https://link.springer.com/article/10.1007/s11229-021-03049-z)

Similarly, MacFarlane explicitly separates proof-rule norms from norms of belief revision. His taxonomy of bridges between consequence and attitudes toward propositions need not be mistaken because it does not settle every question about proofs. The present problem concerns the continuing use of an already accepted derivation: what may an agent retain, reuse or count as corroboration after a challenge? It draws on both projects rather than revealing an oversight in either. [MacFarlane 2004, §§2–3](https://johnmacfarlane.net/normativity_of_logic.pdf)

## 2. Correction and recertification

The engineer's acknowledged invalid step is an objective defect in the displayed derivation. Retaining exactly that step, with exactly its stated premises and deductive role, retains the defect. More confidence in the final conclusion cannot alter this fact. A successful correction changes the derivation, its premises or the interpretation of the challenged step.

Not every challenge has that form. A researcher has a short proof of a theorem and a much longer computer-generated derivation. Her only reason to accept the long derivation as correctly formed was its acceptance by a checker. She then learns that the checker accepted malformed inputs of the relevant kind. She cannot inspect the long derivation herself. Stipulate that this information defeats her present warrant to endorse it, while leaving the short proof untouched. The long derivation happens, in fact, to be correct.

Here no alteration of the derivation is necessary. An adequately trusted second checker might certify the same bytes. An investigation could show that the warning does not apply to this run. Either could restore endorsement of the unchanged derivation. Call this *recertification*, reserving *correction* for changes to the derivation itself. One changes an artifact; the other changes the grounds on which an agent accepts it.

The contrast prevents a misleading generalization from the engineer's case. Independent evidence cannot make an invalid inference valid without changing what inference is being assessed. It can nevertheless restore warrant for a valid inference whose certification had been compromised. Thus the proper requirement is not always to change the old proof. It is to stop endorsing it for the challenged purpose until one has addressed the relevant defect: in the inference, or in one's warrant for accepting it.

This is not a defense of every theory of higher-order defeat. The checker case stipulates a serious loss of warrant for certification. Someone who disputes that loss may reject the application without disputing the distinction between an artifact's correctness and an agent's grounds for endorsing it. Montessori's discussion of defeat in single-premise deduction provides a nearby framework, but his central principle concerns a conclusion believed solely through the deduction. A case with a surviving second ground is not a counterexample to that principle. [Montessori 2026, §1](https://link.springer.com/article/10.1007/s10670-025-01024-5)

Proof correction also has a substantial place in the epistemology of mathematics. Hamami argues that the capacity of competent agents to verify and correct proofs over time matters beyond reliability at a single moment. His account makes correction central to the normative standing of mathematical practice. The issue here is narrower: which later uses of a derivation are supported by the particular way its acceptance has been restored? [Hamami, author preprint, pp.7–9, 11–12](https://www.yacinhamami.com/wp-content/uploads/2020/12/Hamami-Proofs-Reliable-Processes-and-Justification-in-Mathematics-2020-preprint.pdf)

## 3. Can agreement rehabilitate the old proof?

A tempting principle says that a new proof cannot vindicate an old one merely by proving the same conclusion. This is sound as a denial of logical sufficiency: the conclusion's truth does not entail that every derivation of it is correct. But as an epistemic principle it needs qualification. Agreement can provide evidence about how an answer was obtained.

Suppose a checking process is suspected of a specific fault. On an independently warranted account of its behavior, a faulty run is much less likely than a correct run to produce a particular pattern that is subsequently confirmed by a separate calculation. Observing that agreement can increase justified trust in the run. One need not inspect every internal step to learn something about its correctness. A general verification theorem can do still more: a new proof may establish that all derivations satisfying a checkable condition are sound, and the old derivation may satisfy that condition. New reasoning can thereby certify old reasoning wholesale.

The difference is not whether the evidence comes from an independent source. It is whether there is a warranted connection from what the evidence establishes to the challenged certification. An independently measured lit indicator, without any such connection, does not answer the objection to choosing P from a disjunction. By contrast, an appropriate error model connects observed agreement to the probability that the suspected fault occurred. A verification theorem connects an artifact's checkable features to its deductive adequacy.

This gives a substantive way to distinguish mere replacement from recertification. In replacement, the new ground establishes c while leaving the case for endorsing derivation r unresolved. In recertification, there is also a warranted inference from the new information, together with relevant background, to r's adequacy. That inference may be deductive or defeasible. Its strength, assumptions and target must be assessed rather than inferred from the bare fact that both procedures reached c.

The qualification matters. A correct output may be weak evidence about the validity of every internal step, even if it strongly confirms that a computation gave the right answer. The fault under investigation determines what agreement tests. An argument containing an invalid but truth-preserving-in-this-instance step can pass an output test. An agent who needs a reusable deduction must therefore assess support for the derivation, not only support for its answer.

There are now three distinct propositions: c is true; r correctly derives c from Γ; and r is available as support for c independently of another ground a. Evidence can support the first two without establishing the third. That is where the main normative consequence appears.

## 4. The cost of borrowed certification

Return to the two-proof researcher. Let a be the short argument and r the long derivation. After the checker warning, she uses the agreement between r's output and the independently established result of a, together with an appropriate account of the checker, to restore sufficient confidence in r. Assume for the argument that this recertification is reasonable. She now has grounds to endorse both derivations.

It does not follow that she has two independently warranted safeguards against error. Her present grounds for endorsing r include her warrant for a. If that warrant is defeated, the very evidence that rehabilitated r may be compromised. She cannot simply announce that r will protect her against the loss of a while suppressing that dependency.

“Independent” here has a limited epistemic meaning. Ground r is a fallback relative to a specified possible defeat of a when the agent retains adequate warrant to use r after that defeat, holding fixed the other evidence not itself undermined. This is not a claim that the proofs were produced by statistically independent processes, that their texts share no lemmas, or that their authors never communicated. Independence is indexed to a challenge and to the warrant actually available to the agent.

The norm can then be stated precisely: when an agent's warrant for endorsing r depends essentially on an undefeated ground a, she should not endorse r as a fallback against a defeat that removes that essential support, unless she has further grounds sufficient to sustain r's endorsement. Dependence is essential when the remaining grounds, without the challenged contribution of a, are insufficient for the endorsement in question.

Why accept this norm? Endorsing a fallback makes a conditional commitment: it identifies support that remains available under a specified loss. In the case described, that commitment is not met. The same dependency that licenses r in the actual situation removes its license under the envisaged loss. Counting r as a safeguard then overstates what the accepted evidence supports. The error is not that the researcher believes a false theorem. It is that she misjudges the resilience of her reasons.

This is more than the instruction not to count identical evidence twice. There may be two different artifacts, produced by different methods, and both may genuinely be proofs. What is shared is an essential part of the agent's present basis for trusting them. A structurally independent proof can be epistemically dependent in its certification. Conversely, two proofs sharing a lemma may provide distinct safeguards against errors elsewhere. Counting artifacts does not settle either question.

Consider a concrete decision. A team is deciding whether it can archive its short proof without retaining the information needed to check it, on the ground that the long proof supplies a verified backup. If the long proof's present certification rests essentially on agreement with that short proof, the justification for the backup claim is incomplete. A fresh trusted check of the long proof would address the problem. So might a separately secured verification theorem. Repeating that two derivations exist would not.

The norm does not deny that agreement can increase confidence. It also does not forbid mutual support within a broader evidential system. Such support may strengthen the system while failing to provide a fallback against every loss within it. Nor does epistemic dependence automatically imply a probabilistic correlation of a particular magnitude. Claims about increased confidence require their own model; claims about fallback support require surviving warrant. Neither follows simply from the number of proofs.

## 5. Limits and objections

One objection is that the proposed norm is almost definitional. If an alleged fallback fails when the original support is removed, it is not a fallback. That is correct. The philosophical work lies in identifying which dependencies matter and showing that reasonable recertification can create precisely this situation. It is easy to slide from “the second proof is again acceptable” to “we again have independent assurance.” The distinction blocks that inference without denying the first claim.

The result is therefore a diagnostic synthesis, not a new analysis of evidence or an undiscovered logical axiom. It connects familiar facts about invalid inference, basing and proof repair to a specific constraint on certification. Its practical content is a test: specify the anticipated loss, identify what sustains each derivation's endorsement, and ask whether the alleged backup remains warranted under that loss. The test can reveal a deficiency even when all currently endorsed conclusions and derivations are correct.

A second objection concerns the possibility of recertification that does not borrow the short proof's vulnerable support. Suppose a new argument proves a general verification theorem using assumptions untouched by the suspected error in a. That theorem certifies r. Then r may indeed remain available when a fails. The norm permits this. What matters is the particular dependency, not the chronological fact that new reasoning helped certify an old artifact. A new proof can restore a genuinely separate safeguard; it must actually provide warrant that survives the relevant challenge.

A third objection says that the problem is entirely epistemic. The normative force cannot be extracted from logical consequence alone. Again, this is substantially right. Logical facts distinguish the engineer's invalid step from her valid argument by cases. They also identify the assumptions needed by a verification theorem. They do not, by themselves, tell us which checker to trust or how much evidence is sufficient to rehabilitate a derivation. The account combines logical structure with epistemic norms. It does not answer the whole question of why logic is normative for thought.

What it does show is why rational use of deductions cannot be assessed solely by checking whether an agent accepts the right propositions at their endpoints. Her claims about what those deductions can establish, and what can survive a challenge, must also be represented. This is a requirement about the content of an adequate account, not a claim that endorsement cannot be encoded as a belief. One may represent the relevant dependency through beliefs about proofs. The encoding preserves the distinction rather than eliminating it.

Boghossian's discussion of inference connects drawing a conclusion with taking premises to support it. Nothing here requires accepting that as a universal condition on all cognition. In the cases considered, agents explicitly endorse specified derivations for particular purposes; the relevant support commitments are already in view. [Boghossian 2014, §§2–4](https://paulboghossian.com/pb/files/WhatIsInference.pdf)

Finally, no obligation to audit every old inference follows. An agent may shelve a challenged derivation, retain the conclusion on another ground and stop there. She may keep a flawed proof as a heuristic, provided she does not treat it as establishing what it fails to establish. No correction of every historical copy is required merely because a past error occurred. The requirement attaches to present endorsement and the work assigned to it.

A new proof can thus do several different things for an old result. It can preserve belief in the result, justify changing the old derivation, or restore warrant for endorsing the unchanged one. It can even provide a separate safeguard. But that final achievement requires more than restored acceptability. It requires warrant that survives the particular loss against which the safeguard is offered. The resilience of reasoning depends on those relations of support, not on the apparent abundance of proofs.

## References

Boghossian, Paul. 2014. “What is inference?” *Philosophical Studies* 169: 1–18. https://doi.org/10.1007/s11098-012-9903-x.

Evershed, J. W. 2021. “Another way logic might be normative.” *Synthese* 199: 5861–5881. https://doi.org/10.1007/s11229-021-03049-z.

Hamami, Yacin. 2023. “Proofs, Reliable Processes, and Justification in Mathematics.” *British Journal for the Philosophy of Science* 74 (4): 1027–1045. https://doi.org/10.1086/715137. Author-hosted preprint, 2020 URL version, consulted; page citations refer to that preprint.

MacFarlane, John. 2004. “In What Sense (If Any) Is Logic Normative for Thought?” Draft of April 21, 2004, Central Division APA. https://johnmacfarlane.net/normativity_of_logic.pdf.

Montessori, Auke. 2026. “Single Premise Deduction and Defeat.” *Erkenntnis* 91: 2991–3002. First published online October 11, 2025. https://doi.org/10.1007/s10670-025-01024-5.
