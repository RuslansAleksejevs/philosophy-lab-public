#!/usr/bin/env python3
"""Rebuild a per-session inventory from validated archive evidence only."""
import collections
import datetime
import json
from pathlib import Path

from research_archive import Archive, ArchiveError
from collector_views import capture_provider, codex_item, provider_inventory, write_provider_inventory


def inventory(archive):
    validation = archive.validate()
    if not validation['ok']:
        raise ArchiveError('Archive validation failed: ' + str(validation['errors']))
    events = archive.events()
    identities = {}
    text_audits = {}
    groups = collections.defaultdict(list)
    coverage = collections.defaultdict(list)
    for event in events:
        sid = event['session_id']
        if event['kind'] == 'capture.session_identified':
            identities[sid] = event['payload']
        elif event['kind'] == 'capture.text_audit':
            text_audits[sid] = {**event['payload'], 'event_id': event['id']}
        elif event['kind'] == 'capture.raw_record' and capture_provider(event) == 'CODEX':
            groups[sid].append(event)
        elif event['kind'] == 'capture.coverage' and capture_provider(event) == 'CODEX':
            coverage[sid].append(event)
    sessions = []
    for sid, records in sorted(groups.items()):
        counts = collections.Counter()
        for event in records:
            item = codex_item(archive,event)
            if item['type'] == 'message':
                if item.get('role') == 'user':
                    counts['user_prompts'] += 1
                elif item.get('phase', item.get('channel')) in ('final', 'final_answer'):
                    counts['assistant_final'] += 1
                else:
                    counts['assistant_commentary'] += 1
            else:
                counts['tool_records'] += 1
        reports = []
        for event in coverage[sid]:
            report = json.loads(archive.get(event['payload']['report_sha256']))
            reports.append({'event_id': event['id'], 'range': report['selected_range'],
                            'status': report['status'], 'gaps': report['gaps']})
        sessions.append({
            'session_id': sid,
            'source_project': identities.get(sid, {}).get('source_project', 'UNKNOWN'),
            'classification': identities.get(sid, {}).get('classification', 'UNKNOWN'),
            'session_kind': identities.get(sid, {}).get('session_kind', 'UNKNOWN'),
            'title': identities.get(sid, {}).get('title', 'UNKNOWN'),
            'agent_name': identities.get(sid, {}).get('agent_name'),
            'role': identities.get(sid, {}).get('role'),
            'parent_session_id': identities.get(sid, {}).get('parent_session_id'),
            'raw_records': len(records),
            **{key: counts[key] for key in ('user_prompts', 'assistant_final',
                                           'assistant_commentary', 'tool_records')},
            'first_captured_message_or_tool_at': min(e['timestamp'] for e in records),
            'last_captured_message_or_tool_at': max(e['timestamp'] for e in records),
            'source_lines': sorted(e['payload']['source_line'] for e in records),
            'coverage_reports': reports,
            'text_audit': text_audits.get(sid),
            'whole_chat_completeness': 'NOT_ESTABLISHED',
        })
    return {'generated_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'archive_head': events[-1]['sha256'] if events else None,
            'session_count_with_raw_records': len(sessions),
            'projects': dict(collections.Counter(s['source_project'] for s in sessions)),
            'session_kinds': dict(collections.Counter(s['session_kind'] for s in sessions)),
            'scope': 'Captured sessions only; not discovery of every existing project chat. '
                     'BOUNDED_COMPLETE never means a complete chat.',
            'sessions': sessions, 'provider_inventory': provider_inventory(archive,events)}


