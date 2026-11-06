# One small complete cycle

## Ясное изложение для будущих работ

С 10 октября 2026 года использовать `workflows/CLEAR_PROSE.md`: сохранять
качество и глубину аргумента, выражать его относительно простым человеческим
языком, не перегружать предложения. В новые задания автору и редактору включать
нейтральный текст правила. Существующие рукописи, оценки и запечатанные задания
не менять; правило не запускает новый раунд и не меняет рубрику оценщика.

## Раунд и мягкие рекомендации по исследованию

Уточнение пользователя от 8 сентября 2026, America/Los_Angeles. Это общие
рекомендации по процессу и качеству, без человеческих философских тезисов.

Раунд — один зафиксированный цикл: вопрос → источники → вклад → критика в
отдельном AI-контексте → решение и датированный checkpoint. Его результатом
может быть эссе, отдельный аргумент, уточнение или обоснованный отказ от идеи.
Одно эссе может проходить несколько раундов с явными связями версий и кандидатов.

- Цель лаборатории — первое место в конкурсе; выбирать действия по их вкладу
  в оригинальность и философское качество будущих работ.
- 6000 слов без библиографии — верхняя граница конкурсного эссе. Не задавать
  минимальный объём или цель приблизиться к потолку, особенно для первых пилотов.
- Объём определяется тем, что нужно для ясного раскрытия и достаточного
  обоснования тезиса, работы с существенными возражениями и источниками.
  Искусственное удлинение и сокращение за счёт аргумента нежелательны.
- По возможности искать самостоятельный, нетривиальный вклад и новый угол
  относительно существующей философии. Желательная «ортогональность» — вкус
  пользователя, а не требование экзотики или основание объявлять новизну без
  проверки литературы. Темы, тезисы и аргументы выбирает и разрабатывает AI.
- Длина, число эссе и число пройденных раундов сами по себе не показатели успеха.
  Число первых пилотов — пересматриваемое решение; ограничение трёх конкурсных
  подач не ограничивает число внутренних кандидатов и исследовательских раундов.

Рекомендации действуют со следующего явно запущенного раунда и связываются с ним
как текущая версия инструкций. Они не меняют происхождение исторических
результатов, не доказывают превосходство метода и не запускают генерацию.

Подтверждение пользователя 8 сентября 2026: даже обычные правки и форматирование
эссе выполняет Codex по зафиксированному запросу. Пользователь читает, выбирает
и даёт допустимый нейтральный feedback; содержание развивает AI.
Для разрешённой серии pilot10-20260908 каждый автор и каждый критик работает
в свежем контексте с одной ветвью. Общий resume обновляется координатором после
завершения всех десяти, чтобы ранние результаты не попадали к поздним авторам.
Канонические стадии и checkpoints сохраняются по мере выполнения.

## Технический протокол

This protocol launches no model, paid API, task or background process. The agent
performs ordinary explicit work inside this lab, captures original records at
each boundary, and uses the helper to save exact artifact versions.

1. Read START_HERE, current resume, active method and applicable profile. For a
   competition round, recheck official rules and use an appropriate fresh
   context. Keep the historical planning catalog outside default research input.
2. Probe only the current exact session using capture_codex.py; consult CAPTURE.
   A failing/unavailable collector must be resolved before dependent work, or the
   segment is explicitly incomplete. Never claim full Desktop recording.
3. Start with a unique run ID, actual session ID, purpose and explicit inputs:
   `python3 scripts/philosophy_round.py start --run R001 --session ACTUAL_ID --purpose research --input RELATIVE_SOURCE`
   Exact method/instructions/configuration/inputs become immutable object refs.
   Supply `--stage-id` and `--selection-round-id` for the actual project phase and
   selection cycle. A changed configuration creates a new linked lab epoch;
   `--epoch-event` may name a previously recorded matching epoch. Never reuse an
   epoch label to conceal a changed method or helper implementation.
4. AI selects or sharpens one question. Save its exact output artifact, capture
   its original message/tool event, then record it:
   `python3 scripts/philosophy_round.py record --run R001 --stage question --file notes/question.md --session ACTUAL_ID --evidence CAPTURE_EVENT_ID`
