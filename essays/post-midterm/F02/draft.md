# Perfectly Proportioned, Poorly Informed

An inquirer can lose something epistemically important without acquiring a single belief that fails to fit the evidence she has. This is easy to accept when a flood destroys her notebooks. It becomes harder to explain when she needlessly destroys the relevant information herself. Perhaps her later beliefs are reasonable, but her way of managing them is not. What makes that criticism epistemic?

One attractive answer evaluates a cognitive policy by its tendency to produce beliefs proportioned to the agent's evidence. A policy may happen to produce a reasonable belief while remaining defective because it usually produces unreasonable ones. This answer handles many lucky successes. I will argue that it does not handle every defect in evidence management. A policy can systematically maintain perfect fit between credence and surviving evidence, while making future credences needlessly less accurate. Its defect need not involve either a current evidential mismatch or a disposition toward one.

The argument concerns a particular reduction of epistemic assessment, not every theory of rationality at a time. It does not establish that forgotten evidence must continue to govern present belief. Nor does it establish that memory should preserve everything. It establishes a gap between two demands: responding well to the information that remains, and retaining information well. I develop that gap through a case in which forgetting leaves present confidence unchanged but removes a distinction that an impending audit will make useful. The case also explains why acknowledging an epistemic limitation need not mean lowering one's current confidence.

## 1. Two questions about memory

Suppose I can no longer recall where I learned that a particular bridge opened in 1932. Must I stop believing it? A requirement to reconstruct every original source would make ordinary knowledge precarious. But suppose I am preparing an account that may need correction if one historical archive proves unreliable. Whether my date came from that archive can matter even if recalling it would add nothing to my present confidence. Forgetting a source raises two questions: what may I believe now, and what future work can the retained information support?

The familiar controversy about forgotten evidence mainly addresses the first question. Dogramaci distinguishes a surviving belief's rationality from defects in the way it was formed and from harmful forgetfulness. He also separates his narrow practice of epistemic evaluation from language that discourages cognitive defects. That distinction prevents criticism of an earlier process from automatically condemning a later belief. [Dogramaci 2015, §3.3, pp. 670–671](https://www.sinandogramaci.net/Sinan_Dogramaci/_____files/Dogramaci,%20Forget%20and%20Forgive.pdf).

The second question concerns the informational setting within which future rationality will operate. A person may respond impeccably to every new item she receives, yet have discarded what she needed to understand its significance. This is not necessarily stubbornness. Sometimes the responsible later response is an average over several possible histories. The loss lies in having to average, not in averaging incorrectly.

Consider a distinction relevant to both questions. A *credence* is a degree of confidence, represented here by a number between zero and one. Call it *proportioned* when it matches what the agent's available evidence supports. This is a standard of evidential fit. Call a retention policy *informationally adequate for a task* when what remains enables the relevant task to be performed to the promised standard. The first assessment takes available evidence as given. The second assesses, among other things, what was allowed to remain available. An informationally inadequate policy need not leave an unproportioned credence behind.

These are not competing definitions of all epistemic goodness. They identify different objects of assessment. Their separation matters because a widely available response to criticism of a process is that the process usually leads to failures of evidential fit. The following case closes off that response.

## 2. A source label worth remembering

A researcher is investigating whether a sealed box contains a blue token. Call that proposition *p*. All probabilities in this example are stipulated and correctly understood. The setup is a model, not an empirical claim about human memory or instruments.

Initially, blue and red are equally likely. A fair randomizer selects one of two sensors, A or B. The researcher sees both the selected sensor's identity and its report. Each sensor reports either blue or red.

Sensor B reports the true color with probability 0.9, symmetrically for both colors. Sensor A has two possible operating conditions. With probability 0.8 it is sound and reports the color perfectly. With probability 0.2 it is faulty and produces a fair random report, independent of the token. Its condition is independent of the token and of the randomizer. Thus, before its condition is revealed, A also reports correctly with probability 0.9:

\[
0.8(1)+0.2(0.5)=0.9.
\]

An independent inspection will shortly reveal whether A was sound or faulty when the report was made. The inspection discloses only that condition. It neither inspects the token nor changes the sensors' past behavior.

Suppose the report is blue. Whichever sensor supplied it, the researcher's rational credence in *p* is 0.9. The source label makes no difference to that answer. But the researcher can adopt either of two retention policies, selected before the randomizer operates:

**Keep:** retain the report and the source label.

**Erase:** retain the report but erase the source label completely.

