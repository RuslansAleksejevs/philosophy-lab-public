# What a Mathematical Explanation Leaves Open

Remove two opposite corner squares from an ordinary chessboard. Can the remaining board be covered with dominoes? Each domino must cover two squares that share a side. It may not overlap another domino or hang outside the board.

There is a short reason why the answer is no. Each domino covers one black square and one white square. The two removed corners have the same colour. The remaining board therefore has unequal numbers of black and white squares. No collection of dominoes can cover it.

The argument does more than spare us a long search through possible arrangements. It identifies a feature that makes every arrangement fail. It also travels well: any board with unequal colour totals is impossible to cover, whatever its shape.

But suppose someone takes away one black square and one white square instead. The familiar explanation no longer rules out a covering. Does it follow that a covering exists? No such conclusion follows from the explanation. The difference between “this obstacle has gone” and “the task can now be done” is easy to state. It is also easy to lose when a powerful explanation becomes our main way of thinking about a problem.

I will argue that understanding a mathematical explanation as a reusable reason includes understanding what its chosen information leaves open. This is a limited claim. An explanation need not settle every related problem. Yet when we use it across a family of cases, we must distinguish a change in its ability to answer from a change in the answer itself. Sometimes the best way to deepen an explanation is to prove that its information cannot decide a further question. Such a proof adds no new reason for the original result. It changes what we are entitled to do with that reason.

## One argument, two boundaries

Let a board be any finite collection of square cells in the usual square grid. We will concentrate on boards connected by shared sides. Colour the underlying grid like a chessboard. A covering uses ordinary dominoes, each occupying two cells that share a side.

The colour argument applies to every board in this family. A covering would pair each black cell with a white cell. Unequal totals therefore rule out a covering. This proof does not use the board's outer shape or the locations of its cells, except for the general fact that cells sharing a side have different colours.

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

Suppose two readers have learned the colour argument. Both can reproduce it and use it to reject any board with unequal totals. Both can describe infinitely many changes of shape that leave the obstruction intact. Neither makes a mistake on those applications.

The first reader nevertheless treats colour balance as a complete guide to coverability. The second knows the pair of six-cell examples and can explain why no refinement that still uses only the two totals could decide between them. The second reader understands something about the explanation that the first does not: how far the information it retains can take us.

Their difference is not simply that the second knows one more answer. The extra example supports a general restriction on inference. It identifies an entire class of attempted solutions that cannot succeed: those that keep the same two numbers and discard where the cells lie. It also gives a direction for further work. We must recover some information about which cells can be paired, or restrict the family of boards.

This is why the distinction belongs to understanding a mathematical reason. A reason is not just a true sentence stored beside its conclusion. Using it requires recognising what follows from it in the current setting. A person who systematically infers coverability from balance has not merely forgotten an unrelated fact. They have misunderstood the reach of the very reason they offer.

It does not follow that their first insight was worthless. They may understand why the mutilated chessboard cannot be covered while having a poor grasp of the method as a general tool. Understanding comes in degrees and concerns different tasks. My claim concerns the latter task: taking an explanation out of its first example and relying on it elsewhere.

Nor must every reader discover the six-cell board unaided. A more modest reader may say, correctly, that the argument proves only an obstruction and supplies no converse. That already avoids the first reader's mistake. But there is a further gain when we see the two boards. Before seeing them, we may merely lack a proof that the totals settle the issue. Afterwards, we have a proof that they do not. Recognising a gap in our knowledge and knowing a limit of our information are different achievements.

The distinction has a simple general form. First specify a family of cases and the information the explanation keeps about each case. Then find two permitted cases that agree on that information but differ on the further answer being sought. Their agreement proves that this information cannot determine that answer throughout the family. We can learn this without finding a general procedure for deciding the answer itself.

This is ordinary mathematical reasoning, not a new theorem. Its philosophical importance is that it identifies a source of understanding that does not consist in extending the original successful inference. We learn to stop that inference at the right place.

## The family matters

