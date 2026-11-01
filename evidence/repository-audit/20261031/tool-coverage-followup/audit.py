"""Fixed81-prefix/37-bundle equality audit; hashes/metadata only, no new export."""
from pathlib import Path, PurePosixPath
import collections,hashlib,json,re,sys,tarfile
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];REPO=ROOT/'repository';PRIOR=HERE.parent/'history-audit/tool-coverage';OLD=HERE.parent/'log-audit'
sys.path.insert(0,str(ROOT/'scripts'))
from codex_rollout import rollout_file
from capture_codex import strict_json
from collector_source import project_record,UNKNOWN_MODEL
from collector_safety import contains_credential
UUID=re.compile(r'[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}\Z')
TYPES={'function_call','function_call_output','custom_tool_call','custom_tool_call_output'}
CORE=('type','name','namespace','call_id','arguments','input','output','status')
BODY={'text','arguments','input','output','content','body','stdout','stderr','response'}
SKIP={'reasoning','analysis','thinking','system','developer','system_prompt','developer_instructions','base_instructions','instructions'}
def require(v,m):
 if not v:raise ValueError(m)
def sha(b):return hashlib.sha256(b).hexdigest()
def encoded(v):return (json.dumps(v,ensure_ascii=False,indent=2,sort_keys=True,allow_nan=False)+'\n').encode()
def canonical(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def read(p):
 require(p.is_file() and not p.is_symlink(),'Missing/symlink audited input');return p.read_bytes()
def load(p):return strict_json(read(p))
def desc(p):
 b=read(p);return {'path':str(p.relative_to(ROOT)),'sha256':sha(b),'bytes':len(b)}
def bound(row):
 p=ROOT/row['path'];require(p.is_relative_to(ROOT) and '..' not in p.parts,'Outside audited input');b=read(p)
 require(len(b)==row['bytes'] and sha(b)==row['sha256'],'Frozen audited input changed');return b
def save(name,value):
 require(not contains_credential(value),'Credential-shaped diagnostic metadata');raw=encoded(value)
 with (HERE/name).open('xb') as f:f.write(raw)
 return desc(HERE/name)
def core(value):
 if isinstance(value,dict) and isinstance(value.get('type'),str) and value['type'] in TYPES and any(k in value for k in ('arguments','input','output')):
  return {k:value[k] for k in CORE if k in value}
def scope(value,inherited):
 for candidate in (value.get('session_id'),value.get('session',{}).get('session_id') if isinstance(value.get('session'),dict) else None,
                   value.get('metadata',{}).get('session_id') if isinstance(value.get('metadata'),dict) else None):
  if isinstance(candidate,str) and UUID.fullmatch(candidate):return candidate
 return inherited

class Matcher:
 def __init__(self,native,prior):
  self.native=native;self.prior=prior;self.tuples=collections.defaultdict(list);self.payloads=collections.defaultdict(set);self.strings=collections.defaultdict(set)
  for key,row in native.items():
   if row['call_id_sha256'] is not None:self.tuples[(row['session_id'],row['call_id_sha256'],row['tool_type'])].append(key)
   self.payloads[row['payload_core_sha256']].add(key)
   for item in row['string_bodies']:self.strings[(item['sha256'],item['bytes'])].add(key)
  self.exact=collections.defaultdict(list);self.ambiguous=collections.defaultdict(set);self.content={};self.stats=collections.Counter()
 def content_match(self,kind,digest,size,keys,location,sid,provider):
  if not keys:return
  group=self.content.setdefault((kind,digest,size),{'kind':kind,'sha256':digest,'bytes':size,'native_identities':set(keys),'occurrences':0,'locations':[],'sid_contexts':set(),'provider_contexts':set()})
  group['occurrences']+=1
  if len(group['locations'])<12:group['locations'].append(location)
  if sid:group['sid_contexts'].add(sid)
  group['provider_contexts'].add(provider or 'UNKNOWN')
 def text(self,value,location,sid=None,provider=None,kind='literal_string'):
  if not isinstance(value,str) or not value:return
  raw=value.encode();key=(sha(raw),len(raw));self.content_match(kind,key[0],key[1],self.strings.get(key,set()),location,sid,provider)
 def walk(self,value,location,sid=None,provider=None,pointer=''):
  if isinstance(value,list):
   for i,item in enumerate(value):self.walk(item,location,sid,provider,pointer+'/'+str(i))
   return
  if not isinstance(value,dict):return
  sid=scope(value,sid)
  session=value.get('session',{})
  if value.get('provider')=='claude' or isinstance(session,dict) and session.get('provider')=='claude':provider='claude'
  if value.get('role') in ('system','developer') or value.get('phase') in ('analysis','reasoning','thinking') or value.get('type') in ('reasoning','thinking'):
   self.stats['hidden_or_context_objects_skipped']+=1;return
  loc=dict(location,pointer=pointer)
  c=core(value)
  if c:
   self.stats['structured_tool_payloads']+=1;raw=canonical(c);digest=sha(raw);keys=self.payloads.get(digest,set())
   self.content_match('payload_core',digest,len(raw),keys,loc,sid,provider)
   if sid and provider!='claude' and isinstance(c.get('call_id'),str):
    candidates=self.tuples.get((sid,sha(c['call_id'].encode()),c['type']),[])
    matching=[k for k in candidates if self.native[k]['payload_core_sha256']==digest]
    if len(candidates)==len(matching)==1:self.exact[matching[0]].append(loc)
    elif matching:
     for k in matching:self.ambiguous[k].add(digest)
  for key,item in value.items():
   if key in SKIP:continue
   # Paths contain only field labels or a label hash, never arbitrary text keys.
   label=key if re.fullmatch(r'[A-Za-z0-9_-]{1,80}',key) and not contains_credential(key) else 'key-sha256-'+sha(key.encode())
   child=pointer+'/'+label
   if key in BODY and isinstance(item,str):self.text(item,dict(location,pointer=child),sid,provider)
   elif isinstance(item,(dict,list)):self.walk(item,location,sid,provider,child)

def native_records(prefixes,discovery,cuts):
 records={};verified=[];histogram=collections.Counter()
 for prefix in prefixes:
  sid=prefix['session_id'];cut=cuts[sid];source=discovery[sid]
  require(source.get('session_kind')!='internal_runtime','Internal runtime prohibited')
  require((prefix['bytes'],prefix['sha256'],prefix['lines'])==(cut['source_bytes_at_cutoff'],cut['source_prefix_sha256'],cut['source_line_cutoff']),'Previous cutoff mismatch')
  used=0;number=0;digest=hashlib.sha256();turn=None;model=UNKNOWN_MODEL;count=0
  with rollout_file(Path(source['source_path'])) as stream:
   while used<prefix['bytes']:
    raw=stream.readline(min(8*1024*1024+1,prefix['bytes']-used));require(raw,'Truncated frozen prefix');used+=len(raw);digest.update(raw);number+=1
    if len(raw)>8*1024*1024 or not raw.endswith(b'\n'):
     while raw and not raw.endswith(b'\n') and used<prefix['bytes']:
      raw=stream.readline(min(1024*1024,prefix['bytes']-used));require(raw,'Truncated long record');used+=len(raw);digest.update(raw)
     continue
    obj=strict_json(raw)
    if number==1:require(obj.get('type')=='session_meta' and obj['payload'].get('id')==sid and obj['payload'].get('cwd')==source['source_cwd'],'Native identity differs')
    projection=project_record(obj,number,sid,turn,model);turn,model=projection['next_turn'],projection['next_model']
    if projection['kind']!='tool_pending':continue
    count+=1;payload=obj['payload'];c=core(payload);require(c is not None,'Pending tool lacks a bounded payload core')
    key=(sid,number,sha(raw));strings=[]
    for field in ('arguments','input','output'):
     if isinstance(payload.get(field),str) and payload[field]:
      body=payload[field].encode();strings.append({'field':field,'sha256':sha(body),'bytes':len(body)})
    records[key]={'session_id':sid,'source_line':number,'source_record_sha256':key[2],'tool_type':payload['type'],'call_id_sha256':sha(payload['call_id'].encode()) if isinstance(payload.get('call_id'),str) else None,'payload_core_sha256':sha(canonical(c)),'string_bodies':strings}
    histogram[payload['type']]+=1
   stream.verify_unchanged()
  require(used==prefix['bytes'] and number==prefix['lines'] and digest.hexdigest()==prefix['sha256'],'Frozen prefix changed')
  require(count==cut['counts'].get('tool_pending',0),'Current classifier differs from frozen per-session pending count')
  verified.append(dict(prefix,tool_pending_records=count))
 return records,verified,dict(histogram)

def main():
 previous=load(PRIOR/'REPORT.json');audit=load(PRIOR/'BUNDLE_AND_INDEX_AUDIT.json');prefixes=load(PRIOR/'NATIVE_PREFIX_VERIFICATION.json');prior_rows=load(PRIOR/'EXACT_TOOL_IDENTITIES.json')
 require(len(prefixes)==81 and len(audit['bundles'])==37 and len(audit['loose_json_files'])==119,'Frozen scope differs')
 required={row['path']:row for row in previous['inputs']}
 discovery_path=str((OLD/'DISCOVERY.json').relative_to(ROOT));cut_path=str((OLD/'recovery/SESSIONS.json').relative_to(ROOT))
 discovery={x['session_id']:x for x in strict_json(bound(required[discovery_path]))};cuts={x['session_id']:x for x in strict_json(bound(required[cut_path]))}
 prior={(x['session_id'],x['source_line'],x['source_record_sha256']) for x in prior_rows};require(len(prior)==1938,'Prior exact count differs')
 frozen=[desc(p) for p in [Path(__file__),PRIOR/'REPORT.json',PRIOR/'BUNDLE_AND_INDEX_AUDIT.json',PRIOR/'NATIVE_PREFIX_VERIFICATION.json',PRIOR/'EXACT_TOOL_IDENTITIES.json',ROOT/'scripts/collector_source.py',ROOT/'scripts/capture_codex.py',ROOT/'scripts/codex_rollout.py']]
 native,verified,histogram=native_records(prefixes,discovery,cuts);require(prior<=set(native),'Earlier exact tool identity not in frozen pending set');matcher=Matcher(native,prior)
 central=strict_json(bound(required['repository/logs/bundles/manifest.json']));late=strict_json(bound(required['repository/logs/updates/20261031-late-receipts/MANIFEST.json']))
 specs={'repository/logs/'+x['path']:x for x in central['bundles']};specs['repository/'+late['bundle']['path']]=late['bundle']
 members=0
 for row in audit['bundles']:
  spec=specs[row['path']];require((row['sha256'],row['bytes'])==(spec['sha256'],spec['bytes']),'Bundle scope hash differs');bound(row)
  expected={x['path']:x for x in spec['members']};seen=set()
  with tarfile.open(ROOT/row['path'],'r:gz') as archive:
   for member in archive:
    name=member.name;require(member.isfile() and not PurePosixPath(name).is_absolute() and '..' not in PurePosixPath(name).parts and name not in seen and name in expected,'Unsafe/unbound archive member');seen.add(name)
    raw=archive.extractfile(member).read();ref=expected[name];require(len(raw)==ref['bytes'] and sha(raw)==ref['sha256'],'Member drift')
    loc={'bundle':row['path'],'member':name,'member_sha256':ref['sha256']};provider='claude' if 'claude' in Path(row['path']).name or name.startswith('claude/') else None
    if name.endswith('.json'):matcher.walk(strict_json(raw),loc,provider=provider)
    elif name.endswith('.jsonl'):
     for i,line in enumerate(raw.splitlines(),1):
      if line.strip():matcher.walk(strict_json(line),dict(loc,jsonl_line=i),provider=provider)
    else:
     try:text=raw.decode()
     except UnicodeError:matcher.stats['non_utf8_opaque_members']+=1;continue
     matcher.text(text,loc,provider=provider,kind='whole_text_member')
  require(seen==set(expected),'Missing expected member');members+=len(seen)
 for row in audit['loose_json_files']:matcher.walk(strict_json(bound(row)),{'bundle':None,'member':row['path'],'member_sha256':row['sha256']})
 require(frozen==[desc(ROOT/r['path']) for r in frozen],'Audit inputs changed')
 for row in audit['loose_json_files']:bound(row)
 exact=set(matcher.exact);content=set();groups=[]
 for _,row in sorted(matcher.content.items()):
  keys=row.pop('native_identities');content.update(keys);row['matched_native_identity_count']=len(keys);row['additional_to_previous1938']=len(keys-prior)
  row['ambiguous_native_occurrences']=len(keys)>1;row['weak_short_string']=row['kind']!='payload_core' and row['bytes']<=32
  row['native_identities']=[{'session_id':k[0],'source_line':k[1],'source_record_sha256':k[2]} for k in sorted(keys)]
  row['sid_contexts']=sorted(row['sid_contexts']);row['provider_contexts']=sorted(row['provider_contexts']);groups.append(row)
 exact_rows=[dict(native[k],export_locations=matcher.exact[k],already_in_previous1938=k in prior) for k in sorted(exact)]
 refs=[save('NATIVE_PREFIXES.json',verified),save('EXACT_CALL_PAYLOAD_MATCHES.json',exact_rows),save('CONTENT_ONLY_MATCH_GROUPS.json',groups)]
 report={'status':'PASS_BOUNDED_CALL_AND_CONTENT_EQUALITY_AUDIT','bundle_count':37,'members_verified':members,'loose_json_files_verified':119,'native_prefixes':81,'native_prefix_bytes':sum(r['bytes'] for r in verified),
  'native_tool_pending_records_in81':len(native),'native_tool_types_in81':histogram,'previous_exact_raw_identities':1938,
  'native_pending_without_explicit_call_id':sum(r['call_id_sha256'] is None for r in native.values()),
  'call_type_sid_plus_exact_payload_unique_native_matches':len(exact),'additional_exact_identity_matches':len(exact-prior),
  'previous_raw_identities_not_unique_call_payload_matched':len(prior-exact),'previous_raw_identities_with_ambiguous_call_tuple':len(prior&set(matcher.ambiguous)),
  'ambiguous_call_tuple_native_records':len(matcher.ambiguous),
  'native_records_with_equal_exported_content':len(content),'additional_content_only_native_records':len(content-prior-exact),
  'content_match_groups':len(groups),'short_or_repeated_content_groups':sum(r['weak_short_string'] or r['ambiguous_native_occurrences'] for r in groups),
  'structured_scan_counts':dict(matcher.stats),'inputs':frozen,'outputs':refs,
  'boundary':['Only the previously frozen81 native prefixes and37 bundles/119 loose JSON files were read. No new cutoff, private session discovery, canonical write, provider or service action.',
   'Exact additional identity requires an explicit exported SID, matching call-id hash and native tool type, exactly one native tuple occurrence within the fixed81 prefixes, and identical complete allowlisted payload core. Repeated native call tuples remain ambiguous even if text matches.',
   'Content equality uses whole payload cores, complete string body fields, or entire UTF8 non-JSON members. It does not use substring, fuzzy or semantic search. Matching content alone does not identify which native record or provider invocation produced the copy.',
   'Hidden reasoning and system/developer objects and fields are not searched. Native bodies are hashed in RAM; no body, URL, credential or scientific/private text is emitted or saved.',
   'The84799 generic denominator covers3355 sources; this followup covers only81. The previous82861 remainder remains UNKNOWN coverage, never a demonstrated loss count. No inference is made for the other sources.',
   'Per-hash example export locations are capped at12; occurrences and native-identity counts are complete within this exact equality scope. Source hashes do not claim original raw envelopes were exported.']}
 final=save('REPORT.json',report)
 print(json.dumps({'report':final,**{k:report[k] for k in ('status','native_tool_pending_records_in81','additional_exact_identity_matches','additional_content_only_native_records','content_match_groups')}}))

if __name__=='__main__':main()
