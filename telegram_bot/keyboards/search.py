from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def education_type_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Бюджет"), KeyboardButton(text="Платное")]],
        resize_keyboard=True,
        input_field_placeholder="Бюджет или платное",
    )


def search_results_keyboard(results_count: int) -> ReplyKeyboardMarkup:
    save_buttons = [
        KeyboardButton(text=f"Сохранить {index}")
        for index in range(1, min(results_count, 3) + 1)
    ]
    rows = []
    if save_buttons:
        rows.append(save_buttons)
    rows.extend(
        [
            [KeyboardButton(text="Избранные вузы"), KeyboardButton(text="Сравнить вузы")],
            [KeyboardButton(text="Как читать категории")],
            [KeyboardButton(text="Новый подбор"), KeyboardButton(text="Вернуться в меню")],
        ]
    )

    return ReplyKeyboardMarkup(
        keyboard=rows,
        resize_keyboard=True,
        input_field_placeholder="Можно сохранить вариант",
    )


def no_results_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Новый подбор")],
            [KeyboardButton(text="Регионы"), KeyboardButton(text="Направления")],
            [KeyboardButton(text="Вернуться в меню")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Попробуй изменить запрос",
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
