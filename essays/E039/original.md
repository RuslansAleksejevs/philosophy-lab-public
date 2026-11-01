# Settled, but Still Revisable

An investigator reaches a well-supported conclusion, records her degree of confidence, and closes the file. She deletes some information that makes no difference to that confidence. Everything she currently takes to be relevant to the question survives. Has she preserved what matters epistemically?

Not necessarily. Information can make no difference to the confidence presently warranted by an inquiry yet determine how that confidence should change when a foreseeable criticism arrives. Its loss need neither lower present justification nor make a later belief irrational. It can instead destroy a capacity for informed correction. That is a distinctive failure, and a theory of responsible inquiry should be able to identify it before it occurs.

I defend a limited norm for maintaining settled answers. Information that improves our use of foreseeable corrections supplies a pro tanto epistemic reason for retention: a reason that can be outweighed. A stronger requirement arises under an additional principle defended below, when an agent maintains an aim of appropriately informed assessment and deletion gratuitously sacrifices a recognized means to it. This stronger claim concerns alternatives with no relevant difference in cost or other disadvantage; merely small costs belong to the defeasible case. The distinction matters because a beneficial improvement is not automatically obligatory.

The underlying informational phenomenon is already familiar in both memory epistemology and the theory of signals. The contribution proposed here is a prospective account of responsibility for controllable compression after settlement. It separates the rationality of subsequent beliefs from the adequacy of an earlier preservation decision and identifies the limitations of judging that decision solely by present confidence.

## 1. An apparently harmless deletion

Consider two channels, A and B, each reporting on whether a proposition H is true. Initially H and its negation are equally probable. Each channel has an independent probability of 0.8 of being sound. A sound channel reports H's truth value perfectly. An unsound channel produces a fair random answer, independently of H. Which channels are sound is also independent of H.

An investigator uses a fair coin to select one channel and receives a positive report. She knows the model just described. The report's probability is 0.9 if H is true: a sound channel certainly reports positively, while a randomizing channel does so half the time. Its probability is 0.1 if H is false. The investigator's rational confidence in H is therefore 0.9.

Crucially, it is 0.9 whether A or B was selected. The channels have identical initial credentials. After observing the positive report, learning which one supplied it would make no difference to her confidence in H. Suppose she already knows which one she used. She now proposes to retain the positive report and the model, including her justified confidence, but delete the channel's identity. There is no distortion of her present assessment. She is not suppressing an objection, forgetting that she reasoned badly, or inflating a probability by omitting an unfavorable result.

Tomorrow a routine audit will disclose which channels were sound. Imagine its finding is that A randomized while B was sound. If the investigator used A, her positive report now gives her no reason to prefer H to its negation: her posterior is 0.5. If she used B, her posterior is 1 in this idealized model. A retained identity would tell her which response is appropriate.

Without the identity, she must average the possibilities. Conditional on the audit and the positive report, each channel remains equally likely to have been selected. Her confidence is now 0.75. That is the appropriate assessment given what survives. But it is a poorer epistemic position than the one she could cheaply have preserved. She has lost the ability to distinguish a report whose force has collapsed from one whose force has increased.

A close philosophical antecedent appears in Frise's discussion of forgotten evidence. His paired cases concern initially justified beliefs, forgotten source identities, and the subsequent discrediting of one source. He uses them to challenge preservationism about justification (2017, §III, especially pp. 492–494). The present example does not discover that source-specific criticism can matter after forgetting. It changes the evaluative target: before deletion, with a correction procedure already anticipated, what reason has an agent to preserve the distinction? We can answer that question without resolving Frise's dispute about surviving justification.

The example separates two kinds of relevance. The channel's identity is irrelevant to the present probability of H, conditional on the positive report. It is relevant to that probability conditional on the report and the audit. Deleting it preserves today's answer but fails to preserve tomorrow's appropriate revision.

Nothing depends on the use of certainty. Sound channels could instead be extremely reliable, and audits could be fallible. Those changes complicate the arithmetic without removing the difference. Nor must the information be stored in a person's unaided memory. A source label on a document would do. The idealization isolates a choice over a tiny, controllable record.

## 2. What must a summary preserve?

The example admits a precise generalization. Fix a finite background probability model, a target proposition H, an original record E, and a deterministic summary M obtained from E. The original record can include observations, source identities, selection procedures, or other information. Throughout, probabilities are relative to the fixed background, and conditional probabilities are considered only where defined.

Call a summary *presently sufficient* for H when, for every possible original record, it preserves the probability of H:

P(H | E) = P(H | M).

