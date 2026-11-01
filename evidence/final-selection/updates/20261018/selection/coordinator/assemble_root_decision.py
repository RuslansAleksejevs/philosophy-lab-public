"""Root-authored decisions; mechanical assembly, no new evaluation or model call."""
import hashlib, json, pathlib

ROOT=pathlib.Path(__file__).resolve().parents[3]
R=ROOT/'runs/final-selection-20261018'
def read(p): return json.loads(p.read_text())
def encode(x): return (json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n').encode()
def write(p,x):
    data=(json.dumps(x,ensure_ascii=False,indent=2)+'\n').encode() if not isinstance(x,str) else x.encode()
    p.parent.mkdir(parents=True,exist_ok=True)
    if p.exists(): assert p.read_bytes()==data, str(p)
    else: p.write_bytes(data)
def ref(p):
    b=p.read_bytes(); return dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))

REASONS={
'E009':[
'Политика может ослабить положение человека настолько, что обещанная жалоба станет для него недоступна: нужны доказательства, деньги и исполнение решения.',
'Включаю в основные восемь, потому что эссе прослеживает всю эту цепочку и объясняет, почему защиту надо оценивать именно в условиях возможного ущерба.',
'Перед окончательным выбором остаётся уточнить, насколько надёжной должна быть такая защита; текст не доказывает, что любая несовершенная процедура запрещает политику.'],
'E012':[
'Фонд обещал хранить фотографии для будущих разбирательств, потерял их и заплатил компенсацию, но позднее его решение ошибочно используют как доказательство ложной жалобы.',
'Включаю в основные восемь: эссе показывает конкретную обязанность помочь с защитой, которую первая выплата могла не закрыть, и поэтому идёт дальше общего требования честно рассматривать жалобы в F01.',
'Нужно ещё проверить объём разумной помощи: фотографии могли показать прежнее наличие трещины, но сами по себе не доказывали вину подрядчика.'],
'E041':[
'Спойлер может лишить зрителя возможности сначала обоснованно понять произведение неверно, а затем самому пересмотреть это понимание.',
'Включаю в основные восемь, потому что здесь названа конкретная возможная потеря в восприятии произведения, тогда как E100 ещё не объясняет, почему невозможность возвращения сама по себе ценна.',
'Открытый вопрос — почему реальный пересмотр ценнее осведомлённого воображения такого пересмотра; общего запрета спойлеров из текста не следует.'],
'E050':[
'В построенной модели две системы одинаково отвечают на все постоянные удержания переменных, но после освобождения могут прийти к противоположным результатам.',
'Включаю в основные восемь: проверены и этот пример, и доказательство того, как последовательное освобождение позволяет получить нужный результат внутри указанного класса систем.',
'До окончательного выбора нужно установить значимость этого ограниченного результата и его отличие от прежних работ; доказательство не охватывает любые реальные системы.'],
'E055':[
'Сведения об ошибке автоматической системы могут не попасть к проверяющему, если их отбирает тот же механизм, который эту ошибку породил.',
'Включаю в основные восемь: эссе показывает, почему одного дополнительного проверяющего недостаточно, и различает помощь по отдельной жалобе и проверку всей системы.',
'В отличие от E009, здесь разобран именно путь сведений об ошибке; остаётся обосновать, какие ошибки должна охватывать проверка и какую надёжность от неё требовать.'],
'E079':[
'Одинаковые доли решений в эксперименте совместимы и с полным исключением запрещённого довода у части людей, и с частичным снижением его веса у всех.',
'Включаю в основные восемь: расчёт даёт конкретное альтернативное объяснение опубликованных результатов и ограничивает вывод о полном исключении довода из размышления.',
'Это не опровержение того, что люди вообще следуют правилам; перед окончательным выбором нужно ещё уточнить статистические соглашения исходной работы и новизну именно этого возражения.'],
'F02':[
'Удаление метки источника может сохранить сегодняшнюю уверенность и безошибочное рассуждение по оставшимся данным, но ухудшить использование завтрашней проверки.',
'Включаю в основные восемь: расчёт проверен, а вывод ограничен недостаточностью одной правильной работы с сохранившимися данными для оценки решения об удалении.',
'Все пять сравнений с E039 дали ничью; я выбираю F02 за более узкий вывод без дополнительной спорной обязанности хранить сведения, хотя историческая новизна обоих текстов остаётся открытой.'],
'F06':[
'Пробную общественную систему могут сделать настолько необходимой для помощи людям, что обещанная возможность отказаться от неё перестанет работать.',
'Включаю в основные восемь: эссе связывает первоначальное разрешение с конкретными действиями — заранее сохранить возможность отказа, получить новое разрешение либо исправить созданную зависимость.',
'Это даёт больше практических последствий, чем E047 и S02, но для неявного разрешения и слишком дорогого восстановления возможности отказа границы обязанности ещё нужно уточнить.'],
'E074':[
'Если несогласных участников объявляют неподходящими только из-за несогласия, согласие оставшихся перестаёт служить независимой проверкой практики.',
'Беру как один из двух перспективных текстов: он различает уход новичка, возражение выпускника и потерю навыка, поэтому помогает понять, чьё свидетельство отвечает на какой вопрос.',
'До основных восьми не поднимаю: в рассмотренном реальном случае не подтверждён отбор именно по религиозному согласию, а смешанные требования к навыку и убеждениям ещё нуждаются в разборе.'],
'E078':[
'Один участник может изменить совместную работу так, что другой будет вынужден продолжать помощь людям, хотя прежде мог её прекратить.',
'Беру как один из двух перспективных текстов: он объясняет, почему за сохранение чужого выбора обычно платит инициатор необязательного изменения, а при общих расходах ответ иной; все пять сравнений предпочли его E036.',
'До основных восьми не поднимаю, потому что ещё не решено, какое исходное распределение обязанностей справедливо и когда цена сохранения выбора становится чрезмерной.'],
'E036':[
'Дневник может помочь вернуть ошибочно исключённого человека в равную жеребьёвку, но это ещё не даёт ему права на дополнительный выигрышный шанс за найденные достоинства.',
'Пока оставляю вне десятки: различие полезно, однако главный запрет бонуса уже во многом следует из независимо принятого правила равной жеребьёвки.',
'В прямом сравнении все пять отзывов предпочли E078 за более развитое объяснение распределения расходов; версия E036 R1 сохраняется, а общий случай неравных заслуг остаётся нерешённым.'],
'E037':[
'Женщина искренне извиняется, но ошибочно объявляет себя единственной виноватой, и уже простившая её потерпевшая отказывается принять именно это описание.',
'Пока оставляю вне десятки: пример хорошо различает прощение и принятие извинения, но не исключает ответ, что перед нами два разных действия или неудавшееся извинение.',
'Для возвращения нужен довод, почему этот ответ не снимает возражение к рассматриваемой теории; неискренность или сознательная ложь здесь не доказаны и для примера не нужны.'],
'E039':[
'Можно правильно рассуждать сегодня и всё же удалить сведения, нужные для завтрашней проверки того же вопроса.',
'Пока оставляю вне десятки при сохранённой ничьей с F02: дополнительно требуемая обязанность хранить сведения зависит от спорного запрета избегаемой потери качества даже без других затрат.',
'Для десятки выбираю более узкий вывод F02; чтобы предпочесть E039, нужен убедительный ответ тому, кто допускает достаточно хорошее исследование без обязательного использования каждой бесплатной возможности улучшения.'],
'E047':[
'Участник может искренне одобрить программу, хотя его отказ не запустил бы обещанную независимую проверку, доступную без ухода из программы.',
'Пока оставляю вне десятки: текст убедительно различает действительное согласие и соблюдение процедуры, но после полноценного нового одобрения его результат может свестись к установлению прошлого нарушения.',
'F06 лучше показывает, какие действия всё ещё требуются; у E047 надо установить, когда остаётся обязанность исправления, а не только основание назвать прежнюю процедуру неправильной.'],
'E086':[
'Призыв доверять банку может поддержать его работу, но не заменяет проверку состояния банка и исправление найденных проблем.',
'Пока оставляю вне десятки: текст полезно разделяет проверку, исправление и публичное обещание, однако разобранный пример ещё не меняет конкретный спорный вывод о том, какую уверенность допустимо обещать.',
'Для возвращения нужен такой случай и его обоснованное решение; одного общего различия между полезной верой и доказанным обещанием здесь недостаточно.'],
'E098':[
'Чужое предупреждение может помочь человеку остановиться, даже если заранее никто не договаривался о помощи.',
'Пока оставляю вне десятки: текст верно отделяет умение воспользоваться предупреждением от авторства чужого наблюдения, но не до конца объясняет, когда это именно способность действующего человека, а не предоставленная ему возможность.',
'E055 точнее указывает условие, при котором помощь проверяющего сработает; для E098 нужно убедительнее отличить управление действием от простого возобновления управления после подсказки.'],
'E100':[
'Если остановить исполнение перед последней нотой, можно потерять само завершение произведения, а не сохранить его в наиболее ценном виде.',
'Пока оставляю вне десятки: этот довод защищает завершение, но ещё не показывает, почему невозможность снова увидеть или исполнить произведение сама по себе обладает художественной ценностью.',
'В E041 конкретная потеря при восприятии описана яснее, и все пять сравнений предпочли его; записи, повторы и сохранение искусства текст E100 в целом не запрещает.'],
'F01':[
'Организация обещает возмещение, но сама контролирует доказательства нарушения, к которым заявитель не имеет доступа.',
'Пока оставляю вне десятки: требование доступного рассмотрения жалобы обосновано яснее, чем более сильная обязанность защитить человека от оставшегося убытка.',
'E012 показывает конкретный дополнительный долг после уже выплаченной компенсации; F01 нужно уточнить, когда честного разбирательства недостаточно и почему тогда требуется дальнейшая помощь.'],
'F03':[
'Обнаруженная ошибка в одном мысленном примере может изменить доверие к другому, если обе реакции зависят от общего способа рассуждения.',
'Пока оставляю вне десятки: условный расчёт верен и включает последующее исправление ошибки, но реальная общая причина ошибок в обсуждаемом споре ещё не установлена, а предложенный опыт не проведён.',
'E074 и E078 уже подробнее различают случаи с разными выводами о свидетельствах или расходах; небольшой перевес F03 над F05 сам по себе не закрывает этот пробел.'],
'F04':[
'Ребёнок может перестать требовать обещанное от отца потому, что устал спорить, а не потому, что обязательство исчезло.',
'Пока оставляю вне десятки: текст убедительно показывает неоднозначность прекращения спора, но его сила против выбранной теории зависит от дополнительного перехода от изменения отношений к прекращению обязательства.',
'Этот переход в тексте признан отдельной предпосылкой; нужно показать, что оппонент действительно обязан его принять, иначе остаётся полезное уточнение, а не решающее возражение.'],
'F05':[
'Точное описание переживания после обучения наблюдению ещё не показывает, каким переживание было до обучения.',
'Пока оставляю вне десятки: текст правильно различает выводы о прежнем наличии и отсутствии признака, но не даёт подтверждённого описания того, как обучение меняет именно спорное переживание.',
'Нужно также установить, что реальные оппоненты говорят об одном и том же прежнем состоянии; без этого условный пример ещё не исправляет конкретный ошибочный вывод.'],
'S02':[
'Можно честно собрать гражданские собрания и всё же выбрать удобный ответ, повторяя их до первого одобрения.',
'Пока оставляю вне десятки: различие между подлинностью собрания, силой его свидетельства и правом отчёта считаться итогом убедительно, но положительное правило выбора итогового отчёта разработано слабее.',
'F06 яснее выводит обязанности из выданного разрешения; S02 нужен случай, где достаточные сведения и допустимые политические причины уже есть, а выбор итогового отчёта всё равно создаёт отдельную проблему.']}

