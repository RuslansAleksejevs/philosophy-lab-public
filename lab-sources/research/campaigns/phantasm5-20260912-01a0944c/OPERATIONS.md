# Фиксация своей ветви

Только свой каталог essay-XX. Все команды из корня лаборатории. Подставьте свой номер 01–05. Helper: scripts/phantasm5_01a0944c_artifacts.py. Автор /root/phantasm_author_XX, критик /root/phantasm_critic_XX. Не запускать старые campaign helpers.

Перед содержательной работой:
`python3 -B scripts/phantasm5_01a0944c_artifacts.py init --essay XX --agent-path /root/phantasm_author_XX`

Каждую стадию сначала сохранить в новом файле (не переписывать старое), вычислить `shasum -a 256 FILE`, затем отправить настоящее отдельное assistant commentary:
`[PHANTASM5:XX:question sha256=ACTUAL_SHA256]`
Используйте вместо question точную стадию sources/contribution/critique/decision; final — для окончательной рукописи. Marker ровно один раз; tool output не заменяет commentary. После этого:
`python3 -B scripts/phantasm5_01a0944c_artifacts.py record --essay XX --agent-path /root/phantasm_author_XX --stage question --file research/campaigns/phantasm5-20260912-01a0944c/essay-XX/question.md`

Порядок question → sources → contribution (draft.md). Sources требует `--source-note 'Конкретный фактический охват чтения и ограничения'`. Сохраните реально прочитанные источники/фрагменты в sources/ с метаданными, URL, датой и локаторами. Архивируйте каждый файл источника через `python3 -B scripts/research_archive.py --root research/archive put PATH` до фиксации sources; результат с sha256 включите в sources.md или sources-manifest.json. Никакого другого архива.

Перед зависимым шагом дождаться exit 0 каждого mandatory-вызова. session_id в exec означает, что процесс идёт; получить результат через write_stdin. Архив может ждать общую блокировку; не убивать процесс и не удалять lock. Ошибка mandatory-записи останавливает следующую стадию: сообщить root. Никогда не рисовать квитанции или native ID вручную.

После contribution сохранить author-notes.json и завершить DRAFT_READY. Критик назначается root отдельно, не делает init, читает только свою ветвь, сохраняет critique.md, отправляет PHANTASM5:XX:critique и вызывает record с --agent-path /root/phantasm_critic_XX.

После возобновления автор читает critique.md, сохраняет final.md, revision.md, decision.md. Отдельное commentary может содержать два marker: decision с хешем decision.md и final с хешем final.md. Затем record --stage decision --file .../decision.md --final-file .../final.md. Это сохраняет исходный draft и отдельный конечный кандидат.

Создать checkpoint.json с непустыми строками: question, outcome (CONTINUE/REVISE/SET_ASIDE), contribution, criticism, limitations, next_step, method_change, comparability, coverage_boundary. Не сертификат истины. Указать точный охват: собственные hash-commentary и снапшоты артефактов; общий видимый текст собирается отдельно; скрытые рассуждения и provider trace недоступны.
`python3 -B scripts/phantasm5_01a0944c_artifacts.py checkpoint --essay XX --agent-path /root/phantasm_author_XX --summary research/campaigns/phantasm5-20260912-01a0944c/essay-XX/checkpoint.json`

Сохранить final-notes.json и HISTORY.md, перечисляющий собственные версии, стадии и существенные ограничения. Никакого глобального refresh: helper откладывает только обновление общих обзоров, сохраняя канонический checkpoint. Координатор агрегирует после запечатывания всех пяти эссе.
