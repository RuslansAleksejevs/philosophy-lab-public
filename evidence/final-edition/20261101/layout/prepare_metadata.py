from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[2]
RUN=Path(__file__).resolve().parent
OUT=ROOT/'output/submission-20261101'
OLD=RUN/'prior-package/forms'

abstracts={
'E050':'''Knowing what happens while a system is held in place may not tell us what happens when it is released. This essay makes that gap precise using a family of two-variable dynamical systems. The systems agree on every specified long-run outcome while at least one variable is held fixed, as well as on a baseline trajectory and their equilibria and qualitative stability. Yet releasing both variables from the same prepared state leads to opposite stable outcomes in two ranges of an unknown decay rate. The missing information is how quickly the variables move relative to one another. If the equations and time scale are independently justified, one release order guarantees the desired eventual outcome for every positive rate without estimating it. The reverse order does not, and there is no common finite settling time. The example connects limits on causal identification with established work on robust switching: evidence may leave an outcome undetermined while a justified model family still supports a reliable choice.''',
'E012':'''Compensation for lost evidence can later be mistaken for proof of what happened. This essay asks what an institution still owes when it has paid fairly but its earlier wrongdoing continues to make that mistake harder to challenge. A municipal fund destroys photographs it promised to preserve. Later, another office misrepresents the fund's decision, despite receiving an accurate explanation. Two cases isolate the difference that matters: the photographs would have provided a usable defence in one case, but would not have made correction easier in the other. Drawing on Gardner's account of substitute performance, I argue that the fund may still owe proportionate help when its breach continues to impair a defence it promised to protect. Such help must keep historical evidence, entitlement to compensation and binding procedural decisions distinct. The duty is limited by adequate substitutes, privacy, third-party rights and the claimant's choices. Legal examples illuminate the argument without establishing a general duty after proceedings close.''',
'E051':'''Can we learn that two earlier experiences differed without recreating either one? This essay argues that full reconstruction is not always necessary. A simple model shows that recollections can differ from their originals and lose some distinctions, yet never produce a contrast between originals that felt the same. Under that condition, a difference between the outputs entails a difference between the originals. The inference is valid even though neither original can be recovered. Using it as evidence, however, requires independent support for the condition and for the claim that the outputs differ in how they feel; a noisy process needs a different model. That support may be obtained after the contrast is noticed. The argument distinguishes this proposal from Andonovski's account of simplified event models. It challenges a strong reconstruction requirement while leaving the weaker distortion objection intact. It neither establishes the reliability of human memory nor identifies what caused an original difference.'''
}
tldrs={
'E050':'Knowing every specified outcome while a system is held fixed can leave its release outcome unknown, yet a justified model family can still support a release order that works across all its unknown rates.',
'E012':'Fair compensation may leave an institution owing further help when its destruction of evidence still makes a later misrepresentation harder to challenge.',
'E051':'A difference between recollections can reveal a difference between original experiences without reconstructing them, if there is independent reason to rule out a contrast created by recollection itself.'
}

intro='''## 1. Who did what

AI developed the philosophical argument and wrote and revised the essay. The human started the competition project, set its resources and working rules, requested a range of topics, chose among candidates and asked for clearer prose. The human did not supply this essay's central argument or write its sentences. The appropriate submission category is **AI-driven**.

Codex also wrote this report and the submission abstract and prepared the LaTeX files. External quotations and ideas remain attributed to their sources. Human prompts and choices are recorded as human contributions. Dates below refer to 2026 and use UTC unless stated otherwise.
'''