This is an intentionally demanding standard of present preservation. It requires more than retaining a belief, a confidence category, or a verdict that some threshold has been met. Nevertheless, it is insufficient for the further task we are considering.

Let F be a future observation, such as the result of an audit. Call M *sufficient for revision by F* when:

P(H | E, F) = P(H | M, F)

for every possible combination of original record and subsequent observation. If a family of future investigations matters, the requirement applies to each, including relevant sequences of observations. The family is part of the specification; sufficiency for revision is not an unqualified property of a summary.

This is a restricted instance of an established problem in comparing information. Brooks, Frankel, and Kamenica distinguish sufficiency from stronger comparisons that remain valid when additional, potentially correlated signals are available (2024, author manuscript, §§4.1, 5). Their comparisons range over additional signals generally. Here the purpose is narrower: assess a compression relative to a specified correction practice, without claiming robustness to every possible source of further information.

A simple criterion follows. A summary permits exact reproduction of the revisions supported by the original record if and only if it never merges two records that, upon the same possible later observation, support different probabilities for H. Necessity is immediate. An updater receiving the same summary and the same new observation cannot return two different probabilities. For sufficiency, if all records compatible with that summary and observation support the same probability, their probability-weighted average has that same value. Conditioning on the summary therefore recovers the result of conditioning on any compatible original record.

This is an elementary fact about conditional probabilities, not a new statistical theorem. Its philosophical use is to show why a tempting test of permissible forgetting is inadequate. Checking that a deletion leaves current confidence unchanged examines only the first equality. The second can fail even when the first holds exactly.

The criterion also explains why retaining every detail is unnecessary. If different original records would license the same response to every relevant later observation, merging them loses nothing for this purpose. A summary could preserve a table of responses to an anticipated audit instead of preserving the history from which the table was calculated. Or it could preserve a compact reference that allows the needed distinction to be recovered elsewhere. What matters for this limited purpose is accessible discriminatory information, not fidelity to a particular physical record. A response table preserves posterior reproduction only under the specified model and observations. It need not preserve the material needed to question that model, evaluate the auditor, or choose a new investigation. Those are additional tasks, considered below.

There is no objection here to Bayesian updating. A full probability distribution over the target, sources, and prospective audit already represents the conditional relationships that matter. What fails is the identification of that richer state with a marginal probability for the target, even an entirely justified marginal. The corresponding distinction between present beliefs and a state adequate for subsequent revision is established territory: Darwiche and Pearl explicitly argue that iterated revision can depend on information not captured by a belief set (1997, abstract). My concern is what follows for the deliberate removal of information after an inquiry has produced a usable answer.

## 3. From informational loss to a preservation norm

One response is to accept the calculations while denying that anything normatively significant follows. After deletion the investigator believes exactly what her remaining information supports. After the audit she again updates correctly. Where is the epistemic fault?

If there is a fault, it lies in the earlier choice. The point can first be made without assigning blame or declaring any belief irrational. Imagine that a colleague offers to maintain the channel label at no additional cost, distraction, privacy burden, or risk. Both policies leave today's assessment untouched. Tomorrow, however, retention allows the investigator to discriminate more accurately in expectation.

Use squared error to assess a confidence p, assigning error (p − 1)² when H is true and p² when it is false. Before the audit, confidence 0.9 has expected error 0.09 under either retention policy. After the full audit, keeping the identity yields expected error 0.05: with probability 0.8 the selected channel is sound and identifies the truth, while with probability 0.2 it randomized and warrants confidence 0.5, whose expected error is 0.25.

Without the identity, expected error is 0.07. Both channels are sound with probability 0.64, in which case the positive report settles H. Both randomize with probability 0.04, yielding confidence 0.5. Exactly one is sound with probability 0.32, yielding confidence 0.75. The weighted error is therefore 0.64 × 0 + 0.04 × 0.25 + 0.32 × 0.1875 = 0.07. These soundness probabilities remain appropriate after the positive report because either kind of channel produces a positive report half the time before H is known.

There is a general connection between this accuracy comparison and the criterion in §2. Let X be 1 if H is true and 0 otherwise; let q = P(H | E, F) and r = P(H | M, F). Write Expected for expectation in the stipulated model. Then:

Expected[(X − r)²] − Expected[(X − q)²] = Expected[(q − r)²].

To see this, write X − r as (X − q) + (q − r), expand the square, and average. The cross term vanishes because the conditional average of X − q, given E and F, is zero, while q − r is fixed by E and F. The same argument works conditional on a particular original record, so the prospective comparison can use the information the agent possesses at the time of choice.

