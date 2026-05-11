from html import escape

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from telegram_bot.handlers.start import HELP_TEXT
from telegram_bot.keyboards.menu import main_menu_keyboard
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


@router.message(F.text == "Мои баллы")
async def my_scores(message: Message, state: FSMContext) -> None:
    await state.clear()
    if not message.from_user:
        await message.answer("Не удалось определить пользователя.", reply_markup=main_menu_keyboard())
        return

    profile = user_storage.get_profile(message.from_user.id)
    if not profile or profile.get("score") is None:
        await message.answer(
            "Пока баллы не сохранены. Нажми “Подобрать вуз”, и я запомню их во время подбора.",
            reply_markup=main_menu_keyboard(),
        )
        return

    last_results = user_storage.get_last_results(message.from_user.id)
    history = "История последнего подбора: пока нет сохранённых результатов."
    if last_results:
        titles = [
            f"{item.get('university', 'Вуз')} — {item.get('program', 'программа')}"
            for item in last_results[:3]
        ]
        history = "История последнего подбора:\n" + "\n".join(
            f"{index}. {escape(title)}" for index, title in enumerate(titles, start=1)
        )

    text = (
        "Твои сохранённые данные:\n"
        f"Регион: {escape(str(profile.get('region', 'не указан')))}\n"
        f"Баллы ЕГЭ: {escape(str(profile.get('score')))}\n"
        f"Направление: {escape(str(profile.get('direction', 'не указано')))}\n"
        f"Тип обучения: {education_type_label(profile.get('education_type', ''))}"
        f"\n\n{history}"
    )
    await message.answer(text, reply_markup=main_menu_keyboard())


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
