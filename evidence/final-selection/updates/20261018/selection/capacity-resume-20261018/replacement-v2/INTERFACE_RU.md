# V2: две отдельные замены пустых capacity-попыток

Это новая техническая версия после прямого возобновления пользователем того же
отбора на Astra. Она сохраняет v1, все START inputs, обе failure001 и все уже
принятые отзывы. Само наличие кода не запускает модели. Root выполняет реальные
шаги ниже после канонической приёмки текущего возобновления и остальных108 отзывов.

Исключения фиксированы: **M12-N2, затем M13-N2**. Для каждого разрешена только
одна новая физическая `attempt-002`; любое её существование запрещает повторный
запуск. Модель/effort/tier — исходные `gpt-6-astra/ultra/default`. Prompt/schema,
рубрикa, распределение3N+2J и сводка60/40 не меняются. Работник получает только
свой исходный prompt целиком, без истории ошибок и других оценок.

## Принятые исходные ссылки

Проверены только поля локальных квитанций, без чтения отзывов:

- original ready: `event-3a08660ab4024183b9acf41dc1fb7907`;
- resume: `event-1693b19527294cafa5cf61f9c1c801ee`;
- fresh user capture, сообщён root: `event-f63839cb8c6342b2afef5403f55f9ed8`;
- M12 failure: `event-b3519057c6a24486bca718c999d0a20e`, disposition:
  `event-9afcd19556934b8bbad8c4e2dc1564d9`;
- M13 failure: `event-1118f540c1644baf8ca3fea78bdacf12`, preserved stop:
  `event-fad5b6b2ca6c4b428771c20caaa2bf36`.

Resume authorization descriptor берётся из
`capacity-resume-20261018/ARCHIVE_RECEIPT.json.authorization`. Его настоящий SHA
`c480f1cbf5435596488eef0f118f439f2b0825f14d971c1a21a630b719ff9b8f`, 1046 bytes.
Это справочные ссылки; код заново проверяет actual events, parents, outputs,
local hashes/sizes и stored objects при выполнении root.

## Механическая подготовка и приёмка готовности

Все команды запускаются из этой папки. Аргументы путей ниже абсолютные.
Вместо `V2` root подставляет полный путь к этой папке. Defaults `--root` и
`--run-dir` указывают на текущий проект и исходный run.

```text
python3 -B ready_capacity_v2.py --prepare-request V2/READY_REQUEST.json --session-id ACTUAL_ROOT_SESSION
python3 -B ready_capacity_v2.py --request V2/READY_REQUEST.json
```

Первая команда **не открывает архив**: читает только точные metadata receipts
capacity-recovery-001, capacity-recovery-002, capacity-resume и REPLACEMENT_TESTS.
Она проверяет хеши файлов из test report и атомарно создаёт новый immutable
READY_REQUEST.json. Вторая команда открывает один writer, проверяет фактические
ссылки и сама создаёт два отдельных неизменяемых `M12-N2/PLAN.json`,
`M13-N2/PLAN.json`, два actual ready events и два `READY_RECEIPT.json`.
Не надо вручную собирать события или копировать job из queue.

Root может вместо первого CLI передать собственный descriptor в
`ready_with_writer(root,run,request_ref,writer)`. Exact request schema:

```json
{
  "schema": "capacity-replacements-ready-request.v2",
  "run_id": "final-selection-20261018",
  "session_id": "ACTUAL_ROOT_SESSION",
  "authorization": {
    "event_id": "ACTUAL_RESUME_EVENT",
    "artifact": {"path":".../AUTHORIZATION.json","sha256":"...","bytes":1046},
    "user_capture_event_ids": ["ACTUAL_FRESH_USER_FRAGMENT_EVENT"]
  },
  "failures": {
    "M12-N2": {
      "failure_event_id":"ACTUAL_M12_FAILURE",
      "preserved_state":{"event_id":"ACTUAL_DISPOSITION","kind":"research.selection.transport_disposition.accepted","status":"CAPACITY_DISPOSITION_ACCEPTED_BOUNDED"},
      "inspection":{"path":".../capacity-recovery-001/FAILURE_INSPECTION.json","sha256":"...","bytes":0}
    },
    "M13-N2": {
      "failure_event_id":"ACTUAL_M13_FAILURE",
      "preserved_state":{"event_id":"ACTUAL_STOP","kind":"research.selection.stopped","status":"SELECTION_INCOMPLETE_CAPACITY_STOP"},
      "inspection":{"path":".../capacity-recovery-002/FAILURE_INSPECTION.json","sha256":"...","bytes":0}
    }
  },
  "files": ["EXACT_SOURCE_TEST_REPORT_DESCRIPTORS"]
}
```

