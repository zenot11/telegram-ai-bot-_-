from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from telegram_bot.keyboards.feedback import (
    FEEDBACK_CANCEL_CALLBACK,
    FEEDBACK_CATEGORY_PREFIX,
    empty_feedback_keyboard,
    feedback_cancel_keyboard,
    feedback_categories_keyboard,
    feedback_created_keyboard,
)
from telegram_bot.keyboards.menu import main_menu_keyboard
from telegram_bot.services.feedback import (
    format_feedback_ticket_created,
    format_user_feedback,
    get_feedback_category_label,
    validate_feedback_message,
)
from telegram_bot.states.feedback_states import FeedbackStates
from telegram_bot.storage.feedback_data import create_feedback_ticket, get_user_feedback
from telegram_bot.storage.user_data import user_storage


router = Router()


@router.message(Command("feedback"))
@router.message(
    F.text.in_(
        {
            "Обратная связь",
            "📬 Обратная связь",
            "Поддержка проекта",
            "Создать обращение",
            "Создать ещё обращение",
        }
    )
)
async def feedback_entry(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "Выбери тип обращения.\n\n"
        "Если тебе тревожно из-за поступления, используй /support. "
        "Если заметил ошибку в сервисе, подборе или Mini App, используй /feedback.",
        reply_markup=feedback_categories_keyboard(),
    )


@router.callback_query(F.data.startswith(FEEDBACK_CATEGORY_PREFIX))
async def choose_feedback_category(callback: CallbackQuery, state: FSMContext) -> None:
    category = (callback.data or "").removeprefix(FEEDBACK_CATEGORY_PREFIX)
    await state.update_data(feedback_category=category)
    await state.set_state(FeedbackStates.message)
    await callback.answer()

    if callback.message:
        await callback.message.answer(
            f"Тип обращения: {get_feedback_category_label(category)}\n\n"
            "Опиши обращение одним сообщением. Например: не нашёл регион Крым, "
            "Mini App не открывается, в карточке вуза неверная ссылка.",
            reply_markup=feedback_cancel_keyboard(),
        )


@router.callback_query(F.data == FEEDBACK_CANCEL_CALLBACK)
async def cancel_feedback_callback(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.answer("Обращение отменено.")
    if callback.message:
        await callback.message.answer("Обращение отменено.", reply_markup=main_menu_keyboard())


@router.message(Command("cancel"))
@router.message(FeedbackStates.message, F.text == "Отмена")
async def cancel_feedback(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Обращение отменено.", reply_markup=main_menu_keyboard())


@router.message(FeedbackStates.message)
async def save_feedback_message(message: Message, state: FSMContext) -> None:
    text = message.text or ""
    is_valid, error = validate_feedback_message(text)
    if not is_valid:
        await message.answer(error, reply_markup=feedback_cancel_keyboard())
        return

    if not message.from_user:
        await message.answer("Не удалось определить пользователя.", reply_markup=main_menu_keyboard())
        await state.clear()
        return

    state_data = await state.get_data()
    category = str(state_data.get("feedback_category") or "other")
    ticket = create_feedback_ticket(
        source="bot",
        user_id=message.from_user.id,
        user_name=_format_user_name(message),
        category=category,
        message=text,
        context=_build_bot_feedback_context(message.from_user.id),
    )
    await state.clear()
    await message.answer(format_feedback_ticket_created(ticket), reply_markup=feedback_created_keyboard())


@router.message(Command("my_feedback"))
@router.message(F.text == "Мои обращения")
async def my_feedback(message: Message, state: FSMContext) -> None:
    await state.clear()
    if not message.from_user:
        await message.answer("Не удалось определить пользователя.", reply_markup=main_menu_keyboard())
        return

    tickets = get_user_feedback(message.from_user.id, limit=5)
    reply_markup = feedback_created_keyboard() if tickets else empty_feedback_keyboard()
    await message.answer(format_user_feedback(tickets), reply_markup=reply_markup)


def _format_user_name(message: Message) -> str | None:
    user = message.from_user
    if not user:
        return None
    full_name = " ".join(part for part in (user.first_name, user.last_name) if part).strip()
    if full_name:
        return full_name
    if user.username:
        return f"@{user.username}"
    return None


def _build_bot_feedback_context(user_id: int) -> dict:
    profile = user_storage.get_profile(user_id) or {}
    last_results = user_storage.get_last_results(user_id)
    return {
        "last_search": {
            "region": profile.get("region"),
            "score": profile.get("score"),
            "direction": profile.get("direction"),
            "type": profile.get("education_type"),
            "results_count": len(last_results),
        },
        "page": "telegram_bot",
    }
