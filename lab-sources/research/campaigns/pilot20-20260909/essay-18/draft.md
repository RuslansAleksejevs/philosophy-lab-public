# Understanding What Remains Unresolved

Scientists can know why an outcome would change under one intervention while remaining uncertain about what would happen under another. This familiar situation invites a simple picture of partial understanding. List the relevant questions, enter the answers that are supported, and mark the rest unresolved. More supported answers mean more understanding; uncertainty occupies the gaps.

That picture overlooks a kind of achievement. Scientists may understand how unresolved answers constrain one another, even when they cannot settle any of them individually. This is not merely knowing that their evidence is incomplete. It is knowing something about the causal organization of the system: which combinations of responses are possible, and consequently what learning one response would reveal about another. Two investigators can have precisely the same answers to every individual intervention question, and precisely the same uncertainty about the others, yet possess importantly different understanding.

I defend this claim through a small example and explain what it changes about understanding through unresolved models. The central proposal is that partial causal understanding should preserve relations among unanswered questions. It should not be reduced to the intersection of the models’ answers considered one question at a time. This is a claim about the content and assessment of understanding, not a new technique for causal identification or an argument that every admission of ignorance constitutes understanding.

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

The construction information is assumed accurate and sufficient to exclude further types. This is not an inference from the two behavioral observations alone. Those observations would support neither restricted family over all conceivable devices.

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

## 3. Why this is understanding of the device

One might describe the difference as useful information about experiments and deny that it concerns understanding. But consider what each investigator has grasped about the actual output.

In Selection, the two inputs have asymmetrical roles even though the investigator cannot identify their occupants. One input controls Y, and the other does not. In Combination, the inputs have symmetrical roles: they are either jointly required or individually sufficient. These claims specify alternative ways in which the on-state is sustained. They exclude materially different causal organizations of the actual device.

The same information therefore does two jobs. It limits which explanation of Y = 1 may eventually be accepted, and it supports inference about how that explanation would extend to altered conditions. Its relevance to experiment is a consequence of its relevance to the target’s organization. It is not merely a report about the investigator’s mental state.

The difference is particularly clear if we compare a third investigator who knows only the table. This investigator can correctly answer every settled single-intervention question and give the correct range for every unsettled one. Nevertheless, the table alone warrants neither transfer from the X test to the Z test. It suppresses precisely the relation that explains why the transfers differ. A conception of understanding sensitive to grasp of causal dependence has a reason to distinguish these epistemic situations even though a count of individual answers cannot.

The example does not establish that Selection contains more understanding than Combination or conversely. Their understanding has different content. Both contain more relevant structure than the table alone, relative to their respective true construction information. Assessment should consequently distinguish amount, correctness, and organization rather than insist on a single score.

Nor does either investigator possess a fully discriminating explanation of the actual output. Selection does not establish whether X or Z was the controlling input. Combination does not establish whether the output depended on both inputs jointly or was sustained redundantly. Calling their understanding partial acknowledges these missing answers. It does not erase the positive knowledge of the alternatives’ organization.

A limited answer to a broader contrast remains available. Relative to the contrast between both inputs on and both off, each family supports the output’s dependence on that joint change. Relative to the contrast between one input on and off with the other on, the answer remains unresolved. But even at this finer level, ignorance is not unstructured: the unresolved dependencies are opposed in one family and aligned in the other.

This yields a positive reason to attribute partial explanatory understanding before model selection. Grasping a genuine constraint on possible causal explanations is understanding something about how the actual outcome depends on its conditions, provided the constraint is about the target and the investigator can use it appropriately. Knowing only that there are “two possible models” would not meet that standard. Knowing what makes their explanations differ, what remains common, and how the unsettled differences constrain one another can.

## 4. The loss caused by separate answer sets

The general point is elementary but consequential. A model assigns a response to each question in a chosen family. Collect these responses into a profile. A collection of live models supplies a set of possible profiles. If instead we record the possible responses separately for each question, we can combine responses that no live model combines.

Selection and Combination make the loss visible. Their separate answer sets for A and B are both {0, 1}. Treating these sets independently permits all four pairs. Selection permits only two, Combination only the other two. Once the profile structure is removed, the missing constraint cannot be reconstructed from the separate sets.

This is not a demand to retain every detail of every model. Models can be grouped together when they have the same response profile for the questions relevant to the inquiry. Unresolved microscopic differences that alter none of those responses need not be carried forward. The point is to retain dependencies that matter to the inquiry rather than retaining models indiscriminately.

It is also not a novel mathematical result. The distinction between a joint constraint and its separate projections is basic, and causal identification can concern a vector of quantities. The philosophical lesson is that an apparently cautious summary of understanding can lose explanatory content without losing a single settled answer, enlarging a single individual answer set, or becoming inaccurate in any entry. Accuracy question by question is therefore an insufficient criterion for preservation of partial understanding.

This matters for assessing what someone has learned. Suppose instruction replaces detailed competing models with an accessible table of “known” and “unknown” intervention outcomes. The table may preserve all individually reportable results and still leave the learner unable to make inferences the original models warranted. The defect is not simply lower confidence or fewer facts. It is the loss of relations among possible causal answers. An assessment confined to the table’s questions would miss it.