history={
'E050':'''## 2. How the essay developed

The first version was generated on 22 September in an AI-designed campaign seeking varied philosophical ideas. The assigned area was scientific explanation and experimentation. The AI author chose the question, equations, counterexample and argument. Local records identify GPT-6 Astra at medium effort for the author and separate critics. The process included candidate ideas, a bounded web search, a proposal and a contribution check, followed by a draft, separate argument and contribution reviews, and revision. Some exploratory searching overlapped archival work; the record does not show perfect archive-before-exploration ordering.

An October revision by a fresh Astra/high author developed the staged-release result and the distinction between identifying an outcome and choosing an action. Both versions were kept. Fresh Codex comparisons and a separate Claude Opus 5.5 comparison examined them. Literature checks also used separate Codex and Claude routes. Later Codex searches used Astra/max, followed by a recorded GPT-6.1 Sol/xhigh synthesis. These searches did not establish exhaustive priority.

The essay passed through the 22-candidate comparison and the ten-essay deep-review stage. Separate argument and literature reports informed a source-focused revision on 1 November. A fresh Astra/ultra author worked from the selected manuscript and checked primary passages. It acknowledged the diagonal-rate example in Bongers, Blom and Mooij, clarified the relationship to robust switching, and distinguished a common first-stage waiting period from the absence of a common settling time.

A different Astra/ultra checker compared the complete versions and sources. It requested a small grammatical and citation-placement correction in the Sootla-Ernst discussion. The AI coordinator made that exact repair, and a further fresh checker accepted it. The original full review remains recorded as requiring minor fixes; the later check was limited to the repair.

The human then requested a more readable essay and a structured appendix for the calculations. A new Astra/ultra editor rewrote the prose and moved the proofs into five appendix sections. Another fresh critic checked the full original, rewrite, exact changes, abstract and source material. It found no required correction or material loss of content. It checked the calculations, quantifiers, settling-time distinction and main-text references to the appendix.
''',
'E012':'''## 2. How the essay developed

The first version was generated on 8 September in a ten-essay pilot. A neutral instruction left the question, thesis, examples and conclusions to the AI. Each author worked in a fresh context on its own branch. A separate critic reviewed the draft, and the author revised it. Local records identify GPT-6 Astra at ultra effort for the research turns. The question, sources, draft, critique, revision and decision were retained. The pilot did not include another independent review after that first revision.

On 17 October, an Astra/max revision strengthened the connection between lost photographs and the later cost of correction. In one case, preserving the photographs would have provided a cheaper defence; in the other, preservation would not have helped. A separate review followed. The essay then entered the 22-to-ten comparison, with three neutral and two profile-based individual reviews and a disputed-pair comparison. Separate deep argument and literature reviews followed. The human selected it for the final three.

On 1 November, a fresh Astra/ultra author revised the selected manuscript using specific AI-generated tasks and checked source passages. It added precise comparisons with Gardner, the Thompson opinion and the 2015 Rule 37 notes. It made clear that these legal materials are limited analogies: the continuing promise and the paired hypothetical cases support the philosophical argument. A separate fresh checker compared both complete versions, the exact changes and the source packet. It required no correction; it suggested splitting a dense paragraph for readability.

After the first PDFs, the human requested simpler and more natural prose. A new Astra/ultra editor reorganized the essay around Mara's case. A different fresh critic found the argument and limits preserved and accepted the abstract. It identified one ambiguous sentence that could suggest Mara had destroyed her own opportunity. The AI coordinator made the exact recommended wording change. A further fresh critic read both complete versions and their difference, accepted the correction and confirmed that nothing else had changed. That last check covered the sentence and preservation of the rest, not a new review of unchanged arguments or sources.
''',
'E051':'''## 2. How the essay developed

The first version was generated on 22 September in an AI-designed campaign seeking varied philosophical ideas. Its broad area was mind and experience. The AI author chose the problem, formal condition, countermodel and response. Local records identify GPT-6 Astra at medium effort for the original author and separate critics. The process included candidate ideas, a bounded literature search, a proposal and a contribution review before drafting. Separate argument and contribution critics then reviewed the draft, followed by revision. Some exploratory searching overlapped archival work; strict archive-before-exploration ordering is not claimed.

The essay received portfolio reviews but was outside the later ten-essay deep-review shortlist. The human asked to see other candidates, liked its central idea and chose it as the third submission. This was a choice among AI-origin proposals, rather than human authorship of the thesis.

Two fresh Astra/ultra reviewers then examined the unchanged essay, one for its argument and one for its literature comparisons. The literature review identified a missing close comparison with Andonovski's account of episodic mental models. The AI revision plan also called for a clearer distinction between independent evidence and the time at which that evidence is obtained.

On 1 November, a fresh Astra/ultra author received the selected manuscript, specific tasks and checked primary passages. It distinguished Andonovski's event models from the whole phenomenal types discussed in the essay. It clarified later validation, comparison domains, noisy retrieval, reports of difference and the distinction between finding a difference and explaining it. A separate fresh checker compared the complete versions and source packet and required no correction. Neither this check nor the essay validates an actual human memory procedure.

The human then requested simpler and more natural prose. A new Astra/ultra editor rewrote the essay. A different fresh critic checked the complete versions, exact changes, proposed abstract and source material. It found no material loss or required correction. It checked the finite models and the distinctions between valid inference and warranted evidence, whole phenomenal types and their parts, and deterministic and noisy procedures.
'''
}

