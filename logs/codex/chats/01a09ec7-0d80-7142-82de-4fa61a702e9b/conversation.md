# Conversation 01a09ec7-0d80-7142-82de-4fa61a702e9b

Original visible text, unchanged. Dates and headings are editorial.

Message range: **2026-09-14 → 2026-09-14** · America/Los_Angeles.

[Structured log](conversation.json) · [Date policy](../../../DATES.md)

<a id="source-line-9"></a>
## User · source line 9

**2026-09-14T00:17:38.627000-07:00** · original timestamp `2026-09-14T07:17:38.627Z`

```text
Расскажи простым языком и коротко как у нас на уровне папок проект организован

```

<a id="source-line-12"></a>
## Assistant · source line 12

**2026-09-14T00:17:42.277000-07:00** · original timestamp `2026-09-14T07:17:42.277Z`

```text
Посмотрю структуру папок и кратко объясню, что где лежит.

```

<a id="source-line-25"></a>
## Assistant · source line 25

**2026-09-14T00:18:04.659000-07:00** · original timestamp `2026-09-14T07:18:04.659Z`

```text
У нас **две основные папки**:

**[Codex / Philosophy Lab](</Users/ruslansaleksejevs/Documents/Codex/Philosophy Lab>) — главный проект и архив.**
- **research/** — эссе: серии в `campaigns`, пробные работы в `pilots`, материалы судей в `judges`. У каждого эссе своя папка с версиями и историей.
- **research/archive/** — записи происхождения работ и сохранённые материалы.
- **docs/**, **methods/**, **workflows/** — инструкции и описание процессов.
- **scripts/**, **tests/** — программы обслуживания и их проверки.
- **runs/** — материалы отдельных технических запусков и ремонтов.
- **collector/** — служебные файлы сборщика истории чатов.
- **knowledge/** — краткая память о состоянии проекта.
- **exports/** — отдельные копии для передачи наружу.

**[Claude Code / Philosophy Lab](</Users/ruslansaleksejevs/Documents/Claude Code/Philosophy Lab>) — рабочая папка Claude.**
Туда передаются задания: в **work/** лежат их входные материалы и результаты; **jobs/** хранит старые задания.

Claude работает в своей папке, а Codex проверяет и сохраняет результаты в главном проекте.
```

