from pathlib import Path

from telegram_bot.services import menu_cards


def test_menu_card_assets_exist() -> None:
    for section in ("main", "results", "assistant", "service", "about"):
        path = menu_cards.get_menu_asset_path(section)
        assert path.exists()
        assert path.suffix == ".svg"


def test_menu_card_captions_are_short_and_use_sections() -> None:
    assert "Главное меню Аиши" in menu_cards.get_menu_caption("main")
    assert "Мои результаты" in menu_cards.get_menu_caption("results")
    assert "Помощник" in menu_cards.get_menu_caption("assistant")
    assert "Сервис" in menu_cards.get_menu_caption("service")
    assert "О проекте" in menu_cards.get_menu_caption("about")

    for section in ("main", "results", "assistant", "service", "about"):
        assert 20 <= len(menu_cards.get_menu_caption(section)) <= 300


def test_menu_card_fallback_text_is_available() -> None:
    assert menu_cards.get_menu_fallback_text("main")
    assert menu_cards.get_menu_fallback_text("unknown") == menu_cards.get_menu_caption("main")


def test_menu_cards_module_does_not_contain_secrets() -> None:
    source = Path(menu_cards.__file__).read_text(encoding="utf-8")
    assert "TELEGRAM_BOT_TOKEN" not in source
    assert "OPENAI_API_KEY" not in source
    assert ".env" not in source