models={
'E050':'''## 3. Models and roles

- **GPT-6 Astra:** manuscript authorship, revisions, criticism and literature checks. The last authors and checkers used ultra effort through the standard Codex subscription route; earlier stages used medium, high or max as described above.
- **GPT-6 Luna:** earlier evaluation profiles, not manuscript authorship.
- **GPT-6.1 Sol/xhigh:** a recorded literature synthesis.
- **Claude Opus 5.5:** separate comparison and literature review. Claude did not write the submitted manuscript.
''',
'E012':'''## 3. Models and roles

- **GPT-6 Astra:** manuscript authorship, revisions, criticism and literature checks. The last authors and checkers used ultra effort through the standard Codex subscription route; the October revision used max. Earlier portfolio evaluations requested high effort.
- **GPT-6 Luna:** earlier evaluation profiles at high effort, not manuscript authorship.

The traced authorship of this manuscript is Codex/Astra. Claude was used elsewhere in the project, but is not an author of this essay.
''',
'E051':'''## 3. Models and roles

- **GPT-6 Astra:** manuscript authorship, revisions, criticism and literature checks. The original author and critics used medium effort; the last authors and checkers used ultra through the standard Codex subscription route. Earlier portfolio evaluations requested high effort.
- **GPT-6 Luna:** earlier evaluation profiles at high effort, not manuscript authorship.

The traced authorship of this manuscript is Codex/Astra. Claude was used elsewhere in the project, but is not an author of this essay.
'''
}

workflow='''## 4. How editing and review were organized

An AI coordinator kept the project record and managed separate author, critic, literature and evaluation roles. Authors and critics received a restricted packet for one essay, rather than the whole project history or rankings. Earlier stages used separate subagent contexts. The final revisions used fresh Codex CLI sessions with all assigned material in the prompt. Those authors and critics had no browsing or other tools and were instructed not to read other files or delegate. The coordinator supplied the checked primary passages.

For each full revision check, the critic received the complete earlier and revised texts, their exact difference, source passages and access notes. It did not receive the author's self-assessment or earlier verdicts. The later prose checks also covered the abstract and TL;DR. Review focused on premises, reasoning, examples, calculations, citations, objections and limits. A recommendation of “ready” means that the reviewer found no required correction within that material; it is not proof of truth or originality.

Separate contexts reduced exposure to other outputs. They did not make models statistically independent: workers shared model families and public literature, and some earlier tasks shared a filesystem. Recorded isolation limits and disagreements were retained.

Portfolio selection used both neutral AI reviewers and AI profiles based on the published interests of named competition judges. The real judges did not participate or endorse these profiles, and no model was trained to reproduce them. The 22-to-ten round used three neutral and two profile-based voices under a 60/40 scheme, plus comparisons of disputed pairs. Scores and agreement were not treated as proof of quality or novelty.

There was no fine-tuning. Project memory consisted of saved files, not a shared memory automatically given to every worker. Initial authors and literature reviewers used web search and accessible primary sources. File and shell tools supported source retrieval, exact comparisons, archive checks and document preparation.
'''

limits={
'E050':'''## 5. Sources and limits of the result

The final source packets included checked passages on dynamical causal models and robust switching, with explicit versions and page conventions. The Ryan-Dablander comparison remains limited to search excerpts and bibliographic records; its full text was unavailable. The later prose review checked supplied passages and preservation of the earlier source claims, rather than conducting another full literature search.

The mathematical argument is supported by the inequalities in the appendix, not by numerical trajectories alone. It concerns a specified family of systems, a prepared state, an intervention menu and a known time scale. It does not establish empirical applicability or exhaustive novelty. The successful release order is not claimed to work in every model compatible with the endpoint evidence, and it gives no common finite settling time across all positive rates.
''',
'E012':'''## 5. Sources and limits of the result

The final packets supplied Gardner's author eprint, the reproduced Thompson opinion and the 2015 Rule 37 advisory notes, with their pagination and scope. The later full prose review directly checked those passages. Other citations were checked for preservation and consistency with the existing access notes. The full Porat-Stein and Friedman texts were unavailable; their comparisons remain limited to a repository abstract and introductory passage, respectively.

The municipal fund, photographs, later database error and numerical example are hypothetical. The conclusion depends on a promise protecting later use of the evidence, a continuing impairment, a relevant causal connection and proportionality. It establishes neither perpetual liability nor a general rule of law. Existing work on evidential damage, corrective justice and epistemic reparation is acknowledged. The contribution is the particular application and its distinctions.
''',
'E051':'''## 5. Sources and limits of the result

The final packets supplied primary passages from Andonovski, including his distinction between episodic representation and the content of memory experience. Earlier checks considered Nourbakhshi, Fulkerson and Cohen, and Chudnoff. In the later prose review, direct source verification was limited to the supplied Andonovski passages; other citations were checked for preservation and consistency with the access notes.

The finite table illustrates a logical possibility. No memory experiment or empirical calibration was performed. The argument challenges a strong reconstruction requirement while leaving the weaker distortion objection intact. It does not show that real recollection satisfies the required condition, that a verbal report establishes a phenomenal difference, or that an established difference concerns the feature under investigation. Deterministic and noisy comparisons require different treatments.
'''
}

