# Settled, but Still Revisable

An investigator reaches a well-supported conclusion, records her degree of confidence, and closes the file. She deletes some information that makes no difference to that confidence. Everything she currently takes to be relevant to the question survives. Has she preserved what matters epistemically?

Not necessarily. Information can make no difference to the confidence presently warranted by an inquiry yet determine how that confidence should change when a foreseeable criticism arrives. Its loss need neither lower present justification nor make a later belief irrational. It can instead destroy a capacity for informed correction. That is a distinctive failure, and a theory of responsible inquiry should be able to identify it before it occurs.

I defend a limited preservation norm: when we intend to continue relying on a conclusion, we have an epistemic reason to preserve affordable information that materially improves our response to foreseeable challenges to its basis. In the absence of countervailing reasons, we ought to preserve it. Present evidential sufficiency does not supply a permission to discard such information. The norm can require retaining a source identifier while permitting the deletion of thousands of observations; it can also require nothing at all. Its object is the capacity to revise appropriately, not the indiscriminate accumulation of records.

## 1. An apparently harmless deletion

Consider two channels, A and B, each reporting on whether a proposition H is true. Initially H and its negation are equally probable. Each channel has an independent probability of 0.8 of being sound. A sound channel reports H's truth value perfectly. An unsound channel produces a fair random answer, independently of H. Which channels are sound is also independent of H.

An investigator uses a fair coin to select one channel and receives a positive report. She knows the model just described. The report's probability is 0.9 if H is true: a sound channel certainly reports positively, while a randomizing channel does so half the time. Its probability is 0.1 if H is false. The investigator's rational confidence in H is therefore 0.9.

Crucially, it is 0.9 whether A or B was selected. The channels have identical initial credentials. After observing the positive report, learning which one supplied it would make no difference to her confidence in H. Suppose she already knows which one she used. She now proposes to retain the positive report and the model, including her justified confidence, but delete the channel's identity. There is no distortion of her present assessment. She is not suppressing an objection, forgetting that she reasoned badly, or inflating a probability by omitting an unfavorable result.

Tomorrow a routine audit will disclose which channels were sound. Imagine its finding is that A randomized while B was sound. If the investigator used A, her positive report now gives her no reason to prefer H to its negation: her posterior is 0.5. If she used B, her posterior is 1 in this idealized model. A retained identity would tell her which response is appropriate.

Without the identity, she must average the possibilities. Conditional on the audit and the positive report, each channel remains equally likely to have been selected. Her confidence is now 0.75. That is the appropriate assessment given what survives. But it is a poorer epistemic position than the one she could cheaply have preserved. She has lost the ability to distinguish a report whose force has collapsed from one whose force has increased.

The example separates two kinds of relevance. The channel's identity is irrelevant to the present probability of H, conditional on the positive report. It is relevant to that probability conditional on the report and the audit. Deleting it preserves today's answer but fails to preserve tomorrow's appropriate revision.

Nothing depends on the use of certainty. Sound channels could instead be extremely reliable, and audits could be fallible. Those changes complicate the arithmetic without removing the difference. Nor must the information be stored in a person's unaided memory. A source label on a document would do. The idealization isolates a choice over a tiny, controllable record.

## 2. What must a summary preserve?

The example admits a precise generalization. Fix a background probability model, a target proposition H, an original record E, and a summary M obtained from E. The original record can include observations, source identities, selection procedures, or other information. Throughout, probabilities are relative to the fixed background, and conditional probabilities are considered only where defined.

Call a summary *presently sufficient* for H when, for every possible original record, it preserves the probability of H:

P(H | E) = P(H | M).

This is an intentionally demanding standard of present preservation. It requires more than retaining a belief, a confidence category, or a verdict that some threshold has been met. Nevertheless, it is insufficient for the further task we are considering.

Let F be a future observation, such as the result of an audit. Call M *sufficient for revision by F* when:

P(H | E, F) = P(H | M, F)

for every possible combination of original record and subsequent observation. If a family of future investigations matters, the requirement applies to each, including relevant sequences of observations. The family is part of the specification; sufficiency for revision is not an unqualified property of a summary.

A simple criterion follows. A summary permits exact reproduction of the revisions supported by the original record if and only if it never merges two records that, upon the same possible later observation, support different probabilities for H. Necessity is immediate. An updater receiving the same summary and the same new observation cannot return two different probabilities. For sufficiency, if all records compatible with that summary and observation support the same probability, their probability-weighted average has that same value. Conditioning on the summary therefore recovers the result of conditioning on any compatible original record.

