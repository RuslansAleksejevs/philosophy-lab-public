"""Derived per-chat, per-turn views. Never a second canonical diary."""
from __future__ import annotations
import collections
import datetime as dt
import json
import os
from pathlib import Path
import re
import uuid

from research_archive import ArchiveError, _safe_path


def write(path, text):
    path=_safe_path(path); path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists() and path.read_text()==text: return
    temp=path.parent/('.tmp-'+uuid.uuid4().hex)
    try:
        with temp.open('x') as stream:
            stream.write(text); stream.flush(); os.fsync(stream.fileno())
        os.replace(temp,path)
    finally:
        if temp.exists(): temp.unlink()


def json_text(value):
    return json.dumps(value,ensure_ascii=False,indent=2)+'\n'


def seconds(ms):
    return 'UNKNOWN' if ms is None else f'{ms / 1000:g} с'


def model_label(model):
    if not model or model.get('status')!='known': return 'UNKNOWN'
    value=model.get('value',{}); return str(value.get('model','UNKNOWN'))+' / '+str(value.get('reasoning_effort') or 'UNKNOWN')


def block(text):
    fence='```'
    while fence in text: fence+='`'
    return fence+'text\n'+text+'\n'+fence+'\n'


def capture_provider(event):
    """Dispatch on archived format metadata before reading any original body."""
    format_name=event['payload'].get('format')
    if format_name=='codex-visible-selection.v1': return 'CODEX'
    if format_name=='claude-visible-fragments.v1': return 'CLAUDE'
    # Codex coverage historically omits format but has its adapter identity.
    if (event['kind']=='capture.coverage' and format_name is None
            and event['actor']['id']=='codex-capture-adapter'): return 'CODEX'
    return 'UNKNOWN'


def codex_item(archive,event):
    """Only known, validated Codex envelopes enter Codex text rendering."""
    if capture_provider(event)!='CODEX':
        raise ArchiveError('non-Codex capture cannot supply a Codex conversation: '+event['id'])
    from capture_codex import classify, strict_json
    try:
        raw=strict_json(archive.get(event['payload']['raw_sha256']))
        line=event['payload']['source_line']
        reason=classify(raw,line,{line},set())
        if reason is not None: raise ArchiveError('unsupported Codex original: '+str(reason))
        return raw['payload']
    except (ValueError,TypeError,KeyError) as exc:
        raise ArchiveError('invalid Codex original envelope: '+event['id']) from exc


