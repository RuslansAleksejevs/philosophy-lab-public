# История работы — expedition-03, draft-001

Дата кампании: 27 сентября 2026, America/Los_Angeles. Это только первичная авторская фаза. Рукопись `draft-001.md` не проходила независимую критику и не является финалом.

## Задание и конфигурация

- Run: `hundred-20260925-expedition-03`; entity: `hundred-20260925/expedition-03`.
- Нативный UUID авторского контекста: `01a0e27a-8f77-7932-99b8-5e1761d716fa`.
- Запрошено в неизменяемом init: `gpt-6-luna / xhigh`. Нативное локальное наблюдение для этого контекста также указывает `gpt-6-luna / xhigh`; оно не доказывает точную серверную модель, скрытую маршрутизацию или длительность рассуждения.
- Init: `init.json` (SHA256 `34c59ab3b5cef610146c8be6f02b2eff01b780f071e405492783a9dd5d7e6b18`); init receipt `init.receipt.json` (SHA256 `f607f22ae17b037853650f1fd4760630ec3dbf406ef84ce60131775fbcdb8a91`). Plan event `event-eecdc817d0314bc08f8fb52f5e9c324a`; start `event-a932083da6f545f88679510fe3498acc`; lineage `event-3bac8b56a514436794301cd27408b2c6`; origin lineage `hundred-origin:68ea3dbd20086ffda9e4b76ea54a0165`.
- Метод связан с `methods/hundred-six-v1.json`; его заданная топология требует question, sources, contribution, critique и decision. В этой авторской фазе завершены только первые три содержательные этапа. Критика и решение остаются будущими стадиями другого разрешённого контекста; это не пройденный gate.
- Новый пакет включил повторную ручную сверку правил `competition/RECHECK_20260927_RU.md`; bound copies `rules.txt`, `faq.txt` и `RULES_SUMMARY.md` оставлены неизменными. После успешной подготовки immutable init входы не менялись.
- Запись `runs/hundred-20260925/resume-20260927/METHOD_CHANGE_RU.md` фиксирует смену запрошенной конфигурации кампании с прежних Astra/ultra-контекстов на Luna/xhigh и ограничение сопоставимости. Этот результат нельзя считать контролируемым сравнением моделей с прежними эссе.

## Ход и архивные события

