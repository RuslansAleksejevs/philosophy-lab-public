# What a Mathematical Explanation Leaves Open

Take an eight-by-eight chessboard and remove two diagonally opposite corner squares. Can dominoes cover what remains? Each domino covers exactly two squares that share a side. It may not overlap another domino or hang outside the board.

There is a short reason why the answer is no. Each domino covers one black square and one white square. The two removed corners have the same colour. The remaining board therefore has unequal numbers of black and white squares. No collection of dominoes can cover it.

The argument does more than spare us a long search through possible arrangements. It identifies a feature that makes every arrangement fail. It also travels well: any board with unequal colour totals is impossible to cover, whatever its shape.

But suppose someone takes away one black square and one white square instead. The familiar explanation no longer rules out a covering. Does it follow that a covering exists? No such conclusion follows from the explanation. The difference between “this obstacle has gone” and “the task can now be done” is easy to state. It is also easy to lose when a powerful explanation becomes our main way of thinking about a problem.

Learning why this board cannot be covered and learning what the colour counts can tell us about other boards are different achievements. The first concerns the original explanation. The second concerns its use as a method. I will argue that the second can improve while the first stays fixed. In particular, we can move from not knowing whether the counts settle every case to proving that they cannot. That proof lets us reject a whole class of proposed solutions before inspecting their details. This is a limited but useful addition to accounts of mathematical understanding through the abilities it gives us.

## One argument, two boundaries

Let a board be any finite collection of square cells in the usual square grid. We will concentrate on boards connected by shared sides. Colour the underlying grid like a chessboard. A covering uses ordinary dominoes, each occupying two cells that share a side.

The colour argument applies to every board in this family. A covering would pair each black cell with a white cell. Unequal totals therefore rule out a covering. The proof uses a structural rule: every legal domino joins opposite colours. That rule holds throughout our family. What varies from board to board in this test is just the pair of colour totals. To study the test's reach, suppose that these totals are the only information we receive about an individual board. We still know the general domino rules and that the board belongs to our stated family. We are not claiming that the proof literally contains only two numbers, or that every argument inspired by colouring must use only those numbers.

Now consider two boards with six cells. The first is a rectangle with two rows and three columns. Three vertical dominoes cover it. It has three cells of each colour.

For the second board, put four cells in a horizontal row. Call them A, B, C, and D, from left to right. Add a cell E immediately below B and a cell F immediately above C:

```text
    F
A B C D
  E
```

These are six cells, not points, and only shared sides allow a domino. If A is black, then C and E are also black; B, D, and F are white. The board is connected and has the same colour totals as the rectangle.

It cannot be covered. A has only one neighbour, B, so any covering must include a domino over A and B. E also has only one neighbour, B, so any covering must include a domino over E and B. Both cannot occur: they would overlap at B.

The two examples establish something stronger than the bare warning that equal colour totals may not be enough. Any proposed rule that uses only the two colour totals must treat these boards alike. But their answers differ. Consequently, no rule using only those totals can correctly decide coverability for every board in our family. The missing information matters in principle, not just because we have yet to find a clever calculation.

There are now two distinct boundaries. One separates boards with unequal totals from boards with equal totals. It marks where the familiar obstacle is present. Another separates boards that can be covered from boards that cannot. The first does not coincide with the second. The six-cell examples show the gap without requiring a complete account of the second boundary.

This distinction also clarifies the word “failure.” On the second board, the colour test does not fail by giving a false answer. It gives no answer about coverability. The test remains entirely correct. Trouble begins when its silence is treated as permission to conclude that a covering exists.

## What the added example explains

Suppose two careful readers have learned the colour argument. Both can reproduce it, explain why unequal totals prevent covering, and apply it to new boards. Neither infers coverability merely from balance. Both recognise that the argument gives only one direction.

The first reader does not know whether a more ingenious rule using the same two totals could settle every board. Perhaps there is a clever formula waiting to be found. The second reader knows the pair of six-cell examples and can explain why no such rule can succeed. They do not differ in their understanding of why the original mutilated chessboard is impossible. They differ in their understanding of what can be achieved using this information.

Their difference is not simply that the second knows one more answer. Imagine being offered a complicated formula that claims to decide every board from its two colour totals. The first reader has reason to investigate it. The second can reject the claim without checking the formula: whatever it says at three and three, it must give the wrong answer for one of the two boards. This is an ability to rule out an entire approach, not just to detect a mistake in a particular calculation.

The second reader also has a reason to seek more information about individual boards, or to narrow the task. They need not yet know which extra facts will suffice. The six-cell pair does not supply a general solution. It tells them why a complete solution cannot come from rearranging the same two inputs.

