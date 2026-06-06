# Final pre-defense checklist

Финальный контрольный список перед показом проекта “Аиша”.

## A. Environment and launch

- Активировать виртуальное окружение:

```bash
source .venv/bin/activate
```

- Запустить backend в PostgreSQL-режиме:

```bash
export USE_POSTGRES=true
export DATABASE_URL="postgresql://$(whoami)@localhost:5432/tgbot"
export BACKEND_BASE_URL="http://localhost:8000"
bash scripts/run_backend.sh
```

- В отдельном терминале запустить Telegram-бота с теми же переменными:

```bash
source .venv/bin/activate
export USE_POSTGRES=true
export DATABASE_URL="postgresql://$(whoami)@localhost:5432/tgbot"
export BACKEND_BASE_URL="http://localhost:8000"
python -m telegram_bot.main
```

- Проверить `http://localhost:8000/health`.
- Проверить локальный Mini App: `http://localhost:8000/miniapp`.
- Для телефона и Telegram Mini App запустить `ngrok http 8000`, указать `WEBAPP_URL=https://<actual-ngrok-domain>/miniapp`, перезапустить бота и обновить BotFather Menu Button/Main App.

## B. PostgreSQL and data

- `pg_isready` должен отвечать `accepting connections`.
- `psql -d tgbot -c "SELECT COUNT(*) FROM universities;"` должен показывать ожидаемое количество вузов локального стенда.
- Запустить:

```bash
python3 scripts/check_postgres.py
```

- Убедиться, что synthetic/demo rows скрыты из обычной выдачи и доступны только через `include_synthetic=true` для диагностики.
- Проверить, что suspicious scores `< 40` не дают safe-категорию и не показывают ложный запас.
- Проверить, что `/api/directions?q=09.03.04&limit=20` ищет по полной PostgreSQL-базе, а первые 200 направлений в Mini App являются только стартовыми подсказками.
- Помнить: достижения из `achievements` являются общим справочником, а не вуз-специфичными правилами.

## C. Telegram bot smoke

- Открыть `https://t.me/seren_dipity_bott_bot`.
- Проверить `/start` и главное меню.
- Запустить `/search`.
- Ввести регион текстом, например `Адыгея`.
- Ввести баллы, например `230`.
- Ввести направление текстом, например `айти` или `09.03.04`.
- На шаге финансирования проверить кнопки `Бюджет`, `Платное`, `Любое`, `Назад`.
- Проверить выдачу страницами по 5: первая страница `1–5`, затем `➡️ Ещё варианты` для `6–10`.
- Проверить, что одновременно не показывается больше 5 кнопок `⭐ Сохранить N`.
- Сохранить вариант с текущей страницы и проверить `/favorites`.
- Проверить `/summary`, `/compare`, `/export`, `/history`, `/filters`, `/categories`, `/advice`, `/support`, `/feedback`, `/my_feedback`.

## D. Mini App smoke

- Открыть `http://localhost:8000/miniapp` в браузере.
- Проверить режим запуска `Браузер` и отдельный источник данных `PostgreSQL-база проекта` или `JSON fallback`.
- Проверить вкладки `Подбор`, `Фильтры`, `Сравнение`, `Избранное`, `План`, `Экспорт`, `Поддержка`.
- В direction picker проверить поиск по коду и тексту: `09.03.04`, `архитектура`, `экономика`.
- Проверить, что кнопка `×` очищает только направление.
- Проверить быстрый сценарий и обычный поиск.
- Проверить кнопки Telegram CTA: `Открыть бота`, `Начать подбор в Telegram`, `Связаться в Telegram`, `Открыть Telegram-бота`; все должны вести на `https://t.me/seren_dipity_bott_bot`.
- Через Telegram `/webapp` проверить валидную Mini App-сессию и синхронизацию избранного, если задан актуальный публичный `WEBAPP_URL`.

## E. Final checks and repository hygiene

- Запустить обязательные проверки:

```bash
python3 scripts/check_data.py
bash scripts/check_project.sh
bash -n scripts/run_backend.sh
bash -n scripts/run_bot.sh
git diff --check
node --check mini_app/app.js
```

- Убедиться, что `.env`, Telegram token, реальные пароли, `telegram_bot/storage/user_data.json`, `telegram_bot/storage/feedback.json`, `finalproj.zip` и распакованные архивы не попали в Git.
- Проверить, что пользовательские тексты не выводят `None`, `null`, `undefined`, `Конкурс: бюджет` как дубль, старые ngrok ссылки или `href="#"`.
- Перед ответом на защите сказать, что баллы и условия поступления нужно сверять на официальных сайтах вузов.
- Commit/push не делать до ручной проверки. Ожидаемое имя коммита после проверки: `Final full pre-defense project audit`.
