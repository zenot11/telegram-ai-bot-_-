# Архитектура проекта

## Общая идея

“Аиша” - Telegram-сервис для абитуриентов. Он помогает подобрать вуз по региону, баллам ЕГЭ, направлению и типу обучения, а также показывает категории поступления, фильтры результатов, избранное, историю подборов, советы по последнему подбору, сравнение и итог последнего подбора.

Проект сделан как демонстрационный прототип: сейчас используется временная JSON-база вузов, но структура подготовлена так, чтобы перед сдачей можно было подставить финальные данные.

## Основные части

- Telegram Bot - основной интерфейс в Telegram.
- Backend Stub - временный HTTP backend на aiohttp.
- Mini App - веб-интерфейс внутри Telegram или браузера.
- JSON-база вузов - демонстрационный файл с программами.
- Data Loader - загрузка и проверка структуры JSON-базы.
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
-> карточки, фильтры и локальное избранное в Mini App
```

## `telegram_bot/`

`telegram_bot/` содержит весь код Telegram-бота.

- `main.py` - точка входа, создание `Bot`, `Dispatcher`, подключение роутеров и BotCommand.
- `config.py` - чтение настроек из `.env`: токен Telegram, OpenAI key, backend URL, WebApp URL.
- `handlers/` - обработчики команд, кнопок и сценариев.
- `keyboards/` - reply-клавиатуры для меню, поиска, сравнения и профиля.
- `services/` - чистая логика: API-клиент, OpenAI wrapper, safety, validation, formatting, comparison, summary, history, advice, filters, export.
- `states/` - FSM-состояния для поиска и сравнения.
- `storage/` - локальное JSON-хранилище пользователя.

## `telegram_bot/handlers/`

- `start.py` - `/start`, `/help`, `/about`, `/demo`, `/privacy`, `/next`, `/botfather`, `/webapp`, `/reset`.
- `menu.py` - главное меню, профиль, избранное, `/summary`, `/advice`, `/history`, очистка истории, категории, регионы и направления.
- `filters.py` - `/filters`, inline-фильтры последних результатов и активная отфильтрованная выдача.
- `export.py` - `/export`, текстовый отчёт и отправка `.txt` файла по последнему подбору.
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
- `history.py` - короткие записи истории подборов и форматирование `/history`.
- `advice.py` - локальные советы по последнему подбору без обращения к OpenAI.
- `filters.py` - фильтрация последних результатов по категориям и типу обучения.
- `export.py` - plain text отчёт по `last_results` и `favorites`, split длинных сообщений и безопасное имя `.txt`.
- `texts.py` - тексты команд `/help`, `/demo`, `/privacy`, `/botfather`.

## `telegram_bot/storage/`

Локальное хранилище использует JSON-файл `telegram_bot/storage/user_data.json`. Он не попадает в Git.

Для пользователя хранится:

- Telegram ID;
- профиль последнего подбора;
- `last_results`;
- `active_results` - текущая показанная выдача для кнопок `Сохранить N`;
- `favorites`;
- `history` - последние 5 подборов с краткими top-items и счётчиками категорий.

`last_results` используется для `/summary`, `/history`, `/compare` и `/export`. `active_results` нужен только для сохранения вариантов из текущей отфильтрованной выдачи и не заменяет полный последний подбор.

История хранит только учебный запрос и краткий результат подбора. Токены, OpenAI-данные и лишние персональные данные туда не записываются.

Экспорт строится из уже сохранённых данных пользователя: profile, `last_results` и `favorites`. Он не обращается к backend повторно и не создаёт постоянные файлы в проекте.

## `backend_stub/`

`backend_stub/` - временный backend API.

- `main.py` - aiohttp-приложение, фильтрация вузов, normalizing query params, static routes Mini App.
- `data_loader.py` - загрузка, нормализация и валидация `universities.json`.
- `/health` - проверка, что backend работает.
- `/api/universities` - основной endpoint подбора вузов.
- `/miniapp` и `/miniapp/` - отдача `mini_app/index.html`.
- `/miniapp/{asset}` - отдача `styles.css`, `app.js`, `favicon.svg`.
- `/favicon.ico` - favicon для браузера.
- `data/universities.json` - демонстрационная база вузов.

Backend загружает базу при создании приложения. Если JSON некорректный или структура записей не соответствует контракту, backend завершает запуск с понятной ошибкой. Формат базы описан в `docs/DATA.md`.

## `mini_app/`

Mini App остается простым HTML + CSS + JS без сборки.

- `index.html` - структура страницы.
- `styles.css` - стиль в духе командного сайта “Аиша”, CSS-переменные для светлой/тёмной темы, адаптивные вкладки, фильтры и карточки.
- `app.js` - вкладки, переключение темы, валидация формы, запрос к `/api/universities`, локальные фильтры, итог подбора, избранное через `localStorage` и отрисовка карточек.
- `favicon.svg` - favicon.

Mini App не использует OpenAI и не хранит токены. Избранное Mini App и выбранная тема хранятся локально в браузере через `localStorage`. Избранное не синхронизируется с Telegram-ботом, потому что авторизация и `initData`-проверка не входят в текущий этап.

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
- history;
- advice;
- filters;
- storage;
- Mini App файлы и static routes;
- структуру `universities.json`;
- клавиатуры и help-тексты.

Тесты не требуют Telegram-токена, настоящего `.env` или реального OpenAI API.

## Почему такая архитектура удобна

- JSON можно заменить на финальную базу вузов, если сохранить структуру полей.
- `backend_stub` можно заменить на полноценный backend без переписывания Telegram-бота.
- Mini App использует тот же API, что и бот.
- Фильтры Mini App работают локально по уже полученным результатам и не требуют изменения backend API.
- Mini App не требует сборки и дополнительных frontend-зависимостей.
- OpenAI опционален: без ключа бот работает через fallback.
- Safety-фильтр локальный и стоит до OpenAI.
- Тесты запускаются без Telegram-токена.