This standard conditional-variance identity shows that lossless posterior reproduction is exactly the zero-loss case for the expected squared-error comparison. A discrepancy on an event of positive probability entails a strict loss. In the example that loss is 0.02. This does not guarantee greater accuracy in every realized world. If the selected channel randomized and H happens to be true, the informed confidence 0.5 is less accurate on that occasion than 0.75. The advantage is in expectation under the assumed model.

The loss supplies an epistemic reason for retention. Its ground is an avoidable impairment of truth-directed assessment, not reputational damage or monetary consequences. Calling it epistemic uses a broad category encompassing the management of inquiry and its results. It does not imply that all ordinary uses of “irrational belief” evaluate informational choices in this way.

A reason, however, is not yet a requirement. An investigator might reply: “My answer is already good enough. Even after deletion I will respond rationally to the audit. I have no obligation to improve every future assessment.” This is a substantive satisficing objection. Listing the advantages of retention does not answer it. Nor does Friedman's necessary-means principle settle the issue: she explicitly distinguishes necessary, satisficing, and optimizing formulations of instrumental norms (2020, §3, manuscript pp. 6–8). Retention is not necessary for every acceptable epistemic achievement.

The stronger conclusion needs a further premise. I propose a restricted principle against gratuitous informational loss:

> While an agent continues to endorse informed accuracy about an answer as an aim, she ought not knowingly choose a preservation policy that foreseeably impairs that aim when an available alternative avoids the impairment with no relevant additional cost or countervailing disadvantage.

Three restrictions do work here. The relevant alternatives and advantage must already be recognized; the principle does not require a costly search for the best conceivable policy. Their costs and other disadvantages must be equal; a tiny benefit does not automatically justify even a small burden. And the epistemic aim must continue; settling a one-off question does not obligate a person to preserve its basis indefinitely.

Why accept this principle instead of unrestricted satisficing? Adequacy can justify bringing an investigation to an end because further inquiry consumes attention, postpones reliance, or competes with other purposes. None of those explanations supports the stipulated deletion. The choice is already before the investigator; retention need not postpone settlement or require another check. Refusing a recognized, costless means of preventing deterioration does not protect a space in which she can pursue something else. It simply makes the continuing aim harder to serve.

The principle concerns preservation of a usable capacity, not the demand to make every belief maximally certain. A retained label allows the agent to use a correction that her existing practice will supply. If she would regard that correction as a reason to change her mind were the label available, yet deliberately removes the costless means of determining its relevance, her management of the answer conflicts with that continuing concern. “Today's answer is adequate” concerns the answer now; it does not explain the choice to disable tomorrow's relevant discrimination.

A thoroughgoing satisficer can still deny the principle. She may hold that all policies above a threshold are equally permissible even when one gratuitously impairs a continuing aim. The foregoing argument challenges that view by removing the burdens that ordinarily make satisficing attractive; it is not a deduction of its falsity from probability theory. The stronger requirement remains conditional on rejecting this unrestricted permission to waste. Moreover, someone whose only aim is meeting a fixed threshold, with no continuing concern for more informed assessment, does not satisfy the principle's stated antecedent. Mere continued use of an answer does not establish every aim required for the stronger conclusion.

The resulting position has two levels. Anticipated loss of accuracy grounds a pro tanto reason to keep the trace. When the relevant continuing aim, recognized alternatives, and absence of additional costs also obtain, the principle against gratuitous loss makes retention a requirement. For cases with positive costs or contested aims, the broader reason survives, but this argument supplies no automatic verdict. Both levels assess a choice while the needed information is still controllably available.

## 4. Three permissions that come apart

The proposal distinguishes permission to hold a conclusion, permission to stop actively investigating it, and permission to discard its basis. These are often exercised together. They need not stand or fall together.

The investigator may reasonably use H as her working answer today. She may also have no reason to run additional tests: a routine audit is already scheduled, or further testing is too expensive relative to its expected benefit. Neither fact settles whether she should delete the channel label. Retention does not involve collecting another observation, reopening the question, or suspending her current judgment. It simply preserves the ability to use the observation she already expects to receive.

This matters because inquiry cannot rationally require perpetual checking. Friedman argues that some repeated checking is epistemically problematic even when further evidence would improve an agent's position (2019, §§1, 6). Preserving a capacity to revise does not commit us to such checking. One can stop looking while keeping enough information to recognize the force of a challenge when it arrives.

Nor does the preservation norm require a historical theory of present justification. Dogramaci defends the rationality of some beliefs whose defective origins have been forgotten. He expressly distinguishes that issue from the harmfulness of forgetfulness itself (2015, §§1.1, 3.3). The distinction is indispensable here. He also keeps language discouraging forgetfulness outside his narrow category of epistemic evaluations. I accept his distinction of evaluative targets while using a broader, inquiry-centered sense of an epistemic reason. What the present argument adds is a specified prospective ground for retention; it does not establish a new verdict about the rationality of a forgotten belief.

