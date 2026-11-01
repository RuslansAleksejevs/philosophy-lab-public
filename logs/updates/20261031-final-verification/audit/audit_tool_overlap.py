"""Compare exported tools to the original fixed recovery snapshots; no new cut."""
from pathlib import Path
import collections, hashlib, json, sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];sys.path.insert(0,str(ROOT/'scripts'))
from codex_rollout import rollout_file
from capture_codex import strict_json
from collector_source import project_record,UNKNOWN_MODEL
def sha(raw):return hashlib.sha256(raw).hexdigest()
def load(path):return strict_json(path.read_bytes())
def main():
 out=HERE/'TOOL_PENDING_EXPORT_OVERLAP.json'
 if out.exists():raise ValueError('Preserve prior overlap audit')
 tools=load(HERE/'REVIEWED_CODEX_TOOL_FRAGMENTS.json')['records'];sessions={x['session_id']:x for x in load(HERE/'DISCOVERY.json')};cutoffs={x['session_id']:x for x in load(HERE/'recovery/SESSIONS.json')}
 targets=collections.defaultdict(dict);result=[];prefixes=[]
 for row in tools:targets[row['session_id']][row['source_line']]=row
 for sid,wanted in sorted(targets.items()):
  if sid not in cutoffs:
   result.extend({'session_id':sid,'source_line':line,'source_record_sha256':r['source_record_sha256'],'disposition':'OUTSIDE_ORIGINAL_RECOVERY_SCOPE'} for line,r in wanted.items());continue
  session=sessions[sid];cut=cutoffs[sid];assert session['session_kind']!='internal_runtime'
  total=cut['source_bytes_at_cutoff'];used=0;line=0;digest=hashlib.sha256();found=set()
  with rollout_file(Path(session['source_path'])) as source:
   while used<total:
    raw=source.readline(min(8*1024*1024+1,total-used));assert raw;line+=1;used+=len(raw);digest.update(raw);record_hash=hashlib.sha256(raw);length=len(raw)
    oversized=len(raw)>8*1024*1024 or not raw.endswith(b'\n')
    if oversized:
     tail=raw
     while not tail.endswith(b'\n') and used<total:
      tail=source.readline(min(1024*1024,total-used));assert tail;used+=len(tail);digest.update(tail);record_hash.update(tail);length+=len(tail)
    if line not in wanted:continue
    row=wanted[line];found.add(line);entry={'session_id':sid,'source_line':line,'source_record_sha256':row['source_record_sha256']}
    if record_hash.hexdigest()!=row['source_record_sha256']:entry['disposition']='EXPORTED_RECORD_DIFFERS_FROM_NATIVE_PREFIX'
    elif oversized:entry['disposition']='EXACT_EXPORTED_TOOL_BUT_RECOVERY_SIZE_GAP'
    else:
     projection=project_record(strict_json(raw),line,sid,None,UNKNOWN_MODEL)
     entry['projection_kind']=projection['kind'];entry['disposition']='EXACT_EXPORTED_TOOL_INCLUDED_IN_GENERIC_PENDING' if projection['kind']=='tool_pending' else 'EXACT_EXPORTED_TOOL_NOT_GENERIC_PENDING'
    result.append(entry)
   source.verify_unchanged()
  assert digest.hexdigest()==cut['source_prefix_sha256'],'Original frozen native prefix changed'
  prefixes.append({'session_id':sid,'bytes':total,'sha256':digest.hexdigest(),'verified':True})
  for line,row in wanted.items():
   if line not in found:result.append({'session_id':sid,'source_line':line,'source_record_sha256':row['source_record_sha256'],'disposition':'AFTER_ORIGINAL_RECOVERY_CUTOFF'})
 counts=dict(collections.Counter(x['disposition'] for x in result));generic=load(HERE/'recovery/SUMMARY.json')['counts']['tool_pending'];overlap=counts.get('EXACT_EXPORTED_TOOL_INCLUDED_IN_GENERIC_PENDING',0)
 report={'status':'PASS_BOUNDED_TOOL_EXPORT_OVERLAP','generic_native_tool_pending_count':generic,'exported_reviewed_tool_fragments':len(tools),'exact_overlap':overlap,
  'generic_pending_without_this_supplement_identity':generic-overlap,'dispositions':counts,'verified_original_source_prefixes':prefixes,'records':result,
  'boundary':'Generic project_record classification uses an empty reviewed set and includes manually reviewed/exported records. The difference excludes only this1938-record supplement and is not a verified count of missing GitHub records; older bundles may contain additional copies. Existing fixed cutoffs only; no final delta, new cutoff, canonical write or tool body export.'}
 with out.open('x') as stream:json.dump(report,stream,ensure_ascii=False,indent=2);stream.write('\n')
 print(json.dumps({k:report[k] for k in ('status','generic_native_tool_pending_count','exported_reviewed_tool_fragments','exact_overlap','generic_pending_without_this_supplement_identity','dispositions')}))
if __name__=='__main__':main()
