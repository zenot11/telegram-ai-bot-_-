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

## Favorites API для Telegram Mini App

Эти endpoints нужны для синхронизации избранного между Telegram-ботом и Mini App.

Mini App должен передавать Telegram WebApp initData в header:

```text
X-Telegram-Init-Data: <window.Telegram.WebApp.initData>
```

Backend проверяет `initData` через `TELEGRAM_BOT_TOKEN`, достаёт `user.id` из проверенных данных и только после этого работает с избранным пользователя. `user_id` из query или body не принимается.

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