def provider_inventory(archive,events):
    """External providers remain visible without parsing their native fragments.

    Counts are fragment counts, not human prompts. Only known normalized Claude
    coverage reports are read; unknown formats remain explicit metadata only.
    """
    rows={}
    def group(provider,event):
        p=event['payload']; job=p.get('job_id')
        if not isinstance(job,str) or not job: job='UNKNOWN'
        key=(provider,event['session_id'],job)
        return rows.setdefault(key,{'provider':provider,'session_id':event['session_id'],
            'job_id':job,'workspace':p.get('workspace','UNKNOWN'),
            'status':'KNOWN_FORMAT_METADATA_ONLY' if provider=='CLAUDE' else 'UNSUPPORTED_FORMAT_METADATA_ONLY',
            'counts':collections.Counter(),'contribution_origins':collections.Counter(),
            'originals':[],'coverage_reports':[],'returns':[],
            'whole_trace':'NOT_ESTABLISHED','count_unit':'safe fragments; never new human contributions'})
    def object_path(digest):
        return 'research/archive/objects/'+digest if isinstance(digest,str) and re.fullmatch('[0-9a-f]{64}',digest) else None
    for event in events:
        if event['kind'] not in {'capture.raw_record','capture.coverage'}: continue
        provider=capture_provider(event)
        if provider=='CODEX': continue
        row=group(provider,event); p=event['payload']
        if event['kind']=='capture.raw_record':
            row['counts']['raw_fragments']+=1
            source_type=p.get('source_type'); role=event['actor']['role']
            if provider=='CLAUDE':
                key=('user_role_message_fragments' if source_type=='message' and role=='user' else
                     'assistant_message_fragments' if source_type=='message' and role=='assistant' else
                     'tool_call_fragments' if source_type=='tool_call' else
                     'tool_result_fragments' if source_type=='tool_result' else 'other_fragments')
                row['counts'][key]+=1
            origin=p.get('contribution_origin','UNKNOWN') if provider=='CLAUDE' else 'UNKNOWN'
            if not isinstance(origin,str): origin='UNKNOWN'
            row['contribution_origins'][origin]+=1
            row['originals'].append({'event_id':event['id'],'source_line':p.get('source_line'),
                'source_fragment':p.get('source_fragment'),'source_type':source_type,
                'format':p.get('format','UNSPECIFIED'),'raw_sha256':p.get('raw_sha256'),
                'object_path':object_path(p.get('raw_sha256')),'contribution_origin':origin,
                'native_channel_role':p.get('native_channel_role'),
                'timestamp':event['timestamp'],'run_id':event['run_id'],'attempt_id':event['attempt_id']})
        else:
            report={'event_id':event['id'],'format':p.get('format','UNSPECIFIED'),
                'status':p.get('status','UNKNOWN'),'run_id':event['run_id'],'attempt_id':event['attempt_id'],
                'claim_event_id':p.get('claim_event_id'),'report_sha256':p.get('report_sha256'),
                'report_path':object_path(p.get('report_sha256')),'selected_range':None,
                'gaps':p.get('gaps',[]) if provider=='CLAUDE' else ['unsupported_capture_format'],
                'exclusions':p.get('exclusions',[]) if provider=='CLAUDE' else []}
            if provider=='CLAUDE':
                data=json.loads(archive.get(p['report_sha256']))
                selected=data.get('selected_range') if isinstance(data,dict) else None
                if (not isinstance(selected,list) or len(selected)!=2
                        or any(type(n) is not int for n in selected) or not 1<=selected[0]<=selected[1]):
                    raise ArchiveError('malformed normalized Claude coverage report: '+event['id'])
                report['selected_range']=selected
            row['coverage_reports'].append(report)
    for event in events:
        if event['kind']!='bridge.return.collected': continue
        p=event['payload']
        if p.get('protocol')!='philosophy-claude-bridge.v1': continue
        # Unclaimed returns have no observed Claude session; never borrow the
        # coordinating Codex session that happened to archive the files.
        if not p.get('claim_event_id'): continue
        row=group('CLAUDE',event)
        job=p.get('job_id'); collection=p.get('collection_id')
        path=('research/bridge/returns/'+job+'/'+collection+'/collection.json'
              if isinstance(job,str) and re.fullmatch('[a-z0-9][a-z0-9_-]*',job)
              and isinstance(collection,str) and re.fullmatch('[0-9a-f]{64}',collection) else None)
        row['returns'].append({'event_id':event['id'],'collection_id':collection,
            'collection_path':path,'claim_event_id':p.get('claim_event_id'),
            'coverage_event_id':p.get('coverage_event_id'),'source_coverage':p.get('source_coverage','UNKNOWN'),
            'run_id':event['run_id'],'attempt_id':event['attempt_id']})
    sessions=[]
    for key in sorted(rows):
        row=rows[key]; row['counts']=dict(row['counts']); row['contribution_origins']=dict(row['contribution_origins'])
        sessions.append(row)
    return {'schema_version':1,'session_count':len({(s['provider'],s['session_id']) for s in sessions}),
            'job_session_count':len(sessions),'sessions':sessions,
            'boundary':'Separate external-provider metadata inventory. Original bodies are linked, not parsed as Codex envelopes. Counts do not attest human authorship.'}


