# Accuracy Needs a Target: Public Forecasts and Epistemic Claims

## Abstract

A forecast about a person who can respond to it may be assessed against what that person does after disclosure, what she would do without disclosure, or a causal contrast between different messages. These are related but distinct questions. Prior work on self-fulfilling predictions and performative models already emphasizes counterfactual outcomes; this essay does not claim to introduce a new taxonomy or establish priority. It offers a diagnostic schema for keeping the target of an accuracy statistic, the intervention being compared, and the epistemic conclusion drawn from the statistic in view at the same time. An exhaustive search of 65,536 deterministic models shows that one balanced, perfectly accurate disclosed record is compatible with different no-disclosure outcomes and message effects. The result establishes non-identification within the stated model class. It does not show that exposed accuracy is no evidence for a counterfactual, or that a self-fulfilling forecast cannot be knowledge. Those further judgments require assumptions and evidence beyond the observed table.

## 1. What does a perfect record establish?

Suppose I tell a person, before she chooses, “You will pick the blue card.” She picks blue. Repeat the pattern with predictions of both colors, and imagine that every forecast is correct. The record establishes perfect accuracy for a particular arrangement: these predictions were shown, under this policy, before these choices. It does not yet settle what the person would have chosen without seeing them, whether changing the message would change her choice, or what the forecaster knew.

The forecast and choice may match because the forecaster detects a prior preference. They may match because the person follows the forecast. A more complex response may depend on which forecast is shown or how credible it appears. All can fit the same visible record while differing about what would happen if the message were withheld.

My claim is narrow. When a target can respond to a forecast, an accuracy result belongs to an outcome measured under specified conditions. A result for one disclosure policy does not uniquely determine the outcome under a different policy across all compatible causal models. Whether the observed result nonetheless provides evidence for that other outcome depends on background assumptions, knowledge of the response process, and other evidence. Causal influence is a separate matter: a forecast may help cause the event it predicts and still be an informed prediction of that event under the stated conditions.

This is a diagnostic proposal, not a general theory of knowledge. It does not show that a self-fulfilling forecast is defective, that accuracy is useless, or that earlier work has overlooked counterfactual targets. It asks authors and evaluators to state which inference they are making.

## 2. Content, policy, and causal contrast

Let F be a binary forecast shown to a person before a binary choice. Let Y-shown be the choice under a specified policy that discloses F. Let Y-none be the choice under a specified intervention that withholds this forecast. In a population, one can compare F with Y-shown or with the potential outcome Y-none. The first is an accuracy measure for the disclosed policy; the second concerns a no-disclosure outcome. Only one potential outcome is ordinarily observed for each person.

There is also more than one causal contrast. To measure sensitivity to the communicated value, compare the choice after message 0 with the choice after message 1, holding other factors fixed. To measure the effect of the deployment policy, compare the choice after the generated forecast is disclosed with the choice after no message is received. These contrasts can differ. Neither is the same as an accuracy score.

A further distinction concerns what proposition is under discussion. Someone may assert p, such as “the price will rise by Friday,” and an evaluator may ask whether that same belief would remain justified, true, and appropriately connected to the fact in a world where no prophecy was made. That is a counterfactual test of the same belief content. Alternatively, someone may assert a policy-indexed claim: “the price will rise if this report is circulated.” That differs from the claim that the price would rise if the report were withheld. The first can be true because investors respond to the report; the second asks about another policy.

These formulations should not be collapsed. A counterfactual test can hold a belief's content fixed while evaluating its truth or warrant in another world. A forecast can also explicitly concern an outcome under one policy rather than another. Specifying the policy does not by itself decide which content the speaker intended, and learning that a report caused an outcome does not by itself settle whether the speaker knew the outcome under actual use.

## 3. What the finite search shows

I tested whether perfect accuracy under disclosure can coexist with different no-disclosure choices and message effects. The search enumerated a bounded class of deterministic models. There are two independent fair binary latent features, H and V, with four equally weighted states. Every Boolean function from those features to a binary forecast F is included: 16 forecast rules; F is generated from the state before disclosure. The person's response is any Boolean function of H, V, and the received message, where the message can be none, 0, or 1. The same response rule is evaluated under each message, including none; that stability across the compared regimes is an assumption of the model. This yields 4,096 response rules and 65,536 forecast-response models.

For each model, the disclosed choice is the response to the generated forecast; the no-disclosure choice is the response to receiving no message. The search keeps exact population counts rather than sampling. Among models with the same balanced, perfectly accurate disclosed table—two observations of (F=0, Y-shown=0) and two of (F=1, Y-shown=1)—there are 1,536 compatible models. Across them, the joint table for F and Y-none takes nine forms, and no-disclosure accuracy ranges from 0/4 to 4/4.

A tracker and a follower illustrate the result. In the tracker model, F=H and the person always chooses H. The forecast and choice share a cause; the person ignores the message. Disclosed and no-disclosure accuracy are both 4/4. Changing the message from 0 to 1 never changes the choice, and disclosing the generated forecast rather than no message has no effect.

