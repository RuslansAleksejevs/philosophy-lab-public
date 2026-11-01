#!/usr/bin/env python3
"""Standalone, read-only verification of the frozen 2026-10-31 log supplements.

Only Python's standard library and files inside this repository are used. No
native session database, canonical archive, Git, network or model is accessed.
The approved manifests are pinned below; future editions need a new verifier.
"""
from pathlib import Path, PurePosixPath
import argparse
import collections
import hashlib
import json
import math
import re
import sys
import tarfile

PREFIX = 'logs/updates/20261031-complete-visible'
LATE = 'logs/updates/20261031-late-receipts'
BASE = '6f3748923631d43945a9ea03909e56b867a5ef0c'
FROZEN = {
    PREFIX + '/MANIFEST.json': '9ee62042209c8a67e8a8e1546a0ab70e28fabff28dd17a3d32e7341aae2373e4',
    LATE + '/MANIFEST.json': 'dea4d87456cd6a2625f703ec21ed803ea21626eaaa0938906eac9dd1da80a49b',
}
HEX = re.compile(r'[a-f0-9]{64}\Z')
PATTERNS = tuple(re.compile(p) for p in (
    r'-----BEGIN (?:RSA |EC |OPENSSH |DSA |ENCRYPTED )?PRIVATE KEY-----[\s\S]*?(?:-----END (?:RSA |EC |OPENSSH |DSA |ENCRYPTED )?PRIVATE KEY-----|\Z)',
    r'\bsk-[A-Za-z0-9_-]{20,}\b',
    r'\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,})\b',
    r'\bxox[baprs]-[A-Za-z0-9-]{20,}\b', r'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b',
    r'(?i)\b(?:authorization\s*:\s*bearer\s+)[A-Za-z0-9._~+/-]{20,}',
    r'(?i)\b(?:api[_-]?key|client[_-]?secret|access[_-]?token|password)["\x27]?\s*[:=]\s*["\x27][A-Za-z0-9_./+~=-]{20,}["\x27]',
))
SENSITIVE_KEYS = {'api_key', 'apikey', 'api-key', 'client_secret', 'client-secret',
                  'access_token', 'access-token', 'password', 'private_key'}
NATIVE_FIELDS = {'role','phase','text','text_blocks','turn_id','observed_model','attachment_gaps',
                 'source_line','source_timestamp','source_line_sha256','text_sha256','retain_original',
                 'session_id','origin','transformation'}
VIEW_FIELDS = {'role','phase','timestamp','recorded_at','source_line','raw_sha256','event_id',
               'model','turn_id','origin','text','text_sha256','source_view_sha256'}
TRANSFORMS = {'omit_top_display_metadata','omit_completed_status','omit_content_item_provenance_metadata',
              'omit_empty_annotations','omit_empty_logprobs','visible_text_and_allowlisted_metadata_only'}


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def strict_json(raw):
    def pairs(items):
        out = {}
        for key, value in items:
            require(key not in out, 'Duplicate JSON key')
            out[key] = value
        return out
    def bad(_):
        raise ValueError('Non-finite JSON value')
    def floating(text):
        value = float(text)
        require(math.isfinite(value), 'Non-finite JSON value')
        return value
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=bad, parse_float=floating)


def canonical(value):
    # Type-sensitive object equality, without conflating true with integer 1.
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)


def safe_name(name):
    require(isinstance(name, str) and bool(name), 'Missing relative path')
    p = PurePosixPath(name)
    require(str(p) == name and not p.is_absolute() and '..' not in p.parts
            and '.git' not in p.parts and '\0' not in name and '\\' not in name, 'Unsafe relative path')
    return name


def credential(value, depth=0):
    if isinstance(value, dict):
        return any((str(k).lower() in SENSITIVE_KEYS and isinstance(v,str) and len(v)>=8
                    and v.lower() not in {'redacted','unknown','placeholder','your_api_key','your_password'})
                   or credential(v,depth) for k,v in value.items())
    if isinstance(value, list):
        return any(credential(x,depth) for x in value)
    if not isinstance(value, str):
        return False
    if any(p.search(value) for p in PATTERNS):
        return True
    if depth < 3 and value.lstrip().startswith(('{','[','"')):
        try:
            return credential(strict_json(value),depth+1)
        except (ValueError,RecursionError):
            pass
    return False