Both policies retain the general setup, including the random selection mechanism and the fact that any erasure was applied uniformly. Neither conceals a surviving clue to the source. To isolate the epistemic comparison, suppose keeping the label has no additional cost, creates no distraction, and prevents no other useful retention.

Both policies include an exact rule for assigning probabilities from the information that remains. The researcher following Erase therefore does not simply carry over her old attitudes about the source. She becomes appropriately uncertain about it. She also retains a coherent account of the inspection's significance under that uncertainty. The case grants the ideal of immediate adjustment to available evidence; it does not depend on a transient mismatch during a memory operation.

Immediately after erasure, her credence in *p* is still 0.9. Because either source would have produced a blue report with probability 0.5, the blue report does not disturb the equal probabilities of A and B. Moreover, the inspection's result remains independent of which sensor was selected. The later probabilities are consequently:

| Information retained about the blue report | Inspection: A was faulty | Inspection: A was sound |
|---|---:|---:|
| It came from A | 0.5 | 1 |
| It came from B | 0.9 | 0.9 |
| Its source was erased | 0.7 | 0.95 |

The last row follows by averaging the first two with equal weights. If A was faulty, the erased report might be uninformative or might be a reliable B report: the appropriate average is 0.7. If A was sound, it might be conclusive or might remain a 0.9 report: the appropriate average is 0.95. A red report produces the corresponding probabilities for red.

There is no irrational updating in the last row. The researcher would make a mistake if she acted as though she knew the report came from A, or as though she knew it came from B. She does not know either. Her later uncertainty is a proper response to what she has retained.

Nor is the fit accidental. For every possible token, source, report, and inspection result, each policy assigns exactly the probabilities supported by its surviving information. We can specify this for all propositions in the finite model, not just *p*. In each retained information state, assign the conditional probability distribution over the underlying possibilities. Both policies then systematically achieve perfect evidential fit throughout the modeled inquiry.

Nevertheless, Keep seems epistemically better. It allows a known source failure to be applied precisely where it belongs. Erase needlessly converts a discriminating disclosure into a less discriminating one. That loss can be measured without assuming that sharper confidence is always better.

For a credence *c* in *p*, measure inaccuracy by \((c-X)^2\), where *X* is 1 if *p* is true and 0 otherwise. A credence equal to a supported probability *c* has expected inaccuracy \(c(1-c)\). Before the inspection, both policies have expected inaccuracy 0.09 concerning *p*. After the inspection, conditional on the blue report, Keep has expected inaccuracy

\[
0.2\left(\frac{0.25+0.09}{2}\right)
+0.8\left(\frac{0+0.09}{2}\right)=0.07.
\]

Erase has expected inaccuracy

\[
0.2(0.7)(0.3)+0.8(0.95)(0.05)=0.08.
\]

The lost label therefore has positive expected epistemic value even though it contributes nothing to the present probability of the question under investigation. Keeping it does not invariably produce a credence closer to the truth in each individual outcome. It produces a strictly better expected accuracy result under the very probability model both policies correctly use.

## 3. The general structure of the loss

The numerical case illustrates a familiar information-theoretic structure. Let *H* be the information before compression, let *S* be the summary retained from it, and let *Z* be a later disclosure. The general background model remains available throughout. Write

\[
q=P(p\mid H,Z),\qquad r=P(p\mid S,Z).
\]

Here *q* is the credence supported if the original information is retained, and *r* is the credence supported by the summary and the disclosure. Because *S* is a function of *H*, the law of conditional expectation gives

\[
r=\mathbb E[q\mid S,Z].
\]

Expanding the squared errors yields

\[
\mathbb E[(r-X)^2]-\mathbb E[(q-X)^2]
=\mathbb E[(q-r)^2].
\]

To see why, write \(r-X=(r-q)+(q-X)\). The cross term has expectation zero because the expectation of \(q-X\), conditional on *H* and *Z*, is zero. The remaining term is nonnegative, and it is positive whenever different histories hidden within the same summary support different later probabilities with positive probability.

Nothing in this identity is a new mathematical result. Nor is the distinction between preserving a current answer and preserving future responses new. Aevyra's recent online manuscript gives an exact criterion for whether a compressed history supports a declared family of revisions, including source withdrawals. Alvarez develops related distinctions between current prediction and later learning in mathematical models. Both explicitly connect their work to established sufficiency or distinguishability ideas. [Aevyra 2026, §§4.1–4.3, 6.2](https://aevyra.github.io/ledger-of-will/); [Alvarez 2026, §9](https://arxiv.org/html/2610.13881v1).

