from pathlib import Path


MINI_APP_DIR = Path("mini_app")


def read_mini_app_file(name: str) -> str:
    return (MINI_APP_DIR / name).read_text(encoding="utf-8")


def test_index_contains_feedback_tab_and_form() -> None:
    html = read_mini_app_file("index.html")

    assert "Поддержка" in html
    assert 'id="feedback"' in html
    assert "Поддержка и обратная связь" in html
    assert 'id="feedback-form"' in html
    assert 'id="feedback-category"' in html
    assert 'id="feedback-message"' in html
    assert "Отправить обращение" in html
    assert "Мои последние обращения" in html
    assert "MVP" not in html


def test_app_js_contains_feedback_api_logic_without_tokens() -> None:
    js = read_mini_app_file("app.js")

    assert "/api/feedback" in js
    assert "async function submitFeedback" in js
    assert "async function loadMyFeedback" in js
    assert "function renderFeedbackStatus" in js
    assert "function validateFeedbackForm" in js
    assert "X-Telegram-Init-Data" in js
    assert "showToast" in js
    assert "1000" in js
    assert "TELEGRAM_BOT_TOKEN" not in js
    assert "OPENAI_API_KEY" not in js
    assert "console.log" not in js


def test_styles_include_feedback_blocks_and_dark_support() -> None:
    css = read_mini_app_file("styles.css")

    assert ".feedback-section" in css
    assert ".feedback-form" in css
    assert ".feedback-status-card" in css
    assert ".feedback-ticket" in css
    assert ".feedback-actions" in css
    assert '[data-theme="dark"]' in css
