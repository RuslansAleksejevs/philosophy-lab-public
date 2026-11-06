# Independent argument review — essay 15

Recommendation: **REVISE, retaining the construction and its proof.** I found no fatal mathematical defect. The main repair is to distinguish the established identification result from stronger suggestions about experimental or explanatory necessity. The contribution is a useful exact example; its philosophical significance still needs a sharper account.

## Scope of this review

I read the assigned opponent instructions, question, sources assessment, novelty gate, proposal.md and draft.md. I did not read precheck reports, the other post-draft review, other essays or a global research summary. The first attempted proposal filename, proposal-p1.md, did not exist; I then read the actual proposal.md identified by sources.md. This review independently checks the equations and philosophical inference. I make no new bibliographical or historical-priority judgment and performed no new external source retrieval. The source coverage limitations in sources.md therefore remain in force. No numerical integration is needed for the checks below.

## Charitable reconstruction

The evidence map E reports endpoints under every nonempty coordinate clamp, indexed by the constant clamp settings and the initial values of every free coordinate. It additionally reports one free baseline trajectory and qualitative equilibrium information. The claim is that E is not injective with respect to a different query Q: the endpoint after releasing both coordinates from (-1/2,1). In the family D_k, E is constant for all k>0, whereas Q differs between k=.01 and k=100. Hence Q cannot be identified from E over any model class containing these two systems.

That is a precise result. It does not assert that causal models cannot represent release, that all equilibrium experiments are uninformative, or that interventions cannot identify dynamics. Those would be unfair objections to the actual manuscript.

## Mathematical audit

**The universal clamp quantifiers are satisfied.** There are exactly three nonempty target subsets. Clamping x at any real a leaves y(t)=y(0)e^{-kt}, including negative and zero starting y, and its endpoint is (a,0). Clamping y at any real b leaves the same scalar polynomial differential equation for x in every model. For every finite real starting x, inward drift at large absolute x gives forward boundedness. Between consecutive real roots, the derivative has constant sign; uniqueness prevents finite crossing of a root. Thus the solution has a root as its limit. This covers initial roots, repeated roots, the one-root regime, the three-root regime and their boundary cases. Joint clamping is identical by stipulation. The proof does not silently assume unique clamped equilibria.

**Forward existence and stability claims hold.** The bounded exponential input together with cubic confinement rules out forward explosion. At each free equilibrium the triangular Jacobian has eigenvalues 1-3x² and -k. The two outer points are sinks and the middle point is a saddle for every positive k. Numerical eigenvalues differ, as the manuscript expressly acknowledges. Clamped classifications agree because the free scalar equations either are identical or differ only by a positive rate.

**The slow-release proof works.** Its bound -2/(3√3) is conservative but valid on [-1/2,0]; the sharper bound -3/8 is unnecessary. The positive derivative at the lower boundary excludes a downward exit. If x did not reach zero before .5/.605, integration would contradict x<0. A strictly positive finite-time derivative at zero prevents return across it. Starting the autonomous comparison immediately after crossing makes its initial value lie in (0,1), so its limit is 1. Cubic confinement and the eventual inward vector field at every 1+ε give the asserted upper limit.

**The fast-release proof also works.** Before a putative first zero crossing, x cannot fall below -1 and x-x³≤0. The integrated input bound therefore places x≤-.49 and excludes that crossing. The compact interval [-1+ε,-.49] lies strictly inside (-1,0) when 0<ε<.51, so the claimed positive minimum exists. Eventually negative drift forces entry into the lower trapping interval. Letting ε decrease proves convergence to -1. There is no assumption here that negativity alone implies convergence to the negative sink.

**The identification inference is valid.** Identical E and unequal Q rule out an everywhere-correct, single-valued function of E giving Q on this model class. This establishes logical nonidentification; no statistical assumption is needed.

## Repairable philosophical issues

### 1. State the model-class dependence in the conclusion

Location: “What the separation establishes,” first and final paragraphs, and the opening question.

The precise proof shows nonidentification over a class admitting unknown relative rates and multistability. A reader might otherwise hear the stronger claim that endpoint evidence cannot warrant a release prediction, even when background restrictions select a subclass with a common release outcome. Logical entailment from E alone differs from warranted inference using independently justified background assumptions. The text mostly respects this difference, but the conclusion should carry the restriction explicitly.

Concrete repair: state the theorem in one sentence with its model class and say that identification can be restored either by additional observations **or by independently supported structural restrictions**. For example, within this displayed family, knowledge that k lies in a sufficiently small or sufficiently large range can settle the outcome without identifying its exact value. This follows from the same strict inequalities used in the proof. Do not suggest that uniquely learning k is necessary.

### 2. Separate prediction, identification and explanation

Location: the paragraph beginning “This bears on the evidential role of equilibrium explanations.”

The construction decisively shows that E does not settle which contrast actually occurs. It does not establish a general criterion for adequate explanation, or show that every satisfactory explanation must mention a rate. A coarse account that includes the relevant basin membership can settle the endpoint without an explicit time history or rate parameter. The draft already rejects the demand for a complete microscopic history; extend that restraint to explanatory vocabulary.

Concrete repair: describe relative decay as the mechanism distinguishing **these two candidate dynamical explanations**, while saying that the theorem concerns what the stipulated endpoint data establish. Acknowledge that adequate extra information could be qualitative basin information, rather than timing itself. This preserves the contribution and prevents an unnecessary philosophical overreach.

### 3. Make the positive significance less dependent on an unnamed mistaken inference

Location: “The distinction already in place,” and the objection about familiar loss of timing.

The manuscript commendably disclaims refuting its predecessors. But showing that a deliberately restricted data menu omits a query can remain a technically elegant illustration unless the reason for initially suspecting the menu sufficient is stated clearly. “All targets and all values” sounds exhaustive, yet all these experiments suppress at least one equation. In this triangular system, the k-dependent equation either is replaced by a clamp or has its rate erased by the endpoint readout. That observation is the transparent reason target coverage fails.

Concrete repair: add this mechanistic diagnosis directly after the equality-of-evidence proof. Present the result as exposing an easily overlooked distinction between target coverage and retaining information about freely interacting dynamics. Do not invent a literature consensus that the example overturns. Whether the exact example merits a major originality claim remains unresolved by this argument review.

## Optional strengthening

Briefly note that the separation is not a knife-edge choice of k: the proof's strict inequalities give ranges of sufficiently slow and sufficiently fast rates with the same respective outcomes. An explicit general threshold is unnecessary. This would answer a natural concern about the huge numerical contrast without requiring simulations or a new theorem.

Keep the existing qualifications about the empty intervention and transient readouts. Including all free initial-state endpoints would trivially include Q, while a transient y trace under an x clamp distinguishes the two systems. These are boundaries of the result, not defects that should be concealed.

## Final recommendation and uncertainties

Revise the philosophical framing and retain the mathematical core. The repairs do not erase the interesting feature: even all initial-state-indexed, nonempty clamp endpoints can agree while the same release selects opposite stable equilibria. Remaining uncertainties are historical originality, the appropriate weight of this exact example as a philosophical contribution, and empirical relevance beyond ideal perfect clamps. This review finds no counterexample to the stated mathematical claims and no need to replace the construction.
