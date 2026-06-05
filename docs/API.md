# API backend_stub

`backend_stub` - временный backend API проекта “Аиша”. Он используется Telegram-ботом и Mini App.

При `USE_POSTGRES=true` backend читает пользовательский каталог из PostgreSQL по `DATABASE_URL`: вузы, регионы, города, направления, формы обучения, типы конкурса и справочник индивидуальных достижений. JSON-база `backend_stub/data/universities.json` остаётся fallback для локального запуска и тестов без PostgreSQL. Формат ответа `/api/universities` одинаковый в обоих режимах.

## GET `/health`

Проверяет, что backend запущен.

Пример:

```text
GET /health
```

Ответ:

```json
{
  "status": "ok",
  "service": "backend_stub",
  "storage": "json",
  "universities_count": 45,
  "data_source": "backend_stub/data/universities.json",
  "features": ["universities", "regions", "cities", "directions", "study_forms", "admission_types", "achievements", "filters", "sorting"]
}
```

В PostgreSQL mode:

```json
{
  "status": "ok",
  "service": "backend_stub",
  "storage": "postgresql",
  "data_source": "postgresql",
  "universities_count": 94,
  "features": ["universities", "regions", "cities", "directions", "study_forms", "admission_types", "achievements", "filters", "sorting"]
}
```

Если база расширена дополнительным seed-файлом, `universities_count` будет больше.

## GET `/api/universities`

Основной endpoint для подбора вузов.

### Query parameters

- `region` - регион поиска.
- `score` - сумма баллов ЕГЭ.
- `direction` - направление. Можно передавать название, профиль или код формата `09.03.04`; если код указан, backend сначала ищет точное `directions.code` и расширяет поиск по названию/профилю только при пустом результате.
- `type` - финансирование: `budget`/`бюджет` или `paid`/`платное`.
- `admission_type` - точный тип конкурса/квоты PostgreSQL или пользовательская метка, например `target`, `целевая квота`, `особая квота`. Бюджет/платное задаются через `type`.
- `city` - город.
- `study_form` - форма обучения.
- `year` - год проходных баллов.
- `q` - общий поиск по вузу, городу, региону, направлению, профилю и факультету.
- `limit` - максимальное количество результатов, максимум 200.
- `sort` - сортировка: `min_score_asc`, `min_score_desc`, `university`, `city`, `direction`, `year_desc`.
- `include_synthetic` - если `true`, диагностически включает synthetic/demo записи из supplemental seed. По умолчанию `false`.
- `include_demo` - alias для `include_synthetic`.

Пример запроса:

```text
/api/universities?region=Адыгея&score=230&direction=IT&type=budget&limit=5
```

Пример с опечатками и синонимами:

```text
/api/universities?region=Адыгеая&score=230&direction=айти&type=Бюджет&limit=5
```

Backend мягко нормализует ввод:

- `Адыгеая` -> `Адыгея`;
- `айти` -> `IT`;
- `IT` -> реальные PostgreSQL-направления: `Прикладная информатика`, `Информационная безопасность`, `Программная инженерия`, `Информатика и вычислительная техника` и близкие профили;
- `09.03.04 Программная инженерия` -> сначала `directions.code = 09.03.04`, затем fallback по тексту `Программная инженерия`, если точный код ничего не вернул;
- `Крым` -> `Республика Крым`;
- `Адыгея` -> `Республика Адыгея`;
- `Бюджет` -> `бюджет`;
- `контракт` -> `платное`.

Некорректные `score` и `limit` не ломают endpoint: `score` игнорируется, а `limit` возвращается к безопасному значению.

### Логика фильтрации

Результат подходит, если:

- регион совпадает после нормализации;
- направление совпадает по коду, названию, профилю или распознано через синонимы;
- финансирование совпадает;
- город совпадает, если передан `city`;
- общий поиск `q` найден в одном из текстовых полей;
- `min_score <= score + 20`.

Зазор `+20` - намеренно сохранённое поведение JSON-прототипа. Он нужен, чтобы в выдаче были не только безопасные варианты, но и амбициозные программы немного выше текущего результата. Варианты выше `score + 20` не возвращаются в основной выдаче.

Synthetic/demo записи из `06_seed_supplement_universities.sql`, например `Региональный центр технологий и инженерии (...)` с `short_name` вида `РЦТИ-12`, не удаляются из PostgreSQL, но скрываются из обычной выдачи по умолчанию. Для диагностики их можно запросить через `include_synthetic=true`.

### Пример ответа

