from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, WebAppInfo

from telegram_bot.config import settings
from telegram_bot.keyboards.menu import main_menu_keyboard
from telegram_bot.storage.user_data import user_storage


router = Router()

HELP_TEXT = (
    "Я Аиша, AI-помощник для абитуриентов.\n\n"
    "Команды:\n"
    "/start — запуск бота\n"
    "/menu — главное меню\n"
    "/search — подбор вузов\n"
    "/compare — сравнение вузов\n"
    "/categories — как читать категории подбора\n"
    "/webapp — открыть Mini App\n"
    "/support — психологическая поддержка\n"
    "/reset — сброс введённых данных\n"
    "/help — помощь\n\n"
    "Чтобы начать подбор, нажми «Подобрать вуз» или введи /search. "
    "После подбора можно сохранить варианты в «Избранные вузы», сравнить их через /compare "
    "и посмотреть данные в «Мой профиль». Категории подбора можно посмотреть через /categories."
)


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
