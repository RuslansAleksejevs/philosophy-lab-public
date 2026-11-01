from pathlib import Path
import argparse, hashlib, importlib.util, json, re, sys, unicodedata, zipfile
from datetime import datetime, timezone
import pdfplumber
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[2]; RUN=Path(__file__).resolve().parent
PDF=ROOT/'output/pdf/submission-20261101'; TEX=ROOT/'output/latex/submission-20261101'; FORMS=ROOT/'output/submission-20261101'
def load(p): return json.loads(p.read_text())
def ref(p): return {'path':str(p.relative_to(ROOT)), 'sha256':hashlib.sha256(p.read_bytes()).hexdigest(), 'bytes':p.stat().st_size}
def dump(p,v): p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def norm(s): return ''.join(c for c in unicodedata.normalize('NFKD',s).lower() if c.isalnum())
parser=argparse.ArgumentParser();parser.add_argument('--archive',action='store_true');args=parser.parse_args()

if args.archive:
    manifest=load(RUN/'READY.json')
    for item in manifest['artifacts']+manifest['qa_and_build']:
        assert ref(ROOT/item['path'])==item,item['path']
    sys.path.insert(0,str(ROOT/'scripts'))
    from research_archive import Archive
    paths=[ROOT/x['path'] for x in manifest['artifacts']+manifest['qa_and_build']]+[RUN/'READY.json']
    print('Saving the final package in the canonical archive.',flush=True)
    with Archive(ROOT/'research/archive').writer() as w:
        outputs=[w.put(p.read_bytes()) for p in paths]
        event=w.append({'kind':'submission.final_layout.package.accepted',
            'actor':{'id':'codex-submission-package-coordinator','role':'assistant'},
            'session_id':'01a190b5-03e2-70d0-8fcf-b4a1e67148d0','run_id':RUN.name,
            'operation_id':RUN.name+':final-package','attempt_id':RUN.name+':final-package:1',
            'parents':[load(RUN/'SCOPE.json')['parent_event']],
            'outputs':list(dict.fromkeys(outputs)),'payload':manifest},RUN.name+':final-package:v1')
    receipt={'status':manifest['status'],'event_id':event['id'],'event_sequence':event['sequence'],
             'event_sha256':event['sha256'],'manifest':ref(RUN/'READY.json'),
             'submitted':False,'github_updated':False}
    dump(RUN/'FINAL_RECEIPT.json',receipt);print(json.dumps(receipt),flush=True)
    sys.exit(0)

selection=load(RUN/'SELECTION.json');qa=load(RUN/'PDF_QA.json');render=load(RUN/'RENDER_MANIFEST.json')
assert len(qa)==6
for q in qa:
    assert ref(ROOT/q['pdf'])['sha256']==q['sha256']
    assert ref(ROOT/q['source'])['sha256']==q['source_sha256']
    for field in ['unmatched_prose','author_metadata','identifying_strings','file_attachments','missing_urls','compiler_warnings']:
        assert not q[field],(q['pdf'],field)
    assert set(q['internal_links'])<=set(q['named_destinations'])
    assert q['bytes']<50_000_000

# All final contacts were inspected by the coordinator, including the final
# E012 report after its Appendix F page-break repair. This records that review.
visual={'all_pages_inspected':True,'pages_inspected':sum(q['pages'] for q in qa),
        'unresolved_defects':[], 'method':'Visual inspection of every final rendered page through 14 contact sheets; checks of margins, headers, page numbers, formulas, table, bibliography and prompt appendices.',
        'documents':[]}
for q in qa:
    name=Path(q['pdf']).stem.replace('-essay','')
    row=next(r for r in render if r['name']==name)
    for s in row['sources']:assert ref(ROOT/s['path'])['sha256']==s['sha256']
    visual['documents'].append({'pdf':q['pdf'],'sha256':q['sha256'],
        'pages_inspected':list(range(1,q['pages']+1)),
        'contacts':[ref(ROOT/p) for p in row['contacts']]})
dump(RUN/'VISUAL_QA.json',visual)

tool_results=load(RUN/'LATEX_TOOL_RESULTS.json')
latex={'all_six_succeeded':True,'results':[]}
for row in tool_results['results']:
    assert row['desktop_compilation']['kind']=='success'
    latex['results'].append({**row,'sources':[ref(TEX/row['name']/n) for n in ['main.tex','body.tex']]})
assert len(latex['results'])==6
latex['E012_methodology_final_pagebreak_recompiled']=tool_results['final_E012_methodology_recompiled_successfully_after_appendix_F_pagebreak']
dump(RUN/'LATEX_DIAGNOSTICS.json',latex)

