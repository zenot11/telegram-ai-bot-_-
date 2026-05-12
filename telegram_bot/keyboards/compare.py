from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def compare_source_keyboard(has_last_results: bool, has_favorites: bool) -> ReplyKeyboardMarkup:
    rows = []
    if has_last_results:
        rows.append([KeyboardButton(text="Сравнить последние результаты")])
    if has_favorites:
        rows.append([KeyboardButton(text="Сравнить избранные вузы")])
    rows.append([KeyboardButton(text="Вернуться в меню")])

    return ReplyKeyboardMarkup(
        keyboard=rows,
        resize_keyboard=True,
        input_field_placeholder="Выбери источник для сравнения",
    )


def compare_options_keyboard(items_count: int) -> ReplyKeyboardMarkup:
    rows = []
    if items_count >= 2:
        rows.append([KeyboardButton(text="Сравнить 1 и 2")])
    if items_count >= 3:
        rows.append([KeyboardButton(text="Сравнить 1 и 3"), KeyboardButton(text="Сравнить 2 и 3")])
        rows.append([KeyboardButton(text="Сравнить первые 3")])
    rows.append([KeyboardButton(text="Вернуться в меню")])

    return ReplyKeyboardMarkup(
        keyboard=rows,
        resize_keyboard=True,
        input_field_placeholder="Выбери варианты",
    )
