from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from aiogram.types import CallbackQuery, FSInputFile, InlineKeyboardMarkup, Message


logger = logging.getLogger(__name__)

MENU_ASSETS_DIR = Path(__file__).resolve().parents[1] / "assets" / "menu"

MENU_CARD_CAPTIONS = {
    "main": (
        "🎓 Главное меню Аиши\n\n"
        "Выбери раздел: можно начать подбор, открыть Mini App, посмотреть результаты "
        "или перейти к помощнику."
    ),
    "results": (
        "📊 Мои результаты\n\n"
        "Здесь собраны действия с последним подбором: итог, избранное, история, "
        "сравнение, фильтры и экспорт."
    ),
    "assistant": (
        "🧭 Помощник\n\n"
        "Здесь можно получить советы по подбору, следующий шаг и поддержку, "
        "если сложно выбрать."
    ),
    "service": (
        "⚙️ Сервис\n\n"
        "Профиль, обратная связь, мои обращения, приватность и управление сохранёнными данными."
    ),
    "about": (
        "ℹ️ О проекте\n\n"
        "Информация об Аише, демо-сценарий и команды BotFather."
    ),
}


def get_menu_asset_path(section: str) -> Path:
    normalized_section = _normalize_section(section)
    return MENU_ASSETS_DIR / f"{normalized_section}.svg"


def get_menu_caption(section: str) -> str:
    return MENU_CARD_CAPTIONS[_normalize_section(section)]


def get_menu_fallback_text(section: str) -> str:
    return get_menu_caption(section)


async def send_menu_card(
    target: Message | CallbackQuery,
    section: str,
    keyboard: InlineKeyboardMarkup,
) -> None:
    if isinstance(target, CallbackQuery):
        await target.answer()
        message = target.message
        if not message:
            return
        await _send_menu_card_to_message(message, section, keyboard)
        return

    await _send_menu_card_to_message(target, section, keyboard)


async def edit_or_send_menu_card(
    callback: CallbackQuery,
    section: str,
    keyboard: InlineKeyboardMarkup,
) -> None:
    await send_menu_card(callback, section, keyboard)


async def _send_menu_card_to_message(
    message: Any,
    section: str,
    keyboard: InlineKeyboardMarkup,
) -> None:
    caption = get_menu_caption(section)
    asset_path = get_menu_asset_path(section)

    if asset_path.exists():
        try:
            await message.answer_photo(
                photo=FSInputFile(str(asset_path)),
                caption=caption,
                reply_markup=keyboard,
            )
            return
        except Exception as error:  # pragma: no cover - depends on Telegram transport
            logger.warning(
                "Menu banner send failed for section %s: %s",
                section,
                error.__class__.__name__,
            )

    await message.answer(get_menu_fallback_text(section), reply_markup=keyboard)


def _normalize_section(section: str) -> str:
    if section not in MENU_CARD_CAPTIONS:
        return "main"
    return section
