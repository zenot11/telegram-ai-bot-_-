from pathlib import Path


MINI_APP_DIR = Path("mini_app")


def read_mini_app_file(name: str) -> str:
    return (MINI_APP_DIR / name).read_text(encoding="utf-8")


def test_export_tab_and_section_exist() -> None:
    html = read_mini_app_file("index.html")

    assert "Экспорт" in html
    assert 'id="export"' in html
    assert 'id="export-content"' in html
    assert "Отчёт по подбору" in html
    assert "Скопировать отчёт" in html
    assert "Печать / сохранить PDF" in html
    assert 'id="export-copy-fallback"' in html
    assert "MVP" not in html


def test_export_js_builds_copyable_printable_report_without_tokens() -> None:
    js = read_mini_app_file("app.js")

    assert "function buildExportReportData" in js
    assert "function buildExportPlainText" in js
    assert "function renderExportPreview" in js
    assert "function copyExportReport" in js
    assert "function printExportReport" in js
    assert "function refreshExportReport" in js
    assert "window.print" in js
    assert "navigator.clipboard" in js
    assert "exportCopyFallbackNode" in js
    assert "showToast" in js
    assert "lastResults" in js
    assert "favorites" in js
    assert "comparisonItems" in js
    assert "buildAdmissionPlan" in js
    assert "TELEGRAM_BOT_TOKEN" not in js
    assert "OPENAI_API_KEY" not in js
    assert "console.log" not in js


def test_export_js_has_expected_report_sections() -> None:
    js = read_mini_app_file("app.js")

    assert "Аиша — отчёт по подбору вузов" in js
    assert "Параметры подбора" in js
    assert "Краткий итог" in js
    assert "Найденные варианты" in js
    assert "Избранные вузы" in js
    assert "Сравнение" in js
    assert "План поступления" in js
    assert "сохранить отчёт как PDF" in js
    assert "Сначала выполни подбор" in js
    assert "Проходные баллы и условия поступления нужно проверять" in js


def test_export_css_contains_preview_actions_and_print_styles() -> None:
    css = read_mini_app_file("styles.css")

    assert ".export-section" in css
    assert ".export-report" in css
    assert ".export-actions" in css
    assert ".export-copy-fallback" in css
    assert ".export-section-block" in css
    assert ".export-item" in css
    assert "@media print" in css
    assert ".no-print" in css
    assert "#ffffff" in css or "#fff" in css
    assert "#111111" in css
    assert '[data-theme="dark"]' in css
