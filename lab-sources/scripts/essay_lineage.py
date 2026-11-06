#!/usr/bin/env python3
"""Canonical append-only essay/idea lineage with rebuildable readable biographies.

No provider calls. Legacy associations are evidence inventories, not invented
causal ancestry. Human-readable files are derived; original HISTORY is untouched.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path
from research_archive import Archive, ArchiveError
from collector_views import write

PROTOCOL = 'essay-lineage.v1'
KINDS = {'origin', 'idea', 'draft', 'critique', 'revision', 'final', 'evaluation',
         'selection', 'tournament', 'correction', 'legacy_inventory', 'cli_attempt'}
HEX = re.compile(r'[0-9a-f]{64}')
IDENT = re.compile(r'[A-Za-z0-9][A-Za-z0-9_.:/-]{0,200}')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def event_references(value, events):
    """Follow explicit IDs in receipts only, never infer meaning from manuscript text."""
    if isinstance(value,str):return [value] if value in events else []
    if isinstance(value,dict):return [e for v in value.values() for e in event_references(v,events)]
    if isinstance(value,list):return [e for v in value for e in event_references(v,events)]
    return []


def canonical(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2)+'\n').encode()


def index(events):
    return {e['payload']['entry']['id']: e for e in events
            if e['kind'] == 'essay.lineage.entry' and e['payload'].get('protocol') == PROTOCOL}


def validate(entry, known, events, get):
    required = {'id','entity','kind','parents','artifacts','evidence','occurred_at',
                'actor','configuration','workflow','summary','gaps'}
    if not required <= entry.keys() or entry['kind'] not in KINDS:
        raise ValueError('Incomplete lineage entry or unknown kind')
    for key in ('id','entity'):
        if not isinstance(entry[key],str) or not IDENT.fullmatch(entry[key]) or '..' in entry[key].split('/'):
            raise ValueError('Invalid identity')
    if not isinstance(entry['summary'],str) or not entry['summary'].strip():
        raise ValueError('Summary required')
    if not isinstance(entry['parents'],list) or not isinstance(entry['gaps'],list):
        raise ValueError('Parents/gaps must be lists')
    if len(set(entry['parents'])) != len(entry['parents']):
        raise ValueError('Duplicate parent')
    for parent in entry['parents']:
        if parent == entry['id'] or parent not in known:
            raise ValueError('Unknown or cyclic parent: '+parent)
    if not isinstance(entry['configuration'],dict) or not {'requested','observed'} <= entry['configuration'].keys():
        raise ValueError('Separate requested/observed configuration required')
    if entry['occurred_at'] != 'UNKNOWN':
        import datetime
        value=datetime.datetime.fromisoformat(entry['occurred_at'].replace('Z','+00:00'))
        if value.tzinfo is None: raise ValueError('Event time needs timezone')
    for a in entry['artifacts']:
        if not {'path','sha256','role'} <= a.keys() or not HEX.fullmatch(a['sha256']):
            raise ValueError('Invalid artifact')
        if digest(get(a['sha256'])) != a['sha256']:
            raise ValueError('Artifact object mismatch')
    for e in entry['evidence']:
        if e not in events: raise ValueError('Unknown evidence event: '+e)
    if entry['kind'] in {'evaluation','tournament'}:
        match=entry.get('assessment',{})
        if not {'versions','judge','rubric_sha256','prompt_sha256','order','verdict','rationale','round'} <= match.keys():
            raise ValueError('Assessment requires exact versions, judge, rubric, order and verdict')
        if not match['versions'] or not {'requested','observed'} <= match['judge'].keys():
            raise ValueError('Missing judge settings or assessed versions')
        for v in match['versions']:
            parent=known.get(v.get('entry_id'))
            if not parent or v['entry_id'] not in entry['parents']:
                raise ValueError('Assessed version must be a declared parent')
            if v.get('sha256') not in [a['sha256'] for a in parent['payload']['entry']['artifacts']]:
                raise ValueError('Version not bound to parent')
        ids=[v['entry_id'] for v in match['versions']]
        if sorted(match['order']) != sorted(ids): raise ValueError('Assessment order mismatch')
        if entry['kind']=='tournament' and len(ids)<2: raise ValueError('Tournament needs opponents')
        for key in ['rubric_sha256','prompt_sha256']:
            if not HEX.fullmatch(match[key]) or digest(get(match[key]))!=match[key]:
                raise ValueError('Unbound evaluation prompt/rubric')
    if entry['kind']=='selection' and (not entry['parents'] or not entry.get('decision')):
        raise ValueError('Selection needs candidate/evaluation parents and decision')
    if entry['kind']=='correction' and not entry['parents']:
        raise ValueError('Correction must retain superseded record as parent')
    if entry['kind'] in {'idea','draft','critique','revision','final'} and not entry['parents']:
        raise ValueError('New research stage must identify its origin/predecessor')


def append(writer, entry, session, known=None, events=None):
    if events is None: events={e['id']:e for e in writer.events()}
    if known is None: known=index(events.values())
    existing=known.get(entry['id'])
    if existing:
        if existing['payload']['entry'] != entry: raise ValueError('Lineage ID already bound to different bytes')
        return existing
    validate(entry,known,events,writer.get)
    obj=writer.put(canonical(entry))
    result=writer.append({'kind':'essay.lineage.entry','actor':{'id':'essay-lineage','role':'tool'},
        'session_id':session,'run_id':'essay-lineage','operation_id':'lineage:'+digest(entry['id'].encode())[:24],
        'attempt_id':'append-v1','parents':list(dict.fromkeys(entry['evidence']+[known[p]['id'] for p in entry['parents']])),
        'outputs':list(dict.fromkeys([obj]+[a['sha256'] for a in entry['artifacts']])),
        'payload':{'protocol':PROTOCOL,'entry':entry,'entry_sha256':obj}},'essay-lineage:'+entry['id'])
    known[entry['id']]=result;events[result['id']]=result
    return result


def base_entry(identity, entity, kind, summary):
    return {'id':identity,'entity':entity,'kind':kind,'summary':summary,'parents':[],
            'artifacts':[],'evidence':[],'occurred_at':'UNKNOWN','actor':'UNKNOWN',
            'configuration':{'requested':'UNKNOWN','observed':'UNKNOWN'},
            'workflow':'UNKNOWN','gaps':[]}


def bind_packet(writer, packet, campaign, session):
    if not re.fullmatch(r'[A-Za-z0-9_.-]+', campaign): raise ValueError('Invalid campaign')
    return writer.append({'kind':'essay.lineage.packet_binding','actor':{'id':'essay-lineage','role':'tool'},
        'session_id':session,'run_id':'essay-lineage','operation_id':'bind:'+packet,'attempt_id':'one',
        'payload':{'protocol':PROTOCOL,'packet':packet,'campaign':campaign}},'lineage-packet:'+packet)


def ingest_cli(writer, collection, intake, session):
    """Called inside the existing intake transaction, before dependent reporting."""
    events={e['id']:e for e in writer.events()};known=index(events.values())
    receipt_bytes=(collection/'collection.json').read_bytes()
    if digest(receipt_bytes)!=intake['payload'].get('collection_sha256'):
        raise ValueError('Collection receipt differs from canonical intake')
    receipt=json.loads(receipt_bytes)
    if 'manifest.json' not in receipt['files']:raise ValueError('Manifest not bound to collection')
    for name,expected in receipt['files'].items():
        if name=='manifest.json' or name.startswith(('records/','bindings/')):
            path=(collection/name).resolve(strict=True)
            if not path.is_relative_to(collection.resolve()) or digest(path.read_bytes())!=expected:
                raise ValueError('Lineage evidence changed after intake')
    manifest=json.loads((collection/'manifest.json').read_text())
    if manifest.get('purpose') != 'research':return []
    bindings=[e for e in events.values() if e['kind']=='essay.lineage.packet_binding'
              and e['payload']['packet']==manifest['id']]
    if not bindings: raise ValueError('Research packet needs explicit lineage campaign binding')
    campaign=bindings[0]['payload']['campaign'];records=[]
    for name in receipt['files']:
        if name.startswith('records/') and name.endswith('.json'):
            f=collection/name
            records.append((f,json.loads(f.read_text())))
    records.sort(key=lambda pair:(pair[1].get('at',''),pair[0].name))
    tasks={t['id']:t for t in manifest['tasks']};starts={};native={};validation={};results={};added=[]
    for file,r in records:
        attempt=r.get('attempt');key=(r.get('task'),attempt);kind=r.get('kind')
        if kind=='attempt.started': starts[key]=r
        elif kind=='native.observations':native[key]=r['report']
        elif kind=='output.validation':validation[key]=r['report']
        elif kind=='provider.visible' and r.get('observation',{}).get('type')=='result':results[key]=r['observation']
        if kind!='attempt.finished':continue
        task=tasks[r['task']];entity=campaign+'/'+task['essay_id']
        identity='cli:'+manifest['id']+':'+attempt
        origin_id='cli-origin:'+manifest['id']+':'+task['id']
        if origin_id not in known:
            origin=base_entry(origin_id,entity,'origin','Точное задание и исходный пакет для '+task['id'])
            origin['artifacts']=[{'path':n,'sha256':h,'role':'input'} for n,h in manifest.get('input_hashes',{}).items()
                                 if n.startswith('inputs/'+task['id']+'/')]
            origin['evidence']=[intake['id'],bindings[0]['id']]
            origin['configuration']['requested']={'model':task['model'],'effort':task['effort']}
            origin['workflow']={'protocol':manifest['protocol'],'task':task['id'],'role':task['role']}
            origin['gaps']=['User-to-concept ancestry before this exact task packet requires separate evidence.']
            added.append(append(writer,origin,session,known,events)['id'])
        if identity in known:
            if origin_id not in known[identity]['payload']['entry']['parents']:
                correction=base_entry('origin-link:'+attempt,entity,'correction','Дополнена связь сохранённой попытки с точным исходным заданием; прежняя запись не изменена.')
                correction['parents']=[identity,origin_id]
                correction['evidence']=[intake['id']]
                # First supporting intake stays bound on subsequent replays.
                if correction['id'] not in known:added.append(append(writer,correction,session,known,events)['id'])
            continue
        start=starts.get(key,{})
        e=base_entry(identity,entity,'cli_attempt',r['task']+': '+r['status']+' / '+r['reason'])
        e.update(actor='Claude',occurred_at=r['at'],workflow={'protocol':manifest['protocol'],'role':task['role'],'orchestration':task.get('orchestration')})
        e['configuration']={'requested':start.get('requested',{'model':task['model'],'effort':task['effort']}),
                            'observed':native.get(key,'UNKNOWN')}
        e['attempt']={'task_id':task['id'],'session_id':start.get('session_id','UNKNOWN'),'started_at':start.get('at','UNKNOWN'),
                      'finished_at':r['at'],'seconds':r.get('wall_seconds'),'status':r['status'],
                      'reason':r['reason'],'validation':validation.get(key),'usage':results.get(key),
                      'prompt':start.get('prompt','UNKNOWN')}
        e['evidence']=[intake['id'],bindings[0]['id']]
        for n,h in r.get('outputs',{}).items():e['artifacts'].append({'path':n,'sha256':h,'role':'output'})
        for n,h in manifest.get('input_hashes',{}).items():
            if n.startswith('inputs/'+task['id']+'/'):e['artifacts'].append({'path':n,'sha256':h,'role':'input'})
        binding=collection/'bindings'/(task['id']+'.json')
        if str(binding.relative_to(collection)) in receipt['files']:
            for n,h in json.loads(binding.read_text()).items():
                # Dependency bytes may be stored under inputs or output object store.
                if (collection/'objects'/h).exists():
                    e['artifacts'].append({'path':'input/'+n,'sha256':h,'role':'dependency'})
        prior=[v['payload']['entry'] for v in known.values() if v['payload']['entry']['entity']==entity
               and v['payload']['entry']['kind']=='cli_attempt']
        predecessors={d['task'] for d in task.get('dependencies',[])} | set(task.get('source_dependencies',[]))
        linked={}
        for earlier in prior:
            a=earlier.get('attempt',{})
            if a.get('session_id')==start.get('session_id') or a.get('task_id') in predecessors:
                linked[a.get('task_id')]=earlier['id']
        e['parents']=[origin_id]+list(linked.values())
        e['gaps']=['Pre-CLI conceptual ancestry is in legacy evidence; not inferred.',
                   'Private reasoning and full unreviewed tool bodies excluded; usage is not a subscription invoice.']
        added.append(append(writer,e,session,known,events)['id'])
    return added


def render(root, writer):
    events=writer.events();known=index(events);group={}
    for event in known.values():
        entry=event['payload']['entry'];entities={entry['entity']}
        if entry['kind'] in {'tournament','evaluation','selection'}:
            entities.update(known[parent]['payload']['entry']['entity'] for parent in entry['parents'])
        for entity in entities:group.setdefault(entity,[]).append(event)
    summaries=[]
    for entity,items in sorted(group.items()):
        folder=root/'research/biographies'/entity
        data={'protocol':PROTOCOL,'entity':entity,'entries':[{'event_id':e['id'],'recorded_at':e['recorded_at'],**e['payload']['entry']} for e in items]}
        write(folder/'biography.json',canonical(data).decode())
        lines=['# Биография: '+entity,'','Производное представление канонического архива. Старые HISTORY сохранены. UNKNOWN означает отсутствие подтверждения.','']
        for event in items:
            e=event['payload']['entry'];lines += ['## '+e['kind']+' · '+e['occurred_at'],'',e['summary'],'',
                '- ID: `'+e['id']+'`','- Предшественники: '+(', '.join(e['parents']) or 'не связаны'),
                '- Событие архива: `'+event['id']+'`','- Workflow: '+json.dumps(e['workflow'],ensure_ascii=False)]
            conf=e['configuration'];obs=conf['observed']
            if isinstance(obs,dict) and 'observations' in obs:
                labels=set()
                for observation in obs['observations']:
                    value=observation.get('value', observation)
                    model=value.get('model', 'UNKNOWN')
                    effort=value.get('effort', value.get('reasoning_effort', 'UNKNOWN'))
                    if model!='<synthetic>': labels.add(str(model)+' / '+str(effort))
                obs=sorted(labels)
            lines += ['- Запрошено: '+json.dumps(conf['requested'],ensure_ascii=False),'- Наблюдалось: '+json.dumps(obs,ensure_ascii=False)]
            lines += ['- Свидетельства архива: '+(', '.join('`'+i+'`' for i in e['evidence']) or 'не связаны')]
            if e.get('assessment'):lines += ['- Оценка: '+json.dumps(e['assessment'],ensure_ascii=False)]
            if e.get('decision'):lines += ['- Решение: '+json.dumps(e['decision'],ensure_ascii=False)]
            for gap in e['gaps']:lines += ['- Пробел/граница: '+gap]
            lines += ['','Артефакты (точные версии доступны в архиве):','']
            for a in e['artifacts']:
                target=root/a['path']
                label=('['+a['path']+'](<'+str(target)+'>)') if target.is_file() else '`'+a['path']+'`'
                obj=root/'research/archive/objects'/a['sha256']
                lines += ['- '+a['role']+': '+label+' · [точная версия](<'+str(obj)+'>) · `'+a['sha256']+'`']
            lines += ['']
        write(folder/'BIOGRAPHY.md','\n'.join(lines)+'\n')
        summaries.append({'entity':entity,'entries':len(items),'path':str((folder/'BIOGRAPHY.md').relative_to(root)),
                          'gaps':sorted({g for e in items for g in e['payload']['entry']['gaps']})})
    write(root/'research/biographies/index.json',canonical(summaries).decode())
    write(root/'research/biographies/README.md','# Биографии эссе и идей\n\nОбновляется из архива. Наличие карточки не означает, что эссе закончено.\n\n'+'\n'.join('- ['+s['entity']+']('+s['entity']+'/BIOGRAPHY.md) — '+str(s['entries'])+' записей' for s in summaries)+'\n')
    return summaries


def backfill(root, writer, session):
    events={e['id']:e for e in writer.events()};known=index(events.values())
    byhash={}
    for e in events.values():
        if e['kind'].startswith('essay.lineage.'):continue
        for h in e.get('outputs',[]):byhash.setdefault(h,[]).append(e['id'])
    folders=sorted(p for p in (root/'research/campaigns').glob('*/essay-*') if p.is_dir())
    if (root/'research/pilots').exists():
        folders+=sorted(p for p in (root/'research/pilots').iterdir() if p.is_dir() and (p/'HISTORY.md').exists())
    selected={'HISTORY.md','identity.json','question.md','draft.md','final.md','critique.md','revision.md','decision.md',
              'author-task.txt','critic-task.txt','revision-task.txt','dispatch.txt','author-prompt.md','model-transition.md',
              'author-notes.json','final-notes.json','process.md','sources.md'}
    for folder in folders:
        entity=folder.parent.name+'/'+folder.name if folder.parent.name!='pilots' else 'pilots/'+folder.name
        e=base_entry('legacy:'+entity,entity,'legacy_inventory','Исторические материалы: точные байты, существующие квитанции и связи. Содержание истории не заменяет независимого подтверждения.')
        for p in sorted(folder.iterdir()):
            if p.is_file() and not p.is_symlink() and (p.name in selected or p.name.endswith('.receipt.json') or re.fullmatch(r'(draft|final|critique|revision)-\d+\.md',p.name)):
                data=p.read_bytes();h=writer.put(data)
                e['artifacts'].append({'path':str(p.relative_to(root)),'sha256':h,'role':'legacy_evidence'})
                e['evidence'].extend(byhash.get(h,[]))
                if p.suffix=='.json':
                    try:
                        value=json.loads(data)
                        e['evidence'].extend(event_references(value,events))
                    except (ValueError,AttributeError):pass
        # Campaign briefs preserve shared neutral workflow context, never infer ancestry from prose.
        for name in ['AUTHOR_BRIEF.md','METHODOLOGY.md','campaign.json','method.json','OPERATIONS.md']:
            p=folder.parent/name
            if p.is_file() and not p.is_symlink():e['artifacts'].append({'path':str(p.relative_to(root)),'sha256':writer.put(p.read_bytes()),'role':'shared_context'})
        e['evidence']=list(dict.fromkeys(e['evidence']))
        e['id'] += ':'+digest(canonical({'artifacts':e['artifacts'],'evidence':sorted(e['evidence'])}))[:20]
        if e['id'] in known:continue
        prior=[x['payload']['entry'] for x in known.values()
               if x['payload']['entry']['entity']==entity and x['payload']['entry']['kind']=='legacy_inventory']
        if prior:e['parents']=[prior[-1]['id']]
        e['configuration']['observed']=[{'event_id':i,'model':events[i]['model']}
             for i in e['evidence'] if events[i].get('model',{}).get('status')=='known'] or 'UNKNOWN'
        e['gaps']=['Historical causal links/model settings not reconstructed automatically; inspect linked original evidence.',
                   'No recorded tournament does not prove no historical selection occurred.']
        append(writer,e,session,known,events)
    return len(folders)


def main():
    p=argparse.ArgumentParser();p.add_argument('command',choices=['record','refresh','backfill','bind-packet'])
    p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--session',default='lineage-maintenance')
    p.add_argument('--input',type=Path);p.add_argument('--packet');p.add_argument('--campaign');args=p.parse_args();root=args.root.resolve()
    with Archive(root/'research/archive').writer() as w:
        if args.command=='record':
            entry=json.loads(args.input.read_text())
            for artifact in entry.get('artifacts',[]):
                if 'sha256' not in artifact:
                    path=(root/artifact['path']).resolve(strict=True)
                    if not path.is_relative_to(root) or path.is_symlink():raise ValueError('Artifact outside lab')
                    artifact['sha256']=w.put(path.read_bytes())
            append(w,entry,args.session)
        if args.command=='backfill':backfill(root,w,args.session)
        if args.command=='bind-packet':bind_packet(w,args.packet,args.campaign,args.session)
        result=render(root,w)
    print(json.dumps({'entities':len(result),'index':'research/biographies/README.md'}))

if __name__=='__main__':main()