```json
[
  {
    "university": "Адыгейский государственный университет",
    "city": "Майкоп",
    "region": "Республика Адыгея",
    "program": "Прикладная информатика",
    "direction": "Прикладная информатика",
    "subjects": ["русский язык", "математика", "информатика"],
    "min_score": 185,
    "score_is_valid": true,
    "score_display": "185",
    "score_note": "",
    "type": "бюджет",
    "financing_label": "бюджет",
    "price": null,
    "url": "https://www.adygnet.ru",
    "study_form": "очная",
    "study_form_label": "очная",
    "duration": "4 года",
    "note": "демонстрационные данные",
    "year": 2025,
    "faculty": "",
    "admission_type": "budget",
    "admission_type_label": "бюджет",
    "contest_label": "общий конкурс",
    "profile": "",
    "direction_code": "",
    "university_full_name": "Адыгейский государственный университет",
    "university_short_name": "АГУ",
    "source": "postgresql"
  }
]
```

Поля `year`, `faculty`, `admission_type`, `admission_type_label`, `financing_label`, `contest_label`, `study_form_label`, `profile`, `direction_code`, `university_full_name`, `university_short_name`, `score_is_valid`, `score_is_suspicious`, `score_display`, `score_note`, `match_quality`, `match_reason`, `source` могут присутствовать в PostgreSQL mode. Старые клиенты могут их игнорировать. `source`, `match_quality` и `match_reason` являются диагностическими полями API и не показываются в обычном пользовательском интерфейсе.

UI использует подписи:

- `financing_label` или `type` -> `Финансирование`;
- `study_form_label` или `study_form` -> `Форма обучения`;
- `contest_label`/`admission_type_label` -> `Конкурс`, но общий бюджетный конкурс не дублируется как `Конкурс: бюджет`.

Правила отображения баллов:

- `min_score` остаётся числом или `null`; backend не заменяет его строкой.
- `score_is_valid=true`, если `min_score >= 40`.
- `score_is_suspicious=true`, если `1 < min_score < 40`.
- `min_score=0`, `min_score=1`, suspicious-значения, `null` и отрицательные значения не показываются в UI как обычный проходной балл.
- Для таких записей UI показывает `Проходной балл: не указан`, `Минимальный балл: ...` или `балл требует уточнения`, не считает `Запас` и не присваивает категорию `безопасный вариант` только из-за малого значения.
- `score_display` и `score_note` помогают новым клиентам показать аккуратный текст, старые клиенты могут их игнорировать.

Если `universities.short_name` выглядит как технический код (`РЦТИ-26`, `РУТЭ-25`), backend и UI используют полное `universities.name` как главное название. Короткое название выводится отдельно только если оно полезно для пользователя.

Совместимость JSON и PostgreSQL, а также правила скрытия пустых необязательных полей описаны в [DATA_COMPATIBILITY.md](DATA_COMPATIBILITY.md).

## Directory endpoints

Все справочники работают и в JSON fallback, и в PostgreSQL mode. Mini App загружает их из backend при старте и использует static fallback только если backend недоступен или вернул пустой справочник.

### GET `/api/regions`

Возвращает регионы:

```json
{
  "storage": "json",
  "count": 8,
  "total_count": 8,
  "items": ["Адыгея", "Москва"]
}
```

`count` - число элементов в текущем ответе, `total_count` - полный размер справочника до frontend/endpoint-лимита. Mini App использует `total_count`, чтобы показывать `показано 200 из 937`, если начальные подсказки направлений ограничены для удобства.

### GET `/api/cities`

Параметры:

- `region` - опциональный фильтр по региону.

### GET `/api/directions`

Параметры:

- `region`;
- `city`;
- `study_form`;
- `type`;
- `year`;
- `q` - поиск по полному PostgreSQL-справочнику направлений: название, код `directions.code`, профиль, вуз, город, регион и факультет;
- `limit` - максимум записей в текущем ответе.

Возвращает направления и программы, доступные при выбранных фильтрах. Без `q` endpoint отдаёт компактный список названий направлений для начальной загрузки формы. С `q` в PostgreSQL mode поиск идёт по полной базе до frontend-лимита, поэтому Mini App может показывать только стартовые популярные подсказки, но искать `09.03.04`, `архитектура` или `экономика` по всему справочнику.

Mini App использует этот endpoint для кастомного direction picker: при вводе делает debounce-запрос `/api/directions?q=...&limit=20`, показывает dropdown, позволяет выбрать подсказку клавишами и очистить только направление кнопкой `×`.

Пример:

```text
/api/directions?q=09.03.04&limit=20
```

Формат ответа:

```json
{
  "storage": "postgresql",
  "count": 20,
  "total_count": 54,
  "items": ["09.03.04 Программная инженерия"]
}
```

### GET `/api/study-forms`

