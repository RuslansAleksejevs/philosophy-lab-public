from pathlib import Path
import argparse,hashlib,json,re,subprocess,unicodedata
import pdfplumber
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[2];RUN=Path(__file__).resolve().parent
PDF=ROOT/'output/pdf/submission-20261101'
def norm(s):return ''.join(c for c in unicodedata.normalize('NFKD',s).lower() if c.isalnum())
def parts(s):
 s=s.replace('0.90 × 0.90 + 0.10 × 0.40 = 0.85','@@MATH@@')
 s=re.sub(r'\\\[.*?\\\]','\n@@MATH@@\n',s,flags=re.S)
 s=re.sub(r'\\\(.*?\\\)','@@MATH@@',s)
 s=re.sub(r'`[^`]+`','@@MATH@@',s)
 s=re.sub(r'\[([^\]]+)\]\((?:https?://[^\s)]+|#[^\s)]+)\)',r'\1',s)
 s=re.sub(r'^\|.*$','\n@@MATH@@\n',s,flags=re.M)
 s=re.sub(r'(?m)^\d+\. ', '\n\n',s)
 return [norm(p) for p in re.split(r'@@MATH@@|\n\s*\n',s) if norm(p)]
parser=argparse.ArgumentParser();parser.add_argument('--selection',default='SELECTION.json');parser.add_argument('--names',nargs='+');args=parser.parse_args()
selection=json.loads((RUN/args.selection).read_text())
sources={x['essay_id']:ROOT/x['manuscript']['path'] for x in selection['essays']}
rows=[]
for p in sorted(PDF.glob('*.pdf')):
 if args.names and p.stem not in args.names:continue
 eid=p.name[:4];method='methodology' in p.name
 source=ROOT/f'output/submission-20261101/{eid}-methodology.txt' if method else sources[eid]
 s=source.read_text();plain=[];alltext=[]
 with pdfplumber.open(p) as doc:
  for page in doc.pages:
   crop=page.crop((0,65,page.width,page.height-50))
   alltext.append(crop.extract_text(x_tolerance=2,y_tolerance=3) or '')
   prose=crop.filter(lambda x:x.get('object_type')!='char' or 'TeXGyrePagella' in x.get('fontname',''))
   plain.append(prose.extract_text(x_tolerance=2,y_tolerance=3) or '')
 target=norm('\n'.join(plain));cursor=0;missing=[];fragments=parts(s)
 for n,fragment in enumerate(fragments):
  at=target.find(fragment,cursor)
  if at<0:missing.append({'part':n,'start':fragment[:160],'end':fragment[-80:]})
  else:cursor=at+len(fragment)
 reader=PdfReader(p);urls=[];destinations=[];attachments=[]
 for page in reader.pages:
  for ann in page.get('/Annots',[]):
   a=ann.get_object()
   if a.get('/Subtype')=='/FileAttachment':attachments.append(str(a))
   action=a.get('/A',{})
   if '/URI' in action:urls.append(str(action['/URI']))
   if '/D' in action:destinations.append(str(action['/D']))
   if '/Dest' in a:destinations.append(str(a['/Dest']))
 markdown_urls=re.findall(r'\[[^\]]*\]\((https?://[^\s)]+)\)',s)
 without_links=re.sub(r'\[[^\]]*\]\(https?://[^\s)]+\)','',s)
 expected=markdown_urls+[u.rstrip('.,;') for u in re.findall(r'https?://[^\s)\]]+',without_links)]
 text='\n'.join(alltext)
 privacy=re.findall(r'ruslan|aleksejev|/Users/|Philosophy Lab|github\.com',text,re.I)
 log=ROOT/'tmp/pdfs/submission-final-layout-20261101'/(eid+'-methodology' if method else eid)/'main.log'
 warnings=[line for line in log.read_text().splitlines() if any(k in line for k in ['Overfull','Missing character','undefined'])]
 fonts=subprocess.run(['/opt/homebrew/bin/pdffonts',str(p)],capture_output=True,text=True,check=True).stdout
 row={'pdf':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size,'pages':len(reader.pages),'source':str(source.relative_to(ROOT)),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'prose_fragments':len(fragments),'unmatched_prose':missing,'author_metadata':reader.metadata.get('/Author'),'identifying_strings':privacy,'file_attachments':attachments,'missing_urls':sorted(set(expected)-set(urls)),'internal_links':destinations,'named_destinations':sorted(reader.named_destinations),'compiler_warnings':warnings,'fonts':fonts}
 rows.append(row)
 (RUN/(p.stem+'-extracted.txt')).write_text(text)
 print(p.name,'pages',len(reader.pages),'unmatched prose',len(missing),'missing URLs',len(row['missing_urls']),'internal links',len(destinations),'warnings',warnings)
 if missing:print(json.dumps(missing[:5],ensure_ascii=False))
out=RUN/'PDF_QA.json'
if args.names and out.exists():
 prior={r['pdf']:r for r in json.loads(out.read_text())};prior.update({r['pdf']:r for r in rows});rows=[prior[k] for k in sorted(prior)]
out.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
