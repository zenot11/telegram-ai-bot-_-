from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from telegram_bot.keyboards.menu import main_menu_keyboard
from telegram_bot.keyboards.search import support_keyboard
from telegram_bot.services.ai import generate_support_reply


router = Router()


@router.message(Command("support"))
@router.message(F.text == "Психологическая поддержка")
async def support_entry(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "Я рядом. Поступление правда может давить: баллы, выбор, ожидания родителей, страх ошибиться.\n"
        "Выбери, что ближе к твоей ситуации:",
        reply_markup=support_keyboard(),
    )


@router.message(StateFilter(None), F.text == "Мне тревожно")
async def anxiety(message: Message) -> None:
    fallback = (
        "Похоже, тревоги сейчас много. Давай не будем решать всё сразу. "
        "Сначала выберем один маленький следующий шаг: например, посмотреть 3 варианта вузов "
        "или спокойно записать свои баллы."
    )
    await _answer_support(message, fallback, "Пользователю тревожно из-за поступления.")


@router.message(StateFilter(None), F.text == "Я не знаю, куда поступать")
async def unsure_direction(message: Message) -> None:
    fallback = (
        "Это нормально — не знать точный ответ сразу. Можно начать не с «профессии на всю жизнь», "
        "а с того, какие предметы тебе даются легче и что тебе хотя бы немного интересно."
    )
    await _answer_support(message, fallback, "Пользователь не знает, куда поступать.")


@router.message(StateFilter(None), F.text == "Я боюсь не поступить")
async def fear_not_admitted(message: Message) -> None:
    fallback = (
        "Страх не поступить понятен. Но сейчас полезнее не пугать себя худшим вариантом, "
        "а собрать несколько запасных маршрутов: бюджет, платное, другой регион, похожее направление."
    )
    await _answer_support(message, fallback, "Пользователь боится не поступить.")


@router.message(StateFilter(None), F.text == "На меня давят родители")
async def parents_pressure(message: Message) -> None:
    fallback = (
        "Когда давят ожидания, выбирать сложнее. Попробуй отделить два вопроса: "
        "чего хотят от тебя другие и какие варианты реально подходят тебе по баллам, интересам и возможностям."
    )
    await _answer_support(message, fallback, "На пользователя давят родители или ожидания семьи.")


@router.message(StateFilter(None), F.text.in_({"Составить короткий план", "Сделать короткий план"}))
async def short_plan(message: Message) -> None:
    await message.answer(
        "Короткий план:\n"
        "1. Записать свои баллы.\n"
        "2. Выбрать 1-2 региона.\n"
        "3. Выбрать 2-3 направления.\n"
        "4. Найти минимум 3 варианта вузов.\n"
        "5. Отдельно оставить запасной вариант.",
        reply_markup=support_keyboard(),
    )


@router.message(StateFilter(None), F.text.in_({"Вернуться в меню", "Вернуться позже"}))
async def back_to_menu(message: Message) -> None:
    await message.answer("Главное меню. Выбери, с чего начнём:", reply_markup=main_menu_keyboard())


async def _answer_support(message: Message, fallback: str, situation: str) -> None:
    answer = await generate_support_reply(fallback, situation=situation)
    await message.answer(answer or fallback, reply_markup=support_keyboard())
