# Progress Across a Change in Measurement Standard

**Status.** This is a conceptual expansion of idea-026, not a finished essay. No primary literature was retrieved or read, no novelty check was performed, and the formal and worked examples below are proposals for tests rather than reported findings.

## Question and narrowed claim

When can a change in a measuring standard count as progress if the new standard changes the interpretation of earlier readings? The claim defended here is local and conditional: a replacement standard can count as an improvement for a fixed, independently justified task profile when it preserves every warranted distinction the earlier standard already gets right and resolves at least one specified error, without trading that gain for a new failure in the same registered profile.

The claim does not establish that science as a whole has advanced, that the new vocabulary is closer to truth, or that two standards can be ranked for every use. If no common task commitments can be defended across a transition, this comparison gives no verdict. That restriction is a feature of the argument: it avoids converting every change of purpose into a hidden numerical score.

## The comparison rule

Let a task profile T be fixed before the candidate standards are compared. It records (1) the use or decision at issue, (2) the cases and observations to be tested, (3) the distinctions and outcomes independently warranted for those uses, (4) the reasons for treating those distinctions as warranted, and (5) which results remain unknown. A task profile may contain several uses with different priorities. It contains no weights that combine them into one total score.

For a standard S and a fully assessed profile T, let G_T(S) be the set of registered obligations S meets. An obligation may require a warranted distinction to be retained, a known failure case to be corrected, or a held-out case to be classified as specified by the task. “Retain” means preserve the decision-relevant distinction, not preserve old numbers or labels. Two scales may use different units or concepts while still supporting the same warranted decision. Conversely, unchanged numbers do not count as preservation if their task-relevant interpretation has changed.

Define S ≺_T S′ exactly when G_T(S) is a strict subset of G_T(S′), with both standards assessed on the same complete obligation set and with the same evidence rules. The relation is intentionally partial. If one standard meets some obligations that the other misses and vice versa, neither is better under this rule. If a required outcome is unknown, the comparison is provisional and no strict improvement is declared until that gap is resolved. Obligations cannot be added, removed, reworded, or reweighted after seeing which standard they favor without declaring a new profile and giving up the earlier comparison.

The independent justification of T is the hard part. It must come from the uses, stakes, and publicly discussable evidence of the task, not from a desire to make one candidate win. The justification can be contested. The method requires the disagreement to be exposed and tested, not hidden inside a score.

## Argument

**P1.** A claim that one standard is better than another needs a stated basis of comparison. Without one, “progress” is only a report that the standard changed.

**P2.** A single score can conceal task-relevant differences. Equal totals can describe cases that call for different decisions; a total can also impose trade-offs among dimensions for which no common exchange rate has been justified.

**P3.** A task may justify several obligations separately without justifying a weight that ranks every case on one scale. For instance, one use may require low missed detections while another requires low false alarms. Meeting both obligations is assessable without declaring how many false alarms equal one missed detection across all uses.

**P4.** For a fixed profile, recording the obligations met by each standard preserves successful results and identifies corrections as separate facts. Strict set inclusion expresses “at least the earlier successes, plus one or more newly met obligations” without adding their values.

**P5.** Strict inclusion is transitive and asymmetric. If G_T(S0) ⊂ G_T(S1) and G_T(S1) ⊂ G_T(S2), then G_T(S0) ⊂ G_T(S2); no chain under one unchanged T can return from a standard to a strictly dominated starting standard.

**C.** Thus, for a fixed and independently defended task profile, a change in measurement representation can support a local progress claim without a shared scalar measure of overall accuracy. The comparison rests on a stable set of warranted obligations, not on a stable measurement scale or a total ranking.

P5 is a mathematical consequence of the proposed rule, not evidence that a real standard meets the rule’s conditions. P3 and the justification of T carry the substantive philosophical burden. The framework cannot decide by itself which outcomes matter, whether the relevant task remained stable, or whether the evidence is adequate.

## Worked hypothetical case

Suppose a fictional evaluation system compresses two error dimensions into one number: missed detections m and false alarms f, with reported score q = m + f. Consider two hypothetical systems: A has (m, f) = (0.2, 1.8), and B has (1.2, 0.8). Both receive q = 2.0, even though A has fewer misses and B has fewer false alarms. A third system C has (0.1, 0.1), while D has (2.0, 2.0).

