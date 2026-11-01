"""Build the current 22-candidate register from reviewed coordinator decisions."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,copy
D=Path(__file__).resolve().parent;R=D.parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
def dump(p,x):
 with p.open('x') as f:json.dump(x,f,ensure_ascii=False,indent=2);f.write('\n')
old=json.loads((D/'BASELINE_DECISIONS.json').read_text());method=json.loads((D/'METHOD.json').read_text());targets=method['eight_in_order']+method['seven_current_reviews']
new=copy.deepcopy(old);changed=[];role_summary=[];seen_sessions=set()
summary_overrides={x['candidate']:x for x in json.loads((D/'CURRENT_SUMMARY_OVERRIDES.json').read_text())['candidates']}
for row in json.loads((D/'PROTECTED_VERSIONS.json').read_text())['files']:
 assert sha((R/row['path']).read_bytes())==row['sha256'],row['path']
for c in new['candidates']:
 cid=c['id'];c['prior_decision_before_this_goal']=c['decision']
 if cid not in targets:
  c['this_goal']={'reopened':False,'reason':'No new task was assigned to this essay in this goal; prior selected version and rationale retained.'}
  continue
 d=json.loads((D/'decisions'/f'{cid}.json').read_text())
 assert d['candidate']==cid and d['decision'] in ['keep','defer']
 assert len(d['why']) in [2,3] and all(isinstance(x,str) and x.strip() for x in d['why'])
 assert all(d.get(k) for k in ['selected_path','problem','action','next_action','review_scope'])
 p=R/d['selected_path'];b=p.read_bytes();selected_sha=sha(b)
 existing=next((v for v in c['versions'] if v['path']==d['selected_path']),None)
 for v in c['versions']:v['current']=False
 if existing:existing['current']=True;assert existing['sha256']==selected_sha
 else:
  c['versions'].append({'variant':'preselection-20261017-v1','path':d['selected_path'],'sha256':selected_sha,'bytes':len(b),'current':True,'actual_title':next((x.lstrip('# ').strip() for x in b.decode().splitlines() if x.startswith('# ')),c['title'])})
 roles=[]
 for lane in sorted((D/'roles'/cid).iterdir()):
  if not lane.is_dir() or not (lane/'DISPATCH.json').exists():continue
  receipt=json.loads((lane/'ARCHIVE_RECEIPT.json').read_text());assert receipt['status']=='ROLE_ARCHIVED'
  assert receipt['session_id'] not in seen_sessions,'Research roles must use separate sessions'
  seen_sessions.add(receipt['session_id'])
  for f in receipt['files']:assert sha((R/f['path']).read_bytes())==f['sha256'],f['path']
  roles.append({'role':lane.name,'session_id':receipt['session_id'],'receipt':str((lane/'ARCHIVE_RECEIPT.json').relative_to(R)),'event_id':receipt['event_id'],'lineage_entry_id':receipt['lineage_entry_id']})
  role_summary.append({'candidate':cid,**roles[-1]})
  report=lane/'output'/('REPORT_RU.txt' if lane.name.startswith('author') else 'REVIEW_RU.txt')
  c['evidence'].append({'path':str(report.relative_to(R)),'sha256':sha(report.read_bytes())})
 assert sum(r['role'].startswith('author') for r in roles)<=1
 if not existing:
  final=D/'roles'/cid/'review-final';assert (final/'ARCHIVE_RECEIPT.json').exists()
  assert sha((final/'input/manuscript.md').read_bytes())==selected_sha,'Selected revision differs from independently checked manuscript'
 c.update({k:d[k] for k in ['decision','action','problem','why','next_action']})
 if cid in summary_overrides:
  summary=summary_overrides[cid]
  if summary['manuscript']==d['selected_path']:
   assert summary['manuscript_sha256']==selected_sha
   c['prior_candidate_summary']=c['idea'];c['idea']=summary['idea']
   c['summary_update_evidence']=str((D/'CURRENT_SUMMARY_OVERRIDES.json').relative_to(R))
 c['issue_type']=d.get('issue_type','Bounded preselection task completed; comparative rank and historical novelty not established.')
 c['this_goal']={'reopened':True,'roles':roles,'review_scope':d['review_scope'],'coordinator_decision':str((D/'decisions'/f'{cid}.json').relative_to(R)),'disagreement':d.get('disagreement'),'limitations':d.get('limitations',[])}
 changed.append(cid)
assert len(changed)==15 and len(new['candidates'])==22 and sum(sum(v['current'] for v in c['versions']) for c in new['candidates'])==22
resolution_reports=[]
for cid in method['eight_in_order']:
 p=D/'roles'/cid/'author/output/DECISION.json'
 a=json.loads(p.read_text())
 resolution_reports.append({'candidate':cid,'author_reported_original_problem_resolved':a.get('original_problem_resolved','not_reported'),'source':str(p.relative_to(R)),'interpretation':'An author assessment, separate from the coordinator version decision; finite work completion does not establish complete resolution of every original question.'})
new['original_question_resolution_reports']=resolution_reports
partial=[x['candidate'] for x in resolution_reports if x['author_reported_original_problem_resolved'] in (False,'unknown')]
new['authors_reporting_partial_or_uncertain_resolution']=partial
new.update({'schema':'final-preselection-register.v1','run_id':D.name,'supersedes_for_current_navigation':'runs/final-selection-e036-20261017/DECISIONS.json','candidate_count':22,'counts':{key:sum(c['decision']==key for c in new['candidates']) for key in ['keep','revise','defer']},'changed_decisions':changed,'manuscript_edits':any((D/'roles'/c/'author/output/revision.md').exists() or (D/'roles'/c/'author-repair/output/revision.md').exists() for c in targets),'step2_started':True,'step2_completed':True,'remaining_preliminary_candidates':[],'reading_boundary':'Fresh agents read and assessed their own whole manuscripts; coordinator integrated reports, source checks, and selected manuscript passages/differences. Seven unassigned lines retain prior evidence. No comparative tournament or ten-selection.','correction':'This register supersedes prior navigation; old decisions, versions, failed attempts and dissent remain unchanged.','final_selection_started':False,'completed_at':datetime.now(timezone.utc).isoformat()})
new.pop('changes_this_step',None)
if 'editorial_corrections' in new:new['inherited_editorial_history']=new.pop('editorial_corrections')
dump(D/'DECISIONS.json',new)
dump(D/'ROLE_SUMMARY.json',{'roles':role_summary,'count':len(role_summary),'targets':targets})
keep=new['counts']['keep'];defer=new['counts']['defer']
lines=['# 22 кандидата после подготовки к отбору','',f'**Берём в дальнейшее сравнение: {keep}. Пока откладываем: {defer}. Десятка не выбиралась.**','',
'«Берём в сравнение» означает, что в этой конечной проверке не осталось обязательного исправления, мешающего следующему шагу. Это не признание новизны и не место в десятке. «Пока откладываем» означает, что указанная серьёзная проблема осталась после разрешённой попытки; текст и вся история сохранены.','',
'Разобраны восемь заданных старых кандидатов и отдельно проверены семь новых. По остальным семи сохранены прежние решения; новых проверок этих семи здесь не было.','',
('Исходный вопрос остался решён лишь частично или не вполне определённо у '+', '.join(partial)+'. Конкретные ограничения и причины выбора версии указаны ниже.' if partial else 'Оставшиеся вопросы и границы выводов указаны в каждой строке.'),'',
'| Эссе и ситуация | Что выяснили и что осталось | Решение и конкретная причина |','|---|---|---|']
for c in new['candidates']:
 v=next(v for v in c['versions'] if v['current']);label='правка 17.10.2026' if v['variant']=='preselection-20261017-v1' else v['variant']
 link=f'[{label}](<{R/v["path"]}>)'
 why=' '.join(c['why'])
 if c['id']=='E036':
  # Readable three-sentence condensation only; the inherited rationale remains
  # verbatim in DECISIONS.json, with no new assessment or changed version.
  why='R1 выводит шансы из обоснованного правила распределения, тогда как исходник недостаточно объясняет, почему право не показывать дневник должно сохранять прежний шанс. Она также разбирает возврат несправедливо исключённого участника: шансы остальных законно уменьшаются, но всю стипендию вернувшийся не получает. Поэтому сохраняем ранее выбранную R1; её более узкий вывод уже защищён.'
 status='Берём в сравнение' if c['decision']=='keep' else 'Пока откладываем'
 review_label='Новая проверка.' if c['this_goal']['reopened'] else 'Прежнее решение сохранено.'
 fields=[f'**{c["id"]} · {c["title"]}**<br>{c["idea"]}<br>{link}<br>{review_label}',c['problem'],f'**{status}.** {why}']
 lines.append('| '+' | '.join(x.replace('|','\\|').replace('\n','<br>') for x in fields)+' |')
lines+=['','Точные пути, хеши, сохранённые альтернативы и ссылки на отзывы — в [DECISIONS.json](<'+str(D/'DECISIONS.json')+'>).','Следующий отдельный этап — сравнение для выбора десяти. В этом запуске оно не проводилось.','']
with (D/'22_CANDIDATES_RU.md').open('x') as f:f.write('\n'.join(lines))
print(json.dumps({'counts':new['counts'],'completed_candidates':len(changed),'archived_roles':len(role_summary),'current_versions':22},ensure_ascii=False))
