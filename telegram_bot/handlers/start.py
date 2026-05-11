from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from telegram_bot.keyboards.menu import main_menu_keyboard
from telegram_bot.storage.user_data import user_storage


router = Router()

HELP_TEXT = (
    "Я Аиша, AI-помощник для абитуриентов.\n\n"
    "Команды:\n"
    "/start — запуск бота\n"
    "/menu — главное меню\n"
    "/search — подбор вузов\n"
    "/support — психологическая поддержка\n"
    "/reset — сброс введённых данных\n"
    "/help — помощь\n\n"
    "Чтобы начать подбор, нажми «Подобрать вуз» или введи /search."
)


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "Привет! Я Аиша. Помогу подобрать вуз по региону, баллам, направлению "
        "и типу обучения. Если из-за поступления тревожно, я помогу разложить "
        "задачу на маленькие шаги.",
        reply_markup=main_menu_keyboard(),
    )


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(HELP_TEXT, reply_markup=main_menu_keyboard())


@router.message(Command("reset"))
async def cmd_reset(message: Message, state: FSMContext) -> None:
    await state.clear()
    if message.from_user:
        user_storage.reset_user(message.from_user.id)
    await message.answer("Данные сброшены. Можно начать заново.", reply_markup=main_menu_keyboard())
