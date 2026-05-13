from pathlib import Path

from telegram_bot.config import load_settings


def test_webapp_url_can_be_empty(monkeypatch) -> None:
    monkeypatch.delenv("WEBAPP_URL", raising=False)

    settings = load_settings()

    assert settings.webapp_url is None


def test_webapp_url_is_read_from_environment(monkeypatch) -> None:
    monkeypatch.setenv("WEBAPP_URL", "https://example.com/miniapp")

    settings = load_settings()

    assert settings.webapp_url == "https://example.com/miniapp"


def test_env_example_contains_webapp_url() -> None:
    content = Path(".env.example").read_text(encoding="utf-8")

    assert "WEBAPP_URL=" in content
