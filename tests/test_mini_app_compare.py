from pathlib import Path


MINI_APP_DIR = Path("mini_app")


def read_mini_app_file(name: str) -> str:
    return (MINI_APP_DIR / name).read_text(encoding="utf-8")


def test_comparison_tab_and_section_exist() -> None:
    html = read_mini_app_file("index.html")

    assert "Сравнение" in html
    assert 'id="comparison"' in html
    assert 'id="comparison-status"' in html
    assert 'id="comparison-table"' in html
    assert "Выбери 2–3 варианта" in html
    assert "MVP" not in html


def test_comparison_js_uses_local_storage_without_tokens() -> None:
    js = read_mini_app_file("app.js")

    assert "aisha_compare" in js
    assert "MAX_COMPARISON_ITEMS = 3" in js
    assert "comparisonItems" in js
    assert "function toggleCompare" in js
    assert "function renderComparison" in js
    assert "function clearComparison" in js
    assert "function getUniversityKey" in js
    assert "Можно сравнить до 3 вариантов одновременно" in js
    assert "Выбран 1 вариант" in js
    assert "formatValue" in js
    assert "textValue" in js
    assert "OPENAI_API_KEY" not in js
    assert "TELEGRAM_BOT_TOKEN" not in js


def test_comparison_js_has_table_rows_and_safe_links() -> None:
    js = read_mini_app_file("app.js")

    assert "Вуз" in js
    assert "Программа" in js
    assert "Город" in js
    assert "Регион" in js
    assert "Направление" in js
    assert "Категория" in js
    assert "Мин. балл" in js
    assert "Запас/не хватает" in js
    assert "Стоимость" in js
    assert 'rel="noopener noreferrer"' in js


def test_comparison_css_contains_table_and_highlight_styles() -> None:
    css = read_mini_app_file("styles.css")

    assert ".comparison-section" in css
    assert ".comparison-table-scroll" in css
    assert ".comparison-table" in css
    assert ".compare-best" in css
    assert ".compare-good" in css
    assert ".compare-warning" in css
    assert "overflow-x: auto" in css
    assert '[data-theme="dark"]' in css
