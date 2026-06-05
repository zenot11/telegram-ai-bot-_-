from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup


EXPORT_TEXT_CALLBACK = "export_text"
EXPORT_TXT_CALLBACK = "export_txt"
EXPORT_SUMMARY_CALLBACK = "export_summary"
EXPORT_ADVICE_CALLBACK = "export_advice"
EXPORT_BACK_CALLBACK = "export_back"


def export_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Показать текстом", callback_data=EXPORT_TEXT_CALLBACK),
                InlineKeyboardButton(text="Скачать .txt", callback_data=EXPORT_TXT_CALLBACK),
            ],
            [
                InlineKeyboardButton(text="Итог подбора", callback_data=EXPORT_SUMMARY_CALLBACK),
                InlineKeyboardButton(text="Советы по подбору", callback_data=EXPORT_ADVICE_CALLBACK),
            ],
            [InlineKeyboardButton(text="🔙 Главное меню", callback_data=EXPORT_BACK_CALLBACK)],
        ]
    )


def empty_export_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎓 Подобрать вуз")],
            [KeyboardButton(text="🔙 Главное меню")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Сначала сделай подбор",
    )