main={'E009','E012','E041','E050','E055','E079','F02','F06'}
wild={'E074','E078'}
allocation=read(R/'ALLOCATION.json')['rows']
pairs=read(R/'summaries/PAIRS_COMPLETE/summary.json')
assert (pairs['review_count'],pairs['pair_count'])==(50,10)
p10=next(x for x in pairs['rows'] if x['pair_id']=='P10')
write(R/'coordinator/PAIR_REVIEW_NOTES_10.json',dict(
 status='COORDINATOR_FULL_READING_OF_ACCEPTED_PAIR_REVIEWS_NO_FINAL_SELECTION',pair_id='P10',
 candidates=['E036','E078'],reviews_read=[x['job_id'] for x in p10['reviews']],
 evidence_event_ids=[x['evidence']['event_id'] for x in p10['reviews']],batch_event_id='event-855342bdb34e4b44a4ac3eed2a9e5369',
 recorded_verdicts={'neutral':{'E078':3},'profile':{'E078':2}},profile_ids=['kacper_kowalczyk','henry_shevlin'],
 common_findings='All five narrowly prefer E078, medium confidence. E036 supplies the tighter conditional lottery inference and a useful correction-versus-bonus distinction. E078 gives a more substantive defeasible explanation of proposer payment, common costs, proportionality and repair before requested withdrawal. No historical priority established.',
 remaining_issues={'E036':'Independently justified equality does most distributive work; privacy does not yield numerical rights. Eligibility correction can itself require intimate proof. Comparative merit cases lack a general correction formula.', 'E078':'A fair existing distribution need not establish a unique protected continuation. Competing limited commitments and intermediate disproportionate sacrifices remain unresolved. Do not treat all safeguards as automatically proposer-financed.'},
 coordinator_text_check='Root already read both frozen manuscripts and re-read E036 lottery/correction passages; all five complete P10 reviews read in neutral-then-profile order. Conditional claims and limitations retained.',
 decision='Unanimous narrow preference supports E078 over E036, but does not establish automatic admission or resolve the substantive baseline problem.'))