def forbidden(value):
    if isinstance(value,dict):
        if {'timestamp','type','payload'} <= set(value):
            return True
        if set(value) & {'encrypted_content','base_instructions','system_prompt','developer_prompt'}:
            return True
        if isinstance(value.get('type'),str) and value['type'] in {'reasoning','thinking','redacted_thinking'}:
            return True
        return any(forbidden(v) for v in value.values())
    return isinstance(value,list) and any(forbidden(v) for v in value)


def private_check(value, label, *, hidden=False):
    require(not credential(value), 'Credential-shaped content: ' + label)
    if hidden:
        require(not forbidden(value), 'Internal/native envelope: ' + label)


def key(message):
    require(isinstance(message,dict) and isinstance(message.get('text'),str), 'Invalid message object')
    require(type(message.get('source_line')) is int and message['source_line'] >= 1, 'Invalid source line')
    return message['source_line'],message.get('role'),sha(message['text'].encode())


def model_check(value):
    require(isinstance(value,dict), 'Invalid model observation')
    if value.get('status') == 'unknown':
        require(set(value) <= {'status','reason'} and isinstance(value.get('reason'),str), 'Unknown model envelope')
        return
    require(value.get('status') == 'known' and set(value) <= {'status','value','source','source_line','boundary'}, 'Unsupported model observation')
    model = value.get('value')
    require(isinstance(model,dict) and set(model) == {'model','reasoning_effort'}, 'Model envelope is not scalar-only')
    require(isinstance(model['model'],str) and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._:/-]{0,199}',model['model']), 'Invalid model label')
    require(model['reasoning_effort'] in {None,'none','minimal','low','medium','high','xhigh','max','ultra'}, 'Invalid effort')
    require(type(value.get('source_line')) is int and value['source_line'] > 0, 'Invalid model source line')


def new_message(message, sid, view_only):
    identity = key(message)
    require(message.get('text_sha256') == identity[2], 'New message text hash mismatch')
    require(message['role'] in {'user','assistant'}, 'Nonvisible message role')
    if message['role'] == 'assistant':
        require(message.get('phase') in {'commentary','final','final_answer'}, 'Hidden assistant phase')
    private_check(message, sid + ':' + str(message['source_line']), hidden=True)
    if 'source_view_sha256' in message:
        require(set(message) == VIEW_FIELDS, 'Unreviewed current-view message metadata')
        expected = view_only.get((sid,*identity))
        require(expected is not None and expected.get('text_sha256') == identity[2]
                and message['raw_sha256'] == expected['raw_sha256']
                and message['event_id'] == expected['event_id'], 'Unbound view-only addition')
        require(HEX.fullmatch(message['source_view_sha256']) is not None, 'Invalid view source hash')
        model_check(message['model'])
        return 'view_only'
    require(set(message) == NATIVE_FIELDS, 'Unreviewed native-fragment metadata')
    require(message['session_id'] == sid and message['retain_original'] is False, 'Native envelope/origin mismatch')
    require(HEX.fullmatch(message['source_line_sha256']) is not None, 'Invalid native source hash')
    require(isinstance(message['text_blocks'],list) and all(isinstance(x,str) for x in message['text_blocks'])
            and '\n'.join(message['text_blocks']) == message['text'], 'Text blocks differ from visible text')
    require(isinstance(message['transformation'],list) and bool(message['transformation'])
            and set(message['transformation']) <= TRANSFORMS, 'Unknown fragment transformation')
    require(message['origin'] == ('USER_ROLE_INPUT' if message['role']=='user' else 'AI_VISIBLE_RESPONSE'), 'Mislabelled message origin')
    require(message['attachment_gaps'] == [], 'Unexpected attachment payload')
    model_check(message['observed_model'])
    return 'native'


