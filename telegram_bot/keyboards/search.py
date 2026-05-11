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
            [KeyboardButton(text="Мне тревожно")],
            [KeyboardButton(text="Я не знаю, куда поступать")],
            [KeyboardButton(text="Я боюсь не поступить")],
            [KeyboardButton(text="На меня давят родители")],
            [KeyboardButton(text="Составить короткий план")],
            [KeyboardButton(text="Вернуться в меню")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Выбери следующий шаг",
    )
