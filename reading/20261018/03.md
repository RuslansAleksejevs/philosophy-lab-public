# Perfectly Proportioned, Poorly Informed

*A note on relevance and the value of retained evidence*

A researcher can respond faultlessly to every piece of evidence she has and still manage her evidence badly. Perhaps she destroys a record needed to interpret an impending audit. Her later confidence may then fit the information that remains, although keeping the record would have made her inquiry more accurate. How should we understand this difference?

A tempting test for harmless deletion asks two questions: does the deletion leave my present answer unchanged, and will I still reason correctly from whatever information remains? For an inquiry concerned with just one proposition, passing both tests may seem enough. I show why it is not. A source label can leave present confidence unchanged yet help interpret an anticipated inspection. Deleting it can reduce expected accuracy even when every later probability correctly reflects the surviving evidence.

The point is a limit on an explanation of harmlessness, not a new theory of information loss. The label need not matter as a separate object of curiosity, and retaining it need not prevent any future reasoning mistake. Its relevance lies in how old and new evidence work together on the same question. This gives a reason for retention if expected credal accuracy is admitted as one dimension of inquiry's quality. Whether that reason grounds a fundamental epistemic obligation governing voluntary action is a further question.

## 1. When does an unchanged answer justify deletion?

A *credence* is a degree of confidence, represented here by a number between zero and one. A credence fits the evidence when it equals the probability supported by that evidence. We can assess fit without first deciding whether the agent should have gathered or preserved more evidence.

Now distinguish three questions:

1. Do the agent's present factual credences fit her available evidence?
2. How good is a retention policy for the epistemic quality of her ongoing inquiry?
3. Is choosing that policy permitted or required by fundamental norms of rational action?