decisions=[]
for row in allocation:
 cid=row['candidate']; bid=row['blind_id']
 ev=[read(R/f'results/{bid}-{role}/ARCHIVE_RECEIPT.json')['event_id'] for role in ['N1','N2','N3','J1','J2']]
 for p in pairs['rows']:
  if cid in p['candidate_ids']: ev.extend(x['evidence']['event_id'] for x in p['reviews'])
 decisions.append(dict(candidate_id=cid,version=row['version'],selection='main' if cid in main else 'wildcard' if cid in wild else 'outside',reason_ru=REASONS[cid],evidence_event_ids=list(dict.fromkeys(ev))))
assert len(decisions)==22 and set(REASONS)=={x['candidate_id'] for x in decisions}
write(R/'DECISIONS.json',{'decisions':decisions})
order=[x for x in read(R/'READING_ORDER.json')['candidate_order'] if x in main|wild]
entries=[]
for i,cid in enumerate(order,1):
 v=next(x['version'] for x in decisions if x['candidate_id']==cid)
 b=(ROOT/v['path']).read_bytes(); assert hashlib.sha256(b).hexdigest()==v['sha256'] and len(b)==v['bytes']
 p=R/f'reading/{i:02}.md'; p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists(): assert p.read_bytes()==b
 else: p.write_bytes(b)
 entries.append(dict(candidate_id=cid,**ref(p)))
