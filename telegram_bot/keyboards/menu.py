from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, WebAppInfo

from telegram_bot.config import settings

MAX_FAVORITE_ACTION_BUTTONS = 5


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton(text="Подобрать вуз"), _mini_app_button("Mini App")],
        [KeyboardButton(text="Мои результаты"), KeyboardButton(text="Помощник")],
        [KeyboardButton(text="Сервис"), KeyboardButton(text="О проекте")],
    ]

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Выбери раздел",
    )


def results_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Итог подбора"), KeyboardButton(text="Избранные вузы")],
            [KeyboardButton(text="История подборов"), KeyboardButton(text="Сравнить вузы")],
            [KeyboardButton(text="Фильтры результатов"), KeyboardButton(text="Экспорт результата")],
            [KeyboardButton(text="Назад")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Действия с результатами",
    )


def assistant_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Советы по подбору"), KeyboardButton(text="Что делать дальше")],
            [KeyboardButton(text="Как читать категории")],
            [KeyboardButton(text="Направления"), KeyboardButton(text="Регионы")],
            [KeyboardButton(text="Психологическая поддержка")],
            [_mini_app_button("Mini App")],
            [KeyboardButton(text="Назад")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Советы и поддержка",
    )


def service_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Мой профиль")],
            [KeyboardButton(text="Обратная связь"), KeyboardButton(text="Мои обращения")],
            [KeyboardButton(text="Приватность"), KeyboardButton(text="Сбросить данные")],
            [KeyboardButton(text="Назад")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Сервисные действия",
    )


def about_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Описание проекта"), KeyboardButton(text="Демо-сценарий")],
            [KeyboardButton(text="BotFather")],
            [KeyboardButton(text="Назад")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Информация о проекте",
    )


def back_to_main_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Назад")]],
        resize_keyboard=True,
        input_field_placeholder="Вернуться в меню",
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


def summary_keyboard() -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton(text="Избранные вузы"), KeyboardButton(text="Сравнить вузы")],
        [KeyboardButton(text="Советы по подбору"), KeyboardButton(text="Фильтры результатов")],
        [KeyboardButton(text="Экспорт результата"), KeyboardButton(text="История подборов")],
    ]
    if settings.webapp_url:
        keyboard.append([KeyboardButton(text="Открыть Mini App", web_app=WebAppInfo(url=settings.webapp_url))])
    keyboard.extend(
        [
            [KeyboardButton(text="Подобрать вуз"), KeyboardButton(text="Вернуться в меню")],
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


def history_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Повторить последний подбор")],
            [KeyboardButton(text="Очистить историю")],
            [KeyboardButton(text="Подобрать вуз"), KeyboardButton(text="Вернуться в меню")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Выбери действие",
    )


def empty_history_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Подобрать вуз")],
            [KeyboardButton(text="Вернуться в меню")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Выбери действие",
    )


def advice_keyboard(has_results: bool) -> ReplyKeyboardMarkup:
    keyboard = []
    if has_results:
        keyboard.extend(
            [
                [KeyboardButton(text="Итог подбора"), KeyboardButton(text="Сравнить вузы")],
                [KeyboardButton(text="Избранные вузы"), KeyboardButton(text="Фильтры результатов")],
                [KeyboardButton(text="Экспорт результата"), KeyboardButton(text="История подборов")],
            ]
        )
    else:
        keyboard.append([KeyboardButton(text="История подборов")])

    keyboard.append([KeyboardButton(text="Подобрать заново")])
    if settings.webapp_url:
        keyboard.append([KeyboardButton(text="Открыть Mini App", web_app=WebAppInfo(url=settings.webapp_url))])
    keyboard.append([KeyboardButton(text="Вернуться в меню")])

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Что сделать дальше",
    )


def empty_advice_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Подобрать вуз")],
            [KeyboardButton(text="Вернуться в меню")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Выбери действие",
    )


def _mini_app_button(text: str = "Mini App") -> KeyboardButton:
    if settings.webapp_url:
        return KeyboardButton(text=text, web_app=WebAppInfo(url=settings.webapp_url))
    return KeyboardButton(text=text)
