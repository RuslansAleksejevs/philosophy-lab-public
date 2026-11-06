# Independent critique: Settled, but Still Revisable

Date: 2026-09-08 UTC. Critic: a separate AI context, `/root/critic_06`. Status: REVISE. This is philosophical criticism of this essay alone, not an eligibility or truth certificate. The manuscript has not been edited.

## Reconstruction and verdict

The essay's strongest claim is that the permission to retain a justified answer, the permission to stop investigating, and the permission to discard the answer's informational basis are distinct. A summary can preserve the present probability of H exactly while losing distinctions required to exploit anticipated later evidence. If the answer will remain in use, preserving those distinctions can be an epistemically valuable action even though forgetting neither immediately changes the justified credence nor makes subsequent updating irrational.

The argument has five steps: (1) present posterior equality can coexist with unequal posteriors after a further observation; (2) a summary supports exactly the original revisions precisely when it merges no records requiring different responses to the same possible observation; (3) in the example, preventing this loss improves expected accuracy; (4) a continuing epistemic concern supplies a reason for preserving affordable means of improved assessment; (5) with no countervailing disadvantage, that reason becomes a requirement. Steps 1–3 are sound within the model. Step 4 is plausible. Step 5 needs a more explicit normative defense. Originality is also less secure than the current bibliography suggests.

The essay should be revised, not abandoned. Its best feature is the prospective placement of responsibility: act while correction-relevant information is controllably available, without retrospectively declaring the later rational updater irrational. But the descriptive phenomenon has much closer antecedents than the draft acknowledges. The revised essay must make its distinctive normative work carry the contribution.

## 1. Significant missing neighbors narrow the originality claim

Frise already considers an initially justified belief whose source has been forgotten and a later discovery discrediting that source; his paired Cases 3–4 vary the forgotten source while holding the surviving mental position fixed. His target is preservationism about justification. The overlap includes the essay's source-specific challenge and absent initial defect, not merely generic forgetting. Cite and directly distinguish this discussion: Matthew Frise, “Preservationism in the Epistemology of Memory” (2017), §III, pp. 492–497, [primary text](https://philpapers.org/archive/FRIPIT-5.pdf).

