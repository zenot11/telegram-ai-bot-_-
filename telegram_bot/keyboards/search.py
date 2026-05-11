from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def education_type_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Бюджет"), KeyboardButton(text="Платное")]],
        resize_keyboard=True,
        input_field_placeholder="Бюджет или платное",
    )


def support_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Подобрать 3 варианта")],
            [KeyboardButton(text="Сделать короткий план")],
            [KeyboardButton(text="Вернуться позже")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Выбери следующий шаг",
    )
