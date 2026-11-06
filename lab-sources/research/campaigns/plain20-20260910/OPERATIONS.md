# PLAIN20: локальная фиксация стадий

Это нейтральная техническая инструкция. Автор читает общий AUTHOR_BRIEF.md,
campaign.json и только собственный каталог essay-NN. Исторические эссе,
содержимое других кандидатов и глобальные производные обзоры в контекст автора
не загружаются. Скрипт читает метаданные разрешённых локальных сессий для
единственного точного agent_path; открывает native-файл только выбранной
собственной сессии. Не используйте ручной обзор других сессий для поиска себя.

Ниже 31 — пример; каждый агент подставляет свой номер 31–50. Все команды
выполняются из корня лаборатории. Каждый вызов печатает только локальные ID,
хеши и стадию. Записи JSON в собственном каталоге являются неизменяемыми
квитанциями; одинаковый повтор допустим, изменение прежней записи запрещено.

Перед началом координатор проверяет действующую службу сборщика и свежую
полноту текстового охвата. Обязательная ошибка архива останавливает зависимую
работу: сохраните файлы, сообщите координатору точную ошибку и не объявляйте
стадию завершённой. Не подделывайте marker, native ID или квитанцию вручную.

Автор начинает раунд до философской работы:

```sh
python3 -B scripts/plain20_artifacts.py init --essay 31 --agent-path /root/essay_31
```

Старт связывает точные байты AUTHOR_BRIEF.md, campaign.json, этой инструкции,
самого helper, метода simple-v1 и действующих лабораторных инструкций.

Порядок: question → sources → contribution → critique → decision. Перед
переходом к следующей стадии сохраните непустой артефакт в essay-31, вычислите
SHA-256 файла и отправьте **настоящее видимое сообщение assistant commentary**
с точным marker. Строка в tool output, коде или файле таким сообщением не
является. Отправляйте каждый marker ровно один раз; неопределённость наличия
сообщения сначала разрешите повтором команды фиксации, а не дублированием.

Пример последовательности для вопроса:

```sh
shasum -a 256 research/campaigns/plain20-20260910/essay-31/question.md
```

Отдельное commentary: `[PLAIN20:31:question sha256=ТОЧНЫЙ_64_ЗНАЧНЫЙ_SHA256]`.

```sh
python3 -B scripts/plain20_artifacts.py record --essay 31 --agent-path /root/essay_31 --stage question --file research/campaigns/plain20-20260910/essay-31/question.md
python3 -B scripts/plain20_artifacts.py record --essay 31 --agent-path /root/essay_31 --stage sources --file research/campaigns/plain20-20260910/essay-31/sources.md --source-note 'State actual retrieval, saved source coverage, and any unavailable source surfaces.'
python3 -B scripts/plain20_artifacts.py record --essay 31 --agent-path /root/essay_31 --stage contribution --file research/campaigns/plain20-20260910/essay-31/draft.md
```

Каждая из последних двух команд также требует предварительного собственного
commentary с marker `sources` или `contribution` и хешем соответствующего файла.
В --source-note передайте фактическое описание получения и охвата источников,
а не оставляйте пример. Сохраняйте использованные первоисточники или их
реально прочитанные фрагменты в собственном каталоге с URL и датой получения.

Вопрос автоматически регистрируется как исходный thesis-кандидат, вклад —
как ORIGINAL essay-кандидат до продолжения. Время начала написания неизвестно;
время наблюдаемого hash-сообщения сохранено отдельно и не заменяет его.

После contribution автор завершает текущую фазу и сообщает координатору о
готовности. Координатор запускает отдельный чистый контекст /root/critic_31;
критик читает только материалы назначенного essay-31, сохраняет critique.md,
вычисляет его SHA-256, отправляет собственный commentary
`[PLAIN20:31:critique sha256=ТОЧНЫЙ_64_ЗНАЧНЫЙ_SHA256]` и выполняет:

```sh
python3 -B scripts/plain20_artifacts.py record --essay 31 --agent-path /root/critic_31 --stage critique --file research/campaigns/plain20-20260910/essay-31/critique.md
```

Критик не вызывает init. Разные native-сессии автора и критика обязательны;
отдельный контекст не доказывает независимость суждения или точность критики.

Координатор возобновляет автора для ответа на собственную критику. Автор
сохраняет decision.md с решением и final.md с окончательной версией эссе,
вычисляет оба хеша и отправляет commentary с **обоими** marker:

`[PLAIN20:31:decision sha256=SHA256_DECISION]`
`[PLAIN20:31:final sha256=SHA256_FINAL]`

```sh
python3 -B scripts/plain20_artifacts.py record --essay 31 --agent-path /root/essay_31 --stage decision --file research/campaigns/plain20-20260910/essay-31/decision.md --final-file research/campaigns/plain20-20260910/essay-31/final.md
```

Оба точных сообщения/marker захватываются с BOUNDED_COMPLETE; final.md
сохраняется отдельным объектом, DERIVED essay-кандидатом с исходным вкладом
как родителем и final_sha256 в квитанции. Если decision.md сам содержит
полный окончательный текст, допустимо опустить --final-file; тогда он же
будет окончательным артефактом, отдельный final-marker не нужен.

Автор создаёт checkpoint.json в собственном каталоге. Все поля ниже обязательны,
должны содержать конкретные непустые строки. outcome имеет только значения
CONTINUE, REVISE или SET_ASIDE; завершение пилотного процесса не является
сертификатом философской истинности или конкурсной готовности.

```json
{
  "question": "Actual question",
  "outcome": "CONTINUE",
  "contribution": "Actual defended contribution",
  "criticism": "Strongest criticism and response",
  "limitations": "Remaining limitations",
  "next_step": "Concrete next action",
  "method_change": "Actual changes, or none",
  "comparability": "Boundaries on comparison with other runs",
  "coverage_boundary": "Exact marker lines and artifact snapshots; broader visible text recorded by collector; no hidden reasoning or provider trace"
}
```

```sh
python3 -B scripts/plain20_artifacts.py checkpoint --essay 31 --agent-path /root/essay_31 --summary research/campaigns/plain20-20260910/essay-31/checkpoint.json
```

Checkpoint использует все пять стадий и охват всех marker, включая final.
Канонические проверки и terminal-событие выполняет philosophy_round.checkpoint.
Только запись производных глобальных обзоров отложена: координатор вызывает
`python3 -B scripts/philosophy_round.py refresh` после закрытия всех двадцати.
Автор не читает глобальные обзоры. При ошибке не переходите к следующей
стадии и не переписывайте прежний артефакт: сообщите координатору, сохраняя
оригиналы и незавершённый статус до проверяемого исправления.

Вклад — полный draft.md, не отчёт/аннотация. Ждите exit 0 каждого обязательного вызова: session_id означает, что процесс ещё идёт. Отдельный архивный put при необходимости: `python3 -B scripts/research_archive.py --root research/archive put ПУТЬ`. Не создавайте другой архив.