def write_provider_inventory(view,report):
    write(view/'providers.json',json_text(report))
    lines=['# Другие провайдеры','','Отдельно от чатов и человеческих промптов Codex. Числа означают фрагменты, а не новые человеческие реплики.','']
    for row in report['sessions']:
        lines+=['## '+str(row['provider'])+' / '+str(row['session_id']),'',
                'Задание: '+str(row['job_id'])+'; workspace: '+str(row['workspace']),
                'Статус: '+row['status']+'; фрагментов: '+str(row['counts'].get('raw_fragments',0)),
                'Происхождение: '+str(row['contribution_origins']), '']
        for c in row['coverage_reports']:
            lines.append('- Coverage '+str(c['status'])+'; диапазон '+str(c['selected_range'])+
                ('; [отчёт](../archive/objects/'+c['report_sha256']+')' if c['report_path'] else '')+'.')
        for result in row['returns']:
            if result['collection_path']: lines.append('- [Возврат файлов](../'+result['collection_path'].removeprefix('research/')+').')
        for original in row['originals']:
            if original['object_path']: lines.append('- [Оригинальный фрагмент '+str(original['source_line'])+':'+str(original['source_fragment'])+'](../archive/objects/'+original['raw_sha256']+').')
        lines.append('')
    lines+=['[Машинный реестр](providers.json). UNKNOWN сохраняет неизвестное происхождение; bounded coverage не означает всю историю провайдера.','']
    write(view/'providers.md','\n'.join(lines))