| Этап | Успешный receipt / событие | Содержание и граница |
|---|---|---|
| Инициализация | plan `event-eecdc817d0314bc08f8fb52f5e9c324a`; start `event-a932083da6f545f88679510fe3498acc`; lineage `event-3bac8b56a514436794301cd27408b2c6` | Иммутабельный план с точными inputs, методом и запрошенной конфигурацией. |
| `question-001` | receipt `event-b07ed0a354824d27a540d1ed465e0b3f`; stage `event-edf43f6878e04ac5a8fa1b181bdc26e`; coverage `event-34195ffed63b48fc8aee464fb1e30e27`; candidate `candidate:hundred-0bf1337a7a9c453d6b07fa2472ed78f5` | Первоначально выбран широкий вопрос о Кавендиш и микроскопическом знании. Сохранены альтернативы: повар Дин в «Чжуан-цзы», «Критон» Платона, письма 94–95 Сенеки (`question-selection.json`). |
| `sources-001` | receipt `event-b583f3145de2469c9f740eae48705669`; stage `event-f17d00f7a1d94cac835ec2be782fcd1b`; coverage `event-a569e53ff8504f14a7646e9bc3710038`; canonical source `event-2d3aa1318b41418b9c2a693ced37da51`; lineage `event-e885918ffdb24c089ffdcc5ab5837792` | После чтения источников широкий тезис был отвергнут как слишком знакомый и вопрос сужен. Сохранены оригиналы/доступные транскрипции, source manifest, retrieval failures, журналы поиска, границы чтения и novelty gate. |
| `question-002` — неполная попытка | stage `event-4835f7a648d040fa85ea7788965938f1`; capture `event-849043d89f5148b9a50a377bc4efc05e`; coverage `event-f7c75ee265c24a18a3e11836b5486208`; **успешного receipt нет** | Архив отказал в канонической записи: `stage replay conflict; append a new linked revision/round`. Попытка сохранена в `archive-incident-question-002.json` (SHA256 `172ca8c938c924edb5f9392b707ce4437bf60cad9d77f052ebd1c278f78cee7d`) и остаётся неполной. |
| `question-recovery-001` — отказ до подготовки | receipt/stage отсутствуют | Попытка сделать неполную запись родителем была отклонена до prepare: `parent archival attempt is incomplete; replay its record first`. Инцидент сохранён в `archive-incident-question-recovery-001.json` (SHA256 `7ed1ceca5a27ee2c649f83dd7a4b5b3bd84c071e5c69d0302379b58113977937`). |
| `question-recovery-002` — связанная корректировка | receipt `event-fab396424f9d43e9a1d5999129d928e5`; stage `event-2ca55166804f4c23874e84e3238c4c18`; coverage `event-787de0ba4c9a459b8961af59da8e412f`; candidate `candidate:hundred-0be4f4a2c6b42b2b9193c56e6fcc4f61` | Повторно аттестован тот же суженный вопрос, связанный только с успешными `question-001` и `sources-001`. Это не ремонтирует и не выдаёт неполный `question-002` за завершённый. Артефакт `question-recovery-002.json`, SHA256 `9204ccc0a7390236357be352fe5fd4ef9ba8540bf61b973c0064edb23d1645bc`. |
| `contribution-001` | receipt `event-a7f0d902f8354619ad98a73e79a53bfa`; stage `event-51f02f50b0b14172a2ebe4799a5e7938`; contribution `event-e21826d632064bcdb7619f65bfab64fd`; coverage `event-c4f246084d394a0683868f98f64ae537`; lineage `event-5d1f86889a834e02a2d98710104d8922`; candidate `candidate:hundred-7ba970ae536e136641b69da04b7f3052` | Авторская рукопись и обязательные приложения записаны после успешных источников и связанного вопроса. |

Дополнительная неудачная подготовка источникового marker из-за путей manifest записана в `archive-attempts.json`; stage record тогда не был создан. Исходные неудачные попытки не удалялись. Более поздний `sources/search-log-supplemental.json` — только библиографическая проверка выходных метаданных Clucas/Birkbeck/Cambridge, выполненная после sealed contribution; она не меняла рукопись и не служила её основанием. Файл сохранён для provenance отдельно от contribution packet.

## Источники и фактическое покрытие

Основной текст — Margaret Cavendish, *Observations upon Experimental Philosophy* (1666; Cambridge/O’Neill edition, 2001). Сохранён PDF-скан издания и локальный текстовый excerpt печатных страниц 47–61 (PDF 96–110); полностью прочитаны релевантные главы “Of Micrography, and of Magnifying and Multiplying Glasses” (pp.49–52) и “Of the Eyes of Flies” (pp.59–60). Это английское издание, отдельный перевод не использовался.

Robert Hooke, *Micrographia* (1665), Observation XXXIX, прочитано целиком по транскрипции Wikisource, строки 113–155, revision `oldid=10505748`; локально сохранён выбранный excerpt с более полной парафразой. Первое издание и запись Wellcome использованы для идентификации; скан не сверялся построчно.

Stephen Clucas (2022), глава о риторике микроскопического изображения, прочитана только в excerpts PDF pp.2–4, 12–16, 20–26; Purcell (2025), только релевантные journal pp.56–57 / PDF pp.18–19 (pp.54–55 использованы для локализации); обе работы не прочитаны полностью. Статья Emma Wilkins (2014) не была прочитана: были доступны лишь метаданные/короткий поисковый snippet, а запрос PDF вернул HTML interstitial. Эти пределы описаны в `sources.note.md`, `sources/source_manifest.json`, `sources/retrieval-failures.json` и `sources/search-log.json`. Современная энтомология не изучалась; рукопись не делает выводов о биологической точности исторических моделей.

