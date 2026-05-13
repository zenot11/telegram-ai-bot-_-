from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, WebAppInfo

from telegram_bot.config import settings

MAX_FAVORITE_ACTION_BUTTONS = 5


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton(text="Подобрать вуз"), KeyboardButton(text="Сравнить вузы")],
        [KeyboardButton(text="Избранные вузы"), KeyboardButton(text="Мой профиль")],
        [KeyboardButton(text="Направления"), KeyboardButton(text="Регионы")],
        [KeyboardButton(text="Как читать категории")],
    ]
    if settings.webapp_url:
        keyboard.append([KeyboardButton(text="Открыть Mini App", web_app=WebAppInfo(url=settings.webapp_url))])
    keyboard.extend(
        [
            [KeyboardButton(text="Психологическая поддержка")],
            [KeyboardButton(text="Помощь")],
        ]
    )

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Выбери действие",
    )


def profile_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Подобрать вуз"), KeyboardButton(text="Избранные вузы")],
            [KeyboardButton(text="Сравнить вузы")],
            [KeyboardButton(text="Сбросить профиль")],
            [KeyboardButton(text="Вернуться в меню")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Выбери действие",
    )


def favorites_keyboard() -> ReplyKeyboardMarkup:
    return favorites_keyboard_for_count(0)


def favorites_keyboard_for_count(items_count: int) -> ReplyKeyboardMarkup:
    delete_buttons = [
        KeyboardButton(text=f"Удалить {index}")
        for index in range(1, min(items_count, MAX_FAVORITE_ACTION_BUTTONS) + 1)
    ]

    keyboard = []
    if delete_buttons:
        keyboard.extend(_chunk_buttons(delete_buttons, 3))
    keyboard.extend(
        [
            [KeyboardButton(text="Очистить избранное")],
            [KeyboardButton(text="Сравнить вузы")],
            [KeyboardButton(text="Подобрать вуз"), KeyboardButton(text="Вернуться в меню")],
        ]
    )

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Выбери действие",
    )


def _chunk_buttons(buttons: list[KeyboardButton], size: int) -> list[list[KeyboardButton]]:
    return [buttons[index:index + size] for index in range(0, len(buttons), size)]


def empty_favorites_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Подобрать вуз")],
            [KeyboardButton(text="Вернуться в меню")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Выбери действие",
    )
