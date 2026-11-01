# How Much Must a Rational Plan Settle?

## Abstract

A policy can select individually permissible acts yet fail E-admissibility as a whole. Its rows must share an expected-utility witness. That established requirement leaves three different tasks: choosing one permissible policy, preserving all completions of a fixed partial plan, and preserving permissions uniformly when new menus are added. A set of compatible witnesses represents the second task, but a proper subset, sometimes even one probability, can represent it too. By contrast, every proper closed convex reduction loses a permission in some additional binary menu. Drawing on existing conservative-extension and probability-set distinguishability results, I apply this distinction to deliberation and delegation. Selecting a probability first can be a permissible implementation without being a faithful record of everything an agent has left open. This is a limited interpretation of coordination, not a new rationality requirement or representation theorem.

## 1. What must an implementation preserve?

Suppose your evidence leaves the probability of rain between one quarter and three quarters. You must prepare instructions for someone who will make one decision on your behalf. There are several possible menus of acts, and you do not yet know which menu will be offered. Can you provide coherent instructions without first fixing an exact probability of rain?

The question is sometimes made too easy. It is not enough to say that whichever act your instructions select will be permissible when considered alone. The instructions themselves are an option you can evaluate. They might perform worse than another available policy according to every probability you regard as admissible.

E-admissibility supplies a familiar standard. An act is permissible when it maximizes expected utility for at least one probability in the agent's credal set. The standard allows different acts to have different justifying probabilities. That freedom creates a problem when acts are combined.

Elga's argument for sharp credences makes sequential choice central. His section 8, footnote 23, already describes removing probabilities that do not endorse an act; he also considers plans as a separate response. The removal operation is therefore inherited, not introduced here. [Elga 2010, §§8–10 and n. 23](https://swh.princeton.edu/~adame/papers/sharp/elga-subjective-probabilities-should-be-sharp.pdf).