This is an elementary fact about conditional probabilities, not a new statistical theorem. Its philosophical use is to show why a tempting test of permissible forgetting is inadequate. Checking that a deletion leaves current confidence unchanged examines only the first equality. The second can fail even when the first holds exactly.

The criterion also explains why retaining every detail is unnecessary. If different original records would license the same response to every relevant later observation, merging them loses nothing for this purpose. A summary could preserve a table of responses to an anticipated audit instead of preserving the history from which the table was calculated. Or it could preserve a compact reference that allows the needed distinction to be recovered elsewhere. What matters is accessible discriminatory information, not fidelity to a particular physical record.

There is no objection here to Bayesian updating. A full probability distribution over the target, sources, and prospective audit already represents the conditional relationships that matter. What fails is the identification of that richer state with a marginal probability for the target, even an entirely justified marginal. The corresponding distinction between present beliefs and a state adequate for subsequent revision is established territory: Darwiche and Pearl explicitly argue that iterated revision can depend on information not captured by a belief set (1997, abstract). My concern is what follows for the deliberate removal of information after an inquiry has produced a usable answer.

## 3. Why the lost capacity matters

One response is to accept all the calculations while denying that anything normatively significant follows. After deletion the investigator believes exactly what her remaining information supports. After the audit she again updates correctly. Where is the epistemic fault?

It lies, if anywhere, in the earlier choice of what to preserve. We can evaluate an informational action without treating every belief produced downstream as irrational. Imagine that a colleague offers to maintain the channel label at no cost or inconvenience. Refusing the offer does not improve the investigator's present assessment. It does not release attention needed for another question. It predictably makes her later assessment less discriminating. If she remains concerned to get H right, refusal frustrates that continuing concern without a compensating benefit.

This is not just a preference for more detail. The retained bit improves accuracy in expectation. Use squared error to assess a confidence p, assigning error (p − 1)² when H is true and p² when it is false. Before the audit, rational confidence 0.9 has expected error 0.09, whether or not the channel identity survives.

After the full audit, keeping the identity yields expected error 0.05. With probability 0.8, the selected channel is sound, and the investigator can identify the truth without error. With probability 0.2, it randomized, so confidence 0.5 incurs expected error 0.25. The weighted average is 0.05.

Without the identity, expected error is 0.07. Both channels are sound with probability 0.64, in which case the positive report settles H. Both randomize with probability 0.04, yielding confidence 0.5. Exactly one is sound with probability 0.32, yielding confidence 0.75. The resulting average is 0.64 × 0 + 0.04 × 0.25 + 0.32 × 0.1875 = 0.07. These probabilities remain appropriate after the positive report because, before learning H, either kind of channel produces a positive report half the time.

The audit improves matters under either retention policy. Keeping the label preserves more of that improvement. There is no need to suppose that deletion makes the investigator dogmatic, dishonest, or unwilling to listen. She can be perfectly responsive to all the evidence available at each later moment while having avoidably impaired the evidence available to her.

Why call the reason to avoid that impairment epistemic? Its ground is that retaining the label helps an agent distinguish the truth from error about a proposition in which she maintains an interest. It does not depend on monetary stakes, reputational damage, or obligations to an audience. Those considerations may strengthen the case, but the defect exists in a solitary investigation pursued from curiosity. The reason concerns how to maintain the means of reaching appropriately informed assessments.

Friedman's account of inquiry makes room for evaluating such informational choices alongside the fit between beliefs and evidence. Her instrumental principle connects an inquirer's epistemic aim with the means necessary to pursuing it (2020, §3). The present proposal extends this way of thinking to the maintenance of an answer after active investigation has stopped. It does not require accepting her broader account of conflicts between epistemic and inquiry norms.

The preservation norm is consequently conditional and defeasible:

> If an agent intends to keep relying on an answer, has reason to anticipate a kind of further evidence, and can retain information that would materially improve her response to it at negligible cost and without countervailing disadvantage, she ought to retain that information.

More generally, the improvement supplies an epistemic reason whose weight must be assessed against the costs and competing ends. The strict case establishes a clear requirement; it does not settle every tradeoff. The reason applies at the point where retention is a feasible choice. It is not a demand that a later agent recreate information that has become inaccessible.

## 4. Three permissions that come apart

The proposal distinguishes permission to hold a conclusion, permission to stop actively investigating it, and permission to discard its basis. These are often exercised together. They need not stand or fall together.