write(R/'reading/INDEX.md','# Тексты для чтения\n\n'+''.join(f'{i}. [Текст {i:02d}]({i:02d}.md)\n' for i in range(1,11)))
write(R/'SELECTION_MANIFEST.json',{'selected_ids':order})
write(R/'READING_MANIFEST.json',{'entries':entries})
write(R/'FINAL_COUNTS.json',dict(accepted_individual_reviews=110,accepted_neutral_individual=66,accepted_profile_individual=44,actual_pairs=10,accepted_pair_reviews=50))
write(R/'closure-input/PLAIN_LANGUAGE_REVIEW.json',dict(concrete_plain_ru_2_to_3_sentences_each=True,decisions_sha256=hashlib.sha256(encode(decisions)).hexdigest(),reviewer='root coordinator',basis='Every reason explains the concrete situation, the selection action and its specific remaining limitation. All22 decision paragraphs read by root; no jargon replaces the reason.'))
plan=dict(schema='selection-final-plan.v1',run_id=R.name,decisions=decisions,pair_batches=[dict(queue='pair-batches/pairs-001/queue.json',input_receipt='pair-batches/pairs-001/START_RECEIPT.json')],reading=dict(directory=str((R/'reading').relative_to(ROOT)),entries=entries,index_file=str((R/'reading/INDEX.md').relative_to(ROOT))),plain_language_review=dict(artifact=ref(R/'closure-input/PLAIN_LANGUAGE_REVIEW.json'),event_id=None))
write(R/'closure-input/PLAN_INPUT.json',plan)
write(R/'closure-input/CHECKPOINT_SUMMARY.json',dict(question='Which eight main and two promising current manuscripts should the user read from the frozen22?',outcome='CONTINUE',contribution='Root selected8main+2promising after110 individual and50 pair reviews at3neutral:2profile, full reading and bounded source/numerical checks; exact unchanged reading copies prepared.',criticism='All individual overall/significance scores tied at3; choice rests on explicit argument comparison, not invented score differences. Pair ties and substantive limits are retained.',limitations='Novelty remains unestablished; profile fidelity unvalidated; sources checked only within recorded bounds. Original standard capture gap and three failed physical attempts preserved. No whole-provider capture claim.',next_step='Complete private GitHub update, project memory and collector restoration; then stop for user reading. No final-three selection or submission.',method_change='Astra/ultra retained. Two original capacity failures and one local initialization failure preserved; only two missing logical reviews replaced under accepted repair. Root integration used accepted v5 validator and v4 closure.',comparability='Original60 reviews unchanged; same frozen inputs and3:2 ratio. Pair ordering/profile allocation fixed before pair reviews. Equal ratings do not establish equal quality.',coverage_boundary='Finite160 accepted reviews and their bounded visible capture only. Administrative checkpoint remains INCOMPLETE for the preserved original standard capture gap; dedicated finite receipt governs selection acceptance.'))
labels={'main':'В десятку — основная часть','wildcard':'В десятку — перспективный','outside':'Пока вне десятки'}
lines=['# Решения по 22 эссе','', 'Выбраны восемь основных и два перспективных текста. «Перспективный» означает: уже есть содержательный результат, но один из главных вопросов остаётся открытым. «Пока вне десятки» не означает ошибку или удаление текста.','', 'Сначала можно прочитать [десять текстов без оценок](reading/INDEX.md). Порядок был задан до отзывов и не является рейтингом.','', '110 отдельных отзывов и 50 отзывов по десяти парам приняты. В каждом составе три нейтральных агента и два агента с описаниями подходов судей; это не настоящие судьи и не проверенная имитация их решений. Все отзывы выполнены на Astra с заданной настройкой ultra.','', 'Общие численные оценки оказались одинаковыми, поэтому выбор основан на доводах, проверках и прямых сравнениях. Новизна не считается доказанной ни для одного текста.','', '| Эссе | Решение | Почему |','|---|---|---|']
for d in sorted(decisions,key=lambda x:x['candidate_id']): lines.append('| '+d['candidate_id']+' | '+labels[d['selection']]+' | '+' '.join(d['reason_ru'])+' |')
lines+=['','## Как решены близкие случаи','', 'E009 и E055 оставлены оба: первый прослеживает весь путь защиты пострадавшего, второй разбирает конкретную возможность донести сведения об ошибке до проверяющего. Это разные результаты, несмотря на близкую тему.','', 'F02 и E039 получили пять ничьих. Выбор F02 — решение координатора в пользу более узкого обоснованного вывода, а не победа по голосам.','', 'Два перспективных места отданы E074 и E078. В E074 уже различены случаи, в которых свидетельство участника отвечает на разные вопросы; в E078 — основания индивидуальной и общей оплаты. В F03 пока не установлена общая причина ошибок в реальном споре, а предлагаемая проверка остаётся будущей работой. Это сравнительное суждение координатора: прямого сравнения E074 с E078 или F03 не было.','', 'Ни одно эссе не прошло автоматически из-за победы в паре, темы или отсутствия пары. Восемь основных также имеют открытые вопросы; это список для чтения, а не готовые три конкурсные работы.','', '## Точные версии','', 'R1 — сохранённая первая редакция; R1-display — её указанная в реестре версия для чтения; preselection-20261017-v1 — редакция предварительной подготовки 17 октября. Ни один текст во время этого отбора не изменялся.','', '| Эссе | Версия | Файл | SHA-256 |','|---|---|---|---|']
for d in sorted(decisions,key=lambda x:x['candidate_id']):
 v=d['version']; lines.append(f"| {d['candidate_id']} | {v['variant']} | [{v['actual_title']}](../../{v['path']}) | {v['sha256']} |")