In the follower model, F still equals H, but the no-message choice is V and the person follows whichever value she receives. The disclosed table is exactly the same as for the tracker, with perfect balanced accuracy. No-disclosure accuracy is 2/4. The direct message contrast—0 versus 1—changes the choice in all four states; the deployment-policy contrast—generated forecast versus no message—changes it in two of four. A resistant model supplies the opposite case: accuracy is 0/4 when the forecast is disclosed and 4/4 when it is withheld.

The exhaustive count adds information beyond the tracker-follower pair: within this precise class it quantifies how many models match the table, how many no-disclosure tables are compatible, and the range of effects. The pair alone would suffice to refute unique identification. The enumeration does not measure how common any mechanism is and does not establish a theorem about human behavior.

The warranted conclusion is correspondingly limited. Across this class, the same disclosed table is compatible with different no-disclosure outcomes and causal contrasts. Thus that table does not identify a unique no-disclosure accuracy or message effect. This does not mean the table is no evidence at all: under a prior over mechanisms, stability assumptions, or other causal knowledge it might support a probabilistic expectation. Nor does it decide knowledge. A forecaster who knows the response rule and has adequate grounds to expect compliance could know what the person will choose after seeing the forecast. The model concerns compatibility and identification, not an epistemic criterion.

## 4. What the literature already contributes

Goldman's causal theory of knowledge helps explain why causal involvement need not automatically defeat knowledge. In his future-action example, a present intention can cause both a later action and another person's belief about it. The future act need not cause the earlier belief; a common cause may connect them. Goldman also requires an appropriate causal reconstruction and warranted inference (Goldman 1967, pp. 365–366, 370). This is a reason to ask what causal story supports a forecast, not to infer from influence alone that it is unknowable.

Stalkfleet's Gene case presses a difficulty for Goldman's account. Stalkfleet proposes a counterfactual repair asking whether the same belief would remain justified, true, and causally connected if the prophecy had never been made (Stalkfleet 2011, pp. 75–78). This is a test of the belief in a no-prophecy counterfactual; it does not, on the account I can support, show that Stalkfleet substitutes a new proposition for the belief being tested. My distinction is different: it separates that same-belief counterfactual test from an explicitly policy-indexed claim about what happens under circulation versus withholding. The two can inform one another, but the latter is not a correction to Stalkfleet. Whether his full argument already addresses every version of the policy-indexed question remains open here.

King and Mertens distinguish transformative self-fulfillment, where a prediction's use changes whether the outcome occurs, from operative self-fulfillment, where using the prediction contributes to an outcome that would occur anyway; they also identify self-securing prediction (King and Mertens 2023, pp. 10–11). Their account already makes the no-prediction counterfactual central. It explains why “the prediction helped cause the result” and “the result would not otherwise have occurred” are different claims. The present ledger does not add another axis to their taxonomy. It asks an evaluator to make explicit whether the epistemic conclusion concerns the same belief across a counterfactual test, a policy-indexed outcome, the causal effect of deployment, or some combination.

Khosrowi explicitly treats counterfactual forecasts without performativity as accuracy targets and calls for comparing them to the relevant counterfactual outcomes (Khosrowi 2023). That is close to the target distinction used here. I therefore do not claim that this distinction is new or that Khosrowi misses it. My modest proposal is to carry the distinction through one further step in practical argument: state whether a claim about knowledge or warrant follows from the deployed accuracy statistic, from a counterfactual forecast that was separately tested, or from additional causal premises. The present comparison is a diagnostic synthesis, not a demonstrated priority claim.

The performative-prediction literature evaluates models in distributions shaped by acting on them (Perdomo et al. 2020). Kim and Perdomo distinguish accuracy objectives from steering outcomes toward preferred states (2023). These works show why deployed accuracy need not be suspect: a predictor may be useful because it forecasts a response-sensitive environment. They also make the basic contrast familiar. The remaining question in this essay is how that statistic supports a particular proposition and epistemic conclusion, not whether policy-sensitive targets exist.

Kopec's analysis treats reflexive influence probabilistically. The bounded passage verified for this revision gives a case in which observing the predicted outcome has no evidential value for testing the hypothesis (Kopec 2011, p. 1255). The broader range of possible evidential effects was not fully checked in the recorded source review, so I do not rely on that broader characterization here. The point needed for this essay is only that outcome observation and evidential support can come apart under some reflexive mechanisms.

Mertens and co-authors discuss neuroprognosis in which treatment decisions following a poor prognosis can hide a false positive and make it difficult to learn whether the original prognosis was correct (Mertens et al. 2022). This is a system-level learning problem, distinct from the question whether a clinician knows what will happen under a specific treatment policy. It illustrates why an actual outcome can be predicted accurately under one intervention while the evidence base remains weak about another. I do not infer from this example that every individual prediction is unknowable.

