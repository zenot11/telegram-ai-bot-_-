from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

from telegram_bot.keyboards.search import MAX_SAVE_BUTTONS
from telegram_bot.services.filters import (
    FILTER_ALL,
    FILTER_AMBITIOUS,
    FILTER_BUDGET,
    FILTER_PAID,
    FILTER_REALISTIC,
    FILTER_SAFE,
)


FILTER_CALLBACK_PREFIX = "filter_"


def filters_keyboard(counts: dict[str, int]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"Все варианты ({counts.get(FILTER_ALL, 0)})",
                    callback_data=f"{FILTER_CALLBACK_PREFIX}{FILTER_ALL}",
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"🟢 Безопасные ({counts.get(FILTER_SAFE, 0)})",
                    callback_data=f"{FILTER_CALLBACK_PREFIX}{FILTER_SAFE}",
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"🟡 Реалистичные ({counts.get(FILTER_REALISTIC, 0)})",
                    callback_data=f"{FILTER_CALLBACK_PREFIX}{FILTER_REALISTIC}",
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"🔴 Амбициозные ({counts.get(FILTER_AMBITIOUS, 0)})",
                    callback_data=f"{FILTER_CALLBACK_PREFIX}{FILTER_AMBITIOUS}",
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"Бюджет ({counts.get(FILTER_BUDGET, 0)})",
                    callback_data=f"{FILTER_CALLBACK_PREFIX}{FILTER_BUDGET}",
                ),
                InlineKeyboardButton(
                    text=f"Платное ({counts.get(FILTER_PAID, 0)})",
                    callback_data=f"{FILTER_CALLBACK_PREFIX}{FILTER_PAID}",
                ),
            ],
        ]
    )


def filtered_results_keyboard(results_count: int) -> ReplyKeyboardMarkup:
    save_buttons = [
        KeyboardButton(text=f"Сохранить {index}")
        for index in range(1, min(results_count, MAX_SAVE_BUTTONS) + 1)
    ]
    rows = []
    if save_buttons:
        rows.extend(_chunk_buttons(save_buttons, 3))
    rows.extend(
        [
            [KeyboardButton(text="Все варианты"), KeyboardButton(text="Фильтры результатов")],
            [KeyboardButton(text="Итог подбора"), KeyboardButton(text="Советы по подбору")],
            [KeyboardButton(text="Избранные вузы"), KeyboardButton(text="Вернуться в меню")],
        ]
    )

    return ReplyKeyboardMarkup(
        keyboard=rows,
        resize_keyboard=True,
        input_field_placeholder="Можно сохранить вариант",
    )


def empty_filters_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Подобрать вуз")],
            [KeyboardButton(text="Вернуться в меню")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Сначала сделай подбор",
    )


def empty_filtered_results_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Все варианты"), KeyboardButton(text="Фильтры результатов")],
            [KeyboardButton(text="Подобрать заново"), KeyboardButton(text="Советы по подбору")],
            [KeyboardButton(text="Вернуться в меню")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Выбери действие",
    )


def _chunk_buttons(buttons: list[KeyboardButton], size: int) -> list[list[KeyboardButton]]:
    return [buttons[index:index + size] for index in range(0, len(buttons), size)]
