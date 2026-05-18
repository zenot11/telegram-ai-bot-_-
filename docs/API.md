# API backend_stub

`backend_stub` - временный backend API проекта “Аиша”. Он используется Telegram-ботом и Mini App.

## GET `/health`

Проверяет, что backend запущен.

Пример:

```text
GET /health
```

Ответ:

```text
ok
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

Ожидаемые поля:

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

Если структура полей сохранится, финальную базу можно подставить перед сдачей без переписывания основной логики поиска, карточек, сравнения и Mini App.

## Static routes Mini App

Backend также отдаёт Mini App:

- `/miniapp` - HTML-страница;
- `/miniapp/` - HTML-страница;
- `/miniapp/styles.css` - стили;
- `/miniapp/app.js` - JavaScript;
- `/miniapp/favicon.svg` - favicon;
- `/favicon.ico` - favicon для браузера.

Mini App использует тот же endpoint `/api/universities`, что и Telegram-бот.
