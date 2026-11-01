[Home](../README.md) · [Read](final-shortlist.md) · [Method](method.md) · [History](timeline.md) · [Archive](../logs/README.md)

# Ideas that shaped the lab

Several of the project's most distinctive ideas appeared before the first essay. This guide separates the original proposal from the work later carried out. It is an editorial reconstruction from the linked records.

## September 7 · Give an essay a visible ancestry

The first ambition was a research record that travelled with the work: prompts, drafts, objections, decisions, and failed branches. Later that day, Ruslan imagined a tree showing how a final essay emerged and which other essays fell away. The repository now preserves versions and biographies; this edition adds readable journeys for the five recommended or reserve texts. A full interactive tree remains an unbuilt possibility.

[The original archive proposal](../logs/codex/chats/01a07d7c-05c5-7091-a7cc-692e19ff8fca/conversation.md#source-line-54) · [The tree and idea-tournament proposal](../logs/codex/chats/01a07d7c-05c5-7091-a7cc-692e19ff8fca/conversation.md#source-line-642)

## September 7 · Build agents in the judges' image

Ruslan proposed agents based on the real competition judges' writings, comments, and biographies, to judge our internal essay tournaments and selections. His “keep Summer safe” analogy expressed the ambition to model particular people closely. A later correction explicitly rejected reducing that ambition to generic criticism based on their publications.

The implementation used a library of source-grounded profiles, eventually 23, supplied to fresh model sessions. Two profiles criticized each draft in the judge-guided series; the midterm used all 23 per essay; the later selection used two profiles plus three neutral reviewers per text. No separate model weights were trained, and fidelity to the real judges remains unvalidated.

[Original proposal, item 5](../logs/codex/chats/01a07d7c-05c5-7091-a7cc-692e19ff8fca/conversation.md#source-line-642) · [Experiment, sources and calibration](judges.md)

## September 7 · Tournament the ideas before writing essays

Why spend a full writing cycle on every proposal? The plan included comparing ideas themselves. The September extension ran 120 admitted proposals through 24 dossiers, six finalists and three selections; two duplicate proposals had first been replaced. The later 300-attempt search yielded one tentative seed. Keeping unsuccessful proposals visible shows what the filtering actually did.

[Original wording](quotes.md#q03) · [September execution](generation.md#six-ways-to-begin) · [October search](post-midterm.md)

## September 13 · Vary how much criticism a text receives

One Claude series split into five essays without separate critics and five with criticism and revision. Later, two branching cases preserved a common starting draft and compared zero, one, and three critique–revision cycles. The selectors preferred one cycle in one case and three in the other. Different models and contexts prevent treating this as a clean estimate of the best revision count.

[The five-and-five request](quotes.md#q32) · [Revision branches](generation.md#six-ways-to-begin) · [E078's journey](../essays/E078/README.md)

## September 22 · Give two critics different questions

An argument can work and still add little. One critic examined whether it worked; another examined the contribution. After three full manuscripts failed the contribution check, that check moved before drafting. Across 17 attempts, ten were accepted, three rejected after drafting and four before it.

[Ruslan's response to two critics](quotes.md#q33) · [What changed in the creative series](generation.md#check-the-contribution-before-writing-the-essay)

## September 25–27 · Let methods produce different kinds of thought

The extension combined free inquiry, idea tournaments, debate, primary-source expeditions, executable counterexamples, and branching revision. Debate ended with a fresh third author rather than mandatory agreement. One counterexample search was independently reproduced over 65,536 models. These are different ways of developing a question, not evidence that any one method generally wins.

[The six methods](generation.md#six-ways-to-begin) · [Dated campaign record](timeline.md)

## October 7–11 · Hide the biography, then test the judges

Reviewers read full manuscripts without production histories or earlier ratings. The full panel exposed a problem: none of 2,400 primary reviews recommended rejection. The lab then tested planted errors, clearer wording, reversed comparison order, and false accusations. A separate critic also challenged the coordinator's choices.

[The blinding request](quotes.md#q34) · [Every essay, every judge](quotes.md#q35) · [Diagnostics and their limits](evaluation.md)

## October 8–14 · Preserve a way back for an unpopular essay

The process kept a wildcard route and later rechecked 20 preselected rejected essays with 40 blind reviews. Six received conditional returns. This helped build the 22-candidate pool; it did not estimate the number of overlooked good essays in the entire collection.

[Wildcard request](quotes.md#q38) · [Rejection check](post-midterm.md) · [E041's journey](../essays/E041/README.md)

The ambition ran ahead of the implementation in places. Large-scale generation, accurate personal imitation, and a fully interactive ancestry tree should be read as proposals or targets wherever the record does not establish their realization.