A suitable practical test is to ask how learning the answer to one unresolved question would affect another. This tests whether the investigator grasps the organization of the possibilities. Such tests need not involve actual experimentation. The investigator can reason conditionally: if this input proved dispensable, what would follow about the other? Correct conditional transfer can reveal understanding that direct questions fail to detect.

## 5. Four objections

The first objection is decisive against an overstatement of the thesis. A relation among unresolved answers is itself a settled answer to a more complex question. Selection answers “Must A and B differ?” affirmatively. Consequently, a sufficiently expressive inventory of all common truths already contains the relation. There is no formal impossibility of representing partial understanding through invariant content.

I accept this. The target is a reduction to separate answers about individual interventions, not closure under every possible compound question. The positive demand is on what an adequate account counts as relevant content. A stability account can accommodate the example by treating the relation among responses as the object whose stability matters. Doing so preserves the achievement instead of treating it as a blank where an answer should be. The proposal supplements the use of stable answers; it does not refute every theory formulated in terms of stability.

The second objection says that the construction information already supplies the understanding. Comparing models adds nothing. In one sense this is right: the comparison cannot manufacture truth independently of its premises. But possessing a premise is different from grasping its causal implications. Someone may know that a device is one gate type or another without recognizing the constraints this imposes on unresolved responses. The model comparison makes those implications available and allows the person to use them. The achievement is the grasp of a consequence of construction knowledge, not the generation of evidence from model plurality.

A related concern is that the example assumes its model families are exhaustive. Real science rarely has such assurances. The inference does depend on the family’s adequacy. If an unconsidered third type is a serious possibility, Selection’s transfer rule might fail. That is a limitation, not an embarrassment to be removed by declaring the result “robust.” We should distinguish a conditional achievement—understanding the implications of an explicitly hypothesized family—from warranted understanding of the target through that family. The latter additionally requires good grounds for the relevant structural exclusions. Such grounds can be fallible. The present argument specifies what must be preserved once they are supplied; it does not supply a universal method for establishing them.

The third objection questions whether higher-order counterfactual constraints explain anything. They do not tell us which concrete mechanism operated. Perhaps they concern only possible explanations and so fall short of explanatory understanding.

This correctly identifies what is missing but draws too sharp a boundary. Knowing that exactly one input is causally controlling tells us something about the actual dependency even without identifying the input. It excludes both joint necessity and redundant sufficiency. A person who can articulate and use those exclusions has acquired a partial characterization of the actual causal organization. Insisting that this is no understanding until the controlling input is named would make the attribution discontinuous: the person would go from no understanding to understanding upon acquiring the final discriminating bit, despite already grasping most of the inferential structure. The more proportionate assessment is that learning the bit completes a previously partial answer.

There are cases where a disjunction is too weak to illuminate. “The device has some mechanism” offers almost nothing. The relevant distinction is not disjunction versus categorical assertion. It is whether the content nontrivially organizes causal possibilities and supports discriminating inferences. Our two families meet that standard in different ways.

The fourth objection is that the proposal overintellectualizes understanding. Must someone who understands an ordinary switch enumerate every live model and know the limits of every inference?

No. The claim concerns preservation and attribution of understanding across an explicitly disputed family of causal questions. It does not impose complete awareness of one’s ignorance as a prerequisite for understanding anything. A person can understand the joint switch-off dependency without knowing the device’s unresolved finer structure. What that person cannot legitimately claim is the fuller understanding possessed by someone who grasps the relations between its unresolved individual dependencies. The requirement grows with the scope of the understanding attributed, not with an impossible demand for exhaustive self-knowledge.

## 6. Partial understanding as organized possibility

An unresolved model choice need not force a choice between pretending to know the mechanism and declaring that nothing is understood. Common intervention answers can establish a limited causal dependency. Relations among disputed answers can establish more: a structured account of which explanations remain possible and what discovering one feature would reveal about another.

The two devices demonstrate why this additional content deserves explicit recognition. Their separate possible answers coincide completely, while their warranted transfers of learning diverge. What distinguishes the investigators is not certainty about more individual outcomes. It is their grasp of different constraints on the mechanism sustaining the actual outcome.

Partial understanding therefore should not be represented solely as completed answers surrounded by empty spaces. Some of its content lies in the relations across those spaces. Preserving that content allows us to acknowledge both a real explanatory achievement and exactly what it leaves unresolved.

## References

Frigg, Roman, and James Nguyen. 2025. “Stabilising Understanding.” *Philosophical Studies*. Published online 9 August 2025. https://doi.org/10.1007/s11098-025-02384-y.

Pearl, Judea. 2010. “The Foundations of Causal Inference.” Manuscript dated May 12, 2010, submitted to *Sociological Methodology*. https://web.cs.ucla.edu/~kaoru/r355-corrections.pdf.

Weisberg, Michael. 2006. “Robustness Analysis.” *Philosophy of Science* 73 (5): 730–742. https://doi.org/10.1086/518628.
