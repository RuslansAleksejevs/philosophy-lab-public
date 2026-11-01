# The Signal in Saying No: Confidentiality, Opt-Outs, and Design-First Responsibility

## Abstract

A person may be free to refuse disclosure and still be exposed by refusing. In a group protecting a legitimate confidential matter, an optional procedure can make one member’s refusal unusually informative: the pattern of everyone’s answers may identify the exception. I call this response-pattern disclosure. The risk does not establish a general right against inference, nor does it make peers responsible for lying or imitating a refusal. It raises a narrower question: what must the person who governs the procedure do?

I defend a defeasible, design-first responsibility. When someone accepts control of a confidentiality procedure, assures people that it will protect their information, and can reasonably foresee that its output will make a protected refusal materially identifying, that person should first consider an effective and proportionate redesign. This is a focused application of existing ideas about confidentiality, inferential privacy, and responsibility for information flows. Its originality is not established. The proposal is meant to identify a practical class of cases, not to claim a new general right or a complete theory of privacy.

## 1. The problem with an apparently free choice

Suppose a small group has agreed not to expose a member’s sensitive personal circumstance to outsiders. The circumstance is legitimate to keep private: it is not evidence of an imminent threat, abuse, or public wrongdoing that others have a duty to reveal. The group’s coordinator introduces an optional round of individual responses, perhaps to learn who is affected by a topic or to decide who will speak at a meeting. Participants may answer or decline.

The rule appears respectful. No one is forced to disclose. Yet imagine that the coordinator tells the group that exactly one member has a protected exception. If Ada declines and everyone else answers, the choice reveals who she is. Even without that announcement, an audience may know enough about the group to interpret the pattern. Each answer is voluntary, but the relation among answers creates information that no single answer contains.

The familiar question is whether Ada has a right to say no. She does. A second question is whether others have a duty to imitate her refusal. That question is harder. If they do, their choice may reduce the signal, but the price is that they must perform a response they otherwise would not make. It may also pressure them to mislead an outsider or suppress their own speech. Treating solidarity as an automatic duty makes privacy depend on asking the rest of a group to carry the cost of a procedure they did not design.

The prior question is about the procedure itself. If a coordinator promised confidentiality or took responsibility for protecting the group’s information, did that responsibility include noticing that the opt-out could identify the person who used it? A meaningful choice must be assessed against the information that its exercise makes available. Offering an unprotected refusal does not by itself make the procedure privacy-preserving.

I call the risk response-pattern disclosure: an observer learns something about a person or group from the pattern of individual answers, refusals, or deviations from a shared response. The term describes an information channel, not yet a moral wrong. My claim is narrow. When a procedure-governor has accepted responsibility for a confidentiality procedure, invited reliance on that responsibility, and can reasonably foresee that the procedure makes a protected refusal materially identifying, the governor has a defeasible responsibility to consider redesign before shifting the burden to other participants to conceal the signal. This is not a general right to prevent inference, a duty on peers to lie, or a rule that privacy always defeats public interests.

## 2. Privacy, inference, and the response pattern

Three distinctions keep the claim limited.

First, confidentiality is not the same as secrecy or anonymity. A group may share information internally while seeking to limit its flow to outsiders. Helen Nissenbaum’s account of contextual integrity helps explain why privacy depends partly on who gathers information, about whom, in what role, and under which rules of distribution. Information disclosed in one context is not automatically available for every use merely because some participants know it. But contextual integrity is not a command to preserve every custom. Existing practices still require normative scrutiny, including scrutiny of the values they serve and the effects of changing them (Nissenbaum 2004). The question is not simply whether a convention has been broken. It is what information moves between which roles and what interests are affected by that flow.

Second, inference is not identical to disclosure by the person inferred about. Benedict Rumbold and James Wilson argue that privacy interests can sometimes extend to information a person did not intend to reveal, even where another person infers it from information that was made public (Rumbold and Wilson 2019). Their account is a close antecedent: the subject need not utter the sensitive fact for a signal to expose it. It also places moral attention on people who appropriate or transmit information, not only on the person who first made something public. My proposal does not discover that inference can threaten privacy. It asks a more specific question about the earlier point at which a procedure-governor chooses how responses will be collected and released. Whether that is a distinct contribution, rather than a new application of their account, remains unresolved.

