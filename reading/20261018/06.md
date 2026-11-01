# What Holding Cannot Tell Us About Letting Go

Suppose an intervention can keep a system in a desired condition while it remains in place. Can it also produce a lasting change after support is withdrawn? This is a question about temporary control: success means reaching a state that maintains itself after the intervention ends. Evidence about maintained conditions does not automatically answer it.

Consider an exceptionally rich body of such evidence. For every nonempty selection of variables, every constant setting, and every initial state, we know the final outcome when those variables are held fixed indefinitely. We also know a baseline trajectory and all equilibria with their qualitative stability. Does this identify the outcome when a prepared state is released?

It need not. Two smooth systems can agree on this entire collection of evidence yet converge to opposite stable equilibria after the same release. The limitation concerns both the intervention menu and its readout: persistent coordinate clamps are observed only through their limiting outcomes. Complete coverage within that menu does not establish what happens under withdrawal.

The practical question is therefore not just whether more observations are needed. It is also whether a different withdrawal procedure can succeed despite the remaining uncertainty. In the example below, simultaneous withdrawal has an unidentified outcome, whereas releasing the variables in a suitable order guarantees the desired outcome throughout the specified model family. Reversing that order, with any fixed finite waiting period, preserves the uncertainty. This supplies a concrete use for the separation result: evaluating whether evidence certifies a temporary intervention, and distinguishing failure to identify one procedure from inability to design a reliable alternative.

## The question and its scope

