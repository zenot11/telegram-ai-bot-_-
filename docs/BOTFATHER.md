# Настройка BotFather

Этот документ описывает команды Telegram-бота и настройки Mini App через BotFather.

## Команды бота

Готовый список для `/setcommands`:

```text
start - Запуск бота
menu - Главное меню
search - Подобрать вуз
summary - Итог последнего подбора
advice - Советы по подбору
filters - Фильтры результатов
export - Экспорт результата
history - История подборов
compare - Сравнить вузы
categories - Как читать категории
support - Психологическая поддержка
webapp - Открыть Mini App
about - О проекте
demo - Сценарий демонстрации
privacy - Приватность
next - Что подготовить перед сдачей
botfather - Настройки BotFather
clear_history - Очистить историю подборов
reset - Сброс введённых данных
help - Помощь
```

В самом боте команда `/botfather` выводит такую же подсказку.

## Mini App

Для Telegram Mini App нужен публичный HTTPS URL.

Локальный адрес:

```text
http://localhost:8000/miniapp
```

подходит только для проверки в браузере.

Для проверки внутри Telegram можно использовать ngrok:

```bash
ngrok http 8000
```

После запуска ngrok нужно указать URL в локальном `.env`:

```env
WEBAPP_URL=https://your-ngrok-url.ngrok-free.dev/miniapp
```

После изменения `.env` нужно перезапустить Telegram-бота.

## Menu Button

В BotFather:

```text
Mini Apps -> Menu Button
```

Настройки:

```text
URL = WEBAPP_URL из .env
Label = Mini App
```

Можно использовать label:

```text
Открыть Аишу
```

## Main App

В BotFather:

```text
Mini Apps -> Main App
```

Настройки:

```text
URL = WEBAPP_URL из .env
Launch mode = fullsize
```

## Direct Link

Direct Link можно использовать для быстрого запуска сценария Mini App.

Это внешняя настройка BotFather. Она не меняет код проекта и не создаёт git commit.

## Важное предупреждение

Ngrok URL временный. Если ngrok перезапущен и ссылка изменилась, нужно обновить:

- `WEBAPP_URL` в локальном `.env`;
- BotFather Menu Button;
- BotFather Main App.

Если `WEBAPP_URL` пустой, кнопка Mini App в меню Telegram-бота не показывается. Это нормальное fallback-поведение.
