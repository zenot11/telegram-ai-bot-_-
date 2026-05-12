from html import escape

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from telegram_bot.handlers.start import HELP_TEXT
from telegram_bot.keyboards.menu import (
    empty_favorites_keyboard,
    favorites_keyboard_for_count,
    main_menu_keyboard,
    profile_keyboard,
)
from telegram_bot.services.recommendation import format_categories_explanation
from telegram_bot.services.validation import (
    AVAILABLE_DIRECTIONS,
    AVAILABLE_REGIONS,
    education_type_label,
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


@router.message(F.text == "Сбросить профиль")
async def reset_profile_button(message: Message, state: FSMContext) -> None:
    await state.clear()
    if message.from_user:
        user_storage.reset_profile(message.from_user.id)
    await message.answer("Профиль и избранное очищены.", reply_markup=main_menu_keyboard())


@router.message(F.text == "Избранные вузы")
async def favorites(message: Message, state: FSMContext) -> None:
    await state.clear()
    if not message.from_user:
        await message.answer("Не удалось определить пользователя.", reply_markup=main_menu_keyboard())
        return

    items = user_storage.get_favorites(message.from_user.id)
    if not items:
        await message.answer(
            "Пока избранных вузов нет. После подбора нажми «Сохранить N» рядом с понравившимся вариантом.",
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
        "\n\nПока избранных вузов нет. После подбора нажми «Сохранить N» рядом с понравившимся вариантом."
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
        "Сейчас в MVP доступны тестовые направления. Можешь использовать одно из них в подборе:\n"
        + "\n".join(f"- {direction}" for direction in AVAILABLE_DIRECTIONS),
        reply_markup=main_menu_keyboard(),
    )


@router.message(F.text == "Регионы")
async def regions(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "Сейчас в MVP доступны тестовые регионы. Для проверки лучше использовать:\n"
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
    lines = [
        f"⭐ <b>{index}. {escape(str(item.get('university', 'Вуз')))}</b>\n"
        f"Город: {escape(_text_value(item.get('city')))}\n"
        f"Программа: {escape(_text_value(item.get('program')))}\n"
        f"Мин. балл: {escape(_text_value(item.get('min_score')))}\n"
        f"Тип: {escape(_text_value(item.get('type')))}"
    ]
    if item.get("study_form"):
        lines.append(f"Форма: {escape(str(item['study_form']))}")
    if item.get("duration"):
        lines.append(f"Срок: {escape(str(item['duration']))}")
    if item.get("url"):
        lines.append(f"Сайт: {escape(str(item['url']))}")
    return "\n".join(lines)


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


def _plural(count: int, one: str, few: str, many: str) -> str:
    if count % 10 == 1 and count % 100 != 11:
        return one
    if 2 <= count % 10 <= 4 and not 12 <= count % 100 <= 14:
        return few
    return many
