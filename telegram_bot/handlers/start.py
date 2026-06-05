from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, WebAppInfo

from telegram_bot.config import settings
from telegram_bot.keyboards.menu import main_menu_inline_keyboard, main_menu_keyboard, next_steps_inline_keyboard
from telegram_bot.services.menu_cards import send_menu_card
from telegram_bot.services.next_steps import build_next_steps_text
from telegram_bot.services.texts import (
    ABOUT_TEXT,
    BOTFATHER_TEXT,
    DEMO_TEXT,
    HELP_TEXT,
    PRIVACY_TEXT,
)
from telegram_bot.storage.user_data import user_storage


router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await send_menu_card(message, "main", main_menu_inline_keyboard())


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
@router.message(Command("plan"))
async def cmd_next(message: Message) -> None:
    user_id = message.from_user.id if message.from_user else 0
    profile = user_storage.get_profile(user_id) if user_id else None
    results = user_storage.get_last_results(user_id) if user_id else []
    await message.answer(
        build_next_steps_text(profile, results),
        reply_markup=next_steps_inline_keyboard(),
    )


@router.message(Command("botfather"))
async def cmd_botfather(message: Message) -> None:
    await message.answer(BOTFATHER_TEXT, reply_markup=main_menu_keyboard())


@router.message(Command("webapp"))
@router.message(F.text.in_({"Mini App", "📱 Mini App", "Открыть Mini App"}))
async def cmd_webapp(message: Message) -> None:
    if not settings.webapp_url:
        await message.answer(
            "Mini App сейчас не подключён.\n"
            "Пока можно продолжить в обычном режиме: сделай подбор через /search "
            "или открой главное меню.",
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
    await message.answer(
        "Данные, последний подбор, история и избранное сброшены. Можно начать заново.",
        reply_markup=main_menu_keyboard(),
    )