spec=importlib.util.spec_from_file_location('layout',RUN/'build_layout.py')
layout=importlib.util.module_from_spec(spec);spec.loader.exec_module(layout)
links=[];build=[]
for selected in selection['essays']:
    eid=selected['essay_id'];source=ROOT/selected['manuscript']['path']
    assert ref(source)==selected['manuscript']
    assert (RUN/'sources'/f'{eid}.md').read_bytes()==source.read_bytes()
    md=source.read_text();form=load(FORMS/f'{eid}-form.json')
    assert form['title']==re.sub(r'^#+\s*','',md.splitlines()[0])
    assert form['abstract']==(FORMS/f'{eid}-abstract.txt').read_text().strip()
    assert form['name_attribution']=='Yes, attach my name'
    assert form['philosophical_background']=='Academic in another field'
    assert form['pdf']==eid+'-essay.pdf' and form['methodology_report']==eid+'-methodology.pdf'
    report=(FORMS/f'{eid}-methodology.txt').read_text()
    oldreport=(RUN/'prior-package/forms'/f'{eid}-methodology.txt').read_text()
    assert report[report.index('## Appendix A.'):]==oldreport[oldreport.index('## Appendix A.'):]
    oldtex=(RUN/'prior-package/latex'/eid/'body.tex').read_text()
    newtex=(TEX/eid/'body.tex').read_text()
    mathpattern=r'(?<!\\)\$.*?(?<!\\)\$|\\\[.*?\\\]|\\begin\{(?:equation|align)\*?\}.*?\\end\{(?:equation|align)\*?\}'
    oldmath=re.findall(mathpattern,oldtex,re.S);newmath=re.findall(mathpattern,newtex,re.S)
    assert oldmath==newmath,(eid,'Mathematical LaTeX differs')
    words=len(re.split(r'^## (?:References|Bibliography)\s*$',md,maxsplit=1,flags=re.M)[0].split())
    assert words<6000
    build.append({'essay_id':eid,'manuscript':ref(source),'whitespace_words_excluding_bibliography':words,
                  'math_expressions_unchanged':len(oldmath),'abstract':ref(FORMS/f'{eid}-abstract.txt'),
                  'methodology':ref(FORMS/f'{eid}-methodology.txt'),'form':ref(FORMS/f'{eid}-form.json')})
    reader=PdfReader(PDF/f'{eid}-essay.pdf');references=dict(layout.REFERENCES[eid]);destrows=[]
    actual_links=[]
    for page in reader.pages:
        for annotation in page.get('/Annots',[]):
            ann=annotation.get_object();act=ann.get('/A',{})
            target=act.get('/D',ann.get('/Dest'))
            if target is not None:actual_links.append(str(target))
    with pdfplumber.open(PDF/f'{eid}-essay.pdf') as document:
        for key,start in references.items():
            key='ref:'+key
            assert key in actual_links and key in reader.named_destinations
            destination=reader.named_destinations[key]
            pageidx=reader.get_destination_page_number(destination);page=document.pages[pageidx]
            y=float(page.height)-float(destination.top)
            nearby=page.crop((0,max(0,y-2),page.width,min(page.height,y+45))).extract_text() or ''
            assert norm(start) in norm(nearby),(eid,key,nearby)
            destrows.append({'target':key,'page':pageidx+1,'top_points':round(y,3),
                             'expected_reference_start':start,'near_destination_text':nearby})
    for key,phrase in layout.CITATIONS[eid]:assert 'ref:'+key in actual_links
    links.append({'essay':eid,'pdf':ref(PDF/f'{eid}-essay.pdf'),
                  'source_citations_linked':len(layout.CITATIONS[eid]),'targets':destrows,
                  'all_expected_citations_and_targets_present':True})
dump(RUN/'BUILD_MANIFEST.json',build);dump(RUN/'LINK_TARGET_QA.json',links)

fidelity={'reviewer':'AI coordinator; not a new independent scientific reviewer',
 'manuscript_wording_unchanged':True,'prompt_appendices_unchanged':True,
 'abstracts':{
  'E050':'Retains the restricted evidence menu, unknown positive decay rate, two sufficient outcome ranges, independently justified model/time scale, eventual guarantee and absence of a uniform settling deadline. Does not generalize to every system compatible with the evidence.',
  'E012':'Retains the causal contrast, continuing promise, proportionate substitute assistance, distinction between history/entitlement/procedural force, claimant choice and limits of legal analogies. Does not assert a general legal duty.',
  'E051':'Retains the conditional contrast inference, non-reconstruction, independent warrant for the comparison and phenomenal difference, permissible later validation, different treatment of noise, distinction from event models, surviving weaker objection and absence of empirical validation.'},
 'methodology':'Narratives checked against the prior archived reports and selected review histories. Historical model labels, roles, dates, access limits, human steering, exact instruction appendices and missing cost allocation are retained. The current metadata edit is explicitly disclosed.',
 'new_research_or_independent_scientific_review':False}
dump(RUN/'METADATA_FIDELITY_REVIEW.json',fidelity)

