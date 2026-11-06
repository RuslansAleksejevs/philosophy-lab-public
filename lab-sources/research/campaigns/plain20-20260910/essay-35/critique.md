# Critique: A Good Measurement Can Be a Bad Test

## Reconstruction and verdict

The argument is sound in its explicit two-sensor case. If X=q+d+e1 and Y=q−d+e2, with independent normal errors of variance s², the average is normal with mean q and variance s²/2 regardless of d. The difference has mean 2d and variance 2s². Keeping only the average therefore preserves estimation of q while destroying the test of d. This proves a useful distinction between an accurate estimate and evidence for all the assumptions used in deriving it.

The strongest reading is deliberately local: agreement cannot discriminate between two specified accounts when those accounts assign the same distribution to the entire evidence being used. The essay does not require theory-free observations, does not demand elimination of every rival, and does not claim that preserving information guarantees a powerful test. Those qualifications protect the core argument.

The manuscript is worth revising. Its main weakness is the gap between an excellent elementary illustration and a substantial new philosophical contribution. Some broader sentences also outrun what the conditional statistical example proves. Revision should sharpen those boundaries rather than add more rhetoric about how surprising the result is.

## Argument and defended premises

1. **Equality conditional on q is not yet unrestricted evidential silence.** The example establishes identical average distributions for fixed q under the two accounts. The broader claim that reports themselves supply no distinction needs background knowledge held fixed as well. Suppose a scientist has independent grounds to associate a large directional effect with high values of q. Learning q from the average can then rationally change confidence in d, despite the average's conditional insensitivity to d. This is not a direct test of cancellation, but it is evidence in a wider model. More generally, a report that is uninformative alone can be informative jointly with another observation. Say explicitly that the no-evidence conclusion concerns the specified comparison with the same q and shared background assumptions, and no extra relation between q and d. The relevant object is all evidence used in that comparison, not each report separately. The existing sentence allowing changes of confidence “for other reasons” does not fully resolve this: a new average can activate an existing background relation.

2. **Physical reliability and warranted trust need their own separation.** At first the reader knows by stipulation that shifts cancel. The investigators may not. The final section repairs this through a revised model and reference checks, but the middle sometimes treats survival of the estimate as survival of the original reason to trust it. If the only original justification for the error bar relied on a now-rejected model, that particular justification can fail even though a later argument vindicates the same numerical result. Distinguish three things: the estimate actually performs well; investigators were justified in trusting it before the discovery; investigators can justify it after the discovery. You need only the first and third to establish that rejecting a model need not require rejecting every value obtained with it. That narrower point is secure and useful.

3. **This does not solve the hardest calibration circle.** The essay assumes q means the same thing in both models and that another method estimates it. That is appropriate for the example, but it removes the question of how investigators establish that two instruments measure a common quantity. Your residual test checks equal response around an already accepted common quantity. It does not test the entire basis for identifying the quantity. Make that limit explicit where you write that a model can help test itself. A source-search lead, Jalloh's calibration paper, addresses common-quantity assumptions directly; its indexed abstract/introduction indicate a nearby debate, but I could not open its full PhilArchive text. You need not add an unverified citation, but should avoid presenting the local result as a general answer to that debate.

4. **Strengthen the best objection: “the model is adequate for its purpose.”** A scientist can accept your calculations yet say that d is irrelevant to a model designed only to estimate q. Calling that model inadequate because it misses d may confuse exact truth with fitness for a task. The essay partly answers this by changing the next scientific question. Give the response explicitly: estimation success warrants the restricted use, while the stronger claim that both sensors lack a directional effect remains unwarranted. This makes the thesis about the scope of claims, not a demand that useful models represent every detail. Gelman and Shalizi already make inference-specific reliability central, so the reply also clarifies your relation to them.

5. **The retention rule has two smaller problems.** In this two-number example, a mean and signed difference retain everything; they do not illustrate economical partial retention. Avoid implying otherwise. Also, the reproducibility paragraph imagines reproducing every average from an algorithm when the inputs no longer exist. An algorithm alone cannot do this. Revise to distinguish rerunning analysis on saved averages from rerunning the original transformation, or specify that a separate audit previously checked the transformation. The intended distinction between repeatable downstream calculation and preserved diagnostic evidence is good.

## Originality, significance and scholarship

The practical problem is significant: summaries can be good products for one scientific task while preventing another. The manuscript makes it unusually easy to see why accurate measurements and mistaken apparatus descriptions can coexist. Its disciplined restriction to specified errors is an advantage.