lines+=['','Следующий шаг — чтение пользователем и отдельные глубокие проверки перед выбором трёх работ и двух резервных. Этот этап здесь не запускается.','']
write(R/'22_CANDIDATES_RU.md','\n'.join(lines))
write(R/'coordinator/FINAL_COMPARISON_RU.txt','\n'.join(lines[:lines.index('## Точные версии')]))
notes=[]
for n in range(1,28):
 p=R/f'coordinator/REVIEW_NOTES_{n:03}.json'
 if not p.exists():
  candidates=list((R/'coordinator').glob(f'*{n:03}*')); raise RuntimeError(str(candidates))
 notes.extend(read(p)['reviews_read'])
pairnotes=[j for n in range(1,11) for j in read(R/f'coordinator/PAIR_REVIEW_NOTES_{n:02}.json')['reviews_read']]
assert len(notes)==len(set(notes))==110 and len(pairnotes)==len(set(pairnotes))==50
assert read(R/'DECISIONS.json')['decisions']==plan['decisions']
assert read(R/'READING_MANIFEST.json')['entries']==plan['reading']['entries']
assert read(R/'SELECTION_MANIFEST.json')['selected_ids']==[x['candidate_id'] for x in entries]
write(R/'coordinator/FINAL_LOCAL_CHECK.json',dict(status='ROOT_CROSS_FILE_AND_READING_COVERAGE_PASS',individual_reviews_read=notes,pair_reviews_read=pairnotes,counts={'main':8,'wildcard':2,'outside':12},selected_reading_order=order,checks=['Exact decision/plan equality','Exact manifest/plan reading equality','Selected set and precommitted order equality','Ten copies match frozen source hashes and sizes','110+50 unique accepted reviews covered by full-reading notes'],boundary='Mechanical cross-file check; not canonical finite acceptance, publication or a new review.'))
print(json.dumps({'status':'ROOT_FINAL_INPUTS_PREPARED','main':sorted(main),'wildcard':sorted(wild),'reading_order':order},ensure_ascii=False))
