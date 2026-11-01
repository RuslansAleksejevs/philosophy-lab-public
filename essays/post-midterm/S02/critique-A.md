# S02 — Role A: argument and counterexamples

## Outcome

**Potentially defensible, on the draft's expressly limited reading.** Fair recruitment alone does not justify giving an answer-selected report the warrant of an unselected verdict or the standing of a completed independent review. The draft establishes that insufficiency claim. I find no fatal logical error and no error in its probability table.

Two major scope issues remain: what additional warrant the mayor actually claims, and which sense of independence the designation procedure must satisfy. These limit the accusation against the example and the argument's further institutional implications; they do **not** refute the qualified thesis at line 9. I would not set the essay aside on argument grounds.

### Reading and limits

I read the complete checksum-verified manuscript, **lines 1–177, including the bibliography at 165–177**, and every one of the 21 exact assigned inputs. Manuscript SHA256: `5cf43ea11a62bc351779a443d785b068681be6efb39d1205d24daff9b0ccf41a`. All manuscript locations below refer to those original lines.

Primary-source assessment used the supplied passages, not fresh internet retrieval or whole-work reading. Exact raw copies, surfaced source-line intervals, inherited retrieval failures, and reading boundaries are preserved under `sources/` and indexed in `SOURCES_A.json`. Exact duplicate decoded lines were displayed once, with their original occurrences mapped. No other review, other essay, global lab context, or earlier role packet was consulted. Embedded author notes and biographical/search snippets were not used to assess the argument. This is not an exhaustive novelty assessment.

## 1. Charitable reconstruction

The thesis is not that a first panel has a veto, that later approval is worthless, or that every asymmetric procedure is illegitimate. It is a claim about an **unsupported transfer of warrant** (9–11, 27, 125–129).

The argument has two branches:

1. **Evidential branch.** An authentic endorsement by these participants is distinct from evidence about other comparable panels and from an institutionally privileged answer (17–23). In the stipulated independent, constant-`p` model, selecting the first approval changes the distribution of the designated verdict: `p` becomes `1 − (1 − p)^n` (35–48). Thus panel-level recruitment fairness does not guarantee an unselected-report sampling distribution.
2. **Standing branch.** Where conflicting reports share the very properties offered to justify one report's special standing, those properties do not discriminate between them (68–70). An account of the designated report's authority must therefore include the designation procedure, not just the recruitment procedure (74–79).
3. **Normative bridge.** If an outside review is supposed to supply a check on the sponsor, the sponsor's satisfaction with its answer cannot, without another reason, establish that this answer alone fulfills that task (81–89). Better arguments, a material repair, or a justified mandate can provide a different reason (70, 87, 107–115, 125–129).
4. **Conclusion.** Institutions owe an account of what the selected report shows and why it completes their task. Neither account automatically substitutes for the other (133–151).

The mathematical branch is a counterexample to a sufficiency inference, not a proof of illegitimacy. The normative bridge does the work needed for the institutional conclusion. The draft generally keeps those jobs separate.

## 2. Strengths that should survive criticism

- **The three-way distinction is useful.** Authentic authorship, evidential generalization, and institutional standing need not coincide (17–23). In particular, an advisory report can matter institutionally without binding policy (21, 85, 141).
- **The stopping calculations are correct and unusually well qualified.** The values `37/64`, `63/64`, `63/37`, and `1/3` are correct under the stated assumptions (44, 52–60). I independently checked them and the identity-symmetric illustration at line 48; see `sources/argument-checks.py` and `.json`.
- **The complete-history concession is substantial, not cosmetic.** The same observed rejection–rejection–approval record has likelihood `(1 − p)^2 p` under either of the two specified protocols (60–62). This blocks an easy but false claim that stopping always destroys usable evidence.
- **The essay permits genuine alternatives.** It allows better later reasoning, justified reopening, transparent endorsement searches, and separately justified asymmetric gates (70, 87, 107–129). Criticism must not quietly withdraw those concessions and then attack a stronger thesis.
- **Its source-facing claims are restrained.** Membership fairness is not misrepresented as a complete theory of authority (29); temporal fairness is acknowledged (31); the general anti-capture insight is credited to Bagg (91–93). The inspected primary passages support these limited characterizations.
- **It does not pretend to have found an actual scandal or a new theorem.** Those limitations are explicit (46, 155, 163). An illustrative counterexample does not need a verified mayor to be logically effective.

## 3. Concerns by severity

### Fatal: none identified for the stated limited thesis

Neither a legitimate asymmetric gate nor successful inference from a complete record defeats line 9: both are explicitly allowed. Nor does the elementary character of the mathematics make it false. The core conclusion is weaker than a general indictment of repeated consultation.