Originality remains modest and uncertain. [Blocker and Meng, §3.1](https://arxiv.org/html/1309.6790v1) directly precede the information-loss point, and the manuscript acknowledges this honestly. [Gelman and Shalizi, §4.1](https://arxiv.org/html/1006.3868v4) also discuss reliability without full model fidelity, particular errors, and nonidentifiability. Thus moving the warning into philosophy does not by itself establish a new result. The strongest contribution would be a carefully defended account of when trust in a numerical value survives withdrawal of its earlier justification, tied to the limits of cross-instrument agreement. Develop that connection only if you can defend it; otherwise describe the essay as clarification and application, not a new principle.

The Tal attribution is accurate in the selected passages checked: [Tal, model-based account and objectivity discussion](https://www.researchgate.net/publication/383482082_Models_and_measurement) supports model-mediated measurement and context-invariance. The essay appropriately does not say Tal endorses unrestricted inference to model truth. Keep that restraint. I verified selected primary passages, not complete works or every publisher datum. Retrieval details and the inaccessible Jalloh full text are recorded in sources/critic/retrieval-notes.md.

## Concrete language review

The opening is immediately understandable in outline, but “right answer” suggests exact accuracy where the case establishes unbiasedness and unchanged uncertainty:

> “A measuring device can give the right answer while hiding the mistake in the model used to build it. This can happen without fraud, careless work, or an unusually unlucky sample. The same calculation that makes the answer useful can remove the evidence that something is wrong.”

Suggested rewrite: “A measuring device can estimate a quantity accurately even when its designers misunderstand how it works. The calculation that improves the estimate may also hide the designers' mistake.” This states the two tasks directly and removes a list of distractions. The original is not artificial scene-setting.

**Central thesis, opening third paragraph:**

> “Before agreement between a model and a reported measurement counts against a particular possible error, the reporting procedure must preserve some ability to reveal that error.”

“Counts against” and “preserve some ability” force the reader to decode the important claim. Rewrite: “If we use a measurement to argue that a particular error is absent, we must ask whether that error could have changed the evidence we examined.” Then state that this is a necessary condition, not a guarantee of a good test. Incorporate the shared-background limit discussed above.

**What the device reports:**

> “The working model and the alternative therefore predict exactly the same distribution of reported averages, for every fixed value of q.”

“Distribution” has not been explained for a nonspecialist. Rewrite: “Keep q fixed and repeat the measurement. The two accounts predict the same pattern of averages: the same center, the same spread, and the same chances of unusually high or low results.” The normal-error assumptions make this concrete explanation exact here.

**The role of models:**

> “The relevant unit of assessment is a procedure used to support a specified claim, not a procedure considered alone.”

“Relevant unit of assessment” sounds like a committee report. Rewrite: “We must ask what a procedure is being used to show. The same average can test for one error and hide another.” This preserves the core claim and points back to the example.

**Why some agreement says nothing:**

> “Any decision rule based only on those reports must behave in the same way under both. It cannot tend to detect one account while accepting the other.”

“Decision rule” is unexplained, and rules detect errors rather than accounts. Rewrite: “Any test that uses only these reports will reject the first account just as often when it is true as when the second account is true.” This is both simpler and more exact. It applies under the matched assumptions of the example.

**Strongest current objection, final section:**

> “A critic might insist that if the model of the instrument is wrong, its output cannot be a justified measurement of q. Perhaps all we possess is a coincidentally useful number.”

This is already clear. Optional improvement makes the epistemic challenge stronger: “If our reason for trusting the instrument was a mistaken model, why should we still trust its answer? Getting the value right by accident would not be enough.” This avoids attributing an overly sweeping claim to the critic and sets up the distinction between old and new justification.

**Conclusion:**

> “The decisive question for a particular test is whether the route to the report leaves the tested error somewhere to appear.”

The spatial metaphor is readable but “decisive” overstates a necessary condition. Rewrite: “A first question is whether the error could have changed the evidence we used. If it could not, agreement does not test for that error.” Use the qualifications established earlier rather than pretending this is the whole assessment.

## Revision priorities

First restrict evidential silence to the complete, specified comparison and distinguish accurate output from continued justification. Second answer the purpose-relative-model objection and state the common-quantity boundary. Third revise the central thesis and statistical explanations for ordinary readers, then repair the reproducibility example. Finally keep the originality claim modest unless a further defended philosophical result emerges. None of these changes requires padding or a longer essay for its own sake.