The claim that colour totals are insufficient needs its stated family. Consider only rectangular boards with whole-number side lengths. If such a rectangle has an even number of cells, at least one side length is even. Pair successive cells along that direction to produce a covering. If both side lengths are odd, the number of cells is odd and no domino covering is possible. Thus a rectangle can be covered exactly when its area is even.

For these rectangles, equal black and white totals are also equivalent to even area. If one side length is even, cells can be paired along it and the colours balance. If both side lengths are odd, alternating colours leave one colour with one extra cell. So, within this restricted family, colour balance does settle coverability.

This does not repair the earlier argument by extracting more information from the same numbers. It adds knowledge about the shape of the board. That knowledge supplies a construction whenever the totals balance. The general colour argument gives one direction; the rectangular shape gives the other.

A limit of an explanation's information is therefore relative to what else is held fixed. “Colour tells us nothing once the totals balance” would be too crude. It would ignore the background restriction that makes a positive answer available for rectangles. Equally, “colour balance decides the problem for rectangles, so it decides it for boards” would quietly discard the premise that made the positive answer possible.

This yields a practical standard for evaluating claims of understanding. Ask what the explanation uses, and ask which facts are being supplied by the surrounding problem. If the family is enlarged, an earlier licence to infer may disappear even though every sentence of the original proof remains true. Understanding the proof as a tool requires noticing that loss.

The family need not be chosen once for all mathematical purposes. Restricting it can be a legitimate achievement. But the restriction must be stated and justified. We cannot count a method as more informative by silently narrowing its task whenever it encounters two cases it cannot distinguish.

## Where this fits among existing views

The thought that understanding involves more than checking a proof is well established. Avigad treats mathematical understanding through the abilities involved in doing mathematics. These include choosing strategies, adapting arguments, and seeing what happens when a hypothesis is omitted. My proposal belongs within that broad approach. It specifies one ability: distinguishing the end of a particular inference from a negative answer to the problem. It also distinguishes merely withholding a conclusion from proving that certain information cannot support it. This is an extension of an existing programme, not a rival definition of understanding. See Avigad, *Understanding Proofs*, Part I, §2.

Steiner makes variation central to mathematical explanation. His account connects an explanatory proof to a property that characterises an object within a family, and to related proofs obtained by varying it while keeping the proof idea. His proposal is already more subtle than the claim that wider generality always means better explanation. The present argument concerns a different question: what to conclude when the information used by a reason remains fixed while the target result varies. Successful adaptation is one achievement; showing that a retained description is too coarse for a further task is another. See Steiner, *Mathematical Explanation*, pp. 143–147.

Baron, Colyvan, and Ripley examine mathematical explanation through counterfactual dependence. Their procedure includes fixing some facts, changing others, and following the consequences. That makes the selection of background conditions central. My examples use changes between ordinary, possible boards, so they do not require an account of impossible mathematics. Nor do they refute a counterfactual theory. They show why an assessment based on changed conditions should include cases in which a proposed reason ceases to determine an answer. Asking whether an answer changes must be kept separate from asking whether an argument still settles it. See *A Counterfactual Approach to Explanation in Mathematics*, §§1–2.

Inglis and Mejía-Ramos develop a functional approach, on which explaining is understood through the understanding it produces in an audience. This invites a question about what counts as improvement. More successful applications are one possible gain. Learning a justified restriction on those applications is another. The two gains need not come together. Our two readers could perform identically on every unbalanced board while differing sharply on balanced ones. The example therefore suggests a specific way to examine a claimed gain in understanding, without deciding whether all explanation should receive a functional analysis. See *Functional Explanation in Mathematics*, §§2–3.

These connections limit the claim to originality. Variation, transferable ability, and awareness of hypotheses are not new themes. The proposed contribution is the argument for treating a proof of informational limits as a distinct improvement in our understanding of a reusable explanation. It makes clear why success over many changed cases can coexist with a serious misunderstanding of the reason being used.

## Three objections

The first objection is that this is only the elementary distinction between a sufficient condition and a necessary condition. Unequal colour totals suffice for impossibility. They are not necessary for it. Why give a familiar logical warning philosophical weight?