def write_transcripts(archive, view, report):
    """Readable copies; exact originals remain linked archive objects."""
    grouped = collections.defaultdict(list)
    for event in archive.events():
        if event['kind'] != 'capture.raw_record' or capture_provider(event) != 'CODEX':
            continue
        item = codex_item(archive,event)
        if item['type'] == 'message':
            grouped[event['session_id']].append((event,item))
    for session in report['sessions']:
        sid = session['session_id']
        directory = view / 'chats' / sid
        directory.mkdir(parents=True, exist_ok=True)
        records = []
        for event, item in sorted(grouped[sid], key=lambda pair: pair[0]['payload']['source_line']):
            records.append({'event_id': event['id'], 'source_line': event['payload']['source_line'],
                            'timestamp': event['timestamp'], 'recorded_at': event['recorded_at'],
                            'role': item['role'], 'phase': item.get('phase', item.get('channel')),
                            'model': event['model'], 'raw_sha256': event['payload']['raw_sha256'],
                            'text': ''.join(c['text'] for c in item['content'])})
        prompts = [record for record in records if record['role'] == 'user']
        for name, selected in [('prompts', prompts), ('conversation', records)]:
            document = {'session_id': sid, 'source_project': session['source_project'],
                        'title': session['title'], 'archive_head': report['archive_head'],
                        'boundary': 'Captured text only; excludes tools and uncaptured continuation.',
                        'messages': selected}
            (directory / (name + '.json')).write_text(json.dumps(document, ensure_ascii=False, indent=2) + '\n')
            lines = ['# ' + session['title'], '', 'Проект: ' + session['source_project'], '',
                     'Сессия: ' + sid, '',
                     'Производная копия захваченного текста. Инструменты и ещё не захваченное '
                     'продолжение не включены. Оригиналы по ссылкам ниже.', '']
            for number, record in enumerate(selected, 1):
                fence = '```'
                while fence in record['text']:
                    fence += '`'
                lines += ['## ' + str(number) + '. ' + record['role'] + ' / ' + str(record['phase']), '',
                          'Время: ' + record['timestamp'] + '; строка источника: ' + str(record['source_line']), '',
                          '[Оригинальная запись](../../../archive/objects/' + record['raw_sha256'] + ')', '',
                          fence + 'text', record['text'], fence, '']
            (directory / (name + '.md')).write_text('\n'.join(lines))


def main():
    root = Path(__file__).resolve().parents[1]
    archive = Archive(root / 'research/archive')
    events=archive.events()
    if any(e['kind']=='collector.coverage' for e in events):
        from collector_views import refresh
        report=refresh(root,archive,events=events)
        print(json.dumps({'sessions':report['session_count'],'projects':report['projects']},ensure_ascii=False))
        return
    report = inventory(archive)
    view = root / 'research/views'
    view.mkdir(exist_ok=True)
    write_provider_inventory(view,report['provider_inventory'])
    (view / 'chats.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    lines = ['# Реестр захваченных чатов', '',
             'Производное представление research/archive. Пересобрать: '
             '`python3 -B scripts/chat_inventory.py`.', '',
             'Дата отчёта: ' + report['generated_at'], '',
             'Всего сессий с оригинальными записями: ' + str(len(report['sessions'])), '',
             'Типы: ' + str(report['session_kinds']), '',
             '| Исходный проект | Тип | Сессия | Промпты | Финальные ответы | Commentary | Инструменты | Полный чат |',
             '|---|---|---|---:|---:|---:|---:|---|']
    for s in report['sessions']:
        lines.append('| {source_project} | {session_kind} | {session_id} | {user_prompts} | '
                     '{assistant_final} | {assistant_commentary} | {tool_records} | '
                     'Не подтверждено |'.format(**s))
    lines += ['', 'Диапазоны и пробелы каждого захвата: [chats.json](chats.json).',
              '[Другие провайдеры](providers.md) перечислены отдельно и не увеличивают счётчики Codex.',
              'Реестр не утверждает, что обнаружены все существующие чаты. '
              'Служебный bootstrap и экспортные копии не считаются чатами.', '']
    (view / 'chats.md').write_text('\n'.join(lines))
    write_transcripts(archive, view, report)
    print(json.dumps({'sessions': report['session_count_with_raw_records'],
                      'projects': report['projects']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