### Major M1 — Ending a procedure is not necessarily giving one report comparative authority

**Locations:** 5–11; 64; 68–85; 97–101; 125–129; 143–151.

The opening tells us that two reports reject, the third approves, all remain public, and consultation ends (5). Line 68 then describes the approving report as overriding or superseding the others. That is a consequential additional specification. A report can be the **event that completes an aggregate test** without being treated as more authoritative than contrary reports.

For example, an independently assigned task could require checking whether at least one of three panels endorses a proposal. A full three-panel collection aggregated by “any approval” and a first-approval procedure have the same binary outcome for every possible verdict sequence. Early closure can merely avoid obtaining reports that cannot change that specified outcome. The approving report witnesses satisfaction of a threshold; it need not erase the earlier reports, estimate typical judgment, or defeat their reasons.

Likewise, “passed an independent citizen check” can mean either that an autonomous panel really endorsed the proposal, or that an appropriately constituted review supplied an additional institutional warrant. The first statement may be true in the opening; the second needs the missing account. The essay itself recognizes the existential claim's permissibility at 99 and 119–121.

**Best reply already available:** the target is expressly an *approval-selected report with additional authority* (9), and a separately justified gate is admitted at 125–129. If comparative priority and an incompatible review obligation are stipulated, rather than inferred from the fact of closure, the objection works.

**Remaining issue:** the opening should not be taken to establish that those stronger conditions obtain merely from the sequence and its endpoint. An observed RRA sequence could also occur under fixed-last, and no original consultation mandate is specified. This is a major application gap, not a refutation of the insufficiency result. Resolving it requires identifying the claimed warrant and the counterfactual continuation policy, not supplying a universal theory of legitimate commissioning.

### Major M2 — Outcome dependence and dependence on the sponsor are different relations

**Locations:** 74–83, especially 77–81; 109–111; 125–129; 157–159.

Three relations need separation:

- statistical selection of an outcome;
- causal or institutional control by the sponsor;
- justification for the output's assigned role.

A rule can depend on approval without depending counterfactually on the sponsor's preference. Suppose an external body fixes a proposal-acceptance threshold before this mayor takes office. The rule would remain unchanged if the mayor changed sides. It selects for an answer, but the sponsor does not thereby control its operation. It may also preserve a genuine outside check while assigning different consequences to the two verdicts.

The probability calculation establishes outcome selection. The original discretionary-shopping scenario can establish sponsor control as well. But outcome selection alone cannot establish that second relationship. The phrase “dependent on agreement” at 79 risks joining them too quickly. A design can be nonrepresentative of typical panel opinion yet institutionally insulated from the sponsor.

**Best reply already available:** line 81 limits the independence claim by function, and 125–129 explicitly permit a justified asymmetric mandate. Those passages prevent a blanket invalid inference.

**Remaining issue:** it remains unclear whether a justified externally imposed gate qualifies as independent allocation of standing, or only as legitimate despite lacking it. That choice affects what the concluding distinction explains. I do not require neutrality between approval and rejection; I require specifying which dependence defeats the particular independence being claimed. On a narrowly sponsor-discretionary interpretation, this is largely resolved; on an outcome-invariance interpretation, the argument overreaches.

### Minor m1 — Identifying a defect is not necessary for every justified reopening

**Locations:** 105–115, especially 109 and 113; 145–149.

A second panel can be commissioned to test the stability of a surprising or closely divided first verdict without an identified information gap or demonstrable error. Under a defensible, bounded replication policy, uncertainty itself can supply a reason. New deliberation can also generate arguments from unchanged materials.

The demand for a report-specific defect is persuasive against the mayor's particular excuse that every rejection betrays misunderstanding (113). Read as a necessary condition for *all* reopening, it would be too strong. The alternatives already admitted at 70, 119–129 and 149 make the narrower reading preferable. This is a local scope ambiguity, not a conflict requiring abandonment of the thesis.

### Uncertain concerns and unresolved boundaries

- **External importance:** the real frequency, effects, and feasibility of unchanged-question report shopping are unknown here (155). That limits practical importance, not the counterexample's validity. I have not independently established any such case.
- **Empirical generalization:** neither panel variation nor a relationship between approval propensity and policy quality is estimated (35–46). The model supports a possibility result, not a diagnosis of actual assemblies.
- **Distinctive contribution:** Bagg's institutional cautions and the OECD's whole-process principles already contain much of the general lesson acknowledged at 91–93 and 139. The report-designation application may still be illuminating. The assigned passages and their finite searches cannot establish its priority or lack of priority. Failed finds are not evidence of exhaustive absence.

## 4. Strongest countermodels and what they actually defeat

### A live justification for an asymmetric check

