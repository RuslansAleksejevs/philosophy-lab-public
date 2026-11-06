# Independent critique: How Much Must a Rational Plan Settle?

**Verdict: specific substantive revision required.** The stated mathematical results survive review, and the supplied computations reproduce exactly within their bounds. The outstanding problem is the contribution: two close primary sources substantially narrow what can be claimed as new. A second issue is the shift from completing a fixed finite menu list to preserving permissions against arbitrary additional menus. Neither issue warrants discarding the correct example or proof, but the present contribution statement should not be accepted unchanged.

Reviewed version: `draft-01.md`, SHA-256 `07e433f526be0f99e03518d34a587014496a6103db657b9053977cada33b73ba`. This is a fresh argument/source/model review, not a simulated judge report. The source-check stage was sealed before preparation of this critique. Exact coverage and calculations are in its archived packet.

## 1. The central inference reconstructed

The comparison class is the full Cartesian product of row choices. Each row has strictly positive probability, independent of the state under every admitted probability. A complete policy maximizes expected utility at a probability exactly when each of its rows does. Therefore a partial policy has an admissible completion precisely when the intersection of its row-witness sets is nonempty. Intersecting further row constraints preserves all admissible completions and cannot lead to a dead end while that intersection remains nonempty.

The additional proposition is also valid. If a nonempty closed convex subset C′ omits a point of C, nearest-point separation supplies a utility vector whose expectation at that omitted point is strictly greater than at every point of C′. A binary menu can exploit this difference. The lost act remains compatible with the previous rows and is excluded under C′. This establishes a possible loss from binding oneself to a narrower practical record; it does not make the completion selected under C′ irrational.

The manuscript appropriately distinguishes this mathematical witness from an agent's belief, physical randomization from constructing a definite policy, and modal coordination from sequential choice. These qualifications matter and should survive revision.

## 2. Material issue: the contribution needs a closer literature comparison

The strongest objection is not that the proof fails. It is that its proposed combination of conservative continuation and distinguishability of probability sets is close to established results. The bibliography misses both parts of that connection.

**Conservative continuation.** Decadt, Erreygers and De Bock construct the conservative E-admissible extension of partial choice assessments using all agreeing probability models. Section 4, especially manuscript pages 6–7, explicitly motivates retaining choices unless the assessment warrants rejecting them. This is close to the essay's permission-preservation rationale, rather than merely an earlier efficient algorithm. There are real differences: their assessments specify rejections, include a background dominance order, and can induce nonconvex sets with strict constraints. A chosen row in this essay only requires weak maximality at a common witness; choosing one act does not declare every rival impermissible. The two formalisms should therefore be compared carefully, not called identical. But the source makes it untenable to present retaining all compatible models as an unqualified new intermediate object. [Author manuscript, §§3–4 and 10](https://users.ugent.be/~jdbock/documents/AD-2026-FSS-paper.pdf).

