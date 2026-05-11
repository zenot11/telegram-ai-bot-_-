from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

from telegram_bot.handlers.start import HELP_TEXT
from telegram_bot.keyboards.menu import main_menu_keyboard
from telegram_bot.services.validation import education_type_label
from telegram_bot.storage.user_data import user_storage


router = Router()


@router.message(Command("menu"))
async def cmd_menu(message: Message) -> None:
    await message.answer("Главное меню:", reply_markup=main_menu_keyboard())


@router.message(F.text == "Мои баллы")
async def my_scores(message: Message) -> None:
    if not message.from_user:
        await message.answer("Не удалось определить пользователя.", reply_markup=main_menu_keyboard())
        return

    profile = user_storage.get_user(message.from_user.id)
    if not profile or profile.get("score") is None:
        await message.answer(
            "Пока баллы не сохранены. Нажми «Подобрать вуз», и я запомню их во время подбора.",
            reply_markup=main_menu_keyboard(),
        )
        return

    text = (
        "Твои сохранённые данные:\n"
        f"Регион: {profile.get('region', 'не указан')}\n"
        f"Баллы ЕГЭ: {profile.get('score')}\n"
        f"Направление: {profile.get('direction', 'не указано')}\n"
        f"Тип обучения: {education_type_label(profile.get('education_type', ''))}"
    )
    await message.answer(text, reply_markup=main_menu_keyboard())


@router.message(F.text == "Направления")
async def directions(message: Message) -> None:
    await message.answer(
        "Можно указать направление свободным текстом, например:\n"
        "IT, медицина, психология, экономика, педагогика, юриспруденция, инженерия.",
        reply_markup=main_menu_keyboard(),
    )


@router.message(F.text == "Регионы")
async def regions(message: Message) -> None:
    await message.answer(
        "Для MVP в заглушке есть тестовые данные по регионам:\n"
        "Адыгея, Краснодарский край, Москва, Санкт-Петербург, Татарстан.\n\n"
        "Можно ввести регион вручную во время подбора.",
        reply_markup=main_menu_keyboard(),
    )


@router.message(F.text == "Помощь")
async def help_button(message: Message) -> None:
    await message.answer(HELP_TEXT, reply_markup=main_menu_keyboard())