The distinction between holding and releasing already has a place in the literature. Weinberger’s *Intervening and Letting Go* discusses a gas with a movable piston and models appropriate when its volume is fixed or free. On the source account available here, this discussion treats removing a constraint as an action against which a model’s adequacy can be assessed. The question here is narrower: what can an exhaustive collection of holding outcomes establish about release? [Weinberger 2023, §5](https://link.springer.com/article/10.1007/s10670-021-00463-0)

Initial-state dependence is also established territory. The available account of Blom, Bongers, and Mooij’s causal constraints models describes a construction that incorporates equilibrium outcome maps for every intervention target, including the empty target. A formalism that can represent all those maps need not make some of them inferable from the others. Here the missing information concerns an unclamped outcome from a particular prepared state. [Blom, Bongers, and Mooij 2020, §§2.2–3.4](https://proceedings.mlr.press/v115/blom20a/blom20a.pdf)

Dash’s discussion of manipulation and equilibration supplies a related reason to attend to temporal information. The argument below makes a specific claim about identification: equality across a stated experimental menu can coexist with disagreement outside it. [Dash 2005, §6](https://proceedings.mlr.press/r5/dash05a/dash05a.pdf) The distinction between pulse and press interventions likewise precedes this argument. The available account of publisher excerpts for Ryan and Dablander distinguish a change at a particular time from a sustained intervention. [Ryan and Dablander 2025, §1 and Appendix A](https://www.tandfonline.com/doi/abs/10.1080/00273171.2025.2522733)

These literature descriptions and bibliographic details have not been independently verified here. In particular, the available account of Ryan and Dablander rests on publisher excerpts, not full-text access. No priority claim follows from these comparisons, and none of these authors is being charged with inferring release outcomes from the restricted evidence considered below. The mathematical argument is self-contained.

## Systems and evidence

Let two observed real-valued quantities obey

\[
\dot x=x-x^3+y,\qquad \dot y=-ky,\qquad k>0.
\tag{1}
\]

Write \(\mathcal C\) for this family of systems. Its members differ only in the positive constant \(k\). When \(y=0\), the \(x\) equation has stable equilibria at \(-1\) and \(1\), separated by an unstable equilibrium at \(0\). Positive \(y\) supplies an upward influence whose duration depends on \(k\).

These are mathematical systems, not fitted models of a particular treatment or apparatus. Their possible application is structural: a variable with two self-maintaining states receives temporary support. The equations carry the argument. They are smooth and have unique solutions for all future times. Indeed, \(y\) decays exponentially, and the negative cubic term keeps \(x\) bounded.

A *persistent coordinate clamp* replaces the equation for each selected coordinate by the requirement that it remain at a specified constant. Equations for free coordinates remain unchanged. Initial values of the free coordinates are specified, and the readout is the limiting pair \((x,y)\).

Let the evidence \(E\) contain:

- Every limiting outcome under an \(x\) clamp, for every clamp value and initial \(y\).
- Every limiting outcome under a \(y\) clamp, for every clamp value and initial \(x\).
- Every limiting outcome under a joint clamp, at every pair of values.
- The uncontrolled baseline trajectory from \((-1,0)\).
- The complete unclamped and clamped equilibrium catalogues, with qualitative stability classifications.

The first three items exhaust the nonempty persistent coordinate clamps. They include initial-state dependence, rather than assuming each clamp has a unique attracting equilibrium. The baseline trajectory is constant. Arbitrary uncontrolled trajectories are excluded: knowing the uncontrolled endpoint from every initial state would already supply the release outcome in question.

Every member of \(\mathcal C\) agrees on \(E\).

To prove this, first clamp \(x=a\). Then \(\dot y=-ky\), so the limiting pair is \((a,0)\), regardless of \(k\) and the initial \(y\).

Next clamp \(y=b\). The remaining equation is

\[
\dot x=x-x^3+b.
\tag{2}
\]

It contains no \(k\), so the entire free trajectory is identical across the family for any specified initial \(x\). Each trajectory has a limit: the cubic points inward for large absolute \(x\), and between consecutive roots the derivative has a constant sign. A solution moves monotonically toward a root and cannot cross it, by uniqueness. A solution starting at a root stays there. Multiple roots and one-sided attraction do not disturb agreement because the scalar equation is identical.

A joint clamp fixes the pair by stipulation. The baseline \((-1,0)\) is an equilibrium for every \(k\).

Finally, the unclamped equilibria are exactly

\[
(-1,0),\quad (0,0),\quad (1,0).
\]

Their Jacobian matrices are triangular, with eigenvalues \(1-3x^2\) and \(-k\). Thus the outer equilibria are asymptotically stable and the middle equilibrium is a saddle for every \(k>0\). Under an \(x\) clamp the free coordinate decays to zero; under a \(y\) clamp the free equation is identical across the family. The clamped equilibrium and stability catalogues therefore agree as well, including nonhyperbolic cases of (2). Numerical eigenvalues and relaxation rates are not included in this qualitative evidence.

The information loss has a precise location. Clamping \(y\) replaces the equation containing \(k\). Clamping only \(x\) leaves that equation active, but the endpoint readout discards its rate. Clamping both replaces both equations. No experiment in this menu both permits the two equations to interact away from baseline and retains information about that interaction. Exhaustiveness over targets does not repair what the intervention and readout jointly remove.

## The same release, opposite endpoints

Prepare both systems by jointly clamping

\[
x=-\tfrac12,\qquad y=1.
\]

At time zero remove both clamps. Then \(y(t)=e^{-kt}\). Compare \(k=1/100\) with \(k=100\).

**Slow decay.** For \(k=1/100\), while \(x\in[-1/2,0]\),

\[
x-x^3\geq-\frac{2}{3\sqrt3}>-0.385.
\]

During the first unit of time, \(y(t)\geq e^{-0.01}>0.990\). Hence \(\dot x>0.605\) throughout that interval of \(x\)-values. The trajectory cannot exit through \(-1/2\) and must cross zero within less than

\[
\frac{0.5}{0.605}<0.827
\]

time units.

At \(x=0\), the derivative is \(y(t)>0\) at every finite time, so \(x\) cannot subsequently cross back into negative values. Choose a time \(s\) just after the crossing, with \(0<x(s)<1\), and compare \(x\) with

\[
\dot z=z-z^3,\qquad z(s)=x(s).
\]

Scalar comparison gives \(x(t)\geq z(t)\) for \(t\geq s\), since the additional input \(y\) is positive. As \(z(t)\to1\), it follows that \(\liminf x(t)\geq1\).

For any \(\varepsilon>0\), once \(y\) is sufficiently small, \(\dot x\) is bounded strictly below zero whenever \(x\geq1+\varepsilon\). This follows because \(x-x^3\) is decreasing there and is negative at \(1+\varepsilon\). Boundedness forces eventual entry below that level, and the vector field prevents upward recrossing. Thus \(\limsup x(t)\leq1\). The released system converges to \((1,0)\).

**Fast decay.** For \(k=100\), the total upward input is

\[
\int_0^\infty y(t)\,dt=0.01.
\]

Before any hypothetical first crossing of zero, \(x\geq-1\), because at \(-1\) its derivative is positive. On \([-1,0]\), \(x-x^3\leq0\). Integration therefore gives

\[
x(t)\leq-\tfrac12+\int_0^t y(u)\,du\leq-0.49.
\]

This contradicts a first crossing of zero, so the bound holds for all time:

\[
-1\leq x(t)\leq-0.49.
\]

For any \(0<\varepsilon<0.51\), the continuous function \(-(x-x^3)\) has a strictly positive minimum \(m\) on \([-1+\varepsilon,-0.49]\). Eventually \(y<m/2\). Thereafter \(\dot x<-m/2\) throughout that interval. The trajectory must enter \([-1,-1+\varepsilon]\), and the negative derivative at its upper boundary prevents upward exit. Since \(\varepsilon\) can be arbitrarily small, \(x(t)\to-1\). The limiting pair is \((-1,0)\).

The same estimates work for every \(0<k\leq1/100\) and every \(k\geq100\), respectively. These are sufficient ranges, not an exact dividing threshold.

We have therefore established:

> Over \(\mathcal C\), the limiting outcome of simultaneous release from \((-1/2,1)\) is not identified by \(E\). The same nonidentification holds over any larger admissible class containing the displayed pair.

Any rule assigning a unique release endpoint from \(E\) alone must assign the same answer to both systems, and hence fail for at least one. This is a limitation on entailment from specified evidence, not a prohibition on prediction informed by further assumptions.

## What the basin explanation must say

The crossing of \(x=0\) in the slow system is not a crossing of that autonomous system’s basin boundary.

For a fixed \(k\), a basin of attraction consists of full states \((x,y)\) whose future trajectories converge to the relevant attractor. If a trajectory converges to \((1,0)\), every later state on that trajectory has the same limiting outcome. The trajectory remains in that basin throughout its autonomous evolution. In particular, \((-1/2,1)\) already belongs to the positive equilibrium’s basin in the slow system. The same coordinate pair belongs to the negative equilibrium’s basin in the fast system.

The sign of \(x\) does not by itself classify full-system basin membership when \(y\ne0\). With \(y=0\), zero separates the positive and negative outcomes of the scalar \(x\) dynamics. With positive \(y\), the line \(x=0\) is not invariant: there \(\dot x=y>0\). Crossing it supplies a useful sufficient condition for the positive outcome in our proof, rather than marking passage between basins of the same released system.

The explanatory contrast is consequently between two vector fields and their different basin assignments. Slow decay permits enough upward motion for \(x\) to become positive while the influence persists; comparison then establishes convergence to \(1\). Fast decay supplies too little total input, leaving \(x\) bounded away from zero on the negative side. These inequalities explain the different outcomes without misdescribing either autonomous trajectory.

A basin description could state the relevant difference without specifying an exact rate. The result does not require every adequate explanation to mention \(k\). It establishes that equilibrium locations, qualitative stability, and the stipulated clamp outcomes do not determine the needed basin assignment.

## An application: choosing the order of withdrawal

Suppose the objective is a lasting transition to \((1,0)\), starting from the jointly prepared state \((-1/2,1)\). Assume the functional form (1) is independently justified, while \(k>0\) remains unknown. This assumption matters: the following guarantees concern \(\mathcal C\), not every system compatible with the endpoint evidence.

Simultaneous release cannot be certified as successful throughout \(\mathcal C\). Nevertheless, a different withdrawal procedure can. It uses the same prepared state and removes the same two clamps, but in stages:

1. Release \(x\), keeping \(y=1\) for one time unit.
2. Release \(y\) as well.

During the first stage,

\[
\dot x=x-x^3+1,
\]

independently of \(k\). While \(x\in[-1/2,0]\),

\[
\dot x\geq c:=1-\frac{2}{3\sqrt3}>0.615.
\]

It therefore crosses zero within at most \(1/(2c)<0.814\) time units. It cannot return through zero while \(y=1\), since the derivative there is \(1\). At the second release, \(x>0\) and \(y=1\), for every member of the family.

Any released state with \(x>0\) and \(y\geq0\) converges to \((1,0)\) in this family. To verify this, compare its \(x\) trajectory with the unforced equation \(\dot z=z-z^3\) from the same positive initial value. That solution tends to \(1\), whether it starts above or below \(1\), and scalar comparison gives \(x\geq z\). Thus \(\liminf x\geq1\). Since \(y\to0\), the upper-bound argument used in the slow-decay proof gives \(\limsup x\leq1\). The staged procedure therefore succeeds for every \(k>0\).

The order matters. Consider the reverse procedure: release \(y\) first, keep \(x=-1/2\) for a fixed finite time \(T\geq0\), and then release \(x\). At that final release the state is

\[
\left(-\tfrac12,e^{-kT}\right).
\]

Writing \(t\) for time since this release, the remaining input is \(y(t)=e^{-k(T+t)}\).

For every fixed finite \(T\), sufficiently slow members still converge to \((1,0)\). Specifically, if

\[
0<k\leq\frac{0.01}{T+1},
\]

then \(y(t)\geq e^{-0.01}>0.990\) for the first unit of released time. The slow-decay proof applies unchanged.

For \(k\geq100\), by contrast,

\[
\int_0^\infty y(t)\,dt=\frac{e^{-kT}}{k}\leq0.01,
\]

so the fast-decay proof applies and the endpoint is \((-1,0)\). No fixed finite waiting period in this reverse order removes the disagreement across \(\mathcal C\).

This is more than a recommendation to collect a time trace or measure a rate. It answers a control question despite continued uncertainty about that rate. Under the justified family restriction, keeping support in place while allowing \(x\) to move guarantees a lasting transition; allowing support to decay while preventing that movement does not give a uniform guarantee. The one-unit duration is a sufficient bound in the units of (1), not a claim about an optimal duration or an arbitrary physical system.

The successful procedure uses no additional measurements to estimate \(k\). Its guarantee comes from the shared dynamics while \(y\) is clamped and the convergence result for positive \(x\). These assumptions are not consequences of \(E\) alone. Enlarging the model class preserves the original impossibility result whenever the two counterexample systems remain admissible, but need not preserve the staged procedure’s guarantee.

The distinction is useful in assessing interventions intended to leave a lasting effect. One may be unable to certify a proposed withdrawal while still being able to certify an alternative. Identification of an unknown parameter, identification of one procedure’s outcome, and successful choice among procedures are different tasks.

## What experimental completeness amounts to

One might object that the example merely loses timing information at equilibrium. That is part of its mechanism, but losing timing does not necessarily lose endpoints. Multiplying both equations of an autonomous system by the same positive constant changes its clock while preserving its state-space paths and release outcomes. Here a relative rate changes the final attractor, while remaining invisible to every experiment in the specified menu.

Nor is the problem a lack of clamp settings. Every value, target, and initial state allowed by the menu is already covered. Both coordinates are read out, joint clamps are included, and all equilibrium locations and qualitative stability classifications are supplied. More exhaustive coverage along those dimensions cannot distinguish the systems.

The exclusion of arbitrary uncontrolled initial states is essential. If those outcomes were known, the disputed release outcome would already be known. But preparation ability does not entail that every procedure following preparation has been observed. Preparing a state and maintaining a clamp is one experiment; preparing it and leaving both coordinates free is another. The result concerns the inference between them.

A sufficiently rich dynamical or initial-state-sensitive equilibrium model can represent the missing outcome. Representational adequacy does not establish that the available evidence identifies that model. Our pair agrees on the supplied outcome maps while disagreeing on the relevant unclamped map.

This gives the philosophical contribution a specific form. Equivalence relative to an experimental menu licenses substitution only for the questions that equivalence preserves. Here it does not license substituting one model for the other when evaluating simultaneous withdrawal. The distinction cannot be repaired merely by calling the original intervention catalogue complete: its completeness is indexed to procedures and readouts. The withdrawal-order result then shows why this limitation matters for action. Evaluating a permanent clamp and choosing how to end a temporary clamp impose different demands on a model.

Additional evidence can of course change the answer. A decay trace under an \(x\) clamp reveals \(k\); a release experiment directly measures the disputed outcome; justified rate bounds or basin information can settle it without an exact parameter estimate. These are routes beyond the restricted menu, not consequences of enlarging its already exhaustive target-and-value coverage.

The limits of the result should remain explicit. It establishes neither a general failure of equilibrium causal modeling nor a universal need for temporal measurements. It does not locate the exact transition between positive and negative outcomes as \(k\) varies, characterize every basin, or prove that staged withdrawal succeeds outside \(\mathcal C\). Its substantive conclusions are narrower: the stated endpoint evidence fails to identify simultaneous release, and, under an explicit shared dynamical restriction, withdrawal order permits a reliable alternative without resolving the hidden rate.

## Bibliography

Blom, Tineke, Stephan Bongers, and Joris M. Mooij. 2020. “Beyond Structural Causal Models: Causal Constraints Models.” *Proceedings of the 35th Conference on Uncertainty in Artificial Intelligence (UAI 2019)*, PMLR 115. [Paper](https://proceedings.mlr.press/v115/blom20a/blom20a.pdf).

Dash, Denver. 2005. “Restructuring Dynamic Causal Systems in Equilibrium.” *Proceedings of the Tenth International Workshop on Artificial Intelligence and Statistics*. [Paper](https://proceedings.mlr.press/r5/dash05a/dash05a.pdf).

Ryan, Oisín, and Fabian Dablander. 2025. “Equilibrium Causal Models: Connecting Dynamical Systems Modeling and Cross-Sectional Data Analysis.” *Multivariate Behavioral Research*. [Publisher article](https://doi.org/10.1080/00273171.2025.2522733). The available source account was based on retrieved publisher excerpts.

Weinberger, Naftali. 2023 [online 2021]. “Intervening and Letting Go: On the Adequacy of Equilibrium Causal Models.” *Erkenntnis* 88: 2467–2491. [Article](https://doi.org/10.1007/s10670-021-00463-0).
