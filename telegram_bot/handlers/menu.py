from html import escape

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message, WebAppInfo

from telegram_bot.config import settings
from telegram_bot.keyboards.compare import (
    compare_options_keyboard,
    compare_source_keyboard,
    empty_compare_keyboard,
    not_enough_favorites_keyboard,
)
from telegram_bot.keyboards.export import empty_export_keyboard, export_menu_keyboard
from telegram_bot.keyboards.feedback import empty_feedback_keyboard, feedback_categories_keyboard, feedback_created_keyboard
from telegram_bot.keyboards.filters import empty_filters_keyboard, filters_keyboard
from telegram_bot.keyboards.menu import (
    MENU_ABOUT_CALLBACK,
    MENU_ABOUT_TEXT_CALLBACK,
    MENU_ACHIEVEMENTS_CALLBACK,
    MENU_ADVICE_CALLBACK,
    MENU_ASSISTANT_CALLBACK,
    MENU_BOTFATHER_CALLBACK,
    MENU_CATEGORIES_CALLBACK,
    MENU_COMPARE_CALLBACK,
    MENU_DEMO_CALLBACK,
    MENU_DIRECTIONS_CALLBACK,
    MENU_EXPORT_CALLBACK,
    MENU_FAVORITES_CALLBACK,
    MENU_FEEDBACK_CALLBACK,
    MENU_FILTERS_CALLBACK,
    MENU_HISTORY_CALLBACK,
    MENU_MAIN_CALLBACK,
    MENU_MY_FEEDBACK_CALLBACK,
    MENU_NEXT_CALLBACK,
    MENU_PRIVACY_CALLBACK,
    MENU_PROFILE_CALLBACK,
    MENU_REGIONS_CALLBACK,
    MENU_RESET_CALLBACK,
    MENU_RESULTS_CALLBACK,
    MENU_SEARCH_CALLBACK,
    MENU_SERVICE_CALLBACK,
    MENU_SUMMARY_CALLBACK,
    MENU_SUPPORT_CALLBACK,
    MENU_WEBAPP_CALLBACK,
    about_menu_keyboard,
    about_menu_inline_keyboard,
    advice_keyboard,
    assistant_menu_keyboard,
    assistant_menu_inline_keyboard,
    empty_advice_keyboard,
    empty_favorites_keyboard,
    empty_history_keyboard,
    favorites_keyboard_for_count,
    history_keyboard,
    main_menu_keyboard,
    main_menu_inline_keyboard,
    next_steps_inline_keyboard,
    profile_keyboard,
    results_menu_keyboard,
    results_menu_inline_keyboard,
    service_menu_keyboard,
    service_menu_inline_keyboard,
    summary_keyboard,
)
from telegram_bot.keyboards.search import no_results_keyboard, search_results_keyboard, support_keyboard
from telegram_bot.services.api import UniversityAPIError, fetch_achievements, fetch_directory_items, fetch_universities
from telegram_bot.services.advice import build_advice, has_advice_context
from telegram_bot.services.export import build_export_preview
from telegram_bot.services.feedback import format_user_feedback
from telegram_bot.services.filters import EMPTY_FILTERS_TEXT, build_filters_overview_message, get_filter_counts
from telegram_bot.services.formatters import format_university_card
from telegram_bot.services.history import format_history_message
from telegram_bot.services.menu_cards import send_menu_card
from telegram_bot.services.next_steps import build_next_steps_text
from telegram_bot.services.recommendation import (
    format_categories_explanation,
    group_universities_by_recommendation,
    visible_recommendations,
)
from telegram_bot.services.summary import EMPTY_SUMMARY_TEXT, format_last_search_summary, format_search_brief_summary
from telegram_bot.services.texts import ABOUT_TEXT, BOTFATHER_TEXT, DEMO_TEXT, HELP_TEXT, PRIVACY_TEXT
from telegram_bot.services.validation import (
    AVAILABLE_DIRECTIONS,
    AVAILABLE_REGIONS,
    education_type_label,
    normalize_education_type,
)
from telegram_bot.states.compare_states import CompareStates
from telegram_bot.states.search_states import SearchStates
from telegram_bot.storage.feedback_data import get_user_feedback
from telegram_bot.storage.user_data import user_storage


