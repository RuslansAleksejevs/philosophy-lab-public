from pathlib import Path
import hashlib,importlib.util,json,re

ROOT=Path(__file__).resolve().parents[2];RUN=Path(__file__).resolve().parent
TEX=ROOT/'output/latex/submission-20261101';FORMS=ROOT/'output/submission-20261101'
spec=importlib.util.spec_from_file_location('renderer',ROOT/'runs/submission-package-20261101/build_sources.py')
F=importlib.util.module_from_spec(spec);spec.loader.exec_module(F)

PREAMBLE=r'''\documentclass[11pt,a4paper]{article}
\usepackage{mathpazo}
\usepackage{fontspec}
\setmainfont{texgyrepagella-regular.otf}[BoldFont=texgyrepagella-bold.otf,ItalicFont=texgyrepagella-italic.otf,BoldItalicFont=texgyrepagella-bolditalic.otf]
\usepackage{amsmath,amssymb}
\usepackage[left=27mm,right=27mm,top=26mm,bottom=27mm,headheight=14pt,headsep=8mm,footskip=12mm]{geometry}
\usepackage{microtype}
\usepackage{booktabs,enumitem,titlesec,fancyhdr,xcolor,needspace}
\usepackage{xurl}
\definecolor{inklink}{HTML}{284B60}
\definecolor{quietink}{HTML}{6B6B6B}
\usepackage[unicode,pdfencoding=auto,colorlinks=true,linkcolor=inklink,urlcolor=inklink,citecolor=inklink,bookmarksopen=true]{hyperref}
\hypersetup{pdftitle={TITLEMETA},pdfauthor={},pdfsubject={},pdfkeywords={},pdfcreator={LaTeX},pdfproducer={}}
\urlstyle{same}
\setlength{\parindent}{1.15em}
\setlength{\parskip}{0.12em}
\linespread{1.075}
\setlength{\emergencystretch}{2em}
\widowpenalty=10000
\clubpenalty=10000
\displaywidowpenalty=10000
\brokenpenalty=10000
\predisplaypenalty=10000
\postdisplaypenalty=10000
\setlist{leftmargin=1.6em,itemsep=0.22em,topsep=0.4em,parsep=0pt}
\titleformat{\section}{\normalfont\bfseries\fontsize{12}{15}\selectfont}{}{0pt}{}
\titleformat{\subsection}{\normalfont\itshape}{}{0pt}{}
\titlespacing*{\section}{0pt}{1.35em}{0.55em}
\titlespacing*{\subsection}{0pt}{1em}{0.35em}
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\fontsize{9}{11}\selectfont\color{quietink}\itshape\nouppercase{SHORTTITLE}}
\fancyhead[R]{\fontsize{9}{11}\selectfont\color{quietink}\thepage}
\renewcommand{\headrulewidth}{0.25pt}
\renewcommand{\headrule}{\hbox to\headwidth{\color{black!18}\leaders\hrule height \headrulewidth\hfill}}
\fancypagestyle{plain}{\fancyhf{}\fancyfoot[C]{\fontsize{9}{11}\selectfont\color{quietink}\thepage}\renewcommand{\headrulewidth}{0pt}}
\begin{document}
\thispagestyle{plain}
\pdfbookmark[0]{TITLEMETA}{document-title}
\begin{center}
{\fontsize{23}{28}\selectfont TITLEPRINT\par}
\vspace{0.7em}
{\color{black!35}\rule{28mm}{0.35pt}\par}
\end{center}
\vspace{0.65em}
\input{body.tex}
\end{document}
'''

REFERENCES={
'E050':[
 ('blom2020','Blom, Tineke'),('bongers2022','Bongers, Stephan'),('dash2005','Dash, Denver'),
 ('ryan2025','Ryan, Oisín'),('sootla2016','Sootla, Aivar, Diego'),('sootla2018','Sootla, Aivar, and Damien'),('weinberger2023','Weinberger, Naftali')],
'E012':[
 ('altanian2024','Altanian, Melanie'),('rule37','Federal Rules of Civil Procedure'),('flowerree2026','Flowerree, A. K.'),
 ('friedman1997','Friedman, Richard'),('gardner2011','Gardner, John'),('nance2010','Nance, Dale'),
 ('nissenbaum2019','Nissenbaum, Helen'),('porat1997','Porat, Ariel'),('ross2023','Ross, Lewis. 2023'),
 ('ross2026','Ross, Lewis. 2026'),('thompson1998','*Thompson ex rel.')],
'E051':[
 ('andonovski2022','Andonovski, Nikola'),('chudnoff2015','Chudnoff, Elijah'),
 ('fulkerson2025','Fulkerson, Matthew'),('nourbakhshi2023','Nourbakhshi, Hamid')]
}