This is a worthwhile object of mathematical understanding in its own right. We use mathematics not only to certify answers but also to choose what to investigate. Knowing that a kind of information cannot settle a question can guide that choice as firmly as knowing how to solve another case. A person may fully understand the original explanation while lacking this further ability. We should not erase the distinction by calling every useful new fact a deeper grasp of why the original result holds.

The claim is therefore about understanding a method adopted from an explanation. It is not a requirement that every explanation include an account of its limits. A text answering only the original chessboard question may reasonably stop after the colour proof. A text promising to show how far colour totals solve covering problems has a further task. The pair of boards helps fulfil that task even though the original proof remains unchanged.

The distinction has a simple general form. First specify a family of cases and the information the explanation keeps about each case. Next, find two cases with the same recorded information but different answers to the new question. Their agreement proves that this information cannot determine that answer throughout the family. We can learn this without finding a general procedure for deciding the answer itself.

This is ordinary reasoning about information loss. It applies to algorithms and measurements as well as explanations, so it cannot tell us which proofs are explanatory. Its role here is narrower: it identifies an improvement in understanding the use of an explanation after we have adopted it. Successful applications and justified decisions to abandon a proposed approach are distinct abilities. Counting only the former would miss the latter; none of the views discussed below needs to deny this point.

## The family matters

The pair proves that colour totals cannot decide every board in the family. It does not prove that they fail to settle every balanced case. A connected board with one cell of each colour has only two cells. Connectedness forces them to share a side, so one domino covers it. The same general background that leaves the answer open at totals three and three settles it at one and one.

The family also matters. Consider only rectangular boards with whole-number side lengths. If such a rectangle has an even number of cells, at least one side length is even. Pair successive cells along that direction to produce a covering. If both side lengths are odd, the number of cells is odd and no domino covering is possible. Thus a rectangle can be covered exactly when its area is even.

For these rectangles, equal black and white totals are also equivalent to even area. If one side length is even, cells can be paired along it and the colours balance. If both side lengths are odd, alternating colours leave one colour with one extra cell. So, within this restricted family, colour balance does settle coverability.

This does not repair the earlier argument by extracting more information from the same numbers. It adds knowledge about the shape of the board. That knowledge supplies a construction whenever the totals balance. The general colour argument gives one direction; the rectangular shape gives the other.

What the colour counts can tell us depends on what else we know about the board. “Colour tells us nothing once the totals balance” would be too crude. It would ignore the background restriction that makes a positive answer available for rectangles. Equally, “colour balance decides the problem for rectangles, so it decides it for boards” would quietly discard the premise that made the positive answer possible.

This yields a practical standard for evaluating claims about a method. State the information supplied for each case, the general background, and the question to be answered. If the family is enlarged, an earlier inference may no longer be justified even though every sentence of the original proof remains true. Understanding the method includes noticing that loss.

The family need not be chosen once for all mathematical purposes. Restricting it can be a legitimate achievement. But the restriction must be stated and justified. We cannot count a method as more informative by silently narrowing its task whenever it encounters two cases it cannot distinguish.

## Where this fits among existing views

Avigad treats mathematical understanding through the abilities involved in doing mathematics. He explicitly includes giving counterexamples that show what happens when hypotheses are omitted (*Understanding Proofs*, Part I, §4, preprint pp. 9–10). That is a close predecessor. The present example is a small elaboration: it rules out every complete decision rule with specified inputs, rather than only refuting a theorem with a missing hypothesis. The gain concerns the choice of a method, while understanding the original proof may stay fixed. This does not establish a new general position, and the distinction itself may have other precedents.

Steiner makes variation central to mathematical explanation. His account connects an explanatory proof to a property that characterises an object within a family, and to related proofs obtained by varying it while keeping the proof idea. His proposal is already more subtle than the claim that wider generality always means better explanation. The present argument concerns a different question: what to conclude when the information used by a reason remains fixed while the target result varies. It is one thing to make a proof work on a new case. It is another to show that certain inputs cannot settle a further question. See Steiner, *Mathematical Explanation*, pp. 143–147.

Baron, Colyvan, and Ripley examine mathematical explanation through counterfactual dependence. Their procedure includes fixing some facts, changing others, and following the consequences. That makes the selection of background conditions central. My examples use changes between ordinary, possible boards, so they do not require an account of impossible mathematics. Nor do they refute a counterfactual theory. They show why an assessment based on changed conditions should include cases in which a proposed reason ceases to determine an answer. Asking whether an answer changes must be kept separate from asking whether an argument still settles it. See *A Counterfactual Approach to Explanation in Mathematics*, §§1–2.

Inglis and Mejía-Ramos develop a functional approach that connects explaining a proposition with improving understanding of it (*Functional Explanation in Mathematics*, §§2–3). Our example raises a question about that object of understanding. The extra pair may teach us more about a method without teaching us more about why the original proposition is true. The account should not automatically count one gain as the other. Its cognitive approach also differs from Avigad's account through abilities; these are not interchangeable theories. My claim is compatible with separating the two achievements rather than forcing both into an account of explaining the original proposition.

