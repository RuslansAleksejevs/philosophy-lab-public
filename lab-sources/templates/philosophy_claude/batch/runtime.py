#!/usr/bin/env python3
"""Batch-local mechanical transport. No model/API calls. Hooks take JSON on stdin."""
import contextlib
import datetime
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile

VERSION = 'claude-batch.v1'
MAX = 16 * 1024 * 1024


class ToolCorrection(ValueError):
    """A refused request the caller can correct; no batch integrity failure."""


class ResultCorrection(ValueError):
    """Unusable result formatting; preserve the response and resume its worker."""


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))+'\n').encode()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def stamp():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def safe(path):
    p = Path(os.path.abspath(path))
    for part in [p, *p.parents]:
        if part.is_symlink():
            raise ValueError('symlink refused')
    return p


def read(path):
    p=safe(path)
    with p.open('rb') as f:
        before=os.fstat(f.fileno())
        if before.st_nlink != 1 or before.st_size > MAX:
            raise ValueError('unbounded or linked file')
        data=f.read(MAX+1);after=os.fstat(f.fileno())
    now=p.stat()
    fields=('st_ino','st_dev','st_size','st_mtime_ns','st_ctime_ns')
    if len(data)>MAX or any(getattr(before,k)!=getattr(x,k) for x in (after,now) for k in fields):
        raise ValueError('file changed while reading')
    return data


def atomic(path,data):
    p=safe(path);p.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(prefix='.pending-',dir=p.parent)
    try:
        with os.fdopen(fd,'wb') as f:f.write(data);f.flush();os.fsync(f.fileno())
        os.replace(tmp,p)
        fd=os.open(p.parent,os.O_RDONLY)
        try:os.fsync(fd)
        finally:os.close(fd)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)


def object_put(base,data):
    h=digest(data);p=base/'.journal/objects'/h
    if p.exists():
        if read(p)!=data:raise ValueError('damaged object')
    else:atomic(p,data)
    return h


def event(base,kind,payload):
    folder=base/'.journal/events';folder.mkdir(parents=True,exist_ok=True)
    paths=sorted(folder.glob('*.json'));previous=digest(read(paths[-1])) if paths else None
    value={'sequence':len(paths)+1,'previous':previous,'recorded_at':stamp(),'kind':kind,'payload':payload}
    data=encoded(value);atomic(folder/f'{len(paths)+1:08d}.json',data)
    return digest(data)


def word_count(data):
    text=data.decode();heads=list(re.finditer(r'^#{1,6}\s+(?:Bibliography|References)\s*#*\s*$',text,re.M|re.I))
    if len(heads)>1:raise ValueError('ambiguous bibliography boundary')
    body=text[:heads[0].start()] if heads else text
    return {'word_units':sum(bool(re.search(r'\w',t)) for t in body.split()),'whitespace_units':len(body.split()),'official_eligibility':'NOT_CERTIFIED'}


def safe_visible(value):
    s=json.dumps(value,ensure_ascii=False).lower()
    return not any(x in s for x in ('<system-reminder>', '"thinking"', '"redacted_thinking"', '"signature"', '"encrypted_content"', '-----begin private key-----', 'authorization: bearer', 'api_key'))


def read_eof_diagnostic(block, read_calls):
    """Provider Read diagnostics are visible data, despite their reminder wrapper.

    Match both the request identity and the entire numeric-only diagnostic. This
    does not admit arbitrary reminder text or treat the wrapper as instructions.
    """
    if set(block)-{'type','tool_use_id','content','is_error'}:return False
    if 'is_error' in block and not isinstance(block['is_error'],bool):return False
    if block.get('type')!='tool_result' or not isinstance(block.get('tool_use_id'),str) or block['tool_use_id'] not in read_calls:return False
    content=block.get('content')
    if not isinstance(content,str):return False
    return re.fullmatch(r'<system-reminder>Warning: the file exists but is shorter than the provided offset \([0-9]+\)\. The file has [0-9]+ lines\.</system-reminder>',content) is not None


def fragments(raw):
    """Exact JSON spans, preserving safe fragment bytes without copying its envelope.

    Hidden-thinking siblings are parsed for structure but never returned/stored.
    A fragment is explicitly not claimed to be a complete original JSONL record.
    """
    text = raw.decode('utf-8')
    decoder = json.JSONDecoder()
    result = {}
    def ws(i):
        while i < len(text) and text[i].isspace(): i += 1
        return i
    def visit(i, path):
        i = ws(i)
        begin = i
        if text[i] == '{':
            i = ws(i + 1)
            while text[i] != '}':
                key, i = decoder.raw_decode(text, i)
                i = ws(i)
                if text[i] != ':': raise ValueError('invalid object delimiter')
                i = visit(i + 1, path + (key,))
                i = ws(i)
                if text[i] == '}': break
                if text[i] != ',': raise ValueError('invalid object separator')
                i = ws(i + 1)
            end = i + 1
        elif text[i] == '[':
            i, n = ws(i + 1), 0
            while text[i] != ']':
                i = visit(i, path + (n,)); n += 1
                i = ws(i)
                if text[i] == ']': break
                if text[i] != ',': raise ValueError('invalid array separator')
                i = ws(i + 1)
            end = i + 1
        else:
            _, end = decoder.raw_decode(text, i)
        if path == ('message', 'content') or (len(path) == 3 and path[:2] == ('message', 'content')):
            result[path] = text[begin:end].encode('utf-8')
        return end
    visit(0, ())
    return result