Показанные обозначения не являются готовыми данными. `files` — descriptors
`{path,sha256,bytes}`; команда подготовки заполнит их настоящими значениями.
Готовность связывает каждый plan, request и явные code/test/report files с outputs
actual `research.selection.replacement.ready`; у каждого события свой job ID.
Resume обязан быть `research.selection.resume.accepted`, связывать AUTHORIZATION
bytes и зависеть от свежего user `visible_fragment.captured`. Resume должен быть
потомком обоих сохранённых capacity states; user capture должен быть записан позже
них. Старые pause/disposition сами по себе замены не разрешают.

## Строгие гейты запуска

- Все остальные108 должны быть канонически `REVIEW_ARCHIVED`, с завершённой001.
  Прежние60 не запускаются заново; ещё48 обслуживает исходный frozen dispatcher.
- Обе готовности должны быть приняты и связывать одно текущее возобновление.
- Общий `dispatch.lock` исключает одновременную работу frozen dispatcher.
  Любой STOP.json блокирует запуск; этот код его не удаляет.
- Перед каждой заменой заново проверяется точная native001: 0 visible assistant,
  0 finals, исходный prompt/config, подтверждённые stop/drain, empty stderr,
  ровно известная capacity-error. Ошибка не считается отзывом или quota.
- Новый SID не должен совпасть ни с одной другой001/002, включая обе ошибки.
- M13 запускается только после принятого M12 review, lineage и per-job map.
  M13 review event прямо ссылается на actual M12 map event.
- Неполный ответ/внутренний retry/неверная schema дают карантин без новой попытки.
  Unknown event/tool/model/speed, quota или обычная ошибка дают stop. Attempt003 нет.

## Последовательные операции root

```text
python3 -B runner_capacity_v2.py --ready-receipt V2/M12-N2/READY_RECEIPT.json --check-only
python3 -B runner_capacity_v2.py --ready-receipt V2/M12-N2/READY_RECEIPT.json
python3 -B archive_capacity_v2.py --ready-receipt V2/M12-N2/READY_RECEIPT.json --map V2/M12-N2/ACCEPTED_ATTEMPTS.v2.json --map-receipt V2/M12-N2/ACCEPTED_ATTEMPTS_RECEIPT.json
python3 -B runner_capacity_v2.py --ready-receipt V2/M13-N2/READY_RECEIPT.json --check-only
python3 -B runner_capacity_v2.py --ready-receipt V2/M13-N2/READY_RECEIPT.json
python3 -B archive_capacity_v2.py --ready-receipt V2/M13-N2/READY_RECEIPT.json --map V2/M13-N2/ACCEPTED_ATTEMPTS.v2.json --map-receipt V2/M13-N2/ACCEPTED_ATTEMPTS_RECEIPT.json
python3 -B ready_capacity_v2.py --complete-maps
```

Archive helper поддерживает `--check-only` для местной проверки без archive writes.
Реальная архивация использует один writer и общий `archive-reviews.lock`.
Папки001 остаются точными исходными ошибками. У каждого logical job создаются
первые настоящие lane `ARCHIVE_RECEIPT.json`/`CAPTURE_RECEIPT.json` вне attempts.
В archive receipt: `accepted_attempt=2`, `physical_attempt=2`, exact `attempt_path`,
`replacement_ready_event_id`, `failed_attempt_event_id`. `input_event_id` остаётся
**исходным START ready**, а evaluation ID — `<run>:<job>:evaluation-v1`.
Failure001 evaluation не создавала. Review parents связывают original ready,
own replacement ready/failure, assigned version, exact visible capture;
M13 дополнительно связывает M12 map. Все новые receipts/maps пишутся атомарно.

## Карты и четыре потребителя

