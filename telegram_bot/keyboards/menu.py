from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, WebAppInfo

from telegram_bot.config import settings

MAX_FAVORITE_ACTION_BUTTONS = 5

MENU_MAIN_CALLBACK = "menu:main"
MENU_RESULTS_CALLBACK = "menu:results"
MENU_ASSISTANT_CALLBACK = "menu:assistant"
MENU_SERVICE_CALLBACK = "menu:service"
MENU_ABOUT_CALLBACK = "menu:about"
MENU_SEARCH_CALLBACK = "menu:search"
MENU_WEBAPP_CALLBACK = "menu:webapp"
MENU_SUMMARY_CALLBACK = "menu:summary"
MENU_FAVORITES_CALLBACK = "menu:favorites"
MENU_HISTORY_CALLBACK = "menu:history"
MENU_COMPARE_CALLBACK = "menu:compare"
MENU_FILTERS_CALLBACK = "menu:filters"
MENU_EXPORT_CALLBACK = "menu:export"
MENU_ADVICE_CALLBACK = "menu:advice"
MENU_NEXT_CALLBACK = "menu:next"
MENU_SUPPORT_CALLBACK = "menu:support"
MENU_CATEGORIES_CALLBACK = "menu:categories"
MENU_ACHIEVEMENTS_CALLBACK = "menu:achievements"
MENU_DIRECTIONS_CALLBACK = "menu:directions"
MENU_REGIONS_CALLBACK = "menu:regions"
MENU_PROFILE_CALLBACK = "menu:profile"
MENU_FEEDBACK_CALLBACK = "menu:feedback"
MENU_MY_FEEDBACK_CALLBACK = "menu:my_feedback"
MENU_PRIVACY_CALLBACK = "menu:privacy"
MENU_RESET_CALLBACK = "menu:reset"
MENU_ABOUT_TEXT_CALLBACK = "menu:about_text"
MENU_DEMO_CALLBACK = "menu:demo"
MENU_BOTFATHER_CALLBACK = "menu:botfather"


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton(text="🎓 Подобрать вуз"), _mini_app_button("📱 Mini App")],
        [KeyboardButton(text="📌 Мои результаты"), KeyboardButton(text="🤝 Помощник")],
        [KeyboardButton(text="⚙️ Сервис"), KeyboardButton(text="ℹ️ О проекте")],
    ]

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Выбери раздел",
    )


def main_menu_inline_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🎓 Подобрать вуз", callback_data=MENU_SEARCH_CALLBACK),
                _mini_app_inline_button("📱 Mini App"),
            ],
            [
                InlineKeyboardButton(text="📌 Мои результаты", callback_data=MENU_RESULTS_CALLBACK),
                InlineKeyboardButton(text="🤝 Помощник", callback_data=MENU_ASSISTANT_CALLBACK),
            ],
            [
                InlineKeyboardButton(text="⚙️ Сервис", callback_data=MENU_SERVICE_CALLBACK),
                InlineKeyboardButton(text="ℹ️ О проекте", callback_data=MENU_ABOUT_CALLBACK),
            ],
        ]
    )


def results_menu_inline_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⭐ Избранные вузы", callback_data=MENU_FAVORITES_CALLBACK)],
            [InlineKeyboardButton(text="⚖️ Сравнить вузы", callback_data=MENU_COMPARE_CALLBACK)],
            [InlineKeyboardButton(text="📤 Экспорт результата", callback_data=MENU_EXPORT_CALLBACK)],
            [InlineKeyboardButton(text="🕘 История подборов", callback_data=MENU_HISTORY_CALLBACK)],
            [InlineKeyboardButton(text="📊 Итог подбора", callback_data=MENU_SUMMARY_CALLBACK)],
            [InlineKeyboardButton(text="🔙 Назад", callback_data=MENU_MAIN_CALLBACK)],
        ]
    )


def assistant_menu_inline_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Мне тревожно", callback_data=MENU_SUPPORT_CALLBACK)],
            [InlineKeyboardButton(text="Я не знаю, куда поступать", callback_data=MENU_SUPPORT_CALLBACK)],
            [InlineKeyboardButton(text="Я боюсь не поступить", callback_data=MENU_SUPPORT_CALLBACK)],
            [InlineKeyboardButton(text="На меня давят родители", callback_data=MENU_SUPPORT_CALLBACK)],
            [InlineKeyboardButton(text="Составить короткий план", callback_data=MENU_NEXT_CALLBACK)],
            [InlineKeyboardButton(text="🔙 Назад", callback_data=MENU_MAIN_CALLBACK)],
        ]
    )


def next_steps_inline_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🎓 Подобрать вуз", callback_data=MENU_SEARCH_CALLBACK),
                InlineKeyboardButton(text="Советы по подбору", callback_data=MENU_ADVICE_CALLBACK),
            ],
            [_mini_app_inline_button("📱 Mini App")],
            [InlineKeyboardButton(text="🔙 Главное меню", callback_data=MENU_MAIN_CALLBACK)],
        ]
    )


