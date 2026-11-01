from pathlib import Path
import json,sys,hashlib,shutil
D=Path(__file__).resolve().parent;R=D.parents[1]
cid,role,parentrole=sys.argv[1:4];parent=D/'roles'/cid/parentrole;lane=D/'roles'/cid/role
assert role in ['author-repair','review-final'];assert not lane.exists()
ip=lane/'input';op=lane/'output';ip.mkdir(parents=True);op.mkdir()
def sha(b):return hashlib.sha256(b).hexdigest()
def save(p,x):
 with p.open('x') as f:json.dump(x,f,ensure_ascii=False,indent=2);f.write('\n')
baseline=json.loads((D/'BASELINE_DECISIONS.json').read_text());c=next(x for x in baseline['candidates'] if x['id']==cid);v=next(x for x in c['versions'] if x['current'])
if role=='review-final':
 source=parent/'output/revision.md' if (parent/'output/revision.md').exists() else R/v['path']
 (ip/'manuscript.md').write_bytes(source.read_bytes())
 work=(D/'REVIEW_CRITERIA.txt').read_text()
else:
 source=R/v['path'];(ip/'manuscript.md').write_bytes(source.read_bytes())
 for p in sorted((parent/'output').rglob('*')):
  if not p.is_file() or p.name in ['SESSION.json'] or p.suffix=='.py' or '__pycache__' in p.parts:continue
  target=ip/'review-evidence'/p.relative_to(parent/'output');target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(p.read_bytes())
 work='''Read the full current manuscript and the newly archived independent review. This is the only new revision cycle authorized for this essay. Evaluate objections charitably; do not assume the critic is always right. Make only justified changes, preserving every unaffected valid contribution. If revising, write a complete English revision.md, with bibliography, not a patch or fragment. If no revision is justified or no responsible repair is available, explain why. Consult targeted primary sources for disputed load-bearing attributions and save accessed excerpts with URL, access time, exact locator and limitations. Deliver REPORT_RU.txt (concrete issue, response to each criticism, changes or reasons to retain the text, costs/narrowing, remaining uncertainty), DECISION.json (revised boolean, proposed_version, change_summary, resolved_issues, remaining_issues), SOURCES.json, and source files actually used. Do not alter originals. A different fresh reviewer will check any new manuscript.\n'''+(D/'AUTHOR_CLEAR_PROSE.txt').read_text()
prompt=(D/'NEUTRAL_WORKER.txt').read_text()+'\n'+work+'\nYour entire input packet: '+str(ip)+'\nWrite outputs only here: '+str(op)+'\nDo not read the parent run register or another candidate. Your role identity is '+cid+'/'+role+'. Record your actual CODEX_THREAD_ID from the environment in output/SESSION.json; do not read native logs or account settings. On completion report files and the observed session ID. Begin the final response with PHILOSOPHY_ROLE_COMPLETE.\n'
(lane/'PROMPT.txt').write_text(prompt)
save(lane/'INPUTS.json',{'candidate':cid,'role':role,'parent_role':parentrole,'parent_entry':D.name+':'+cid+':'+parentrole+':v1','manuscript_source':str(source.relative_to(R)),'files':[{'path':str(p.relative_to(lane)),'sha256':sha(p.read_bytes())} for p in sorted(ip.rglob('*')) if p.is_file()]})
print(json.dumps({'candidate':cid,'role':role,'parent_entry':D.name+':'+cid+':'+parentrole+':v1'}))