The investigator may reasonably use H as her working answer today. She may also have no reason to run additional tests: a routine audit is already scheduled, or further testing is too expensive relative to its expected benefit. Neither fact settles whether she should delete the channel label. Retention does not involve collecting another observation, reopening the question, or suspending her current judgment. It simply preserves the ability to use the observation she already expects to receive.

This matters because inquiry cannot rationally require perpetual checking. Friedman argues that some repeated checking is epistemically problematic even when further evidence would improve an agent's position (2019, §§1, 6). Preserving a capacity to revise does not commit us to such checking. One can stop looking while keeping enough information to recognize the force of a challenge when it arrives.

Nor does the preservation norm require a historical theory of present justification. Dogramaci defends the rationality of some beliefs whose defective origins have been forgotten. He expressly distinguishes that issue from the harmfulness of forgetfulness itself (2015, §§1.1, 3.3). The distinction is indispensable here. The present argument does not discover that harmful forgetting and rational surviving belief can coexist. It identifies a particular prospective ground for discouraging forgetting even when nothing was wrong with the original belief, no existing defeater was suppressed, and its current evidential strength is perfectly preserved.

The contrast is especially clear if the summary passes to someone else. A recipient who never had the channel identity need not be at fault for updating to 0.75 after the audit. The original investigator need not be irrational in making the same update after deletion. Yet the investigator earlier had an inexpensive opportunity to place either person in a better epistemic position. Whether present belief is rational and whether that opportunity was responsibly handled are different questions.

The normative work is therefore done by present reasons for a present act of retention. No mysterious authority is assigned to a vanished past self. No one is instructed to obey old confidence merely because it is old. On the contrary, the point of keeping the trace is to let newly arriving evidence defeat or strengthen the answer appropriately.

## 5. Selection is not contamination

The argument could easily be mistaken for a general complaint about evidence chosen by a motivated investigator. That would be a mistake. A result does not lose its force merely because someone hoped to find it, decided when to stop, or selected what to report. Its force depends on what the recipient learns, including what is known about the process.

In the finite model presented by Hendriksen, de Heide, and Grünwald, posterior odds are invariant across stopping rules compatible with the retained observation sequence (2020, §2.1). A demand to penalize every adaptive search would ignore this result. Moreover, Gandenberger shows why a rule can be noninformative for the researcher while informative for a recipient who suspects that its selection reflects undisclosed information (2018 manuscript, §3). The same procedural fact can have different evidential roles given different informational backgrounds.

Both points constrain the preservation norm. We should not demand that agents retain procedural details merely because procedures look epistemically important. A detail that makes no difference to any relevant later revision may safely disappear. Conversely, a detail may require retention even though the procedure was fair, the agent was disinterested, and the original inference was exemplary. The two-channel case was deliberately designed this way: selection was random, both sources had equal credentials, and all current probabilities were correct.

The relevant question is thus not simply whether a record describes a procedure or whether the procedure was biased. It is whether losing that record merges evidential situations which a foreseeable development would require us to treat differently. A record of how evidence was selected is one possible answer. A source identifier, calibration date, or distinction between an observation and a quotation of an observation may be another. None is mandatory just because it belongs to a familiar category of documentation.

A useful consequence is that an inquiry's successful result cannot, by itself, establish that its remaining record is adequate for future use. Confidence in the answer is not confidence that every foreseeable correction can still be made. An assessment of the latter requires examining which informational dependencies survive. This is a limitation on what success certifies, not an additional deduction against the truth of the conclusion.

## 6. Does this demand too much memory?

For any innocuous detail, one can invent future evidence that would make it relevant. Perhaps tomorrow a message will reveal that every report produced on a Tuesday was corrupted, or that the color of a notebook encodes an otherwise inaccessible truth. If possibilities like these generated retention requirements, almost nothing could be forgotten.

The formal criterion does not itself generate those requirements. It identifies informational loss relative to a specified family of subsequent observations. The normative premise concerns which observations an agent has reason to anticipate and which losses matter enough to prevent. A merely imaginable correlation is not yet a reason to organize an epistemic life around it.

In the example, a known forthcoming source audit provides that reason. In less artificial cases, an ongoing correction practice, a known vulnerability in a method, or a scheduled review can do so. When inquiry uses revisable testimony, information about source reliability is often a recognizable kind of potential challenge. This does not establish that every source identifier should always be kept. Some claims will never be used again. Some traces are costly to maintain. Some information can easily be reacquired, while some preserves distinctions too insignificant to matter.

There is no context-free solution to the choice of relevant future challenges. That is a limitation of the proposal, but not one peculiar to it. An obligation to check a calculation also requires judgment about which errors are worth checking for and what checking would cost. The absence of a universal decision procedure does not make a scheduled, cheap, decisive check optional for no reason. Likewise, the possibility of difficult preservation cases does not erase the clear ones.

