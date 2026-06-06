# Запуск проекта

Этот документ описывает запуск проекта “Аиша” с нуля: backend API, Telegram-бота, Mini App и проверок.

## 1. Клонирование проекта

```bash
git clone <repository-url>
cd telegram-ai-bot
```

## 2. Виртуальное окружение

```bash
python -m venv .venv
source .venv/bin/activate
```

Если команда `python` недоступна, можно использовать `python3`.

## 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

## 4. Настройка `.env`

Создайте локальный `.env` из примера:

```bash
cp .env.example .env
```

Пример структуры:

```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
OPENAI_API_KEY=
BACKEND_BASE_URL=http://localhost:8000
WEBAPP_URL=
USE_POSTGRES=false
DATABASE_URL=postgresql://<user>@localhost:5432/tgbot
USE_POSTGRES_TESTS=false
```

Пояснения:

- `TELEGRAM_BOT_TOKEN` обязателен для запуска Telegram-бота.
- `OPENAI_API_KEY` опционален. Если он пустой, бот работает через fallback.
- `BACKEND_BASE_URL=http://localhost:8000` подходит для локального запуска.
- `WEBAPP_URL` нужен только для открытия Mini App внутри Telegram через публичный HTTPS URL.
- `USE_POSTGRES=false` оставляет JSON fallback.
- `DATABASE_URL` используется только при `USE_POSTGRES=true`.

Настоящие токены нельзя хранить в коде и коммитить в Git.

## 5. Запуск backend

По умолчанию backend работает через JSON fallback `backend_stub/data/universities.json`.

Перед запуском можно проверить структуру базы вузов:

```bash
python scripts/check_data.py
```

В первом терминале:

```bash
source .venv/bin/activate
python -m backend_stub.main
```

Или через скрипт:

```bash
bash scripts/run_backend.sh
```

Backend по умолчанию открывается на:

```text
http://localhost:8000
```

Проверка:

```text
http://localhost:8000/health
```

PostgreSQL-режим для защиты включается так; порядок подготовки базы описан в [POSTGRES.md](POSTGRES.md).

```bash
source .venv/bin/activate
export USE_POSTGRES=true
export DATABASE_URL="postgresql://$(whoami)@localhost:5432/tgbot"
export BACKEND_BASE_URL="http://localhost:8000"
bash scripts/run_backend.sh
```

Быстрые проверки API:

```bash
curl "http://localhost:8000/api/regions"
curl "http://localhost:8000/api/directions"
curl "http://localhost:8000/api/directions?q=09.03.04&limit=20"
curl "http://localhost:8000/api/universities?score=230&limit=5&sort=min_score_desc"
```

## 6. Запуск Telegram-бота

Во втором терминале для PostgreSQL-сценария защиты:

```bash
source .venv/bin/activate
export USE_POSTGRES=true
export DATABASE_URL="postgresql://$(whoami)@localhost:5432/tgbot"
export BACKEND_BASE_URL="http://localhost:8000"
python -m telegram_bot.main
```

Или через скрипт:

```bash
bash scripts/run_bot.sh
```

Бот читает токен только из локального `.env`.

## 7. Проверка проекта

```bash
bash scripts/check_project.sh
```

Скрипт выполняет:

- `compileall` для Python-кода;
- проверку JSON-файла `universities.json`;
- проверку структуры базы через `scripts/check_data.py`;
- опциональную PostgreSQL-проверку через `scripts/check_postgres.py`, только если `USE_POSTGRES_TESTS=true`;
- весь набор `pytest`.

## 8. Mini App локально

Сначала запустите backend:

```bash
bash scripts/run_backend.sh
```

Затем откройте в браузере:

```text
http://localhost:8000/miniapp
```

Локальный адрес подходит для проверки на ноутбуке в браузере. Телефон внутри Telegram не увидит `localhost`, поэтому для Mini App нужен публичный HTTPS URL.

Frontend-ссылки на Telegram-бота должны открывать Aisha bot: `https://t.me/seren_dipity_bott_bot`. В локальном браузере проверьте кнопки `Открыть бота`, `Начать подбор в Telegram`, `Связаться в Telegram` и `Открыть Telegram-бота`: они должны открывать эту ссылку в новой вкладке.

Если нужно сохранить отчёт Mini App как PDF, откройте вкладку `Экспорт`, нажмите `Печать / сохранить PDF` и выберите сохранение в системном окне печати браузера.

## 9. Mini App через Telegram и ngrok

Для Telegram Mini App нужен публичный HTTPS URL.

Пример:

```bash
ngrok http 8000
```

После запуска ngrok укажите HTTPS-адрес в `.env`:

```env
WEBAPP_URL=https://<actual-ngrok-domain>/miniapp
```

После изменения `.env` перезапустите Telegram-бота. Если ngrok перезапущен и домен изменился, обновите `WEBAPP_URL` и BotFather Menu Button/Main App на актуальный адрес.

В обычном браузере Mini App показывает режим запуска `Браузер`, а избранное хранится только в этом браузере через `localStorage`. Источник данных показывается отдельно в блоке подбора: это может быть PostgreSQL-база проекта или JSON fallback.

Проверенный Telegram-режим появляется только при открытии Mini App через Telegram `/webapp` и публичный HTTPS `WEBAPP_URL`, когда Telegram передаёт WebApp `initData`. Backend проверяет эту сессию через `/api/webapp/session`, и только после этого синхронизация избранного с Telegram-ботом включается.

Обращения пользователей сохраняются в `telegram_bot/storage/feedback.json`. Файл создаётся автоматически при первом обращении через `/feedback` или вкладку `Поддержка` в Mini App и не должен попадать в Git.

## 10. Частые проблемы

### Backend не запущен

Симптом: бот пишет, что не получилось получить список вузов.

Решение:

```bash
bash scripts/run_backend.sh
```

### Порт 8000 занят

Симптом: backend не стартует, потому что порт занят.

Решение: остановить процесс на порту 8000 или задать другой порт через `BACKEND_PORT`.

### ngrok ссылка изменилась

Ngrok URL временный. Если ngrok перезапущен, нужно обновить:

- `WEBAPP_URL` в локальном `.env`;
- Menu Button в BotFather;
- Main App в BotFather.

### VPN или интернет мешают Telegram API

Симптом: бот не отвечает или polling не запускается.

Решение: проверить интернет, VPN и доступность Telegram API.

### `WEBAPP_URL` пустой

Если `WEBAPP_URL` пустой, кнопка `Mini App` в меню остаётся обычной текстовой кнопкой и показывает подсказку. Это нормальное поведение: бот продолжает работать как обычный Telegram-бот.

Для визуального меню Telegram-бота нужны локальные ассеты из `telegram_bot/assets/menu/`. Они уже лежат в проекте. Если Telegram не примет баннер или файл временно недоступен, бот покажет текстовый fallback и продолжит работать.
