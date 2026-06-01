# Архитектура проекта

## Общая идея

“Аиша” - Telegram-сервис для абитуриентов. Он помогает подобрать вуз по региону, баллам ЕГЭ, направлению и типу обучения, а также показывает категории поступления, фильтры результатов, избранное, историю подборов, советы по последнему подбору, сравнение, итог последнего подбора и обратную связь.

Проект сделан как демонстрационный прототип с PostgreSQL-first пользовательским сценарием: при `USE_POSTGRES=true` каталог вузов и справочники берутся из SQL-базы команды, а JSON-база вузов остаётся fallback для локального запуска и тестов без PostgreSQL. На 37 этапе добавлен PostgreSQL-режим для каталога вузов, на 38 этапе backend начал использовать PostgreSQL для справочников, расширенных фильтров и сортировки без изменения старого API-контракта, на 39 этапе добавлена проверка совместимости данных и качества пользовательской выдачи, а на 40 этапе Mini App и бот адаптированы под реальные PostgreSQL-значения команды.

## Основные части

- Telegram Bot - основной интерфейс в Telegram.
- Backend Stub - временный HTTP backend на aiohttp.
- Mini App - веб-интерфейс внутри Telegram или браузера.
- JSON-база вузов - демонстрационный fallback с программами.
- PostgreSQL source - основной источник пользовательских данных при `USE_POSTGRES=true`.
- Directory API - справочники регионов, городов, направлений, форм обучения, типов конкурса и индивидуальных достижений.
- Data Loader - загрузка и проверка структуры JSON-базы.
- Tests - pytest-проверки логики проекта.
- Scripts - скрипты запуска и проверки.
- Docs - документация по запуску, API, BotFather и защите.

## Схема взаимодействия Telegram-бота

```text
Пользователь
-> Telegram Bot
-> backend_stub /api/universities
-> PostgreSQL или JSON fallback
-> Telegram Bot
-> карточки вузов
```

## Схема взаимодействия Mini App

```text
Пользователь
-> Telegram Mini App
-> backend_stub /api/universities и directory endpoints
-> PostgreSQL или JSON/static fallback
-> карточки, фильтры, сравнение и локальное избранное в Mini App
```

Mini App при старте загружает `/api/regions`, `/api/cities`, `/api/directions`, `/api/study-forms`, `/api/admission-types` и `/api/achievements`. Если backend недоступен, интерфейс остаётся рабочим на fallback-справочниках и показывает пользователю статус fallback.

Слой форматирования в Telegram-боте и Mini App не показывает пустые необязательные поля как технические значения. PostgreSQL-поля `year`, `faculty`, `financing_label`, `contest_label`, `study_form_label`, `admission_type_label`, `note`, `profile` используются как дополнительный контекст, а диагностическое поле `source` остаётся только в API. Полное `universities.name` используется как основное название, а synthetic/demo rows supplemental seed скрываются из обычной выдачи по умолчанию.

Для Telegram-режима Mini App дополнительно проверяет сессию:

```text
Mini App
-> backend_stub /api/webapp/session
-> проверка Telegram WebApp initData по HMAC
-> режим telegram/local/invalid
```

## `telegram_bot/`

`telegram_bot/` содержит весь код Telegram-бота.

- `main.py` - точка входа, создание `Bot`, `Dispatcher`, подключение роутеров и BotCommand.
- `config.py` - чтение настроек из `.env`: токен Telegram, OpenAI key, backend URL, WebApp URL.
- `handlers/` - обработчики команд, кнопок и сценариев.
- `keyboards/` - reply-клавиатуры для старых сценариев и inline-клавиатуры карточного меню. Главное меню разделено на 6 основных разделов: подбор, Mini App, результаты, помощник, сервис и информация о проекте.
- `services/` - чистая логика: API-клиент, OpenAI wrapper, safety, validation, formatting, comparison, summary, history, advice, filters, export, feedback, menu cards.
- `assets/menu/` - локальные SVG-баннеры для главного меню и основных подменю.
- `states/` - FSM-состояния для поиска и сравнения.
- `storage/` - локальное JSON-хранилище пользователя.

## `telegram_bot/handlers/`