Third, shared confidentiality and inferential privacy are related but different. Michele Loi and Markus Christen distinguish the privacy of information held in common by a group from privacy threatened by inferences about group members. They reject an absolute right to prevent inference, while leaving room for limited inferential-privacy claims where protection does not impose unreasonable costs. They also emphasize that those who produce knowledge should consider its social effects (Loi and Christen 2020). My claim fits within that limited approach. It does not give groups ownership of every fact outsiders infer. It concerns a procedure controlled by a responsible actor, a foreseeable output, and an individual whose legitimate choice to withhold may be converted into evidence by that output.

This comparison also sets the scale of the argument. Loi and Christen already connect inferential privacy with responsibilities in knowledge production; Rumbold and Wilson already discuss moral duties around inferred information. The proposal here is narrower and more procedural: where a person has accepted governance of a confidentiality procedure and encouraged reliance on it, the role-holder should assess the response channel before it produces a foreseeable identifying pattern. The relevant addition, if there is one, is the focus on a prospective design choice and on who controls it. The cited work may already support that application. I do not claim field-wide novelty.

## 3. Why a refusal can carry information

A small Bayesian model shows how a response pattern can identify someone without anyone stating the underlying fact. Imagine ten people. Exactly one has a protected exception and always declines to answer. Everyone else independently declines with probability one third per round, perhaps because they value privacy for their own reasons. Assume an observer knows these rules, starts with an equal prior probability for each person, and sees exactly who declines.

The observer can rule out anyone who answered. Among those who declined, the stipulated model assigns equal likelihood to each person being the protected person. If X is the number of non-protected people who also declined, the posterior probability assigned to the protected person after observing the pattern is 1/(1+X). Since X has a binomial distribution with nine trials and probability one third, the expected posterior probability assigned to the true protected identity is:

> E[1/(1+X)] = [1 − (2/3)^10] / [10 × (1/3)] ≈ 0.295.

Before observing any response pattern, the same symmetric observer assigns each person probability 0.10. Under the same assumptions, the expected posterior rises to about 0.623 when the observer sees who refuses in both of two rounds, and about 0.849 after three rounds. The values follow from the stipulated model; they are not measurements of actual audiences.

This example establishes only that a procedure can create an identifying signal. It does not show that real audiences reason this way, that 0.295 is an acceptable or unacceptable risk, or that this probability is a general privacy metric. It assumes one protected person, a known rule, a uniform prior, independent choices, and fixed refusal tendencies. Prior knowledge, correlated choices, unequal behavior, and repeated releases may weaken or strengthen the inference. The model establishes possibility, not the moral duty.

The example does, however, clarify why the response pattern matters. Even if each participant exercises an individual choice, the organizer has chosen which choices become visible together, when they become visible, and to whom. A reasonable assessment of confidentiality must include those design choices. It is the procedure’s output that is under the organizer’s control; the organizer does not control what an observer later believes.

## 4. What an accepted role requires

The moral bridge is not the bare fact that someone can reduce a risk. Three grounds must be kept apart.

An explicit promise creates one ground. Someone who assures participants that their information will remain confidential gives them a reason to rely on that assurance. The promise’s content matters: a promise against direct naming is different from a promise that no participant will be identifiable through the procedure. But a role-holder cannot preserve only the literal wording while knowingly arranging an output that defeats the assurance’s evident purpose. If the assurance was too broad to keep, the role-holder should say so before people rely on it, rather than treat it as empty after the fact.

Accepted governance creates a second ground. A person who takes charge of a protective procedure chooses its rules, output, and audience. That control makes the person well placed to foresee ordinary consequences of the design. The role does not make the organizer responsible for every inference by every observer. It does make a foreseeable and avoidable output risk part of the organizer’s work. A title alone is insufficient: the relevant person must have accepted responsibility for the procedure and have some control over it. Nor does every procedural role create the same promise-based obligation. Where no confidentiality assurance was made, a narrower responsibility to assess the output may follow from voluntary control, but the stronger reliance-based duty defended here does not automatically follow.

