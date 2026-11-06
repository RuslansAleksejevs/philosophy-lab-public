# In an Infinite World, Refusal to Rank Can Be Informative

## Expanded argument proposal — not a completed essay

### Question and claim

When may finite-horizon welfare comparisons justify a ranking of two infinite, temporally ordered histories? I propose a conservative answer: extend a finite-prefix total-welfare comparison only when its direction is stable at every sufficiently late finite horizon. If positive and negative prefix verdicts each recur at arbitrarily late horizons, the histories are incomparable under this rule. That incompleteness is informative: it identifies dependence on an unchosen boundary schedule, rather than a missing fact about either history.

Let `x = (x₁, x₂, …)` and `y = (y₁, y₂, …)` be two histories with finite real welfare at each period. The finite-horizon rule compares cumulative totals:

`Dₙ(x,y) = Σₜ₌₁ⁿ (xₜ − yₜ)`.

The proposal is conditional on that finite rule and on an independently defensible ordering of periods. It does not claim that total welfare is the only value, that populations may be enumerated arbitrarily, or that every infinite history must receive a complete ranking.

### Horizon-stability rule

Treat an unbounded sequence of finite cutoffs `n₁ < n₂ < …` as a cofinal inspection schedule: it keeps looking at larger finite prefixes without selecting a final horizon. I do not treat any one such schedule as a moral aggregator. Instead, the family of all cofinal schedules is a robustness test. No particular late cutoff pattern is allowed to settle the comparison by itself when no ethical reason privileges it.

Define weak horizon support for `x` over `y` by:

`x ⪰H y` iff there is an `N` such that `Dₙ(x,y) ≥ 0` for every `n ≥ N`.

Define strict horizon support by:

`x ≻H y` iff there is an `N` such that `Dₙ(x,y) > 0` for every `n ≥ N`.

The histories are tied under this comparison iff both weak relations hold, equivalently iff `Dₙ(x,y) = 0` from some point onward. They are incomparable when neither direction has eventual weak support. In particular, if positive and negative prefix differences both occur infinitely often, there are cofinal schedules that keep seeing each opposing verdict, so neither direction survives the robustness test.

This rule is equivalent to requiring the corresponding weak or strict sign to hold eventually along every cofinal cutoff schedule. If `Dₙ ≥ 0` eventually, every cofinal schedule eventually encounters only nonnegative differences. If negative differences recur without bound, selecting their indices gives a cofinal schedule with a negative verdict at every inspection. The strict case follows the same reasoning, with recurring zero cutoffs also defeating strict support. The universal test therefore does not choose a boundary; it asks whether any unbounded finite-horizon inspection can reverse the direction.

### Argument

1. **Finite rankings are locally available.** Given the stipulated finite total-welfare rule, every prefix has a determinate weak comparison, and every nonzero `Dₙ` has a determinate strict direction.
2. **An infinite comparison needs a bridge.** A finite cutoff cannot itself be the horizon of an infinite history. Choosing one cutoff, one subsequence, or one generalized summation procedure therefore needs an independent ethical justification.
3. **A horizon-neutral bridge should not depend on an unprivileged cofinal schedule.** If the ordering of periods supplies no reason to privilege one unbounded schedule of cutoffs, an extension is warranted only when the direction is stable across all such schedules. This is the proposal’s substantive normative premise, not a theorem of arithmetic.
4. **Eventual sign is exactly the stability condition.** The equivalence above shows that the bridge yields `⪰H` when every sufficiently late prefix is nonnegative, and strict support only when every sufficiently late prefix is positive.
5. **Repeated reversal blocks a horizon-neutral verdict.** If `Dₙ` is positive and negative at arbitrarily large `n`, each side has a cofinal schedule on which it wins every inspected finite comparison. Selecting one side would add a schedule-selection rule not supplied by the histories or the finite total-welfare rule.

So the proposed conclusion is limited: eventual agreement licenses the corresponding weak comparison; persistent sign reversal licenses neither direction. The latter is not a claim that the two histories have equal value. It is a claim that this finite-prefix method has not justified ranking them.

### Worked cases

**Simple dominance.** Let `x₁ = 1`, `y₁ = 0`, and let both histories have welfare `0` at every later period. Then `Dₙ(x,y) = 1` for all `n ≥ 1`, so `x ≻H y`. More generally, if `xₜ ≥ yₜ` for every period and the inequality is strict at some finite period, all later cumulative differences are strictly positive. The rule preserves this pointwise finite-welfare dominance case.

**Oscillating cumulative advantage.** Set `D₁ = 1` and then let `Dₙ = 1` for odd `n` and `Dₙ = −1` for even `n`. This is generated by welfare differences `x₁ − y₁ = 1`, followed by `+2` at odd periods and `−2` at even periods. The streams can be nonnegative: use `(x₁,y₁)=(1,0)`, `(xₙ,yₙ)=(2,0)` at later odd periods, and `(0,2)` at even periods. Every finite cutoff strictly favors one history, but the winner reverses forever. The odd-cutoff schedule favors `x`; the even-cutoff schedule favors `y`. Unless an ethical reason privileges one schedule, the proposed relation withholds an infinite ranking while preserving every finite verdict. The remaining philosophical question is whether withholding the extension is justified, not whether the arithmetic is determinate.

