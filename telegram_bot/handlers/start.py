from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, WebAppInfo

from telegram_bot.config import settings
from telegram_bot.keyboards.menu import main_menu_keyboard
from telegram_bot.services.texts import (
    ABOUT_TEXT,
    BOTFATHER_TEXT,
    DEMO_TEXT,
    HELP_TEXT,
    NEXT_TEXT,
    PRIVACY_TEXT,
)
from telegram_bot.storage.user_data import user_storage


router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "Привет! Я Аиша — помощник абитуриента.\n"
        "Я помогу спокойно подобрать варианты вузов по региону, баллам, направлению и типу обучения.\n"
        "А если из-за поступления тревожно или сложно выбрать — помогу разложить задачу на маленькие шаги.",
        reply_markup=main_menu_keyboard(),
    )


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(HELP_TEXT, reply_markup=main_menu_keyboard())


@router.message(Command("about"))
async def cmd_about(message: Message) -> None:
    await message.answer(ABOUT_TEXT, reply_markup=main_menu_keyboard())


@router.message(Command("demo"))
async def cmd_demo(message: Message) -> None:
    await message.answer(DEMO_TEXT, reply_markup=main_menu_keyboard())


@router.message(Command("privacy"))
async def cmd_privacy(message: Message) -> None:
    await message.answer(PRIVACY_TEXT, reply_markup=main_menu_keyboard())


@router.message(Command("next"))
async def cmd_next(message: Message) -> None:
    await message.answer(NEXT_TEXT, reply_markup=main_menu_keyboard())


@router.message(Command("botfather"))
async def cmd_botfather(message: Message) -> None:
    await message.answer(BOTFATHER_TEXT, reply_markup=main_menu_keyboard())


@router.message(Command("webapp"))
async def cmd_webapp(message: Message) -> None:
    if not settings.webapp_url:
        await message.answer(
            "Mini App пока не настроен. Для локальной демонстрации запусти backend и укажи WEBAPP_URL в .env.",
            reply_markup=main_menu_keyboard(),
        )
        return

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Открыть Mini App", web_app=WebAppInfo(url=settings.webapp_url))]
        ]
    )
    await message.answer("Открой Mini App Аиши:", reply_markup=keyboard)


@router.message(Command("reset"))
async def cmd_reset(message: Message, state: FSMContext) -> None:
    await state.clear()
    if message.from_user:
        user_storage.reset_profile(message.from_user.id)
    await message.answer("Данные, последний подбор и избранное сброшены. Можно начать заново.", reply_markup=main_menu_keyboard())