## Вопрос и novelty gate

Начальный кандидат «может ли микроскоп раскрывать скрытую структуру природы?» отвергнут как слишком знакомый: Clucas уже подробно касается эпистемологии микроскопических изображений, Кавендиш, Хука и примера с глазами мух. Суженный вопрос: что значит «perfect eye» у Хука применительно к отдельным фасеткам, и направлено ли поведенческое возражение Кавендиш против локальной оптической функции или против интегрированного зрения животного?

Защищаемое здесь — только ограниченная реконструкция. Хук даёт небезосновательные, но опровержимые доводы за оптически значимые локальные части и сам не выводит из их числа улучшенное зрение всего животного. Кавендиш справедливо требует не выводить орган или способность из одного счёта видимых бугорков; пример с пауком и холодом, однако, сам по себе не опровергает локальную функцию фасеток. Сильнейшее возражение — что Хук и без того проводит это различие, а эссе лишь переформулирует его текст. Никакой глобальной новизны или оригинальности не заявлено; gate остаётся предварительным.

## Рукопись и приложения

- `draft-001.md` — “What Counts as an Eye? Hooke, Cavendish, and the Levels of Fly Vision”; SHA256 `d38db05ce0e52a855af19a0ce568c1d6db90663a1cfbc0998b9d7aeb0dc36896`.
- Объём по зафиксированному Unicode-token методу: 3,073 слова без библиографии; 3,186 с ней; лимит 6,000 без библиографии.
- `argument-map.md`, SHA256 `35c9d1b3256ed04f2765c2302cbe645e2232f714ecebbef40cb5a3e776607fb8`.
- `self-assessment.md`, SHA256 `570d9e840d232055a7f4c47614a8ea00cb294568238a4d105107df99a91f2e06`; это авторская самооценка, не критика.
- `draft-001-text-accounting.json`, SHA256 `a572f5f969112b50304ccea4bef23654cd860b5c092fb376f3beff794b0b887a`.
- `draft-001-precopy.md`, SHA256 `468f0d645ec1b09ceb1685ae989801b17573a93c0db5611443421043f39a904f`; и `draft-edit-log.json`, SHA256 `c033bd5ca9aa892a064db8ba34b2d4f7f11d29fd6fb840b724f7a15b52808a89`, сохраняют исходный вариант и последующую правку.
- `sources.note.md` SHA256 `4742c1ec8bba83bd7d136fbc1ca224174e9128b93f80193ffa9e0c6c2b0e1e1b`; `novelty-gate.json` `ff35ae430f684a40c1c0b8039c572671f505a3477cbce30418f472fe6d721716`; `sources/source_manifest.json` `576d10eb6f59775a0abb83f22a3b7b35efd348ba045ce623636e0a7a6754e21a`.
- Поиск: `sources/search-log.json` SHA256 `005c2c8234e80859230f1b571dcdae4d6e0db88c41657b3f8267bfa6aedf9c04`; поздняя библиографическая проверка `sources/search-log-supplemental.json` SHA256 `60aa92715ea6f8495802e865d6e09daa2af6bd186114741e6ba0fb2c432c8005`; недоступные материалы `sources/retrieval-failures.json` SHA256 `45e149e080143c8823761ed566bc099d8e7d73e8381bebc292feb95d3bd0b422`.

## Граница завершённости

Это завершённый авторский `draft-001`, а не законченное финальное эссе. Независимый критик не запускался и не имитировался. Доработка, итоговое решение и финальный checkpoint не создавались. Следующий процессный шаг — передать только запечатанные материалы этой работы свежему независимому критику в отдельном разрешённом контексте и продолжить по методу. Не делать выводов о победе, качестве конкурса или готовности подачи.