def service_menu_inline_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔎 Фильтры результатов", callback_data=MENU_FILTERS_CALLBACK)],
            [InlineKeyboardButton(text="📖 Как читать категории", callback_data=MENU_CATEGORIES_CALLBACK)],
            [InlineKeyboardButton(text="🔐 Приватность", callback_data=MENU_PRIVACY_CALLBACK)],
            [InlineKeyboardButton(text="🧹 Сбросить данные", callback_data=MENU_RESET_CALLBACK)],
            [InlineKeyboardButton(text="🛠 BotFather", callback_data=MENU_BOTFATHER_CALLBACK)],
            [InlineKeyboardButton(text="📬 Обратная связь", callback_data=MENU_FEEDBACK_CALLBACK)],
            [InlineKeyboardButton(text="🔙 Назад", callback_data=MENU_MAIN_CALLBACK)],
        ]
    )


def about_menu_inline_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="О проекте", callback_data=MENU_ABOUT_TEXT_CALLBACK),
                InlineKeyboardButton(text="Демо-сценарий", callback_data=MENU_DEMO_CALLBACK),
            ],
            [InlineKeyboardButton(text="🛠 BotFather", callback_data=MENU_BOTFATHER_CALLBACK)],
            [InlineKeyboardButton(text="🔙 Назад", callback_data=MENU_MAIN_CALLBACK)],
        ]
    )


def results_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⭐ Избранные вузы")],
            [KeyboardButton(text="⚖️ Сравнить вузы")],
            [KeyboardButton(text="📤 Экспорт результата")],
            [KeyboardButton(text="🕘 История подборов")],
            [KeyboardButton(text="📊 Итог подбора")],
            [KeyboardButton(text="🔙 Назад")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Мои результаты",
    )


def assistant_menu_keyboard() -> ReplyKeyboardMarkup:
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
        input_field_placeholder="Мягкая поддержка",
    )


def service_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔎 Фильтры результатов")],
            [KeyboardButton(text="📖 Как читать категории")],
            [KeyboardButton(text="🔐 Приватность")],
            [KeyboardButton(text="🧹 Сбросить данные")],
            [KeyboardButton(text="🛠 BotFather")],
            [KeyboardButton(text="📬 Обратная связь")],
            [KeyboardButton(text="🔙 Назад")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Сервис",
    )


def about_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Описание проекта"), KeyboardButton(text="Демо-сценарий")],
            [KeyboardButton(text="🛠 BotFather")],
            [KeyboardButton(text="🔙 Назад")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Информация о проекте",
    )


def back_to_main_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🔙 Назад")]],
        resize_keyboard=True,
        input_field_placeholder="Вернуться в меню",
    )


def profile_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎓 Подобрать вуз"), KeyboardButton(text="⭐ Избранные вузы")],
            [KeyboardButton(text="⚖️ Сравнить вузы")],
            [KeyboardButton(text="🧹 Сбросить данные")],
            [KeyboardButton(text="🔙 Главное меню")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Выбери действие",
    )


def summary_keyboard() -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton(text="📌 Мои результаты")],
        [KeyboardButton(text="🤝 Помощник"), KeyboardButton(text="⚙️ Сервис")],
    ]
    if settings.webapp_url:
        keyboard.append([KeyboardButton(text="📱 Mini App", web_app=WebAppInfo(url=settings.webapp_url))])
    keyboard.extend(
        [
            [KeyboardButton(text="🎓 Новый подбор")],
            [KeyboardButton(text="🔙 Главное меню")],
        ]
    )

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Что открыть дальше",
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
            [KeyboardButton(text="⚖️ Сравнить вузы")],
            [KeyboardButton(text="🎓 Подобрать вуз"), KeyboardButton(text="🔙 Главное меню")],
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
            [KeyboardButton(text="🎓 Подобрать вуз")],
            [KeyboardButton(text="🔙 Главное меню")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Выбери действие",
    )


def history_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Повторить последний подбор")],
            [KeyboardButton(text="Очистить историю")],
            [KeyboardButton(text="🎓 Подобрать вуз"), KeyboardButton(text="🔙 Главное меню")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Выбери действие",
    )


def empty_history_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎓 Подобрать вуз")],
            [KeyboardButton(text="🔙 Главное меню")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Выбери действие",
    )


def advice_keyboard(has_results: bool) -> ReplyKeyboardMarkup:
    keyboard = []
    if has_results:
        keyboard.extend(
            [
                [KeyboardButton(text="📌 Мои результаты")],
                [KeyboardButton(text="⚙️ Сервис")],
            ]
        )
    else:
        keyboard.append([KeyboardButton(text="📌 Мои результаты")])

    keyboard.append([KeyboardButton(text="🎓 Новый подбор")])
    if settings.webapp_url:
        keyboard.append([KeyboardButton(text="📱 Mini App", web_app=WebAppInfo(url=settings.webapp_url))])
    keyboard.append([KeyboardButton(text="🔙 Главное меню")])

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Что сделать дальше",
    )


def empty_advice_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎓 Подобрать вуз")],
            [KeyboardButton(text="🔙 Главное меню")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Выбери действие",
    )


def _mini_app_button(text: str = "Mini App") -> KeyboardButton:
    if settings.webapp_url:
        return KeyboardButton(text=text, web_app=WebAppInfo(url=settings.webapp_url))
    return KeyboardButton(text=text)


def _mini_app_inline_button(text: str = "Mini App") -> InlineKeyboardButton:
    if settings.webapp_url:
        return InlineKeyboardButton(text=text, web_app=WebAppInfo(url=settings.webapp_url))
    return InlineKeyboardButton(text=text, callback_data=MENU_WEBAPP_CALLBACK)