Variation, counterexamples, and awareness of hypotheses are established themes. The proposed contribution is a precise comparison between two cautious users of a method: one lacks a complete rule, while the other can prove that no complete rule on those inputs exists. The difference matters to what they can reasonably investigate next. It is offered as a useful clarification within existing work, not as a claim to overturn it.

## Three objections

Is this just the familiar warning that an argument does not prove its converse? Unequal colour totals rule out a covering. That does not mean every impossible board has unequal totals. Why give that warning philosophical weight?

The logical distinction is indeed elementary. Nothing here depends on its being new. But saying “do not infer the converse” leaves two questions unanswered. Is the converse false, or merely unproved? And could some other rule, using the very same information more intelligently, settle the issue? The pair of boards answers both. At the shared totals of three and three, the converse is false, and no calculation based solely on those totals can distinguish the outcomes.

The philosophical step is to locate the gain accurately. It need not improve understanding of the original impossibility. It improves understanding of how to pursue a further task. The reader can reject all proposed complete rules on those inputs without separately testing them. That ability is stronger than merely remembering not to reverse the original implication.

The second objection is that the demand is too strong. A mathematician can understand a proof without knowing the exact limits of every technique it uses. Requiring a pair of contrasting examples for every unanswered question would make understanding unattainable.

That would be an unreasonable demand. Neither a complete classification nor a proof of every limitation is required. Someone may understand the original proof and use its one-way test competently without knowing the pair. Learning the pair gives a further ability relevant to finding a complete method. The comparison shows a difference in understanding for that task; it does not set a universal entrance examination for understanding mathematics.

The standard is strongest where a person claims that one feature fully accounts for the pattern of answers in a family. That claim is vulnerable to two cases with the same feature and different answers. A more cautious claim—that this feature explains why a particular case is impossible—survives. Thus the standard also protects good local explanations from an excessive demand to explain everything.

The third objection is that the second board has a better counting explanation after all. Its cells A and E need distinct neighbouring white cells, but between them they have only B. Could we not say that counting remains the right explanation, and that the first colour argument merely counted at the wrong scale?

We can. Counting possible neighbours reveals the local shortage. But that uses information absent from the global totals. The second explanation succeeds precisely because it retains where cells lie and which neighbours they have. It is therefore no reply to the claim that the two colour totals cannot decide the matter.

This objection helps identify what must be held fixed in comparing explanations. A “method” described simply as counting is too broad for the proposed test. Almost any new combinatorial insight might then count as using the same method. We must specify the information supplied for each case, alongside the fixed rules. Otherwise a failed prediction can always be repaired by calling a richer description a further application of the old one. The distinction between global totals and local pairing options makes that move visible.

## What we learn from a limit

The colour argument can explain why a particular board cannot be covered without deciding all balanced boards. Understanding that explanation and understanding how far its numerical test can take us are different achievements.

Two careful readers may share the first and differ in the second. One has no complete rule; the other knows that none can work using only the stated inputs. The pair of six-cell boards supports that stronger knowledge and gives a reason to seek more information or change the task. It leaves both the original proof and many further questions untouched.

When we assess what someone has learned from an explanation, we should therefore specify the task. Better understanding of the original result need not follow from every useful lesson about the method. But the latter lessons matter too. Here we can prove that the same colour totals occur on boards with different answers. We then know that those totals cannot solve the whole problem, however cleverly we calculate with them.

## References

Avigad, Jeremy. 2008. “Understanding Proofs.” In Paolo Mancosu, ed., *The Philosophy of Mathematical Practice*, 317–353. Oxford University Press. [Author preprint](https://www.andrew.cmu.edu/user/avigad/Papers/understanding.pdf).

Baron, Sam, Mark Colyvan, and David Ripley. 2020. “A Counterfactual Approach to Explanation in Mathematics.” *Philosophia Mathematica* 28(1): 1–34. [doi:10.1093/philmat/nkz023](https://doi.org/10.1093/philmat/nkz023). [Institutional preprint](https://api.research-repository.uwa.edu.au/ws/files/65657562/intramath18.pdf).

Inglis, Matthew, and Juan Pablo Mejía-Ramos. 2021. “Functional Explanation in Mathematics.” *Synthese* 198: 6369–6392. First published online 2019. [doi:10.1007/s11229-019-02234-5](https://doi.org/10.1007/s11229-019-02234-5).

Steiner, Mark. 1978. “Mathematical Explanation.” *Philosophical Studies* 34: 135–151. [Accessible transcription](https://paperzz.com/doc/9454464/mathematical-explanation).
