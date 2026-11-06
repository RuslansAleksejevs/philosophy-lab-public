# Understanding What Remains Unresolved

Scientists can know how a system would respond to some interventions while remaining uncertain about others. A tempting way to summarize their understanding is to list each relevant intervention, enter the supported outcome, and otherwise list its possible outcomes. Such a summary can preserve every separate answer range and still discard causal understanding. It can omit what the unresolved answers imply about one another.

I demonstrate this loss with two simple devices. Investigators in each case know the same possible outcomes for every individual intervention, but different constraints on their joint response profiles. Those constraints characterize the target's causal organization and warrant opposed inferences from the same experimental discovery. The example supports an adequacy condition for summaries and assessments of partial causal understanding: preserving separate answers does not suffice when understood relations among those answers support further warranted inference.

The claim concerns a restricted, intuitively appealing reporting practice, not an established theory shown to endorse it. A sufficiently expressive stability account can already accommodate relations among responses as objects of understanding. Nor is the formal distinction between joint constraints and separate projections new. The philosophical argument is that this distinction identifies an explanatory loss that an apparently comprehensive inventory of intervention results can conceal. The immediate object understood is the device's response dependence; its bearing on why a particular output occurred is a further, contrast-relative application.

## 1. What model agreement can establish

Consider a scientist with several causal models that remain compatible with the evidence. A model here specifies how a target would respond to interventions, not merely how observed quantities covary. When the models disagree, the scientist need not believe that the target literally has incompatible mechanisms. The models represent alternative possibilities about one mechanism.

Agreement among such models can be epistemically useful. Pearl’s criterion of identification captures an important version of this idea: given assumptions, models with the same observational distribution must agree on the causal quantity at issue. His treatment of interventions distinguishes changing a variable’s generating equation from merely observing its value (Pearl 2010, §3.2.1, especially p. 17). Neither the criterion nor its mathematical extension to several quantities is new here.

There is also an established philosophical connection between model comparison and understanding. Weisberg’s account of robustness concerns common predictions and theorems across models (2006, abstract). More recently, Frigg and Nguyen require stable target behavior across an appropriate model class that includes a truthful model of the target. They distinguish understanding which features matter from understanding which do not, and treat discovering an incorrectly drawn boundary between them as an achievement (2025, §§4.1, 5.1–5.3).

These ideas rule out any claim that understanding under model variation, or learning from unsuccessful robustness tests, is itself a new philosophical contribution. The issue pursued here is narrower: what is lost when a body of unresolved models is summarized by its common answers and separate lists of possible answers to the remaining questions?

Two preliminary distinctions matter. First, the target’s being represented adequately somewhere in a model family is different from our having good evidence that it is. Agreement among an arbitrarily selected set of models does not establish truth. Second, varying an assumption in our description is different from intervening on the system. The former explores uncertainty about the mechanism; the latter explores the behavior of a mechanism taken as fixed. A family of models gives us both dimensions. Losing their relationship can impoverish understanding even when no individual answer becomes false.

## 2. Two kinds of unresolved device

Imagine a deterministic device with two binary inputs, X and Z, and a binary output Y. One means on; zero means off. The device is stable across tests, the inputs can be set separately, and interventions have no effects beyond setting the designated input. These are explicit assumptions of the case. Nothing turns on whether the device is electronic, mechanical, or a laboratory abstraction.

The available behavioral observations concern only the two matched settings. When both inputs are on, the output is on. When both are off, the output is off. Investigators also possess credible construction information. This information differs between two cases.

In the first case, called Selection, the output is wired to one of the inputs, but investigators do not know which. The live models are:

- Y = X.
- Y = Z.

In the second case, called Combination, both inputs enter a gate, but investigators do not know its kind. The live models are:

- Y = X AND Z.
- Y = X OR Z.

The construction information is assumed accurate and sufficient to exclude further functional types. A trustworthy schematic could justify such a restriction before an investigator understood all its consequences. This is not an inference from the two behavioral observations alone. Those observations would support neither restricted family over all conceivable devices. The equations specify response functions, not unique internal implementations: different physical constructions can realize the same function.

Let the actual setting be X = Z = 1, so that Y = 1. The question is how far the investigators understand this output and the dependence it manifests. Consider every possible joint setting of the two binary inputs:

| Inputs set by intervention | Selection: possible Y | Combination: possible Y |
|---|---|---|
| X = 0, Z = 0 | 0 | 0 |
| X = 0, Z = 1 | 0 or 1 | 0 or 1 |
| X = 1, Z = 0 | 0 or 1 | 0 or 1 |
| X = 1, Z = 1 | 1 | 1 |

The columns are identical. For every individual intervention, the two cases have the same set of possible answers. The settled answers also coincide. Both investigators know that switching both inputs off would turn the output off. Neither can say what would happen on switching just X off, or just Z off, from the actual setting.

Yet the uncertainty has a different structure. Define A as the output at X = 0, Z = 1, and B as the output at X = 1, Z = 0. These are responses to alternative tests on the same stable device, not simultaneous values produced by one test.

In Selection, the possible response pairs (A, B) are (0, 1) and (1, 0). The responses must differ. Exactly one of the two separate switch-offs would disable the output.

