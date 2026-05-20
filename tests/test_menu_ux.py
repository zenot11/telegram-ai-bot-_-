from telegram_bot.handlers import menu
from telegram_bot.keyboards.menu import (
    about_menu_keyboard,
    assistant_menu_keyboard,
    main_menu_keyboard,
    results_menu_keyboard,
    service_menu_keyboard,
)


def keyboard_texts(markup) -> list[str]:
    return [button.text for row in markup.keyboard for button in row]


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