These grounds combine in the central case. The special design-first responsibility requires both an accepted governance role with meaningful control over the response channel and an assurance or undertaking that reasonably invites reliance on confidentiality. The undertaking explains why the affected person should not be left to bear the consequence of an undisclosed design choice. Control explains why redesign is an appropriate first response from this particular role-holder. Neither condition alone does all the work. A person who made a promise but cannot control the channel may owe candor, help, or a request to the controller, but may not be able to redesign it. A person who controls an ordinary procedure without undertaking confidentiality may have reasons to assess it, but the heightened duty defended here is not established by capacity alone.

The Tri-Council Policy Statement for research involving humans offers a useful but limited analogue. Its Article 5.1 treats a researcher’s promise of confidentiality as ethically significant and calls on institutions to support that duty (TCPS 2 2022, art. 5.1). That illustrates how an assurance can create responsibilities that go beyond avoiding an intentional direct disclosure. It does not establish a general duty on coordinators or peer groups to redesign every response pattern. The policy governs research ethics. Its Chapter 10 example, in which one participant’s waiver of anonymity should not compromise other group members’ anonymity, runs in the opposite direction from Ada’s individual opt-out. It helps show that a person cannot waive other people’s protections, but does not itself settle the present case.

A third ground is general aid. Peter Singer’s principle that one should prevent serious harm at relatively low cost may support redesign when it is easy and effective (Singer 1972). But that principle is not the basis of the special responsibility. A low-cost opportunity to help can arise even when no one accepted a role or made a promise. Conversely, if concealment would violate a stronger duty or harm others, a role-based promise may have to yield. The general aid ground may support the same action, but it cannot by itself explain why the procedure-governor, rather than every bystander, has the first responsibility.

John Rawls’s distinction between justifying a practice and judging a particular action within it is a useful analogy for role-based duties: accepted practices can give actions their meaning and structure. But Rawls also cautions that relatively few moral actions are defined by practices. His account does not prove that every group has a confidentiality practice or that its organizer must redesign a procedure (Rawls 1955). The argument here must stand on the undertaking, reliance, and control just described; the analogy only helps identify why an accepted role can matter.

## 5. When redesign should come first

A design-first duty needs usable limits. It does not require a numerical privacy threshold or perfect anonymity. The role-holder should ask six practical questions.

1. **Is the information legitimately protected?** Group agreement alone is not enough. If withholding would conceal abuse, a serious threat, or public wrongdoing that others have a duty to report, the confidentiality interest may be overridden.

2. **What undertaking and control exist?** Identify the actual assurance, what participants could reasonably understand it to cover, who chose the response rules, and who can change or delay release. Do not infer responsibility from job title or technical capacity alone.

3. **Who is the relevant audience?** Consider an ordinary, relevant observer: someone who may realistically see the output and has the ordinary background information available in this setting. Do not assume an omniscient attacker, but do not ignore information the organizer already knows the audience will have.

4. **Is the inference reasonably foreseeable and material?** Foreseeability can rest on concrete features such as a very small group, an announced number of exceptions, individually visible answers, a known response rule, an audience familiar with members, or repeated releases that reveal the same pattern. An inference is material when it would meaningfully narrow the identity or expose sensitive information with a real consequence for the person—not merely when an observer could form any belief at all. These are comparative judgments, not numerical cutoffs.

5. **Would an alternative materially reduce the signal at proportionate cost?** Compare realistic options against the procedure’s legitimate purpose: collect responses privately; report an aggregate only when its size and composition withstand the relevant audience’s knowledge; delay or combine releases; permit a different truthful response; or avoid collecting individual information. Aggregation and delay are not automatically safe. If a well-informed audience can still isolate the person, they have not solved the problem. Nor must the organizer choose an alternative that defeats a stronger purpose, destroys necessary accuracy, imposes serious burdens, or violates another person’s rights.

6. **What does the affected person choose, and what duties compete?** Ask before exposing the person to a risk inconsistent with the assurance. The person may want to speak or may decide that participation is worth the risk. Their choice matters, but it must be informed and free; it cannot be inferred from silence or extracted under pressure. A duty to protect confidentiality does not require suppressing the person’s own speech, and a person cannot waive other group members’ interests.

Why should redesign have priority over mere warning? The role-holder chose or accepted the channel, and the assurance invited reliance on protection from its foreseeable effects. If a proportionate change can preserve the procedure’s legitimate purpose while materially reducing the identifying cost of refusal, requiring the affected person to carry that cost would let the organizer discharge the role by warning of a harm the organizer can prevent. The point is not that design is always better than consent. It is that an assurance about a controlled procedure should include reasonable attention to what the procedure communicates through its structure, not just the wording of its prompt.