(FORMS/'README.txt').write_text('''Final submission package: E050 / E012 / E051

Use THREE separate OpenReview entries. For each entry:
1. Upload its essay PDF to PDF.
2. Upload its separate methodology PDF to Methodology Report.
3. Paste its Title, Keywords, TL;DR, Abstract and AI Models Used from the matching form text file. Abstract is a separate text field; the methodology report is a separate uploaded file.

The essay wording is the accepted, independently checked prose revision. Final layout adds clickable in-text bibliography citations, restrained article typography and improved page breaks. The final abstract and report language was revised and coordinator-checked. E050's mathematical appendix stays inside its essay PDF and within the word limit.

Confirmed personal choices: Name Attribution = Yes, attach my name; Philosophical Background = Academic in another field. Keep the essay PDFs anonymous for judging. The signed-in author profile is Ruslans Aleksejevs.

Deadline: 1 November 2026, 03:59 PST San Francisco / 11:59 UTC.

The ZIP is for convenience; do not upload it in place of either required PDF. LaTeX sources are included for editing, not submission. Compile each main.tex with Tectonic or XeLaTeX. All six PDFs and all 44 pages were checked. This preparation step did not submit any entry.
''')
(FORMS/'FORM_GUIDE_RU.txt').write_text('''Три отдельные заявки. Дедлайн: 1 ноября 2026, 03:59 PST по Сан-Франциско (11:59 UTC).

Для каждой заявки:
PDF → соответствующее эссе.
Methodology Report → соответствующий отдельный отчёт.
Abstract → текст из поля Abstract в файле form.txt или отдельного abstract.txt.
Title, Keywords, TL;DR и AI Models Used → готовые значения из соответствующего form.txt.
ZIP и исходники LaTeX в эти поля не загружать.

Authors: выбранный профиль Ruslans Aleksejevs. В PDF имя не добавлять.
AI Involvement: AI-driven. AI developed the arguments and wrote the essay; humans set the topic or direction and selected among outputs.
Name Attribution: Yes, attach my name — подтверждено пользователем.
Philosophical Background: Academic in another field — подтверждено пользователем.
AI Experience: предлагаю Extensive. I use AI daily or professionally.; подтвердить по факту.
Self Assessment: предлагаю Good. On a par with the average published paper.; необязательное поле.
Estimated AI Usage Cost In USD: оставить пустым; достоверной стоимости отдельного эссе нет.
Entry Limit: подтвердить, если всего не более трёх заявок.
Originality: подтвердить, если эссе не опубликовано и не находится на рассмотрении в другом месте.
Publication Consent: обязательное согласие на публикацию эссе и отчёта после объявления победителей.
License: CC BY 4.0; Readers и Signatures: оставить системные значения.

После отправки каждой заявки сохранить номер, ссылку и подтверждение загрузки обоих PDF. Подготовка файлов сама по себе не является подачей.
''')
files=sorted(PDF.glob('*.pdf'))+sorted(TEX.glob('*/*.tex'))+sorted(FORMS.glob('*.txt'))+sorted(FORMS.glob('*.json'))
zpath=ROOT/'output/Submission-Package-E050-E012-E051.zip'
with zipfile.ZipFile(zpath,'w',zipfile.ZIP_DEFLATED) as z:
    for p in files:
        arc='pdf/'+p.name if p.is_relative_to(PDF) else 'latex/'+str(p.relative_to(TEX)) if p.is_relative_to(TEX) else 'forms/'+p.name
        z.write(p,arc)
with zipfile.ZipFile(zpath) as z:
    assert z.testzip() is None
    for p in files:
        arc='pdf/'+p.name if p.is_relative_to(PDF) else 'latex/'+str(p.relative_to(TEX)) if p.is_relative_to(TEX) else 'forms/'+p.name
        assert z.read(arc)==p.read_bytes()
support=['SCOPE.json','SELECTION.json','CITATION_LINKS.json','LINK_TARGET_QA.json','METADATA_MANIFEST.json',
         'METADATA_FIDELITY_REVIEW.json','PDF_QA.json','VISUAL_QA.json','BUILD_MANIFEST.json',
         'RENDER_MANIFEST.json','LATEX_TOOL_RESULTS.json','LATEX_DIAGNOSTICS.json',
         'prior-package/SNAPSHOT.json','build_layout.py','prepare_metadata.py','compile_render.py',
         'check_pdfs.py','finalize.py']
manifest={'status':'FINAL_SUBMISSION_FILES_READY','prepared_at':datetime.now(timezone.utc).isoformat(),
          'parent_event':load(RUN/'SCOPE.json')['parent_event'],'essays':build,
          'artifacts':[ref(p) for p in files]+[ref(zpath)],'qa_and_build':[ref(RUN/p) for p in support],
          'six_pdfs_pages':visual['pages_inspected'],'submitted':False,'github_updated':False,
          'new_scientific_review':False,'name_attribution':'Yes, attach my name',
          'philosophical_background':'Academic in another field',
          'limits':'Presentation and metadata preparation preserves the accepted manuscript and its recorded argument, source-access and archival limits. This is not new evidence of novelty or empirical validity.'}
dump(RUN/'READY.json',manifest)
print(json.dumps({'status':manifest['status'],'pdf_pages':visual['pages_inspected'],
                  'files':len(files),'zip':ref(zpath),'words':[(x['essay_id'],x['whitespace_words_excluding_bibliography']) for x in build]},ensure_ascii=False))
