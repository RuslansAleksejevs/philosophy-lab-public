"""Resume input acceptance after the preserved unsupported assistant-envelope gap.
No research/model call. The original bootstrap and manifest remain unchanged.
"""
from pathlib import Path
from datetime import datetime, timezone
import sys,json,hashlib,os
D=Path(__file__).resolve().parent;R=D.parents[1]
sys.path.insert(0,str(R/'scripts'));sys.path.insert(0,str(D))
from research_archive import Archive
from essay_lineage import base_entry,index,append as append_lineage
from archive_reviews import freeze_visible_fragments,BOUNDARY
RUN=D.name;auth=json.loads((D/'AUTHORIZATION.json').read_text());SID=auth['session_id']
def sha(b):return hashlib.sha256(b).hexdigest()
def save(name,v):
 with (D/name).open('x') as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
assert not (D/'START_RECEIPT.json').exists()
old=json.loads((D/'INPUT_MANIFEST.json').read_text())['files']
for x in old:assert sha((R/x['path']).read_bytes())==x['sha256'],x['path']
for x in json.loads((D/'PROTECTED_VERSIONS.json').read_text())['files']:assert sha((R/x['path']).read_bytes())==x['sha256']
selections=[{'line':x['source_line'],'role':x['role'],'phase':'final_answer' if x['role']=='assistant' else None,'text':x['text'],'record_sha256':x['source_line_sha256']} for x in auth['decision_history']]
fragments=freeze_visible_fragments(SID,R,selections,D/'authorization-fragments')
addon={'status':'RECOVERY_BEFORE_ANY_RESEARCH_DISPATCH','failure':{'standard_adapter_event':'event-d4c48cda910d4a33abec60420637be53','source_line':4872,'reason':'unknown_payload_fields','status':'INCOMPLETE'},'method':BOUNDARY,'scope':'Exact independently checked visible text tokens of the current human authorization, 60/40 role correction and accepted AI proposal. No model call, manuscript/rubric change or generated-result rerun. All original bootstrap artifacts and failed standard capture remain.','stages':'Use distinct research.selection.stage events for the five substantive stages. Existing philosophy-round adapter requires whole accepted native message records and cannot represent this fragment capture. Its administrative checkpoint will retain INCOMPLETE; final finite acceptance is a dedicated receipt, not an assertion that old gaps disappeared.'}
save('CAPTURE_RECOVERY_ADDENDUM.json',addon)
additional=[D/'INPUT_MANIFEST.json',D/'archive_start_recovery.py',D/'archive_reviews.py',D/'CAPTURE_METHOD.md',D/'test_archive_reviews.py',D/'ARCHIVE_TESTS.json',D/'CAPTURE_RECOVERY_ADDENDUM.json']+list((D/'authorization-fragments').glob('*'))
files=list(old)
for p in additional:
 assert p.is_file(),p
 row={'path':str(p.relative_to(R)),'sha256':sha(p.read_bytes()),'bytes':p.stat().st_size}
 if not any(x['path']==row['path'] for x in files):files.append(row)
