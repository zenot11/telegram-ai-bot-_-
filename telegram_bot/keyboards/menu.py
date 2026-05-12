from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Подобрать вуз"), KeyboardButton(text="Мой профиль")],
            [KeyboardButton(text="Избранные вузы")],
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
            [KeyboardButton(text="Сбросить профиль")],
            [KeyboardButton(text="Вернуться в меню")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Выбери действие",
    )


def favorites_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Очистить избранное")],
            [KeyboardButton(text="Подобрать ещё")],
            [KeyboardButton(text="Вернуться в меню")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Выбери действие",
    )
