"""Append accepted finite-role files, bounded visible records and lineages.
The batch plan is prepared and reviewed by the coordinator; no provider calls.
"""
from pathlib import Path
from datetime import datetime,timezone
import sys,json,hashlib,re,os
D=Path(__file__).resolve().parent;R=D.parents[1];sys.path.insert(0,str(R/'scripts'))
from research_archive import Archive
from capture_codex import resolve_session
from essay_lineage import base_entry,index,append as append_lineage
RUN=D.name;SID='01a1496a-7b42-7a11-b00a-11d33df80222'
def sha(b):return hashlib.sha256(b).hexdigest()
def save(p,x):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x') as f:json.dump(x,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
planpath=Path(sys.argv[1]).resolve();assert planpath.is_relative_to(D)
plan=json.loads(planpath.read_text());batch=plan['batch_id'];receipt=D/'batches'/f'{batch}.receipt.json';assert not receipt.exists()
start=json.loads((D/'START_RECEIPT.json').read_text());mapping=json.loads((D/'LINEAGE_INPUTS.json').read_text())
protected=json.loads((D/'PROTECTED_VERSIONS.json').read_text())['files']
for x in protected:assert sha((R/x['path']).read_bytes())==x['sha256'],x['path']
roles=[]
for item in plan.get('roles',[]):
 cid=item['candidate'];role=item['role'];lane=D/'roles'/cid/role;dispatch=json.loads((lane/'DISPATCH.json').read_text());sid=dispatch['session_id']
 assert not (lane/'ARCHIVE_RECEIPT.json').exists()
 assert sha((lane/'PROMPT.txt').read_bytes())==dispatch['prompt_sha256']
 outputs=sorted(p for p in (lane/'output').rglob('*') if p.is_file() and '__pycache__' not in p.parts)
 required=['REPORT_RU.txt','DECISION.json','SOURCES.json'] if role=='author' else ['REVIEW_RU.txt','REVIEW.json','SOURCES.json']
 if role.startswith('author'):required=['REPORT_RU.txt','DECISION.json','SOURCES.json']
 for name in required:assert (lane/'output'/name).is_file(),(cid,role,name)
 for p in outputs:
  assert not p.is_symlink();assert p.stat().st_size<25*1024*1024
 for p in outputs:
  if p.suffix=='.json':json.loads(p.read_text())
 source=resolve_session(sid,R);raws=source.read_bytes().splitlines(keepends=True);observed=[];selected=[]
 capture_dir=lane/('capture-'+str(len(list(lane.glob('capture*')))+1).zfill(3));capture_dir.mkdir()
 prompt_seen=False;final_seen=False
 for n,raw in enumerate(raws,1):
  try:e=json.loads(raw)
  except ValueError:continue
  q=e.get('payload',{})
  if e.get('type')=='turn_context':
   allowed={k:q[k] for k in ['model','effort','reasoning_effort','service_tier'] if k in q}
   if allowed:observed.append({'source_line':n,'timestamp':e.get('timestamp'),'fields':allowed})
  if e.get('type')!='response_item' or q.get('type')!='message':continue
  actual_prompt=q.get('role')=='user' and any(c.get('text')==dispatch['message'] for c in q.get('content',[]) if isinstance(c,dict))
  visible=q.get('role')=='assistant' and q.get('phase') in ['commentary','final','final_answer']
  if not(actual_prompt or visible):continue
  texts=[c['text'] for c in q.get('content',[]) if c.get('type') in ['output_text','input_text','text'] and 'text' in c]
  if actual_prompt:prompt_seen=True;texts=[dispatch['message']]
  if visible and q.get('phase') in ['final','final_answer'] and any('PHILOSOPHY_ROLE_COMPLETE' in t for t in texts):final_seen=True
  tokens=[m.group(1) for m in re.finditer(rb'"text"\s*:\s*("(?:\\.|[^"\\])*")',raw)]
  entries=[]
  for j,t in enumerate(texts):
   token=next(x for x in tokens if json.loads(x)==t);p=capture_dir/f'line-{n}-part-{j}.json-string.txt'
   with p.open('xb') as f:f.write(token)
   entries.append({'path':str(p.relative_to(R)),'sha256':sha(token)})
  selected.append({'source_line':n,'source_line_sha256':sha(raw),'timestamp':e.get('timestamp'),'role':q['role'],'phase':q.get('phase'),'parts':entries})
 parent_source=resolve_session(SID,R);launch=None
 for n,raw in enumerate(parent_source.read_bytes().splitlines(keepends=True),1):
  try:e=json.loads(raw)
  except ValueError:continue
  q=e.get('payload',{})
  if e.get('type')!='response_item' or q.get('type')!='function_call' or q.get('name')!='spawn_agent':continue
  args=q.get('arguments','')
  try:a=json.loads(args)
  except (ValueError,TypeError):continue
  if a.get('task_name')!=dispatch['agent_task'].split('/')[-1]:continue
  assert set(a)<={'task_name','fork_turns','message','model','reasoning_effort'} and a.get('fork_turns')=='none'
  # Native inter-agent task bodies are opaque/encrypted. Never copy them.
  launch={'parent_session':SID,'source_line':n,'source_line_sha256':sha(raw),'timestamp':e.get('timestamp'),'call_id':q.get('call_id'),'task_name':a['task_name'],'fork_turns':a.get('fork_turns'),'model_override':a.get('model'),'reasoning_effort_override':a.get('reasoning_effort'),'message_body_capture':'EXCLUDED_OPAQUE_NATIVE_AGENT_FIELD','plaintext_task_record':'Coordinator-preserved visible tool-call text in DISPATCH.json plus frozen PROMPT.txt; not asserted to be native plaintext byte capture.'}
 assert launch,('Observed parent dispatch metadata not found',cid,role,sid)
 assert final_seen,('Worker completion not found',cid,role,sid)
 capture={'session_id':sid,'status':'BOUNDED_VISIBLE_FRAGMENTS_COMPLETE','observed_configuration':observed,'records':selected,'parent_dispatch':launch,'task_exposed_as_child_user_record':prompt_seen,'boundary':'Exact recognized child commentary/final text string bytes and selected parent dispatch metadata only. Native inter-agent task bodies are opaque/encrypted and excluded. Plain task text is retained separately from the coordinator visible call record and frozen packet, not claimed as native plaintext capture or proof of exact backend delivery. Unsupported full envelopes, injected instructions, reasoning, unreviewed tool bodies and future records excluded. Actual manuscript/source artifacts captured separately. No full provider trace or intellectual-independence proof.'}
 save(lane/'VISIBLE_CAPTURE.json',capture)
 roles.append((item,lane,dispatch,capture,outputs))
