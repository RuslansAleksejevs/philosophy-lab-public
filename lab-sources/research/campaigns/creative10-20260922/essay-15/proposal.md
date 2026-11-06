# Exact proposal for independent precheck

Working title: **Knowing What Happens While You Hold It Is Not Knowing What Happens When You Let Go**

## Thesis and restricted claim

Agreement under every nonempty persistent perfect clamp, even from arbitrary starting states and supplemented by identical baseline observations and identical equilibrium/stability catalogues, does not entail agreement about the final equilibrium reached after removing a joint clamp. Consequently, adequacy supported by an exhaustive menu of persistent interventions cannot be extended to intervention withdrawal simply because withdrawal uses the same variables and eventually measures the same equilibrium outcomes. Experimental sufficiency must be assessed relative to allowed sequences of actions, not only the list of variable targets and values.

This does not challenge the mathematical adequacy of a fully specified dynamical model or of a causal constraints model carrying the complete initial-state-to-limit map. It provides an evidential limit on inferring that map from a particularly rich but incomplete experimental menu. It extends, rather than refutes, Weinberger's treatment of intervening and letting go.

## Exact model and evidence class

For each k > 0 let D_k have two observed, real-valued variables:

    dx/dt = x - x^3 + y
    dy/dt = -k y.

A perfect persistent clamp replaces each targeted variable's equation by holding that variable at its stipulated constant. The experimentally observed outcome is the limiting pair, not elapsed relaxation time or a transient trace. All experiments begin with complete, specified state values; there are no hidden variables or ambiguous treatment versions.

The evidence class E consists of (i) all nonempty persistent coordinate clamps, including joint clamps, at every real value, from every initial state; and (ii) the unmanipulated baseline (-1,0). E deliberately does NOT include arbitrary unclamped initial-state experiments. Those would contain the information the release test is designed to elicit.

For do(x=a), y tends to zero for every initial y and every k, so the outcome is (a,0). For do(y=b), x follows the same scalar equation dx/dt=x-x^3+b for every k, from the same initial x; bounded scalar trajectories converge to a root, with the same root selected for each k. For joint clamps the outcome is stipulated. The baseline stays (-1,0). Thus E is identical for all k, including its initial-state dependence wherever E allows that dependence to be tested.

In addition, every unmanipulated fixed point is (x,0), x in {-1,0,1}. The Jacobian eigenvalues are (1-3x^2,-k): the two outer equilibria are stable and the middle one unstable for all k. Clamped equilibrium sets and their stability classifications likewise agree. Quantitative relaxation eigenvalues are NOT part of the identical evidence. The available stability annotation is qualitative stable/unstable, not a claim about indistinguishable transient experiments.

## Separating experiment and proof

Hold both variables at (x,y)=(-1/2,1), then remove both clamps simultaneously. The starting state is exact and identical. Compare k=1/100 with k=100.

For k=1/100, y(t)=exp(-t/100). On [-1/2,0], x-x^3 is at least -2/(3 sqrt(3)) > -0.385. Until time 1, y is at least exp(-.01) > .990. Hence while x remains in that interval, dx/dt > .605; it crosses zero before time .827. The vector field at zero is positive, so it cannot subsequently cross to negative x. It reaches a positive value; comparison with the autonomous equation x'=x-x^3 then gives liminf x >=1. For any epsilon>0, once y is sufficiently small the vector field is negative at and above 1+epsilon, giving limsup x<=1. Thus the final state is (1,0).

For k=100, y(t)=exp(-100t) and its total time integral is .01. Before any hypothetical first crossing of zero, x remains at least -1 (at -1 the vector field is positive) and x-x^3<=0. Integrating gives x(t)<=-.5+.01=-.49, contradicting any first crossing of zero and establishing the bound globally. Given epsilon in (0,.51), eventually y is smaller than the positive minimum of -(x-x^3) throughout [-1+epsilon,-.49]. The trajectory must enter [-1,-1+epsilon] and cannot exit it upward thereafter. Hence x tends to -1, and the final state is (-1,0).

The separating observation is a different *final attractor*, so objection that equilibrium models deliberately discard timing is insufficient. The distinction matters to whether a temporary intervention has a lasting effect.

## Proposed philosophical increment

The generic claim 'equilibrium data fail to determine dynamics' is old and is NOT the contribution. The result is a precise nonclosure: equality across the exhaustive family of nonempty persistent interventions, including all their initial-state-conditioned outcomes, is not preserved by adding the operation of release. Even knowing the complete fixed-point and qualitative stability catalogues does not repair it. This shows why a model's validated action repertoire cannot be inferred from target coverage alone. The distinction is between completeness of a set of static intervention targets and completeness for a class of experimental protocols.

There is no proposed new grand label or general causal theory. A short essay would defend this exact result and its implications for interpreting experimental adequacy.

## Closest works and adverse overlap

1. Naftali Weinberger, *Intervening and Letting Go: On the Adequacy of Equilibrium Causal Models*, online 2021, Erkenntnis 88 (2023), 2467–2491. https://doi.org/10.1007/s10670-021-00463-0 . Retrieved HTML excerpts include introduction, Sections 2–4, and Section 5 excerpts. His comparison already establishes that models appropriate to clamping and to letting go can have symmetric limitations. Our claimed increment cannot be the importance of release or model-relative adequacy. It is the two-system indistinguishability proof for an exhaustive clamp menu with different released *equilibrium values*. It is not a counterexample to his piston argument.

2. Tineke Blom, Stephan Bongers, Joris M. Mooij, *Beyond Structural Causal Models: Causal Constraints Models*, UAI 2019 proceedings, PMLR 115 (2020). https://proceedings.mlr.press/v115/blom20a/blom20a.pdf . Read retrieved PDF excerpts at pp. 1–8, especially Sections 2.2 and 4, Theorems 1–3. They already show that initial conditions can be indispensable to equilibrium causal semantics and construct richer models. Our proposal does not claim these formalisms fail: their complete initial-state maps distinguish D_.01 from D_100. It asks whether the nonempty intervention portion of those maps plus baseline observations determines the release portion, and supplies a negative answer.

3. *Hamiltonian Monte Carlo methods for efficient parameter estimation in steady state dynamical systems* (2014), https://pmc.ncbi.nlm.nih.gov/articles/PMC4262080/ . Bounded excerpts acknowledge steady-state parameter nonidentifiability and set aside complicated basin effects. We rely on, rather than newly discover, rate nonidentifiability. Proposed gain: an explicit exhaustive perfect-clamp counterexample with attractor disagreement and no hidden state.

4. Dash (2005), *Restructuring Dynamic Causal Systems in Equilibrium*, https://proceedings.mlr.press/r5/dash05a/dash05a.pdf . Search excerpts only: temporal information can be needed to know whether equilibrium manipulation commutes. Not read in full, and not a target of a claimed refutation.

## Limits and rejection triggers

The proof is mathematical, not an empirical assertion that laboratory clamps are perfect. No assertion of absolute priority. Independent review should reject or require revision if existing literature already gives the exhaustive nonempty-clamp equivalence result with differing released attractors, or if the inference is merely a restatement of the initial-condition dependence already proved in CCM work. The philosophical case depends on distinguishing a real extrapolation error, not representing existing authors as making that error. Releasing a clamp is not the same static do-operation as adding another clamp. Its absence from E is explicit, not a hidden technicality.
