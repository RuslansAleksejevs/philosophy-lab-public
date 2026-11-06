# When Every Finite Classification Chart Contains a Circle

Imagine a dependency structure in which every route toward grounds terminates after finitely many steps. No fact lies on a dependency cycle or an endless descent. We try to represent that world with a finite number of categories, drawing an arrow whenever something in one category helps explain something in another. The resulting map contains a circle. We split the categories more carefully. Another circle appears. We keep refining the classification, but no finite refinement eliminates every circle.

There need be nothing wrong with the world's explanatory structure. The failure can arise because its dependency routes, although individually finite, have no common finite bound on their length. Such a structure has foundations but cannot have a complete finite chart of strict dependency. Here completeness means retaining every selected binary dependency edge, not representing every feature of an explanation.

I will establish the exact condition under which finite refinement succeeds. The mathematics is elementary and closely connected to Mirsky's theorem on partially ordered sets. The philosophical point concerns what persistent circles in a map entitle us to conclude. The existence of some chart circle after every finite subdivision does not entail either circular grounding or an infinite descending dependency route. The circle need not involve the same facts after each subdivision; any particular finite collection of acyclic dependency witnesses can still be disentangled finitely. It can reveal a limitation of finite classification instead. This identifies a commitment stronger than foundationalism in the demand that a sufficiently detailed finite taxonomy must display the world's entire strict dependence order.

## 1. What the map claims

Metaphysical grounding concerns what obtains in virtue of what. A conjunction may hold in virtue of its conjuncts; the existence of a singleton may depend on the existence of its member. Whether every such case belongs to one relation is controversial. My argument needs a selected relation of explanatory dependence, with its interpretation kept fixed throughout.

Write **x → y** when the fact x grounds, or helps ground, the fact y. The direction runs from ground to grounded. The nodes are particular facts, not the kinds to which they belong. I initially suppose this graph is acyclic: there is no finite sequence of arrows returning to its starting node. The argument does not require that every arrow be an immediate dependency, or that the relation be transitive.

If several facts jointly ground another, draw an arrow from each contributing fact to the result. This records partial dependencies. It does not encode which contributors form a sufficient plurality. The conclusions therefore concern the possibility of preserving all these dependency edges; they do not claim that a graph alone represents complete explanations.

A classification assigns every fact in the selected domain to exactly one cell. For example, we might group facts by their subject matter. Its map has an arrow from cell A to cell B whenever some fact in A helps ground some fact in B. That is an existential claim. It does not mean that every A-fact grounds every B-fact, or even that every B-fact has an A-ground.

Three requirements define the maps at issue:

1. There are finitely many exclusive cells covering the domain.
2. Every selected dependency edge appears in the map.
3. The cell graph itself must serve as a presentation of strict priority: its dependency arrows must form an acyclic relation, including when the underlying facts occupy the same cell.

Edge retention means retaining self-loops. If a fact in A helps ground another fact in A, the map contains A → A. This does not mean that a natural kind literally grounds itself: the two witnesses can be different facts. The third requirement asks the map to perform an additional task, presenting strict priority through its cells alone. That task fails in the presence of such a loop. Erasing the loop would conceal a dependency, not demonstrate its absence. A map without cycles, including self-loops, will be called an **acyclic chart**.

These requirements are intentionally demanding. A diagram may serve many purposes without satisfying them. A chart of broad scientific domains, for instance, might leave internal dependencies unspecified. The question here is when a finite classification can preserve *every* selected edge while presenting their order as acyclic.

## 2. The exact limit of finite refinement

A finite path of length n contains n successive arrows. An infinite directed path is an endless sequence of distinct nodes linked in the same direction. Say that a graph has **uniformly bounded depth** when some finite number h bounds the length of every finite path anywhere in the graph. This is stronger than the absence of infinite paths, and stronger than each fact having its own finite maximum depth of ancestry. The countermodel below satisfies both of those weaker conditions while lacking a common bound.

Here is the relevant equivalence:

> An acyclic dependency graph admits a complete finite acyclic chart if and only if its paths have a uniform finite length bound. Moreover, when this bound exists, every finite classification has a finite refinement whose chart is acyclic.

First suppose a complete acyclic chart has m cells. Follow any path through the underlying facts. Each arrow projects to an arrow between cells. If the path visited more than m cells, counting repeated visits, some cell would repeat. The segment between two visits would be a nonempty closed directed walk. Such a walk contains a cycle, contrary to the chart's acyclicity. Thus every path has at most m−1 arrows.

This direction explains why choosing more imaginative labels cannot solve every problem. Any successful chart, whatever its categories mean, imposes a numerical ceiling on the depth of the represented structure.

