from aiogram.types import ReplyKeyboardMarkup

from telegram_bot.keyboards.menu import favorites_keyboard_for_count
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


def test_compare_buttons_do_not_promise_fourth_or_fifth_items() -> None:
    texts = keyboard_texts(compare_options_keyboard(5))

    assert "Сравнить первые 3" in texts
    assert "Сравнить 4 и 5" not in texts
