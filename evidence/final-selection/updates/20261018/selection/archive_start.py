"""Canonical input acceptance. Run once after the independent mechanical checks."""
from pathlib import Path
from datetime import datetime,timezone
import sys,json,hashlib,os
D=Path(__file__).resolve().parent;R=D.parents[1];sys.path.insert(0,str(R/'scripts'))
from research_archive import Archive
from capture_codex import capture,resolve_session
from philosophy_round import start,record
from essay_lineage import base_entry,index,append as append_lineage
RUN=D.name;auth=json.loads((D/'AUTHORIZATION.json').read_text());SID=auth['session_id']
def sha(b):return hashlib.sha256(b).hexdigest()
def save(name,v):
 with (D/name).open('x') as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
assert not (D/'START_RECEIPT.json').exists()
for name in ['runner.py','test_runner.py','METHOD_CHECK.json','TRANSPORT_TESTS.json']:assert (D/name).is_file(),name
for x in json.loads((D/'PROTECTED_VERSIONS.json').read_text())['files']:assert sha((R/x['path']).read_bytes())==x['sha256']
source=resolve_session(SID,R)
files=[]
for p in sorted(D.rglob('*')):
 if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc':files.append({'path':str(p.relative_to(R)),'sha256':sha(p.read_bytes()),'bytes':p.stat().st_size})
for name in ['AGENTS.md','START_HERE.md','workflows/FINAL_SELECTION_60_40.md']:
 p=R/name;files.append({'path':name,'sha256':sha(p.read_bytes()),'bytes':p.stat().st_size})
save('INPUT_MANIFEST.json',{'files':files,'frozen_at':datetime.now(timezone.utc).isoformat()})
print('Inputs verified; waiting for canonical archive writer.',flush=True)
with Archive(R/'research/archive').writer() as w:
 st=start(R,w,RUN,SID,'research',str((D/'METHOD.json').relative_to(R)),[str((D/n).relative_to(R)) for n in ['AUTHORIZATION.json','BASELINE_DECISIONS.json','INPUT_MANIFEST.json','CONFIGURATION.json']],stage_id='FINAL_SELECTION',selection_round_id='22_TO_10_60_40')
 print('Round start accepted; recording explicit current authorization.',flush=True)
 caps=[]
 for item in auth['decision_history']:
  cap=capture(R/'research/archive',source,SID,R,start_line=item['source_line'],end_line=item['source_line'],run_id=RUN,archive_writer=w)
  assert cap['status']=='BOUNDED_COMPLETE',cap
  caps.append(cap)
 save('CAPTURE_START.json',caps)
 for x in files:assert w.put((R/x['path']).read_bytes())==x['sha256']
 for x in json.loads((D/'PROTECTED_VERSIONS.json').read_text())['files']:assert w.put((R/x['path']).read_bytes())==x['sha256']
 ev=w.append({'kind':'research.selection.inputs.accepted','actor':{'id':SID,'role':'AI'},'session_id':SID,'run_id':RUN,'operation_id':RUN,'attempt_id':'preparation-v1','parents':[st['id']]+[x['coverage_event_id'] for x in caps],'bindings':st['bindings'],'outputs':[x['sha256'] for x in files]+[w.put((D/'INPUT_MANIFEST.json').read_bytes())],'payload':{'status':'SELECTION_INPUTS_ARCHIVED','files':files,'reviews':110,'additional_ceiling':50,'ratio':'60/40','boundary':'Exact current human request, role correction, accepted proposal and frozen artifacts. Existing collector gaps remain; explicit bounded capture replaces dependency on stale collector progress. No full-provider capture.'}},RUN+':inputs:v1')
 events={e['id']:e for e in w.events()};known=index(events.values());mapping={}
 baseline=json.loads((D/'BASELINE_DECISIONS.json').read_text())
 for c in baseline['candidates']:
  v=next(x for x in c['versions'] if x['current']);matches=[e for e in known.values() if any(a.get('sha256')==v['sha256'] for a in e['payload']['entry']['artifacts'])]
  assert matches,('No existing lineage',c['id'])
  direct=[e for e in matches if e['payload']['entry']['kind'] in ['origin','draft','revision','final']];previous=(direct or matches)[-1];old=previous['payload']['entry']
  row=next(x for x in json.loads((D/'ALLOCATION.json').read_text())['rows'] if x['candidate']==c['id'])
  le=base_entry(RUN+':'+c['id']+':assigned',old['entity'],'selection','Текущая версия включена в сравнение22 →10; три нейтральных и два судейских свежих отзыва. Результата ещё нет.')
  le['parents']=[old['id']];le['artifacts']=[{'path':v['path'],'sha256':v['sha256'],'role':'frozen-candidate'},{'path':str((D/'ALLOCATION.json').relative_to(R)),'sha256':w.put((D/'ALLOCATION.json').read_bytes()),'role':'frozen-review-allocation'}];le['evidence']=[ev['id']];le['occurred_at']=datetime.now(timezone.utc).isoformat();le['actor']='AI coordinator';le['configuration']={'requested':json.loads((D/'CONFIGURATION.json').read_text())['requested_for_all_reviewers'],'observed':{'parent':json.loads((D/'CONFIGURATION.json').read_text())['observed_parent'],'workers':'not dispatched'}};le['workflow']=RUN;le['decision']={'action':'admit to comparison','selected_for_ten':False,'blind_id':row['blind_id']};le['gaps']=['No philosophical verdict at input acceptance.']
  lev=append_lineage(w,le,SID,known,events);known[le['id']]=lev;events[lev['id']]=lev
  mapping[c['id']]={'entity':old['entity'],'parent_entry':old['id'],'assigned_entry':le['id'],'assigned_event':lev['id'],'blind_id':row['blind_id'],'version':v}
 save('LINEAGE_INPUTS.json',mapping)
 # The accepted AI proposal contains the selection question; bind its exact visible authorship.
 proposal_cap=caps[next(i for i,x in enumerate(auth['decision_history']) if x['role']=='assistant')]
 (D/'QUESTION_RU.txt').write_text('Какие десять из22нынешних эссе имеют наиболее убедительный и ценный философский вклад, если каждому дать три нейтральных и два судейских отзыва? Выбрать восемь основных и два перспективных, сохранить все причины и подготовить чтение без оценок.\n')
 qs=record(R,w,RUN,'question',str((D/'QUESTION_RU.txt').relative_to(R)),SID,proposal_cap['raw_event_ids'])
 end=w.append({'kind':'research.selection.ready','actor':{'id':SID,'role':'AI'},'session_id':SID,'run_id':RUN,'operation_id':RUN,'attempt_id':'preparation-v1','parents':[ev['id'],qs['id']]+[x['assigned_event'] for x in mapping.values()],'bindings':st['bindings'],'outputs':[w.put((D/'LINEAGE_INPUTS.json').read_bytes())],'payload':{'status':'SELECTION_INPUTS_ARCHIVED','individual_reviews':110,'pair_review_ceiling':50}},RUN+':ready:v1')
 save('START_RECEIPT.json',{'status':'SELECTION_INPUTS_ARCHIVED','event_id':end['id'],'input_event_id':ev['id'],'run_start_event':st['id'],'bindings':st['bindings'],'files':files,'capture_events':[x['coverage_event_id'] for x in caps],'question_stage_event':qs['id']})
 print(json.dumps({'status':'SELECTION_INPUTS_ARCHIVED','event_id':end['id']}),flush=True)
