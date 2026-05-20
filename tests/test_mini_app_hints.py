from pathlib import Path


MINI_APP_DIR = Path("mini_app")


def read_mini_app_file(name: str) -> str:
    return (MINI_APP_DIR / name).read_text(encoding="utf-8")


def test_index_contains_aisha_hint_controls() -> None:
    html = read_mini_app_file("index.html")

    assert "aisha-hint" in html
    assert "Aisha советует" in html
    assert "aisha-orb" in html
    assert "aisha-hint-hide" in html
    assert "aisha-hint-show" in html
    assert "Показать подсказки" in html
    assert "MVP" not in html


def test_app_js_builds_contextual_aisha_hints_without_tokens() -> None:
    js = read_mini_app_file("app.js")

    assert "function getAishaHintContext" in js
    assert "function buildAishaHint" in js
    assert "function renderAishaHint" in js
    assert "function updateAishaHint" in js
    assert "function hideAishaHints" in js
    assert "function showAishaHints" in js
    assert "aisha_hints_hidden" in js
    assert "actionTab" in js
    assert "lastResults" in js
    assert "favorites" in js
    assert "comparisonItems" in js
    assert "activeTab" in js
    assert "showToast" in js
    assert "TELEGRAM_BOT_TOKEN" not in js
    assert "OPENAI_API_KEY" not in js
    assert "console.log(initData)" not in js


def test_app_js_has_hint_texts_for_key_states() -> None:
    js = read_mini_app_file("app.js")

    assert "Начни с подбора" in js
    assert "Я ищу подходящие варианты" in js
    assert "ничего не найдено" in js
    assert "Сохрани 2–3 варианта" in js
    assert "Для сравнения нужно минимум 2 вуза" in js
    assert "Проверь баллы, стоимость, город и сайт" in js
    assert "План помогает не потеряться" in js
    assert "сохрани отчёт" in js
    assert "отправь обращение" in js


def test_styles_define_aisha_hint_components_with_dark_and_reduced_motion() -> None:
    css = read_mini_app_file("styles.css")

    assert ".aisha-hint" in css
    assert ".aisha-orb" in css
    assert ".aisha-hint-show" in css
    assert ".aisha-hint.is-hidden" in css
    assert ".hint-action" in css
    assert ".hint-secondary" in css
    assert "--hint-bg" in css
    assert "--hint-border" in css
    assert '[data-theme="dark"]' in css
    assert "prefers-reduced-motion" in css