CITATIONS={
'E050':[
 ('weinberger2023','2023, §5, especially pp. 2480–2482'),
 ('blom2020','2020, §§1.1, 2.2, and 3.4, Theorem 2 and proof, PDF p. 7'),
 ('bongers2022','2022, §4.6, Example 4.21, pp. 36–37'),
 ('dash2005','2005, §§5–6, especially PDF p. 7'),
 ('ryan2025','Ryan and Dablander (2025)'),
 ('sootla2016','2016; author preprint dated 5 October 2015, §2.1, p. 3'),
 ('sootla2016','preprint p. 5'),
 ('sootla2016','p. 6, conditions (11)–(13) and inclusion (14)'),
 ('sootla2018','Sootla and Ernst'),
 ('sootla2018','arXiv:1708.00232v1'),
 ('sootla2018','2018 article'),
 ('sootla2018','§III.B, pp. 3–4'),
 ('sootla2018','§III.C, p. 5')],
'E012':[
 ('gardner2011','Gardner 2011'),('porat1997','Porat and Stein 1997'),('friedman1997','Friedman 1997'),
 ('thompson1998','*Thompson* 1998'),('rule37','Rule 37, 2015 Advisory Committee Notes'),
 ('flowerree2026','Flowerree 2026'),('altanian2024','Altanian 2024'),('nissenbaum2019','Nissenbaum 2019'),
 ('nance2010','Nance 2010'),('ross2023','Ross 2023'),('ross2026','Ross 2026')],
'E051':[
 ('nourbakhshi2023','2023, §§4, 6–9, especially §§7–8'),
 ('andonovski2022','2022, “Mental models as structural representations”'),
 ('andonovski2022','“Modeling and surrogative reasoning”'),
 ('andonovski2022','2022, “Episodic representation: What the thesis is not,” first qualification'),
 ('fulkerson2025','2025, §§1–4, especially §4; manuscript p. 8 n. 15, continuing on p. 9'),
 ('chudnoff2015','2015, Introduction and §1, especially manuscript pp. 9–11')]
}