print('Role files and selected visible evidence verified; acquiring canonical archive.',flush=True)
with Archive(R/'research/archive').writer() as w:
 events={e['id']:e for e in w.events()};known=index(events.values());batch_events=[];results=[]
 for item,lane,dispatch,capture,outputs in roles:
  cid=item['candidate'];role=item['role'];sid=dispatch['session_id'];files=[]
  for p in sorted(p for p in lane.rglob('*') if p.is_file() and '__pycache__' not in p.parts):
   b=p.read_bytes();files.append({'path':str(p.relative_to(R)),'sha256':w.put(b),'bytes':len(b)})
  parent_entry=item.get('parent_entry',mapping[cid]['assigned_entry'])
  assert parent_entry in known
  ev=w.append({'kind':'research.preselection.role.completed','actor':{'id':sid,'role':'AI'},'session_id':sid,'run_id':RUN,'operation_id':RUN+':'+cid+':'+role,'attempt_id':'role-v1','parents':[start['ready_event'],known[parent_entry]['id']],'bindings':start['bindings'],'outputs':[f['sha256'] for f in files],'payload':{'candidate':cid,'role':role,'status':'ROLE_FILES_AND_VISIBLE_CAPTURE_ACCEPTED','files':files,'capture_boundary':capture['boundary'],'observed_configuration':capture['observed_configuration'],'decision':json.loads((lane/'output'/('DECISION.json' if role.startswith('author') else 'REVIEW.json')).read_text())}},RUN+':'+cid+':'+role+':completed-v1')
  events[ev['id']]=ev
  revised=role.startswith('author') and (lane/'output'/'revision.md').is_file()
  le=base_entry(RUN+':'+cid+':'+role+':v1',mapping[cid]['entity'],'revision' if revised else 'critique','Новая ограниченная работа по текущей версии: '+role+'. Точный вывод и ограничения сохранены в отчёте роли.')
  le['parents']=[parent_entry];le['artifacts']=[{'path':str(p.relative_to(R)),'sha256':w.put(p.read_bytes()),'role':'revised-manuscript' if p.name=='revision.md' else 'role-output'} for p in outputs]
  le['evidence']=[ev['id']];le['occurred_at']=capture['records'][-1]['timestamp'];le['actor']='Fresh Codex context '+sid;le['configuration']={'requested':'Inherited current model/effort, Standard, fresh single-essay context','observed':capture['observed_configuration']};le['workflow']=RUN;le['gaps']=[capture['boundary']]
  lev=append_lineage(w,le,sid,known,events);batch_events.extend([ev['id'],lev['id']])
  rec={'status':'ROLE_ARCHIVED','candidate':cid,'role':role,'session_id':sid,'event_id':ev['id'],'lineage_event_id':lev['id'],'lineage_entry_id':le['id'],'files':files,'capture_status':capture['status']}
  save(lane/'ARCHIVE_RECEIPT.json',rec);w.put((lane/'ARCHIVE_RECEIPT.json').read_bytes());results.append(rec)
 for item in plan.get('prepared_packets',[]):
  cid=item['candidate'];role=item['role'];lane=D/'roles'/cid/role;parent=item['parent_entry'];assert parent in known
  files=[]
  for p in sorted(p for p in lane.rglob('*') if p.is_file()):
   b=p.read_bytes();files.append({'path':str(p.relative_to(R)),'sha256':w.put(b),'bytes':len(b)})
  ev=w.append({'kind':'research.preselection.packet.prepared','actor':{'id':SID,'role':'AI'},'session_id':SID,'run_id':RUN,'operation_id':RUN+':'+cid+':'+role,'attempt_id':'packet-v1','parents':[known[parent]['id']],'outputs':[x['sha256'] for x in files],'payload':{'candidate':cid,'role':role,'parent_entry':parent,'files':files,'status':'READY_FOR_DISPATCH'}},RUN+':'+cid+':'+role+':packet-v1')
  save(lane/'PREPARED_RECEIPT.json',{'status':'READY_FOR_DISPATCH','event_id':ev['id'],'parent_entry':parent,'files':files});batch_events.append(ev['id'])
 end=w.append({'kind':'research.preselection.batch.accepted','actor':{'id':SID,'role':'AI'},'session_id':SID,'run_id':RUN,'operation_id':RUN,'attempt_id':batch,'parents':batch_events,'inputs':[w.put(planpath.read_bytes())],'outputs':[w.put((D/'roles'/x['candidate']/x['role']/'ARCHIVE_RECEIPT.json').read_bytes()) for x in results],'payload':{'batch_id':batch,'accepted_roles':[{'candidate':x['candidate'],'role':x['role']} for x in results],'prepared_packets':plan.get('prepared_packets',[]),'protected_versions_unchanged':True}},RUN+':batch:'+batch)
 save(receipt,{'status':'BATCH_ACCEPTED','event_id':end['id'],'roles':results,'prepared_packets':plan.get('prepared_packets',[])})
 print(json.dumps({'status':'BATCH_ACCEPTED','batch':batch,'roles':len(results),'event_id':end['id']}),flush=True)
