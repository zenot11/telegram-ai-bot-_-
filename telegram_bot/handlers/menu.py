from html import escape

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from telegram_bot.config import settings
from telegram_bot.keyboards.menu import (
    empty_favorites_keyboard,
    empty_history_keyboard,
    favorites_keyboard_for_count,
    history_keyboard,
    main_menu_keyboard,
    profile_keyboard,
    summary_keyboard,
)
from telegram_bot.keyboards.search import no_results_keyboard, search_results_keyboard
from telegram_bot.services.api import UniversityAPIError, fetch_universities
from telegram_bot.services.formatters import format_university_card
from telegram_bot.services.history import format_history_message
from telegram_bot.services.recommendation import (
    format_categories_explanation,
    group_universities_by_recommendation,
    visible_recommendations,
)
from telegram_bot.services.summary import EMPTY_SUMMARY_TEXT, format_last_search_summary, format_search_brief_summary
from telegram_bot.services.texts import HELP_TEXT
from telegram_bot.services.validation import (
    AVAILABLE_DIRECTIONS,
    AVAILABLE_REGIONS,
    education_type_label,
    normalize_education_type,
)
from telegram_bot.storage.user_data import user_storage


router = Router()


@router.message(Command("menu"))
async def cmd_menu(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Главное меню. Выбери, с чего начнём:", reply_markup=main_menu_keyboard())


@router.message(F.text == "Вернуться в меню")
async def back_to_menu(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Главное меню. Выбери, с чего начнём:", reply_markup=main_menu_keyboard())


@router.message(F.text == "Мои баллы")
@router.message(F.text == "Мой профиль")
async def my_profile(message: Message, state: FSMContext) -> None:
    await state.clear()
    if not message.from_user:
        await message.answer("Не удалось определить пользователя.", reply_markup=profile_keyboard())
        return

    summary = user_storage.get_profile_summary(message.from_user.id)
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
        f"Тип обучения: {education_type_label(str(summary.get('education_type') or ''))}\n"
        f"Последний подбор: {summary['last_results_count']} {_plural(summary['last_results_count'], 'вариант', 'варианта', 'вариантов')}\n"
        f"Избранное: {summary['favorites_count']} {_plural(summary['favorites_count'], 'вуз', 'вуза', 'вузов')}"
    )
    await message.answer(text, reply_markup=profile_keyboard())


@router.message(Command("summary"))
@router.message(F.text == "Итог подбора")
async def search_summary(message: Message, state: FSMContext) -> None:
    await state.clear()
    if not message.from_user:
        await message.answer("Не удалось определить пользователя.", reply_markup=main_menu_keyboard())
        return

    profile = user_storage.get_profile(message.from_user.id)
    last_results = user_storage.get_last_results(message.from_user.id)
    favorites_count = len(user_storage.get_favorites(message.from_user.id))
    text = format_last_search_summary(profile, last_results, favorites_count)
    reply_markup = summary_keyboard() if text != EMPTY_SUMMARY_TEXT else main_menu_keyboard()
    await message.answer(text, reply_markup=reply_markup)


@router.message(Command("history"))
@router.message(F.text == "История подборов")
async def search_history(message: Message, state: FSMContext) -> None:
    await state.clear()
    if not message.from_user:
        await message.answer("Не удалось определить пользователя.", reply_markup=main_menu_keyboard())
        return

    history = user_storage.get_search_history(message.from_user.id)
    reply_markup = history_keyboard() if history else empty_history_keyboard()
    await message.answer(format_history_message(history), reply_markup=reply_markup)


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
            "Сейчас не получилось повторить подбор. Проверь, что backend-заглушка запущена.",
            reply_markup=history_keyboard(),
        )
        return

    groups = group_universities_by_recommendation(profile["score"], results)
    display_results = visible_recommendations(groups)
    user_storage.save_search(message.from_user.id, profile, display_results)
    user_storage.add_search_history(message.from_user.id, profile, display_results)

    if not display_results:
        await message.answer(
            "Пока не нашла подходящих вариантов по этим параметрам.\n\n"
            "Можно попробовать:\n"
            "- выбрать соседний регион;\n"
            "- рассмотреть платное обучение;\n"
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
        f"Тип: {education_type_label(profile['education_type'])}\n\n"
        f"{cards}\n\n"
        f"{summary}\n\n"
        "Сейчас используются демонстрационные данные.",
        reply_markup=search_results_keyboard(len(display_results)),
    )


@router.message(F.text == "Сбросить профиль")
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

    items = user_storage.get_favorites(message.from_user.id)
    if not items:
        await message.answer(
            "Избранное пока пустое.\n"
            "Сначала пройди подбор и нажми «Сохранить 1», «Сохранить 2» и т.д.",
            reply_markup=empty_favorites_keyboard(),
        )
        return

    cards = "\n\n".join(_format_favorite_card(index, item) for index, item in enumerate(items, start=1))
    await message.answer(cards, reply_markup=favorites_keyboard_for_count(len(items)))


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
    await message.answer(
        "Сейчас в демонстрационной базе доступны направления. Можешь использовать одно из них в подборе:\n"
        + "\n".join(f"- {direction}" for direction in AVAILABLE_DIRECTIONS),
        reply_markup=main_menu_keyboard(),
    )


@router.message(F.text == "Регионы")
async def regions(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "Сейчас в демонстрационной базе доступны регионы. Для проверки можно использовать:\n"
        + "\n".join(f"- {region}" for region in AVAILABLE_REGIONS),
        reply_markup=main_menu_keyboard(),
    )


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


def _plural(count: int, one: str, few: str, many: str) -> str:
    if count % 10 == 1 and count % 100 != 11:
        return one
    if 2 <= count % 10 <= 4 and not 12 <= count % 100 <= 14:
        return few
    return many
