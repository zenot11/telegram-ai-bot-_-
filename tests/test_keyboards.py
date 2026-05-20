from aiogram.types import ReplyKeyboardMarkup

from telegram_bot.keyboards.menu import (
    MENU_ABOUT_CALLBACK,
    MENU_ADVICE_CALLBACK,
    MENU_ASSISTANT_CALLBACK,
    MENU_MAIN_CALLBACK,
    MENU_RESULTS_CALLBACK,
    MENU_SEARCH_CALLBACK,
    MENU_SERVICE_CALLBACK,
    about_menu_keyboard,
    about_menu_inline_keyboard,
    advice_keyboard,
    assistant_menu_keyboard,
    assistant_menu_inline_keyboard,
    empty_history_keyboard,
    favorites_keyboard_for_count,
    history_keyboard,
    main_menu_keyboard,
    main_menu_inline_keyboard,
    next_steps_inline_keyboard,
    results_menu_keyboard,
    results_menu_inline_keyboard,
    service_menu_keyboard,
    service_menu_inline_keyboard,
)
from telegram_bot.keyboards.compare import compare_options_keyboard
from telegram_bot.keyboards.export import empty_export_keyboard, export_menu_keyboard
from telegram_bot.keyboards.filters import filtered_results_keyboard, filters_keyboard
from telegram_bot.keyboards.search import search_results_keyboard


def keyboard_texts(markup: ReplyKeyboardMarkup) -> list[str]:
    return [button.text for row in markup.keyboard for button in row]


def inline_keyboard_texts(markup) -> list[str]:
    return [button.text for row in markup.inline_keyboard for button in row]


def inline_callback_data(markup) -> set[str | None]:
    return {button.callback_data for row in markup.inline_keyboard for button in row}


def test_search_save_buttons_match_results_count() -> None:
    texts = keyboard_texts(search_results_keyboard(3))

    assert "Сохранить 1" in texts
    assert "Сохранить 2" in texts
    assert "Сохранить 3" in texts
    assert "Сохранить 4" not in texts
    assert "Итог подбора" in texts
    assert "История подборов" in texts
    assert "Советы по подбору" in texts
    assert "Фильтры результатов" in texts
    assert "Экспорт результата" in texts
    assert "Экспорт результата" in texts


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


def test_main_menu_is_compact_and_contains_sections() -> None:
    texts = keyboard_texts(main_menu_keyboard())

    assert "Подобрать вуз" in texts
    assert "Mini App" in texts
    assert "Мои результаты" in texts
    assert "Помощник" in texts
    assert "Сервис" in texts
    assert "О проекте" in texts
    assert len(texts) == 6
    assert "История подборов" not in texts
    assert "Фильтры результатов" not in texts
    assert "Экспорт результата" not in texts
    assert "Обратная связь" not in texts
    assert "Мой профиль" not in texts


def test_main_menu_inline_keyboard_contains_card_sections() -> None:
    markup = main_menu_inline_keyboard()
    texts = inline_keyboard_texts(markup)
    callbacks = inline_callback_data(markup)

    assert texts == [
        "Подобрать вуз",
        "Mini App",
        "Мои результаты",
        "Помощник",
        "Сервис",
        "О проекте",
    ]
    assert MENU_SEARCH_CALLBACK in callbacks
    assert MENU_RESULTS_CALLBACK in callbacks
    assert MENU_ASSISTANT_CALLBACK in callbacks
    assert MENU_SERVICE_CALLBACK in callbacks
    assert MENU_ABOUT_CALLBACK in callbacks


def test_results_submenu_contains_result_actions() -> None:
    texts = keyboard_texts(results_menu_keyboard())

    assert "Итог подбора" in texts
    assert "Избранные вузы" in texts
    assert "История подборов" in texts
    assert "Сравнить вузы" in texts
    assert "Фильтры результатов" in texts
    assert "Экспорт результата" in texts
    assert "Назад" in texts


def test_results_inline_submenu_contains_back_callback() -> None:
    markup = results_menu_inline_keyboard()
    texts = inline_keyboard_texts(markup)
    callbacks = inline_callback_data(markup)

    assert "Итог подбора" in texts
    assert "Экспорт результата" in texts
    assert MENU_MAIN_CALLBACK in callbacks


def test_assistant_submenu_contains_help_actions() -> None:
    texts = keyboard_texts(assistant_menu_keyboard())

    assert "Советы по подбору" in texts
    assert "Что делать дальше" in texts
    assert "Как читать категории" in texts
    assert "Психологическая поддержка" in texts
    assert "Mini App" in texts
    assert "Назад" in texts


