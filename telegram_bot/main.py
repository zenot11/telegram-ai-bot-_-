import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from telegram_bot.config import settings
from telegram_bot.handlers import common, compare, export, feedback, filters, menu, search, start, support


async def set_bot_commands(bot: Bot) -> None:
    await bot.set_my_commands(
        [
            BotCommand(command="start", description="Запуск бота"),
            BotCommand(command="menu", description="Главное меню"),
            BotCommand(command="search", description="Подобрать вуз"),
            BotCommand(command="summary", description="Итог последнего подбора"),
            BotCommand(command="advice", description="Советы по подбору"),
            BotCommand(command="filters", description="Фильтры результатов"),
            BotCommand(command="export", description="Экспорт результата"),
            BotCommand(command="history", description="История подборов"),
            BotCommand(command="clear_history", description="Очистить историю подборов"),
            BotCommand(command="compare", description="Сравнить вузы"),
            BotCommand(command="categories", description="Как читать категории"),
            BotCommand(command="support", description="Психологическая поддержка"),
            BotCommand(command="feedback", description="Обратная связь"),
            BotCommand(command="my_feedback", description="Мои обращения"),
            BotCommand(command="webapp", description="Открыть Mini App"),
            BotCommand(command="about", description="О проекте"),
            BotCommand(command="demo", description="Сценарий демонстрации"),
            BotCommand(command="privacy", description="Приватность"),
            BotCommand(command="next", description="Следующий шаг после подбора"),
            BotCommand(command="botfather", description="Настройки BotFather"),
            BotCommand(command="reset", description="Сброс введённых данных"),
            BotCommand(command="help", description="Помощь"),
        ]
    )


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    if not settings.telegram_bot_token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set. Create .env from .env.example.")

    bot = Bot(
        token=settings.telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(start.router)
    dp.include_router(menu.router)
    dp.include_router(filters.router)
    dp.include_router(export.router)
    dp.include_router(feedback.router)
    dp.include_router(support.router)
    dp.include_router(search.router)
    dp.include_router(compare.router)
    dp.include_router(common.router)

    await set_bot_commands(bot)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