Возвращает формы обучения в пользовательском виде, например `очная`, `заочная`.

### GET `/api/admission-types`

Возвращает человекочитаемые типы конкурса. В PostgreSQL mode это могут быть `бюджет`, `платное`, `целевая квота`, `особая квота`, `отдельная квота`, `дополнительный прием`.

### GET `/api/achievements`

Параметры:

- `limit` - максимальное количество записей.

Возвращает общий справочник индивидуальных достижений. В SQL-схеме `achievements` не связана с конкретными вузами, поэтому UI показывает эти записи как общие достижения, а не как правила отдельного университета.

```json
{
  "storage": "postgresql",
  "count": 13,
  "items": [
    {
      "code": "gto",
      "name": "Знак отличия ГТО",
      "max_points": 2,
      "description": "Баллы за индивидуальное достижение",
      "category": "спорт"
    }
  ],
  "note": "Баллы за индивидуальные достижения зависят от правил конкретного вуза."
}
```

## Контракт записи в ответе

В JSON fallback данные берутся из файла:

```text
backend_stub/data/universities.json
```

Структура ответа `/api/universities` совпадает с записью в JSON-базе и сохраняется в PostgreSQL mode. Ожидаемые поля:

- `university` - название вуза;
- `city` - город;
- `region` - регион;
- `program` - образовательная программа;
- `direction` - направление;
- `subjects` - список предметов;
- `min_score` - минимальный балл из источника, число или `null`;
- `score_is_valid` - можно ли использовать `min_score` для категории и запаса;
- `score_is_suspicious` - низкое значение `min_score`, которое требует проверки и не участвует в расчёте запаса;
- `score_display` - безопасный пользовательский текст для проходного балла;
- `score_note` - пометка вроде `балл требует уточнения`;
- `type` - legacy-поле финансирования, `бюджет` или `платное`;
- `financing_label` - подпись для строки `Финансирование`;
- `price` - стоимость или `null`;
- `url` - ссылка на сайт;
- `study_form` - legacy-поле формы обучения;
- `study_form_label` - подпись для строки `Форма обучения`;
- `contest_label` - подпись для строки `Конкурс`, если конкурс нужно показать отдельно;
- `duration` - срок обучения;
- `note` - пометка о демонстрационных данных.

`price: null` означает, что стоимость не указана. Клиентские интерфейсы должны скрывать необязательные строки без данных, а не выводить `Стоимость: null`, `Стоимость: None`, `Предметы: []` или пустой `Срок:`.

`note` используется для пометки демонстрационных данных или для контекста PostgreSQL-записи. Малые значения `min_score`, например `25`, не исправляются искусственно: UI показывает их как минимальный балл, требующий проверки, рядом с `Конкурс`, `Год данных` и `Примечание`, чтобы не выдавать догадки за данные. Значения `< 40` не используются для расчёта запаса.

Если структура полей сохранится, источник данных можно заменить без переписывания Telegram-бота, карточек, сравнения, экспорта и Mini App. PostgreSQL-настройка описана в [docs/POSTGRES.md](POSTGRES.md).

Подробный контракт и проверка базы описаны в [docs/DATA.md](DATA.md).

## Static routes Mini App

Backend также отдаёт Mini App:

- `/miniapp` - HTML-страница;
- `/miniapp/` - HTML-страница;
- `/miniapp/styles.css` - стили;
- `/miniapp/app.js` - JavaScript;
- `/miniapp/favicon.svg` - favicon;
- `/favicon.ico` - favicon для браузера.

Mini App использует тот же endpoint `/api/universities`, что и Telegram-бот.

## WebApp session API

### GET `/api/webapp/session`

Endpoint нужен для диагностики режима Mini App и безопасной проверки Telegram WebApp `initData`.

Mini App передаёт `initData` в header:

```text
X-Telegram-Init-Data: <window.Telegram.WebApp.initData>
```

Если header отсутствует, backend считает, что Mini App открыт в обычном браузере, и возвращает local mode:

```json
{
  "status": "ok",
  "mode": "local",
  "authenticated": false
}
```

Если `initData` валиден, backend возвращает подтверждённую Telegram-сессию:

```json
{
  "status": "ok",
  "mode": "telegram",
  "authenticated": true,
  "user": {
    "id": 123456,
    "first_name": "Test"
  }
}
```

Если `initData` не проходит проверку:

```json
{
  "status": "error",
  "mode": "telegram",
  "authenticated": false,
  "error": "invalid_init_data"
}
```

HTTP status: `401`.

Если backend не настроен для проверки Telegram-сессии, например нет `TELEGRAM_BOT_TOKEN`, ответ содержит безопасную ошибку `bot_token_not_configured` без значения токена.

