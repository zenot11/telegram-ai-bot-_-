from pathlib import Path


MINI_APP_DIR = Path("mini_app")


def read_mini_app_file(name: str) -> str:
    return (MINI_APP_DIR / name).read_text(encoding="utf-8")


def test_index_contains_webapp_session_status_elements() -> None:
    html = read_mini_app_file("index.html")

    assert "session-badge" in html
    assert "session-card" in html
    assert "session-description" in html
    assert "Статус Mini App" in html
    assert "MVP" not in html


def test_app_js_checks_webapp_session_without_exposing_secrets() -> None:
    js = read_mini_app_file("app.js")

    assert "/api/webapp/session" in js
    assert "X-Telegram-Init-Data" in js
    assert "function checkWebAppSession" in js
    assert "function renderSessionStatus" in js
    assert "function hasTelegramInitData" in js
    assert "function isTelegramSessionVerified" in js
    assert "Локальный режим" in js
    assert "Telegram-сессия не прошла проверку" in js
    assert "TELEGRAM_BOT_TOKEN" not in js
    assert "OPENAI_API_KEY" not in js
    assert "console.log" not in js


def test_styles_include_webapp_session_states() -> None:
    css = read_mini_app_file("styles.css")

    assert ".session-badge" in css
    assert ".session-card" in css
    assert ".session-badge--success" in css
    assert ".session-badge--local" in css
    assert ".session-badge--warning" in css
    assert ".session-badge--error" in css
    assert ".session-card--success" in css
    assert ".session-card--local" in css
    assert ".session-card--warning" in css
    assert ".session-card--error" in css
    assert '[data-theme="dark"]' in css