The philosophical point turns on a distinction between two targets for the later inquirer. One target is reproducing the answer that the full information would support. The other is responding correctly to the information actually retained. A compressed record may make the first impossible while leaving the second entirely achievable. It is therefore a mistake to move directly from an information-loss result to a verdict that the later inquirer reasons irrationally.

The converse mistake is more tempting. Since the later inquirer can always respond correctly to the reduced evidence, perhaps the retention policy is epistemically unobjectionable. But the identity shows why that conclusion does not follow. Correct response to reduced evidence does not remove the cost of reducing it. In the sensor case, that cost appears only when a new disclosure interacts with the discarded detail. Measuring present confidence alone would miss it.

## 4. Why a disposition toward evidential fit is not enough

Hedden's time-slice approach takes what an agent ought to believe at a time to depend on her state at that time, without giving her own past attitudes a special role. His initial discussion distinguishes that question from questions about the rationality of an agent or the basis of a belief. [Hedden 2015, §1 and n. 3](https://11243971-2fc2-4a01-b59f-e247f0f3c35e.filesusr.com/ugd/0f1e81_e6793e3d37ee403e9af45b0f45805987.pdf).

Podgorski objects that rational assessment also concerns cognitive processes. In particular, he notes that an account of evidence must not make objectionable changes harmless merely because changing beliefs also changes the evidence against which they are assessed. His concern about evidence management is a direct predecessor of the present argument. [Podgorski 2016, §§3, 8](https://philpapers.org/archive/PODART.pdf).

Hedden's reply permits derivative evaluations of processes by their tendency to bring beliefs into proportion with evidence. His note 15 applies this strategy to an agent who drops a belief and happens to remain proportioned to the impoverished evidence: the success can be lucky while the disposition remains defective. Note 14 also acknowledges a different possibility, in which process norms and evidential-fit norms derive separately from a concern for truth. [Hedden 2016, §4, nn. 14–15](https://11243971-2fc2-4a01-b59f-e247f0f3c35e.filesusr.com/ugd/0f1e81_66deef15afa74c87be6935ee9f277371.pdf).

The sensor case targets the first strategy, not the alternative he acknowledges. Erase does not happen to land on the right credences after a reckless fluctuation. Its rule is designed to land on them across the entire modeled domain. Compare Keep and Erase under three ways of assessing their tendency toward evidential fit: actual success, expected success, and success across possible inputs. They tie under each. Neither leaves behind unsupported beliefs about the token or the source. Yet their informational prospects differ.

This is not an objection to conditional probability. Correct conditioning is what makes the case work. It also does not show that the researcher should somehow continue to condition on a source identity she has lost. Instead, it challenges the assumption that all epistemic reasons governing the policy must pass through a tendency to make surviving attitudes better proportioned to surviving evidence.

One response is to evaluate Erase against the richer evidence the agent *could have retained*. That would identify its defect. But this changes the standard. It compares the information made available by different policies rather than measuring fit to whatever evidence each policy leaves in place. It thereby recognizes the additional dimension for which the example argues.

Another response evaluates the disposition more broadly. Real people who discard sources may also confuse reports, conceal doubts, or fail to average appropriately. Those tendencies would make a realistic policy worse. They are absent from the stipulated case. To insist that the policy must be assessed only together with such tendencies would require an independent account of why those are the relevant comparison cases. They cannot be imported simply because the exact policy has an unwelcome verdict. Transparent erasure followed by correct adjustment is a coherent method; its failure of future discrimination does not depend on an associated reasoning error.

The equal initial sensor accuracies are not responsible for that systematic fit. If their probabilities change, and the changes are represented in the retained background model, assigning the conditional distribution over the reduced information still preserves fit. Equal initial confidence makes this particular loss initially invisible with respect to *p*. It is an additional feature of the example, not a lucky condition on which the policy's proportionality depends.

The limited conclusion is that fit alone cannot supply the whole assessment. This leaves several philosophical options. One may add truth-directed norms for managing evidence. One may recognize norms of inquiry that are distinct from norms of belief. One may allow the epistemic value of information to enter instrumental reasoning about retention. The case does not decide among these options. It does rule out treating the extra assessment as merely another way of measuring a policy's tendency to fit the evidence it preserves.

## 5. A modest norm for retaining information

The example supports a local principle:

> When an inquirer can retain information that, by her present lights, will improve the expected accuracy of an ongoing inquiry, without a relevant cost or competing reason, she has an epistemic reason to retain it. That reason need not consist in preventing future failures of evidential fit.

Three qualifications keep this principle modest. First, it concerns an inquiry already underway. It does not demand that an agent gather or preserve every truth she might someday find interesting. Second, the improvement must be supported by the agent's present perspective. A detail's usefulness discovered years later does not by itself show that forgetting it was unreasonable. Third, the principle leaves room for costs, including attention, retrieval difficulty, privacy, and interference with more important inquiries.

Why call the reason epistemic? In the sensor case its whole basis is a better prospect of accurately answering the same question. No reward, punishment, promise, reputational benefit, or effect on another person is needed. Removing those practical factors leaves the reason intact. It would be peculiar to allow accuracy to explain why an instrument is epistemically better while denying any epistemic significance to preserving the one bit needed to interpret its output.

This argument identifies a reason, not a universal duty to maximize an aggregate accuracy score. The example holds the question and other effects fixed. It does not license making one belief evidentially irrational in order to improve many others. At every stage, each policy's beliefs can remain fully proportioned. What is compared is the information each policy makes available for a single inquiry.

The distinction also matters when storage is costly. Suppose preserving the source label would displace information crucial to another inquiry. Erase may then be the better policy overall. But permissible loss should be represented as loss. A summary that retains only the blue report supports present confidence of 0.9. It does not support the more specific assertion that the report will remain at 0.9 if A fails inspection. Nor does it support the assertion that it will fall to 0.5. Its permissible later use depends on acknowledging the unresolved source.

This gives a second, different norm: do not present a summary as preserving a distinction that it has erased when that distinction matters to an anticipated use. There is no requirement to attach a general warning to every memory. If all users already know the summary's limitations, nothing further need be said. The requirement concerns a mismatch between the use invited and the information supplied.

In the numerical case, a sufficient qualification is simple: the blue report came from A or B, with equal probabilities, and the source identity has been lost. That qualification enables the last row of the table. It does not restore the first two rows. Thus it repairs a misleading presentation without repairing the information loss itself. A warning cannot compensate for every avoidable deletion; it can make a justified deletion, or an unavoidable one, usable without pretending it was costless.

Notice what the qualification does *not* require. It does not lower current confidence from 0.9. The researcher is not uncertain whether she now has grounds for that probability. She is uncertain which grounds she has lost, and that uncertainty will matter differently under different future disclosures. A generic instruction to become less confident would make her less proportioned to the surviving evidence. Appropriate humility here consists in limiting what she claims about the future behavior of her reasons.

This is a useful form of epistemic restraint. Instead of treating every inability to explain a belief as a reason to abandon it, it asks which explanatory detail has been lost and which inferential use requires that detail. The result can be continued confidence together with a narrower claim about what that confidence can do.

## 6. Objections and limits

**Doesn't a complete Bayesian state already solve the problem?** Yes, if the state retains the relevant joint probabilities. A marginal probability for *p* is only one part of that state. The example compares retaining a source distinction with discarding it, not two mathematically identical full states. An agent who keeps conditional probabilities sufficient to recover every relevant response has preserved the useful information in another form. Literal source labels are not intrinsically required.

That reply confirms rather than removes the distinction. Two representations can support the same present probability while differing in their relation to later evidence. An account of good retention must specify which relation matters. The proposed criticism applies only when a policy actually discards a useful distinction; it does not condemn compression as such.

**Is this simply the familiar value of information?** Its formal core is. No priority is claimed for the proposition that more information can improve expected accuracy. The contribution is its use against a particular explanation of process assessment. Here the lost information has no present value for the target probability, its future value can be made explicit, and the poorer policy systematically achieves evidential fit. These features separate the defect from both present irrationality and accidentally successful reasoning. They also show why a test of memory based only on reproducing current justified conclusions can miss the defect.

**Could retaining the belief preserve its historical evidence even after the source is forgotten?** Some theories make that possible. Weatherson defends a view on which past facts can remain available as evidence through memory, and distinguishes rational attitudes from the wisdom of agents. [Weatherson, “Memory, Belief and Time,” introduction and §1](https://philpapers.org/archive/WEAMBA.pdf).

Nothing here shows that all forgetting removes evidence in the way a simple partition model represents. The example stipulates a complete loss of the source distinction. It can be implemented as an external report whose identifying information is deleted and whose recipient never acquires it. Both recipients can have an adequate reason for the same initial probability while one lacks the information needed for the later discrimination. If a theory says the source remains epistemically available despite complete irreversible loss, it owes an explanation of what availability amounts to in this case. If it accepts that such loss is possible, the case applies to that kind of loss.

**Is Erase really a policy of rational forgetting if choosing it is irrational?** The title's contrast should not be read as giving the choice an endorsement. The claim is that all factual credences resulting from the policy can remain perfectly proportioned. The decision to adopt it may be defective. Indeed, that is the point. If its adoption violates a present norm of practical rationality because the researcher values accurate inquiry, the choice can be criticized synchronically. But its inferiority then comes from the informational consequences of the choice, not from an expected failure of evidential fit.

Likewise, an inquirer may correctly believe she should retain the label and nevertheless erase it. That would introduce a separate conflict between judgment and choice. The construction does not require such a conflict, and the argument does not depend on it. We can compare the two methods as candidate retention policies before any irrational decision is made. Their difference in epistemic merit already needs an explanation.

**Does the argument establish irreducible norms extending over time?** No. A reason to preserve future evidence can be a reason the agent has now. A theory could assess her current plan by its expected consequences for later accuracy. The disagreement exposed here is therefore not exhausted by a choice between norms at times and norms over intervals. A theory may remain thoroughly concerned with present reasons while recognizing that good evidence management is not reducible to fitting the evidence currently possessed. That is a narrower conclusion than a general defeat of time-slice epistemology, but it is also more secure.

**Why not always demand exact preservation for every possible future question?** Because finite memory has other work to do. Exact preservation relative to an unrestricted range of questions can require retaining the entire history. The normative standard defended here does not use mere possibility to generate unlimited demands. It begins with a concrete future disclosure, a known interaction with existing evidence, and a cheap way of preserving that interaction. Outside such cases, estimating what to retain is itself fallible inquiry. The principle supplies a reason for a choice, not an algorithm that settles every storage budget.

**What if the model is wrong?** Then the stated numerical ranking may be wrong too. More records can distract; apparent source information can be misleading; retaining a mistaken model can perpetuate error. These are reasons to distinguish an agent's reasonable assessment of a retention policy from its actual success. In the example, the model is stipulated correct to isolate the conceptual issue. Applying the principle to a real archive requires evidence about future uses and actual costs. The argument gives no warrant for assuming that the fullest archive always yields the best inquiry.

## 7. Keeping the right standard in view

The researcher's erased source label leaves her in a position from which she can reason faultlessly. That does not make the erasure harmless. She can do everything the surviving evidence permits and still have needlessly reduced what the inquiry can achieve.

This is why the standard of evidential fit cannot do every job in epistemic assessment. It properly constrains the beliefs formed after information is lost. It does not, by itself, determine whether the information should have been lost. A disposition that reliably meets a moving evidential standard can still move that standard downward.

The appropriate response has two parts. Before loss, preserve a distinction when its expected contribution to the inquiry supplies an undefeated reason to do so. After loss, proportion belief to what remains and represent the limits of that information honestly. The second task sometimes calls for uncertainty about future revision without diminished confidence in the present answer. Remembering a conclusion well therefore requires attention both to its current support and to the uses for which that support remains available.

## Bibliography

Aevyra. 2026. *The Ledger of Will: Evidence, Revaluation, and the Preservation of Revisable Agency*. Version 4.0, 25 September. Online research manuscript; page credits Yue, Anika, and Sofia. [Text](https://aevyra.github.io/ledger-of-will/).

Alvarez, Robert Jenkinson. 2026. “Prediction Is Not a Sufficient Memory State.” arXiv:2610.13881v1. [Text](https://arxiv.org/html/2610.13881v1).

Dogramaci, Sinan. 2015. “Forget and Forgive: A Practical Approach to Forgotten Evidence.” *Ergo* 2 (26): 645–677. [doi:10.3998/ergo.12405314.0002.026](https://doi.org/10.3998/ergo.12405314.0002.026).

Hedden, Brian. 2015. “Time-Slice Rationality.” *Mind* 124 (494): 449–491. [doi:10.1093/mind/fzu181](https://doi.org/10.1093/mind/fzu181).

Hedden, Brian. 2016. “Mental Processes and Synchronicity.” *Mind* 125 (499): 873–888. [doi:10.1093/mind/fzv161](https://doi.org/10.1093/mind/fzv161).

Podgorski, Abelard. 2016. “A Reply to the Synchronist.” *Mind* 125 (499): 859–871. [doi:10.1093/mind/fzv153](https://doi.org/10.1093/mind/fzv153).

Weatherson, Brian. “Memory, Belief and Time.” *Canadian Journal of Philosophy* 45 (5–6). Consulted author manuscript dated 2015; institutional repository records publication in 2016. [doi:10.1080/00455091.2015.1125250](https://doi.org/10.1080/00455091.2015.1125250).
