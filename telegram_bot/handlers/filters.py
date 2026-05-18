from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from telegram_bot.keyboards.filters import (
    FILTER_CALLBACK_PREFIX,
    empty_filtered_results_keyboard,
    empty_filters_keyboard,
    filtered_results_keyboard,
    filters_keyboard,
)
from telegram_bot.keyboards.menu import main_menu_keyboard
from telegram_bot.services.filters import (
    EMPTY_FILTERS_TEXT,
    FILTER_ALL,
    FILTER_NAMES,
    build_filtered_results_message,
    build_filters_overview_message,
    filter_results,
    get_filter_counts,
)
from telegram_bot.storage.user_data import user_storage


router = Router()


@router.message(Command("filters"))
@router.message(F.text == "Фильтры результатов")
async def show_filters(message: Message, state: FSMContext) -> None:
    await state.clear()
    if not message.from_user:
        await message.answer("Не удалось определить пользователя.", reply_markup=main_menu_keyboard())
        return

    profile = user_storage.get_profile(message.from_user.id)
    last_results = user_storage.get_last_results(message.from_user.id)
    if not last_results:
        await message.answer(EMPTY_FILTERS_TEXT, reply_markup=empty_filters_keyboard())
        return

    score = _profile_score(profile)
    counts = get_filter_counts(last_results, score)
    await message.answer(
        build_filters_overview_message(profile, last_results),
        reply_markup=filters_keyboard(counts),
    )


@router.message(F.text == "Все варианты")
async def show_all_results(message: Message, state: FSMContext) -> None:
    await state.clear()
    if not message.from_user:
        await message.answer("Не удалось определить пользователя.", reply_markup=main_menu_keyboard())
        return
    await _send_filtered_results(message, message.from_user.id, FILTER_ALL)


@router.callback_query(F.data.in_({f"{FILTER_CALLBACK_PREFIX}{name}" for name in FILTER_NAMES}))
async def apply_filter(callback: CallbackQuery) -> None:
    await callback.answer()
    if not callback.from_user or not callback.message:
        return

    filter_name = str(callback.data or "").removeprefix(FILTER_CALLBACK_PREFIX)
    await _send_filtered_results(callback.message, callback.from_user.id, filter_name)


async def _send_filtered_results(message: Message, telegram_id: int, filter_name: str) -> None:
    profile = user_storage.get_profile(telegram_id)
    last_results = user_storage.get_last_results(telegram_id)
    if not last_results:
        await message.answer(EMPTY_FILTERS_TEXT, reply_markup=empty_filters_keyboard())
        return

    filtered = filter_results(last_results, filter_name, _profile_score(profile))
    user_storage.set_active_results(telegram_id, filtered)
    reply_markup = (
        filtered_results_keyboard(len(filtered))
        if filtered
        else empty_filtered_results_keyboard()
    )
    await message.answer(
        build_filtered_results_message(profile, last_results, filtered, filter_name),
        reply_markup=reply_markup,
    )


def _profile_score(profile: dict | None) -> int | None:
    if not isinstance(profile, dict):
        return None
    score = profile.get("score")
    if isinstance(score, int):
        return score
    if isinstance(score, str) and score.strip().isdigit():
        return int(score.strip())
    return None