def refresh(root, archive, events=None, changed_sessions=None):
    events=archive.events() if events is None else events
    by_id={e['id']:e for e in events}
    view=Path(root)/'research/views'; previous={}
    if changed_sessions is not None and (view/'chats.json').exists():
        try: previous={s['session_id']:s for s in json.loads((view/'chats.json').read_text()).get('sessions',[])}
        except (ValueError,KeyError,TypeError): previous={}
    identities={}; coverage={}; groups=collections.defaultdict(list)
    for e in events:
        sid=e['session_id']
        if e['kind']=='capture.session_identified': identities[sid]=e['payload']
        if e['kind']=='collector.coverage': coverage[sid]=e['payload']
        if e['kind'].startswith('collector.') or (e['kind']=='capture.raw_record' and capture_provider(e)=='CODEX'): groups[sid].append(e)
    sessions=[]; internal_sessions=[]
    for sid in sorted(set(groups)|set(identities)):
        identity=identities.get(sid,{})
        if sid=='bootstrap': continue
        if identity.get('collection_policy')=='EXCLUDED_INTERNAL_RUNTIME':
            internal_sessions.append({'session_id':sid,'source_project':identity.get('source_project'),
                                      'session_kind':'internal_runtime','source_subtype':identity.get('native_source_subtype'),
                                      'collection_policy':'EXCLUDED_INTERNAL_RUNTIME'})
            directory=view/'chats'/sid
            for name in ('conversation','prompts','turns'):
                write(directory/(name+'.json'),json_text({'session_id':sid,'status':'EXCLUDED_INTERNAL_RUNTIME','messages':[]}))
                if name!='turns': write(directory/(name+'.md'),'# Служебная сессия Codex\n\nИсключена из исследовательских чатов и их счётчиков. Тело не выводится.\n')
            continue
        if (changed_sessions is not None and sid not in changed_sessions and sid in previous
                and previous[sid].get('view_schema_version') == 2):
            sessions.append(previous[sid]); continue
        original={}; messages={}; turns={}; automations={}; view_gaps=[]; item_cache={}; gap_keys=set()
        def view_gap(raw_id, source_line, reason):
            # No exception text or rejected body enters derived views. The
            # original remains in its immutable archive location for diagnosis.
            line=source_line if type(source_line) is int else None
            key=(raw_id,line,reason)
            if key not in gap_keys:
                gap_keys.add(key)
                view_gaps.append({'raw_event_id':raw_id,'source_line':line,'reason':reason,
                                  'body_rendered':False})
        def checked_item(event, source_line, raw_id):
            if (type(source_line) is not int or source_line < 1
                    or event is None or event.get('kind')!='capture.raw_record'
                    or event.get('session_id')!=sid
                    or event.get('payload',{}).get('source_line')!=source_line):
                view_gap(raw_id,source_line,'invalid_or_missing_raw_reference')
                return None
            if raw_id not in item_cache:
                try:
                    item_cache[raw_id]=codex_item(archive,event)
                except (ArchiveError,OSError,ValueError,TypeError,KeyError):
                    item_cache[raw_id]=None
            item=item_cache[raw_id]
            if item is None:
                view_gap(raw_id,source_line,'unsupported_or_invalid_codex_original')
            return item
        def turn(tid,line):
            key=tid or 'unknown-at-line-'+str(line)
            return turns.setdefault(key,{'turn_id':tid,'first_source_line':line,'started_at':None,
                                         'ended_at':None,'duration_ms':None,'status':'UNKNOWN',
                                         'model':None,'messages':[]})
        for e in groups[sid]:
            p=e['payload']; kind=e['kind']
            if kind=='capture.raw_record':
                item=checked_item(e,p.get('source_line'),e['id'])
                if item is None: continue
                if item['type']=='message':
                    original[p['source_line']]={'role':item['role'],'phase':item.get('phase',item.get('channel')),
                        'text':''.join(c['text'] for c in item['content']),'timestamp':e['timestamp'],
                        'recorded_at':e['recorded_at'],'source_line':p['source_line'],
                        'raw_sha256':p['raw_sha256'],'event_id':e['id'],'model':e['model'],
                        'turn_id':item.get('internal_chat_message_metadata_passthrough',{}).get('turn_id')}
            elif kind=='collector.message':
                m=dict(p); m['event_id']=e['id']; m['timestamp']=p.get('source_timestamp',e['timestamp'])
                m['recorded_at']=e['recorded_at']; m['model']=m.get('observed_model')
                if m.get('raw_event_id'):
                    raw_event=by_id.get(m['raw_event_id'])
                    item=checked_item(raw_event,p.get('source_line'),m['raw_event_id'])
                    if item is None: continue
                    if item.get('type')!='message':
                        view_gap(m['raw_event_id'],p.get('source_line'),'raw_reference_is_not_a_message')
                        continue
                    raw_p=raw_event['payload']
                    m['text']=''.join(c['text'] for c in item['content']); m['raw_sha256']=raw_p['raw_sha256']
                messages[p['source_line']]=m
            elif kind=='collector.lifecycle':
                t=turn(p.get('turn_id'),p['source_line']); ts=p.get('source_timestamp',e['timestamp'])
                t.setdefault('lifecycle_record_times',{})[p['event_type']]=ts
                t.setdefault('lifecycle_time_observations',{}).update(p.get('lifecycle_time_observations',{}))
                if p.get('started_at'): t['started_at']=p['started_at']
                if p['event_type']=='task_started': t['started_at']=p.get('started_at',ts); t['status']='ONGOING'
                else:
                    t['ended_at']=p.get('completed_at',ts); t['duration_ms']=p.get('duration_ms'); t['status']='INTERRUPTED' if p['event_type']=='turn_aborted' else 'COMPLETED'
                    t['reason']=p.get('reason'); t['terminal_event_id']=e['id']
                for field in ('time_to_first_token_ms','time_to_first_token_source','time_to_first_token_boundary'):
                    if field in p: t[field]=p[field]
            elif kind=='collector.model': turn(p.get('turn_id'),p['source_line'])['model']=p.get('observed_model')
            elif kind in ('collector.tool_pending','collector.tool_reviewed') and p.get('origin')=='AUTOMATION':
                automations[p['source_line']]={**p,'event_id':e['id']}
        for line,m in original.items(): messages.setdefault(line,m)
        ordered=sorted(messages.values(),key=lambda m:m['source_line'])
        counts=collections.Counter()
        for m in ordered:
            t=turn(m.get('turn_id'),m['source_line']); t['messages'].append(m)
            if not m.get('model') or m['model'].get('status')!='known': m['model']=t.get('model')
            m['origin']='HUMAN' if m['role']=='user' and identity.get('session_kind')=='primary_chat' else ('AI' if m['role']=='assistant' else 'UNKNOWN_DISPATCH_OR_INHERITED')
            counts['user_prompts' if m['role']=='user' else 'assistant_final' if m.get('phase') in ['final','final_answer'] else 'assistant_commentary']+=1
        turn_list=sorted(turns.values(),key=lambda t:t['first_source_line'])
        for t in turn_list:
            assistant=[m for m in t['messages'] if m['role']=='assistant']; finals=[m for m in assistant if m.get('phase') in ['final','final_answer']]
            t['final_answer_present']=bool(finals); t['first_visible_response_at']=assistant[0]['timestamp'] if assistant else None
            t['time_to_first_visible_ms']=None
            if t['started_at'] and assistant:
                elapsed=(dt.datetime.fromisoformat(assistant[0]['timestamp'].replace('Z','+00:00'))-dt.datetime.fromisoformat(t['started_at'].replace('Z','+00:00'))).total_seconds()*1000
                if elapsed>=0: t['time_to_first_visible_ms']=elapsed
                else: t['timing_gap']='source_clock_order_anomaly'
        c=coverage.get(sid,{}); cursor=c.get('cursor',{})
        if automations: counts['automation_triggers']=len(automations)
        session={'session_id':sid,**identity,'counts':dict(counts),'text_coverage':c.get('text_status','NOT_AUDITED'),
                 'tools_coverage':c.get('tools_status','NOT_AUDITED'),
                 'cutoff_source_line':cursor.get('lines'),'last_capture_at':cursor.get('committed_at'),
                 'pending_tool_records':cursor.get('pending_tools'),'gaps':cursor.get('gaps',[]),
                 'view_schema_version':2,'view_status':'GAPS' if view_gaps else 'RENDERED',
                 'view_gaps':view_gaps,
                 'excluded_surfaces':cursor.get('exclusions',{}),'turns':len(turn_list),'whole_trace':'INCOMPLETE'}
        sessions.append(session)
        directory=view/'chats'/sid
        base={'session':session,'boundary':'Source-record counts per session; inherited/AI-dispatched user-role messages are not new human contributions. Duration is wall time including tools and waits.'}
        write(directory/'turns.json',json_text({**base,'turns':turn_list,
              'automation_triggers':[automations[k] for k in sorted(automations)]}))
        write(directory/'conversation.json',json_text({**base,'messages':ordered}))
        write(directory/'prompts.json',json_text({**base,'messages':[m for m in ordered if m['role']=='user']}))
        title=identity.get('title') or identity.get('agent_name') or sid
        header=['# '+title,'','Проект: '+str(identity.get('source_project','UNKNOWN')),'','ID: '+sid,'',
                'Охват текста: '+session['text_coverage']+'; до строки '+str(session['cutoff_source_line'])+'.',
                'Охват инструментов: '+session['tools_coverage']+'; неразобранных пробелов: '+str(len(session['gaps']))+'.',
                'Пробелы отображения: '+str(len(view_gaps))+'. Неподдерживаемые оригиналы не показаны; архив сохранён.',
                'Длительность — время хода, включая инструменты и ожидание. UNKNOWN означает отсутствие наблюдения.',
                'Тела непроверенных инструментов и скрытые рассуждения сюда не включены.','']
        transcript=list(header); prompts=list(header)
        for i,t in enumerate(turn_list,1):
            section=['## Ход '+str(i),'','ID хода: '+str(t['turn_id'] or 'UNKNOWN'),
                     'Статус: '+t['status']+'; финальный ответ: '+('есть' if t['final_answer_present'] else 'нет'),
                     'Модель / reasoning: '+model_label(t['model']),
                     'Начало: '+str(t['started_at'] or 'UNKNOWN')+'; завершение: '+str(t['ended_at'] or 'UNKNOWN'),
                     'Длительность: '+seconds(t['duration_ms'])+'; до первого видимого ответа: '+seconds(t['time_to_first_visible_ms']),
                     'До первого токена по данным Codex: '+seconds(t.get('time_to_first_token_ms')),'']
            transcript+=section
            if any(m['role']=='user' for m in t['messages']): prompts+=section
            for m in t['messages']:
                section=['### '+m['role']+' / '+str(m.get('phase') or 'prompt'),'','Время: '+m['timestamp']+'; строка '+str(m['source_line']),
                         'Наблюдаемая модель: '+model_label(m.get('model')),'']
                if m.get('raw_sha256'): section+=['[Оригинальная запись](../../../archive/objects/'+m['raw_sha256']+')','']
                else: section+=['Сохранена проекция текста; исключения: '+str(m.get('attachment_gaps',[])), '']
                if not m['text']: section+=['Текст отсутствует; содержимое вложений см. в показателях охвата.','']
                section+=[block(m['text']),'']
                transcript+=section
                if m['role']=='user': prompts+=section
        write(directory/'conversation.md','\n'.join(transcript)); write(directory/'prompts.md','\n'.join(prompts))
    summary={'schema_version':1,'archive_head':events[-1]['sha256'] if events else None,
             'session_count':len(sessions),'session_kinds':dict(collections.Counter(s.get('session_kind','UNKNOWN') for s in sessions)),
             'projects':dict(collections.Counter(s.get('source_project','UNKNOWN') for s in sessions)),
             'sessions':sessions,'status_path':'../../collector/runtime/status.json'}
    summary['internal_excluded_session_count']=len(internal_sessions)
    summary['internal_excluded_sessions']=internal_sessions
    summary['view_schema_version']=2
    summary['view_gap_count']=sum(len(s.get('view_gaps',[])) for s in sessions)
    summary['sessions_with_view_gaps']=sum(bool(s.get('view_gaps')) for s in sessions)
    summary['view_status']='GAPS' if summary['view_gap_count'] else 'RENDERED'
    summary['provider_inventory']=provider_inventory(archive,events)
    write_provider_inventory(view,summary['provider_inventory'])
    write(view/'chats.json',json_text(summary))
    lines=['# Чаты лаборатории','','Источник: канонический архив. Основные чаты и субагенты считаются отдельно.',
           'Количество: '+str(summary['session_kinds']),'',
           'Отдельно исключены внутренние служебные сессии Codex: '+str(len(internal_sessions))+'.','',
           'Пробелы отображения: '+str(summary['view_gap_count'])+' в '+str(summary['sessions_with_view_gaps'])+' чатах; неподдерживаемые оригиналы не показаны.','',
           '| Чат | Проект | Тип | Промпты / финалы | Охват текста | Охват инструментов | Инструменты ждут проверки |',
           '|---|---|---|---:|---|---|---:|']
    for s in sessions:
        title=(s.get('title') or s.get('agent_name') or s['session_id']).replace('|','\\|').replace('\n',' ')
        count=s['counts']; prefix='chats/'+s['session_id']+'/'
        lines.append('| ['+title+']('+prefix+'conversation.md) · [промпты]('+prefix+'prompts.md) | '+str(s.get('source_project','UNKNOWN'))+' | '+str(s.get('session_kind','UNKNOWN'))+' | '+str(count.get('user_prompts',0))+' / '+str(count.get('assistant_final',0))+' | '+s['text_coverage']+' | '+str(s.get('tools_coverage','NOT_AUDITED'))+' | '+str(s['pending_tool_records'])+' |')
    lines+=['','[Состояние сборщика](../../collector/runtime/status.json). [Машинный реестр](chats.json).',
            '[Отдельный реестр Claude и неизвестных форматов](providers.md). Они не входят в счётчики чатов Codex.',
            'Полнота относится к зафиксированному участку; будущие сообщения и непроверенные инструменты не объявляются сохранёнными.','']
    write(view/'chats.md','\n'.join(lines))
    return summary
