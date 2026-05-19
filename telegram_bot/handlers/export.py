from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, CallbackQuery, Message

from telegram_bot.keyboards.export import (
    EXPORT_ADVICE_CALLBACK,
    EXPORT_BACK_CALLBACK,
    EXPORT_SUMMARY_CALLBACK,
    EXPORT_TEXT_CALLBACK,
    EXPORT_TXT_CALLBACK,
    empty_export_keyboard,
    export_menu_keyboard,
)
from telegram_bot.keyboards.menu import advice_keyboard, main_menu_keyboard, summary_keyboard
from telegram_bot.services.advice import build_advice, has_advice_context
from telegram_bot.services.export import (
    EXPORT_MESSAGE_LIMIT,
    build_export_preview,
    build_export_report,
    make_export_filename,
    split_message,
)
from telegram_bot.services.summary import EMPTY_SUMMARY_TEXT, format_last_search_summary
from telegram_bot.storage.user_data import user_storage


router = Router()


@router.message(Command("export"))
@router.message(F.text == "Экспорт результата")
async def show_export_menu(message: Message, state: FSMContext) -> None:
    await state.clear()
    if not message.from_user:
        await message.answer("Не удалось определить пользователя.", reply_markup=main_menu_keyboard())
        return

    profile, results, favorites = _export_context(message.from_user.id)
    if not results:
        await message.answer(
            "Пока нет результата для экспорта.\n"
            "Сначала сделай подбор через /search.",
            reply_markup=empty_export_keyboard(),
        )
        return

    await message.answer(
        build_export_preview(profile, results, favorites),
        reply_markup=export_menu_keyboard(),
    )


@router.callback_query(F.data == EXPORT_TEXT_CALLBACK)
async def export_as_text(callback: CallbackQuery) -> None:
    await callback.answer()
    if not callback.from_user or not callback.message:
        return

    profile, results, favorites = _export_context(callback.from_user.id)
    if not results:
        await callback.message.answer(
            "Пока нет результата для экспорта.\n"
            "Сначала сделай подбор через /search.",
            reply_markup=empty_export_keyboard(),
        )
        return

    report = build_export_report(profile, results, favorites)
    if len(report) > EXPORT_MESSAGE_LIMIT:
        await callback.message.answer(
            "Отчёт получился длинным. Лучше скачать его файлом.",
            reply_markup=export_menu_keyboard(),
        )
        return

    for part in split_message(report, EXPORT_MESSAGE_LIMIT):
        await callback.message.answer(f"<pre>{_html_escape(part)}</pre>")


@router.callback_query(F.data == EXPORT_TXT_CALLBACK)
async def export_as_txt(callback: CallbackQuery) -> None:
    await callback.answer()
    if not callback.from_user or not callback.message:
        return

    profile, results, favorites = _export_context(callback.from_user.id)
    if not results:
        await callback.message.answer(
            "Пока нет результата для экспорта.\n"
            "Сначала сделай подбор через /search.",
            reply_markup=empty_export_keyboard(),
        )
        return

    report = build_export_report(profile, results, favorites)
    document = BufferedInputFile(
        report.encode("utf-8"),
        filename=make_export_filename(),
    )
    await callback.message.answer_document(
        document=document,
        caption="Готово. Отправляю текстовый отчёт по последнему подбору.",
    )


@router.callback_query(F.data == EXPORT_SUMMARY_CALLBACK)
async def export_show_summary(callback: CallbackQuery) -> None:
    await callback.answer()
    if not callback.from_user or not callback.message:
        return

    profile, results, favorites = _export_context(callback.from_user.id)
    text = format_last_search_summary(profile, results, len(favorites))
    reply_markup = summary_keyboard() if text != EMPTY_SUMMARY_TEXT else main_menu_keyboard()
    await callback.message.answer(text, reply_markup=reply_markup)


@router.callback_query(F.data == EXPORT_ADVICE_CALLBACK)
async def export_show_advice(callback: CallbackQuery) -> None:
    await callback.answer()
    if not callback.from_user or not callback.message:
        return

    profile, results, favorites = _export_context(callback.from_user.id)
    text = build_advice(profile, results, favorites)
    reply_markup = advice_keyboard(has_results=bool(results)) if has_advice_context(profile) else main_menu_keyboard()
    await callback.message.answer(text, reply_markup=reply_markup)


@router.callback_query(F.data == EXPORT_BACK_CALLBACK)
async def export_back_to_menu(callback: CallbackQuery) -> None:
    await callback.answer()
    if callback.message:
        await callback.message.answer("Главное меню. Выбери, с чего начнём:", reply_markup=main_menu_keyboard())


def _export_context(telegram_id: int) -> tuple[dict | None, list[dict], list[dict]]:
    return (
        user_storage.get_profile(telegram_id),
        user_storage.get_last_results(telegram_id),
        user_storage.get_favorites(telegram_id),
    )


def _html_escape(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
