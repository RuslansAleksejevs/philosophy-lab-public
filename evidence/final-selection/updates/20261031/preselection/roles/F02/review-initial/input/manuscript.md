# Perfectly Proportioned, Poorly Informed

A researcher can respond faultlessly to every piece of evidence she has and still manage her evidence badly. Perhaps she destroys a record needed to interpret an impending audit. Her later confidence may then fit the information that remains, although keeping the record would have made her inquiry more accurate. How should we understand this difference?

One answer evaluates a cognitive method by its tendency to produce beliefs proportioned to available evidence. This can explain why a fallacious method remains objectionable when it happens to produce a reasonable belief: its success was accidental. But not every information-management defect involves accidental success. A method can systematically fit the evidence it preserves while needlessly reducing what that evidence can accomplish.

I defend a restricted conclusion. Success at fitting retained evidence does not exhaust a policy's merit as a method of truthful inquiry. The example concerns a cheap source label that makes no difference to current confidence in one fixed proposition but matters after an anticipated inspection. Its force depends on admitting expected credal accuracy as one dimension of epistemic merit. It does not establish a fundamental epistemic obligation governing voluntary action, refute every time-slice theory, or require forgotten evidence to control later belief.

## 1. What the proposed reduction would have to explain

A *credence* is a degree of confidence, represented here by a number between zero and one. A credence fits the evidence when it equals the probability supported by that evidence. We can assess fit without first deciding whether the agent should have gathered or preserved more evidence.

Now distinguish three questions:

1. Do the agent's present factual credences fit her available evidence?
2. How good is a retention policy for the epistemic quality of her ongoing inquiry?
3. Is choosing that policy permitted or required by fundamental norms of rational action?