router = Router()


@router.message(Command("menu"))
async def cmd_menu(message: Message, state: FSMContext) -> None:
    await state.clear()
    await send_menu_card(message, "main", main_menu_inline_keyboard())


@router.message(F.text.in_({"Вернуться в меню", "Главное меню", "Назад"}))
async def back_to_menu(message: Message, state: FSMContext) -> None:
    await state.clear()
    await send_menu_card(message, "main", main_menu_inline_keyboard())


@router.message(F.text == "Мои результаты")
async def results_menu(message: Message, state: FSMContext) -> None:
    await state.clear()
    await send_menu_card(message, "results", results_menu_inline_keyboard())


@router.message(F.text == "Помощник")
async def assistant_menu(message: Message, state: FSMContext) -> None:
    await state.clear()
    await send_menu_card(message, "assistant", assistant_menu_inline_keyboard())


@router.message(F.text == "Сервис")
async def service_menu(message: Message, state: FSMContext) -> None:
    await state.clear()
    await send_menu_card(message, "service", service_menu_inline_keyboard())


@router.message(F.text == "О проекте")
async def about_project_menu(message: Message, state: FSMContext) -> None:
    await state.clear()
    await send_menu_card(message, "about", about_menu_inline_keyboard())


@router.message(F.text == "Описание проекта")
async def about_project_text(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(ABOUT_TEXT, reply_markup=about_menu_inline_keyboard())


@router.message(F.text == "Демо-сценарий")
async def demo_text(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(DEMO_TEXT, reply_markup=about_menu_inline_keyboard())


@router.message(F.text == "BotFather")
async def botfather_text(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(BOTFATHER_TEXT, reply_markup=about_menu_inline_keyboard())


@router.message(F.text == "Приватность")
async def privacy_text(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(PRIVACY_TEXT, reply_markup=service_menu_inline_keyboard())


@router.message(F.text == "Что делать дальше")
async def next_text(message: Message, state: FSMContext) -> None:
    await state.clear()
    user_id = message.from_user.id if message.from_user else 0
    profile = user_storage.get_profile(user_id) if user_id else None
    results = user_storage.get_last_results(user_id) if user_id else []
    await message.answer(build_next_steps_text(profile, results), reply_markup=next_steps_inline_keyboard())


@router.callback_query(F.data == MENU_MAIN_CALLBACK)
async def main_menu_callback(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await send_menu_card(callback, "main", main_menu_inline_keyboard())


@router.callback_query(F.data == MENU_RESULTS_CALLBACK)
async def results_menu_callback(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await send_menu_card(callback, "results", results_menu_inline_keyboard())


@router.callback_query(F.data == MENU_ASSISTANT_CALLBACK)
async def assistant_menu_callback(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await send_menu_card(callback, "assistant", assistant_menu_inline_keyboard())


@router.callback_query(F.data == MENU_SERVICE_CALLBACK)
async def service_menu_callback(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await send_menu_card(callback, "service", service_menu_inline_keyboard())


@router.callback_query(F.data == MENU_ABOUT_CALLBACK)
async def about_menu_callback(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await send_menu_card(callback, "about", about_menu_inline_keyboard())


@router.callback_query(F.data == MENU_SEARCH_CALLBACK)
async def search_menu_callback(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(SearchStates.region)
    await callback.answer()
    if callback.message:
        await callback.message.answer(
            "С какого региона начнём?\n"
            "Напиши регион, например: Адыгея, Москва или Краснодарский край."
        )


@router.callback_query(F.data == MENU_WEBAPP_CALLBACK)
async def webapp_menu_callback(callback: CallbackQuery) -> None:
    await callback.answer()
    if not callback.message:
        return
    if not settings.webapp_url:
        await callback.message.answer(
            "Mini App сейчас не подключён.\n"
            "Пока можно продолжить в обычном режиме: сделай подбор через /search "
            "или открой главное меню.",
            reply_markup=main_menu_inline_keyboard(),
        )
        return

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Открыть Mini App", web_app=WebAppInfo(url=settings.webapp_url))]
        ]
    )
    await callback.message.answer("Открой Mini App Аиши:", reply_markup=keyboard)


@router.callback_query(F.data == MENU_SUMMARY_CALLBACK)
async def summary_menu_callback(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.answer()
    if callback.message:
        await _send_summary(callback.message, callback.from_user.id)


@router.callback_query(F.data == MENU_FAVORITES_CALLBACK)
async def favorites_menu_callback(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.answer()
    if callback.message:
        await _send_favorites(callback.message, callback.from_user.id)


@router.callback_query(F.data == MENU_HISTORY_CALLBACK)
async def history_menu_callback(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.answer()
    if callback.message:
        await _send_history(callback.message, callback.from_user.id)


@router.callback_query(F.data == MENU_ADVICE_CALLBACK)
async def advice_menu_callback(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.answer()
    if callback.message:
        await _send_advice(callback.message, callback.from_user.id)


@router.callback_query(F.data == MENU_FILTERS_CALLBACK)
async def filters_menu_callback(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.answer()
    if callback.message:
        await _send_filters(callback.message, callback.from_user.id)


@router.callback_query(F.data == MENU_EXPORT_CALLBACK)
async def export_menu_callback(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.answer()
    if callback.message:
        await _send_export(callback.message, callback.from_user.id)


@router.callback_query(F.data == MENU_COMPARE_CALLBACK)
async def compare_menu_callback(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.answer()
    if callback.message:
        await _send_compare(callback.message, state, callback.from_user.id)


@router.callback_query(F.data == MENU_PROFILE_CALLBACK)
async def profile_menu_callback(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.answer()
    if callback.message:
        await _send_profile(callback.message, callback.from_user.id)


@router.callback_query(F.data == MENU_FEEDBACK_CALLBACK)
async def feedback_menu_callback(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.answer()
    if callback.message:
        await callback.message.answer(
            "Выбери тип обращения.\n\n"
            "Если тебе тревожно из-за поступления, используй /support. "
            "Если заметил ошибку в сервисе, подборе или Mini App, используй /feedback.",
            reply_markup=feedback_categories_keyboard(),
        )


@router.callback_query(F.data == MENU_MY_FEEDBACK_CALLBACK)
async def my_feedback_menu_callback(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.answer()
    if callback.message:
        await _send_my_feedback(callback.message, callback.from_user.id)


@router.callback_query(F.data == MENU_PRIVACY_CALLBACK)
async def privacy_menu_callback(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.answer()
    if callback.message:
        await callback.message.answer(PRIVACY_TEXT, reply_markup=service_menu_inline_keyboard())


@router.callback_query(F.data == MENU_RESET_CALLBACK)
async def reset_menu_callback(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.answer("Данные сброшены.")
    user_storage.reset_profile(callback.from_user.id)
    if callback.message:
        await callback.message.answer(
            "Профиль, последний подбор, история и избранное очищены.",
            reply_markup=main_menu_inline_keyboard(),
        )


@router.callback_query(F.data == MENU_NEXT_CALLBACK)
async def next_menu_callback(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.answer()
    if callback.message:
        profile = user_storage.get_profile(callback.from_user.id)
        results = user_storage.get_last_results(callback.from_user.id)
        await callback.message.answer(
            build_next_steps_text(profile, results),
            reply_markup=next_steps_inline_keyboard(),
        )


@router.callback_query(F.data == MENU_SUPPORT_CALLBACK)
async def support_menu_callback(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.answer()
    if callback.message:
        await callback.message.answer(
            "Я рядом. Поступление правда может давить: баллы, выбор, ожидания родителей, страх ошибиться.\n"
            "Выбери, что ближе к твоей ситуации:",
            reply_markup=support_keyboard(),
        )


@router.callback_query(F.data == MENU_CATEGORIES_CALLBACK)
async def categories_menu_callback(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.answer()
    if callback.message:
        await callback.message.answer(format_categories_explanation(), reply_markup=assistant_menu_inline_keyboard())


@router.callback_query(F.data == MENU_ACHIEVEMENTS_CALLBACK)
async def achievements_menu_callback(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.answer()
    if callback.message:
        await _send_achievements_list(callback.message, assistant_menu_inline_keyboard())


@router.callback_query(F.data == MENU_DIRECTIONS_CALLBACK)
async def directions_menu_callback(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.answer()
    if callback.message:
        await _send_directions_list(callback.message, assistant_menu_inline_keyboard())


@router.callback_query(F.data == MENU_REGIONS_CALLBACK)
async def regions_menu_callback(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.answer()
    if callback.message:
        await _send_regions_list(callback.message, assistant_menu_inline_keyboard())


@router.callback_query(F.data == MENU_ABOUT_TEXT_CALLBACK)
async def about_text_menu_callback(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.answer()
    if callback.message:
        await callback.message.answer(ABOUT_TEXT, reply_markup=about_menu_inline_keyboard())


@router.callback_query(F.data == MENU_DEMO_CALLBACK)
async def demo_menu_callback(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.answer()
    if callback.message:
        await callback.message.answer(DEMO_TEXT, reply_markup=about_menu_inline_keyboard())


@router.callback_query(F.data == MENU_BOTFATHER_CALLBACK)
async def botfather_menu_callback(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.answer()
    if callback.message:
        await callback.message.answer(BOTFATHER_TEXT, reply_markup=about_menu_inline_keyboard())


@router.message(F.text == "Мои баллы")
@router.message(F.text == "Мой профиль")
async def my_profile(message: Message, state: FSMContext) -> None:
    await state.clear()
    if not message.from_user:
        await message.answer("Не удалось определить пользователя.", reply_markup=profile_keyboard())
        return

    await _send_profile(message, message.from_user.id)


@router.message(Command("summary"))
@router.message(F.text == "Итог подбора")
async def search_summary(message: Message, state: FSMContext) -> None:
    await state.clear()
    if not message.from_user:
        await message.answer("Не удалось определить пользователя.", reply_markup=main_menu_keyboard())
        return

    await _send_summary(message, message.from_user.id)


@router.message(Command("advice"))
@router.message(F.text == "Советы по подбору")
async def search_advice(message: Message, state: FSMContext) -> None:
    await state.clear()
    if not message.from_user:
        await message.answer("Не удалось определить пользователя.", reply_markup=main_menu_keyboard())
        return

    await _send_advice(message, message.from_user.id)


@router.message(Command("history"))
@router.message(F.text == "История подборов")
async def search_history(message: Message, state: FSMContext) -> None:
    await state.clear()
    if not message.from_user:
        await message.answer("Не удалось определить пользователя.", reply_markup=main_menu_keyboard())
        return

    await _send_history(message, message.from_user.id)


@router.message(Command("clear_history"))
@router.message(F.text == "Очистить историю")
async def clear_search_history(message: Message, state: FSMContext) -> None:
    await state.clear()
    if message.from_user:
        user_storage.clear_search_history(message.from_user.id)
    await message.answer("История подборов очищена.", reply_markup=empty_history_keyboard())


@router.message(F.text == "Повторить последний подбор")
async def repeat_last_search(message: Message, state: FSMContext) -> None:
    await state.clear()
    if not message.from_user:
        await message.answer("Не удалось определить пользователя.", reply_markup=main_menu_keyboard())
        return

    history = user_storage.get_search_history(message.from_user.id, limit=1)
    if not history:
        await message.answer(format_history_message([]), reply_markup=empty_history_keyboard())
        return

    profile = _profile_from_history_entry(message.from_user.id, history[0])
    if not profile:
        await message.answer(
            "Не получилось повторить последний подбор: в истории не хватает данных. "
            "Лучше запусти новый подбор через /search.",
            reply_markup=empty_history_keyboard(),
        )
        return

    await message.answer("Повторяю последний подбор...")

    try:
        results = await fetch_universities(
            base_url=settings.backend_base_url,
            region=profile["region"],
            score=profile["score"],
            direction=profile["direction"],
            education_type=profile["education_type"],
            limit=5,
        )
    except UniversityAPIError:
        await message.answer(
            "Сейчас не получилось повторить подбор. Попробуй позже или начни новый поиск.",
            reply_markup=history_keyboard(),
        )
        return

    groups = group_universities_by_recommendation(profile["score"], results)
    display_results = visible_recommendations(groups)
    user_storage.save_search(message.from_user.id, profile, display_results)
    user_storage.add_search_history(message.from_user.id, profile, display_results)

    if not display_results:
        await message.answer(
            "В обычной выдаче нет подходящих вузов по этим фильтрам.\n\n"
            "Можно попробовать:\n"
            "- выбрать соседний регион;\n"
            "- изменить финансирование;\n"
            "- убрать фильтр конкурса;\n"
            "- изменить направление;\n"
            "- проверить баллы.",
            reply_markup=no_results_keyboard(),
        )
        return

    cards = "\n\n".join(
        format_university_card(index, item, profile["score"])
        for index, item in enumerate(display_results, start=1)
    )
    summary = format_search_brief_summary(display_results, profile["score"])
    await message.answer(
        "Повторила последний подбор:\n"
        f"Регион: {escape(profile['region'])}\n"
        f"Баллы: {profile['score']}\n"
        f"Направление: {escape(profile['direction'])}\n"
        f"Финансирование: {education_type_label(profile['education_type'])}\n\n"
        f"{cards}\n\n"
        f"{summary}\n\n"
        "Источник данных определяется подключённой базой. Проверь условия на официальных сайтах вузов.",
        reply_markup=search_results_keyboard(len(display_results)),
    )


@router.message(F.text.in_({"Сбросить профиль", "Сбросить данные"}))
async def reset_profile_button(message: Message, state: FSMContext) -> None:
    await state.clear()
    if message.from_user:
        user_storage.reset_profile(message.from_user.id)
    await message.answer("Профиль, последний подбор, история и избранное очищены.", reply_markup=main_menu_keyboard())


@router.message(F.text == "Избранные вузы")
async def favorites(message: Message, state: FSMContext) -> None:
    await state.clear()
    if not message.from_user:
        await message.answer("Не удалось определить пользователя.", reply_markup=main_menu_keyboard())
        return

    await _send_favorites(message, message.from_user.id)


async def _send_profile(message: Message, telegram_id: int) -> None:
    summary = user_storage.get_profile_summary(telegram_id)
    if summary["is_empty"]:
        await message.answer(
            "Пока профиль пустой. Нажми «Подобрать вуз», и я сохраню данные во время подбора.",
            reply_markup=profile_keyboard(),
        )
        return

    text = (
        "<b>Мой профиль</b>\n\n"
        f"Telegram ID: {summary['telegram_id']}\n"
        f"Регион: {_value(summary.get('region'))}\n"
        f"Баллы: {_value(summary.get('score'))}\n"
        f"Направление: {_value(summary.get('direction'))}\n"
        f"Финансирование: {education_type_label(str(summary.get('education_type') or ''))}\n"
        f"Последний подбор: {summary['last_results_count']} {_plural(summary['last_results_count'], 'вариант', 'варианта', 'вариантов')}\n"
        f"Избранное: {summary['favorites_count']} {_plural(summary['favorites_count'], 'вуз', 'вуза', 'вузов')}"
    )
    await message.answer(text, reply_markup=profile_keyboard())


async def _send_summary(message: Message, telegram_id: int) -> None:
    profile = user_storage.get_profile(telegram_id)
    last_results = user_storage.get_last_results(telegram_id)
    favorites_count = len(user_storage.get_favorites(telegram_id))
    text = format_last_search_summary(profile, last_results, favorites_count)
    reply_markup = summary_keyboard() if text != EMPTY_SUMMARY_TEXT else main_menu_keyboard()
    await message.answer(text, reply_markup=reply_markup)


async def _send_advice(message: Message, telegram_id: int) -> None:
    profile = user_storage.get_profile(telegram_id)
    last_results = user_storage.get_last_results(telegram_id)
    favorites = user_storage.get_favorites(telegram_id)
    text = build_advice(profile, last_results, favorites)
    reply_markup = advice_keyboard(has_results=bool(last_results)) if has_advice_context(profile) else empty_advice_keyboard()
    await message.answer(text, reply_markup=reply_markup)


async def _send_history(message: Message, telegram_id: int) -> None:
    history = user_storage.get_search_history(telegram_id)
    reply_markup = history_keyboard() if history else empty_history_keyboard()
    await message.answer(format_history_message(history), reply_markup=reply_markup)


async def _send_favorites(message: Message, telegram_id: int) -> None:
    items = user_storage.get_favorites(telegram_id)
    if not items:
        await message.answer(
            "Избранное пока пустое.\n"
            "Сначала пройди подбор и нажми «Сохранить 1», «Сохранить 2» и т.д.",
            reply_markup=empty_favorites_keyboard(),
        )
        return

    cards = "\n\n".join(_format_favorite_card(index, item) for index, item in enumerate(items, start=1))
    await message.answer(cards, reply_markup=favorites_keyboard_for_count(len(items)))


async def _send_filters(message: Message, telegram_id: int) -> None:
    profile = user_storage.get_profile(telegram_id)
    last_results = user_storage.get_last_results(telegram_id)
    if not last_results:
        await message.answer(EMPTY_FILTERS_TEXT, reply_markup=empty_filters_keyboard())
        return

    counts = get_filter_counts(last_results, _profile_score(profile))
    await message.answer(
        build_filters_overview_message(profile, last_results),
        reply_markup=filters_keyboard(counts),
    )


async def _send_export(message: Message, telegram_id: int) -> None:
    profile = user_storage.get_profile(telegram_id)
    results = user_storage.get_last_results(telegram_id)
    favorites = user_storage.get_favorites(telegram_id)
    if not results:
        await message.answer(
            "Пока нет результата для экспорта.\n"
            "Сначала сделай подбор через /search.",
            reply_markup=empty_export_keyboard(),
        )
        return

    await message.answer(build_export_preview(profile, results, favorites), reply_markup=export_menu_keyboard())


async def _send_compare(message: Message, state: FSMContext, telegram_id: int) -> None:
    last_results = user_storage.get_last_results(telegram_id)
    favorites = user_storage.get_favorites(telegram_id)

    has_last_results = bool(last_results)
    has_favorites = bool(favorites)

    if not has_last_results and not has_favorites:
        await message.answer(
            "Пока нечего сравнивать.\n"
            "Сначала пройди подбор вузов или добавь варианты в избранное.",
            reply_markup=empty_compare_keyboard(),
        )
        return

    if has_last_results and has_favorites:
        await message.answer(
            "Что сравним?",
            reply_markup=compare_source_keyboard(has_last_results=True, has_favorites=True),
        )
        return

    source = "last_results" if has_last_results else "favorites"
    items = last_results if has_last_results else favorites
    await _send_compare_options(message, state, source, items)


async def _send_compare_options(
    message: Message,
    state: FSMContext,
    source: str,
    items: list[dict],
) -> None:
    if len(items) < 2:
        await state.clear()
        if source == "favorites":
            await message.answer(
                "Для сравнения нужно минимум два избранных вуза. "
                "Сначала сохрани несколько вариантов после подбора.",
                reply_markup=not_enough_favorites_keyboard(),
            )
        else:
            await message.answer(
                "Для сравнения нужно минимум два варианта. "
                "Пройди подбор ещё раз или сохрани несколько вузов в избранное.",
                reply_markup=empty_compare_keyboard(),
            )
        return

    await state.set_state(CompareStates.choosing_items)
    await state.update_data(compare_source=source)
    source_title = "последних результатов" if source == "last_results" else "избранных вузов"
    scope_hint = " Можно сравнить первые 3 варианта из текущей выдачи." if len(items) > 3 else ""
    await message.answer(
        f"Выбери, какие варианты из {source_title} сравнить. Сейчас доступно: {len(items)}.{scope_hint}",
        reply_markup=compare_options_keyboard(len(items)),
    )


async def _send_my_feedback(message: Message, telegram_id: int) -> None:
    tickets = get_user_feedback(telegram_id, limit=5)
    reply_markup = feedback_created_keyboard() if tickets else empty_feedback_keyboard()
    await message.answer(format_user_feedback(tickets), reply_markup=reply_markup)


@router.message(F.text == "Очистить избранное")
async def clear_favorites(message: Message, state: FSMContext) -> None:
    await state.clear()
    if message.from_user:
        user_storage.clear_favorites(message.from_user.id)
    await message.answer("Избранное очищено.", reply_markup=empty_favorites_keyboard())


@router.message(F.text.regexp(r"^Удалить\s+\d+$"))
async def remove_favorite(message: Message, state: FSMContext) -> None:
    await state.clear()
    if not message.from_user:
        await message.answer("Не удалось определить пользователя.", reply_markup=main_menu_keyboard())
        return

    text = message.text or ""
    try:
        index = int(text.split()[-1]) - 1
    except (ValueError, IndexError):
        favorites_count = len(user_storage.get_favorites(message.from_user.id))
        await message.answer("Не нашла такой номер в избранном.", reply_markup=_favorites_reply_keyboard(favorites_count))
        return

    removed = user_storage.remove_favorite(message.from_user.id, index)
    if not removed:
        favorites_count = len(user_storage.get_favorites(message.from_user.id))
        await message.answer("Не нашла такой номер в избранном.", reply_markup=_favorites_reply_keyboard(favorites_count))
        return

    remaining_count = len(user_storage.get_favorites(message.from_user.id))
    reply_markup = _favorites_reply_keyboard(remaining_count)
    suffix = "" if remaining_count else (
        "\n\nИзбранное пока пустое. Сначала пройди подбор и нажми «Сохранить 1», «Сохранить 2» и т.д."
    )

    await message.answer(
        f"Удалил из избранного: {escape(str(removed.get('university', 'Вуз')))} — "
        f"{escape(str(removed.get('program', 'программа')))}"
        f"{suffix}",
        reply_markup=reply_markup,
    )


@router.message(F.text == "Направления")
async def directions(message: Message, state: FSMContext) -> None:
    await state.clear()
    await _send_directions_list(message, main_menu_keyboard())


@router.message(F.text == "Регионы")
async def regions(message: Message, state: FSMContext) -> None:
    await state.clear()
    await _send_regions_list(message, main_menu_keyboard())


@router.message(Command("achievements"))
@router.message(F.text == "Индивидуальные достижения")
async def achievements(message: Message, state: FSMContext) -> None:
    await state.clear()
    await _send_achievements_list(message, main_menu_keyboard())


async def _send_directions_list(message: Message, reply_markup) -> None:
    items, is_fallback = await _load_directory_items("/api/directions", list(AVAILABLE_DIRECTIONS), limit=20)
    suffix = (
        "\n\nПоказываю базовый список, сервис данных сейчас недоступен."
        if is_fallback
        else "\n\nСписок взят из базы. Можно также написать близкое название направления своими словами."
    )
    await message.answer(
        "Сейчас доступны направления. Можешь использовать одно из них в подборе:\n"
        + "\n".join(f"- {item}" for item in items)
        + suffix,
        reply_markup=reply_markup,
    )


async def _send_regions_list(message: Message, reply_markup) -> None:
    items, is_fallback = await _load_directory_items("/api/regions", list(AVAILABLE_REGIONS), limit=20)
    prefix = (
        "Показываю базовый список регионов, сервис данных сейчас недоступен:\n"
        if is_fallback
        else "Сейчас доступны регионы из базы. Для проверки можно использовать:\n"
    )
    await message.answer(
        prefix
        + "\n".join(f"- {item}" for item in items),
        reply_markup=reply_markup,
    )


async def _send_achievements_list(message: Message, reply_markup) -> None:
    try:
        items = await fetch_achievements(settings.backend_base_url, limit=8)
        is_fallback = False
    except UniversityAPIError:
        items = []
        is_fallback = True

    if items:
        lines = [
            "<b>Индивидуальные достижения</b>",
            "",
            "Это общий справочник. Точные баллы нужно проверять в правилах конкретного вуза.",
            "",
        ]
        for item in items:
            title = escape(str(item.get("title") or "Достижение"))
            points = escape(str(item.get("points") or ""))
            category = escape(str(item.get("category") or ""))
            description = escape(str(item.get("description") or ""))
            meta = " · ".join(part for part in (category, f"до {points} баллов" if points else "") if part)
            lines.append(f"• <b>{title}</b>{f' — {meta}' if meta else ''}")
            if description:
                lines.append(f"  {description}")
        await message.answer("\n".join(lines), reply_markup=reply_markup)
        return

    fallback_text = (
        "<b>Индивидуальные достижения</b>\n\n"
        "Проверь в правилах выбранного вуза: аттестат с отличием, олимпиады, ГТО, "
        "волонтёрство и итоговое сочинение могут дать дополнительные баллы. "
        "Точные условия различаются по вузам."
    )
    if is_fallback:
        fallback_text += "\n\nПоказываю базовую подсказку, сервис данных сейчас недоступен."
    await message.answer(fallback_text, reply_markup=reply_markup)


async def _load_directory_items(endpoint: str, fallback: list[str], limit: int) -> tuple[list[str], bool]:
    try:
        items = await fetch_directory_items(settings.backend_base_url, endpoint, limit=limit)
    except UniversityAPIError:
        return fallback[:limit], True
    return (items or fallback[:limit]), not bool(items)


@router.message(F.text == "Помощь")
async def help_button(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(HELP_TEXT, reply_markup=main_menu_keyboard())


@router.message(Command("categories"))
@router.message(F.text == "Как читать категории")
async def categories_explanation(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(format_categories_explanation(), reply_markup=main_menu_keyboard())


def _format_favorite_card(index: int, item: dict) -> str:
    return format_university_card(index, item, icon="⭐", include_note=False)


def _main_menu_text() -> str:
    return (
        "Главное меню Аиши. Выбери раздел:\n\n"
        "Подобрать вуз — начать новый подбор.\n"
        "Mini App — открыть расширенное приложение.\n"
        "Мои результаты — итог, избранное, история, сравнение и экспорт.\n"
        "Помощник — советы, категории и поддержка.\n"
        "Сервис — профиль, обратная связь и приватность.\n"
        "О проекте — описание, демо и BotFather."
    )


def _value(value: object) -> str:
    if value is None or value == "":
        return "не указано"
    return escape(str(value))


def _text_value(value: object) -> str:
    if value is None or value == "":
        return "не указано"
    return str(value)


def _favorites_reply_keyboard(items_count: int):
    return favorites_keyboard_for_count(items_count) if items_count else empty_favorites_keyboard()


def _profile_from_history_entry(telegram_id: int, entry: dict) -> dict | None:
    region = _clean_history_value(entry.get("region"))
    direction = _clean_history_value(entry.get("direction"))
    score = _history_score(entry.get("score"))
    education_type = normalize_education_type(str(entry.get("type") or ""))

    if not region or not direction or score is None or not education_type:
        return None

    return {
        "telegram_id": telegram_id,
        "region": region,
        "score": score,
        "direction": direction,
        "education_type": education_type,
    }


def _clean_history_value(value: object) -> str | None:
    text = str(value or "").strip()
    if not text or text == "не указано":
        return None
    return text


def _history_score(value: object) -> int | None:
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.strip().isdigit():
        return int(value.strip())
    return None


def _profile_score(profile: dict | None) -> int | None:
    if not isinstance(profile, dict):
        return None
    score = profile.get("score")
    if isinstance(score, int):
        return score
    if isinstance(score, str) and score.strip().isdigit():
        return int(score.strip())
    return None


def _plural(count: int, one: str, few: str, many: str) -> str:
    if count % 10 == 1 and count % 100 != 11:
        return one
    if 2 <= count % 10 <= 4 and not 12 <= count % 100 <= 14:
        return few
    return many