For the converse, suppose no path has more than h arrows. Assign to each fact x the length r(x) of a longest path ending at x. This maximum exists because the possible lengths belong to the finite set 0, 1, …, h; a path containing x alone has length zero. If x → y, appending that arrow to a longest path ending at x yields a path ending at y. Acyclicity ensures that this extension does not revisit y. Consequently,

**r(y) ≥ r(x) + 1.**

Group facts of equal r-value together. Every chart arrow increases r, so none can return to its starting cell. At most h+1 cells are needed.

Now start with an existing classification containing k cells. Split each cell according to r. A fact's new cell records both its old category and its rank. At most k(h+1) cells result. Every projected arrow still increases rank, so this is an acyclic refinement that retains every original distinction.

For a small successful example, consider a → b → c, with a and c initially grouped together. Its two-cell chart is cyclic. Incoming ranks 0, 1, and 2 separate the facts into three cells, and the resulting chart is acyclic. The construction repairs that grouping because all paths have at most two arrows.

No new mathematical theorem is being claimed. Mirsky (1971, Theorem 2) established the connection between finite height and covering a partially ordered set by finitely many antichains. Applying rank to the reachability order gives the ordered partition needed here. An arbitrary antichain partition would not suffice: two independent dependencies a → b and c → d can yield a chart cycle if we group a with d and b with c. The rank construction supplies an order between cells as well as separating comparable nodes. [Mirsky's primary article](https://daiwz.net/course/disc_math/2023/Mirsky.pdf).

The equivalence concerns arbitrary classification cells. If only certain natural kinds are admissible, the necessity proof remains valid, but sufficiency does not follow. A rank subdivision might fail the required standard of naturalness. Uniformly bounded depth removes the purely structural obstruction; it need not supply a metaphysically privileged taxonomy.

## 3. Foundations without a finite acyclic chart

Consider separate finite sequences, one of every positive length:

**a₁,₀ → a₁,₁**

**a₂,₀ → a₂,₁ → a₂,₂**

**a₃,₀ → a₃,₁ → a₃,₂ → a₃,₃**

and so on. There are no arrows between different sequences.

Every fact has finite ancestry. Every sequence begins at a fact with no incoming arrow. There are no cycles, and no infinite paths in either direction: a path stays within one finite component. We can add all the arrows required by transitivity within each component without changing any of these properties. If a full-ground interpretation is wanted, stipulate additionally that each predecessor individually fully grounds its successor and that the first fact in each component is ungrounded. That interpretation supplies finite sufficient grounding sequences for this example. It is an extra assumption, not something binary partial-dependency edges generally guarantee.

Nevertheless, the lengths have no common finite bound. For any proposed m-cell chart, take a sequence with at least m arrows. Some cell repeats along it, producing a chart cycle. This applies to every finite classification, not merely to an initially crude one. Since every finite refinement is itself a finite classification, no finite refinement can repair the problem completely.

The example is compatible with the structural demand that all dependency routes terminate finitely. It does not exploit an endless descending chain with a foundation somehow placed below it. Rabin and Rabern distinguish several conditions often gathered under the name of well-founded grounding: finite grounding, lower bounds, and a foundation. The present example avoids reliance on their weaker alternatives. Its obstruction concerns a further issue: whether the finite lengths are *uniformly* bounded. [Rabin and Rabern, §4](https://www.pure.ed.ac.uk/ws/portalfiles/portal/21548574/RabinRabern_Well_Founding_Grounding_Grounding_preprint_JPL_2015.pdf).

Can the graph receive a metaphysical interpretation? Here is a conditional one. Take distinct base objects b₁, b₂, and so forth. For each n, consider the existence facts for bₙ and for n successive singleton constructions over bₙ. Assume that the existence of each selected singleton is grounded in the existence of its member, and that the selected base existence facts are ungrounded. Within this selected family, assume there are no additional cross-component grounding relations. We then obtain the displayed paths, or their transitive closures.

These are substantive assumptions about grounding, not consequences of set theory. The example also does not claim that a full ontology contains only these selected singletons. It describes a restricted dependency structure. That qualification does not weaken the obstruction: a complete finite acyclic chart of a larger structure would restrict to such a chart of this family, which is impossible. What the restriction cannot establish is that the larger world's *other* dependencies terminate. The abstract disjoint-path model supplies the counterexample to the structural implication; the conditional interpretation shows how familiar grounding commitments can generate the obstructing pattern.

Nor should the result be restated as saying that some fact lacks a finite sufficient explanation. The chart retains all selected dependency routes. Under transitive grounding, a distant foundation might itself fully ground a fact, providing a short direct route alongside a long route through intermediate facts. Our conclusion remains unchanged because the long route is still present. Selecting one sufficient explanation per fact would be a different representational task.

## 4. What this adds to familiar warnings about levels

It is already known that grouping relata can mislead us about dependence. Correia (2021, §5.1) describes alternating mental and physical subkinds that generate reciprocal grounding between the broad kinds. His own foundation relation excludes reverse partial grounding. It is therefore different from the existential relation between classification cells used here. His account also permits natural kinds that overlap, whereas my cells form a partition. The present argument neither introduces his type-level problem nor refutes his solution. Its additional step is to ask whether *any finite subdivision* can remove all chart cycles, and to show that failure is compatible with the absence of all infinite paths. [Correia's primary article](https://d-nb.info/1241231591/34).

Ranks and levels derived from ground are equally familiar. Bevan (2025, §2.1) defines ordinal ranks for well-founded partial ground and distinguishes an ordering of individuals from relations imposed on pluralities of them. A scientific domain may span several ranks. This already blocks the assumption that each broad domain occupies one level. My result identifies a further limit: even arbitrarily many but finitely many subdivisions can be insufficient. It is consistent with Bevan's rank hierarchy, which need not have finitely many levels. [Bevan, “Metaphysical foundationalism”](https://doi.org/10.1007/s11098-025-02444-3).

The broader abstraction literature supplies another warning. Geiger and colleagues (2025, p. 7 and §2.7) explicitly allow acyclic causal models to have cyclic abstractions. The appearance of cycles under abstraction is not itself my contribution. Nor do I assume that causal intervention semantics carries over to grounding. The point here is the exact condition for the existence of *any* complete finite acyclic classification, and the consequence for reasoning from unsuccessful refinement. [Geiger et al.](https://www.jmlr.org/papers/volume26/23-0058/23-0058.pdf).

These comparisons locate the modest claim. A locally misleading grouping and a globally unavoidable compression failure are different problems. The first can be repaired with enough finite distinctions. The second cannot. An account of metaphysical structure may satisfy stringent termination conditions while suffering from the second problem in every finite chart.

## 5. The inference we should refuse

Suppose an apparent grounding circle is challenged on the ground that the same category contains different facts. A natural reply is: “Then distinguish them more carefully.” That local request remains entirely sound. In an acyclic graph, take any finite collection of alleged reciprocal-dependence witnesses. Keep their endpoints and the witnessed edges. Give each endpoint its own cell. This finite evidential subgraph is acyclic. Nothing in the countermodel shows that a particular finite set of witnesses resists finite analysis.

Three claims must therefore be kept separate. One chart may contain a cycle. Several attempted refinements may all contain cycles. Or *every possible finite classification of the entire domain* may contain a cycle. The first two do not establish the third. The theorem characterizes the third, given acyclicity, as the failure of uniformly bounded depth. Moreover, the remaining circle can shift to different witnesses after each refinement.

Here is a schematic argumentative situation where the global demand is explicit. A theorist offers the disjoint finite sequences as a model of foundational dependence. A reviewer accepts each displayed sequence but worries that inspecting examples conceals a global defect. The reviewer asks for one finite classification chart that covers every fact, includes every dependency, and exhibits acyclicity using its cells alone. Such a chart would indeed be a sufficient certificate that no token cycle occurs: any token cycle would project to a closed walk. The request therefore has a reasonable purpose—an inspectable global guarantee rather than a collection of checked cases.

The error arises if the reviewer concludes that foundationalism has failed when this particular certificate cannot be supplied. In the model it cannot be supplied, but a finite rigorous proof of acyclicity is available: every edge stays inside one finite component and strictly increases its index. The reviewer's request selects an unnecessarily restrictive *form* of global certificate. The correct assessment changes from “this structure lacks a defensible foundation” to “this structure needs a different representation of its order.” This is an invented exchange, not a position attributed to a published philosopher.

The invalid guarantee is consequently precise:

> If dependency routes terminate finitely and the relation is noncircular, one finite classification of the whole domain can retain every edge while its cell graph presents strict priority.

The countermodel refutes that guarantee. The equivalence reveals its missing assumption: a uniform finite upper bound on dependency depth. It does not undermine local witness analysis, and it does not show that foundationalism lacks finite proofs. Its lesson is limited to replacing local success with a requirement of one complete finite strict quotient.

A useful alternative retains broad finite categories, reports internal dependencies without interpreting them as strict self-priority of a category, and supplements the chart with a rule governing the internal order. In the example, the component and position indices provide such a rule. The chart's finite skeleton does less work, while the combined description still gives rigorous evidence of acyclicity. Abandoning the specified chart format is not abandoning rigor.

Busse's (2025) discussion of metaphysical coherentism stresses the need for detailed accounts of alleged dependence. The present result supports that scrutiny while limiting one possible way of demanding detail: there may be no finite classification that renders the entire structure acyclic. Busse need not promise such a classification; the result concerns a possible strengthening of the demand, not an error attributed to him. [Busse, §§1 and 3](https://doi.org/10.1007/s11098-023-02055-w).

The conclusion is about entailment. A countermodel does not show that chart cycles never provide probabilistic evidence for token cycles under additional assumptions. A model class might independently exclude unbounded depth or give it little probability. Those assumptions would do essential work. The chart alone does not settle the issue.

## 6. Are the requirements too strong to matter?

An obvious objection is that useful maps leave things out. A geological map does not fail because it omits individual grains. Similarly, a hierarchy of physical, biological, and psychological categories need not preserve every grounding relation within them. Why criticize a requirement that such a map never intended to meet?

The objection is right about useful maps. My argument gives no reason to reject them. Its target is the inference from their global shape to the global shape of strict grounding. A chart can summarize inter-category dependencies while remaining silent about within-category structure. But its acyclicity then cannot establish that all the underlying dependencies form an acyclic order. Erasing self-loops is entirely legitimate if the omission is acknowledged; interpreting the erased map as a complete test for circles is not.

One might instead allow dependencies within a level without drawing them as cycles. This abandons strictness at the level of cells. It offers a coherent representation, but makes the distinction between a level and a stage of strict explanatory priority indispensable. Facts assigned the same level can stand at different positions in a grounding route. The finite-chart theorem clarifies the cost of the choice without prohibiting it.

Another objection is that a finite description can specify the whole countermodel. The phrase “one finite chain of each positive length” already does so. This is also correct. The result concerns finitely many classification cells, not finitely many words. A recursive diagram with an integer parameter can describe infinitely many cells. Parameter values distinguish positions that a literal finite quotient must identify. Recursion therefore provides an effective response precisely by abandoning the finite-cell requirement.

A third objection asks whether natural kinds rescue finite charts. They cannot rescue the unbounded case while retaining all three requirements: the impossibility proof applies to every finite partition, however natural its cells. Naturalness can only impose additional restrictions on the successful bounded case. Conversely, if natural kinds overlap, their relationship needs its own model; we cannot simply assume that a theorem about partitions establishes sufficiency for them.

Finally, the result might look too close to an elementary fact about orders to carry philosophical weight. The mathematics is indeed easy. What needs correction is an inference connecting termination of every dependency route to representation of the whole relation in one finite strict chart. In the countermodel, each fact has finite maximum ancestry, yet no common finite taxonomy records all dependencies as strict progress between cells. Finite path length alone also says nothing about explanatory breadth: a depth-one graph could have infinitely many contributing grounds for one fact. Our chain model can be assigned the stronger sufficient-ground interpretation stated earlier, but the theorem does not settle explanatory adequacy. Its contribution is the exact limit of a particular global certificate, compatible with finite success in every local witness analysis.

We can retain a demand for explanatory detail while distinguishing it from the stronger requirement of a complete finite strict chart. Finite analysis can resolve every particular alleged circle, and a finite recursive argument can establish the whole structure’s acyclicity, even though every finite classification chart contains some circle. What those unavoidable chart circles do not entail is a token cycle or an endless descending dependency route.

## Bibliography

Bevan, Michael. 2025. “Metaphysical foundationalism.” *Philosophical Studies*. https://doi.org/10.1007/s11098-025-02444-3.

Busse, Ralf. 2025 [online 2023]. “No foundations for metaphysical coherentism.” *Philosophical Studies* 182: 2503–2534. https://doi.org/10.1007/s11098-023-02055-w.

Correia, Fabrice. 2021. “A kind route from grounding to fundamentality.” *Synthese* 199: 8299–8315. https://doi.org/10.1007/s11229-021-03163-y.

Geiger, Atticus, Duligur Ibeling, Amir Zur, Maheep Chaudhary, Sonakshi Chauhan, Jing Huang, Aryaman Arora, Zhengxuan Wu, Noah Goodman, Christopher Potts, and Thomas Icard. 2025. “Causal Abstraction: A Theoretical Foundation for Mechanistic Interpretability.” *Journal of Machine Learning Research* 26: 1–64. https://www.jmlr.org/papers/volume26/23-0058/23-0058.pdf.

Mirsky, Leon. 1971. “A Dual of Dilworth's Decomposition Theorem.” *The American Mathematical Monthly* 78(8): 876–877. https://www.jstor.org/stable/2316481. Accessible article scan: https://daiwz.net/course/disc_math/2023/Mirsky.pdf.

Rabin, Gabriel, and Brian Rabern. 2016. “Well Founding Grounding Grounding.” *Journal of Philosophical Logic* 45: 349–379. Author preprint: https://www.pure.ed.ac.uk/ws/portalfiles/portal/21548574/RabinRabern_Well_Founding_Grounding_Grounding_preprint_JPL_2015.pdf.
