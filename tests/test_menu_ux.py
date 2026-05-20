from telegram_bot.handlers import menu
from telegram_bot.keyboards.menu import (
    about_menu_keyboard,
    about_menu_inline_keyboard,
    assistant_menu_keyboard,
    assistant_menu_inline_keyboard,
    main_menu_keyboard,
    main_menu_inline_keyboard,
    results_menu_keyboard,
    results_menu_inline_keyboard,
    service_menu_keyboard,
    service_menu_inline_keyboard,
)
from telegram_bot.services.menu_cards import get_menu_caption


def keyboard_texts(markup) -> list[str]:
    return [button.text for row in markup.keyboard for button in row]


def inline_keyboard_texts(markup) -> list[str]:
    return [button.text for row in markup.inline_keyboard for button in row]


def test_menu_handler_imports_router() -> None:
    assert menu.router is not None


def test_main_menu_keeps_only_primary_sections() -> None:
    texts = keyboard_texts(main_menu_keyboard())

    assert texts == [
        "Подобрать вуз",
        "Mini App",
        "Мои результаты",
        "Помощник",
        "Сервис",
        "О проекте",
    ]


def test_submenus_have_back_navigation() -> None:
    for markup in (
        results_menu_keyboard(),
        assistant_menu_keyboard(),
        service_menu_keyboard(),
        about_menu_keyboard(),
    ):
        assert "Назад" in keyboard_texts(markup)


def test_card_inline_menus_keep_same_sections() -> None:
    assert inline_keyboard_texts(main_menu_inline_keyboard()) == [
        "Подобрать вуз",
        "Mini App",
        "Мои результаты",
        "Помощник",
        "Сервис",
        "О проекте",
    ]

    for markup in (
        results_menu_inline_keyboard(),
        assistant_menu_inline_keyboard(),
        service_menu_inline_keyboard(),
        about_menu_inline_keyboard(),
    ):
        assert "Назад" in inline_keyboard_texts(markup)


def test_menu_card_captions_match_sections() -> None:
    for section in ("main", "results", "assistant", "service", "about"):
        assert get_menu_caption(section)