These questions can have different answers. An account of the first is not automatically an account of the other two. Dogramaci explicitly distinguishes harmful forgetfulness and defective belief formation from the rationality of a surviving belief. He also uses “epistemic evaluation” narrowly enough to exclude criticism of forgetting itself. My broader assessment of inquiry methods does not, merely by being broader, refute his account of that practice. [Dogramaci 2015, §3.3, pp. 670–671](https://www.sinandogramaci.net/Sinan_Dogramaci/_____files/Dogramaci,%20Forget%20and%20Forgive.pdf).

Consider this proposed answer to the second question:

> For an inquiry into a fixed proposition, deleting a distinction has no epistemic downside if it leaves the current supported credence unchanged and the agent will continue to fit her retained evidence perfectly.

There is a reason to take this test seriously. If a question will be answered just once, preserving its supported probability preserves its present expected accuracy. A detail that changes no answer might therefore be dismissed as irrelevant to that task. The second condition addresses a further worry: perhaps deletion will leave the agent confused, overconfident, or unable to adjust correctly. Requiring perfect later fit rules out those defects. The temptation is to infer that the two checks jointly cover what could matter.

The mistaken step is extending adequacy for answering now into adequacy for continuing the same inquiry. Keeping the proposition fixed does not keep fixed the evidential relations needed to answer it. A later inspection can concern the grounds of the original answer. I will identify both a case in which the proposed test fails and an additional independence condition under which preserving the present probability really is enough. Thus the target is a specific inference about relevance, not the claim that a named philosopher denies all value to information.

An ordinary case in which erasure immediately lowers confidence does not refute this test: it fails the first condition. Nor does a case in which the agent later miscalculates: it fails the second. The example below satisfies both. It grants immediate adjustment to available evidence, so a temporary lag in updating cannot explain the loss either.

## 2. A label with delayed value for one question

A researcher is investigating whether a sealed box contains a blue token. Call that proposition *p*. Blue and red are equally probable. A fair randomizer selects sensor A or sensor B, and the researcher sees the selected sensor's identity and its color report.

A is sound with probability 0.8 and faulty with probability 0.2. Its condition is independent of the token and the selection mechanism. When sound, A reports the color perfectly. When faulty, it produces a fair random report independent of the token. Its overall reliability is therefore

\[
0.8(1)+0.2(0.5)=0.9.
\]

B reports the true color with probability 0.9, symmetrically for both colors. Crucially, **conditional on the token, B's report distribution is independent of A's condition**. Its reliability remains 0.9 whether A is sound or faulty. Selection is independent of the token, A's condition, and report-generating noise. These are stipulations of a finite model, not empirical claims about instruments or human memory.

A scheduled inspection will disclose whether A was sound when the report was made. It reveals only that condition, not the token's color. It does not change the sensors' past behavior.

Suppose the report is blue. Whichever sensor supplied it, the supported credence in *p* is 0.9. The researcher can adopt either policy before selection:

**Keep:** retain the report and the source distinction.

**Erase:** retain the report but completely remove the source distinction.

Both retain the background model and the fact that erasure, if chosen, was applied uniformly. Erase removes not just a displayed name but every accessible clue or source-sensitive conditional state that would identify the selected sensor. It does retain the correct probabilities over the possibilities that remain. Keeping the distinction has no additional storage cost, causes no distraction, and prevents no other useful retention.

Each policy assigns the full conditional probability distribution over the model's possibilities, given its retained information. Thus Erase does not silently keep believing that the source was A or B. It becomes appropriately uncertain about the source and adjusts all factual credences accordingly. Both policies achieve perfect fit in every positive-probability information state, for every proposition in the finite model.

Immediately after erasure, the credence in *p* remains 0.9. Either sensor produces a blue report with probability 0.5. Even conditional on either inspection result, this report leaves the source probabilities equal. The later probabilities are:

| Retained information about the blue report | A was faulty | A was sound |
|---|---:|---:|
| Source A | 0.5 | 1 |
| Source B | 0.9 | 0.9 |
| Source erased | 0.7 | 0.95 |

The erased-source row averages the first two rows with equal weights. A faulty A might have supplied an uninformative report, or B might have supplied a reliable one. A sound A might have supplied a conclusive report, or B might have supplied a merely reliable one. A red report gives the corresponding probabilities for red.

The last row is not irrational. After genuine source loss, acting as though the report definitely came from either sensor would be a mistake. Correct averaging is precisely what fit requires.

Nevertheless, keeping the label improves expected credal accuracy. For a credence *c* in *p*, measure inaccuracy by \((c-X)^2\), where *X* is 1 if *p* is true and 0 otherwise. At the supported credence *c*, expected inaccuracy is \(c(1-c)\). Before inspection, both policies have expected inaccuracy 0.09 for *p*. Afterwards, conditional on the blue report, Keep has expected inaccuracy

\[
0.2\left(\frac{0.25+0.09}{2}\right)
+0.8\left(\frac{0+0.09}{2}\right)=0.07,
\]

whereas Erase has

\[
0.2(0.7)(0.3)+0.8(0.95)(0.05)=0.08.
\]

By symmetry, these are also the unconditional expected losses. The same background model supports both policies' credences and the comparison between their prospects. Keep is better in expectation, not in every outcome. If B incorrectly reports blue about a red token and A fails inspection, Erase's 0.7 is closer to the truth than Keep's 0.9.

Three limitations matter. First, the label is initially irrelevant only to the marginal credence in *p*. It already gives information about the source and joint propositions. The inspection makes its value for the fixed token question visible; it does not create every epistemic difference.

Second, the advantage is for credal accuracy, not every task standard. If the only output is the best color classification, scored simply correct or incorrect, both policies achieve expected correctness 0.9. All blue-report posteriors are at least 0.5, so the label does not improve that classification.

Third, marginal reliability alone would not establish the table. If B, like A, were perfect when A was sound and random when A was faulty, both sensors would still be 0.9 reliable before inspection. But afterwards either source would support 1 or 0.5. The label would be redundant and both policies would have expected squared loss 0.05. The conditional independence stipulated above is therefore substantive.

## 3. Why the information loss survives faultless updating

Let *H* be the information before compression, *S* the retained summary, and *Z* the later disclosure. The background model stays available. Set

\[
q=P(p\mid H,Z),\qquad r=P(p\mid S,Z).
\]

Because *S* is a function of *H*,

\[
r=\mathbb E[q\mid S,Z].
\]

The difference in expected squared error is

\[
\mathbb E[(r-X)^2]-\mathbb E[(q-X)^2]
=\mathbb E[(q-r)^2].
\]

To verify it, expand \(r-X=(r-q)+(q-X)\). The cross term has expectation zero because \(\mathbb E[q-X\mid H,Z]=0\). The remaining difference is nonnegative. It is strictly positive when histories merged by the summary support different later probabilities with positive probability. No new information-loss theorem is claimed.

This separates two targets. One is reproducing the answer supported by the full history. The other is responding correctly to the information actually retained. Compression can make the first impossible while leaving the second entirely achievable. A failure to reproduce the full-history answer need not be an updating error. Equally, faultless updating does not recover the lost discrimination.

The proposed deletion test checks that

\[
P(p\mid H)=P(p\mid S).
\]

But, under squared error, preserving expected accuracy after the disclosure requires

\[
P(p\mid H,Z)=P(p\mid S,Z)
\quad\text{with probability one}.
\]

The identity proves this equivalence. The first equality does not imply the second. In the blue-report case, the two histories both support 0.9 now. Yet their responses to a faulty or sound inspection are respectively \((0.5,1)\) and \((0.9,0.9)\). Erasure merges different future responses, not different present answers.

A familiar condition would make the first equality enough: suppose the distribution of the new disclosure, given whether *p* is true, does not further depend on the earlier history. In symbols, \(Z\) is conditionally independent of \(H\) given \(X\). Then Bayes' rule computes the later probability using only the present probability and the two common likelihoods \(P(Z=z\mid X=1)\) and \(P(Z=z\mid X=0)\). Equal present probabilities therefore yield equal later probabilities. This is a sufficient condition, not a necessary one; the exact condition is the second displayed equality.

The inspection in our example lacks that independence. If A reported blue about a red token, A must have been faulty; if B did so, A could still have been sound. The likelihood of the inspection result, conditional on the token, depends on which report history occurred. Preserving the current 0.9 while discarding that dependence loses something needed for further inference about the token itself.

This also explains why the known continuation matters. In an otherwise identical version with no inspection and no further evidence, erasure leaves accuracy for *p* unchanged. With the scheduled inspection, erasure has the calculated cost. No new curiosity about source identities, new proposition to investigate, or new scoring rule is needed to reverse the verdict of harmlessness. The difference concerns a foreseeable use within the original inquiry.

The normative and representational antecedents are close. Pettigrew already evaluates forgetting by expected epistemic value while allowing conditioning on currently possessed evidence and weighing retention costs. His worked example changes credences immediately. The present case instead holds the current answer to *p* fixed and evaluates its continuation. His value-based framework can make that comparison; this is an application, not an objection to it. [Pettigrew 2025, “The value of forgetting” and “An example”](https://richardpettigrew.substack.com/p/the-cost-of-remembering).

Aevyra's criterion requires histories with the same retained representation to agree on the promised future targets. Here both blue-report histories have the same summary, but their inspection-conditioned targets differ. Erase therefore fails that criterion for the full-history targets, although its own evidence-relative answer remains correct. The manuscript specifically treats provenance-sensitive revision and equivalent statistics in place of literal identifiers. [Aevyra 2026, §§4.1–4.3, 6.2](https://aevyra.github.io/ledger-of-will/).

Alvarez develops a related distinction between present prediction and information needed for continued learning, while acknowledging the established ancestry of future distinguishability. Those technical results do not supply the normative premise needed here. [Alvarez 2026, §9](https://arxiv.org/html/2610.13881v1).

These antecedents already establish the broad distinction between a present answer and information for later revision. This note gives that distinction a controlled role in a philosophical explanation: neither present irrelevance to the chosen proposition nor guaranteed future evidential fit establishes harmlessness. The example connects that failed inference to the separate assessment of inquiry and belief. It supplies no new sufficiency theorem, and priority for its combination of conditions is not established.

## 4. From an accuracy difference to a reason for retention

The identity alone does not show that erasure is epistemically objectionable. It becomes such a criticism only if the accuracy difference belongs in the assessment of inquiry. My additional premise is:

> A presently foreseeable improvement in expected credal accuracy within an ongoing inquiry counts in favor of a retention method, in respect of that inquiry's epistemic quality, when it has no relevant cost or competing disadvantage.

This is a local premise, not a general requirement to maximize accuracy. Its rationale has two parts.

First, confidence can answer a question well or badly in its relation to truth, independently of whether it is licensed by the available evidence. A well-supported credence can be false-directed in an unlucky outcome. Evidence-relative permission does not erase that difference. A method's tendency to produce more truthful confidence is accordingly a natural dimension of its quality as a method of inquiry.

Squared error makes that dimension precise without rewarding sharpness by itself. If the supported probability is *a*, expected squared error at an arbitrary credence *c* is

\[
a(1-a)+(c-a)^2.
\]

The supported credence uniquely minimizes it. Thus this measure does not recommend gratuitous certainty or divergence from current evidence. It is *strictly proper*: each supported probability expects itself to perform uniquely best. That is a reason to regard it as an intelligible measure of credal accuracy, not a proof that it is the only permissible epistemic measure.

Second, assessment of an inquiry method can consider which supported probabilities it will enable. If a free, better sensor improves an investigation's expected credal accuracy, that counts in favor of it as an investigative instrument. Preserving the source distinction has the same kind of information-enabling effect. Its value is not merely preserving a name; a different representation that enables the same relevant responses would do. Excluding retention from this comparison just because it occurs before the later beliefs would separate functionally similar contributions to inquiry without explaining why.

This supports a reason to prefer Keep as an inquiry method. It does not settle whether the reason governing the voluntary choice is fundamentally epistemic, fundamentally practical, or derivative on the agent's aim of investigating *p*. No financial or reputational reward is needed to explain the informational advantage. But eliminating such rewards does not eliminate instrumental rationality: an agent can instrumentally pursue accurate inquiry for its own sake.

An instrumentalist can therefore accept the whole comparison while reserving “epistemic rationality” for evidential fit of factual attitudes. On that vocabulary, Keep has greater epistemic value and choosing it has an instrumental justification. The lesson is still that the justification uses an informational benefit not measured by propensity toward fit. It is not a refutation of the instrumentalist's classification.

Someone who denies any epistemic importance to fine-grained credal accuracy can instead restrict the task to categorical classification. For that task, the policies tie. The example supplies no strict reason under that standard alone. My conclusion about unequal epistemic merit is thus conditional on a defended but contestable premise about what matters in the inquiry. It is not smuggled out of a numerical inequality.

Costs can also defeat the retention reason. Keeping a label might displace more important information, violate a legitimate privacy constraint, or impede retrieval. Here these differences are excluded. In practice, their assessment requires evidence, and a larger archive need not yield a better inquiry. The modest principle concerns a known future use and a cheap useful distinction, not every conceivable future question.

## 5. What a fit-based explanation leaves out

The proposed deletion test gives the wrong verdict in the inspection case. Keep and Erase preserve the same present answer and both fit their retained evidence perfectly, but their expected accuracy differs. Given the premise defended in §4, this is a reason against Erase as a method for this inquiry. The reason does not depend on valuing knowledge of the source for its own sake.

A more general completeness claim fails with it: policies equally successful at fitting their retained evidence need not have equal epistemic merit. Call that claim *fit-only completeness*. Both policies assign the supported conditional distribution in every positive-probability retained state. Their actual, expected, and all-inputs success at fit is perfect. The inference is:

1. The policies tie in fit to their respective retained evidence.
2. Keep has better expected credal accuracy for the ongoing inquiry, at no competing cost.
3. That improvement counts in favor of Keep as a method of inquiry.
4. Therefore fit performance does not exhaust this policy comparison.

The first condition of the deletion test does additional work beyond this argument. It blocks the explanation that the loss is simply a worsening of the current answer to *p*. The second blocks the explanation that erasure is bad because it disposes the agent to answer against her evidence. The remaining explanation concerns which well-supported answers the retained information will make possible. An improvement in inquiry need not be an improvement in conformity to its changing evidential standard.

This bears on one component of the exchange between Hedden and Podgorski. Hedden's original time-slice discussion focuses on what one ought to believe and distinguishes that question from basing and agent assessment. [Hedden 2015, §1, n. 3](https://11243971-2fc2-4a01-b59f-e247f0f3c35e.filesusr.com/ugd/0f1e81_e6793e3d37ee403e9af45b0f45805987.pdf). Podgorski questions exhaustive attitude-based assessment and raises the problem of cognitive behavior that changes the evidence against which it is judged. Those are direct antecedents. [Podgorski 2016, §§3, 8, author manuscript](https://www.abelardpodgorski.com/uploads/5/4/0/0/54000997/a_reply_to_the_synchronist.pdf).

Hedden's reply evaluates processes derivatively by their tendency to improve evidential fit. Note 15 explains some fit-preserving belief deletions as lucky results of defective dispositions. Yet he leaves other routes open: instrumental assessment of voluntary deployment, truth-based assessment of processes, and evidence understood as what one is in a position to know. Note 4 also distinguishes a future belief's rationality from its expected accuracy. [Hedden 2016, §2, n. 4; §4, nn. 13–15](https://11243971-2fc2-4a01-b59f-e247f0f3c35e.filesusr.com/ugd/0f1e81_66deef15afa74c87be6935ee9f277371.pdf).

The example therefore gives no reason to attribute fit-only completeness to Hedden. It identifies why the disposition-to-fit explanation, considered by itself, cannot explain this particular disadvantage of Erase. The policy always adjusts correctly within the stipulated model. Broader realistic policies might confuse sources or fail to average, but these additional defects are not needed for the loss. Nor does equal initial sensor reliability make fit accidental. Conditional assignment would preserve fit with unequal reliabilities too, provided the correct background model survived. Equal reliability makes deletion initially invisible specifically for *p*.

An instrumental account can criticize adoption of Erase now, using its expected informational consequences. A truth-directed account can assess retention alongside evidential fit. Both escape fit-only completeness. Neither must make past attitudes directly govern later credences. A reason about future accuracy can be a reason the agent has at the present time.

Schwarz offers a stronger alternative: deteriorating evidence can make proportionality itself the wrong ideal, although resource limitations can justify forgetting. This essay instead grants proportionality throughout and assesses retention separately. Its conclusion requires no verdict that later erased-source probabilities should defy their evidence. [Schwarz 2025, introduction and §8](https://www.umsu.de/papers/disproportionate.pdf).

The result is thus explanatory rather than a refutation of a whole time-slice theory. To explain the loss here, an assessment must consider the accuracy prospects enabled by the evidence, or challenge the stipulated account of what evidence survives. Merely repeating that the agent now fits her evidence, or is disposed to do so, leaves the relevant comparison unanswered.

## 6. Genuine loss and honest limits

**Could a complete Bayesian state preserve the missing information?** Yes. A present marginal for *p* is not the complete state. Retaining the source-sensitive conditional responses can preserve the useful distinction without keeping a literal label. Such compression escapes the objection. Erase is specified to remove those distinctions too. The criticism concerns actual loss, not compression as such.

**What if historical evidence survives forgetting?** A theory may treat past facts as retained evidence even when the agent cannot reconstruct their original sources. Weatherson defends historical evidence and distinguishes rationality of attitudes from wisdom of agents. [Weatherson 2015, introduction and “Evidentialism,” author text](https://brian.weatherson.org/html-papers/posts/2021-02-03-memory-belief-and-time/).

The information partition in the example does not settle that account. If a theory counts the irretrievably lost source identity as evidence still possessed, Erase may fail its fit standard. The main counterexample is conditional on genuine loss from epistemically available information. It is not an argument that every forgotten source must fall outside evidence.

An external-record variant isolates the informational comparison without settling this disagreement. An archive manager selects whether to send a full sensor report or one with its source irreversibly removed. A recipient of the shortened report never possessed the identity. Her correct later confidence can be less accurate in expectation than a recipient's confidence based on the full report. The manager chooses the poorer channel; the recipient has not irrationally forgotten anything. This variant supports the distinction between information quality and response quality, not an unrestricted verdict about the memory of the original researcher.

**Does honest disclosure repair the loss?** No. An additional norm of responsible communication is that a record should not invite a use its information cannot support. That norm does not follow from the squared-error identity. It concerns what users are led to expect, not just the accuracy prospects of the retained state.

A summary might properly report a blue signal with current supported confidence 0.9 while adding that its source, equally likely to have been A or B, has been lost. This supports the last row of the table. It does not support a promise to reproduce whichever full-source row originally applied. If all users already understand the limitation, no extra warning is needed. Erase itself already includes this understanding, so the original comparison involves no misleading presentation.

Aevyra likewise discusses narrowing promised revisions and explicit degradation under a budget. Limitation-reporting is not a new proposal here. [Aevyra 2026, §§4.3, 6.4](https://aevyra.github.io/ledger-of-will/). The example clarifies one consequence: acknowledging lost revision capacity need not lower the current credence. Both sources still support 0.9. Reducing that confidence merely because the label is unavailable would make it less proportioned to the stipulated surviving information.

The appropriate restraint is specific. Do not claim to know how the original grounds would respond to every future disclosure. Continue to assign the confidence the retained information supports. A warning can prevent unsupported use without recovering the lost detail or excusing its avoidable deletion.

## 7. Conclusion

A distinction can leave the present answer unchanged and still deserve retention for the same inquiry. Its value may depend on how a known later disclosure bears on the original grounds. Correctly answering from a shortened record does not establish that shortening the record was harmless.

The sensor example isolates this point without a change of question, a current loss of accuracy for that question, or any later failure to fit the surviving evidence. With expected credal accuracy admitted as part of inquiry's quality, it defeats both the proposed deletion test and fit-only completeness. A theory with instrumental assessment or a richer account of evidence can accommodate the result. The appropriate lesson is to assess retained distinctions against the foreseeable continuation of inquiry, while continuing to assign exactly the confidence that the information actually available supports.

## Bibliography

Aevyra. 2026. *The Ledger of Will: Evidence, Revaluation, and the Preservation of Revisable Agency*. Version 4.0, page dated 25 September. Project-hosted online manuscript. [Text](https://aevyra.github.io/ledger-of-will/).

Alvarez, Robert Jenkinson. 2026. “Prediction Is Not a Sufficient Memory State.” arXiv:2610.13881v1. [Text](https://arxiv.org/html/2610.13881v1).

Dogramaci, Sinan. 2015. “Forget and Forgive: A Practical Approach to Forgotten Evidence.” *Ergo* 2 (26): 645–677. [doi:10.3998/ergo.12405314.0002.026](https://doi.org/10.3998/ergo.12405314.0002.026).

Hedden, Brian. 2015. “Time-Slice Rationality.” *Mind* 124 (494): 449–491. [doi:10.1093/mind/fzu181](https://doi.org/10.1093/mind/fzu181). Consulted excerpt from the author-linked manuscript.

Hedden, Brian. 2016. “Mental Processes and Synchronicity.” *Mind* 125 (499): 873–888. [doi:10.1093/mind/fzv161](https://doi.org/10.1093/mind/fzv161). Consulted §2, note 4, and §4, notes 13–15, in the author-linked manuscript.

Pettigrew, Richard. 2025. “The cost of remembering.” Author essay, 3 February. [Text](https://richardpettigrew.substack.com/p/the-cost-of-remembering).

Podgorski, Abelard. 2016. “A Reply to the Synchronist.” *Mind* 125 (499): 859–871. [doi:10.1093/mind/fzv153](https://doi.org/10.1093/mind/fzv153). [Consulted author manuscript](https://www.abelardpodgorski.com/uploads/5/4/0/0/54000997/a_reply_to_the_synchronist.pdf), §§3, 8; section locators refer to that version.

Schwarz, Wolfgang. 2025. “Dynamic Rationality and Disproportionate Belief.” Author manuscript, June. [Consulted text](https://www.umsu.de/papers/disproportionate.pdf).

Weatherson, Brian. 2015. “Memory, belief and time.” *Canadian Journal of Philosophy* 45 (5–6): 692–715. [doi:10.1080/00455091.2015.1125250](https://doi.org/10.1080/00455091.2015.1125250). [Consulted author text](https://brian.weatherson.org/html-papers/posts/2021-02-03-memory-belief-and-time/), introduction and “Evidentialism”; the author page is dated 1 December 2015.