A notice-and-choice option can sometimes be enough. Before a person decides, notice should plainly state: who will see the responses; whether responses will be linked to names or shown together; what an opt-out pattern may reveal; whether rounds will repeat; what practical consequences could follow; what the assurance does and does not cover; and what alternatives exist. The person must be able to decline without penalty, coercion, or loss unrelated to the procedure. There must be a real alternative, not a forced choice between exposure and an important benefit. The person must be free to participate or to withhold, and the procedure must not compromise someone else’s promise or rights.

Those criteria make informed choice more than a disclaimer. Suppose an optional workplace survey is not promised to be confidential, responses will be visible to a small authorized panel, and the decision the survey informs genuinely requires individual responses. If the affected employee receives an accurate explanation in advance, can decline without penalty, has meaningful alternatives, and freely chooses to answer, notice and choice may suffice. A redesign that makes the information unusable could undermine the legitimate purpose without honoring a prior promise.

A different case calls for redesign first. Suppose a small support group’s coordinator promised that a member’s sensitive circumstance would remain confidential, then proposes to announce that exactly one person is exempt from a visible round of responses. The exemption will make that member’s refusal identifying to the very audience the promise was meant to protect. If a private response channel or a procedure that does not reveal individual choices would still serve the group’s purpose, a warning that “your refusal will identify you” does not discharge the promise. The person may still choose to disclose their own circumstance, but the coordinator should ask before changing the assurance’s scope. To change it, the coordinator must seek prospective, informed agreement rather than treat a warning as a unilateral cancellation. The redesign must also protect other members who have not agreed.

If no reasonable design alternative works, the role-holder should be honest about the limit before proceeding and seek the affected person’s genuinely voluntary choice. This may satisfy the duty when the person understands the audience, inference, and consequences; can refuse without a penalty or coercive loss; and no prior assurance is being silently contradicted. Where an assurance already covers the relevant inference, the organizer should not assume that notice alone releases it. The person’s agreement may permit a prospective change for their own information, but the original commitment continues to constrain the handling of earlier disclosures and of other people’s information.

## 6. Why peers are not presumptively required to cover

Other participants may sometimes reduce the signal by refusing too. But that possibility does not establish a default duty to cover. Peer refusal can impose costs, distort a procedure, frustrate a legitimate decision, or pressure people to conceal their own reasons. It may also shift the work to people who did not design the channel and never accepted a confidentiality role.

Truthful refusal is different from lying. A participant who says, “I do not want to answer either,” may be saying something true. Such a response can be a voluntary way to protect another person, provided it is safe and does not undermine a stronger duty. But it should not become a compulsory performance. The organizer may invite voluntary cooperation after examining the channel itself; it should not presume that group membership creates consent to deception or refusal.

If the procedure is safe only when everyone else voluntarily imitates the protected person, that fact is a reason to examine the design. A coordinator can instead prevent the visible signal, withhold individual outputs, or decline to run a procedure that cannot keep its assurance. The organizer is responsible for the procedure’s output, not for guaranteeing what an outsider will infer from facts independently available.

## 7. Objections and limits

### No one has a right against inference

A person who refuses in front of others communicates something. Observers may reasonably infer facts from public conduct. A design-first duty may look like an indirect attempt to control other people’s beliefs.

This objection defeats a broad right to prevent inference, but not the limited claim here. The observer’s freedom to reason and the organizer’s responsibility for a controlled procedure are distinct. An observer may be permitted to infer a fact while the organizer remains responsible for not producing an avoidable identifying output after inviting reliance on confidentiality. No duty arises without a legitimate protected interest, accepted responsibility, foreseeable material risk, control, and a proportionate remedy. The role-holder regulates the channel it controls, not what anyone is allowed to think.

### Notice should be enough

If the affected person is told the risk and consents, why require redesign? Sometimes a clear warning and a free choice are enough. The proposal accepts that. But notice does not do the same work as prior assurance. A person’s decision to participate after hearing that refusal will identify them cannot automatically be treated as release from a promise that the procedure would protect them. Nor is choice meaningful when refusing carries the very predictable cost the organizer undertook to avoid and there is a proportionate alternative. The test is whether the person has a genuine option, not whether a disclosure form contains the right words.