Before comparing standards, suppose a review group justifies three obligations from two distinct uses. O1 is to choose the lower-miss system for a use where missing a target is the decisive cost; O2 is to choose the lower-false-alarm system for a use where unnecessary alerts are the decisive cost; O3 is to preserve the known ordering of C ahead of D, which is better on both dimensions. The justifications for O1–O3, the cases, and the thresholds must be documented before either standard is tested. These assumptions are part of the toy example, not empirical claims about actual detectors or users.

The scalar-only standard cannot distinguish A from B at q = 2.0, so it fails O1 and O2, but it can distinguish C from D and meets O3. A replacement that reports the pair (m, f) and applies the already registered use-specific rules can meet all three obligations. On this stipulated benchmark, G_T(scalar) = {O3} and G_T(vector) = {O1, O2, O3}. The vector standard is locally better by strict inclusion. A and B remain incomparable across the two uses: the framework does not invent one winner by assigning weights to missed detections and false alarms.

This example only shows that the rule is coherent and illustrates what evidence a real application would need. It does not show that component reporting is practically reliable, that the proposed obligations are morally or scientifically correct, or that a real historical standard change followed this pattern. A new standard that loses O3, produces new errors, or fails on preselected held-out cases would not satisfy the strict-inclusion condition.

## Strongest objection and response

**Objection: the fixed task profile is a master standard in disguise.** To say that O1–O3 matter is already to hold some goal fixed. If those goals determine the verdict, the account has not explained progress through conceptual change; it has just renamed improvement relative to a stable external target. Worse, the assessor or historian could select a task after seeing which standard it favors.

**Response.** The objection succeeds against any claim that this method proves global or value-neutral progress. The proposal should therefore be narrowed, not defended as an escape from all stable standards. A local comparison needs some shared, reasoned basis; otherwise there is no fact of the matter under this rule about which change is better. What it need not have is one master *ranking* that supplies a total order or numerical exchange rate across all tasks. Multiple task profiles may conflict, and the standards may remain incomparable. The task record, independent rationale, candidate-blind specification, and sensitivity checks are safeguards against opportunistic task selection, though they cannot make a contested purpose uncontested.

The account is compatible with the view that all improvement is relative to stable goals if that view permits plural, non-scalar goals. It does not refute that broad alternative. Its possible contribution is a precise test for one narrower case: how to recognize correction across a changed measurement language while refusing to aggregate unresolved trade-offs. Whether this is new relative to existing work remains unknown.

**Objection: cycles may arise when standards or tasks change.** A sequence of locally defensible comparisons could prefer S1 to S0, S2 to S1, then S0 to S2, making “progress” incoherent.

**Response.** Such a cycle cannot arise from strict set inclusion under one fixed T, by P5. It can arise if the task profile changes at each step, if new obligations are selected retrospectively, or if the evidence rules change. Those are not counterexamples to the fixed-profile result; they show why a chain across changing profiles needs an explicit bridge. Without one, report conditional local judgments rather than a single cycle-free history. A bridge would have to identify overlapping obligations and show why adding, dropping, or translating the others is justified independently of the desired ranking. If that cannot be done, the broader comparison should be suspended.

## What would narrow or defeat the claim

The formal coherence result is conditional on one unchanged, complete obligation set. It would not establish useful philosophical progress if no relevant obligations could be justified independently of the rival standards, if the task record were chosen only after the results were known, or if every non-regressive comparison needed a hidden weighting rule. In a real application, a replacement that gains one target case by losing an earlier warranted distinction is not a strict-inclusion improvement; it is either a trade-off with no verdict or a case for revising the task profile openly.

A direct test should freeze the task profile and evidence rules before an adversarial comparison, then evaluate both standards on shared and held-out cases. If the proposed progress verdict disappears under reasonable candidate-blind task specifications, or depends on post hoc thresholds, the claim must be restricted to the remaining robust profile or set aside. If the standard’s concepts change the identity of the cases so radically that no cross-version obligation can be defended, the comparison is unavailable; the account must not pretend that a shared measure has survived.

## Significance and open originality question

If the account works, it gives a disciplined middle position between “every standard change is incomparable” and “all progress can be reduced to one accuracy number.” It permits conditional, task-bounded claims while displaying exactly where trade-offs and value disagreements remain. It also marks the limit: local improvement does not by itself establish overall scientific progress.

No closest-source investigation has been conducted. The nearest questions for a source probe are whether primary theories of measurement already formalize progress through preserved operational roles; how primary accounts of scientific progress treat changed concepts and cross-standard comparison; and whether existing approaches already use plural task-relative criteria with a cycle or anti-cherry-picking condition. Until those works are identified and read, originality is unknown and the present rule may be a reformulation, an incomplete version, or a mistaken reconstruction of an existing account.
