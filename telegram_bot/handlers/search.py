from html import escape

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from telegram_bot.config import settings
from telegram_bot.keyboards.menu import main_menu_keyboard
from telegram_bot.keyboards.search import education_type_keyboard
from telegram_bot.services.ai import ai_service
from telegram_bot.services.api import UniversityAPIError, fetch_universities
from telegram_bot.services.safety import CRISIS_RESPONSE, is_crisis_message
from telegram_bot.services.validation import (
    education_type_label,
    normalize_education_type,
    parse_score,
)
from telegram_bot.states.search_states import SearchStates
from telegram_bot.storage.user_data import user_storage


router = Router()


@router.message(Command("search"))
@router.message(F.text.in_({"Подобрать вуз", "Подобрать 3 варианта"}))
async def start_search(message: Message, state: FSMContext) -> None:
    await state.set_state(SearchStates.region)
    await message.answer(
        "С какого региона начнём? Напиши регион, например: Адыгея, Москва или Краснодарский край."
    )


@router.message(SearchStates.region)
async def search_region(message: Message, state: FSMContext) -> None:
    text = (message.text or "").strip()
    if is_crisis_message(text):
        await state.clear()
        await message.answer(CRISIS_RESPONSE, reply_markup=main_menu_keyboard())
        return

    if not text:
        await message.answer("Напиши регион текстом, например: Адыгея.")
        return

    await state.update_data(region=text)
    await state.set_state(SearchStates.score)
    await message.answer("Теперь введи суммарные баллы ЕГЭ числом, например: 230.")


@router.message(SearchStates.score)
async def search_score(message: Message, state: FSMContext) -> None:
    text = (message.text or "").strip()
    if is_crisis_message(text):
        await state.clear()
        await message.answer(CRISIS_RESPONSE, reply_markup=main_menu_keyboard())
        return

    score, error = parse_score(text)
    if error:
        await message.answer(error)
        return

    await state.update_data(score=score)
    await state.set_state(SearchStates.direction)
    await message.answer("Какое направление интересно? Например: IT, психология, медицина, экономика.")


@router.message(SearchStates.direction)
async def search_direction(message: Message, state: FSMContext) -> None:
    text = (message.text or "").strip()
    if is_crisis_message(text):
        await state.clear()
        await message.answer(CRISIS_RESPONSE, reply_markup=main_menu_keyboard())
        return

    if not text:
        await message.answer("Напиши направление текстом, например: IT.")
        return

    await state.update_data(direction=text)
    await state.set_state(SearchStates.education_type)
    await message.answer("Какой тип обучения рассматриваешь?", reply_markup=education_type_keyboard())


@router.message(SearchStates.education_type)
async def search_education_type(message: Message, state: FSMContext) -> None:
    text = (message.text or "").strip()
    if is_crisis_message(text):
        await state.clear()
        await message.answer(CRISIS_RESPONSE, reply_markup=main_menu_keyboard())
        return

    education_type = normalize_education_type(text)
    if not education_type:
        await message.answer("Выбери «Бюджет» или «Платное».", reply_markup=education_type_keyboard())
        return

    data = await state.get_data()
    profile = {
        "telegram_id": message.from_user.id if message.from_user else None,
        "region": data["region"],
        "score": data["score"],
        "direction": data["direction"],
        "education_type": education_type,
    }

    await message.answer("Ищу подходящие варианты...")

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
        await state.clear()
        await message.answer(
            "Сейчас не получилось получить список вузов. Проверь, что backend-заглушка запущена.",
            reply_markup=main_menu_keyboard(),
        )
        return

    if message.from_user:
        user_storage.save_search(message.from_user.id, profile, results)

    await state.clear()

    if not results:
        await message.answer(
            "По этим параметрам в тестовой базе ничего не нашлось. Попробуй другой регион, "
            "направление или тип обучения.",
            reply_markup=main_menu_keyboard(),
        )
        return

    cards = "\n\n".join(_format_university_card(i, item) for i, item in enumerate(results, start=1))
    await message.answer(
        f"Нашла варианты по запросу:\n"
        f"Регион: {escape(profile['region'])}\n"
        f"Баллы: {profile['score']}\n"
        f"Направление: {escape(profile['direction'])}\n"
        f"Тип: {education_type_label(profile['education_type'])}\n\n"
        f"{cards}",
        reply_markup=main_menu_keyboard(),
    )

    explanation = await ai_service.explain_universities(profile, results)
    if explanation:
        await message.answer(explanation, reply_markup=main_menu_keyboard())


def _format_university_card(index: int, item: dict) -> str:
    subjects = ", ".join(item.get("subjects") or []) or "не указаны"
    price = item.get("price")
    price_line = ""
    if price:
        price_line = f"\nСтоимость: {int(price):,} руб./год".replace(",", " ")

    return (
        f"<b>{index}. {escape(str(item.get('university', 'Вуз')))}</b>\n"
        f"Город: {escape(str(item.get('city', 'не указан')))}\n"
        f"Программа: {escape(str(item.get('program', 'не указана')))}\n"
        f"Предметы: {escape(subjects)}\n"
        f"Мин. балл: {escape(str(item.get('min_score', 'не указан')))}\n"
        f"Тип: {escape(str(item.get('type', 'не указан')))}"
        f"{price_line}\n"
        f"Сайт: {escape(str(item.get('url', 'не указан')))}"
    )