resources='''## 6. Preparation, resources and retained records

After the philosophical revisions, the human requested clearer abstracts and reports, clickable references and more polished typesetting. Codex revised this report and the separate form abstract, and prepared the final LaTeX layout. In-text citations link to the bibliography, whose source links remain clickable. These presentation changes do not alter the accepted essay's wording or argument. The PDF checks cover text preservation, links, fonts, page layout and identifying metadata. The final abstract and report wording were checked by the coordinator against the accepted manuscript and records; they did not receive a further independent scientific review.

Work ran through Codex subscriptions and, where listed above, Claude Code. A reliable per-essay dollar cost has not been allocated: subscriptions, shared searches, rejected candidates and infrastructure served several essays. No zero-cost claim is made. A complete per-essay token or compute total is also unavailable. The project ran from September to submission preparation on 1 November, with waiting and overlapping work; elapsed time is not a measure of compute.

Model and effort labels come from local configurations and run records. They are not an independent verification of server-side routing or the exact commercial version behind each label.

Drafts, prompts, reviews, disagreements, source-access limits and technical failures were retained privately with version links and file hashes. A local collector saved available visible conversations and artifacts, not hidden reasoning or a certified complete provider transcript. Historical capture gaps and unprocessed tool material remain documented.

The appendices below preserve selected exact instruction blocks. Raw project conversations also contain identifying administrative material, so they are not attached to this anonymous report. Further relevant records can be prepared with appropriate redaction. A private repository link is not offered as a substitute for the report.
'''

def main():
    checks=[]
    for eid in ['E050','E012','E051']:
        form=json.loads((OLD/f'{eid}-form.json').read_text())
        form['abstract']=abstracts[eid];form['tldr']=tldrs[eid]
        form['name_attribution']='Yes, attach my name'
        form['philosophical_background']='Academic in another field'
        form['ai_experience_suggestion']='Extensive. I use AI daily or professionally.'
        (OUT/f'{eid}-form.json').write_text(json.dumps(form,ensure_ascii=False,indent=2)+'\n')
        previous=(OLD/f'{eid}-form.txt').read_text()
        import re
        previous=re.sub(r'(?s)(TL;DR\n).*?(\n\nABSTRACT\n)',lambda m:m[1]+tldrs[eid]+m[2],previous)
        previous=re.sub(r'(?s)(ABSTRACT\n).*?(\n\nAI INVOLVEMENT\n)',lambda m:m[1]+abstracts[eid]+m[2],previous)
        previous=previous.replace('NAME ATTRIBUTION / BACKGROUND / EXPERIENCE\nChoose your own truthful answers.','NAME ATTRIBUTION\nYes, attach my name\n\nPHILOSOPHICAL BACKGROUND\nAcademic in another field\n\nAI EXPERIENCE\nSuggested: Extensive. I use AI daily or professionally.')
        previous+='\nREQUIRED CONFIRMATIONS\nEntry Limit: no more than three submissions in your name.\nOriginality: confirm the essay is unpublished and not under review elsewhere.\nPublication Consent: consent to public release of the essay and methodology report after winners are announced.\nLicense: keep CC BY 4.0.\nReaders and Signatures: keep the form defaults.\n'
        (OUT/f'{eid}-form.txt').write_text(previous)
        (OUT/f'{eid}-abstract.txt').write_text(abstracts[eid]+'\n')
        old=(OLD/f'{eid}-methodology.txt').read_text()
        appendices='## Appendix A.'+old.split('## Appendix A.',1)[1]
        title=form['title']
        report='# Methodology Report\n\n*'+title+'*\n\n'+intro+'\n'+history[eid]+'\n'+models[eid]+'\n'+workflow+'\n'+limits[eid]+'\n'+resources+'\n'+appendices
        (OUT/f'{eid}-methodology.txt').write_text(report)
        checks.append({'essay':eid,'abstract_words':len(abstracts[eid].split()),'report_words':len(report.split()),'original_prompt_appendices_unchanged':report.split('## Appendix A.',1)[1]==old.split('## Appendix A.',1)[1]})
    (RUN/'METADATA_MANIFEST.json').write_text(json.dumps(checks,indent=2)+'\n')
    print(json.dumps(checks,indent=2))

if __name__=='__main__':main()