**Distinguishability.** Seidenfeld, Schervish and Kadane already prove that two distinct probability sets have different finite-option admissibility patterns. Their 2007 paper's §2, Theorem 2 and corollary, supplies a stronger set-distinguishability result that also covers nonconvex sets. The essay's closed-convex assumptions enable its particularly simple binary separator with strict margins, but the general thought that discarding probability models can change admissible choices is established prior work. The 2007 text also identifies an earlier convex-set result; that antecedent was not independently read in this review. [Actually retrieved 2007 proceedings text, §2](https://www.cmu.edu/dietrich/philosophy/docs/seidenfeld/Coherent%20Choice%20Functions.pdf).

These sources do **not** establish that the precise modal-planning interpretation has already been published. They do establish that the mathematical and conservative-choice ingredients need explicit attribution and that their combination is a modest application unless a further philosophical gain is defended.

**Required repair:** engage both texts in the contribution section, distinguish permissibility assessments from selected policy rows, and identify what follows about deliberation or delegation beyond their established machinery. Merely adding them to the bibliography will not resolve the issue. If the defensible residue is a conceptual application clarifying practical versus epistemic commitment, say so and explain why that application changes the interpretation of the coordination argument. Do not rebrand the elementary construction as a new representation result.

## 3. Material issue: two different continuation domains

Section 3 begins with a fixed finite list D₁,…,Dₙ. Section 4's theorem instead chooses a further menu after the narrower record C′ has been specified. That quantifier is essential:

> For every proper closed convex C′, there exists a possible additional menu that distinguishes it from C.

It does not follow that C′ loses a completion in the agent's particular fixed list of remaining menus. The manuscript acknowledges restricted act domains, so this is a clarification of the contribution's scope, not a refutation of the displayed theorem. The opening contrast and final claim about the exact practical content of the record nevertheless make the fixed-list and extensible-list tasks sound more interchangeable than they are.

**A critic-originated countercheck uses the manuscript's own fourth menu.** Keep its three settled rows, so C=[1/2,5/8], and suppose the only remaining menu is {Z,T}, where Z=(0,0) and T=(−17,23). At p=23/40, both acts have expected utility zero and all three earlier selections are maximizing. Thus the proper singleton C′={23/40} preserves **both** completions of that fixed four-row problem. The manuscript's selected proxy 11/20 loses Z, but point selection as such need not lose a completion in this particular closed problem. The independent verification program checks both complete policies against all 24 possibilities.

More generally, for any fixed finite family of remaining menus, choose one witness for each admissible completion. That finite witness set preserves every completion in the family; its convex hull does too, since it lies inside C. The hull is not guaranteed to be proper, so this is not a universal compression theorem. It shows why preservation over a fixed family is governed by whether the reduced set intersects every admissible completion's witness region, rather than simply whether it equals C.

**Required repair:** distinguish (a) preserving completions of an already fixed menu list from (b) preserving permissions uniformly against arbitrary added menus. State the separation theorem and any necessity claim under (b). Present C as a sufficient exact representation for (a), without suggesting that every proper reduction changes that fixed family's permissions. A short acknowledgement of the 23/40 example would make the distinction concrete.

This countercheck and the finite witness-selection observation originate in this critic context. If adopted, they must enter the revised essay's lineage as critic contributions, not as the author's previously demonstrated result.

## 4. Philosophical significance and the strongest reply

A defender of point selection can agree with the entire mathematics. The old theorem concerns which completed policies are acceptable; it need not prescribe the internal order of deliberation. A fixed deterministic version of the proposed construction ultimately produces just one common-witness policy. An account giving that construction as a permissible implementation has therefore not overturned the coordination result or its behavioral force.

The manuscript already accepts much of this reply. Its strongest remaining response is the delegation example: an authorization defined by previously settled rows differs from an authorization bound to a selected probability. That is a real extensional distinction when the menu domain separates the records. The question is whether showing that distinction adds enough to known conservative-extension results to bear the essay's contribution claim.

The current paper by Pettigrew and colleagues offers an actual textual target: its introduction says the agent needs to select a probability to determine her plan. In contrast, §3.2.1 explicitly uses an as-if interpretation, and §4.2.1 asks how a set of strategies should itself be evaluated as an act. The essay should explain whether it corrects a literal procedural reading of the introduction or supplies an implementation compatible with the more careful statements. It should not imply that those authors infer actual precise belief or mistake a partial instruction sheet for a randomized act. [Pettigrew, Campbell-Moore and Konek, introduction and §§3.2.1, 4.2.1](https://doi.org/10.1007/s11238-025-10088-2).

Preserving all permissions remains an additional specification of what an implementation is meant to represent, not a new obligation that E-admissibility imposes on every acting agent. The draft says this, but its abstract and final paragraph should keep the same restrained force. This is a scope limit rather than an independently invalid premise.

## 5. Source accuracy and checks that passed

- **Elga:** the reference to narrowing and planning is accurate. Footnote 23 already describes removing probabilities that do not endorse the performed act. Cite that footnote when explaining what is inherited and what changes when the record tracks rows of an unexecuted modal plan. The draft correctly avoids claiming to solve Elga's general temporal objection.
- **Huntley and Troffaes:** Example 6 really has all local strategies admissible but only two global combinations admissible, while subtree perfectness holds there. The diagram and text agree. The draft's limited attribution is fair. The backward-induction citation supports the modest claim about earlier algorithms; its general proofs were not independently audited here.
- **Main numerical example:** witness intervals are [5/8,3/4], [3/8,5/8], [1/4,3/8]; the A/B fair policy has utility 4 in each weather state and the safe policy 5. The biased-coin supremum and its stated strict dominance range are correct. This is expected-utility dominance, not guaranteed statewise dominance over the coin-weather outcomes.
- **General proofs:** the common-witness argument, the binary same-menu lemma and the separating-hyperplane construction are valid under the assumptions stated. Their force does not depend on the finite counts. In particular, zero menu probabilities, restrictions linking rows, dependent menu/state models or restricted utility domains need separate treatment.
- **Executable verification:** inspected both programs, copied them into a new directory, and ran only the copies using `python3 -B`. Both exits were zero. All substantive JSON values matched after excluding generation timestamps, and both exhaustive witness logs were byte-identical. The originals' hashes remained unchanged.
- **Tested bounds:** 300 binary and 2300 ternary menus over utility coordinates 0,…,4; 37 ternary menus fail, with 74 ordered bad pairs. The continuation sweep tested 1176 binary menus over coordinates −3,…,3 against six admissible partial policies: 7056 comparisons and 476 lost permissions. An additional independent crossing-point implementation checked the explicit nine-policy and 24-policy examples and the fixed-menu countercheck. None of this certifies exhaustive philosophical novelty.

## 6. Revision conditions and residual uncertainty

Retain the valid model, examples and separation proof, but revise the contribution around the closest literature and the continuation-domain distinction. Separate a procedural clarification from a new rationality constraint, and make the exact target in the coordination debate explicit. These are the material acceptance conditions; cosmetic editing alone is insufficient.

A satisfactory revision need not agree with this review's estimate of significance. It must give a reasoned answer to the antecedents and the finite-menu countercheck. If no distinctive philosophical gain remains after that comparison, retain the work as a correct application rather than claim the desired original contribution. This review does not rank it against other essays or certify competition eligibility, originality, or philosophical truth.