In Combination, the possible pairs are (0, 0) and (1, 1). The responses must agree. Either each separate switch-off would disable the output, or neither would.

The difference supports opposed inferences from the same discovery. Suppose a test shows that switching X off leaves the output on. In Selection, investigators can infer that switching Z off instead would turn it off. In Combination, they can infer that switching Z off instead would leave it on. The actual test is the same; the initially unsettled individual answers were the same; the warranted transfer of learning is opposite.

No probability assignment is needed. The difference survives complete suspension between the two models within each family. It depends on retaining which possible answers belong together.

## 3. Why the difference concerns causal understanding

The difference between the investigators is not exhausted by their knowledge of which tests would be useful. In Selection, they know that the two inputs have asymmetrical roles: one controls Y and the other does not, although they cannot identify their occupants. In Combination, they know that the inputs have symmetrical roles: they are either jointly required or individually sufficient. These are properties of the actual device's response dependence, given the construction premises. They exclude different causal organizations.

The example becomes a case of understanding when investigators grasp those properties as such. They must connect A and B to the physical interventions, recognize the relevant symmetry or asymmetry, and use the construction premise to explain why the response constraint follows. They must also distinguish uncertainty about the type of one fixed device from variation in type across tests. These are concrete manifestations of interpreted inferential competence in this case, not proposed universal necessary and sufficient conditions for understanding.

Compare an investigator who receives a certified card saying that A and B differ. They can calculate B from A but cannot identify the interventions denoted by the letters. They have conditional information, yet the transfer alone gives us no reason to attribute causal understanding. Even someone who knows the labels might merely memorize the instruction. To distinguish their state from the understanding illustrated here, we should ask why the rule holds and what would defeat it. A response grounded in the controlling-input asymmetry supplies the missing connection between symbols and causal organization.

The stability assumption is revealing. Suppose a selector chooses afresh on every test whether to copy X or Z. Each test still uses a selection rule, but a successful X switch-off no longer establishes what a later Z switch-off will do. The original transfer applies to alternative responses of one fixed response function. Recognizing this restriction demonstrates more than an ability to operate a lookup card: it shows why an apparently similar device falls outside the argument.

A third investigator who knows only the table can correctly answer every settled single-intervention question and give the correct range for every unsettled one. Nevertheless, the table alone warrants neither transfer from the X test to the Z test. It omits the relational fact the first two investigators understand. The comparison therefore establishes a preservation failure, not a sufficient test for understanding based on one successful inference. Where the source representation supports interpreted causal competence, the table can fail to preserve it.

The example does not establish that Selection contains more understanding than Combination or conversely. Their understanding has different content. Both contain more relevant structure than the table alone, relative to their respective true construction information. Assessment should distinguish content and correctness as well as quantity.

How does this bear on explaining the actual output Y = 1? Neither family establishes a fully discriminating explanation even at the functional level. Selection leaves open which input controls the output. Combination leaves open whether both are required or either is sufficient. But each supplies an incomplete answer of a definite kind. Selection tells us that the output is on because its controlling input is on, and that exactly one of the two separate switch-offs would remove that condition. The location of the control remains unknown. Combination instead tells us that the output's dependence on these switches is symmetrical, leaving open whether the on-state is jointly sustained or redundantly sustained.

The reason to count this as partial understanding is positive: investigators already grasp actual structural properties with counterfactual implications. It is not that a final discriminating discovery would be too small to make a categorical difference. Learning which response profile is actual would settle the selected functional inquiry, but would still leave internal pathways, timing, and many other explanatory questions open.

A broader contrast is already resolved. Both families support the output's dependence on changing the joint setting from both inputs on to both off. The finer contrasts involving separate switch-offs remain unresolved. Their organization nevertheless contributes to an incomplete explanation by constraining how those finer why-answers could be completed. This is a modest attribution of causal understanding, not a claim that the concrete internal mechanism has been explained.

## 4. The loss caused by separate answer sets

The general point is elementary but consequential. A model assigns a response to each question in a chosen family. Collect these responses into a profile. A collection of live models supplies a set of possible profiles. If instead we record the possible responses separately for each question, we can combine responses that no live model combines.

Selection and Combination make the loss visible. Their separate answer sets for A and B are both {0, 1}. Treating these sets independently permits all four pairs. Selection permits only two, Combination only the other two. Once the profile structure is removed, the missing constraint cannot be reconstructed from the separate sets.

This is not a demand to retain every detail of every model. Models can be grouped together when they have the same response profile for the questions relevant to the inquiry. Unresolved microscopic differences that alter none of those responses need not be carried forward for that inquiry. Grouping can nevertheless discard timing, internal pathways, or responses to interventions outside the stipulated family. Its faithfulness is relative to the questions being preserved.

It is also not a novel mathematical result. The distinction between a joint constraint and its separate projections is basic, and causal identification can concern a vector of quantities. The philosophical lesson is that an apparently cautious summary of understanding can lose explanatory content without losing a single settled answer, enlarging a single individual answer set, or becoming inaccurate in any entry. Accuracy question by question is therefore an insufficient criterion for preservation of partial understanding.

