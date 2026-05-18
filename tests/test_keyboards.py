from aiogram.types import ReplyKeyboardMarkup

from telegram_bot.keyboards.menu import (
    advice_keyboard,
    empty_history_keyboard,
    favorites_keyboard_for_count,
    history_keyboard,
    main_menu_keyboard,
)
from telegram_bot.keyboards.compare import compare_options_keyboard
from telegram_bot.keyboards.search import search_results_keyboard


def keyboard_texts(markup: ReplyKeyboardMarkup) -> list[str]:
    return [button.text for row in markup.keyboard for button in row]


def test_search_save_buttons_match_results_count() -> None:
    texts = keyboard_texts(search_results_keyboard(3))

    assert "Сохранить 1" in texts
    assert "Сохранить 2" in texts
    assert "Сохранить 3" in texts
    assert "Сохранить 4" not in texts
    assert "Итог подбора" in texts
    assert "История подборов" in texts
    assert "Советы по подбору" in texts


def test_search_save_buttons_include_fourth_and_fifth_results() -> None:
    texts = keyboard_texts(search_results_keyboard(5))

    assert "Сохранить 4" in texts
    assert "Сохранить 5" in texts
    assert "Сохранить 6" not in texts


def test_search_save_buttons_do_not_exceed_existing_results() -> None:
    texts = keyboard_texts(search_results_keyboard(2))

    assert "Сохранить 1" in texts
    assert "Сохранить 2" in texts
    assert "Сохранить 3" not in texts


def test_favorites_delete_buttons_include_fourth_and_fifth_items() -> None:
    texts = keyboard_texts(favorites_keyboard_for_count(5))

    assert "Удалить 4" in texts
    assert "Удалить 5" in texts
    assert "Удалить 6" not in texts


def test_main_menu_contains_search_history_button() -> None:
    texts = keyboard_texts(main_menu_keyboard())

    assert "История подборов" in texts
    assert "Советы по подбору" in texts


def test_history_keyboard_actions() -> None:
    texts = keyboard_texts(history_keyboard())

    assert "Повторить последний подбор" in texts
    assert "Очистить историю" in texts
    assert "Подобрать вуз" in texts


def test_empty_history_keyboard_is_compact() -> None:
    texts = keyboard_texts(empty_history_keyboard())

    assert "Подобрать вуз" in texts
    assert "Вернуться в меню" in texts
    assert "Очистить историю" not in texts


def test_advice_keyboard_with_results_contains_next_steps() -> None:
    texts = keyboard_texts(advice_keyboard(has_results=True))

    assert "Итог подбора" in texts
    assert "Сравнить вузы" in texts
    assert "Избранные вузы" in texts
    assert "История подборов" in texts
    assert "Подобрать заново" in texts


def test_advice_keyboard_without_results_is_compact() -> None:
    texts = keyboard_texts(advice_keyboard(has_results=False))

    assert "Подобрать заново" in texts
    assert "История подборов" in texts
    assert "Сравнить вузы" not in texts


def test_compare_buttons_do_not_promise_fourth_or_fifth_items() -> None:
    texts = keyboard_texts(compare_options_keyboard(5))

    assert "Сравнить первые 3" in texts
    assert "Сравнить 4 и 5" not in texts