Brooks, Frankel, and Kamenica study how additional correlated signals change informational comparisons and distinguish ordinary sufficiency from strengthened comparisons robust to further information. Their framework is an especially close formal neighbor. See “Comparisons of Signals” (2024), [March author manuscript](https://benjaminbrooks.net/downloads/bfk_comparisons.pdf), §§4.1 and 5. The draft's bounded family of prospective audits is narrower than their universal comparison; no identity of the full claims is alleged.

The resulting revision should state the established background first, then identify what remains: a norm governing controllable compression after settlement, assessed relative to anticipated correction practices, together with a separation between downstream credal rationality and upstream informational responsibility. Do not present a fresh example or conditional-independence notation as evidence of a fresh philosophical discovery. The conjunction may still be worthwhile, but adding these citations without changing the contribution statement would leave the principal objection unanswered.

## 2. Expected improvement does not yet entail a duty

The most serious substantive gap occurs in §3, where an expected accuracy advantage becomes an ought. A reason to improve one's position does not automatically prohibit declining the improvement. The essay itself accepts that adequate settlement can be permissible without exhausting available epistemic gains.

Consider a satisficing investigator. She intends to continue using an answer whose confidence exceeds her adequately justified acceptance threshold, while remaining rationally responsive to what later arrives. She has no further project of making every future credence as accurate as possible. Both retention policies permit that practice. Preserving the label would improve expected accuracy; she grants this reason. She denies that continuing reliance commits her to take every negligible-cost improvement. This is a disagreement over the force of epistemic reasons, not an objection defeated by listing privacy or storage costs.

Friedman's ZIP does not close this gap. It requires necessary means and expressly distinguishes alternative strengths of instrumental principles, including satisficing and maximizing formulations: [The Epistemic and the Zetetic](https://jfriedmanphilo.github.io/E%26Z.pdf), §3, manuscript pp. 6–8. Retention is not necessary to have a justified answer tomorrow or to improve after the audit; both policies improve. The manuscript correctly presents an extension, but must now defend the added normative premise.

A precise repair would separate a weak and a strong conclusion. The weak conclusion is a pro tanto epistemic reason grounded in preventable expected accuracy loss. The stronger conclusion requires an explicit principle against gratuitously choosing a foreseeably inferior informational policy when the cost and other consequences are the same, and the agent continues to endorse appropriately informed assessment of this answer as an aim. Defend that restricted principle rather than sliding from beneficial means to necessary means. Replace “negligible” by “no relevant additional cost” in the clean requirement case; reserve small positive costs for the defeasible reason case. Alternatively, retain only the weaker conclusion and acknowledge that a categorical requirement is unsettled.

A second disagreement concerns the label “epistemic.” Dogramaci supports separating harmful forgetting from irrational surviving belief, but explicitly distinguishes language discouraging forgetfulness from his narrow category of epistemic evaluations: [Forget and Forgive](https://www.sinandogramaci.net/Sinan_Dogramaci/_____files/Dogramaci%2C%20Forget%20and%20Forgive.pdf), §3.3, pp. 670–671. The essay may reject that boundary, but should signal that it uses a broader, aim-based category; Dogramaci is partial support, not an ally on the classification of the proposed ought.

## 3. Link the formal criterion to the value claim directly

The arithmetic checks out. Independent exact enumeration gives present posterior 0.9, present Brier risk 0.09, post-audit retained risk 0.05, and post-audit forgotten risk 0.07. In a mixed audit the coarse posterior really is 0.75. The positive report does not change the prior distribution over the channels' soundness patterns in this symmetric model. No numerical correction is needed.

The general argument can nevertheless be substantially tighter. Restrict initially to a finite probability space, set X equal to H's truth indicator, and let M be a deterministic summary of E. Write q = P(H | E,F) and r = P(H | M,F). Since r is the conditional average of q given M,F, elementary expansion and conditional averaging give:

E[(X-r)^2] − E[(X-q)^2] = E[(q-r)^2].

The cross term vanishes because q is the conditional expectation of X given E,F. Thus the criterion for lossless revision is exactly the zero-loss condition for this expected accuracy comparison; failure on a set of positive probability gives strict loss. In the example, the right-hand side is 0.02. This is a standard conditional-variance fact, not a new theorem. Its explanatory value is that it connects §§2 and 3 and makes “materially improves” assessable without relying only on one example.

Keep separate three standards: preserving exact possible revisions; reducing expected discrepancy over likely revisions; and preventing particularly important failures despite low probability. The draft allows practical approximation but has not specified which of these a norm should prioritize. A short acknowledgment and the expected-discrepancy expression would improve the argument. No universal threshold need be invented.

Also clarify that better expected accuracy is not greater accuracy in every realized world. In the mixed audit, if the selected source randomized and H happens to be true, the correctly informed 0.5 is less accurate in that world than the coarse 0.75. That does not refute the expected-value argument, but it prevents “improves our response” from being mistaken for a guarantee of success in each outcome. All these comparisons remain conditional on the appropriateness of the background model.

## 4. Scope: correction capacity exceeds posterior reproduction

The formal criterion concerns one fixed joint model and a specified observation or family of sequences. It does not settle whether a compressed record is adequate for changing the model, checking an auditor, deciding which investigation to undertake, or testing a newly suspected dependence between sources. This matters in §7, where a trusted custodian and a table of anticipated responses are presented as possible replacements for the original history.

Consider two records that generate identical response tables under the current model, but one reveals that two apparently separate reports copied the same original. A later discovery that this shared upstream process is defective may require rebuilding the dependence model itself. A table retaining only the original model's answers may fail even if it was sufficient for every audit previously encoded. This is outside, rather than a mathematical counterexample to, the stated equality. The philosophical risk is claiming more for that equality than it establishes.

The repair is to describe it consistently as a criterion for posterior reproduction relative to specified assumptions. For a foreseeable challenge to those assumptions, include the relevant model alternatives in the target of retention or retain material allowing reconstruction. The public-life application should be conditional: an arrangement adequate for a limited family of challenges is not thereby generally audit-ready. Since the essay already rejects universal retention, this qualification strengthens rather than defeats its position.

## 5. Significance, structure, and source accuracy

The distinction among the three permissions is clear and useful. The source-label example makes a small informational action matter without assuming bias, dishonesty, current evidential deficiency, or a violation by the eventual recipient. These are substantive strengths. The social extension can become consequential if it specifies who controls retention and what kind of subsequent review the summary is represented as supporting.

The committee discussion currently moves too quickly from an individual's reason to what a community “needs.” A minimal allocation example would help: the summarizer controls a cheap dependency map; recipients cannot reconstruct it; the summary is supplied for continued use under an established correction procedure. Then the conclusion concerns the summarizer's available action. A general theory of collective obligations is unnecessary. Nor is every omission misleading; the assurance or reasonable expectation of future review must be present before the misleading-presentation claim follows.

Section 5 on optional stopping is accurate but peripheral to the developed argument. Retain a compact caveat and use the saved space for the normative bridge and the two closest neighbors. The relevant verified sources are [Hendriksen, de Heide, and Grünwald](https://arxiv.org/pdf/1807.09077), §2.1, equations (2)–(4), and [Gandenberger](https://arxiv.org/pdf/1707.00214), §3, manuscript pp. 5–7. Neither establishes a general exemption for biased selection, and the draft does not claim one.

The attribution to [Checking Again](https://jfriedmanphilo.github.io/2CHECK.pdf), §6, manuscript pp. 17–19, is appropriately modest. The Darwiche–Pearl abstract supports the belief-set/epistemic-state distinction, but this is background acknowledgment rather than a result doing independent work: [publisher abstract](https://www.sciencedirect.com/science/article/pii/S0004370296000380). Full verification of its representation theorem was neither needed nor achieved. The bibliography should continue to distinguish preprints from verified publication metadata and avoid invented page correspondences.

## Revision priorities

1. Read and integrate Frise and Brooks–Frankel–Kamenica; rewrite the contribution claim around the remaining normative question.
2. Defend a restricted anti-waste principle or reduce the conclusion to a pro tanto epistemic reason. Make the scope of “ought,” the continuing aim, and the zero-cost idealization explicit.
3. Connect the criterion and accuracy argument through the conditional-variance identity, while preserving the distinction between expected and realized accuracy.
4. Bound claims about response tables and community records to the specified model and correction practice. Give the collective application one concrete responsible actor.
5. Shorten the optional-stopping detour to make room for these changes without padding.

## Verification boundary

I independently checked the load-bearing source passages identified above and recalculated the finite example. Detailed coverage, failed access, retrieval-time boundaries, and the exact-rational calculation are preserved in `sources/critic/retrieval-notes.md`, `sources/critic/check-example.py`, and `sources/critic/check-example-output.json`. Primary-text reading was selective, not exhaustive. Darwiche–Pearl was verified at abstract level only; its PDF extraction was garbled and its screenshot did not produce a visible image. Published PDF access for Brooks–Frankel–Kamenica failed, but the author manuscript was readable. The search does not settle novelty, and I have not inferred statistical or intellectual independence from the existence of a separate critic context.