Pettigrew, Campbell-Moore and Konek characterize acceptable picking strategies through a common expected-utility witness. Their introduction says an agent needs to select a probability to determine her plan. Section 3.2.1 carefully states the behavioral requirement in as-if terms and disclaims an inference to actual precise credences. I question only a literal procedural reading of the introduction: that selecting a numerical proxy must precede assembling the plan. The construction below is compatible with their qualified characterization. [Pettigrew, Campbell-Moore and Konek 2025, introduction and §3.2.1](https://doi.org/10.1007/s11238-025-10088-2).

Once some instructions have been settled, three tasks must be distinguished:

1. Produce one permissible completed policy.
2. Preserve every permissible completion for a specified finite list of remaining menus.
3. Preserve permissions uniformly as arbitrary new menus are added to the plan.

Selecting a point probability can accomplish the first task, can sometimes accomplish the second, and generally cannot accomplish the third when several compatible probabilities remain. The task determines whether the selection is a useful implementation, a faithful compression, or an additional restriction.

The mathematical ingredients have substantial antecedents. Conservative extension of choice assessments and the distinguishability of probability sets are established subjects, discussed in section 6. My contribution is their application to the scope of an unfinished practical mandate. I assume E-admissibility throughout. Preserving every permission is an additional representational aim, not an unconditional duty imposed by that decision rule.

## 2. Why a record of actual choices is insufficient

Consider three acts. Their entries are utilities, not a general assumption that people value money linearly.

| Act | Rain | No rain |
|---|---:|---:|
| A | 8 | 0 |
| S | 5 | 5 |
| B | 0 | 8 |

Let the credal set contain every rain probability p in [1/4, 3/4]. The expected utilities are 8p, 5 and 8(1−p). Thus A is permissible when supported by some p at least 5/8; B is permissible when supported by some p at most 3/8; and S is supported throughout [3/8, 5/8]. All three acts are E-admissible.

Now a fair coin, independent of rain according to every member of the credal set, will be tossed before the choice. The same menu is available after either result. Consider these instructions: choose A after heads and B after tails. Whichever result occurs, the instructions select an individually permissible act. There is only one actual choice. There is no previous act whose justification the agent has forgotten, no new evidence about rain, and no change of preference.

Nevertheless, the policy's expected utility is

E_p(policy) = (1/2)8p + (1/2)8(1−p) = 4.

Always choosing S yields 5. Every probability in the original interval therefore prefers the second policy. Remembering which probabilities justify previously performed acts cannot repair the first policy: before its only actual act, that record is empty.

This is not a newly discovered kind of failure. Huntley and Troffaes already give a tree in which all local options occur in acceptable solutions but some combinations do not. They also distinguish that failure from the property they call subtree perfectness. [Huntley and Troffaes 2012a, Example 6 and discussion](https://arxiv.org/abs/1208.1154). The present example isolates the demand a repair must meet while using a convex credal set and the same menu after either signal.

Several qualifications matter. The rejected policy does not guarantee a monetary loss. It can deliver 8 while S delivers 5. Its deficiency is a lower expected utility for every admitted probability. Moreover, the coin is independent in each joint probability model, not merely uninformative in the weaker sense that the bounds on rain remain unchanged. The example makes no claim about other notions of imprecise independence.

The example is also not a boundary accident. If the probability of heads is q, the largest expected utility of the A/B policy over p∈[1/4,3/4] is

4 + 2|2q−1|.

S beats it for every p whenever 1/4 < q < 3/4. Outside that range the policy still lacks a common maximizing probability if both coin outcomes have positive probability, but S alone need not uniformly beat it. These are different defects.

A finite exact search checked all menus of two or three distinct utility vectors drawn from {0,1,2,3,4}², with the same credal interval and a fair independent signal. None of the 300 binary menus yielded an inadmissible mixture of two individually admissible acts. Of 2300 ternary menus, 37 did. The counts describe only this finite search.

The binary result has a general explanation. If both acts in a two-act menu are E-admissible relative to a convex credal set, their difference in expected utility is nonnegative somewhere and nonpositive somewhere. Along a segment joining those probabilities, it is zero somewhere. At that common probability, both acts and every lottery between them maximize expected utility. A third act can remove this common justification: in the table, A and B tie at p=1/2, but S is better there. Three acts are therefore necessary for this particular same-menu failure under convexity. This does not establish a minimum for arbitrary decision trees.

What must be retained is not merely a history of actual decisions. The restrictions must connect instructions for possibilities that will never occur together.

## 3. A sufficient record of a partial plan

Let Ω be a finite state space, with real, state-independent cardinal utilities, and K a nonempty compact convex set of probabilities on it. There are finitely many nonempty finite menus D₁,…,Dₙ. Menu i will be offered with known probability μᵢ>0, independently of the state under every p∈K. Only one menu is offered. A policy π specifies one act πᵢ from each menu. Every combination of row choices is feasible; there are no costs of writing or executing the instructions.

For an act a in menu i, define its set of witnesses:

Wᵢ(a) = {p∈K : E_p(a) ≥ E_p(b) for every b∈Dᵢ}.

If a partial plan has fixed rows I, define

C_π = ⋂ᵢ∈I Wᵢ(πᵢ).

This is the set of probabilities jointly compatible with those instructions. It is not a new estimate of which state obtains.

The common-witness result gives a precise test: the partial plan has an E-admissible completion exactly when C_π is nonempty. For necessity, any probability that makes a complete policy optimal must make each selected row optimal. Otherwise, changing just that row would improve the policy's expected utility, because μᵢ is positive. For sufficiency, take any probability in C_π and fill the remaining rows with maximizers for it. Summing the row inequalities, weighted by μᵢ, proves that the resulting policy is optimal for that probability. This is the finite special case of the established picking-strategy characterization, not a new representation theorem.

It follows that one can assemble instructions without designating a point probability. Retain C_π. At the next row, permit exactly those acts a for which C_π∩Wᵢ(a) is nonempty. Once a row is fixed, replace the record by that intersection. Continue until the table is complete.

The procedure never reaches a dead end from a nonempty record: any probability remaining in it has a maximizing act in the next finite menu. It can also generate every E-admissible completion. Follow the rows of such a completion in any order; its common witness remains in every intersection. When K is a polytope, these tests are finite systems of linear inequalities. More sophisticated algorithms for E-admissible decision trees already exist; computational tractability is not the novelty claimed here. [Huntley and Troffaes 2012b, abstract and introduction](https://arxiv.org/abs/1104.0191).

The distinction between K and C_π is crucial. K records evidentially admissible probabilities. C_π records which of them could justify the instructions currently being assembled. A probability outside C_π can remain entirely compatible with the evidence. Its exclusion means only that it cannot justify this plan. Reporting C_π as a posterior would confuse choosing a course of action with learning something about rain.

Nor is the procedure an invitation to mix surviving acts freely. The row choices are made while specifying one definite policy, before the menu is drawn. A fixed ordering of feasible entries could make the construction deterministic. After the first row is specified, the next is tested against the actual intersection, not against the original credal set again. In the earlier example, specifying A after heads leaves p≥5/8 and thereby excludes B after tails.

A definite output is required. The unfinished record is not itself an act that somehow receives the best payoff of its possible completions. Keeping C_π is a sufficient way to retain all completions. Whether it contains distinctions unnecessary for a particular remaining list is a separate question.

## 4. Fixed menus and additional menus

The following partial instruction sheet makes the remaining freedom visible. Continue to use K=[1/4,3/4]. Three possible menus have been specified, and the selected entries are bold.

| Menu | Available utility vectors (rain, no rain) | Selected entry |
|---|---|---|
| 1 | (8,0), (5,5), (0,8) | **(5,5)** |
| 2 | (8,0), (4,4) | **(8,0)** |
| 3 | (0,8), (3,3) | **(0,8)** |

The first row requires 3/8≤p≤5/8. The second requires p≥1/2, and the third requires p≤5/8. Their common record is therefore

C = [1/2, 5/8].

Every probability in this interval supports all three instructions. Choosing a particular representative, say r=11/20, is unnecessary for their execution.

Suppose a fourth possible menu must now be added to the same instruction sheet. Its options are Z=(0,0) and T=(−17,23). At the chosen point r, T has expected utility

23 − 40(11/20) = 1,

so an agent who treats r as binding must reject Z. Yet the earlier instructions do not require that rejection. Z is optimal throughout [23/40,5/8], a nonempty part of C. At p=3/5, T has expected utility −1, so Z is strictly better, while all three earlier selections remain optimal. The completed policy choosing Z is therefore E-admissible. Enumeration of all 24 complete policies confirms the same witness interval.

The fourth row is a further possibility being entered into one plan. It is not an actual later gamble, and no issue about sunk costs or changes of evidence arises. Its introduction exposes a difference between two commitments that looked behaviorally identical on the first three rows. Commitment to those rows permits Z; commitment to r does not.

There is an important countercheck. If this fourth menu is the only one left to settle, the point 23/40 preserves both completions: Z and T tie there, and all three previous instructions are maximizing. Thus the point 11/20 loses a completion, but point selection as such need not lose one in this fixed problem. This countercheck was supplied by the independent AI critic and reproduced during revision.

The critic also identified the general finite-domain criterion. Let F be a fixed finite list of remaining menus. For each completion σ, let

R_σ = C ∩ ⋂ⱼ∈F Wⱼ(σⱼ).

A reduced record C′⊆C preserves exactly the same completions for F if and only if it intersects every nonempty R_σ. Indeed, such an intersection is exactly what supplies a common witness for that completion. A subset of C cannot license an originally inadmissible completion. Selecting one witness from every nonempty region therefore gives a finite preserving set; its convex hull also preserves the family because it remains inside C. That hull need not be a proper subset. There is no universal claim that every finite problem compresses to a smaller convex record, still less to one point.

This supplies a test for faithful compression of a specified mandate. It replaces the mistaken idea that a smaller set must always have fewer permissions on the menus currently under consideration.

A different question asks for preservation against every possible added menu. Here every proper closed convex reduction can be detected. The order of quantifiers matters: specify the reduction first; some further menu can then expose a lost permission.

**Loss under an unrestricted extension domain.** Let C be the nonempty record of a finite partial plan. If C′ is a proper nonempty closed convex subset of C, there is a binary additional menu containing an act that can be part of an E-admissible completion of the plan, but is excluded when only C′ is retained.

To prove it, choose p*∈C outside C′. Since C′ is compact and convex, there is a utility vector v and a number t such that

E_q(v) < t < E_p*(v) for every q∈C′.

Add the menu {0,t−v}. At p*, the zero act is strictly better. At every q∈C′, the other act is strictly better. Thus zero can be added without losing the plan's common justification, but the more restricted record prohibits it.

For completeness, the separation used here can be constructed directly. Let q₀ be the point of C′ nearest to p*, and put v=p*−q₀. Convexity and nearest-point optimality give v·q≤v·q₀ for all q∈C′, whereas v·p*=v·q₀+‖v‖². Taking t halfway between the latter two quantities yields the displayed strict inequalities. If negative utility entries are unwanted, adding a common constant to both acts changes no comparison.

The theorem relies on allowing arbitrary finite utility vectors in new menus. Restrictions on available acts can make two different records indistinguishable. Nor does it apply when C itself is a singleton. But whenever a nontrivial interval survives, every point selection loses a permission in some possible further binary menu. The distinguishing menu may differ for different points. The loss is strict at the relevant witnesses; it need not arise from a fragile tie. This claim does not contradict the point 23/40 preserving both completions of the particular fourth menu.

Accordingly, exactness is relative to the domain of possible extensions. For a fixed finite domain, the witness-region test determines whether a reduction changes any permission. Uniformly over arbitrary added binary menus, a proper closed convex reduction always does. The separation construction makes this latter claim transparent; section 6 locates it within prior distinguishability results.

## 5. What the result does, and does not, answer

A first objection is that the completed policy still behaves like expected-utility maximization for some precise probability. Correct. The construction is designed to preserve that property. It challenges an inference about what must be settled during deliberation, not the theorem about how a finished policy can be represented.

This is not just the general distinction between behavior and belief. The continuation example gives that distinction practical consequences. Two processes can issue exactly the same initial instructions while preserving different sets of permissible completions. Choosing a point proxy can restrict what may be entered later. For a fixed menu list, whether it does so is settled by the witness-region test. The relevant contrast is between committing to the choices already made in the plan and committing to additional comparisons that one representative probability happens to resolve.

A defender of point selection may answer that preserving all permissions is unnecessary. Rationality asks for a permissible act, not an exhaustive display of every alternative one could have chosen. This is also correct. Someone may permissibly use r and therefore choose T in the fourth menu. Nothing here shows that her completed policy is irrational.

The conclusion is conditional. A procedure that selects one permissible path may be entirely adequate as a way to act. It fails to represent all remaining authority only if it removes a completion allowed by the specified mandate. No general obligation to postpone choice follows. What needs a further argument is a procedural requirement to select a point first, or a claim that the selected point always records exactly what the earlier instructions already require.

Consider an agent who asks an assistant to transmit her remaining authorization to a delegate. “These three rows are settled; complete the fourth in any E-admissible way” differs from “use probability 11/20 for the fourth.” The latter prohibits Z; the former permits it. Transmitting the latter as an equivalent abbreviation would misstate the mandate. This failure concerns faithful transmission of authority, even though the delegate's eventual choice of T could be rational and authorized under either instruction.

Transmitting “use 23/40” for that same fourth menu, allowing either maximizing act, preserves the two completions. It is a faithful abbreviation for this bounded task. The agent may instead authorize adding further menus before the plan is executed. That broader mandate requires a different preservation test; the same point can then remove a permission.

The norm doing work here is conditional fidelity to the granted authority. E-admissibility determines the permitted completions, but does not independently require transmitting all of them, hiring a delegate, or preserving discretion forever. A principal may explicitly narrow the mandate, and a delegate authorized to select a completion must eventually do so. The error is to treat permission to choose one completion as evidence that every faithful description of the prior mandate must already choose one probability. Keeping these roles separate gives the mathematical distinction practical significance without inventing an additional axiom of rational choice.

A second objection concerns randomization. Perhaps leaving several choices open really means running an uncertain selection mechanism. Then the theory must assess that mechanism, and it may reject it. Pettigrew, Campbell-Moore and Konek explicitly evaluate randomized picking and sets of strategies treated as imprecise acts. The present record is not offered as a counterexample to those evaluations. [2025, §§4–4.2.1](https://doi.org/10.1007/s11238-025-10088-2).

The objection succeeds against a careless version of the proposal. The method must not flip a coin between arbitrary completed policies and assume that their separate permissibility licenses the lottery. Nor may it treat uncertainty about which policy it will execute as automatically harmless. Its output for the present decision must be a determinate instruction sheet, or an explicitly evaluated lottery. The example's full record is a tool for constructing that output, not a distribution over outputs.

One can object in turn that a deterministic construction still needs a tie-breaking rule. It does, just as a precise expected-utility maximizer may need a rule for selecting between equally maximizing acts. An arbitrary fixed ordering of feasible row entries supplies one. The theory need not uniquely mandate the ordering. Crucially, no ordering chosen during construction can license a row whose intersection is empty. Different permissible constructions can produce different admissible policies; their existence does not imply permission to randomize between them.

A third objection is that the set C simply disguises epistemic narrowing. It uses probabilities and removes some of them, after all. But the role of a mathematical set is not settled by the type of its members. The same probability can be compatible with the evidence yet incompatible with the justification of a particular plan. C answers the second question. The agent's factual reports and assessments of unrelated evidence can continue to use K. No inference from “I specified A” to “rain is now more likely” is licensed.

That answer does not automatically justify carrying C through every later decision in the agent's life. My model concerns assembling one plan over mutually exclusive possible menus, either from a fixed list or through finite additions before execution. Extending its prescriptions to successive acts, changing evidence, dependent menus, or unforeseen alterations of the state space requires further arguments. In particular, the procedure is not a general alternative to Bayesian updating, and it does not settle the full dispute over resolute choice.

Finally, perhaps the relevant domain contains every conceivable betting menu. If so, the policy can impose much sharper commitments than any short instruction sheet does. Distinct probabilities can be distinguished by some binary bet. A sufficiently extensive set of settled choices may therefore leave only one common witness. The proposal does not promise permanent practical imprecision. When preserving remaining authority is the task, the required specificity depends on the actual extension domain. An agent with a different task may permissibly settle more.

## 6. What is inherited, and what the application adds

Decadt, Erreygers and De Bock already develop conservative E-admissible extension using all probability models agreeing with partial choice assessments. Their rationale expressly concerns avoiding unwarranted rejections. Their assessments record rejected options, use a background dominance order, and may generate strict constraints and nonconvex sets. Here a selected row requires weak maximality and does not declare its rivals impermissible. Choosing Z in the fourth row allows the tie at 23/40; an assessment rejecting T would exclude it. These input meanings differ, but retaining all compatible models is not a new principle. [Decadt, Erreygers and De Bock, author manuscript, §§3–4, 10](https://users.ugent.be/~jdbock/documents/AD-2026-FSS-paper.pdf).

Seidenfeld, Schervish and Kadane prove a stronger general distinguishability result: distinct probability sets, including nonconvex ones, have different finite-option admissibility patterns. The elementary closed-convex binary separator above is not offered as a new discovery that probability sets have different practical consequences. I cite the 2007 proceedings version actually consulted. [Seidenfeld, Schervish and Kadane 2007, §2, Theorem 2 and corollary](https://www.cmu.edu/dietrich/philosophy/docs/seidenfeld/Coherent%20Choice%20Functions.pdf).

Against these antecedents, the contribution is a limited application to the interpretation of coordination. Requiring a completed policy to have a common witness does not settle the order of deliberation, nor what a partial mandate has authorized. A construction can output one determinate permissible policy without first treating a probability as binding. Alternatively, an agent can retain the full scope of a mandate for later completion or delegation. This is compatible with the established behavioral theorem, not a competing theorem.

The distinction between the two preservation domains prevents an opposite overstatement. Full witness retention is sufficient for any fixed finite list, but not invariably necessary. A probability can faithfully encode the permissions for one list and restrict them for a richer list. Thus neither “always retain every witness” nor “always select one first” follows merely from coordination. Specify the task and the domain before judging the implementation.

This leaves a modest philosophical gain: it identifies when practical precision is a further decision, when it is harmless compression, and when it merely describes the behavior of a completed plan. It does not prove that E-admissibility is the best theory, that indefinite permission-preservation is obligatory, or that this interpretation has no further antecedents. The surviving claim is that rational coordination and the faithful representation of remaining authority answer different questions, with a precise test for the difference in the model considered here.

The independent AI critique contributed the 23/40 countercheck, the finite witness-selection observation, and the two literature comparisons introduced in this section. Those contributions are incorporated with their provenance; the revision received no second independent review.

## Bibliography

Decadt, Arne, Alexander Erreygers, and Jasper De Bock. “Conservative decision-making with sets of probabilities: How to infer new choices from previous ones.” Author manuscript marked © 2025. https://doi.org/10.1016/j.fss.2025.109612. Consulted version: https://users.ugent.be/~jdbock/documents/AD-2026-FSS-paper.pdf.

Elga, Adam. 2010. “Subjective Probabilities Should be Sharp.” *Philosophers' Imprint* 10(5): 1–11. https://swh.princeton.edu/~adame/papers/sharp/elga-subjective-probabilities-should-be-sharp.pdf.

Huntley, Nathan, and Matthias C. M. Troffaes. 2012a. “Identifying Subtree Perfectness in Decision Trees.” arXiv:1208.1154. https://arxiv.org/abs/1208.1154.

Huntley, Nathan, and Matthias C. M. Troffaes. 2012b. “Normal Form Backward Induction for Decision Trees with Coherent Lower Previsions.” *Annals of Operations Research* 195(1): 111–134. https://doi.org/10.1007/s10479-011-0968-2. Author version: https://arxiv.org/abs/1104.0191.

Pettigrew, Richard, Catrin Campbell-Moore, and Jason Konek. 2025. “Choosing how to choose.” *Theory and Decision*. Published online 8 October 2025. https://doi.org/10.1007/s11238-025-10088-2.

Seidenfeld, Teddy, Mark J. Schervish, and Joseph B. Kadane. 2007. “Coherent Choice Functions under Uncertainty.” *Fifth International Symposium on Imprecise Probability: Theories and Applications*, Prague. https://www.cmu.edu/dietrich/philosophy/docs/seidenfeld/Coherent%20Choice%20Functions.pdf.
