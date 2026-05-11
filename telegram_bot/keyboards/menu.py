from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Подобрать вуз"), KeyboardButton(text="Мои баллы")],
            [KeyboardButton(text="Направления"), KeyboardButton(text="Регионы")],
            [KeyboardButton(text="Психологическая поддержка")],
            [KeyboardButton(text="Помощь")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Выбери действие",
    )
