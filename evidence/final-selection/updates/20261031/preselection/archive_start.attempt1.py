from pathlib import Path
from datetime import datetime,timezone
import sys,json,hashlib,os,re
D=Path(__file__).resolve().parent;R=D.parents[1];sys.path.insert(0,str(R/'scripts'))
from research_archive import Archive
from capture_codex import capture,resolve_session
from philosophy_round import start
from essay_lineage import base_entry,index,append as append_lineage
RUN=D.name;auth=json.loads((D/'AUTHORIZATION.json').read_text());SID=auth['session_id']
def sha(b):return hashlib.sha256(b).hexdigest()
def save(name,x):
 with (D/name).open('x') as f:json.dump(x,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
assert not (D/'START_RECEIPT.json').exists()
manifest=json.loads((D/'INPUT_MANIFEST.json').read_text())
for row in manifest['files']+manifest['protected_versions']:assert sha((R/row['path']).read_bytes())==row['sha256'],row['path']
source=resolve_session(SID,R);raws=source.read_bytes().splitlines(keepends=True)
assert sha(raws[auth['request']['source_line']-1])==auth['request']['source_line_sha256']
proposal=None
for n,raw in enumerate(raws[:auth['request']['source_line']-1],1):
 try:e=json.loads(raw)
 except ValueError:continue
 p=e.get('payload',{})
 if e.get('type')=='response_item' and p.get('role')=='assistant' and p.get('phase')=='final':
  t=''.join(c.get('text','') for c in p.get('content',[]) if c.get('type')=='output_text')
  if 'Подготовить 22 кандидата' in t or 'подготовить 22 кандидата' in t:
   proposal={'source_line':n,'source_line_sha256':sha(raw),'timestamp':e.get('timestamp'),'text':t}
assert proposal,'Accepted goal proposal must be recoverable'
save('ACCEPTED_PROPOSAL_VISIBLE.json',proposal)
print('Frozen packets verified; acquiring canonical archive.',flush=True)
with Archive(R/'research/archive').writer() as w:
 st=start(R,w,RUN,SID,'technical',str((D/'METHOD.json').relative_to(R)),[str((D/f).relative_to(R)) for f in ['AUTHORIZATION.json','USER_REQUEST.txt','ACCEPTED_PROPOSAL_VISIBLE.json','INPUT_MANIFEST.json','BASELINE_DECISIONS.json']],stage_id='PRESELECTION_PREPARATION',selection_round_id='22_TO_10_PREPARATION')
 print('Round start saved; capturing the exact launch request.',flush=True)
 line=auth['request']['source_line'];cap=capture(R/'research/archive',source,SID,R,start_line=line,end_line=line,run_id=RUN,archive_writer=w)
 assert cap['status']=='BOUNDED_COMPLETE',cap
 save('CAPTURE_START.json',cap)
 files=[]
 for p in sorted(D.rglob('*')):
  if p.is_file() and '__pycache__' not in p.parts:
   b=p.read_bytes();files.append({'path':str(p.relative_to(R)),'sha256':w.put(b),'bytes':len(b)})
 for row in manifest['protected_versions']:assert w.put((R/row['path']).read_bytes())==row['sha256']
 ev=w.append({'kind':'research.preselection.prepared','actor':{'id':SID,'role':'AI'},'session_id':SID,'run_id':RUN,'operation_id':RUN,'attempt_id':'preparation-v1','parents':[st['id'],cap['coverage_event_id']]+cap['raw_event_ids'],'bindings':st['bindings'],'outputs':[f['sha256'] for f in files],'payload':{'status':'AUTHORIZED_PACKETS_FROZEN','files':files,'scope':'Eight targeted tasks and seven independent current-version checks, at most one revision cycle per essay; stop before selecting ten.','capture_boundary':'Exact current human request plus selected safe proposal text and immutable input files. Old collector gaps remain. No full native log copied.'}},RUN+':prepared:v1')
 events={e['id']:e for e in w.events()};known=index(events.values());baseline=json.loads((D/'BASELINE_DECISIONS.json').read_text());mapping={}
 for c in baseline['candidates']:
  v=next(v for v in c['versions'] if v['current'])
  matches=[e for e in known.values() if any(a.get('path')==v['path'] and a.get('sha256')==v['sha256'] for a in e['payload']['entry']['artifacts'])]
  if not matches:
   matches=[e for e in known.values() if any(a.get('sha256')==v['sha256'] for a in e['payload']['entry']['artifacts'])]
  assert matches,('No known source lineage',c['id'],v['path'])
  # Prefer actual original/revision/final entries over later cross-essay assessments.
  direct=[e for e in matches if e['payload']['entry']['kind'] in ['origin','draft','revision','final']]
  selected=(direct or matches)[-1];old=selected['payload']['entry']
  mapping[c['id']]={'entity':old['entity'],'parent_entry':old['id'],'parent_event':selected['id'],'version':v,'all_matching_entries':[e['payload']['entry']['id'] for e in matches]}
  lanes=list((D/'roles'/c['id']).glob('*')) if (D/'roles'/c['id']).exists() else []
  if lanes:
   lane=lanes[0];le=base_entry(RUN+':'+c['id']+':assigned-v1',old['entity'],'selection','Назначена конечная проверка или одна попытка исправления текущей версии; сравнительный отбор не начат.')
   le['parents']=[old['id']];le['artifacts']=[{'path':v['path'],'sha256':v['sha256'],'role':'selected-input'},{'path':str((lane/'PROMPT.txt').relative_to(R)),'sha256':w.put((lane/'PROMPT.txt').read_bytes()),'role':'exact-role-prompt'}]
   le['evidence']=[ev['id'],cap['coverage_event_id']];le['occurred_at']=datetime.now(timezone.utc).isoformat();le['actor']='AI coordinator';le['configuration']={'requested':'Current Codex settings, fresh contexts, Standard service','observed':json.loads((D/'CONFIGURATION.json').read_text())};le['workflow']=RUN;le['decision']={'action':'Targeted author task' if lane.name=='author' else 'Independent current-version review','rank':None,'maximum_revision_cycles':1};le['gaps']=['Preparation selection is not a philosophical verdict.']
   levent=append_lineage(w,le,SID,known,events);known[le['id']]=levent;events[levent['id']]=levent;mapping[c['id']]['assigned_entry']=le['id'];mapping[c['id']]['assigned_event']=levent['id']
 save('LINEAGE_INPUTS.json',mapping)
 mhash=w.put((D/'LINEAGE_INPUTS.json').read_bytes())
 end=w.append({'kind':'research.preselection.ready','actor':{'id':SID,'role':'AI'},'session_id':SID,'run_id':RUN,'operation_id':RUN,'attempt_id':'preparation-v1','parents':[ev['id']]+[v['assigned_event'] for v in mapping.values() if 'assigned_event' in v],'outputs':[mhash],'payload':{'status':'READY_FOR_FINITE_DISPATCH','independent_initial_roles':15,'service_tier_configured':'default','current_request_capture':cap['status'],'whole_provider_capture':False}},RUN+':ready:v1')
 save('START_RECEIPT.json',{'status':'READY_FOR_FINITE_DISPATCH','run_start_event':st['id'],'prepared_event':ev['id'],'ready_event':end['id'],'capture_event':cap['coverage_event_id'],'bindings':st['bindings'],'files':files,'lineage_inputs_sha256':mhash})
 print(json.dumps({'status':'READY_FOR_FINITE_DISPATCH','event_id':end['id']}),flush=True)
