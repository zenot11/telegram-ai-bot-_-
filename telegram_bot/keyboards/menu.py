from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Подобрать вуз"), KeyboardButton(text="Сравнить вузы")],
            [KeyboardButton(text="Избранные вузы"), KeyboardButton(text="Мой профиль")],
            [KeyboardButton(text="Направления"), KeyboardButton(text="Регионы")],
            [KeyboardButton(text="Психологическая поддержка")],
            [KeyboardButton(text="Помощь")],
        ],
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
        for index in range(1, min(items_count, 3) + 1)
    ]

    keyboard = []
    if delete_buttons:
        keyboard.append(delete_buttons)
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


def empty_favorites_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Подобрать вуз")],
            [KeyboardButton(text="Вернуться в меню")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Выбери действие",
    )