### Redesign may be costly or defeat the purpose

A privacy-preserving format may reduce accuracy, make a necessary decision impossible, increase administrative burdens, or prevent people from receiving credit. The duty is therefore defeasible. Organizers should compare practical alternatives and explain the limits of protection. If no reasonable alternative preserves both the legitimate purpose and the assurance, the organizer may need to pause, disclose the limit, and leave the decision to the affected person, subject to duties to others. The promise should not be treated as unlimited, but it must not be emptied by avoidable design choices.

### Confidentiality can protect wrongdoing

A group might use secrecy to avoid scrutiny or protect unjust power. Agreement does not by itself make information legitimate to withhold. A serious threat, abuse, or public-interest claim may override the confidentiality interest. Nissenbaum’s contextual approach helps identify the information flow; it does not validate every existing norm. If the underlying secrecy is unjustifiable, this design-first claim does not apply.

### The organizer cannot foresee every audience

An observer may combine responses with private information or use an unexpected inference. A role-holder cannot satisfy a duty to predict every possibility. The standard is reasonable foreseeability from the information available to someone in that role, not omniscience. It can be met by noticing a small group, an announced single exception, visible responses, repeated release, and likely audience knowledge. A guarantee of perfect anonymity is neither required nor presumed.

### This is just an application of prior work

The strongest intellectual objection is that the argument restates existing positions. Loi and Christen already allow bounded inferential-privacy claims and assign attention to those who produce knowledge. Rumbold and Wilson already discuss privacy interests and duties connected with information inferred from public signals. That may be right. The present essay does not claim a new general theory. It proposes that, in a defined class of procedures, those ideas support a prospective duty for the person who controls the response channel and has invited reliance on confidentiality. The case for treating this as a distinct contribution remains open pending broader comparison with privacy, research ethics, and statistical-disclosure work.

## 8. Conclusion

An opt-out can preserve a person’s formal freedom while making the exercise of that freedom identifying. Information may come from the pattern of responses rather than from any answer taken alone. That possibility does not establish a general right against inference, a universal secrecy norm, or a duty on peers to lie.

It does support a limited principle of responsible design. When a person accepts governance over a confidentiality procedure, invites reliance on an assurance, controls the response channel, and can reasonably foresee that the procedure will make a protected refusal materially identifying, that person should first consider an effective and proportionate redesign. Notice and informed choice can sometimes suffice, but only when the choice is real and the procedure does not silently defeat an assurance already given. If the purpose cannot reasonably be served another way, the affected person’s freely made choice and competing duties remain decisive.

This principle is an application proposal, not a proven novelty claim or an absolute right to be unknowable. It asks that confidentiality be evaluated by what a procedure actually reveals—including what an audience can learn from saying no—and that the people who govern the procedure take responsibility for its foreseeable output.

## Bibliography

Canadian Institutes of Health Research, Natural Sciences and Engineering Research Council of Canada, and Social Sciences and Humanities Research Council of Canada. 2022. *Tri-Council Policy Statement: Ethical Conduct for Research Involving Humans*, 2nd ed., Chapters 5 and 10. https://ethics.gc.ca/eng/policy-politique_tcps2-eptc2_2022.html.

Loi, Michele, and Markus Christen. 2020. “Two Concepts of Group Privacy.” *Philosophy & Technology* 33: 207–224. https://doi.org/10.1007/s13347-019-00351-0.

Nissenbaum, Helen. 2004. “Privacy as Contextual Integrity.” *Washington Law Review* 79: 119–158. https://digitalcommons.law.uw.edu/wlr/vol79/iss1/10/.

Rawls, John. 1955. “Two Concepts of Rules.” *The Philosophical Review* 64 (1): 3–32. https://doi.org/10.2307/2182230.

Rumbold, Benedict, and James Wilson. 2019. “Privacy Rights and Public Information.” *Journal of Political Philosophy* 27 (1): 3–25. https://doi.org/10.1111/jopp.12158.

Singer, Peter. 1972. “Famine, Affluence, and Morality.” *Philosophy & Public Affairs* 1 (3): 229–243.