save('RECOVERY_INPUT_MANIFEST.json',{'files':files,'frozen_at':datetime.now(timezone.utc).isoformat()})
print('Exact visible authorization preserved; auditing canonical archive.',flush=True)
with Archive(R/'research/archive').writer() as w:
 events={e['id']:e for e in w.events()}
 starts=[e for e in events.values() if e['run_id']==RUN and e['kind']=='operation.started' and e['payload'].get('protocol')=='philosophy-round.v1'];assert len(starts)==1
 st=starts[0];gap=events[addon['failure']['standard_adapter_event']];assert gap['kind']=='capture.coverage' and gap['payload']['status']=='INCOMPLETE'
 for x in files:assert w.put((R/x['path']).read_bytes())==x['sha256']
 for x in json.loads((D/'PROTECTED_VERSIONS.json').read_text())['files']:assert w.put((R/x['path']).read_bytes())==x['sha256']
 amendment=w.append({'kind':'research.selection.capture_method.accepted','actor':{'id':SID,'role':'AI'},'session_id':SID,'run_id':RUN,'operation_id':RUN,'attempt_id':'capture-recovery-v1','parents':[st['id'],gap['id']],'bindings':st['bindings'],'outputs':[w.put((D/'CAPTURE_RECOVERY_ADDENDUM.json').read_bytes()),w.put((D/'CAPTURE_METHOD.md').read_bytes())],'payload':addon},RUN+':capture-recovery-v1')
 evidence=[]
 for row in fragments['records']:
  ev=w.append({'kind':'research.selection.visible_fragment.captured','actor':{'id':'selection-capture','role':'tool'},'session_id':SID,'run_id':RUN,'operation_id':RUN+':authorization:'+str(row['source_line']),'attempt_id':'visible-fragment-v1','parents':[amendment['id']],'bindings':st['bindings'],'outputs':[x['sha256'] for x in row['parts']],'payload':{**row,'boundary':BOUNDARY,'full_provider_capture':False}},RUN+':authorization-fragment:'+str(row['source_line']))
  evidence.append(ev['id'])
 ev=w.append({'kind':'research.selection.inputs.accepted','actor':{'id':SID,'role':'AI'},'session_id':SID,'run_id':RUN,'operation_id':RUN,'attempt_id':'preparation-recovered-v1','parents':[st['id'],amendment['id']]+evidence,'bindings':st['bindings'],'outputs':[x['sha256'] for x in files]+[w.put((D/'RECOVERY_INPUT_MANIFEST.json').read_bytes())],'payload':{'status':'SELECTION_INPUTS_ARCHIVED','files':files,'reviews':110,'additional_ceiling':50,'ratio':'60/40','boundary':BOUNDARY}},RUN+':inputs:v1')
 print('Inputs accepted; linking exact candidate versions.',flush=True)
 events[ev['id']]=ev;known=index(events.values());mapping={}
 baseline=json.loads((D/'BASELINE_DECISIONS.json').read_text());allocation=json.loads((D/'ALLOCATION.json').read_text())['rows'];config=json.loads((D/'CONFIGURATION.json').read_text())
 for c in baseline['candidates']:
  v=next(x for x in c['versions'] if x['current']);matches=[e for e in known.values() if any(a.get('sha256')==v['sha256'] for a in e['payload']['entry']['artifacts'])];assert matches,('No existing lineage',c['id'])
  direct=[e for e in matches if e['payload']['entry']['kind'] in ['origin','draft','revision','final']];previous=(direct or matches)[-1];origin=previous['payload']['entry'];row=next(x for x in allocation if x['candidate']==c['id'])
  le=base_entry(RUN+':'+c['id']+':assigned',origin['entity'],'selection','Текущая версия включена в сравнение 22 → 10; три нейтральных и два судейских свежих отзыва. Результата ещё нет.')
  le.update(parents=[origin['id']],artifacts=[{'path':v['path'],'sha256':v['sha256'],'role':'frozen-candidate'},{'path':str((D/'ALLOCATION.json').relative_to(R)),'sha256':w.put((D/'ALLOCATION.json').read_bytes()),'role':'frozen-review-allocation'}],evidence=[ev['id']],occurred_at=datetime.now(timezone.utc).isoformat(),actor='AI coordinator',configuration={'requested':config['requested_for_all_reviewers'],'observed':{'parent':config['observed_parent'],'workers':'not dispatched'}},workflow=RUN,decision={'action':'admit to comparison','selected_for_ten':False,'blind_id':row['blind_id']},gaps=['No philosophical verdict at input acceptance.'])
  lev=append_lineage(w,le,SID,known,events);known[le['id']]=lev;events[lev['id']]=lev
  mapping[c['id']]={'entity':origin['entity'],'parent_entry':origin['id'],'assigned_entry':le['id'],'assigned_event':lev['id'],'blind_id':row['blind_id'],'version':v}
 save('LINEAGE_INPUTS.json',mapping)
 question='Какие десять из 22 нынешних эссе имеют наиболее убедительный и ценный философский вклад, если каждому дать три нейтральных и два судейских отзыва? Выбрать восемь основных и два перспективных, сохранить все причины и подготовить чтение без оценок.\n'
 with (D/'QUESTION_RU.txt').open('x') as f:f.write(question)
 qs=w.append({'kind':'research.selection.stage','actor':{'id':SID,'role':'AI'},'session_id':SID,'run_id':RUN,'operation_id':RUN,'attempt_id':'bounded-stages-v1','parents':[ev['id'],evidence[1]],'bindings':st['bindings'],'outputs':[w.put(question.encode())],'payload':{'stage':'question','contribution_origin':'AI','evidence_status':'EXACT_VISIBLE_FRAGMENT_LINKED','boundary':BOUNDARY}},RUN+':bounded-stage:question')
 end=w.append({'kind':'research.selection.ready','actor':{'id':SID,'role':'AI'},'session_id':SID,'run_id':RUN,'operation_id':RUN,'attempt_id':'preparation-recovered-v1','parents':[ev['id'],qs['id']]+[x['assigned_event'] for x in mapping.values()],'bindings':st['bindings'],'outputs':[w.put((D/'LINEAGE_INPUTS.json').read_bytes())],'payload':{'status':'SELECTION_INPUTS_ARCHIVED','individual_reviews':110,'pair_review_ceiling':50,'capture_boundary':BOUNDARY}},RUN+':ready:v1')
 save('START_RECEIPT.json',{'status':'SELECTION_INPUTS_ARCHIVED','event_id':end['id'],'input_event_id':ev['id'],'run_start_event':st['id'],'bindings':st['bindings'],'files':files,'capture_events':evidence,'capture_amendment_event':amendment['id'],'preserved_standard_capture_gap':gap['id'],'question_stage_event':qs['id']})
 print(json.dumps({'status':'SELECTION_INPUTS_ARCHIVED','event_id':end['id']}),flush=True)