The checked literature is bounded. The archived source record includes a full reading of Stalkfleet in the original research stage, but the independent source check relied on an indexed excerpt of pp. 75–77. The remaining cited works were checked in selected excerpts, not in full; Merton (1948), which I do not cite, was logged as metadata only. The novelty search was targeted to nearby cited work, and no exhaustive priority search was made. These limits do not support a claim that the diagnostic schema is original. They support only the narrower claim that it is a useful way to separate questions that can otherwise be conflated in this example.

## 5. The surviving contribution and its limits

The strongest objection is that the essay restates familiar counterfactual and performativity points. That objection is partly right. Khosrowi and King and Mertens already treat counterfactual targets as central, and the finite search is a simple illustration of non-identification. I do not claim that prior work lacks target-indexed accuracy or that this essay introduces a new taxonomy.

What remains is a small analytic aid for evaluating epistemic arguments about public forecasts. It separates four questions: What content did the forecast assert? Under which disclosure policy was its accuracy measured? Which causal contrast is relevant? What additional evidence or assumptions support the conclusion about knowledge? This does not guarantee a correct answer, but it makes a slide between distinct answers visible. The model provides one controlled example of why the questions cannot be answered from the same exposed table alone.

A further objection is that if the only proposition at issue is “she will choose blue after seeing this forecast,” then no-disclosure behavior is beside the point. That is correct. A forecaster may know that policy-conditioned fact despite helping bring it about. The counterfactual ledger becomes relevant when someone moves from that fact to a broader claim: that the person would act the same without intervention, that the predictor has learned an underlying disposition, or that a model will remain accurate under a different use policy. Those inferences require evidence that bridges the change in conditions.

The ledger also does not demand randomized disclosure in every study. Ethical or practical limits may rule that out. It asks only that conclusions stay within the conditions the evidence addresses. If the no-disclosure outcome is not identified, the available data may still inform it under stated assumptions; absent those assumptions or other evidence, the conclusion should remain uncertain.

## 6. A diagnostic ledger

For a forecast about a target who can respond, an evaluator can ask:

1. **What proposition is being assessed?** Specify the action, time, population, and any policy condition in the forecast's content.
2. **Under what policy was accuracy measured?** Say who received which message, when, and what information was withheld.
3. **Which causal contrast is being claimed?** Distinguish changing the communicated value from disclosing the generated forecast rather than sending no message.
4. **What supports the epistemic conclusion?** Separate observed accuracy from evidence about the target's response, counterfactual outcome, or the forecaster's warrant.

This is a practical checklist, not a new theory or a guarantee of novelty. Its use is to prevent one statistic from silently doing the work of several different claims.

## Conclusion

Perfect disclosed accuracy establishes a true record for the disclosed regime. In the finite class studied here, it is compatible with different no-disclosure outcomes and message effects. The exact model search establishes non-identification within its specified deterministic class, not a lack of all evidence, not the frequency of real mechanisms, and not a conclusion about knowledge.

Prior work already studies counterfactual accuracy and the effects of prediction use. This essay's surviving contribution is a modest diagnostic synthesis: state the forecast's content, the policy under which accuracy is measured, the causal contrast, and the epistemic inference separately. A self-fulfilling forecast may or may not be knowledge; answering that question requires more than its accuracy score.

## References

Goldman, Alvin I. 1967. “A Causal Theory of Knowing.” *The Journal of Philosophy* 64 (12): 357–372. https://doi.org/10.2307/2024268.

King, Owen C., and Mayli Mertens. 2023. “Self-fulfilling Prophecy in Practical and Automated Prediction.” *Ethical Theory and Moral Practice* 26: 127–152. https://doi.org/10.1007/s10677-022-10359-9.

Kim, Michael P., and Juan C. Perdomo. 2023. “Making Decisions under Outcome Performativity.” In *Proceedings of the 14th Innovations in Theoretical Computer Science Conference*, article 79. https://doi.org/10.4230/LIPIcs.ITCS.2023.79.

Kopec, Matthew. 2011. “A More Fulfilling (and Frustrating) Take on Reflexive Predictions.” *Philosophy of Science* 78 (5): 1249–1259. https://doi.org/10.1086/662266.

Khosrowi, Donal. 2023. “Managing Performative Models.” *Philosophy of the Social Sciences* 53 (5): 371–395. https://doi.org/10.1177/00483931231172455.

Mertens, Mayli, Owen C. King, Michel J. A. M. van Putten, and Marianne Boenink. 2022. “Can We Learn from Hidden Mistakes? Self-Fulfilling Prophecy and Responsible Neuroprognostic Innovation.” *Journal of Medical Ethics* 48 (11): 922–928. https://doi.org/10.1136/medethics-2020-106636.

Perdomo, Juan C., Tijana Zrnic, Celestine Mendler-Dünner, and Moritz Hardt. 2020. “Performative Prediction.” In *Proceedings of the 37th International Conference on Machine Learning*, PMLR 119: 7599–7609.

Stalkfleet, Kenneth. 2011. “Gettiering Goldman.” *Stance* 4: 69–78. https://doi.org/10.5840/stance201147.
