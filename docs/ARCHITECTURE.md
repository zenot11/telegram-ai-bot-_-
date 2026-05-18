# Архитектура проекта

## Общая идея

“Аиша” - Telegram-сервис для абитуриентов. Он помогает подобрать вуз по региону, баллам ЕГЭ, направлению и типу обучения, а также показывает категории поступления, избранное, сравнение и итог последнего подбора.

Проект сделан как демонстрационный прототип: сейчас используется временная JSON-база вузов, но структура подготовлена так, чтобы перед сдачей можно было подставить финальные данные.

## Основные части

- Telegram Bot - основной интерфейс в Telegram.
- Backend Stub - временный HTTP backend на aiohttp.
- Mini App - веб-интерфейс внутри Telegram или браузера.
- JSON-база вузов - демонстрационный файл с программами.
- Tests - pytest-проверки логики проекта.
- Scripts - скрипты запуска и проверки.
- Docs - документация по запуску, API, BotFather и защите.

## Схема взаимодействия Telegram-бота

```text
Пользователь
-> Telegram Bot
-> backend_stub /api/universities
-> universities.json
-> Telegram Bot
-> карточки вузов
```

## Схема взаимодействия Mini App

```text
Пользователь
-> Telegram Mini App
-> backend_stub /api/universities
-> universities.json
-> карточки в Mini App
```

## `telegram_bot/`

`telegram_bot/` содержит весь код Telegram-бота.

- `main.py` - точка входа, создание `Bot`, `Dispatcher`, подключение роутеров и BotCommand.
- `config.py` - чтение настроек из `.env`: токен Telegram, OpenAI key, backend URL, WebApp URL.
- `handlers/` - обработчики команд, кнопок и сценариев.
- `keyboards/` - reply-клавиатуры для меню, поиска, сравнения и профиля.
- `services/` - чистая логика: API-клиент, OpenAI wrapper, safety, validation, formatting, comparison, summary.
- `states/` - FSM-состояния для поиска и сравнения.
- `storage/` - локальное JSON-хранилище пользователя.

## `telegram_bot/handlers/`

- `start.py` - `/start`, `/help`, `/about`, `/demo`, `/privacy`, `/next`, `/botfather`, `/webapp`, `/reset`.
- `menu.py` - главное меню, профиль, избранное, `/summary`, категории, регионы и направления.
- `search.py` - FSM-подбор вузов: регион, баллы, направление, тип обучения, запрос к backend.
- `compare.py` - `/compare`, выбор источника и вариантов сравнения.
- `support.py` - `/support` и кнопки психологической поддержки.
- `common.py` - fallback-обработчик, crisis/safety и свободные вопросы.

## `telegram_bot/services/`

- `validation.py` - нормализация ввода и проверка баллов.
- `api.py` - HTTP-клиент к backend.
- `ai.py` - OpenAI wrapper с fallback.
- `safety.py` - crisis-фразы и фиксированный безопасный ответ.
- `recommendation.py` - категории safe/realistic/ambitious.
- `compare.py` - аналитика сравнения вузов.
- `formatters.py` - форматирование карточек вузов.
- `summary.py` - итог последнего подбора.
- `texts.py` - тексты команд `/help`, `/demo`, `/privacy`, `/botfather`.

## `backend_stub/`

`backend_stub/` - временный backend API.

- `main.py` - aiohttp-приложение, фильтрация вузов, normalizing query params, static routes Mini App.
- `/health` - проверка, что backend работает.
- `/api/universities` - основной endpoint подбора вузов.
- `/miniapp` и `/miniapp/` - отдача `mini_app/index.html`.
- `/miniapp/{asset}` - отдача `styles.css`, `app.js`, `favicon.svg`.
- `/favicon.ico` - favicon для браузера.
- `data/universities.json` - демонстрационная база вузов.

## `mini_app/`

Mini App остается простым HTML + CSS + JS без сборки.

- `index.html` - структура страницы.
- `styles.css` - светлый стиль в духе командного сайта “Аиша”.
- `app.js` - валидация формы, запрос к `/api/universities`, отрисовка карточек.
- `favicon.svg` - favicon.

Mini App не использует OpenAI и не хранит токены.

## `tests/`

Тесты проверяют:

- backend-фильтрацию;
- нормализацию пользовательского ввода;
- validation баллов;
- safety-фильтр;
- OpenAI fallback;
- карточки поиска;
- сравнение вузов;
- summary;
- storage;
- Mini App файлы и static routes;
- структуру `universities.json`;
- клавиатуры и help-тексты.

Тесты не требуют Telegram-токена, настоящего `.env` или реального OpenAI API.

## Почему такая архитектура удобна

- JSON можно заменить на финальную базу вузов, если сохранить структуру полей.
- `backend_stub` можно заменить на полноценный backend без переписывания Telegram-бота.
- Mini App использует тот же API, что и бот.
- Mini App не требует сборки и дополнительных frontend-зависимостей.
- OpenAI опционален: без ключа бот работает через fallback.
- Safety-фильтр локальный и стоит до OpenAI.
- Тесты запускаются без Telegram-токена.
