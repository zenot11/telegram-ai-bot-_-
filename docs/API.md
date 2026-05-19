# API backend_stub

`backend_stub` - временный backend API проекта “Аиша”. Он используется Telegram-ботом и Mini App.

Backend читает данные из JSON-базы `backend_stub/data/universities.json`. Формат базы описан в [docs/DATA.md](DATA.md).

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
  "universities_count": 45,
  "data_source": "backend_stub/data/universities.json"
}
```

## GET `/api/universities`

Основной endpoint для подбора вузов.

### Query parameters

- `region` - регион поиска.
- `score` - сумма баллов ЕГЭ.
- `direction` - направление.
- `type` - тип обучения.
- `limit` - максимальное количество результатов.

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
- `Бюджет` -> `бюджет`.

### Логика фильтрации

Результат подходит, если:

- регион совпадает после нормализации;
- направление совпадает или распознано через синонимы;
- тип обучения совпадает;
- `min_score <= score + 20`.

Варианты выше `score + 20` не возвращаются в основной выдаче.

### Пример ответа

```json
[
  {
    "university": "АГУ",
    "city": "Майкоп",
    "region": "Адыгея",
    "program": "Прикладная информатика",
    "direction": "IT",
    "subjects": ["русский язык", "математика", "информатика"],
    "min_score": 185,
    "type": "бюджет",
    "price": null,
    "url": "https://www.adygnet.ru",
    "study_form": "очная",
    "duration": "4 года",
    "note": "демонстрационные данные"
  }
]
```

## Структура `universities.json`

Файл находится здесь:

```text
backend_stub/data/universities.json
```

Структура ответа `/api/universities` совпадает с записью в JSON-базе. Ожидаемые поля:

- `university` - название вуза;
- `city` - город;
- `region` - регион;
- `program` - образовательная программа;
- `direction` - направление;
- `subjects` - список предметов;
- `min_score` - минимальный балл;
- `type` - `бюджет` или `платное`;
- `price` - стоимость или `null`;
- `url` - ссылка на сайт;
- `study_form` - форма обучения;
- `duration` - срок обучения;
- `note` - пометка о демонстрационных данных.

`price: null` означает, что стоимость не указана.

`note` используется для пометки демонстрационных данных.

Если структура полей сохранится, финальную базу можно подставить перед сдачей без переписывания основной логики поиска, карточек, сравнения, экспорта и Mini App.

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

Этот endpoint используется при первом открытии Mini App внутри Telegram. Если Mini App открыт в обычном браузере без `initData`, он продолжает работать в локальном режиме через `localStorage`.

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
