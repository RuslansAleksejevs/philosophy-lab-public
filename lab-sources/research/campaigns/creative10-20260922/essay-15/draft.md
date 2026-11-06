# What Holding Cannot Tell Us About Letting Go

Suppose we know what a system eventually does whenever we hold any of its variables fixed. We have not merely tried a few settings. For every nonempty selection of variables, every constant setting and every starting state, we know the final outcome. We also know the system's ordinary resting state. Does this knowledge tell us what happens after we prepare a state by holding variables fixed and then let them go?

It need not. I will construct two smooth systems that agree on that entire collection of experiments but settle at opposite stable equilibria after the same release. Their difference is not confined to how quickly they settle. They disagree about where they end up.

This establishes a limited claim about experimental evidence. Complete coverage of the variables and values one can hold fixed is not complete coverage of the procedures one can perform with them. More specifically, the limiting outcomes of all nonempty persistent coordinate clamps need not determine the limiting outcome after a joint clamp is removed. The qualification about what is measured matters: we record the final pair of values, not the intervening time trace. The qualification about ordinary observations also matters: the systems share one specified baseline, not every possible uncontrolled history.

The value of the result is to make an evidential limit precise. It is neither a new theory of causation nor a discovery that removing a constraint can matter.

## The distinction already in place

Weinberger's *Intervening and Letting Go* examines a gas with a movable piston and the different causal models appropriate when the piston is free and when its volume is fixed. His argument gives removing the constraint a place alongside imposing it: a model's limitations concerning one action need not make it inferior to a model with corresponding limitations concerning the other. Thus the distinction between holding and releasing, and the need to assess models relative to actions, are already explicit in the literature. My construction extends that discussion by asking what an exhaustive family of holding experiments can establish about release. [Weinberger 2023, §5](https://link.springer.com/article/10.1007/s10670-021-00463-0)

Initial-state dependence at equilibrium is also familiar. Blom, Bongers and Mooij show that equilibrium causal descriptions may need information about initial states, and their causal constraints models can represent the relevant dependence. Their general construction incorporates the outcome map for every intervention target, including the empty target. The issue here is whether its nonempty-target portion, supplemented by a baseline, determines the missing release outcome. A formalism capable of recording all these maps does not imply that evidence for some of them determines the rest. [Blom, Bongers and Mooij 2020, §§2.2–3.4](https://proceedings.mlr.press/v115/blom20a/blom20a.pdf)

Dash likewise establishes reasons for caution about manipulating models derived at equilibrium, including the need for temporal information when assessing the relation between manipulation and equilibration. The following argument supports a related caution through a different result: equivalence between two systems across an entire specified experimental menu, followed by disagreement outside it. [Dash 2005, §6](https://proceedings.mlr.press/r5/dash05a/dash05a.pdf)

The proposed contribution is this explicit separation. It does not depend on attributing an unrestricted inference from holding to release to any of these authors.

## Two systems and a rich experimental menu

Consider two observed real-valued quantities, x and y. For any positive constant k, let their dynamics be

\[
\dot x=x-x^3+y,\qquad \dot y=-ky.
\tag{1}
\]

The dot means rate of change. Without y, the x equation has two stable resting values, -1 and 1, separated by an unstable resting value, 0. Positive y pushes x upward. The constant k controls how quickly that push disappears when y is free to change.

These equations define a mathematical example, not a fitted model of a particular organism or apparatus. One can think of x as a quantity with two self-maintaining states and y as a temporary influence. The equations, rather than this interpretation, carry the argument. They are smooth. Solutions are unique and exist for all future times: y decays exponentially and is bounded, while the negative cubic term prevents x from escaping to infinity.

A *persistent coordinate clamp* holds the selected coordinate or coordinates at stipulated constants indefinitely. It replaces the equations for those coordinates; the equations for any coordinates left free remain unchanged. The starting values of the free coordinates are specified. The readout is only the limiting pair of coordinate values.

Give the investigator the following evidence:

- Every limiting outcome from clamping x, for every constant x and every starting y.
- Every limiting outcome from clamping y, for every constant y and every starting x.
- Every limiting outcome from clamping both coordinates, at every pair of constants.
- The unmanipulated baseline trajectory starting at (-1,0).

The first three items exhaust all nonempty persistent coordinate clamps for a two-variable system. The last trajectory is simply constant. We do not grant the investigator the unclamped outcomes from every other starting state. That would grant the very release information at issue.

All systems in (1), whatever their positive k, agree on this evidence.

First, hold x at a. The remaining equation is \(\dot y=-ky\), so y tends to zero. The limiting pair is (a,0), independently of k and the initial y.

Second, hold y at b. The remaining equation is

\[
\dot x=x-x^3+b.
\tag{2}
\]

This equation contains no k. For the same starting x, every system therefore follows the same x trajectory and reaches the same limiting root. To see that a limit exists, the cubic points inward for sufficiently large absolute x. Between consecutive roots the derivative has a constant sign, so a solution moves monotonically toward a root; it cannot pass through a root because solutions are unique. Starting at a root leaves x there. Multiple roots and one-sided convergence cause no disagreement between the systems, since the scalar equation is identical.

Third, holding both variables fixes the observed pair by stipulation. Finally, (-1,0) is a fixed point of every system. This proves equality of the specified evidence, including all allowed dependence on initial states. Nothing hinges on sampling too few clamp values.

We can strengthen the evidence further without distinguishing the systems. Their complete unclamped fixed-point catalogue is

\[
(-1,0),\quad (0,0),\quad (1,0).
\]

At a fixed point, the Jacobian is triangular, with eigenvalues \(1-3x^2\) and \(-k\). Thus the two outer fixed points are asymptotically stable and the middle one is a saddle for every k>0. The clamped fixed-point catalogues and stability classifications also agree. Under an x clamp the free coordinate decays to zero; under a y clamp the entire free equation is identical. This includes any nonhyperbolic or one-sided cases in (2).

The extra information is qualitative stability, not numerical relaxation rates. Knowing the eigenvalue -k would obviously disclose k. Agreement on where equilibria lie and whether they attract nearby states does not amount to agreement on every basin of attraction.

## A common release with opposite outcomes

Now compare k=1/100 with k=100. Prepare both systems by jointly clamping

\[
x=-\tfrac12,\qquad y=1.
\]

Remove both clamps simultaneously, calling that moment time zero. The systems start with exactly the same observed state and obey the same x equation. Their released y values are

\[
y(t)=e^{-kt}.
\]

The slow system will end at (1,0); the fast system will end at (-1,0). Here is a proof that does not rely on a plotted trajectory.

**Slow decay.** Take k=1/100. On the interval \([-1/2,0]\),

\[
x-x^3\geq-\frac{2}{3\sqrt3}>-0.385.
\]

For the first unit of time, \(y(t)\geq e^{-0.01}>0.990\). Consequently, while x remains between -1/2 and 0 during that time, its derivative exceeds 0.605. It cannot exit through the lower boundary and must cross zero in less than \(0.5/0.605<0.827\) time units.

At x=0 the derivative is y(t)>0 at every finite time. After crossing into positive values, x therefore cannot cross back into negative values. Choose a time s just after the crossing, when \(0<x(s)<1\). Compare x with the solution z of

\[
\dot z=z-z^3,\qquad z(s)=x(s).
\]

Because x has the additional positive input y, scalar comparison gives \(x(t)\geq z(t)\) for t≥s. The function z increases to 1. Hence \(\liminf x(t)\geq1\).

For the other direction, fix any ε>0. Once y is sufficiently small, the derivative of x is bounded strictly below zero whenever x≥1+ε: the cubic is decreasing there and its value at 1+ε is negative. Boundedness of x implies that it must eventually fall below 1+ε if it is above that level; the vector field then prevents upward recrossing. Thus \(\limsup x(t)\leq1\). Since ε was arbitrary, x tends to 1. The limiting pair is (1,0).

**Fast decay.** Take k=100. The total upward input is now small:

\[
\int_0^\infty y(t)\,dt=\frac1{100}=0.01.
\]

Before any hypothetical first crossing of zero, x remains at least -1: at -1 its derivative is y(t)>0, so it cannot cross that boundary downward. Throughout [-1,0], \(x-x^3\leq0\). Integrating the x equation therefore gives, before any such crossing,

\[
x(t)\leq-\tfrac12+\int_0^t y(u)\,du
\leq-0.49.
\]

This contradicts a first crossing of zero. The bound holds for all time: \(-1\leq x(t)\leq-0.49\).

To establish the exact limit, choose any \(0<\varepsilon<0.51\). The continuous function \(-(x-x^3)\) has a strictly positive minimum m on \([-1+\varepsilon,-0.49]\). Eventually y<m/2. Thereafter, whenever x is in that interval, \(\dot x<-m/2\). It must enter \([-1,-1+\varepsilon]\), and the negative derivative at the upper boundary prevents it from leaving upward. Since ε can be arbitrarily small, x tends to -1. The limiting pair is (-1,0).

The same prepared state thus belongs to different basins in the two systems. The slow influence lasts long enough to push x across zero; the fast influence does not. Once that crossing has or has not occurred, the system's own dynamics sustain the difference after y has disappeared entirely.

## What the separation establishes

Let the evidence described above be E, and let Q ask which equilibrium follows the specified joint-clamp release. The two systems agree on E and disagree on Q. Any rule that gives a unique answer to Q solely from E must give the same answer for both systems and therefore be wrong for at least one. This is a failure of identification, not merely a warning that extrapolation might be risky.

The result survives several possible repairs to the original experiment. Trying more constant values will not help: all values are already included. Trying both variables together will not help: joint clamps are already included. Measuring both coordinates rather than one will not help: the readout already contains the complete limiting pair. Recording the initial state of every clamping experiment will not help: those states were already specified. Nor will listing all equilibria and their qualitative stability.

What would help is a different kind of evidence. A time trace while x is held fixed reveals y's decay rate. A release experiment from the prepared state reveals the answer directly. Knowledge of the relevant rate from another source can select the appropriate dynamics. The point is not that release is unknowable. It is that the proposed ways of improving *coverage within the same menu* cannot supply the missing information.

This bears on the evidential role of equilibrium explanations. Suppose the question is why a temporary manipulation caused a lasting transition rather than a return. An account giving every sustained-clamp endpoint, plus the locations and local stability of the free equilibria, still leaves that contrast unresolved. Both candidate systems satisfy that account. The explanatory difference concerns how quickly a temporary influence disappears relative to the system's movement across a basin boundary. A quantity omitted from the endpoint equations can matter to which endpoint is reached after withdrawal.

This does not require a complete microscopic history for every explanation. Here one additional rate, or a suitably chosen experiment, can suffice. It requires matching the evidence to the contrast being explained. Evidence adequate for predicting what happens while a constraint remains in place does not automatically answer why a state persists after the constraint is removed.

## Four objections

**Isn't this just the familiar loss of timing information at equilibrium?** That loss is part of the mechanism, but it does not by itself settle the question posed. Two systems can run at different speeds while reaching exactly the same endpoint after every release. Multiplying both equations by the same positive constant, for example, changes the clock without changing their state-space paths. Our example changes a relative rate and proves a difference in final attractors. It also shows that the rate remains invisible throughout the entire nonempty clamp menu, not merely in an unperturbed equilibrium equation. Those are the additional conclusions.

**Does excluding arbitrary unclamped initial states manufacture the result?** The exclusion is essential and should not be disguised. If we already know the unmanipulated endpoint from every initial state, we already know the endpoint from (-1/2,1). No separation of that kind is possible. But the evidence granted here is substantial: every nonempty clamp from every starting state, a baseline trajectory, and the fixed-point/stability catalogues. The construction identifies exactly what this evidence fails to determine. It rebuts an inference from exhaustive target coverage, not an inference from all conceivable experiments.

There is no practical inconsistency in knowing the outcomes of experiments from specified initial states while not knowing what happens if all constraints are removed from those states. Preparing a state, applying a lasting clamp, and measuring its endpoint is one procedure. Preparing it and leaving every coordinate free is another. Preparation ability does not mean the second experiment has already been performed.

**Doesn't a sufficiently rich causal model already predict release?** Yes. The differential equations do. A complete initial-state-sensitive equilibrium description also distinguishes these systems. The mistake would be to infer possession of that description from agreement on the restricted evidence. Representational sufficiency and evidential sufficiency are different issues: the existence of a suitable model does not mean this experimental menu identifies it.

**Is the result too idealized to concern experimentation?** It is an impossibility claim within a favorable idealization. Perfect clamps, exact initial states and exact limiting readouts remove familiar sources of error. Their presence would complicate inference, but their absence does not restore the missing entailment. Conversely, real experiments sometimes record timing or use additional interventions that distinguish these systems easily. The result gives no reason to dismiss that evidence or to regard actual experiments as restricted to this menu.

The appropriate conclusion is therefore bounded. For persistent coordinate clamps measured only at their limits, complete target-and-value coverage can coexist with ignorance about a subsequent release's final outcome. The word “complete” becomes informative only after the relevant experimental procedures and readouts have been stated. In this example, letting go contributes information that no expansion of the constant-clamp catalogue can replace.

## Bibliography

Blom, Tineke, Stephan Bongers, and Joris M. Mooij. 2020. “Beyond Structural Causal Models: Causal Constraints Models.” *Proceedings of the 35th Conference on Uncertainty in Artificial Intelligence (UAI 2019)*, PMLR 115. [Paper](https://proceedings.mlr.press/v115/blom20a/blom20a.pdf).

Dash, Denver. 2005. “Restructuring Dynamic Causal Systems in Equilibrium.” *Proceedings of the Tenth International Workshop on Artificial Intelligence and Statistics*. [Paper](https://proceedings.mlr.press/r5/dash05a/dash05a.pdf).

Weinberger, Naftali. 2023 [online 2021]. “Intervening and Letting Go: On the Adequacy of Equilibrium Causal Models.” *Erkenntnis* 88: 2467–2491. [Article](https://doi.org/10.1007/s10670-021-00463-0).