Exact equality of posterior probabilities is also stronger than a practical policy will normally need. The criterion gives the ideal boundary of losslessness. A reasonable retention policy can tolerate small discrepancies or remote contingencies. That makes the required summary smaller, at the price of a consciously accepted risk. It does not make present confidence an adequate measure of that risk: the discrepancies at issue arise only after new information is combined with the summary.

Other objections concern the agent's control. Much ordinary forgetting is involuntary, and much personal information would be burdensome or wrong to retain. The norm is not an accusation against ordinary limitations of memory. It addresses choices available through note-taking, document management, delegation, or other feasible means. Privacy, attention, and the demands of other inquiries can defeat its reason. Sometimes the responsible response is to retain less and acknowledge that the answer can no longer support the same kind of subsequent review.

Finally, a reader may ask whether the proposed norm adds anything beyond the familiar value of information. At the most general level, it does not introduce a new ultimate epistemic value. Its contribution is a discriminating application. Information selected for deletion can have zero value for the presently contemplated inference while having positive value for foreseeable revision of that very inference. A retention policy that checks only current evidential adequacy systematically misses this possibility. The norm identifies the omitted dimension and places the demand at a time when an agent can still satisfy it.

## 7. Maintaining answers together

The issue becomes consequential when a conclusion is maintained by a community. One person gathers the evidence, another prepares a summary, and others rely on it. These people need not each possess the original record. They do need some arrangement capable of preserving the distinctions that foreseeable correction will require, where doing so is affordable and the conclusion remains in use.

Imagine that a committee compresses several reports into a single confidence judgment. The result may be sufficient for today's choice. If a later correction names a particular report, the committee must be able to determine which conclusions depended on it. A present probability, an endorsement, or a record that everyone agreed does not necessarily preserve that dependency. The committee can be confident for good reasons and still organize its future learning badly.

The remedy need not be universal access to all supporting material. A trusted custodian can retain source relationships; summaries can preserve the relevant distinctions; or a conclusion can carry a limited scope of reuse. The general requirement concerns the community's accessible capacity for correction. It does not require every recipient to repeat the original inquiry or to prove the reliability of every custodian in an endless regress. Fallible, ordinarily justified arrangements are enough to make retention beneficial.

This also clarifies what is objectionable about presenting a compressed file as if it were an enduring substitute for the investigation. A summary can transmit justified confidence without transmitting the capacity to reconsider that confidence under source-specific criticism. Treating the first achievement as a guarantee of the second gives recipients a misleading picture of what the file can do, even if every sentence in it is true and its reported confidence is correct. Honest compression may therefore require preserving not only a conclusion but a boundary on the revisions the remaining material can support.

We ordinarily think of settling a question as the point at which information gathering can cease. In many cases that is right. But when an answer will remain in use, closure also marks a choice about its future: whether it will remain answerable to the developments we already have reason to expect. The right record may be very small. What matters is that enough survives to let a changed evidential situation make the appropriate difference.

## References

Darwiche, Adnan, and Judea Pearl. 1997. “On the Logic of Iterated Belief Revision.” *Artificial Intelligence* 89(1–2): 1–29. https://doi.org/10.1016/S0004-3702(96)00038-0.

Dogramaci, Sinan. 2015. “Forget and Forgive: A Practical Approach to Forgotten Evidence.” *Ergo* 2(26): 645–677. https://doi.org/10.3998/ergo.12405314.0002.026.

Friedman, Jane. 2019. “Checking Again.” *Philosophical Issues* 29: 84–96. https://doi.org/10.1111/phis.12141. Author manuscript: https://jfriedmanphilo.github.io/2CHECK.pdf.

Friedman, Jane. 2020. “The Epistemic and the Zetetic.” *The Philosophical Review* 129(4): 501–536. Author manuscript: https://jfriedmanphilo.github.io/E%26Z.pdf.

Gandenberger, Greg. 2018. “Differences Among Noninformative Stopping Rules Are Often Relevant to Bayesian Decisions.” Manuscript dated August 28, 2018, available under arXiv:1707.00214. https://arxiv.org/pdf/1707.00214.

Hendriksen, Allard, Rianne de Heide, and Peter Grünwald. 2020. “Optional Stopping with Bayes Factors: A Categorization and Extension of Folklore Results, with an Application to Invariant Situations.” arXiv:1807.09077v3. https://arxiv.org/abs/1807.09077.
