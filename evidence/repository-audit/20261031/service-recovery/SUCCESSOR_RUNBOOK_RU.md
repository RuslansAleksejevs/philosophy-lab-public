# Отдельная попытка после исправления двух индексов

Команды ниже **не выполнены**. Root сначала подтверждает успешный выход
полных проверок и отдельно даёт сигнал baseline/start. Production pins уже
заданы в CONTRACT, но сам CONTRACT не доказывает установку. Предыдущая
попытка PID 40522 сохранена в prior-attempt/STOP_RECEIPT.json; никаких её
курсоров, событий или временных файлов не удаляли.

Рабочая папка — корень Philosophy Lab. Перед запуском должны завершиться
все research/closure/validation writers. Второй параллельный writer,
collect-once и reconcile запрещены этим планом.

## 1. После отдельного сигнала root

```sh
python3 -B runs/repository-rebuild-20261031/history-audit/service-recovery-performance/prepare_successor_baseline.py --save
```

Команда проверяет установленные bytes, прежние 20 принятых событий по точным
sequence/hash, историческую closure, 21 SID, фактическое отсутствие прежних
PID и launchd service, неизменный последний frontier после stop. Она только
читает архив и сохраняет новый локальный execution/BASELINE.json. Повтор
не перезаписывает папку. Ошибка ps/launchctl не считается доказательством
отсутствия процесса. Для sandbox denial нужен тот же разрешённый scoped вызов.

## 2. Один обычный start для этой отдельной попытки

```sh
python3 -B scripts/collector_service.py start
```

Сохранить фактический exit code, UTC, свежий launchd PID, args/cwd и hash
baseline в новом execution/SERVICE_START.json. Не использовать PID 40522,
не менять приоритет, не запускать повторный start. Один успешный start здесь
означает второй запуск во всей истории восстановления, а не один запуск
за весь день. Наблюдать можно cache/status metadata без нового audit.

## 3. Первый завершённый poll

Ниже вместо ACTUAL_NEW_PID подставляется подтверждённый новый PID. Эта
команда вызывает **неизменённый frozen probe V2** с новым contract.

```sh
python3 -B - ACTUAL_NEW_PID <<'PY'
from pathlib import Path
import hashlib, json, subprocess, sys
root = Path.cwd()
history = root / 'runs/repository-rebuild-20261031/history-audit'
lane = history / 'service-recovery-performance'
probe = history / 'service-recovery-plan/probe_first_poll_v2.py'
if hashlib.sha256(probe.read_bytes()).hexdigest() != 'c345be22562b29a171c016544e719233f7574333789fdc5a134dbc43bb967eab':
    raise ValueError('Frozen probe changed')
b = json.loads((lane / 'execution/BASELINE.json').read_bytes())
args = [sys.executable, '-B', str(probe), '--root', str(root),
        '--pid', str(int(sys.argv[1])), '--started-after', b['started_after'],
        '--baseline-frontier', str(b['archive_sequence']),
        '--contract', str(lane / 'CONTRACT.json'),
        '--contract-sha256', b['contract_sha256']]
for sid in b['required_sessions']:
    args += ['--required-session', sid]
r = subprocess.run(args, capture_output=True, text=True)
print(r.stdout, end='')
if r.returncode == 0:
    result = json.loads(r.stdout)
    if result['status'] != 'PASS_SERVICE_RECOVERY_BOUNDED' or len(result['checks']) != 14 or not all(result['checks'].values()):
        raise ValueError('All fourteen checks required')
    with (lane / 'execution/FIRST_COMPLETED_POLL.json').open('x') as f:
        f.write(r.stdout)
raise SystemExit(r.returncode)
PY
```

WAITING до публикации полного нового poll ожидаем. PASS требует свежий PID,
новый collector.version, текущие signatures всех обычных курсоров, все 21 SID,
отсутствие source errors и согласованные schema2 views. Исторические gaps
и pending tools остаются явными; service PASS не означает полный экспорт
всех служебных инструментов. Оставить службу работающей, второй poll не ждать.

При экспорте связать новый PASS, baseline/start, старый stop/start, два
production hashes, reviewed candidate/tests, installation/full-check receipts,
неизменённый probe и ограничения. Не копировать raw cache/status или source
bodies в публичные административные evidence.
