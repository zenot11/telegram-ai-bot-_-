from html import escape

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from telegram_bot.config import settings
from telegram_bot.keyboards.menu import main_menu_keyboard
from telegram_bot.keyboards.search import education_type_keyboard, no_results_keyboard, search_results_keyboard
from telegram_bot.services.ai import explain_recommendation_groups, explain_results
from telegram_bot.services.api import UniversityAPIError, fetch_universities
from telegram_bot.services.recommendation import (
    classify_university,
    format_recommendation_summary,
    format_score_delta,
    get_recommendation_label,
    group_universities_by_recommendation,
    visible_recommendations,
)
from telegram_bot.services.safety import CRISIS_RESPONSE, is_crisis_message
from telegram_bot.services.validation import (
    education_type_label,
    normalize_direction,
    normalize_education_type,
    normalize_region,
    parse_score,
)
from telegram_bot.states.search_states import SearchStates
from telegram_bot.storage.user_data import user_storage


router = Router()


@router.message(Command("search"))
@router.message(F.text.in_({"Подобрать вуз", "Подобрать 3 варианта", "Подобрать ещё", "Новый подбор"}))
async def start_search(message: Message, state: FSMContext) -> None:
    await state.set_state(SearchStates.region)
    await message.answer(
        "С какого региона начнём?\n"
        "Напиши регион, например: Адыгея, Москва или Краснодарский край."
    )


@router.message(SearchStates.region)
async def search_region(message: Message, state: FSMContext) -> None:
    text = (message.text or "").strip()
    if is_crisis_message(text):
        await state.clear()
        await message.answer(CRISIS_RESPONSE, reply_markup=main_menu_keyboard())
        return

    if len(text) < 2:
        await message.answer("Напиши регион текстом, например: Адыгея.")
        return

    region = normalize_region(text)
    await state.update_data(region=region)
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

    direction = normalize_direction(text)
    await state.update_data(direction=direction)
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
        await message.answer("Выбери тип обучения: бюджет или платное.", reply_markup=education_type_keyboard())
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

    groups = group_universities_by_recommendation(profile["score"], results)
    display_results = visible_recommendations(groups)

    if message.from_user:
        user_storage.save_search(message.from_user.id, profile, display_results)

    await state.clear()

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
        _format_university_card(i, item, profile["score"])
        for i, item in enumerate(display_results, start=1)
    )
    summary = format_recommendation_summary(groups)
    await message.answer(
        f"Нашла варианты по запросу:\n"
        f"Регион: {escape(profile['region'])}\n"
        f"Баллы: {profile['score']}\n"
        f"Направление: {escape(profile['direction'])}\n"
        f"Тип: {education_type_label(profile['education_type'])}\n\n"
        f"{cards}\n\n"
        f"{summary}\n\n"
        "Сейчас используются демонстрационные данные. Финальную базу вузов можно подставить "
        "перед сдачей без переписывания логики подбора.",
        reply_markup=search_results_keyboard(len(display_results)),
    )

    explanation = await explain_recommendation_groups(profile, groups)
    if not explanation:
        explanation = await explain_results(profile, display_results)
    if explanation:
        await message.answer(explanation, reply_markup=search_results_keyboard(len(display_results)))


@router.message(F.text.regexp(r"^Сохранить\s+\d+$"))
async def save_result_to_favorites(message: Message) -> None:
    if not message.from_user:
        await message.answer("Не удалось определить пользователя.", reply_markup=main_menu_keyboard())
        return

    text = message.text or ""
    try:
        result_number = int(text.split()[-1])
    except (ValueError, IndexError):
        await message.answer("Такого варианта сейчас нет. Попробуй выбрать другой номер.")
        return

    last_results = user_storage.get_last_results(message.from_user.id)
    item = _get_result_by_number(last_results, result_number)
    if item is None:
        await message.answer("Такого варианта сейчас нет. Попробуй выбрать другой номер.")
        return

    added = user_storage.add_favorite(message.from_user.id, item)
    if not added:
        await message.answer("Этот вариант уже есть в избранном.", reply_markup=search_results_keyboard(len(last_results)))
        return

    await message.answer(
        f"Добавила в избранное: {escape(str(item.get('university', 'Вуз')))} — "
        f"{escape(str(item.get('program', 'программа')))}.",
        reply_markup=search_results_keyboard(len(last_results)),
    )


def _format_university_card(index: int, item: dict, user_score: int) -> str:
    subjects = ", ".join(item.get("subjects") or []) or "не указаны"
    category = classify_university(user_score, item)
    lines = [
        f"🎓 <b>{index}. {escape(str(item.get('university', 'Вуз')))}</b>",
        f"Город: {escape(str(item.get('city', 'не указан')))}",
        f"Программа: {escape(str(item.get('program', 'не указана')))}",
        f"Категория: {escape(get_recommendation_label(category))}",
        f"Мин. балл: {escape(str(item.get('min_score', 'не указан')))}",
        f"Твои баллы: {user_score}",
        escape(format_score_delta(user_score, item)),
        f"Тип: {escape(str(item.get('type', 'не указан')))}",
    ]

    if item.get("study_form"):
        lines.append(f"Форма: {escape(str(item['study_form']))}")
    if item.get("duration"):
        lines.append(f"Срок: {escape(str(item['duration']))}")

    lines.append(f"Стоимость: {escape(_format_price(item.get('price')))}")
    lines.append(f"Предметы: {escape(subjects)}")

    if item.get("url"):
        lines.append(f"Сайт: {escape(str(item['url']))}")

    lines.extend(
        [
            "",
            f"Пометка: {escape(str(item.get('note') or 'демонстрационные данные'))}",
        ]
    )

    return "\n".join(lines)


def _format_price(price: object) -> str:
    if price is None or price == "":
        return "не указана"
    if isinstance(price, int):
        return f"{price:,} руб./год".replace(",", " ")
    if isinstance(price, str) and price.strip().isdigit():
        return f"{int(price):,} руб./год".replace(",", " ")
    return str(price)


def _get_result_by_number(results: list[dict], result_number: int) -> dict | None:
    index = result_number - 1
    if index < 0 or index >= len(results):
        return None
    return results[index]