These questions can have different answers. An account of the first is not automatically an account of the other two. Dogramaci explicitly distinguishes harmful forgetfulness and defective belief formation from the rationality of a surviving belief. He also uses “epistemic evaluation” narrowly enough to exclude criticism of forgetting itself. My broader assessment of inquiry methods does not, merely by being broader, refute his account of that practice. [Dogramaci 2015, §3.3, pp. 670–671](https://www.sinandogramaci.net/Sinan_Dogramaci/_____files/Dogramaci,%20Forget%20and%20Forgive.pdf).

The target here is a specific completeness claim:

> If two retention policies are equally successful, actually, expectedly, and across their specified possible inputs, at fitting the evidence each leaves available, they have equal epistemic merit for the ongoing inquiry.

Call this *fit-only completeness*. It is stronger than saying that factual beliefs should fit available evidence. It is also stronger than saying that good inference tends to improve fit. It makes fit performance sufficient for the whole comparison of retention methods.

The claim is worth testing because it extends a familiar explanation of process criticism to evidence management. A policy is allegedly defective because it tends to leave the agent with unsupported attitudes. If that tendency is absent, the explanation has no remaining difference to cite. I do not assume that any particular author endorses the extension in this exhaustive form.

The following example grants immediate adjustment to available evidence. It therefore avoids disputes about whether a finite reasoner can update quickly enough. Its concern is not a transition during which confidence briefly lags behind changing evidence. Its concern is the information that a perfectly adjusted confidence state no longer contains.

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

The normative and representational antecedents are close. Pettigrew already evaluates forgetting by expected epistemic value while allowing credences to be obtained by conditioning on currently possessed evidence. He distinguishes practical from epistemic value and weighs the cost of retention. His example exhibits immediate credal change; the source label here leaves the present token marginal unchanged and becomes useful after inspection. Neither accuracy-based assessment of forgetting nor its coexistence with evidence-relative conditioning is distinctive to this essay. [Pettigrew 2025, “The value of forgetting” and “An example”](https://richardpettigrew.substack.com/p/the-cost-of-remembering).

Aevyra's criterion requires histories with the same retained representation to agree on the promised future targets. Here both blue-report histories have the same summary, but their inspection-conditioned targets differ. Erase therefore fails that criterion for the full-history targets, although its own evidence-relative answer remains correct. The manuscript specifically treats provenance-sensitive revision and equivalent statistics in place of literal identifiers. [Aevyra 2026, §§4.1–4.3, 6.2](https://aevyra.github.io/ledger-of-will/).

Alvarez develops a related distinction between present prediction and information needed for continued learning, while acknowledging the established ancestry of future distinguishability. Those technical results do not supply the normative premise needed here. [Alvarez 2026, §9](https://arxiv.org/html/2610.13881v1).

The proposed contribution is a local philosophical application: a systematic fit-preserving policy can lose expected accuracy for a fixed question through a distinction that its present marginal conceals. That combination tests a particular explanation of process criticism. It does not establish priority for the combination.

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

## 5. The exact limit of the dispositional reply

Fit-only completeness cannot distinguish Keep from Erase by their fit performance. Both assign the supported conditional distribution in every retained state. Their actual, expected, and all-inputs success at fit is perfect. Given the premise defended in §4, their epistemic merit nevertheless differs. The inference is explicit:

1. The policies tie in fit to their respective retained evidence.
2. Keep has better expected credal accuracy for the ongoing inquiry, at no competing cost.
3. That improvement counts in favor of Keep as a method of inquiry.
4. Therefore fit performance does not exhaust this policy comparison.

This is related to the dispute between Hedden and Podgorski, but it does not settle their whole dispute. Hedden's original time-slice discussion focuses on what one ought to believe and distinguishes that question from basing and agent assessment. [Hedden 2015, §1, n. 3](https://11243971-2fc2-4a01-b59f-e247f0f3c35e.filesusr.com/ugd/0f1e81_e6793e3d37ee403e9af45b0f45805987.pdf). Podgorski separately questions exhaustive attitude-based assessment and raises the problem of cognitive behavior that changes the evidence against which it is judged. Those are direct antecedents. [Podgorski 2016, §§3, 8](https://philpapers.org/archive/PODART.pdf).

Hedden's reply allows derivative evaluations of processes by their tendency to improve evidential fit. Note 15 treats a belief deletion that happens to preserve fit as accidentally successful: the agent can still manifest a defective disposition. But the same discussion explicitly permits other routes. Voluntary deployment is governed by instrumental rationality; note 14 considers process norms grounded separately in truth; note 15 also considers evidence as what one is in a position to know. These qualifications prevent treating the derivative-fit proposal as his exhaustive account of every retention choice. [Hedden 2016, §4, nn. 13–15](https://11243971-2fc2-4a01-b59f-e247f0f3c35e.filesusr.com/ugd/0f1e81_66deef15afa74c87be6935ee9f277371.pdf).

The case blocks the lucky-success explanation for the stipulated policy. Erase always adjusts correctly. Broader realistic policies might confuse sources or fail to average. Such failures would yield additional criticisms, but they are not needed for this loss. Nor does equal initial sensor reliability make the policy's fit accidental. Conditional assignment would preserve fit with unequal reliabilities too, provided the correct background model survived. Equal reliability makes the loss initially invisible specifically for *p*.

An instrumental account can criticize adoption of Erase now, using its expected informational consequences. A truth-directed account can assess retention alongside, rather than through, evidential fit. Both escape fit-only completeness. Neither must make past attitudes directly govern later credences. A reason about future accuracy can be a reason the agent has at the present time.

Schwarz offers a stronger alternative: deteriorating evidence can make proportionality itself the wrong ideal, although resource limitations can justify forgetting. This essay instead grants proportionality throughout and assesses the retention method separately. Its narrower conclusion requires no verdict that the later erased-source probabilities should defy their evidence. [Schwarz 2025, introduction and §8](https://www.umsu.de/papers/disproportionate.pdf).

What remains unestablished is that Hedden endorses fit-only completeness for these policies. The argument diagnoses a limit of the derivative-fit component if extended to cover the entire comparison. A theory that supplements that component has not thereby been refuted.

## 6. Genuine loss and honest limits

**Could a complete Bayesian state preserve the missing information?** Yes. A present marginal for *p* is not the complete state. Retaining the source-sensitive conditional responses can preserve the useful distinction without keeping a literal label. Such compression escapes the objection. Erase is specified to remove those distinctions too. The criticism concerns actual loss, not compression as such.

**What if historical evidence survives forgetting?** A theory may treat past facts as retained evidence even when the agent cannot reconstruct their original sources. Weatherson defends historical evidence and distinguishes rationality of attitudes from wisdom of agents. [Weatherson 2015, introduction and §1, consulted author manuscript](https://philpapers.org/archive/WEAMBA.pdf).

The information partition in the example does not settle that account. If a theory counts the irretrievably lost source identity as evidence still possessed, Erase may fail its fit standard. The main counterexample is conditional on genuine loss from epistemically available information. It is not an argument that every forgotten source must fall outside evidence.

An external-record variant isolates the informational comparison without settling this disagreement. An archive manager selects whether to send a full sensor report or one with its source irreversibly removed. A recipient of the shortened report never possessed the identity. Her correct later confidence can be less accurate in expectation than a recipient's confidence based on the full report. The manager chooses the poorer channel; the recipient has not irrationally forgotten anything. This variant supports the distinction between information quality and response quality, not an unrestricted verdict about the memory of the original researcher.

**Does honest disclosure repair the loss?** No. An additional norm of responsible communication is that a record should not invite a use its information cannot support. That norm does not follow from the squared-error identity. It concerns what users are led to expect, not just the accuracy prospects of the retained state.

A summary might properly report a blue signal with current supported confidence 0.9 while adding that its source, equally likely to have been A or B, has been lost. This supports the last row of the table. It does not support a promise to reproduce whichever full-source row originally applied. If all users already understand the limitation, no extra warning is needed. Erase itself already includes this understanding, so the original comparison involves no misleading presentation.

Aevyra likewise discusses narrowing promised revisions and explicit degradation under a budget. Limitation-reporting is not a new proposal here. [Aevyra 2026, §§4.3, 6.4](https://aevyra.github.io/ledger-of-will/). The example clarifies one consequence: acknowledging lost revision capacity need not lower the current credence. Both sources still support 0.9. Reducing that confidence merely because the label is unavailable would make it less proportioned to the stipulated surviving information.

The appropriate restraint is specific. Do not claim to know how the original grounds would respond to every future disclosure. Continue to assign the confidence the retained information supports. A warning can prevent unsupported use without recovering the lost detail or excusing its avoidable deletion.

## 7. Conclusion

Perfect response to a diminished information state and good management of information are different achievements. The researcher under Erase can do everything her surviving evidence permits while having needlessly reduced the accuracy prospects of her inquiry.

This difference defeats fit-only completeness if expected credal accuracy is admitted as part of inquiry's epistemic merit. It does not establish a fundamental epistemic action norm or defeat a theory that adds instrumental assessment or a richer account of evidence. Before loss, the comparison concerns what information to preserve. After loss, it concerns how to reason from what remains and how to describe its limits. A disposition to meet a moving evidential standard cannot, by that success alone, explain whether the standard should have been diminished.

## Bibliography

Aevyra. 2026. *The Ledger of Will: Evidence, Revaluation, and the Preservation of Revisable Agency*. Version 4.0, page dated 25 September. Project-hosted online manuscript. [Text](https://aevyra.github.io/ledger-of-will/).

Alvarez, Robert Jenkinson. 2026. “Prediction Is Not a Sufficient Memory State.” arXiv:2610.13881v1. [Text](https://arxiv.org/html/2610.13881v1).

Dogramaci, Sinan. 2015. “Forget and Forgive: A Practical Approach to Forgotten Evidence.” *Ergo* 2 (26): 645–677. [doi:10.3998/ergo.12405314.0002.026](https://doi.org/10.3998/ergo.12405314.0002.026).

Hedden, Brian. 2015. “Time-Slice Rationality.” *Mind* 124 (494): 449–491. [doi:10.1093/mind/fzu181](https://doi.org/10.1093/mind/fzu181). Consulted excerpt from the author-linked manuscript.

Hedden, Brian. 2016. “Mental Processes and Synchronicity.” *Mind* 125 (499): 873–888. [doi:10.1093/mind/fzv161](https://doi.org/10.1093/mind/fzv161). Consulted §4 and notes in the author-linked manuscript through archived primary-text extraction.

Pettigrew, Richard. 2025. “The cost of remembering.” Author essay, 3 February. [Text](https://richardpettigrew.substack.com/p/the-cost-of-remembering).

Podgorski, Abelard. 2016. “A Reply to the Synchronist.” *Mind* 125 (499): 859–871. [doi:10.1093/mind/fzv153](https://doi.org/10.1093/mind/fzv153). Consulted excerpts from the advance article version; section locators refer to that version.

Schwarz, Wolfgang. 2025. “Dynamic Rationality and Disproportionate Belief.” Author manuscript, June. [Consulted text](https://www.umsu.de/papers/disproportionate.pdf).

Weatherson, Brian. 2015. “Memory, belief and time.” *Canadian Journal of Philosophy* 45 (5–6): 692–715. [doi:10.1080/00455091.2015.1125250](https://doi.org/10.1080/00455091.2015.1125250). Year follows the publisher's December 2015 issue. Substantive reading used excerpts from the author manuscript; its section locators are not journal pagination.
