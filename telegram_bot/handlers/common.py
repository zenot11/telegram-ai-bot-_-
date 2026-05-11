from aiogram import Router
from aiogram.types import Message

from telegram_bot.keyboards.menu import main_menu_keyboard
from telegram_bot.keyboards.search import support_keyboard
from telegram_bot.services.ai import ai_service, generate_support_reply
from telegram_bot.services.safety import (
    CRISIS_RESPONSE,
    is_crisis_message,
    is_support_message,
)


router = Router()


@router.message()
async def fallback(message: Message) -> None:
    text = message.text or ""

    if is_crisis_message(text):
        await message.answer(CRISIS_RESPONSE, reply_markup=main_menu_keyboard())
        return

    if is_support_message(text):
        fallback = (
            "Похоже, ты сильно вымотался. Давай сделаем задачу меньше: сейчас не выбираем "
            "всю жизнь, а выбираем один следующий шаг."
        )
        answer = await generate_support_reply(text, fallback)
        await message.answer(answer, reply_markup=support_keyboard())
        return

    ai_answer = await ai_service.answer_free_question(text)
    if ai_answer:
        await message.answer(ai_answer, reply_markup=main_menu_keyboard())
        return

    await message.answer(
        "Я могу подобрать вуз, показать сохранённые баллы или помочь спокойно разобрать тревогу. "
        "Выбери действие в меню.",
        reply_markup=main_menu_keyboard(),
    )
