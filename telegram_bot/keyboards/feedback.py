from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

from telegram_bot.services.feedback import FEEDBACK_CATEGORIES


FEEDBACK_CATEGORY_PREFIX = "feedback_category:"
FEEDBACK_CANCEL_CALLBACK = "feedback_cancel"


def feedback_categories_keyboard() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=label, callback_data=f"{FEEDBACK_CATEGORY_PREFIX}{category}")]
        for category, label in FEEDBACK_CATEGORIES.items()
    ]
    rows.append([InlineKeyboardButton(text="Отмена", callback_data=FEEDBACK_CANCEL_CALLBACK)])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def feedback_cancel_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Отмена")]],
        resize_keyboard=True,
        input_field_placeholder="Опиши обращение",
    )


def feedback_created_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Мои обращения")],
            [KeyboardButton(text="Создать ещё обращение")],
            [KeyboardButton(text="🔙 Главное меню")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Что сделать дальше",
    )


def empty_feedback_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Создать обращение")],
            [KeyboardButton(text="🔙 Главное меню")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Выбери действие",
    )
