from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from telegram_bot.keyboards.menu import main_menu_keyboard
from telegram_bot.keyboards.search import support_keyboard


router = Router()


@router.message(Command("support"))
@router.message(F.text == "Психологическая поддержка")
async def support_entry(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "Похоже, поступление может давить и перегружать. Давай сделаем задачу меньше: "
        "сейчас не выбираем всю жизнь, а выбираем один следующий шаг.",
        reply_markup=support_keyboard(),
    )


@router.message(F.text == "Сделать короткий план")
async def short_plan(message: Message) -> None:
    await message.answer(
        "Короткий план:\n"
        "1. Выбери 1 регион, с которого начнём.\n"
        "2. Введи текущие баллы ЕГЭ.\n"
        "3. Выбери одно направление, даже если пока не уверен.\n"
        "4. Получи 3–5 вариантов и сравни их спокойно.",
        reply_markup=support_keyboard(),
    )


@router.message(F.text == "Вернуться позже")
async def come_back_later(message: Message) -> None:
    await message.answer(
        "Хорошо. Можно вернуться к подбору, когда будет больше сил.",
        reply_markup=main_menu_keyboard(),
    )
