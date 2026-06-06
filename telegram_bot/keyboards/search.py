from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

MAX_SAVE_BUTTONS = 5


def education_type_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Бюджет"), KeyboardButton(text="Платное")],
            [KeyboardButton(text="Любое"), KeyboardButton(text="Назад")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Бюджет, платное или любое",
    )


def search_results_keyboard(
    results_count: int,
    *,
    start_index: int = 1,
    has_more: bool = False,
) -> ReplyKeyboardMarkup:
    start_index = max(1, start_index)
    save_count = min(results_count, MAX_SAVE_BUTTONS)
    save_buttons = [
        KeyboardButton(text=f"⭐ Сохранить {index}")
        for index in range(start_index, start_index + save_count)
    ]
    rows = []
    if save_buttons:
        rows.extend(_chunk_buttons(save_buttons, 3))
    if has_more:
        rows.append([KeyboardButton(text="➡️ Ещё варианты")])
    rows.extend(
        [
            [KeyboardButton(text="📌 Мои результаты")],
            [KeyboardButton(text="🎓 Новый подбор")],
            [KeyboardButton(text="🔙 Главное меню")],
        ]
    )

    return ReplyKeyboardMarkup(
        keyboard=rows,
        resize_keyboard=True,
        input_field_placeholder="Можно сохранить вариант",
    )


def _chunk_buttons(buttons: list[KeyboardButton], size: int) -> list[list[KeyboardButton]]:
    return [buttons[index:index + size] for index in range(0, len(buttons), size)]


def no_results_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎓 Новый подбор")],
            [KeyboardButton(text="Регионы"), KeyboardButton(text="Направления")],
            [KeyboardButton(text="🔙 Главное меню")],
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
            [KeyboardButton(text="🔙 Назад")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Выбери следующий шаг",
    )