- `start.py` - `/start`, `/help`, `/about`, `/demo`, `/privacy`, `/next`, `/botfather`, `/webapp`, `/reset`.
- `menu.py` - главное меню, подменю результатов/помощника/сервиса/проекта, профиль, избранное, `/summary`, `/advice`, `/history`, очистка истории, категории, регионы и направления.
- `filters.py` - `/filters`, inline-фильтры последних результатов и активная отфильтрованная выдача.
- `export.py` - `/export`, текстовый отчёт и отправка `.txt` файла по последнему подбору.
- `feedback.py` - `/feedback`, `/my_feedback`, выбор категории обращения и сохранение заявки.
- `search.py` - FSM-подбор вузов: регион, баллы, направление, финансирование, запрос к backend.
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
- `feedback.py` - категории обращений, валидация текста и форматирование заявок.
- `menu_cards.py` - отправка визуальных меню-карточек с локальными баннерами и fallback на обычный текст, если Telegram не принял изображение.
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

Обращения пользователей хранятся отдельно в `telegram_bot/storage/feedback.json`. Этот файл создаётся автоматически, не попадает в Git и не смешивается с профилем, избранным или историей подборов.

## `backend_stub/`

`backend_stub/` - временный backend API.

- `main.py` - aiohttp-приложение, выбор JSON/PostgreSQL storage, static routes Mini App.
- `db.py` - чтение `USE_POSTGRES`/`DATABASE_URL`, создание и закрытие asyncpg pool.
- `university_repository.py` - фильтрация JSON fallback, SQL-запросы PostgreSQL, справочники, сортировка и нормализация ответа к API contract.
- `data_loader.py` - загрузка, нормализация и валидация `universities.json`.
- `telegram_auth.py` - проверка Telegram WebApp `initData`, извлечение Telegram ID и безопасных полей пользователя.
- `webapp_session.py` - endpoint `/api/webapp/session` для диагностики режима Mini App.
- `favorites_api.py` - защищённые endpoints синхронизации избранного Mini App с ботом.
- `feedback_api.py` - endpoints обратной связи Mini App: local mode и Telegram mode через проверенный `initData`.
- `/health` - проверка, что backend работает.
- `/api/universities` - основной endpoint подбора вузов.
- `/api/regions`, `/api/cities`, `/api/directions`, `/api/study-forms`, `/api/admission-types` - справочники для backend, Mini App и Telegram-бота.
- `/api/webapp/session` - проверка Telegram WebApp-сессии или local mode.
- `/api/feedback` и `/api/feedback/my` - создание обращения и последние обращения пользователя.
- `/miniapp` и `/miniapp/` - отдача `mini_app/index.html`.
- `/miniapp/{asset}` - отдача `styles.css`, `app.js`, `favicon.svg`.
- `/favicon.ico` - favicon для браузера.
- `data/universities.json` - демонстрационная база вузов и fallback по умолчанию.

В JSON mode backend загружает базу при создании приложения. Если JSON некорректный или структура записей не соответствует контракту, backend завершает запуск с понятной ошибкой. В PostgreSQL mode backend создаёт pool при старте и не скрывает ошибку подключения, если `USE_POSTGRES=true`. `/api/universities` поддерживает `region`, `city`, `score`, `direction`, `type`, `admission_type`, `study_form`, `year`, `q`, `limit`, `sort`, `include_synthetic` и `include_demo`. При фильтрации по баллам сохраняется амбициозный зазор `score + 20`. Формат JSON описан в `docs/DATA.md`, PostgreSQL-запуск - в `docs/POSTGRES.md`, совместимость источников - в `docs/DATA_COMPATIBILITY.md`.

## `mini_app/`

Mini App остается простым HTML + CSS + JS без сборки.

- `index.html` - структура страницы.
- `styles.css` - стиль в духе командного сайта “Аиша”, CSS-переменные для светлой/тёмной темы, анимированный бренд в верхней панели без внешних шрифтов, адаптивные вкладки, фильтры, карточки, таблица сравнения, быстрый старт, контекстные подсказки, план поступления, экспортный отчёт, print CSS, форма поддержки и toast-уведомления.
- `app.js` - вкладки, быстрые сценарии, автозаполнение формы, очистка формы, загрузка справочников `/api/regions` и `/api/directions`, toast notification layer, переключение темы, контекстные подсказки `Aisha советует`, валидация формы, запрос к `/api/universities`, проверка `/api/webapp/session`, локальные фильтры, итог подбора, синхронизация избранного или localStorage fallback, локальное сравнение, персональный план поступления, экспорт отчёта, форма обратной связи, отрисовка карточек и таблицы сравнения.
- `favicon.svg` - favicon.