def make_essay(eid):
    md=(RUN/'sources'/f'{eid}.md').read_text()
    title=re.sub(r'^#+\s*','',md.splitlines()[0])
    main,heading,bib=re.split(r'(^## (?:References|Bibliography)\s*$)',md,maxsplit=1,flags=re.M)
    substitutions={};links=[]
    for n,(key,text) in enumerate(CITATIONS[eid]):
        assert main.count(text)==1,(eid,text,main.count(text))
        assert key in dict(REFERENCES[eid])
        token=f'ZCITATIONTOKEN{n}Z'
        main=main.replace(text,token)
        substitutions[token]=r'\hyperlink{ref:'+key+'}{'+F.inline(text)+'}'
        links.append({'target':'ref:'+key,'text':text})
    for n,(key,start) in enumerate(REFERENCES[eid]):
        assert bib.count(start)==1,(eid,start)
        token=f'ZBIBTOKEN{n}Z'
        bib=bib.replace(start,token+start)
        substitutions[token]=r'\hypertarget{ref:'+key+r'}{}\hangindent=1.4em\hangafter=1\noindent '
    # A URL used as its own label must retain xurl's legal line breaks.
    bib=re.sub(r'\[(https?://[^\]]+)\]\((https?://[^)]+)\)',lambda m:m[1] if m[1]==m[2] else m[0],bib)
    linked=main+heading+bib
    # Retain the accepted mathematical content while normalizing table delimiters.
    linked='\n'.join(re.sub(r'\\\((.*?)\\\)',r'\1',line) if line.startswith('| ') else line for line in linked.splitlines())
    if eid=='E012':
        linked=linked.replace('The 2015 Rule 37 notes likewise','\n\nThe 2015 Rule 37 notes likewise').replace('Mara’s case differs:','\n\nMara’s case differs:')
    body=F.body(linked)
    for token,latex in substitutions.items():
        assert body.count(token)==1,(eid,token)
        body=body.replace(token,latex)
    body=body.replace('arXiv:1708.00232v1',r'arXiv:\allowbreak{}1708.00232v1')
    if eid=='E012':
        body=body.replace(r'\section*{References}',r'\clearpage\section*{References}')
    if eid=='E050':
        heads=re.findall(r'^### (A\.\d+) (.+)',md,flags=re.M)
        for number,text in heads:
            h=F.inline(number+' '+text)
            body=body.replace(r'\subsection*{'+h+'}',r'\phantomsection\subsection*{'+h+r'}\label{app:'+number.lower()+'}')
        body=re.sub(r'Appendix (A\.\d+)',lambda m:r'\hyperref[app:'+m[1].lower()+']{Appendix '+m[1]+'}',body)
        body=re.sub(r'Appendices (A\.\d+) and (A\.\d+)',lambda m:r'Appendices \hyperref[app:'+m[1].lower()+']{'+m[1]+r'} and \hyperref[app:'+m[2].lower()+']{'+m[2]+'}',body)
        body=body.replace(r'\section*{Appendix:',r'\clearpage\section*{Appendix:')
        # Keep the final two-line reference with the rest of its bibliography.
        body=body.replace(r'\section*{Bibliography}',r'\enlargethispage{2\baselineskip}\section*{Bibliography}')
    body=re.sub(r'([^\n]+)\n\n(\\begin\{center\}\\renewcommand\{\\arraystretch\})',r'\n\\Needspace{11\\baselineskip}\n\1\n\n\2',body)
    body=body.replace(r'\begingroup\small\setlength{\parindent}{0pt}\setlength{\parskip}{0.65em}\raggedright',r'\begingroup\fontsize{10}{13}\selectfont\setlength{\parindent}{0pt}\setlength{\parskip}{0.55em}\raggedright')
    body=r'\noindent '+body.lstrip()
    write_project(eid,title,body)
    return {'essay':eid,'citations':links,'bibliography_targets':['ref:'+x[0] for x in REFERENCES[eid]],'essay_wording_unchanged':True}

def write_project(name,title,body):
    display=F.inline(title)
    if name=='E050':display=r'What Holding Cannot Tell Us\\About Letting Go'
    pre=PREAMBLE.replace('TITLEMETA',F.esc(title)).replace('SHORTTITLE',F.esc(title)).replace('TITLEPRINT',display)
    if 'methodology' in name:
        pre=pre.replace(r'\setlength{\parindent}{1.15em}',r'\setlength{\parindent}{0pt}').replace(r'\setlength{\parskip}{0.12em}',r'\setlength{\parskip}{0.48em}')
        pre=pre.replace('left=27mm,right=27mm','left=30mm,right=30mm').replace(r'\linespread{1.075}',r'\linespread{1.09}')
    (TEX/name/'main.tex').write_text(pre)
    (TEX/name/'body.tex').write_text(body)

def make_report(eid):
    md=(FORMS/f'{eid}-methodology.txt').read_text()
    body=F.body(md.replace(r'\( ... \)','LITERALINLINEDELIMITERS'))
    body=body.replace('LITERALINLINEDELIMITERS',F.esc(r'\( ... \)'))
    body=body.replace(r'\section*{Appendix A.',r'\clearpage\begingroup\fontsize{10}{12.5}\selectfont\setlength{\parskip}{0.22em}\section*{Appendix A.',1)
    body=body.replace(r'\section*{Appendix F.',r'\clearpage\section*{Appendix F.')
    body+='\n\\endgroup\n'
    write_project(eid+'-methodology','Methodology Report',body)

if __name__=='__main__':
    rows=[]
    selected=json.loads((RUN/'SELECTION.json').read_text())
    for s in selected['essays']:
        assert hashlib.sha256((RUN/'sources'/ (s['essay_id']+'.md')).read_bytes()).hexdigest()==s['manuscript']['sha256']
        rows.append(make_essay(s['essay_id']));make_report(s['essay_id'])
    (RUN/'CITATION_LINKS.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps([{ 'essay':r['essay'],'citation_links':len(r['citations']),'reference_entries':len(r['bibliography_targets'])} for r in rows],indent=2))