The contrast is especially clear if the summary passes to someone else. A recipient who never had the channel identity need not be at fault for updating to 0.75 after the audit. The original investigator need not be irrational in making the same update after deletion. Yet the investigator earlier had an inexpensive opportunity to place either person in a better epistemic position. Whether present belief is rational and whether that opportunity was responsibly handled are different questions.

The normative work is therefore done by present reasons for a present act of retention. No mysterious authority is assigned to a vanished past self. No one is instructed to obey old confidence merely because it is old. On the contrary, the point of keeping the trace is to let newly arriving evidence defeat or strengthen the answer appropriately.

## 5. The limits of a preserved response

The account is relative to a model and a correction practice. It is not a general certificate of readiness for every form of criticism. Consider two records that support the same table of responses under a model treating their sources as independent. One record also reveals that those sources copied the same original. Later evidence about the copying process may require revising the model itself. A table preserving only the model's prescribed answers need not preserve what is needed for that revision.

This is outside the posterior-reproduction criterion, not a counterexample to it. If such a challenge is foreseeable, the agent should assess preservation against the relevant model alternatives as well, or retain enough of the basis to reconstruct an appropriate assessment. The criterion identifies one kind of loss. It does not show that information passing that test can safely be discarded for every epistemic purpose.

Nor should procedural information automatically be retained merely because a process was selective. Hendriksen, de Heide, and Grünwald establish stopping-rule independence in their finite model given a compatible retained observation sequence (2020, §2.1). Gandenberger explains why the informational significance of a rule may nonetheless differ between researcher and recipient when the latter suspects undisclosed information (2018 manuscript, §3). There is no universal evidential penalty for choosing when to stop.

The relevant preservation question concerns the distinctions that future assessment will require. Some procedural detail is dispensable; some detail from an entirely fair procedure is worth keeping. In the two-channel case, selection was random, credentials were symmetric, and the original inference was sound. Avoidable loss arises because present equivalence is treated as a guarantee of future interchangeability.

## 6. Does this demand too much memory?

For any innocuous detail, one can invent future evidence that would make it relevant. Perhaps tomorrow a message will reveal that every report produced on a Tuesday was corrupted, or that the color of a notebook encodes an otherwise inaccessible truth. If possibilities like these generated retention requirements, almost nothing could be forgotten.

The formal criterion does not itself generate those requirements. It identifies informational loss relative to a specified family of subsequent observations. The normative premise concerns which observations an agent has reason to anticipate and which losses matter enough to prevent. A merely imaginable correlation is not yet a reason to organize an epistemic life around it.

In the example, a known forthcoming source audit provides that reason. In less artificial cases, an ongoing correction practice, a known vulnerability in a method, or a scheduled review can do so. When inquiry uses revisable testimony, information about source reliability is often a recognizable kind of potential challenge. This does not establish that every source identifier should always be kept. Some claims will never be used again. Some traces are costly to maintain. Some information can easily be reacquired, while some preserves distinctions too insignificant to matter.

There is no context-free solution to the choice of relevant future challenges. That is a limitation of the proposal, but not one peculiar to it. An obligation to check a calculation also requires judgment about which errors are worth checking for and what checking would cost. The absence of a universal decision procedure does not erase recognizable reasons for particular checks. Likewise, difficult preservation cases do not eliminate the zero-additional-cost case governed by the restricted principle, or the weaker reasons present in less ideal circumstances.

Exact equality of posterior probabilities is also stronger than a practical policy will normally need. The criterion gives the ideal boundary of losslessness. A retention policy can be assessed by three different standards: reproducing every specified revision exactly; minimizing the expected discrepancy measured above; or protecting against particularly important failures even when unlikely. The identity establishes the second comparison and locates its zero at the first. It does not decide which standard every practice should adopt. A reasonable policy may tolerate small discrepancies or remote contingencies, making the summary smaller at the price of a consciously accepted risk. It does not make present confidence an adequate measure of that risk: the discrepancies at issue arise only after new information is combined with the summary.

Other objections concern the agent's control. Much ordinary forgetting is involuntary, and much personal information would be burdensome or wrong to retain. The norm is not an accusation against ordinary limitations of memory, and it does not imply that the existing record is infallible. It addresses choices available through note-taking, document management, delegation, or other feasible means. Privacy, attention, and the demands of other inquiries can defeat its reason. Sometimes the responsible response is to retain less and acknowledge that the answer can no longer support the same kind of subsequent review.