### Strong objection and proposed answer

**Objection: the admissible family is not independently justified.** Calling every cofinal sequence “admissible” may merely rename arbitrary cutoffs. The proposal could then make oscillatory cases incomplete by stipulation, while offering no reason why an agent should care about the stability of finite-prefix signs. A requirement to act also seems to demand a choice, not a diagnosis.

**Answer.** The schedules are not proposed as competing moral evaluators. They are adversarial checks on an extension: if the verdict changes under some indefinitely advancing inspection schedule, the chosen extension depends on a boundary pattern that the method has not justified. The bridge is supported only if horizon neutrality is independently acceptable—roughly, that no finite stopping point or unbounded pattern of stopping points has moral authority merely because it yields a preferred answer. This defense is incomplete until argued against plausible horizon-sensitive ethics; it is the proposal’s central vulnerability.

A required action does not by itself establish which history has greater welfare. An agent can choose under a separate decision rule, rely on other moral reasons, or act under uncertainty while retaining an incomplete welfare ranking. This proposal therefore offers partial guidance: it settles pointwise dominance and any other case with eventual sign stability, and identifies where the finite-total method does not settle the comparison. It does not supply a complete theory of practical choice. If the competition requires an all-things-considered choice rule, that is additional work rather than a result to smuggle into the welfare comparison.

### Replies to the two assessments and the selection reason

The Astra assessment’s decisive question—whether an independently justified truncation family can preserve dominance while leaving enough determinate cases—is exactly the burden captured by the horizon-neutrality premise. The worked dominance case answers the first part for the stated model; it does not show that the unresolved region is small or useful. Astra is also right that familiar incompleteness and infinite-aggregation work may contain the proposal already. I disagree only with treating that risk as a reason to stop before the short formal and source probes: a precise candidate can be rejected cheaply if its relation to known approaches is merely restatement. I accept that no novelty claim is warranted now.

Sol’s recommendation correctly identifies that the sketch can be made formally testable and that incompleteness may be a defensible outcome. But the recommendation is not evidence that the ethical bridge is justified or that the move is original. The proposal makes the missing premise explicit and leaves it open to rejection. The root selection reason asked for a determinate dominance result, an informative unresolved case, and a confrontation with existing incomplete-order approaches; the two cases and the remaining-source tests address those requirements without claiming to have completed them. The disagreement between the assessors remains live: this is worth probing, but it may be familiar or normatively unsupported.

### Scope, invariances, and limits

For this model, multiplying all welfare differences by a positive constant preserves every verdict; adding the same welfare amount to both histories at each period leaves `Dₙ` unchanged; and the relation is transitive because cumulative differences add. Pointwise dominance with a strict finite improvement is preserved as shown. These are properties of the defined relation, not evidence that the assumptions are ethically compulsory.

The rule is sensitive to period order. That is plausible for chronologically ordered histories, but it cannot be transferred directly to an unordered infinite population by picking an arbitrary enumeration. If no morally defensible filtration or ordering is available, the proposed method must be narrowed or abandoned for that domain. Likewise, finite total welfare, temporal priority, and horizon neutrality all need defense. A finite early advantage can also settle a later bounded oscillation under the rule; whether this is acceptable is a separate ethical test.

### Significance if correct and revision conditions

If the bridge survives criticism, it offers a principled distinction between incomplete information and incomplete comparison. We may know every welfare entry and every finite-prefix sum while still lack a schedule-independent reason to rank the infinite histories. The unresolved verdict would then report a structural limit of extending the finite rule, rather than indecision about the data. The payoff is methodological clarity and a partial comparison that preserves simple dominance, not a complete solution to population ethics.

Substantially narrow or reject the claim if (a) horizon neutrality has no independent defense, (b) an independently accepted invariance makes the relation unacceptable, (c) the rule fails an intended finite-dominance case, (d) the temporal ordering cannot be justified in its target cases, or (e) primary literature shows that the same bridge and interpretation are already established. A successful source search would not by itself refute the mathematics, but it could remove the candidate’s contribution and require a different question.

### Closest-source questions still open

No primary sources or secondary literature were retrieved or read for this expansion. Originality remains **UNKNOWN**. A later fresh probe should compare the exact relation and its normative interpretation with work on overtaking and asymptotic dominance, incomplete orderings in infinite utility or population ethics, finite-prefix and limiting comparisons, and generalized summation or aggregation methods. It should locate the closest primary formulations, record the exact passages actually read, and test whether the proposed horizon-neutrality bridge adds anything beyond a known eventual-dominance relation. No literature conclusion is claimed here.