class Batch:
    def __init__(self,base):
        self.base=safe(base);self.root=self.base.parent.parent
        self.manifest=json.loads(read(self.base/'manifest.json'))
        self.tasks={t['id']:t for t in self.manifest['tasks']}
        self.state_path=self.base/'.journal/state.json'

    @property
    def text_transport(self):
        return self.manifest.get('output_transport')=='native_text'

    @property
    def gradual(self):
        return self.manifest.get('recovery_policy') == 'gradual-v1'

    @staticmethod
    def quota_error(value):
        text = json.dumps(value, ensure_ascii=False).lower()
        return any(marker in text for marker in (
            'rate_limit', 'rate limit', 'usage limit', 'usage_limit',
            '5-hour limit', 'five-hour limit', "you’ve hit your limit", "you've hit your limit",
            "you've hit your session limit", "you’ve hit your session limit"))

    def reconcile_quota_halt(self, s):
        # A missing reply immediately before a provider quota signal is an
        # interrupted attempt, not an integrity failure. Never erase other blocks.
        halt=s.get('halt',{})
        if (s.get('quota_wait') and halt.get('reason')=='Worker returned without a sealed result or checkpoint; inspect native record.'
                and halt.get('task') in s['agents'].values() and halt['task'] not in s['done']):
            s['last_receipt']=event(self.base,'batch.quota_supersedes_missing_result',
                                   {'previous_halt':s.pop('halt'),'quota_evidence':s['quota_wait']['evidence'],
                                    'outcome':'INCOMPLETE; no success inferred'})
            self.save(s)

    def agent_quota_error(self, result):
        # Only the provider's leading error notice, never words in an essay or
        # returned prompt. Agent can report status=completed after an API failure.
        blocks=result.get('content',[]) if isinstance(result,dict) else []
        first=blocks[0] if isinstance(blocks,list) and blocks else {}
        text=first.get('text','') if isinstance(first,dict) else ''
        return isinstance(text,str) and text.startswith('Agent terminated early due to an API error:') and self.quota_error(text)

    def pause_quota(self, s, evidence):
        # Keep pending requests and agent identity. Never invent a reset time.
        if not s.get('quota_wait'):
            ref = object_put(self.base, encoded(evidence if safe_visible(evidence) else {'coverage':'unsafe error details withheld','classification':'quota'}))
            s['quota_wait'] = {'at': stamp(), 'evidence': ref, 'reset_at': 'UNKNOWN'}
            s['last_receipt'] = event(self.base, 'batch.quota_wait', s['quota_wait'])
            self.save(s)
        self.reconcile_quota_halt(s)
        if s.get('halt',{}).get('state')=='BLOCKED':
            return {'systemMessage':'Provider quota pause recorded, but a separate integrity block remains: '+s['halt']['reason']+'. Codex review is required; another prompt alone will not clear it.'}
        return {'systemMessage': 'WAITING_FOR_QUOTA. Saved files and agent IDs are retained. Stop without retries. After the provider limit resets, the user may continue this same chat. No scheduler or automatic quota polling.'}

    def resume_quota(self, s):
        return self.resume_interrupted(s, {}, quota=True)

    def cancellation_evidence(self, h, aid=None):
        """Read only the bound transcript; retain exact cancellation fragments.

        Cancellation does not reliably emit PostToolUseFailure. A terminal child
        interrupt is evidence of a stopped worker; an old marker followed by a
        new turn is not. No transcript body is sent to the dispatcher.
        """
        sid=h.get('session_id');parent=safe(h.get('transcript_path',''))
        if not sid or parent.name!=sid+'.jsonl':return {}, None
        path=parent if aid is None else parent.parent/sid/'subagents'/('agent-'+aid+'.jsonl')
        try:raw=read(path)
        except FileNotFoundError:return {}, None
        if not raw.endswith(b'\n'):return {}, None
        calls={};terminal=None
        for n,line in enumerate(raw.splitlines(),1):
            r=json.loads(line)
            if r.get('type') not in ('user','assistant') or r.get('isMeta') or r.get('isCompactSummary'):continue
            if r.get('sessionId')!=sid or r.get('cwd')!=str(self.root) or r.get('agentId')!=aid:
                raise ValueError('cancellation transcript scope differs')
            m=r.get('message',{});content=m.get('content',[])
            if m.get('role')!=r['type']:raise ValueError('cancellation transcript role differs')
            terminal=None
            blocks=[(None,content)] if isinstance(content,str) else list(enumerate(content))
            for index,block in blocks:
                text=block if isinstance(block,str) else block.get('text','')
                marker=r['type']=='user' and text in ('[Request interrupted by user]','[Request interrupted by user for tool use]')
                cancelled=(r['type']=='user' and isinstance(block,dict) and block.get('type')=='tool_result'
                           and block.get('is_error') is True and isinstance(block.get('content'),str)
                           and block['content'].startswith("The user doesn't want to proceed with this tool use. The tool use was rejected")
                           and block['content'].endswith('STOP what you are doing and wait for the user to tell you how to proceed.'))
                if not marker and not cancelled:continue
                key=('message','content') if index is None else ('message','content',index)
                evidence={'object':object_put(self.base,fragments(line)[key]),'line':n,
                          'timestamp':r.get('timestamp','UNKNOWN'),'session_id':sid,'agent_id':aid,
                          'source_sha256':digest(raw),'source_line_count':len(raw.splitlines())}
                if marker:terminal=evidence
                if cancelled:calls[block['tool_use_id']]=evidence
        return calls,terminal

    def resume_interrupted(self, s, h, quota=False):
        # Read-only attempts can be repeated. A known worker must retain its ID.
        # An unacknowledged launch has an unknown outcome; never launch a duplicate.
        if quota:self.reconcile_quota_halt(s)
        if s.get('halt',{}).get('state')=='BLOCKED':
            return {'hookSpecificOutput':{'hookEventName':'UserPromptSubmit','additionalContext':'A separate block still needs review: '+s['halt']['reason']+'. A further human prompt alone will not clear it.'}}
        cancelled,_=self.cancellation_evidence(h) if h else ({},None)
        stopped={}
        for aid,tid in s['agents'].items():
            if tid not in s['done']:
                _,proof=self.cancellation_evidence(h,aid) if h else ({},None)
                # Never reuse the same old cancellation after resuming that worker.
                marker={k:proof[k] for k in ('object','line','timestamp')} if proof else None
                if proof and s.get('consumed_interrupts',{}).get(aid)!=marker:stopped[tid]=(aid,proof)
        aborted=s.get('aborted_calls',{})
        changed=False;recovered_tasks=set()
        unresolved = []
        for call, pending in list(s['pending'].items()):
            name = pending['name']
            tid=pending['task']
            if name == 'Agent':
                task = next(t for t in self.tasks.values() if t['agent_name'] == pending['input']['subagent_type'])
                if task['id'] not in s['agents'].values():
                    unresolved.append(call); continue
                tid=task['id']
            elif name=='SendMessage':tid=s['agents'].get(pending['input'].get('to'))
            elif name not in ('Read', 'WebFetch', 'WebSearch', 'SendMessage', 'ToolSearch'):
                unresolved.append(call); continue
            proof=cancelled.get(call) or aborted.get(call) or (stopped.get(tid) or (None,None))[1]
            if not quota and not proof:continue
            # A cancelled parent call alone cannot declare a background worker idle.
            if not quota and name in ('Agent','SendMessage') and tid not in stopped and tid not in s['done'] and call not in aborted:continue
            event(self.base, 'tool.interrupted', {'call': call, 'request': pending, 'outcome': 'UNKNOWN',
                  'reason': 'quota; resume explicitly requested' if quota else 'cancelled attempt; human resume requested', 'evidence':proof})
            s.setdefault('interrupted_calls', {})[call] = pending
            del s['pending'][call]
            s.get('aborted_calls',{}).pop(call,None)
            if tid:recovered_tasks.add(tid)
            changed=True
        if unresolved and quota:
            self.save(s)
            return {'decision': 'block', 'reason': 'Quota pause preserved. A launch has no confirmed agent ID yet; Codex must reconcile it before resuming. Do not start another worker.'}
        for aid, tid in s['agents'].items():
            if tid not in s['done'] and (quota or tid in stopped or tid in recovered_tasks):
                files = {p.name: digest(read(p)) for p in (self.base/'tasks'/tid/'output').iterdir()}
                s.setdefault('checkpoints', {}).setdefault(tid, {'agent_id': aid, 'files': files, 'count': 0, 'native_object': None})
                s.setdefault('continuing',{}).pop(tid,None)
                if tid in stopped:s.setdefault('consumed_interrupts',{})[aid]={k:stopped[tid][1][k] for k in ('object','line','timestamp')}
                changed=True
        if quota:
            s['continuing'] = {}
            event(self.base, 'batch.quota_resume_requested', {'previous': s.pop('quota_wait'), 'source': 'human prompt; not proof quota reset'})
        if s.get('halt',{}).get('state')=='INTERRUPTED' and not s['pending'] and not s.get('continuing'):
            event(self.base,'batch.interruption_resumed',{'previous':s.pop('halt'),'source':'human prompt; interrupted attempts retained, not successful'})
            changed=True
        if changed:
            s['auto_continue_used']=False
            s.setdefault('tool_corrections',{}).pop('dispatcher',None)
            event(self.base,'batch.resume_reconciled',{'cancelled_workers':{tid:proof for tid,(aid,proof) in stopped.items()},'remaining_pending':list(s['pending'])})
        self.save(s)
        return {'hookSpecificOutput':{'hookEventName':'UserPromptSubmit','additionalContext':
                'Resume state reconciled. Cancelled attempts remain UNKNOWN, never success. '+self.next_action(s)}} if changed else {}

    def next_action(self,s):
        if s.get('halt',{}).get('state')=='BLOCKED':return 'BLOCKED: '+s['halt']['reason']+'. Further prompts alone cannot clear an integrity block.'
        if s.get('quota_wait'):return 'WAITING_FOR_QUOTA. Stop; a later human prompt is needed. No automatic wake-up.'
        if s.get('halt'):return 'State '+s['halt']['state']+': '+s['halt']['reason']
        if len(s['done'])==len(self.tasks):return 'COMPLETE. All tasks are sealed.'
        if s.get('continuing'):return 'Worker is running in background. Yield for its notification; this is not package completion.'
        if s.get('pending'):return 'An operation is outstanding. Read STATUS if needed; do not launch a duplicate.'
        if s.get('checkpoints'):
            tid=next(iter(s['checkpoints']));return 'Continue '+tid+' using SendMessage to '+s['checkpoints'][tid]['agent_id']+'. Then finish all remaining ready tasks.'
        ready=self.summary(s)['ready']
        return ('Start '+ready[0]+' with Agent. Continue the entire remaining package.' if ready else 'Await saved native evidence before dependent work.')

    def halt(self,s,reason,task=None,kind='BLOCKED'):
        s['halt']={'state':kind,'reason':str(reason),'task':task,'at':stamp()}
        s['last_receipt']=event(self.base,'batch.halted',s['halt']);self.save(s)
        return {'systemMessage':'Batch '+kind+': '+str(reason)+'. Stop; Codex will inspect. Do not retry or change configuration.'}

    def tool_error(self, reason):
        raise (ToolCorrection if self.gradual else ValueError)(reason)

    def correction_budget(self, s, task):
        actor = task or 'dispatcher'
        counts = s.setdefault('tool_corrections', {})
        counts[actor] = counts.get(actor, 0) + 1
        return counts[actor] <= 8

    def handle(self,h):
        try:return self.dispatch(h)
        except ToolCorrection as e:
            with self.locked():
                s=self.state();tid=s['agents'].get(h.get('agent_id'))
                if h.get('hook_event_name')!='PreToolUse' or h.get('session_id')!=s.get('parent_session'):
                    raise
                self.observe_hook(h,'tool.correctable_denial',str(e))
                s.setdefault('denied_calls',{})[h['tool_use_id']]={'task':tid,'name':h['tool_name']}
                reason=str(e)+'. This request was not executed. Correct it or continue another allowed step; the batch is not halted.'
                if not self.correction_budget(s,tid):
                    self.halt(s,'Repeated tool failures without a successful step; state preserved',tid)
                    reason='Repeated tool failures; report STATUS and stop.'
                else:self.save(s)
                return {'hookSpecificOutput':{'hookEventName':'PreToolUse','permissionDecision':'deny','permissionDecisionReason':reason}}
        except Exception as e:
            if not self.text_transport:raise
            with self.locked():
                s=self.state()
                # Foreign sessions must not be able to halt or steal an active batch.
                owned=not h.get('agent_id') or h.get('agent_id') in s['agents']
                self.observe_hook(h,'hook.rejected',str(e))
                if owned and s.get('parent_session')==h.get('session_id') and not s.get('halt') and not s.get('quota_wait'):
                    self.halt(s,str(e),s['agents'].get(h.get('agent_id')))
            if h.get('hook_event_name')=='PreToolUse':
                return {'hookSpecificOutput':{'hookEventName':'PreToolUse','permissionDecision':'deny','permissionDecisionReason':str(e)+'. Stop; do not retry.'}}
            if h.get('hook_event_name')=='UserPromptSubmit':return {'decision':'block','reason':str(e)}
            return {'systemMessage':'Batch action failed: '+str(e)+'. Stop; Codex will inspect.'}

    def observe_hook(self,h,kind,reason):
        # Identity/routing metadata only: never archive an unrelated actor's body.
        fields={k:v for k in ('hook_event_name','session_id','agent_id','agent_type','tool_name','tool_use_id')
                if isinstance(v:=h.get(k),str) and re.fullmatch(r'[A-Za-z0-9_.:-]{1,180}',v)}
        fields['reason']=reason if safe_visible(reason) else 'details withheld'
        event(self.base,kind,fields)

    def reconcile_staged(self,s):
        for tid,ref in list(s.get('staged',{}).items()):
            if s.get('halt') or s.get('quota_wait'):break
            try:self.accept_text(self.tasks[tid],s,json.loads(read(self.base/'.journal/objects'/ref)))
            except Exception as e:self.halt(s,str(e),tid)

    @contextlib.contextmanager
    def locked(self):
        (self.base/'.journal').mkdir(exist_ok=True)
        p=safe(self.base/'.journal/lock')
        with p.open('a') as f:
            fcntl.flock(f,fcntl.LOCK_EX)
            yield

    def state(self):
        previous=None;latest=None
        for seq,p in enumerate(sorted((self.base/'.journal/events').glob('*.json')),1):
            data=read(p);e=json.loads(data)
            if e['sequence']!=seq or e['previous']!=previous:raise ValueError('journal chain damaged')
            previous=digest(data)
            if e['kind']=='state.saved':latest=e['payload']['object']
        if latest:
            data=read(self.base/'.journal/objects'/latest)
            if digest(data)!=latest:raise ValueError('state object damaged')
            return json.loads(data)
        return {'parent_session':None,'agents':{},'done':{},'pending':{},'last_receipt':None,'interrupted':[]}

    def save(self,s):
        ref=object_put(self.base,encoded(s));event(self.base,'state.saved',{'object':ref})
        atomic(self.state_path,encoded(s));atomic(self.base/'STATUS.json',encoded(self.summary(s)))

    def check(self):
        pointer=json.loads(read(self.root/'BATCH.json'))
        if pointer != {'protocol':VERSION,'batch_id':self.manifest['batch_id'],'state':'ACTIVE','manifest_sha256':digest(read(self.base/'manifest.json'))}:
            raise ValueError('batch is not active or exact manifest changed')
        for name,h in self.manifest['controls'].items():
            if digest(read(self.root/name))!=h:raise ValueError('bound instructions/runtime/settings changed')
        for name,h in self.manifest['inputs'].items():
            if digest(read(self.base/name))!=h:raise ValueError('bound input changed')

    def summary(self,s):
        ready=[t['id'] for t in self.tasks.values() if t['id'] not in s['done'] and all(d in s['done'] for d in t['depends_on'])]
        if self.text_transport:ready=[tid for tid in ready if tid not in s['agents'].values()]
        if self.gradual:ready.sort(key=lambda tid:(self.tasks[tid]['essay_id'], list(self.tasks).index(tid)))
        return {'protocol':VERSION,'batch_id':self.manifest['batch_id'],'state':'BLOCKED' if s.get('halt',{}).get('state')=='BLOCKED' else 'WAITING_FOR_QUOTA' if s.get('quota_wait') else s['halt']['state'] if s.get('halt') else 'COMPLETE' if len(s['done'])==len(self.tasks) else 'IN_PROGRESS' if s['parent_session'] else 'PREPARED',
                'quota_wait':s.get('quota_wait'),'halt':s.get('halt'),'checkpoints':s.get('checkpoints',{}),
                'awaiting_result':s.get('continuing',{}),'awaiting_native':list(s.get('staged',{})),
                'completed':len(s['done']),'total':len(self.tasks),'ready':ready,'resumable':[{'task':tid,'agent_id':aid} for aid,tid in s['agents'].items() if tid not in s['done']], 'pending_receipts':len(s['pending']),'last_receipt':s['last_receipt'],
                'canonical_import':'PENDING_CODEX_REVIEW','native_configuration':'PENDING_NATIVE_VERIFICATION',
                'boundary':'Mechanical receipts certify saved bytes and gates only; not provider identity, reasoning, source truth or philosophical quality.'}

    def task_for(self,h,s):
        agent=h.get('agent_id')
        if not agent:return None
        tid=s['agents'].get(agent)
        if not tid:raise ValueError('unregistered child; hooks must identify each child')
        return self.tasks[tid]

    def verify_done(self,s):
        for tid,receipt in s['done'].items():
            for name,sha in receipt['files'].items():
                if digest(read(self.base/'tasks'/tid/'output'/name))!=sha:raise ValueError('sealed output changed')
        for mapping in s.get('sources',{}).values():
            for path,sha in mapping.items():
                if digest(read(self.base/path))!=sha:raise ValueError('saved source changed')

    def capture_source(self,task,s,url):
        import importlib.util
        module=getattr(self,'source_module',None)
        if module is None:
            spec=importlib.util.spec_from_file_location('batch_source_capture',Path(__file__).parent/'source_capture.py')
            module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        try:raw,kind,charset,meta=module.fetch(url)
        except Exception as e:
            detail=str(e)[:500]
            event(self.base,'source.unavailable',{'task':task['id'],'url':url,'reason':detail if safe_visible(detail) else 'Details withheld'})
            return 'Direct source download unavailable; preserve this access limitation. No full-source reading is established.'
        raw_sha=object_put(self.base,raw)
        try:
            text,extension,method=module.extract(raw,kind,charset)
            if not text.strip():raise ValueError('No extractable text; OCR or another accessible edition needed')
            if len(text)>MAX:raise ValueError('Extracted text exceeds capture bound')
            meta.update(extraction='TEXT_EXTRACTED',method=method)
        except Exception as e:
            text=None;extension='pdf' if raw.startswith(b'%PDF-') else 'bin'
            meta.update(extraction='UNAVAILABLE',reason=str(e)[:500])
        meta['raw_sha256']=raw_sha
        prefix='tasks/'+task['id']+'/sources/'+raw_sha[:20]+'-'+digest(encoded(meta))[:12]
        meta['original_path']=prefix+'.original.'+extension
        meta['text_path']=prefix+'.txt' if text is not None else None
        material={prefix+'.original.'+extension:raw,prefix+'.json':encoded(meta)}
        if text is not None:material[prefix+'.txt']=text
        mapping=s.setdefault('sources',{}).setdefault(task['id'],{})
        for path,data in material.items():
            ref=object_put(self.base,data);target=self.base/path
            if target.exists() and read(target)!=data:raise ValueError('Source snapshot collision')
            if not target.exists():atomic(target,data)
            mapping[path]=ref
        s['last_receipt']=event(self.base,'source.saved',{'task':task['id'],'files':{p:mapping[p] for p in material},'metadata':mapping[prefix+'.json']})
        self.save(s)
        message='Original source and extraction metadata saved. Read '+str(self.base/(prefix+'.json'))+'. '
        return message+('Read full extracted text at '+str(self.base/(prefix+'.txt'))+'. This is a separate HTTP retrieval, not the WebFetch summary.' if text is not None else 'Text extraction unavailable; original bytes preserved. Do not claim to have read its text.')

    def scoped(self,value,task,s,writing=False):
        if not isinstance(value,str) or not value:self.tool_error('explicit path required')
        p=Path(value);p=safe(p if p.is_absolute() else self.root/p)
        if task:
            out=self.base/'tasks'/task['id']/'output'
            if writing:
                if p.parent!=out or not re.fullmatch(r'[a-z][a-z0-9-]*\.(md|json|txt|pdf)',p.name):raise ValueError('write outside assigned flat output directory')
                if task['id'] in s['done'] or p.exists():raise ValueError('sealed or existing output: use a new numbered file')
            else:
                allowed=[self.base/name for name in task['inputs']]
                allowed += [self.base/'tasks'/d/'output'/name for d in task['depends_on'] for name in s['done'].get(d,{}).get('files',{})]
                allowed += [self.base/name for tid in [task['id']]+[d for d in task['depends_on'] if d in s['done']] for name in s.get('sources',{}).get(tid,{})]
                # Authorization depends on ownership, not file existence. A missing
                # own output must yield an ordinary Read failure, not a batch halt.
                own_output=p.parent==out and (p.exists() or self.gradual and re.fullmatch(r'[a-z][a-z0-9-]*\.(md|json|txt|pdf)',p.name))
                if p not in allowed and not own_output:self.tool_error('Read only assigned inputs, saved sources, completed dependencies or your own output files')
        elif writing:raise ValueError('dispatcher cannot write manuscripts or control files')
        elif p not in (self.root/'BATCH.json',self.root/'CLAUDE.md',self.base/'manifest.json',self.base/'STATUS.json'):
            self.tool_error('dispatcher may read only neutral queue and status')
        return p

    def read_alias(self, value, task, s):
        """Resolve common task-relative paths without guessing across essays."""
        if not self.gradual or not task or not isinstance(value,str):return value
        p=Path(value)
        if p.is_absolute() or '..' in p.parts:return value
        folder=self.base/'tasks'/task['id']
        if p.parts and p.parts[0] in ('input','output','sources'):return str(folder/p)
        if len(p.parts)==1:
            candidates=[self.base/n for n in task['inputs'] if Path(n).name==value]
            candidates += [self.base/n for n in s.get('sources',{}).get(task['id'],{}) if Path(n).name==value]
            if value in task['required_outputs'] or (folder/'output'/value).exists():candidates.append(folder/'output'/value)
            if len(candidates)==1:return str(candidates[0])
        return value

    def dispatch(self,h):
        with self.locked():
            self.check()
            if h.get('cwd')!=str(self.root):raise ValueError('batch hooks must run in the exact released project root')
            s=self.state();self.verify_done(s)
            typ=h['hook_event_name'];session=h.get('session_id')
            if not isinstance(session,str) or not re.fullmatch(r'[A-Za-z0-9_-]+',session):raise ValueError('missing session identity')
            if typ=='SessionStart':
                receipt=event(self.base,'session.observed',{'session_id':session,'at':stamp(),'source':'hook'})
                s['last_receipt']=receipt;self.save(s)
                return {'hookSpecificOutput':{'hookEventName':typ,'additionalContext':'Read BATCH.json and the batch STATUS.json. Execute only its ready tasks. No essay generation in the dispatcher. Hooks provide mechanical save receipts; final canonical review stays with Codex.'}}
            if typ=='UserPromptSubmit':
                prompt=h.get('prompt')
                if self.text_transport and h.get('agent_id'):
                    self.observe_hook(h,'hook.outside_batch','Worker prompt hook is not a human dispatcher prompt')
                    return {}
                notification=isinstance(prompt,str) and prompt.lstrip().startswith('<task-notification>')
                if notification:
                    match=re.search(r'<task-id>([A-Za-z0-9_-]+)</task-id>',prompt)
                    if session!=s['parent_session'] or not match or match[1] not in s['agents']:
                        self.observe_hook(h,'hook.outside_batch','Notification has no registered task; body not retained')
                        return {}
                if not isinstance(prompt,str) or not safe_visible(prompt):raise ValueError('prompt requires scoped archival review')
                if not s['parent_session']:
                    if h.get('agent_id') or s['agents'] or s['pending'] or s['done']:raise ValueError('cannot bind active or child session')
                    s['parent_session']=session
                    event(self.base,'session.bound',{'session_id':session,'source':'first UserPromptSubmit; SessionStart is provisional'})
                elif session!=s['parent_session']:raise ValueError('resume the same dispatcher chat')
                kind='provider.notification' if notification else 'human.prompt'
                ref=object_put(self.base,encoded({'prompt':prompt,'session_id':session,'source':'UserPromptSubmit hook; notification marker distinguished from human input'}))
                s['last_receipt']=event(self.base,kind,{'object':ref});self.save(s)
                if self.gradual and not notification:
                    return self.resume_interrupted(s,h,quota=bool(s.get('quota_wait')))
                return {}
            if session!=s['parent_session']:raise ValueError('session not bound by first user prompt')
            if self.text_transport and h.get('agent_id') not in (None,'') and h['agent_id'] not in s['agents']:
                # Only SubagentStart may register a worker, with a matching launch.
                approved_start=typ=='SubagentStart' and any(
                    p['name']=='Agent' and p['input'].get('subagent_type')==h.get('agent_type')
                    for p in s['pending'].values())
                if not approved_start:
                    self.observe_hook(h,'hook.outside_batch','Unregistered actor; no batch state changed')
                    if typ=='PreToolUse':
                        return {'hookSpecificOutput':{'hookEventName':typ,'permissionDecision':'deny','permissionDecisionReason':'This worker is not assigned to the active batch.'}}
                    return {}
            if self.text_transport and typ=='StopFailure':
                if self.gradual and self.quota_error({k:h[k] for k in ('error','error_details','last_assistant_message','stop_reason') if k in h}):
                    return self.pause_quota(s, {k:h[k] for k in ('error','error_details','last_assistant_message','stop_reason') if k in h})
                return self.halt(s,'Provider turn ended abnormally; preserve pending receipts for Codex recovery.',kind='INTERRUPTED')
            if typ=='SubagentStart':
                agent=h.get('agent_id');name=h.get('agent_type')
                matches=[t for t in self.tasks.values() if t['agent_name']==name]
                if len(matches)!=1 or not agent:raise ValueError('unapproved agent type')
                t=matches[0]
                pending_launch=any(p['name']=='Agent' and p['input'].get('subagent_type')==name or p['name']=='SendMessage' and p['input'].get('to')==agent for p in s['pending'].values())
                continuing=s.get('continuing',{}).get(t['id'],{})
                approved_background=continuing.get('agent_id')==agent and s['agents'].get(agent)==t['id']
                if self.text_transport and not (pending_launch or approved_background):raise ValueError('child start without approved launch/continuation')
                if t['id'] in s['done'] or not all(d in s['done'] for d in t['depends_on']):raise ValueError('task not ready')
                if agent in s['agents'] and s['agents'][agent]!=t['id']:raise ValueError('agent identity reuse')
                if any(v==t['id'] and a!=agent for a,v in s['agents'].items()):raise ValueError('resume the original child; duplicate task launch forbidden')
                s['agents'][agent]=t['id'];s['last_receipt']=event(self.base,'agent.started',{'agent_id':agent,'task':t['id'],'agent_type':name,'requested':t['configuration'],'source':'hook'})
                self.save(s);return {}
            task=self.task_for(h,s)
            if self.text_transport and not task and typ in ('PreToolUse','Stop'):
                self.reconcile_staged(s)
            if typ=='PreToolUse':
                name=h['tool_name'];args=h.get('tool_input',{});call=h.get('tool_use_id')
                diagnostic_read=name=='Read' and not task
                if self.gradual and s.get('quota_wait') and not diagnostic_read:
                    return {'hookSpecificOutput':{'hookEventName':typ,'permissionDecision':'deny','permissionDecisionReason':'WAITING_FOR_QUOTA; stop and preserve state.'}}
                if self.text_transport and s.get('halt') and not (name=='Read' and not task):raise ValueError('batch halted; report STATUS and stop')
                same_actor=[p for p in s['pending'].values() if p['task']==(task['id'] if task else None)]
                reads={'Read','WebSearch','WebFetch'}
                if same_actor and not (self.gradual and diagnostic_read) and not (name in reads and all(p['name'] in reads for p in same_actor)):self.tool_error('Previous tool has no durable result receipt yet; wait for that result before dependent work')
                if not isinstance(args,dict) or not call:raise ValueError('unknown tool call schema')
                updated=None
                if self.text_transport and name=='ToolSearch' and not task:
                    if args.get('query','').strip()!='select:SendMessage':self.tool_error('Use ToolSearch(query="select:SendMessage") only for continuation')
                    if not s.get('checkpoints'):self.tool_error('No checkpoint needs continuation; consult STATUS for the next ready task')
                    updated={'query':'select:SendMessage','max_results':1}
                elif self.text_transport and name=='SendMessage' and not task:
                    # Desktop may emit modern fields together with legacy team-message
                    # aliases. Accept only a consistent direct message, then remove
                    # aliases and replace all prose before the provider sees it.
                    aid=args.get('to') or args.get('recipient');tid=s['agents'].get(aid)
                    if args.get('type','message')!='message':self.tool_error('only direct continuation messages permitted')
                    if 'recipient' in args and args['recipient']!=aid:self.tool_error('conflicting continuation recipient')
                    if not tid or tid in s['done'] or tid not in s.get('checkpoints',{}):self.tool_error('Continuation requires a registered checkpoint; consult STATUS')
                    if tid in s.get('continuing',{}):self.tool_error('Continuation already dispatched; wait for its completion notification')
                    updated={'to':aid,'summary':'Continue the assigned task from its saved checkpoint.',
                             'message':'Continue only your assigned task. Read your saved output files first. Return a result JSON containing only missing or new files; do not repeat or rewrite saved files. Local code retains them from earlier replies. Complete all required outputs, then report complete.'}
                    if self.gradual:
                        saved=sorted(p.name for p in (self.base/'tasks'/tid/'output').iterdir() if p.is_file())
                        missing=[n for n in self.tasks[tid]['required_outputs'] if n not in saved]
                        updated['message']='Continue only your assigned task. Saved files (retained by local code): '+json.dumps(saved)+'. Missing required files: '+json.dumps(missing)+'. '
                        updated['message'] += 'Return only ONE missing or new file as result JSON; checkpoint while work remains, complete when finished. Do not repeat or rewrite saved files. There is no need to test missing files with Read. Read your existing files only if needed. Ordinary missing-file or refused-tool errors do not stop the batch: follow the corrective tool message. Biography is your account of the work; do not invent settings or timestamps.'
                        if s['checkpoints'][tid].get('correction'):updated['message']+=' Required mechanical correction: '+s['checkpoints'][tid]['correction']
                    s.setdefault('continuing',{})[tid]={'agent_id':aid,'call':call,'requested_at':stamp()}
                elif name=='Agent' and not task:
                    if self.text_transport and s.get('continuing'):self.tool_error('Wait for the registered continuation completion notification')
                    if self.gradual and any(tid not in s['done'] for tid in s['agents'].values()):
                        self.tool_error('Finish the existing worker through SendMessage before starting the next task')
                    t=next((t for t in self.tasks.values() if t['agent_name']==args.get('subagent_type')),None)
                    if not t or t['id'] in s['done'] or not all(d in s['done'] for d in t['depends_on']):self.tool_error('Agent task not ready; read STATUS and use an exact ready agent_name from manifest')
                    if args.get('fork') or args.get('isolation') or args.get('run_in_background'):self.tool_error('Launch the fresh custom Agent without fork, isolation or run_in_background fields')
                    existing=[a for a,tid in s['agents'].items() if tid==t['id']]
                    if self.text_transport and (existing or args.get('resume')):self.tool_error('use SendMessage for the registered checkpoint; no duplicate Agent')
                    if existing and args.get('resume') not in existing:raise ValueError('resume original partial child, do not duplicate it')
                    if args.get('resume') and args['resume'] not in existing:raise ValueError('unregistered resume')
                    updated={k:v for k,v in args.items() if k in ('model','effort','resume','run_in_background') and v is not None}
                    updated.update(prompt=t['dispatch_prompt'],subagent_type=t['agent_name'],description='Execute '+t['id'])
                    if args.get('model') is not None and args['model']!=t['configuration']['model']:raise ValueError('model override differs from approved configuration')
                    if args.get('effort') is not None and args['effort']!=t['configuration']['effort']:raise ValueError('effort override differs from approved configuration')
                elif name=='Read':
                    value=args.get('file_path')
                    alias=self.read_alias(value,task,s)
                    if alias!=value:updated={**args,'file_path':alias};value=alias
                    # Provider WebFetch returns its own PDF cache path. When the
                    # exact same bytes are already assigned to this worker, read
                    # our archived copy instead; do not open the whole cache.
                    if task and isinstance(value,str):
                        candidate=Path(value)
                        cache=Path(h.get('transcript_path','')).parent/session/'tool-results'
                        if candidate.parent==cache and re.fullmatch(r'webfetch-[A-Za-z0-9-]+\.pdf',candidate.name):
                            try:content_hash=digest(read(safe(candidate)))
                            except FileNotFoundError:self.tool_error('Provider PDF cache is absent; use the saved source paths returned by the capture hook')
                            sources=s.get('sources',{})
                            owners=[task['id']]+[d for d in task['depends_on'] if d in s['done']]
                            matches=[self.base/p for owner in owners for p,ref in sources.get(owner,{}).items()
                                     if p.endswith('.original.pdf') and ref==content_hash]
                            if matches:
                                local=matches[0]
                                if digest(read(local))!=content_hash:raise ValueError('assigned PDF bytes changed')
                                updated={**args,'file_path':str(local)};value=str(local)
                    self.scoped(value,task,s)
                elif name=='Write':
                    if self.text_transport:self.tool_error('Return this file as result JSON text; local transport saves it. Write is unnecessary')
                    if not task:raise ValueError('dispatcher writes forbidden')
                    self.scoped(args.get('file_path'),task,s,True)
                    if not isinstance(args.get('content'),str) or not safe_visible(args):raise ValueError('write requires safe visible text')
                elif name in ('WebSearch','WebFetch') and task and task['public_web']:
                    if not safe_visible(args):raise ValueError('unsafe source request')
                    if name=='WebFetch':
                        from urllib.parse import urlsplit
                        import ipaddress
                        u=urlsplit(args.get('url',''));host=u.hostname or ''
                        if u.scheme!='https' or u.username or u.password or not host or host=='localhost' or host.endswith('.local'):self.tool_error('Use a public HTTPS source URL without credentials')
                        try:
                            if not ipaddress.ip_address(host).is_global:self.tool_error('private IP source forbidden')
                        except ValueError as e:
                            if 'private IP' in str(e):raise
                else:self.tool_error('Tool '+name+' is unavailable for this role; '+('use Read, approved WebSearch/WebFetch and return files as result JSON' if task else 'use Read for queue/status, Agent for ready tasks, SendMessage for checkpoints'))
                if not safe_visible(updated or args):raise ValueError('unreviewable tool input')
                s['pending'][call]={'name':name,'input':updated or args,'task':task['id'] if task else None}
                ref=object_put(self.base,encoded(s['pending'][call]));s['last_receipt']=event(self.base,'tool.request',{'call':call,'object':ref});self.save(s)
                response={'hookEventName':typ,'permissionDecision':'allow','permissionDecisionReason':'Exact released batch task and scoped tool.'}
                if updated is not None:response['updatedInput']=updated
                return {'hookSpecificOutput':response}
            if typ in ('PostToolUse','PostToolUseFailure'):
                call=h.get('tool_use_id');pending=s['pending'].get(call)
                if not pending:
                    denied=s.get('denied_calls',{}).get(call)
                    if self.gradual and denied and denied['task']==(task['id'] if task else None) and typ=='PostToolUseFailure':
                        self.observe_hook(h,'tool.denied_callback','Refused request callback; no execution or new failure')
                        return {}
                    previous=s.get('interrupted_calls',{}).get(call)
                    if self.gradual and previous and previous['task']==(task['id'] if task else None):
                        self.observe_hook(h,'tool.late_callback','Late callback for preserved interrupted request; not treated as fresh success')
                        return {}
                    raise ValueError('result without registered request')
                if (task['id'] if task else None)!=pending['task']:raise ValueError('result actor mismatch')
                result=h.get('tool_response',h.get('error','UNKNOWN'))
                if not safe_visible(result):raise ValueError('result requires Codex review before dependent work')
                if self.gradual and typ=='PostToolUseFailure' and h.get('is_interrupt') is True:
                    ref=object_put(self.base,encoded({'call':call,'error':result,'is_interrupt':True}))
                    event(self.base,'tool.aborted',{'call':call,'object':ref,'task':pending['task'],'outcome':'INTERRUPTED'})
                    interrupted_task=pending['task']
                    if pending['name']=='Agent':interrupted_task=next(t['id'] for t in self.tasks.values() if t['agent_name']==pending['input']['subagent_type'])
                    if pending['name']=='SendMessage':interrupted_task=s['agents'].get(pending['input'].get('to'))
                    s.setdefault('aborted_calls',{})[call]={'object':ref,'task':interrupted_task}
                    return self.halt(s,'Tool execution aborted; preserve state for explicit recovery',pending['task'],kind='INTERRUPTED')
                if self.gradual and typ=='PostToolUseFailure' and self.quota_error(result):
                    return self.pause_quota(s, {'call':call,'error':result})
                obj=object_put(self.base,encoded({'call':call,'response':result,'hook_event':typ}))
                payload={'call':call,'object':obj,'task':pending['task']}
                if pending['name']=='Write' and typ=='PostToolUse':
                    p=Path(pending['input']['file_path']);p=p if p.is_absolute() else self.root/p
                    data=read(p)
                    if data!=pending['input']['content'].encode():raise ValueError('Write bytes do not match request')
                    payload['file_object']=object_put(self.base,data);payload['file']=p.name
                    if p.name.startswith(('draft-','revision-','final-')) and p.suffix=='.md':payload['word_count']=word_count(data)
                receipt=event(self.base,'tool.result',payload);s['last_receipt']=receipt;del s['pending'][call];self.save(s)
                if self.gradual:
                    if typ=='PostToolUse':s.setdefault('tool_corrections',{}).pop(pending['task'] or 'dispatcher',None)
                    elif pending['name']=='Read':
                        if not self.correction_budget(s,pending['task']):return self.halt(s,'Repeated Read failures without a successful step; state preserved',pending['task'])
                        self.save(s)
                        return {'hookSpecificOutput':{'hookEventName':typ,'additionalContext':'Read failed; exact error saved. The batch continues. If the file is absent, do not claim to have read it; create missing own outputs by returning their text. For bad offsets/pages or unavailable files, correct the request or continue with available assigned material.'}}
                    self.save(s)
                if self.manifest.get('source_capture') and pending['name']=='WebFetch' and task:
                    context=self.capture_source(task,s,pending['input']['url'])
                    return {'hookSpecificOutput':{'hookEventName':typ,'additionalContext':context}}
                if self.text_transport and typ=='PostToolUseFailure':
                    if pending['name'] in ('WebSearch','WebFetch'):
                        return {'hookSpecificOutput':{'hookEventName':typ,'additionalContext':'Source request failed; failure saved in receipt '+receipt+'. Record unavailable access or choose another source. Do not claim the failed source was read.'}}
                    return self.halt(s,'Tool failed: '+pending['name']+'. See saved result receipt.',pending['task'])
                if self.text_transport and pending['name'] in ('Agent','SendMessage'):
                    if self.gradual and self.agent_quota_error(result):
                        return self.pause_quota(s,{'call':call,'provider_result_object':obj,'source':'leading Agent API failure notice; status completed is not task completion'})
                    tid=(s['agents'].get(pending['input'].get('to')) if pending['name']=='SendMessage' else next(t['id'] for t in self.tasks.values() if t['agent_name']==pending['input']['subagent_type']))
                    if tid in s.get('staged',{}):
                        staged=json.loads(read(self.base/'.journal/objects'/s['staged'][tid]));self.accept_text(self.tasks[tid],s,staged)
                    if tid not in s['done'] and tid not in s.get('checkpoints',{}) and not s.get('halt') and not s.get('quota_wait'):
                        return self.halt(s,'Worker returned without a sealed result or checkpoint; inspect native record.',tid)
                return {'hookSpecificOutput':{'hookEventName':typ,'additionalContext':'Mechanical save receipt '+receipt+('. Count: '+json.dumps(payload['word_count']) if 'word_count' in payload else '')+'. '+(self.next_action(s) if self.gradual and not task else 'Continue only within the assigned task.')+' Canonical review is pending.'}}
            if typ=='SubagentStop':
                if not task:raise ValueError('missing child binding')
                if task['id'] in s['done']:return {}
                if self.text_transport:
                    if s.get('halt'):return {}
                    try:return self.accept_text(task,s,h)
                    except Exception as e:return self.halt(s,str(e),task['id'])
                if any(p['task']==task['id'] for p in s['pending'].values()):raise ValueError('unresolved tool result; do not advance')
                out=self.base/'tasks'/task['id']/'output';files={}
                for p in sorted(out.iterdir()):
                    if not p.is_file():raise ValueError('output must contain regular files only')
                    files[p.name]=object_put(self.base,read(p))
                missing=[name for name in task['required_outputs'] if name not in files or not read(out/name).strip()]
                if missing:return {'decision':'block','reason':'Save required output files: '+', '.join(missing)}
                for name in files:
                    if name.startswith('final-') and word_count(read(out/name))['word_units']>6000:
                        return {'decision':'block','reason':'Local count exceeds 6000. Save a shorter numbered final and a new final-selection-NNN.json naming it; preserve old files.'} if not any(n.startswith('final-selection-') and n.endswith('.json') for n in files) else self.seal_selected(task,s,files,h)
                return self.seal_selected(task,s,files,h)
            if typ=='Stop':
                if self.text_transport and h.get('last_assistant_message') is not None:
                    text=h['last_assistant_message']
                    if not isinstance(text,str) or not safe_visible(text):return self.halt(s,'Final dispatcher message needs scoped capture review')
                    event(self.base,'dispatcher.final_text',{'object':object_put(self.base,text.encode()),'session_id':session,'source':'Stop hook last_assistant_message; native transcript may lag'})
                try:ref=self.capture_parent(h)
                except Exception as e:
                    if self.text_transport:return self.halt(s,'Parent capture needs repair: '+str(e))
                    raise
                s['last_receipt']=event(self.base,'dispatcher.visible_capture',{'object':ref});self.save(s)
                if self.text_transport:
                    if s.get('quota_wait'):return {}
                    if self.gradual and not s.get('halt') and not s.get('staged') and not s.get('pending') and not s.get('continuing') and len(s['done'])!=len(self.tasks):
                        if s.get('last_auto_continue') != s.get('last_progress') or not s.get('auto_continue_used'):
                            s['last_auto_continue']=s.get('last_progress');s['auto_continue_used']=True;self.save(s)
                            return {'decision':'block','reason':'Continue the finite package: resume the checkpoint worker with SendMessage, otherwise start the next ready task. Do not repeat saved files.'}
                    if s.get('continuing') and not s.get('halt'):return {}
                    if not s.get('halt') and len(s['done'])!=len(self.tasks):
                        return self.halt(s,'Dispatcher stopped before all tasks completed; preserve partial work.',kind='INTERRUPTED')
                    return {}
                summary=self.summary(s)
                if summary['state']!='COMPLETE':
                    return {'decision':'block','reason':'Batch incomplete. Continue ready tasks '+', '.join(summary['ready'])+'. Resume registered partial agents; do not regenerate completed tasks. If provider limit prevents work, report the interruption and wait for the user.'} if not h.get('stop_hook_active') else {}
                return {}
            raise ValueError('unsupported hook event')

    def capture_parent(self,h):
        path=safe(h.get('transcript_path',''))
        if path.name!=h['session_id']+'.jsonl':raise ValueError('parent transcript identity mismatch')
        data=read(path);items=[];gaps=[];read_calls=set()
        if not data.endswith(b'\n'):raise ValueError('parent transcript partial; preserve before completion')
        for n,line in enumerate(data.splitlines(),1):
            r=json.loads(line)
            if r.get('type') not in ('user','assistant') or r.get('isMeta') or r.get('isCompactSummary'):continue
            if r.get('sessionId')!=h['session_id'] or r.get('cwd')!=str(self.root) or r.get('agentId'):
                raise ValueError('parent transcript scope differs')
            m=r.get('message',{});c=m.get('content',[])
            if m.get('role')!=r['type']:raise ValueError('parent role mismatch')
            blocks=[(None,c)] if isinstance(c,str) else list(enumerate(c))
            for index,b in blocks:
                if isinstance(b,dict) and b.get('type') in ('thinking','redacted_thinking'):continue
                if isinstance(b,dict) and b.get('type')=='tool_use' and b.get('name')=='Read':read_calls.add(b.get('id'))
                diagnostic=isinstance(b,dict) and read_eof_diagnostic(b,read_calls)
                if not safe_visible(b) and not diagnostic:gaps.append({'line':n,'reason':'blocked visible fragment'});continue
                if isinstance(b,dict) and b.get('type') not in ('text','tool_use','tool_result'):
                    gaps.append({'line':n,'reason':'unsupported visible fragment'});continue
                key=('message','content') if index is None else ('message','content',index)
                items.append({'line':n,'index':index,'role':r['type'],'object':object_put(self.base,fragments(line)[key]),'timestamp':r.get('timestamp','UNKNOWN'),'model':m.get('model','UNKNOWN'),'effort':r.get('effort','UNKNOWN')})
        return object_put(self.base,encoded({'session_id':h['session_id'],'source_sha256':digest(data),'fragments':items,'gaps':gaps,'status':'INCOMPLETE' if gaps else 'BOUNDED_COMPLETE','boundary':'Selected exact parent visible fragments; hidden/internal envelopes excluded; no UI mode inference.'}))

    def partial_result(self,text,begin,decoder):
        """Recover only fully decoded file strings, never complete a broken envelope."""
        pos=begin+1;header={};files={}
        def ws(pos):
            while pos<len(text) and text[pos].isspace():pos+=1
            return pos
        try:
            while True:
                key,pos=decoder.raw_decode(text,ws(pos));pos=ws(pos)
                if not isinstance(key,str) or pos>=len(text) or text[pos]!=':':return None
                pos=ws(pos+1)
                if key in header:raise ValueError('duplicate result key')
                if key=='files':
                    if header.get('protocol')!='claude-batch-result.v1' and not (self.gradual and 'protocol' not in header):return None
                    if header.get('status') not in ('complete','checkpoint') and not (self.gradual and 'status' not in header):return None
                    if pos>=len(text) or text[pos]!='{':return None
                    pos+=1
                    while True:
                        name,pos=decoder.raw_decode(text,ws(pos));pos=ws(pos)
                        if not isinstance(name,str) or pos>=len(text) or text[pos]!=':':return None
                        if name in files:raise ValueError('duplicate result key')
                        pos=ws(pos+1)
                        if pos>=len(text) or text[pos]!='"':return None
                        try:content,end=decoder.raw_decode(text,pos)
                        except json.JSONDecodeError:
                            if not files:return None
                            return {**header,'status':'checkpoint','claimed_status':header.get('status','MISSING'),
                                    'files':files,'transport_recovery':'Only complete file strings retained; incomplete file and envelope preserved in native evidence.'}
                        if not isinstance(content,str):return None
                        files[name]=content;pos=ws(end)
                        if pos>=len(text) or text[pos]!=',':return None
                        pos+=1
                value,pos=decoder.raw_decode(text,pos);header[key]=value;pos=ws(pos)
                if pos>=len(text) or text[pos]!=',':return None
                pos+=1
        except json.JSONDecodeError:return None

    def result_envelope(self,text,task):
        def pairs(items):
            result={}
            for k,v in items:
                if k in result:
                    if self.gradual:raise ResultCorrection('Duplicate JSON key in the previous response. Return one unambiguous result object with each key once. Original response preserved; no ambiguous files selected.')
                    raise ValueError('duplicate result key')
                result[k]=v
            return result
        # Preserve the full native message elsewhere. Decode the one result object
        # without rewriting any file strings; prose/fences around it are harmless.
        decoder=json.JSONDecoder(object_pairs_hook=pairs)
        candidates=[];partials=[];cursor=0
        while True:
            begin=text.find('{',cursor)
            if begin<0:break
            try:value,end=decoder.raw_decode(text,begin)
            except json.JSONDecodeError:
                partial=self.partial_result(text,begin,decoder)
                if partial:partials.append(partial)
                cursor=begin+1;continue
            cursor=end
            if isinstance(value,dict) and (value.get('protocol')=='claude-batch-result.v1' or self.gradual and isinstance(value.get('files'),dict)):
                candidates.append(value)
        if not candidates and len(partials)==1:candidates=partials
        if len(candidates)!=1:
            if self.gradual:
                raise ResultCorrection('Your previous response is preserved, but contains '+str(len(candidates))+' result objects. Return exactly one result JSON with the actual file text, without a template or example. No files from the ambiguous response were selected or saved as outputs. Reuse your existing work; do not restart research.')
            raise ValueError('expected one unambiguous result object, found '+str(len(candidates)))
        result=candidates[0]
        if not isinstance(result,dict):raise ValueError('result must be an object')
        if self.gradual:
            # Native session/agent binding establishes identity before materializing.
            # Explicit conflicting identities are still errors; absent labels are not.
            if 'protocol' in result and result['protocol']!='claude-batch-result.v1' or 'task_id' in result and result['task_id']!=task['id']:raise ValueError('result identity differs')
            claimed=result.get('status');label=claimed.strip().lower() if isinstance(claimed,str) else None
            aliases={'complete':'complete','completed':'complete','done':'complete','checkpoint':'checkpoint','partial':'checkpoint','in_progress':'checkpoint','blocked':'blocked','failed':'blocked','error':'blocked'}
            normalized=aliases.get(label,'checkpoint')
            origin='missing' if claimed is None else 'worker' if label in aliases else 'unrecognized'
            result={**result,'protocol':'claude-batch-result.v1','task_id':task['id'],'status':normalized,
                    '_transport':{'status_source':origin,'claimed_status':claimed,'identity_source':'native-bound worker; explicit labels checked'},'files':result.get('files',{})}
            if not isinstance(result['files'],dict):raise ResultCorrection('Return files as a filename-to-text mapping; previous response preserved')
        else:
            if result.get('protocol')!='claude-batch-result.v1' or result.get('task_id')!=task['id']:raise ValueError('result identity differs')
            if result.get('status') not in ('complete','checkpoint','blocked'):raise ValueError('unknown result status')
            if not isinstance(result.get('files'),dict):raise ValueError('result files must be a mapping')
        for name,content in result['files'].items():
            if not re.fullmatch(r'[a-z][a-z0-9-]*\.(md|json|txt)',name) or not isinstance(content,str):raise ValueError('unsafe text output name/content')
            if len(content.encode())>MAX or not safe_visible(content):raise ValueError('output needs scoped review')
        return result

    def accept_text(self,task,s,h):
        if any(p['task']==task['id'] for p in s['pending'].values()):raise ValueError('unresolved child tool receipt')
        if isinstance(h.get('last_assistant_message'),str) and safe_visible(h['last_assistant_message']):
            selected={k:h[k] for k in ('session_id','agent_id','transcript_path','agent_transcript_path','last_assistant_message')}
            ref=object_put(self.base,encoded(selected));s.setdefault('staged',{})[task['id']]=ref
            event(self.base,'text.result.received',{'task':task['id'],'object':ref});self.save(s)
        try:native_object,native_files=self.native_configuration(task,h)
        except (ValueError,FileNotFoundError) as e:
            if isinstance(e,FileNotFoundError) or str(e) in ('hook/native result differs','native child still changing or partial','no native assistant result'):
                return {'systemMessage':'Result text saved; awaiting native transcript flush. No dependent task may start yet.'}
            raise
        native=json.loads(read(self.base/'.journal/objects'/native_object))
        result=native['result'];out=self.base/'tasks'/task['id']/'output'
        if s.get('checkpoints',{}).get(task['id'],{}).get('native_object')==native_object:
            s.setdefault('staged',{}).pop(task['id'],None);self.save(s);return {}
        # Journal exact content before materializing. A retry may repair only identical files.
        files=native['native_files']
        event(self.base,'text.result.prepared',{'task':task['id'],'native_object':native_object,'files':files,'status':result['status']})
        for name,sha in files.items():
            data=read(self.base/'.journal/objects'/sha);p=safe(out/name)
            if p.exists() and read(p)!=data:raise ValueError('returned text would overwrite previous output')
            if not p.exists():atomic(p,data)
        actual={p.name:digest(read(p)) for p in out.iterdir()}
        if actual!=files:raise ValueError('unproven extra output file')
        s.setdefault('staged',{}).pop(task['id'],None);s.setdefault('continuing',{}).pop(task['id'],None)
        if self.gradual and result.get('quota_wait'):return self.pause_quota(s, {'native_object':native_object,'source':'native provider error'})
        if result['status']=='blocked':return self.halt(s,result.get('reason','Worker reported a block'),task['id'])
        if self.gradual and result.get('_transport',{}).get('status_source')=='missing':
            result={**result,'status':'complete' if all(name in files and read(out/name).strip() for name in task['required_outputs']) else 'checkpoint'}
            event(self.base,'task.transport_status_derived',{'task':task['id'],'native_object':native_object,'status':result['status'],'source':'local required-file checks; worker status absent or null, not a model claim'})
        if self.gradual and result['status']=='complete' and any(name not in files or not read(out/name).strip() for name in task['required_outputs']):
            result={**result,'status':'checkpoint'}
        if result['status']=='checkpoint' and not self.gradual:return self.checkpoint(task,s,h,native_object,files)
        if result['status']=='complete' and any(name not in files or not read(out/name).strip() for name in task['required_outputs']):raise ValueError('complete result missing required files')
        counts={name:word_count(read(out/name)) for name in files if name.startswith(('draft-','revision-','final-')) and name.endswith('.md')}
        selections=sorted(n for n in files if re.fullmatch(r'final-selection-[0-9]{3}\.json',n))
        finals=[n for n in counts if n.startswith('final-')]
        if selections:
            try:
                selection=json.loads(read(out/selections[-1]));selected=selection.get('file') if isinstance(selection,dict) else None
                if self.gradual and isinstance(selection,dict):
                    choices=[selection[key] for key in ('file','selected_final','filename') if key in selection]
                    selected=choices[0] if choices and all(isinstance(v,str) and v==choices[0] for v in choices) else None
            except (ValueError,TypeError):selected=None
            if selected not in finals:
                if self.gradual:return self.checkpoint(task,s,h,native_object,files,'Return a new numbered final-selection-NNN.json naming an existing final manuscript. Preserve all old files.')
                raise ValueError('invalid final selection')
            finals=[selected]
        if any(counts[n]['word_units']>6000 for n in finals):
            if self.gradual:return self.checkpoint(task,s,h,native_object,files,'Final exceeds 6000 measured word units. Return a shorter final under a NEW numbered filename, then a NEW final-selection-NNN.json naming it. Preserve all old files.')
            raise ValueError('final exceeds 6000 measured word units; preserved for correction')
        if result['status']=='checkpoint':
            correction=result.get('format_correction')
            if result.get('_transport',{}).get('status_source')=='unrecognized':correction='Files saved. Return the remaining work, using checkpoint while work remains and complete when finished. Do not repeat saved files.'
            return self.checkpoint(task,s,h,native_object,files,correction)
        receipt=event(self.base,'task.sealed',{'task':task['id'],'agent_id':h['agent_id'],'session_id':h['session_id'],'native_object':native_object,'files':files,'counts':counts,'requested':task['configuration'],'source':'exact native assistant text; mechanical JSON decoding; no AI rewrite'})
        s['last_progress']=receipt
        s['done'][task['id']]={'files':files,'receipt':receipt,'agent_id':h['agent_id']};s.setdefault('checkpoints',{}).pop(task['id'],None);s['last_receipt']=receipt;self.save(s);return {}

    def checkpoint(self,task,s,h,native_object,files,correction=None):
        previous=s.setdefault('checkpoints',{}).get(task['id'])
        count=previous.get('count',0)+1 if previous else 1
        if self.gradual:
            progress=files != (previous or {}).get('files',{})
            stalls=0 if progress else (previous or {}).get('stalls',0)+1
            if stalls>2 or count>max(12,len(task['required_outputs'])*4):return self.halt(s,'No further output after bounded continuation attempts; partial files preserved',task['id'])
            if progress:
                s['last_progress']=native_object
                s.setdefault('tool_corrections',{}).pop(task['id'],None)
        elif count>3:return self.halt(s,'Checkpoint retry budget exhausted',task['id'])
        s['checkpoints'][task['id']]={'agent_id':h['agent_id'],'native_object':native_object,'files':files,'count':count,**({'stalls':stalls} if self.gradual else {})}
        if correction:s['checkpoints'][task['id']]['correction']=correction
        s['last_receipt']=event(self.base,'task.checkpoint',{'task':task['id'],**s['checkpoints'][task['id']]});self.save(s);return {}

    def native_configuration(self, task, h):
        # Exact child path from SubagentStop, bounded to this parent's native directory.
        parent=safe(h.get('transcript_path',''))
        child=safe(h.get('agent_transcript_path',''))
        sid=h['session_id'];aid=h['agent_id']
        if parent.name != sid+'.jsonl' or child.parent != parent.parent/sid/'subagents' or child.name != 'agent-'+aid+'.jsonl':
            raise ValueError('unsupported native child path; capability verification required')
        before=child.stat()
        if before.st_size>64*1024*1024:raise ValueError('native child size exceeds bounded capture')
        with child.open('rb') as f:raw=f.read(64*1024*1024+1)
        if child.stat().st_mtime_ns!=before.st_mtime_ns or not raw.endswith(b'\n'):raise ValueError('native child still changing or partial')
        observed=[];writes={};results={};visible=[];gaps=[];originals=[];assistant_texts=[];provider_errors=[];last_text_provider_error=False;read_calls=set();diagnostics=[];text_messages=[];tool_messages=set()
        for n,line in enumerate(raw.splitlines(),1):
            r=json.loads(line)
            if r.get('type') not in ('assistant','user') or r.get('isMeta') or r.get('isCompactSummary'):continue
            if r.get('sessionId')!=sid or r.get('cwd')!=str(self.root) or r.get('agentId')!=aid:
                raise ValueError('child native identity/cwd mismatch')
            m=r.get('message',{});content=m.get('content',[])
            if m.get('role')!=r['type']:raise ValueError('native role mismatch')
            provider_error = (r.get('isApiErrorMessage') is True and m.get('model')=='<synthetic>' and bool(r.get('error')))
            if provider_error:
                provider_errors.append({'source_line':n,'error':r['error'],'timestamp':r.get('timestamp','UNKNOWN'),'model_label':'<synthetic>'})
            elif r['type']=='assistant':observed.append({'model':m.get('model','UNKNOWN'),'effort':r.get('effort','UNKNOWN'),'source_line':n})
            if r['type']=='assistant':
                if m.get('id') and (m.get('stop_reason')=='tool_use' or isinstance(content,list) and any(b.get('type')=='tool_use' for b in content)):
                    tool_messages.add(m['id'])
                text=content if isinstance(content,str) else '\n'.join(b.get('text','') for b in content if b.get('type')=='text')
                if text:
                    assistant_texts.append(text);last_text_provider_error=provider_error
                    text_messages.append((text,m.get('id'),m.get('stop_reason'),n))
            if isinstance(content,str):
                if safe_visible(content):
                    visible.append({'line':n,'role':r['type'],'text':content})
                    originals.append({'line':n,'object':object_put(self.base,fragments(line)[('message','content')])})
                else:gaps.append({'line':n,'reason':'blocked visible message'})
            elif isinstance(content,list):
                for index,b in enumerate(content):
                    if b.get('type') in ('thinking','redacted_thinking'):continue
                    if b.get('type')=='tool_use' and b.get('name')=='Read':read_calls.add(b.get('id'))
                    diagnostic=read_eof_diagnostic(b,read_calls)
                    if not safe_visible(b) and not diagnostic:gaps.append({'line':n,'reason':'blocked visible block'});continue
                    if diagnostic:diagnostics.append({'source_line':n,'tool_use_id':b['tool_use_id'],'kind':'read_offset_beyond_eof','source':'exact visible provider tool diagnostic; not an instruction'})
                    originals.append({'line':n,'index':index,'object':object_put(self.base,fragments(line)[('message','content',index)])})
                    if b.get('type')=='text':visible.append({'line':n,'role':r['type'],'text':b.get('text','')})
                    elif b.get('type')=='tool_use' and b.get('name')=='Write':writes[b['id']]=b.get('input',{})
                    elif b.get('type')=='tool_result' and not b.get('is_error'):results[b.get('tool_use_id')]=b.get('content')
                    elif b.get('type') not in ('tool_use','tool_result'):gaps.append({'line':n,'reason':'unsupported visible block'})
        config=task['configuration']
        if not observed or any(o['model']!=config['model'] or o['effort']!=config['effort'] for o in observed):
            raise ValueError('observed child model/effort mismatch or unavailable; stop batch, do not substitute')
        if gaps:raise ValueError('native visible capture has gaps; Codex review required')
        if self.text_transport:
            if not assistant_texts:raise ValueError('no native assistant result')
            if h.get('last_assistant_message') is not None and h['last_assistant_message']!=assistant_texts[-1]:raise ValueError('hook/native result differs')
            try:result=self.result_envelope(assistant_texts[-1],task)
            except ValueError as e:
                if not self.gradual or not (isinstance(e,ResultCorrection) or str(e).startswith('expected one unambiguous result object, found 0')):raise
                # Exact original text remains in visible/original_fragments. Do not
                # invent any file bytes or claim the model emitted this receipt.
                result={'protocol':'claude-batch-result.v1','task_id':task['id'],'status':'checkpoint','files':{},'transport_incomplete':True}
                if isinstance(e,ResultCorrection):result['format_correction']=str(e)
                if last_text_provider_error and provider_errors and self.quota_error(provider_errors[-1]):result['quota_wait']=True
            # A JSON example in commentary before a tool call is not a delivered
            # result. Native message identity joins separately streamed text/tool
            # blocks. Preserve those original fragments, but do not materialize them.
            delivery_texts=[text for text,mid,stop,n in text_messages if mid not in tool_messages and stop!='tool_use']
            if text_messages[-1][1] in tool_messages or text_messages[-1][2]=='tool_use':
                if not self.gradual:raise ValueError('no terminal native assistant result')
                result={'protocol':'claude-batch-result.v1','task_id':task['id'],'status':'checkpoint','files':{},'transport_incomplete':True}
            native_files={} 
            for text in delivery_texts:
                try:part=self.result_envelope(text,task)
                except (ValueError,TypeError):continue
                for name,content in part['files'].items():
                    sha=object_put(self.base,content.encode())
                    if name in native_files and native_files[name]!=sha:raise ValueError('native output version overwritten; use numbered names')
                    native_files[name]=sha
            obj=object_put(self.base,encoded({'format':'selected-native-text-result.v1','session_id':sid,'agent_id':aid,'models':observed,'provider_errors':provider_errors,'messages':visible,'original_fragments':originals,'native_files':native_files,'result':result,**({'tool_diagnostics':diagnostics} if diagnostics else {}),'source_sha256':digest(raw),'source_line_count':len(raw.splitlines()),'boundary':'Exact selected native visible fragments; decoded file strings mechanically materialized; hidden/internal envelopes excluded.'}))
            return obj,native_files
        native_files={}
        for call,args in writes.items():
            if call not in results:continue
            path=Path(args.get('file_path',''));path=path if path.is_absolute() else self.root/path
            if path.parent!=self.base/'tasks'/task['id']/'output':raise ValueError('native out-of-scope write')
            if not isinstance(results[call],str) or not results[call].startswith('File created successfully at: '+str(path)):raise ValueError('unknown native Write success format')
            native_files[path.name]=digest(args['content'].encode())
        obj=object_put(self.base,encoded({'format':'selected-native-visible-normalized.v1','session_id':sid,'agent_id':aid,'models':observed,'provider_errors':provider_errors,'messages':visible,'original_fragments':originals,'native_files':native_files,'source_sha256':digest(raw),'source_line_count':len(raw.splitlines()),'boundary':'Normalized selected visible text and metadata; original envelopes/hidden reasoning excluded. Exact tool requests/results and file bytes are in hook receipts. Full canonical review pending.'}))
        return obj,native_files

    def seal_selected(self,task,s,files,h):
        out=self.base/'tasks'/task['id']/'output'
        selections=sorted(n for n in files if re.fullmatch(r'final-selection-[0-9]{3}\.json',n))
        if selections:
            selected=json.loads(read(out/selections[-1])).get('file')
            if selected not in files or not selected.startswith('final-') or not selected.endswith('.md'):raise ValueError('invalid final selection')
            if word_count(read(out/selected))['word_units']>6000:return {'decision':'block','reason':'Selected final still over 6000 word units. Preserve old files; save new numbered final-selection record.'}
        saved={}
        for p in sorted((self.base/'.journal/events').glob('*.json')):
            e=json.loads(read(p));pl=e['payload']
            if e['kind']=='tool.result' and pl.get('task')==task['id'] and 'file' in pl:saved[pl['file']]=pl['file_object']
        if saved!=files:raise ValueError('every output needs a durable Write result receipt')
        native_object,native_files=self.native_configuration(task,h)
        if native_files!=files:raise ValueError('native Write evidence does not match every output')
        receipt=event(self.base,'task.sealed',{'native_object':native_object,'task':task['id'],'agent_id':h['agent_id'],'session_id':h['session_id'],'files':files,'requested':task['configuration'],'source':'hooks; native verification pending'})
        s['last_progress']=receipt
        s['done'][task['id']]={'files':files,'receipt':receipt,'agent_id':h['agent_id']};s['last_receipt']=receipt;self.save(s)
        return {}


def main():
    base=Path(__file__).resolve().parent
    if len(sys.argv)>1 and sys.argv[1]=='status':
        b=Batch(base)
        with b.locked():b.check();s=b.state();b.verify_done(s);print(json.dumps(b.summary(s)))
        return
    try:
        data=sys.stdin.buffer.read(MAX+1)
        if len(data)>MAX:raise ValueError('hook input exceeds bound')
        h=json.loads(data)
        if not isinstance(h,dict):raise ValueError('hook object required')
    except Exception as e:
        print(str(e),file=sys.stderr);sys.exit(2)
    try:
        result=Batch(base).handle(h)
    except Exception as e:
        if h.get('hook_event_name')=='PreToolUse':result={'hookSpecificOutput':{'hookEventName':'PreToolUse','permissionDecision':'deny','permissionDecisionReason':str(e)}}
        else:
            print(str(e),file=sys.stderr);sys.exit(2)
    print(json.dumps(result,ensure_ascii=False))

if __name__=='__main__':main()