This matters for assessing what someone has learned. Suppose instruction replaces detailed competing models with an accessible table of “known” and “unknown” intervention outcomes. The table may preserve all individually reportable results and still leave the learner unable to make inferences the original models warranted. The summary does lose facts: it omits the relations among possible causal answers. The important point is that no separate outcome range reveals this loss. An assessment confined to direct answers to the table’s questions would miss it. This is a hypothetical reporting example, not an empirical claim about how often such instruction occurs.

A more informative assessment asks how learning the answer to one unresolved question would affect another, and why. The investigator can reason conditionally: if this input proved dispensable, what would follow about the other, and what feature of the device warrants that inference? Follow-up questions about a changing selector can test whether the fixed-device assumption is understood. Together these probes provide evidence of competence that direct outcome questions alone fail to detect; no finite test is guaranteed to distinguish every instance of understanding from memorization.

## 5. What the result does and does not establish

A first objection is that a relation among unresolved answers is itself a settled answer to a more complex question. Selection answers “Must A and B differ?” affirmatively. A sufficiently expressive inventory of all common truths therefore contains the relation. There is no formal impossibility of representing partial understanding through invariant content.

That is correct. The restriction matters: separate outcome ranges for a fixed intervention family are inadequate, whereas a representation closed under the relevant compound questions need not be. Treating the relation as an object of stable understanding is one way to preserve it. Frigg and Nguyen's framework does not have to be altered to permit richer objects. The example instead tells us why applications of an account must attend to what is being represented and tested. Calling a table exhaustive because it includes every input setting can hide its failure to preserve relations between settings.

A second objection is that the construction information already supplies the understanding, making model comparison redundant. The comparison certainly does not manufacture evidence. But having warranted construction information need not involve grasping all its causal implications. An investigator can know that the device is one of two functional types without recognizing what that rules out about its responses. Model comparison makes the constraint explicit. The explanatory achievement is using the justified structural premise to understand the device, not deriving truth from the mere number of models.

The strength of that premise is a genuine limitation. If an unconsidered third type is a serious possibility, Selection's transfer rule might fail. We should distinguish understanding the conditional implications of a hypothesized family from warranted understanding of the target through that family. The latter requires good grounds for the relevant structural exclusions. These grounds can be fallible; agreement within an arbitrarily chosen family does not supply them. The example establishes a possibility under explicit assumptions, not the adequacy of a particular scientific ensemble.

A third objection denies that constraints on possible explanations supply explanatory understanding. They do not identify which concrete mechanism operated. Perhaps they are only useful preparations for explanation.

The response depends on keeping the object and level clear. If the object is the detailed internal pathway, our investigators do not understand it. If it is the device's functional dependence, knowing that exactly one input controls the output already characterizes a real causal property, despite not locating its occupant. It excludes joint necessity and redundant sufficiency and explains the opposed responses to the two separate switch-offs. That is an intelligible subject of partial causal understanding. Its connection to the actual occurrence is the incomplete, contrast-relative answer described above, not a complete mechanistic account.

Some disjunctions offer almost no understanding. “The device has some mechanism” contributes little. The present attribution relies on more: a justified constraint on the target's response dependence and the investigator's interpreted use of it to explain causal exclusions and their consequences. The lookup-card case shows why neither a bare disjunction nor successful answer transfer suffices by itself.

Finally, the use of complete response profiles should not be confused with recovering a joint distribution of counterfactual outcomes from separately identified intervention distributions. Our devices are deterministic and fixed, and stronger construction information restricts the complete profiles. The argument concerns information lost when those profiles are summarized, not a method for reconstructing them from marginal data. Nothing in it warrants that reconstruction in a more general stochastic case.

## 6. Partial understanding as organized possibility

An unresolved model choice need not force a choice between pretending to know the mechanism and declaring that nothing is understood. Common intervention answers can establish a limited causal dependency. Relations among disputed answers can establish more: a structured account of which explanations remain possible and what discovering one feature would reveal about another.

The two devices demonstrate why this additional content deserves explicit recognition. Their separate possible answers coincide completely, while their warranted transfers of learning diverge. What distinguishes the investigators is not certainty about more individual outcomes. It is their grasp of different constraints on the mechanism sustaining the actual outcome.

For the stipulated intervention inquiry, partial understanding cannot always be faithfully summarized by separate answer ranges. Some of its content lies in relations among unresolved responses, grasped as constraints on a fixed target. Preserving that content acknowledges an explanatory achievement without pretending that the unresolved profile, or the internal mechanism realizing it, has already been identified.

## References

Frigg, Roman, and James Nguyen. 2025. “Stabilising Understanding.” *Philosophical Studies*. Published online 9 August 2025. https://doi.org/10.1007/s11098-025-02384-y.

Pearl, Judea. 2010. “The Foundations of Causal Inference.” Manuscript dated May 12, 2010, submitted to *Sociological Methodology*. https://web.cs.ucla.edu/~kaoru/r355-corrections.pdf.

Weisberg, Michael. 2006. “Robustness Analysis.” *Philosophy of Science* 73 (5): 730–742. https://doi.org/10.1086/518628.