def test_assistant_inline_submenu_contains_back_callback() -> None:
    markup = assistant_menu_inline_keyboard()
    texts = inline_keyboard_texts(markup)
    callbacks = inline_callback_data(markup)

    assert "Советы по подбору" in texts
    assert "Психологическая поддержка" in texts
    assert MENU_MAIN_CALLBACK in callbacks


def test_next_steps_inline_keyboard_contains_user_actions() -> None:
    markup = next_steps_inline_keyboard()
    texts = inline_keyboard_texts(markup)
    callbacks = inline_callback_data(markup)

    assert "Подобрать вуз" in texts
    assert "Советы по подбору" in texts
    assert "Mini App" in texts
    assert "Вернуться в меню" in texts
    assert MENU_SEARCH_CALLBACK in callbacks
    assert MENU_ADVICE_CALLBACK in callbacks
    assert MENU_MAIN_CALLBACK in callbacks


def test_service_submenu_contains_profile_feedback_and_privacy() -> None:
    texts = keyboard_texts(service_menu_keyboard())

    assert "Мой профиль" in texts
    assert "Обратная связь" in texts
    assert "Мои обращения" in texts
    assert "Сбросить данные" in texts
    assert "Приватность" in texts
    assert "Назад" in texts


def test_service_inline_submenu_contains_back_callback() -> None:
    markup = service_menu_inline_keyboard()
    texts = inline_keyboard_texts(markup)
    callbacks = inline_callback_data(markup)

    assert "Мой профиль" in texts
    assert "Обратная связь" in texts
    assert MENU_MAIN_CALLBACK in callbacks


def test_about_submenu_contains_project_info() -> None:
    texts = keyboard_texts(about_menu_keyboard())

    assert "Описание проекта" in texts
    assert "Демо-сценарий" in texts
    assert "BotFather" in texts
    assert "Назад" in texts


def test_about_inline_submenu_contains_back_callback() -> None:
    markup = about_menu_inline_keyboard()
    texts = inline_keyboard_texts(markup)
    callbacks = inline_callback_data(markup)

    assert "О проекте" in texts
    assert "Демо-сценарий" in texts
    assert MENU_MAIN_CALLBACK in callbacks


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
    assert "Фильтры результатов" in texts
    assert "Экспорт результата" in texts


def test_advice_keyboard_without_results_is_compact() -> None:
    texts = keyboard_texts(advice_keyboard(has_results=False))

    assert "Подобрать заново" in texts
    assert "История подборов" in texts
    assert "Сравнить вузы" not in texts


def test_filters_inline_keyboard_contains_expected_callbacks() -> None:
    markup = filters_keyboard(
        {
            "all": 5,
            "safe": 2,
            "realistic": 1,
            "ambitious": 1,
            "budget": 4,
            "paid": 1,
        }
    )
    callbacks = [button.callback_data for row in markup.inline_keyboard for button in row]

    assert "filter_all" in callbacks
    assert "filter_safe" in callbacks
    assert "filter_realistic" in callbacks
    assert "filter_ambitious" in callbacks
    assert "filter_budget" in callbacks
    assert "filter_paid" in callbacks


def test_filtered_results_keyboard_keeps_save_buttons_and_filter_actions() -> None:
    texts = keyboard_texts(filtered_results_keyboard(2))

    assert "Сохранить 1" in texts
    assert "Сохранить 2" in texts
    assert "Сохранить 3" not in texts
    assert "Все варианты" in texts
    assert "Фильтры результатов" in texts


def test_compare_buttons_do_not_promise_fourth_or_fifth_items() -> None:
    texts = keyboard_texts(compare_options_keyboard(5))

    assert "Сравнить первые 3" in texts
    assert "Сравнить 4 и 5" not in texts


def test_export_inline_keyboard_contains_text_and_file_actions() -> None:
    markup = export_menu_keyboard()
    texts = [button.text for row in markup.inline_keyboard for button in row]
    callbacks = [button.callback_data for row in markup.inline_keyboard for button in row]

    assert "Показать текстом" in texts
    assert "Скачать .txt" in texts
    assert "export_text" in callbacks
    assert "export_txt" in callbacks


def test_empty_export_keyboard_points_to_search() -> None:
    texts = keyboard_texts(empty_export_keyboard())

    assert "Подобрать вуз" in texts
    assert "Вернуться в меню" in texts