The logical distinction is indeed elementary. Nothing here depends on its being new. But saying “do not infer the converse” leaves two questions unanswered. Is the converse false, or merely unproved? And could some other rule, using the very same information more intelligently, settle the issue? The pair of boards answers both. At the shared totals of three and three, the converse is false, and no calculation based solely on those totals can distinguish the outcomes.

The philosophical step is to ask what this result changes about understanding. It does not strengthen the original proof of impossibility. It does not help reject an additional board by the same global colour imbalance. Yet it corrects our view of the explanation as a reusable resource. If we count only successful extensions of an argument, we miss this gain. The familiar logic supports the philosophical conclusion; it does not replace it.

The second objection is that the demand is too strong. A mathematician can understand a proof without knowing the exact limits of every technique it uses. Requiring a pair of contrasting examples for every unanswered question would make understanding unattainable.

That would be an unreasonable demand. The proposed standard requires neither a complete classification nor a proof of every limitation. It requires that a person using an explanation across cases distinguish what it establishes from what remains unsupported. When a pair of cases can prove a limit, learning that pair deepens understanding further. The six-cell example exhibits such a gain; it does not set a universal entrance examination for understanding mathematics.

The standard is strongest where a person claims that one feature fully accounts for the pattern of answers in a family. That claim is vulnerable to two cases with the same feature and different answers. A more cautious claim—that this feature explains why a particular case is impossible—survives. Thus the standard also protects good local explanations from an excessive demand to explain everything.

The third objection is that the second board has a better counting explanation after all. Its cells A and E need distinct neighbouring white cells, but between them they have only B. Could we not say that counting remains the right explanation, and that the first colour argument merely counted at the wrong scale?

We can. Counting possible neighbours reveals the local shortage. But that uses information absent from the global totals. The second explanation succeeds precisely because it retains where cells lie and which neighbours they have. It is therefore no reply to the claim that the two colour totals cannot decide the matter.

This objection helps identify what must be held fixed in comparing explanations. A “method” described simply as counting is too broad for the proposed test. Almost any new combinatorial insight might then count as using the same method. We must specify the actual information being used. Otherwise a failed prediction can always be repaired by calling a richer description a further application of the old one. The distinction between global totals and local pairing options makes that move visible.

## Knowing when the reason is silent

A mathematical explanation can reveal why a result holds without drawing the full boundary between truth and falsehood. The colour argument is a clear example. Its value does not depend on deciding all balanced boards.

But once the explanation becomes a general tool, a second question arises: what does its chosen information permit us to infer? A correct answer may take the form of a limit. Two cases with identical retained information and different outcomes show that a further distinction is needed. We then know why some attempts to continue the original argument cannot work.

This is more than modesty about what we happen to know. It is knowledge about what a reason can decide within a stated family. Sometimes mathematical understanding grows because an explanation reaches further. Sometimes it grows because we can prove exactly why, at this point, it must stop.

## References

Avigad, Jeremy. 2008. “Understanding Proofs.” In Paolo Mancosu, ed., *The Philosophy of Mathematical Practice*, 317–353. Oxford University Press. [Author preprint](https://www.andrew.cmu.edu/user/avigad/Papers/understanding.pdf).

Baron, Sam, Mark Colyvan, and David Ripley. 2020. “A Counterfactual Approach to Explanation in Mathematics.” *Philosophia Mathematica* 28(1): 1–34. [doi:10.1093/philmat/nkz023](https://doi.org/10.1093/philmat/nkz023). [Institutional preprint](https://api.research-repository.uwa.edu.au/ws/files/65657562/intramath18.pdf).

Inglis, Matthew, and Juan Pablo Mejía-Ramos. 2021. “Functional Explanation in Mathematics.” *Synthese* 198: 6369–6392. First published online 2019. [doi:10.1007/s11229-019-02234-5](https://doi.org/10.1007/s11229-019-02234-5).

Steiner, Mark. 1978. “Mathematical Explanation.” *Philosophical Studies* 34: 135–151. [Accessible transcription](https://paperzz.com/doc/9454464/mathematical-explanation).
