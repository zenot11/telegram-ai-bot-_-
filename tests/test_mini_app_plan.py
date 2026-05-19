from pathlib import Path


MINI_APP_DIR = Path("mini_app")


def read_mini_app_file(name: str) -> str:
    return (MINI_APP_DIR / name).read_text(encoding="utf-8")


def test_plan_tab_and_section_exist() -> None:
    html = read_mini_app_file("index.html")

    assert "План" in html
    assert 'id="plan"' in html
    assert 'id="plan-content"' in html
    assert "Твой план поступления" in html
    assert "Скопировать план" not in html
    assert 'id="plan-copy-fallback"' in html
    assert "MVP" not in html


def test_plan_js_builds_and_renders_local_plan_without_tokens() -> None:
    js = read_mini_app_file("app.js")

    assert "function buildAdmissionPlan" in js
    assert "function renderAdmissionPlan" in js
    assert "function copyAdmissionPlan" in js
    assert "function buildAdmissionPlanText" in js
    assert "renderAdmissionPlan();" in js
    assert "safeItems" in js
    assert "realisticItems" in js
    assert "ambitiousItems" in js
    assert "favorites.length" in js
    assert "comparisonItems.length" in js
    assert "showToast" in js
    assert "TELEGRAM_BOT_TOKEN" not in js
    assert "OPENAI_API_KEY" not in js
    assert "console.log" not in js


def test_plan_js_has_expected_ux_texts() -> None:
    js = read_mini_app_file("app.js")

    assert "Пока нет плана поступления" in js
    assert "Что сделать сначала" in js
    assert "Безопасные варианты" in js
    assert "Реалистичные варианты" in js
    assert "Амбициозные варианты" in js
    assert "Что проверить перед подачей" in js
    assert "Следующие действия" in js
    assert "План скопирован" in js
    assert "Не удалось скопировать автоматически" in js
    assert "Это не гарантия поступления" in js


def test_plan_css_contains_cards_checklist_actions_and_dark_support() -> None:
    css = read_mini_app_file("styles.css")

    assert ".plan-section" in css
    assert ".plan-content" in css
    assert ".plan-hero" in css
    assert ".plan-card" in css
    assert ".plan-badge" in css
    assert ".plan-checklist" in css
    assert ".plan-checkitem" in css
    assert ".plan-actions" in css
    assert ".plan-copy-fallback" in css
    assert '[data-theme="dark"]' in css
