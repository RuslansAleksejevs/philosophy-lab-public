from pathlib import Path
import argparse,concurrent.futures,hashlib,json,shutil,subprocess
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2];RUN=Path(__file__).resolve().parent
TMP=ROOT/'tmp/pdfs/submission-final-layout-20261101';OUT=ROOT/'output/pdf/submission-20261101'
names=['E050','E012','E051','E050-methodology','E012-methodology','E051-methodology']
def work(name):
 p=TMP/name;p.mkdir(parents=True,exist_ok=True)
 source=ROOT/'output/latex/submission-20261101'/name/'main.tex'
 command=['/opt/homebrew/bin/tectonic','--keep-logs','--outdir',str(p),str(source)]
 result=subprocess.run(command,cwd=ROOT,capture_output=True,text=True)
 (p/'compiler-output.txt').write_text(result.stdout+'\n'+result.stderr)
 if result.returncode:raise RuntimeError(name+': '+result.stderr[-3000:])
 dest=OUT/(name+'.pdf' if name.endswith('methodology') else name+'-essay.pdf')
 shutil.copy2(p/'main.pdf',dest)
 for old in list(p.glob('page-*.png'))+list(p.glob('contact-*.png')):old.unlink()
 subprocess.run(['/opt/homebrew/bin/pdftoppm','-scale-to', '1200','-png',str(dest),str(p/'page')],check=True,capture_output=True)
 pages=sorted(p.glob('page-*.png'),key=lambda f:int(f.stem.split('-')[-1]))
 for start in range(0,len(pages),4):
  canvas=Image.new('RGB',(1700,2310),'#e3e3e3');draw=ImageDraw.Draw(canvas)
  for n,page in enumerate(pages[start:start+4]):
   im=Image.open(page);im.thumbnail((805,1120));x=(n%2)*850+10;y=(n//2)*1155+30
   draw.text((x,y-22),name+' / '+page.stem,fill='black');canvas.paste(im,(x,y))
  canvas.save(p/f'contact-{start//4+1}.png')
 print(json.dumps({'name':name,'pages':len(pages),'bytes':dest.stat().st_size}),flush=True)
 return {'name':name,'pages':len(pages),'pdf':str(dest.relative_to(ROOT)),'sources':[{ 'path':str(x.relative_to(ROOT)),'sha256':hashlib.sha256(x.read_bytes()).hexdigest()} for x in [source,source.parent/'body.tex']],'contacts':[str(x.relative_to(ROOT)) for x in sorted(p.glob('contact-*.png'))]}
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--names',nargs='+',choices=names,default=names);args=parser.parse_args()
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:rows=list(pool.map(work,args.names))
 manifest=RUN/'RENDER_MANIFEST.json'
 previous={row['name']:row for row in json.loads(manifest.read_text())} if manifest.exists() else {}
 previous.update({row['name']:row for row in rows})
 for row in previous.values():
  assert all(hashlib.sha256((ROOT/s['path']).read_bytes()).hexdigest()==s['sha256'] for s in row['sources'])
 manifest.write_text(json.dumps([previous[name] for name in names if name in previous],indent=2)+'\n')