5. Read relevant primary sources. Preserve exact accessed text/files needed to
   reconstruct the argument, URL, access time, locators, quote limits and gaps.
   Record stage `sources` with `--source-note` describing actual retrieval.
   User-provided or unreachable content remains labelled accordingly.
6. Develop one AI contribution with explicit premises, conclusion, uncertainties
   and source dependencies. Save and capture before recording `contribution`.
7. Obtain actual AI critique in a separate context. Supply the exact question,
   source and contribution versions. Preserve the original answer and its
   session capture. Record `critique` with that distinct session ID. Do not
   invent critique, intellectual independence, model metadata or source checks.
8. AI records a decision and justification, including disagreement, failure and
   reopen triggers; a human selection is separately recorded as human input.
   Record `decision`. Supported stages stay in order; older attempts remain.
9. Capture the final bounded segment for each participant. Prepare one JSON
   checkpoint with nonempty fields: question, outcome (CONTINUE/REVISE/SET_ASIDE,
   or COMPLETE_TECHNICAL for a technical demo), contribution, criticism,
   limitations, next_step, method_change, comparability, coverage_boundary.
   `python3 scripts/philosophy_round.py checkpoint --run R001 --summary notes/checkpoint.json --coverage COVERAGE_ID --coverage CRITIC_COVERAGE_ID`
   This appends the canonical dated checkpoint and terminal. An explicit
   `--incomplete` checkpoint preserves an interrupted segment; it does not turn
   loss or an unknown outcome into success.

`pause --run R001 --reason TEXT` and `resume --run R001 --reason TEXT` record
stopping and continuation. After a crash, `research_archive.py recover` is an
audit; unresolved attempts remain unresolved. Do not rerun an external operation
just because its outcome is unknown. Examine exact history before retrying.

`refresh` rebuilds resume/checkpoint index/readable archive. Change a method by
writing a new immutable version and starting a new bound round; explain motive,
effective start, effect on comparison, and provenance link to the former round.
The five-stage engine accepts changed strategies within those stages. A new
stage topology requires a versioned protocol extension, without deleting history.

Register every new essay, thesis or idea with `research_timeline.py candidate`
before the next dependent step; see `docs/TIMELINE.md`. Bind its exact artifact,
run start, epoch, phase, selection cycle and origin/parent candidates. Preserve
birth-time uncertainty and distinguish independent ideas from merely parentless
records. Record rejection/reopening as new decisions. `research_timeline.py weekly`
builds the weekly schedule and candidate-origin table from the same archive.
Explicit activity observations preserve known model labels and wall intervals;
they never estimate hidden thinking time. These are private derived views, not
an authorized publication or a selected final exhibition design.

For a clean new lab, import the archive as historical evidence and explicitly
choose whether to link a new round to it. Scoped export includes causal closure
and exact object dependencies; review exclusions before any external release.

## Authorized extension: judges-v1, 2026-09-12 UTC

The new user-approved Claude bridge allows manuscript work by either Codex or
Claude, keeping the same human/AI provenance distinction. Earlier Codex-only
wording above describes the historical pilot arrangement.

For judges20-20260912, the first fresh named-judge reviewer supplies the canonical
critique stage; a second fresh reviewer supplies a captured `round.judge_review`
event before the author's decision. Both review originals, exact profile bytes
and source snapshots are retained. The author responds to both, retaining
justified disagreement. The five-stage topology remains intact and the method
change is explicit; no equivalence to prior pilots or actual judging is claimed.
Global summaries and ranking occur only after manuscripts are sealed.

## Биография до зависимого шага — 2026-09-21

Использовать docs/ESSAY_BIOGRAPHIES.md и scripts/essay_lineage.py.
До генерации из выбранной идеи записать origin/idea/selection с точными родителями;
до использования критики или результата турнира сохранить соответствующую запись.
Для каждого нового draft/critique/revision/final указать предшественников, точные
версии, входы, модель/effort и workflow. Не считать общий лог достаточной биографией.
Турниры связывают версию каждого участника с судьёй, критериями, порядком и исходом;
проигравших не удалять. Не переходить к зависимому шагу после ошибки записи.
Checkpoint автоматически сохраняет инвентарь; содержательные связи он не угадывает.