The draft's legitimate-gate exception need not remain an empty possibility. Consider a hypothetical externally assigned decision task with equal prior probabilities of good and bad policy. Stipulate independent panels approving with probabilities `3/4` and `1/4` respectively. If a false rejection has loss 10 and a false approval loss 1, the any-approval-in-three rule has expected loss `47/128`. Single-panel choice has expected loss `11/8`; majority-of-three has `55/64`. Indeed, with those stipulated losses, any approval is the posterior-loss-minimizing decision for every complete three-panel record. First-approval stopping implements it without changing the binary decision.

These are exact toy calculations, not evidence that real panels track policy quality or that expected loss exhausts democratic justification. They show a substantive, contestable rationale for asymmetric error allocation that is not simply “the sponsor likes approval.” Such a gate can be a fallible independent test, not merely a publicity search.

**Effect on the essay:** defeats any reading on which asymmetric stopping necessarily nullifies checking authority. **Does not defeat line 9**, because the rationale supplies precisely an additional premise beyond fair recruitment. Sections 4 and 6 already allow this response. Its force is to narrow the accusation and show why the role must be specified.

### Complete disclosure with a known stopping rule

For the public RRA history, the higher/lower propensity likelihood ratio is `1/3` under either specified protocol. Conditional on the two already observed rejections, a third approval contributes a likelihood factor of 3 under either protocol. The coarsened observation “some approval within three” instead gives `63/37`.

**Effect on the essay:** defeats a universal evidential penalty attached to every approval-selected report irrespective of the observer's information. The draft correctly does not defend that universal claim (58–62, 99, 135). Its table shows the importance of the observation being evaluated; it cannot itself establish a normative loss of standing.

### Entirely correlated panels

If all potential verdicts coincide, first approval and fixed last have the same outcome distribution.

**Effect on the essay:** defeats a claim of inevitable numerical inflation, not the claim that recruitment fairness alone fails to guarantee the designated verdict's distribution. The author already acknowledges this case (46). No independence assumption has been covertly used as an empirical finding.

## 5. Primary-source checks relevant to the argument

- **Flanigan et al., “Algorithmic framework,” returned lines 91–98 and 110:** the optimization concerns distributions of membership chances, with representation constraints. This supports the draft's comparator at 29; it does not furnish its normative bridge.
- **Kalaycı and Micha, §2, returned lines 104–141:** the model takes panel number and sizes as inputs and defines individual, panel, global, and prefix criteria. The contrast at 31 is appropriately about a different object of assessment, not a purported refutation of their results. Algorithmic proofs were not independently verified.
- **Bagg, “Two Models” and “The Structure of Citizen Oversight,” returned lines 117–124, 177–198, 207–212:** representation is not interchangeable with anti-capture, and oversight can have different mandates and effects. This supports 91–93 while cautioning against turning an independent check into a mandatory veto. It does not establish the legitimacy of every stopping policy.
- **Lafont, printed pp. 90–97, particularly returned lines 729–755:** public evidential uses are distinct from decisive authority, with outside influence constrained. The draft accurately labels the stopping qualification as its own inference (123), not her endorsement of repeated commissions.
- **OECD, ch. 5, returned lines 4795–4848:** the described accountability, transparency, participant wording control, and arm's-length process safeguards are present. These standards support considering the whole process, but do not decide the hypothetical gate's justification.
- **Ireland's official FAQ, returned lines 29–50:** the distinction between advisory recommendations and an advance undertaking to respond is supported. The draft appropriately makes no claim about actual compliance or report shopping (141).

These are passage-level checks from assigned captures. Neither source titles nor metadata-only returns were treated as full-text access.

## 6. What would change this assessment?

The core would need a genuine counterexample in which recruitment fairness **without an additional role-conferring reason** establishes the disputed comparative standing. The permitted gates above are not such counterexamples.

The application would fail or narrow sharply if the mayor claimed only a genuine existential endorsement, fulfilled a separately justified aggregate test, or conferred no priority beyond recording a threshold event. Conversely, an explicitly promised outside review, a sponsor-controlled rule that withholds completion from rejection, and no compatible justification would make the draft's objection much stronger. Those are relevant discriminating facts, not demands for my preferred aggregation rule.

**Dissent preserved:** a reasonable defender can say that lines 9, 99 and 125–129 already impose all the necessary limits, so my major concerns affect explanatory payoff more than correctness. I substantially agree about correctness. A reasonable skeptic can instead regard the residue as a general injunction to justify institutions, illustrated by elementary selection effects. The draft has not fully defeated that significance objection, although a useful analytical illustration need not be a new general theory.

**Final judgment:** retain the distinction and the limited insufficiency conclusion. Do not read the essay as proving a general prohibition, an unavoidable evidential contamination, or the illegitimacy of the incompletely specified mayoral procedure.