Finally, a reader may ask whether the proposed norm adds anything beyond the familiar value of information. At the most general level, it does not introduce a new ultimate epistemic value. Its contribution is a discriminating application. Information selected for deletion can have zero value for the presently contemplated inference while having positive value for foreseeable revision of that very inference. A retention policy that checks only current evidential adequacy systematically misses this possibility. The norm identifies the omitted dimension and places the demand at a time when an agent can still satisfy it.

## 7. Maintaining answers together

The issue becomes consequential when one person compresses an investigation for others. Suppose an analyst supplies a committee with a confidence judgment for continued use. An established correction procedure sends notices identifying defective source reports. The analyst controls a small map linking each conclusion to its source reports; recipients cannot reconstruct it. The map can remain with a custodian at no additional cost or risk. Preparing conclusions that can be assessed under that correction procedure is part of the analyst's continuing task.

The conclusion may be justified today whether the map survives or not. If a correction later names a report, however, the committee needs the map to identify the conclusions affected. Retaining only probabilities, endorsements, or a record of unanimous agreement may fail to preserve that dependency. Here there is no need to postulate an unexplained obligation borne by a community as a whole. The relevant choice belongs to the analyst, who can preserve an available means of serving the task she continues to undertake.

The arrangement need not give every recipient all the evidence. A custodian can maintain source relationships; a suitably qualified summary can preserve enough; or recipients can be told that a particular form of later review will require reconstructing the investigation. Such arrangements are adequate only for the challenges they actually address. Fallible, ordinarily justified custody can be valuable without supplying a guarantee against every error or grounding an endless demand to prove the custodian's reliability.

An omission becomes misleading when a summary is represented as supporting a kind of continuing review it cannot support, or when the agreed correction practice reasonably creates that expectation. Without such an assurance or expectation, omission is not automatically deception. The narrower point is that justified present confidence does not warrant an assurance of continuing revisability. Someone can accurately report the conclusion and its probability while overstating what the retained material will allow a recipient to do with later criticism.

This difference changes the appropriate question at the close of an inquiry. “Have we reached an adequate answer?” concerns whether to rely and whether to keep looking. “What must remain for the corrections we anticipate?” concerns how to maintain the result. Neither the ability to answer the first question nor the rationality of a later recipient answers the second.

A settled answer need not carry its entire history. It may need only a tiny distinction that is idle today and useful tomorrow. Probability theory explains how that distinction can matter; it does not alone establish what must be done. The normative demand depends on the continuing aim, foreseeable correction, and available alternatives. Once those are made explicit, preserving the means of changing one's mind can be part of responsible closure itself.

## References

Brooks, Benjamin, Alexander Frankel, and Emir Kamenica. 2024. “Comparisons of Signals.” *American Economic Review* 114(9): 2981–3006. https://doi.org/10.1257/aer.20230430. March author manuscript: https://benjaminbrooks.net/downloads/bfk_comparisons.pdf.

Frise, Matthew. 2017. “Preservationism in the Epistemology of Memory.” *The Philosophical Quarterly* 67(268): 486–507. https://doi.org/10.1093/pq/pqw074. Primary text: https://philpapers.org/archive/FRIPIT-5.pdf.

Darwiche, Adnan, and Judea Pearl. 1997. “On the Logic of Iterated Belief Revision.” *Artificial Intelligence* 89(1–2): 1–29. https://doi.org/10.1016/S0004-3702(96)00038-0.

Dogramaci, Sinan. 2015. “Forget and Forgive: A Practical Approach to Forgotten Evidence.” *Ergo* 2(26): 645–677. https://doi.org/10.3998/ergo.12405314.0002.026.

Friedman, Jane. 2019. “Checking Again.” *Philosophical Issues* 29: 84–96. https://doi.org/10.1111/phis.12141. Author manuscript: https://jfriedmanphilo.github.io/2CHECK.pdf.

Friedman, Jane. 2020. “The Epistemic and the Zetetic.” *The Philosophical Review* 129(4): 501–536. Author manuscript: https://jfriedmanphilo.github.io/E%26Z.pdf.

Gandenberger, Greg. 2018. “Differences Among Noninformative Stopping Rules Are Often Relevant to Bayesian Decisions.” Manuscript dated August 28, 2018, available under arXiv:1707.00214. https://arxiv.org/pdf/1707.00214.

Hendriksen, Allard, Rianne de Heide, and Peter Grünwald. 2020. “Optional Stopping with Bayes Factors: A Categorization and Extension of Folklore Results, with an Application to Invariant Situations.” arXiv:1807.09077v3. https://arxiv.org/abs/1807.09077.