Каждая `Mxx-N2/ACCEPTED_ATTEMPTS_RECEIPT.json` имеет status
`ACCEPTED_ATTEMPTS_MAP_ARCHIVED`, logical_job_id, event_id, map descriptor и
ready_receipt descriptor. Per-job map schema `selection-accepted-attempts.v2`:
original input_event_id, ready_event_id, полный failed_attempt и accepted_attempt
`{number:2,path,session_id,event_id,files}`. Это actual post-success map;
ready, intent или карантин её не заменяют.

После обоих успехов `--complete-maps` создаёт в корне V2:

- `ACCEPTED_ATTEMPTS.v2.json`: schema `selection-capacity-map.v2`, input_event_id,
  `attempt_map_receipts` с descriptors ровно двух per-job receipts;
- `ACCEPTED_ATTEMPTS_RECEIPT.json`: status `CAPACITY_REPLACEMENTS_COMPLETE_ARCHIVED`,
  actual event_id и общий map descriptor;
- actual event kind `research.selection.capacity_replacements.accepted`,
  parents обеих per-job maps, outputs общего map и двух receipt objects,
  payload logical_job_ids `[M12-N2,M13-N2]`, accepted_replacements2,
  preserved_failed_attempts2, model_calls0.

`resolver_v2.load_resolution(root,run,group_receipt,events,get)` проверяет всю
цепочку и возвращает schema `selection-capacity-resolution.v2`, original input ID,
group map_event_id, safe evidence_files и `exceptions` с двумя проверенными
per-job resolutions. `resolve_job` возвращает001 для обычных108,002 для двух
исключений. Никаких перестановок папок, symlink, silent fallback или двойных голосов.

1. Архив — `archive_capacity_v2.py` для002, frozen archiver для остальных108.
2. Сводка — `summary_capacity_v2.py --map-receipt V2/ACCEPTED_ATTEMPTS_RECEIPT.json`.
   110accepted и 2failure отдельно, исходная агрегация. Детали — CONSUMERS_README_RU.
3. Приёмка — `validate_capacity_v4.py --plan /absolute/FINAL_PLAN.json --map-receipt V2/ACCEPTED_ATTEMPTS_RECEIPT.json`.
   Ровно22 версии/110отзывов/0..10пар/8+2/42protected/reading/reasons сохраняются.
   Любая третья failure или attempt003 отвергается.
4. Экспорт — `export_capacity_v2.py --map-receipt V2/ACCEPTED_ATTEMPTS_RECEIPT.json`,
   API `build(spec,root,resolution)`. Safe evidence обеих ошибок и group/per-job maps
   обязательны. Native-visible, raw, stdout/stderr не экспортируются. Root включает
   все полученные candidate.files в FINAL_RECEIPT и renderer accepted sources.

Pair-ready совместим с logical receipts: original input_event_id и phase=individual
сохранены. Root также связывает общий actual map event и его metadata как явное
dependency evidence. Предыдущие v1 helpers остаются сохранёнными и не используются
для новой двухошибочной приёмки.

## Closure и граница завершения

Новый closure request сохраняет прежнюю schema и добавляет
`validator:{name:"capacity-v4",code:<validate_capacity_v4 descriptor>,map_receipt:<GROUP receipt descriptor>}`.
Group map event явно входит в `selection_gate_event_ids`. Запуск:

```text
python3 -B closure_capacity_v2.py --validator capacity-v4 --map-receipt V2/ACCEPTED_ATTEMPTS_RECEIPT.json --request /absolute/CLOSURE_REQUEST.json
```

Python API принимает явные `validator_api=validate_capacity_v4.validate` и
`map_receipt`; frozen globals не подменяются. Штатный checkpoint разрешён прежним
явным `--allow-checkpoint-derived-updates`; original core gap остаётся INCOMPLETE.
FINAL_RECEIPT сообщает finite_selection_only, remaining_selection_work0,
preserved_failed_attempts2, actual group-map/failure IDs и реальные pending_goal_steps.
GitHub/collector/overall goal этот helper завершёнными не объявляет.

Тесты используют только искусственные тексты во временных папках. Popen/native
provider transport mocked; настоящий Archive и essay_lineage API проверены только
в disposable temp archive. Реальные отзывы, модели и canonical writers здесь не
запускались. Полный список проверок и source hashes — REPLACEMENT_TESTS.json.