class Verifier:
    def __init__(self, root):
        self.root = Path(root).absolute()
        self.doc_cache = {}
        self.member_cache = {}
        self.verified_bundle_members = 0

    def path(self, rel):
        path = self.root / safe_name(rel)
        require(not any(p.is_symlink() for p in (path,*path.parents)), 'Symlink path: '+rel)
        require(path.is_file(), 'Missing file: '+rel)
        return path

    def read(self, rel, descriptor=None):
        path = self.path(rel)
        if descriptor is not None:
            require(path.stat().st_size == descriptor['bytes'], 'File byte count: '+rel)
        raw = path.read_bytes()
        if descriptor is not None:
            require(len(raw) == descriptor['bytes'] and sha(raw) == descriptor['sha256'], 'File hash: '+rel)
        return raw

    def load(self, rel):
        return strict_json(self.read(rel))

    def bundle(self, descriptor, wanted=(), *, new=False):
        rel = descriptor['path']
        expected = {}
        for row in descriptor['members']:
            name = safe_name(row['path'])
            require(name not in expected, 'Duplicate member descriptor: '+rel)
            require(type(row['bytes']) is int and row['bytes'] >= 0, 'Invalid member size')
            expected[name] = row
        self.read(rel,descriptor)
        with tarfile.open(self.path(rel),'r:gz') as tar:
            for member in tar:
                name = safe_name(member.name)
                require(member.isfile() and not member.issym() and not member.islnk(), 'Nonregular archive member: '+rel)
                row = expected.pop(name,None)
                require(row is not None and member.size == row['bytes'], 'Unexpected/duplicate archive member: '+rel)
                stream = tar.extractfile(member)
                raw = stream.read(row['bytes']+1)
                require(len(raw)==row['bytes'] and sha(raw)==row['sha256'], 'Archive member hash: '+rel+'!'+name)
                self.verified_bundle_members += 1
                if name in wanted:
                    self.member_cache[(rel,name)] = raw
                if new:
                    if name.endswith('.json'):
                        private_check(strict_json(raw),rel+'!'+name,hidden=True)
                    elif name.endswith('.jsonl'):
                        private_check([strict_json(x) for x in raw.splitlines() if x.strip()],rel+'!'+name,hidden=True)
                    else:
                        private_check(raw.decode('utf-8'),rel+'!'+name)
        require(not expected, 'Missing archive members: '+rel)

    def conversations(self,index):
        docs = {}
        for row in index['sessions']:
            sid = row['session_id']
            require(sid not in docs, 'Duplicate indexed session')
            if row.get('conversation_archive'):
                raw = self.member_cache[('logs/'+safe_name(row['conversation_archive']),safe_name(row['conversation_member']))]
            else:
                raw = self.read('logs/'+safe_name(row['conversation']))
            require(sha(raw)==row['conversation_sha256'], 'Indexed conversation hash: '+sid)
            if row['conversation_sha256'] not in self.doc_cache:
                self.doc_cache[row['conversation_sha256']] = strict_json(raw)
            doc = self.doc_cache[row['conversation_sha256']]
            require(doc['session']['session_id']==sid and isinstance(doc['messages'],list), 'Conversation session mismatch')
            docs[sid] = doc
        return docs

    def run(self):
        for name,digest in FROZEN.items():
            require(sha(self.read(name))==digest, 'Approved supplement manifest changed: '+name)
        supplement = self.load(PREFIX+'/MANIFEST.json')
        late = self.load(LATE+'/MANIFEST.json')
        hview = self.load('evidence/repository-audit/20261031/HISTORICAL_VIEW.json')
        require(hview['base_commit']==BASE, 'Historical baseline commit mismatch')
        historical = {}
        for row in hview['files']:
            name = safe_name(row['path'])
            require(name not in historical, 'Duplicate historical path')
            require(row['historical_path']=='evidence/repository-audit/20261031/before/'+name+'.source', 'Unexpected historical location')
            historical[name] = self.read(row['historical_path'],row)
        require({'logs/index.json','logs/bundles/manifest.json'} <= set(historical), 'Historical log indices missing')
        prior_raw = self.read(PREFIX+'/prior-index.json')
        require(prior_raw == historical['logs/index.json'] and sha(prior_raw)==supplement['old_repository_index_sha256'], 'Historical index changed')
        oldindex,current = strict_json(prior_raw),self.load('logs/index.json')
        oldbundles,newbundles = strict_json(historical['logs/bundles/manifest.json']),self.load('logs/bundles/manifest.json')
        wanted = collections.defaultdict(set)
        for index in (oldindex,current):
            for row in index['sessions']:
                if row.get('conversation_archive'):
                    wanted['logs/'+safe_name(row['conversation_archive'])].add(safe_name(row['conversation_member']))
        tools = self.load(PREFIX+'/reviewed-codex-tools.json')
        for row in tools['records']:
            wanted['logs/'+tools['bundle']].add(safe_name(row['member']))
        oldmap = {x['path']:x for x in oldbundles['bundles']}
        newmap = {x['path']:x for x in newbundles['bundles']}
        additions = {x['path']:x for x in supplement['new_bundles']}
        require(len(oldmap)==32 and len(newmap)==len(newbundles['bundles'])==36 and len(additions)==4, 'Bundle inventory changed')
        require(set(newmap)==set(oldmap)|set(additions), 'Unexpected bundle paths')
        for name,row in oldmap.items():
            require(canonical(newmap[name])==canonical(row), 'Historical bundle descriptor changed')
        for name,row in additions.items():
            require(canonical(newmap[name])==canonical(row), 'New bundle descriptor changed')
        for name,row in newmap.items():
            descriptor = dict(row,path='logs/'+name)
            self.bundle(descriptor,wanted[descriptor['path']],new=name in additions)
        require(set(wanted)<=set('logs/'+p for p in newmap), 'Index points to unbound archive')
        olddocs,newdocs = self.conversations(oldindex),self.conversations(current)
        require(set(olddocs)<=set(newdocs) and len(newdocs)==3384, 'Historical session lost')
        union = self.load(PREFIX+'/union-plan.json')
        view_only = {(x['session_id'],x['source_line'],x['role'],x['text_sha256']):x for x in union['safe_current_view_only_messages']}
        require(len(view_only)==10, 'View-only union changed')
        old_count,new_count = 0,0
        kinds = collections.Counter()
        for sid,doc in newdocs.items():
            messages = doc['messages'];lookup = {key(x):x for x in messages}
            require(len(lookup)==len(messages), 'Duplicate current message')
            previous = olddocs.get(sid,{}).get('messages',[])
            prior = {key(x):x for x in previous}
            require(len(prior)==len(previous), 'Duplicate historical message')
            for identity,m in prior.items():
                require(identity in lookup and canonical(lookup[identity])==canonical(m), 'Historical message object changed: '+sid)
                old_count += 1
            line_roles = {(x['source_line'],x['role']) for x in messages}
            require(len(line_roles)==len(messages), 'Conflicting message source identity')
            for identity in set(lookup)-set(prior):
                kinds[new_message(lookup[identity],sid,view_only)] += 1
                new_count += 1
        require((old_count,new_count)==(13880,1059) and kinds=={'native':1049,'view_only':10}, 'Message union count mismatch')
        require(current['message_count']==14939, 'Current index message count mismatch')
        files = {}
        for row in supplement['files']:
            name = safe_name(row['path']);require(name not in files,'Duplicate supplement path');files[name]=row
            require(name.startswith(PREFIX+'/') or name in {'logs/index.json','logs/bundles/manifest.json'},'Supplement scope escape')
            raw = self.read(name,row)
            if name.endswith('.json'):private_check(strict_json(raw),name)
            elif name.endswith(('.md','.txt')):private_check(raw.decode('utf-8'),name)
        require(len(files)==225,'Supplement file count mismatch')
        tool_records = set()
        for row in tools['records']:
            identity = (row['session_id'],row['source_line'],row['source_record_sha256'])
            require(identity not in tool_records,'Duplicate reviewed tool');tool_records.add(identity)
            value = strict_json(self.member_cache[('logs/'+tools['bundle'],row['member'])])
            require(all(value[k]==row[k] for k in ['session_id','source_line','source_record_sha256','canonical_event_id']), 'Reviewed tool index mismatch')
            require(set(value)=={'session_id','source_line','source_timestamp','canonical_event_id','source_record_sha256','scope','visible_tool'}, 'Tool native envelope exported')
            require(HEX.fullmatch(row['source_record_sha256']) is not None,'Invalid tool source hash')
            require(value['visible_tool']['type'] in {'function_call','custom_tool_call','function_call_output','custom_tool_call_output'},'Unexpected reviewed tool type')
        require(len(tool_records)==1938,'Reviewed tool count mismatch')
        claude = self.load(PREFIX+'/accepted-claude-fragments.json');identities=set()
        for row in claude['records']:
            require(row['full_original_record_retained'] is False,'Claude native envelope claim')
            raw = json.dumps(row['fragment'],ensure_ascii=False,separators=(',',':')).encode()
            require(sha(raw)==row['fragment_sha256'] and HEX.fullmatch(row['source_record_sha256']) is not None,'Claude fragment hash mismatch')
            ident=(row['session_id'],row['source_line'],row['source_fragment'],row['fragment_sha256'])
            require(ident not in identities,'Duplicate Claude fragment');identities.add(ident)
            private_check(row,'Claude fragment',hidden=True)
        require(len(identities)==40,'Claude supplement count mismatch')
        self.bundle(late['bundle'],new=True)
        expected = {x['path']:x for x in late['bundle']['members']}
        require(len(expected)==582,'Late member count mismatch')
        records = {x['path']:x for x in late['records']}
        require(len(records)==len(late['records'])==1180,'Late inventory duplicate/count mismatch')
        added = {p for p,x in records.items() if x['disposition']=='ADDED_SAFE_RETAINED_LOG'}
        require(added==set(expected),'Late inclusion/disposition mismatch')
        for name,row in expected.items():
            require(all(records[name][k]==row[k] for k in ['path','bytes','sha256']),'Late source/member binding mismatch')
        for row in records.values():
            if row['disposition']=='ALREADY_EXPORTED_EXACT_BYTES':
                self.read(row['repository_exact_bytes'],row)
        require(dict(collections.Counter(x['disposition'] for x in records.values()))==late['dispositions'],'Late disposition counts differ')
        native = self.load(PREFIX+'/native-recovery-summary.json')
        cutoffs = self.load(PREFIX+'/native-source-cutoffs.json')
        provider = self.load(PREFIX+'/provider-audit.json')
        require(native['status']=='COMPLETE_BOUNDED_VISIBLE_RECOVERY' and not native['errors'] and len(cutoffs)==3355, 'Native source inventory incomplete')
        require(provider['status']=='PASS_BOUNDED_PROVIDER_INVENTORY' and not provider['claude_missing_collection_records'], 'Provider inventory unresolved')
        return {'status':'PASS','historical_base_commit':BASE,'old_message_objects_preserved':old_count,
                'new_visible_messages':new_count,'union_messages':old_count+new_count,'indexed_sessions':len(newdocs),
                'native_additions':kinds['native'],'view_only_additions':kinds['view_only'],
                'bundle_files_verified':len(newmap)+1,'bundle_members_verified':self.verified_bundle_members,
                'reviewed_codex_tool_fragments':len(tool_records),'accepted_claude_fragments':len(identities),
                'late_retained_files':len(expected),'historical_files_verified':len(historical),
                'remaining_native_gap_count':sum(len(x['gaps']) for x in cutoffs),
                'pending_native_tool_records':native['counts']['tool_pending'],
                'credential_scan_findings':0,'native_envelopes_in_new_fragments':0,
                'boundary':'Exact frozen export hashes, type-sensitive old-object preservation and new-fragment/source metadata checks. Native originals are not present and not re-read. Credential scanning is limited to high-confidence patterns in new exports; it is not a universal secrecy proof or whole-provider capture claim.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    try:
        print(json.dumps(Verifier(args.root).run(),ensure_ascii=False,indent=2))
    except (ValueError,KeyError,TypeError,OSError,tarfile.TarError,UnicodeError) as exc:
        print(json.dumps({'status':'FAIL','reason':str(exc)},ensure_ascii=False))
        return 1
    return 0


if __name__=='__main__':
    sys.exit(main())