Mini App не использует OpenAI и не хранит токены. Выбранная тема и выбранные вузы для сравнения хранятся локально в браузере через `localStorage`. Сравнение не синхронизируется с Telegram-ботом.

Визуальный слой Mini App использует только HTML/CSS/JS: бренд Aisha в верхней панели появляется побуквенно через CSS-анимацию, а `prefers-reduced-motion` отключает новую анимацию для пользователей, которым она не подходит. Внешние шрифты, CDN, GIF, видео и Lottie не используются.

Быстрые сценарии и toast-уведомления работают полностью на клиенте и не меняют backend API. Они помогают на демонстрации быстро заполнить форму, показать результат, сохранить вуз, добавить варианты к сравнению и объяснить пустые состояния без дополнительных серверных endpoints.

Контекстные подсказки `Aisha советует` тоже работают полностью на клиенте. Подсказка строится по `lastResults`, `favorites`, `comparisonItems`, активной вкладке и состоянию поиска. Пользователь может скрыть подсказки; это хранится в `localStorage` по ключу `aisha_hints_hidden`.

Персональный план поступления тоже работает полностью на клиенте. Он строится по текущим `lastResults`, `favorites` и `comparisonItems`: показывает краткий итог, чеклист, безопасные/реалистичные/амбициозные блоки и следующие действия. Backend API для плана не добавляется.

Экспорт Mini App тоже работает полностью на клиенте. Он собирает параметры последнего подбора, `lastResults`, `favorites`, `comparisonItems` и краткий план поступления в отчёт. Копирование использует Clipboard API с textarea fallback, а сохранение PDF выполняется через обычный `window.print()` и CSS `@media print`; backend endpoints для экспорта не добавляются.

Mini App показывает статус сессии: local mode, проверенная Telegram-сессия, невалидная сессия или недоступный backend. Если Mini App открыт внутри Telegram, он отправляет `window.Telegram.WebApp.initData` в backend через header `X-Telegram-Init-Data`. Backend проверяет подпись initData через `TELEGRAM_BOT_TOKEN`, достаёт Telegram ID из проверенных данных и возвращает только безопасные поля пользователя. Если Mini App открыт в обычном браузере без initData, он остаётся в локальном режиме.

Для избранного есть дополнительный режим синхронизации. Синхронизация с Telegram-ботом запускается только после успешной проверки `/api/webapp/session`. Backend использует тот же `telegram_bot/storage/user_data.py`, что и Telegram-бот. Если сессия не подтверждена или Mini App открыт в обычном браузере, избранное остаётся в локальном режиме через `localStorage`.

Для обратной связи Mini App использует `POST /api/feedback`. В обычном браузере заявка создаётся без Telegram ID. В Telegram mode backend проверяет `initData` и привязывает заявку к пользователю. Команда `/my_feedback` в боте и `GET /api/feedback/my` в Mini App читают один и тот же `feedback.json`.

Favorites API:

- `GET /api/webapp/session`;
- `GET /api/favorites`;
- `POST /api/favorites/add`;
- `POST /api/favorites/remove`;
- `POST /api/favorites/clear`;
- `POST /api/favorites/sync`.

Feedback API:

- `POST /api/feedback`;
- `GET /api/feedback/my`.

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
- PostgreSQL можно включить через `USE_POSTGRES=true`, не меняя Telegram-бот и Mini App.
- Справочники строятся из текущего источника данных: PostgreSQL или JSON fallback.
- `backend_stub` можно заменить на полноценный backend без переписывания Telegram-бота.
- Mini App использует тот же API, что и бот.
- Фильтры Mini App работают локально по уже полученным результатам и не требуют изменения backend API.
- Mini App не требует сборки и дополнительных frontend-зависимостей.
- OpenAI опционален: без ключа бот работает через fallback.
- Safety-фильтр локальный и стоит до OpenAI.
- Тесты запускаются без Telegram-токена.
