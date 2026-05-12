from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from telegram_bot.keyboards.compare import (
    compare_options_keyboard,
    compare_source_keyboard,
    empty_compare_keyboard,
    not_enough_favorites_keyboard,
)
from telegram_bot.keyboards.menu import main_menu_keyboard
from telegram_bot.services.ai import explain_comparison
from telegram_bot.services.compare import format_comparison
from telegram_bot.states.compare_states import CompareStates
from telegram_bot.storage.user_data import user_storage


router = Router()


@router.message(Command("compare"))
@router.message(F.text == "Сравнить вузы")
async def start_compare(message: Message, state: FSMContext) -> None:
    await state.clear()
    if not message.from_user:
        await message.answer("Не удалось определить пользователя.", reply_markup=main_menu_keyboard())
        return

    last_results = user_storage.get_last_results(message.from_user.id)
    favorites = user_storage.get_favorites(message.from_user.id)

    has_last_results = bool(last_results)
    has_favorites = bool(favorites)

    if not has_last_results and not has_favorites:
        await message.answer(
            "Пока нечего сравнивать. Сначала пройди подбор вузов или добавь варианты в избранное.",
            reply_markup=empty_compare_keyboard(),
        )
        return

    if has_last_results and has_favorites:
        await message.answer(
            "Что сравним?",
            reply_markup=compare_source_keyboard(has_last_results=True, has_favorites=True),
        )
        return

    source = "last_results" if has_last_results else "favorites"
    items = last_results if has_last_results else favorites
    await _show_compare_options(message, state, source, items)


@router.message(F.text == "Сравнить последние результаты")
async def compare_last_results(message: Message, state: FSMContext) -> None:
    if not message.from_user:
        await message.answer("Не удалось определить пользователя.", reply_markup=main_menu_keyboard())
        return

    await _show_compare_options(
        message,
        state,
        "last_results",
        user_storage.get_last_results(message.from_user.id),
    )


@router.message(F.text == "Сравнить избранные вузы")
async def compare_favorites(message: Message, state: FSMContext) -> None:
    if not message.from_user:
        await message.answer("Не удалось определить пользователя.", reply_markup=main_menu_keyboard())
        return

    await _show_compare_options(
        message,
        state,
        "favorites",
        user_storage.get_favorites(message.from_user.id),
    )


@router.message(
    StateFilter(CompareStates.choosing_items),
    F.text.in_({"Сравнить 1 и 2", "Сравнить 1 и 3", "Сравнить 2 и 3", "Сравнить первые 3"}),
)
async def compare_selected_items(message: Message, state: FSMContext) -> None:
    if not message.from_user:
        await message.answer("Не удалось определить пользователя.", reply_markup=main_menu_keyboard())
        return

    data = await state.get_data()
    source = data.get("compare_source")
    items = _load_items(message.from_user.id, source)
    selected = _select_items(items, message.text or "")
    user_score = _load_user_score(message.from_user.id)

    if len(selected) < 2:
        await message.answer(
            "Такого набора вариантов сейчас нет. Попробуй выбрать другую кнопку сравнения.",
            reply_markup=compare_options_keyboard(len(items)),
        )
        return

    await message.answer(format_comparison(selected, user_score=user_score), reply_markup=compare_options_keyboard(len(items)))

    explanation = await explain_comparison(selected)
    if explanation:
        await message.answer(explanation, reply_markup=compare_options_keyboard(len(items)))


async def _show_compare_options(
    message: Message,
    state: FSMContext,
    source: str,
    items: list[dict],
) -> None:
    if len(items) < 2:
        await state.clear()
        if source == "favorites":
            await message.answer(
                "Для сравнения нужно минимум два избранных вуза. "
                "Сначала сохрани несколько вариантов после подбора.",
                reply_markup=not_enough_favorites_keyboard(),
            )
        else:
            await message.answer(
                "Для сравнения нужно минимум два варианта. "
                "Пройди подбор ещё раз или сохрани несколько вузов в избранное.",
                reply_markup=empty_compare_keyboard(),
            )
        return

    await state.set_state(CompareStates.choosing_items)
    await state.update_data(compare_source=source)
    source_title = "последних результатов" if source == "last_results" else "избранных вузов"
    scope_hint = (
        " Можно сравнить первые 3 варианта из текущей выдачи."
        if len(items) > 3
        else ""
    )
    await message.answer(
        f"Выбери, какие варианты из {source_title} сравнить. Сейчас доступно: {len(items)}.{scope_hint}",
        reply_markup=compare_options_keyboard(len(items)),
    )


def _load_items(telegram_id: int, source: str | None) -> list[dict]:
    if source == "favorites":
        return user_storage.get_favorites(telegram_id)
    return user_storage.get_last_results(telegram_id)


def _load_user_score(telegram_id: int) -> int | None:
    profile = user_storage.get_profile(telegram_id) or {}
    score = profile.get("score")
    return score if isinstance(score, int) else None


def _select_items(items: list[dict], action: str) -> list[dict]:
    if action == "Сравнить 1 и 2":
        indexes = [0, 1]
    elif action == "Сравнить 1 и 3":
        indexes = [0, 2]
    elif action == "Сравнить 2 и 3":
        indexes = [1, 2]
    elif action == "Сравнить первые 3":
        indexes = [0, 1, 2]
    else:
        indexes = []

    return [items[index] for index in indexes if 0 <= index < len(items)]