Endpoint не возвращает `initData`, `hash` или bot token.

## Favorites API для Telegram Mini App

Эти endpoints нужны для синхронизации избранного между Telegram-ботом и Mini App.

Mini App должен передавать Telegram WebApp initData в header:

```text
X-Telegram-Init-Data: <window.Telegram.WebApp.initData>
```

Backend проверяет `initData` через `TELEGRAM_BOT_TOKEN`, достаёт `user.id` из проверенных данных и только после этого работает с избранным пользователя. `user_id` из query или body не принимается. Mini App вызывает Favorites API только после успешной проверки `/api/webapp/session`.

Если `initData` отсутствует или не проходит проверку, backend возвращает:

```json
{
  "status": "error",
  "error": "unauthorized"
}
```

HTTP status: `401`.

### GET `/api/favorites`

Возвращает избранные вузы пользователя.

Ответ:

```json
{
  "status": "ok",
  "mode": "telegram",
  "favorites": []
}
```

### POST `/api/favorites/add`

Добавляет вуз в избранное без дублей.

Body:

```json
{
  "item": {
    "university": "АГУ",
    "city": "Майкоп",
    "program": "Прикладная информатика",
    "min_score": 185,
    "type": "бюджет"
  }
}
```

### POST `/api/favorites/remove`

Удаляет вуз из избранного.

Body можно передать по ключу:

```json
{
  "key": "агу|прикладная информатика|майкоп|185|бюджет"
}
```

Или по объекту `item`, тогда backend сам вычислит ключ.

### POST `/api/favorites/clear`

Очищает избранное пользователя.

### POST `/api/favorites/sync`

Объединяет локальное избранное Mini App с избранным Telegram-бота.

Body:

```json
{
  "local_favorites": []
}
```

Backend объединяет записи без дублей по стабильному ключу:

```text
university + program + city + min_score + type
```

Этот endpoint используется при первом открытии Mini App внутри Telegram. Если Mini App открыт в обычном браузере без `initData`, пользовательский режим запуска показывается как `Браузер`, а избранное хранится через `localStorage`.

## Feedback API для Mini App

Эти endpoints нужны для обратной связи из Mini App. Они сохраняют обращения в локальный файл `telegram_bot/storage/feedback.json`.

Если Mini App открыт через Telegram, он передаёт:

```text
X-Telegram-Init-Data: <window.Telegram.WebApp.initData>
```

Backend проверяет `initData` и достаёт `user.id` только из проверенных данных. `user_id` из query или body не принимается.

Если header отсутствует, `POST /api/feedback` работает в local mode: заявка создаётся без Telegram ID. Если header есть, но невалидный, backend возвращает `401 invalid_init_data`.

### POST `/api/feedback`

Создаёт обращение.

Body:

```json
{
  "category": "search_problem",
  "message": "Не нашёл регион в подборе",
  "context": {
    "last_search": {
      "region": "Адыгея",
      "score": 230,
      "direction": "IT",
      "type": "budget",
      "results_count": 5
    },
    "active_tab": "feedback",
    "session_mode": "telegram",
    "theme": "light"
  }
}
```

Категории:

- `admission_question` - вопрос по поступлению;
- `search_problem` - проблема с подбором вузов;
- `mini_app_problem` - проблема с Mini App;
- `data_error` - ошибка в данных;
- `improvement` - предложить улучшение;
- `other` - другое.

Успешный ответ:

```json
{
  "status": "ok",
  "mode": "telegram",
  "ticket": {
    "ticket_id": "AISH-0007",
    "status": "new",
    "category_label": "Проблема с подбором вузов",
    "created_at": "2026-05-19T16:30:00Z"
  }
}
```

Ошибки:

- `400 invalid_category`;
- `400 message_too_short`;
- `400 message_too_long`;
- `401 invalid_init_data`;
- `503 bot_token_not_configured`, если Telegram mode запрошен, но backend не настроен для проверки сессии.

Ответы не содержат `initData`, `hash` или bot token.

### GET `/api/feedback/my`

Возвращает последние обращения пользователя в Telegram mode.

Если Mini App открыт в обычном браузере без `initData`, endpoint возвращает local mode и пустой список:

```json
{
  "status": "ok",
  "mode": "local",
  "tickets": []
}
```

Если `initData` валиден:

```json
{
  "status": "ok",
  "mode": "telegram",
  "tickets": [
    {
      "ticket_id": "AISH-0007",
      "status": "new",
      "category_label": "Проблема с Mini App",
      "created_at": "2026-05-19T16:30:00Z",
      "message": "Mini App не открывается"
    }
  ]
}
```
