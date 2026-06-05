from pathlib import Path


MINI_APP_DIR = Path("mini_app")


def read_mini_app_file(name: str) -> str:
    return (MINI_APP_DIR / name).read_text(encoding="utf-8")


def test_index_contains_quick_start_helpers_and_toasts() -> None:
    html = read_mini_app_file("index.html")

    assert "Быстрый старт" in html
    assert "Попробовать пример" in html
    assert "Адыгея · 230 · IT · Бюджет" in html
    assert "Москва · 260 · экономика · Бюджет" in html
    assert "Татарстан · 250 · медицина · Бюджет" in html
    assert "data-quick-scenario" in html
    assert "field-helper" in html
    assert "Введи сумму баллов ЕГЭ" in html
    assert "Очистить форму" in html
    assert "toast-container" in html
    assert "Как пользоваться" in html
    assert "Проверь данные на официальных сайтах вузов" in html
    assert "MVP" not in html


def test_app_js_contains_quick_scenarios_and_clear_form_logic() -> None:
    js = read_mini_app_file("app.js")

    assert "quickScenarios" in js
    assert "function applyQuickScenario" in js
    assert "function setFormValues" in js
    assert "function clearSearchForm" in js
    assert "setDirectionValue(direction, { selected: true })" in js
    assert "clearDirectionSelection()" in js
    assert "Сценарий применён" in js
    assert "Форма очищена" in js
    assert "Адыгея" in js
    assert "Москва" in js
    assert "Татарстан" in js


def test_app_js_contains_toasts_for_key_actions_without_tokens() -> None:
    js = read_mini_app_file("app.js")

    assert "function showToast" in js
    assert "toast--" in js
    assert "Добавлено в избранное" in js
    assert "Удалено из избранного" in js
    assert "Избранное очищено" in js
    assert "Добавлено к сравнению" in js
    assert "Убрано из сравнения" in js
    assert "Сравнение очищено" in js
    assert "Можно сравнить до 3 вариантов" in js
    assert "Тёмная тема включена" in js
    assert "Светлая тема включена" in js
    assert "TELEGRAM_BOT_TOKEN" not in js
    assert "OPENAI_API_KEY" not in js
    assert "console.log" not in js


def test_app_js_improves_empty_states() -> None:
    js = read_mini_app_file("app.js")

    assert "По этим параметрам вариантов не нашлось" in js
    assert "По текущим фильтрам обычных вузов не найдено" in js
    assert "В этом фильтре вариантов нет" in js
    assert "Пока здесь пусто" in js
    assert "Добавь 2–3 вуза к сравнению" in js
    assert "Проверь подключение или попробуй позже" in js


def test_mini_app_uses_clean_financing_study_form_and_contest_labels() -> None:
    html = read_mini_app_file("index.html")
    js = read_mini_app_file("app.js")

    assert "Финансирование" in html
    assert "Форма обучения" in html
    assert "Конкурс" in html
    assert "Тип обучения" not in html
    assert "Тип конкурса" not in html
    assert "Финансирование:" in js
    assert "Форма обучения:" in js
    assert "Конкурс: бюджет" not in js
    assert "общий конкурс" in js
    assert "function getContestLabel" in js


def test_mini_app_uses_postgres_aware_copy_and_expanded_result_limit() -> None:
    html = read_mini_app_file("index.html")
    js = read_mini_app_file("app.js")

    assert "до 12 программ" in html
    assert "MINI_APP_RESULT_LIMIT = 12" in js
    assert "limit: String(MINI_APP_RESULT_LIMIT)" in js
    assert "PostgreSQL-база проекта" in js
    assert "Источник данных: JSON fallback" in js
    assert "formatDirectoryCount" in js
    assert "показано ${loadedCount} из ${totalCount}" in js
    assert "Поиск по коду или названию работает по полной базе" in js
    assert "Подсказки ищутся по полному справочнику PostgreSQL" in html
    assert "Начни вводить код или название" in js
    assert "Ничего не найдено. Попробуй код" in js
    assert "backend" not in html
    assert "временная демонстрационная база" not in html
    assert "будут заменены" not in html


def test_mini_app_has_custom_direction_picker_keyboard_and_clear_button() -> None:
    html = read_mini_app_file("index.html")
    js = read_mini_app_file("app.js")
    css = read_mini_app_file("styles.css")

    assert "direction-picker" in html
    assert "direction-clear" in html
    assert "Очистить направление" in html
    assert "aria-autocomplete=\"list\"" in html
    assert "aria-expanded=\"false\"" in html
    assert "handleDirectionPickerKeydown" in js
    assert "ArrowDown" in js
    assert "ArrowUp" in js
    assert "Escape" in js
    assert "Enter" in js
    assert "data-direction-suggestion" in js
    assert "direction-picker__dropdown" in css
    assert "direction-picker__clear" in css
    assert "direction-picker__code" in css
    assert "max-height: min(340px, 46vh)" in css


def test_styles_include_ux_blocks_toasts_and_dark_support() -> None:
    css = read_mini_app_file("styles.css")

    assert ".quick-start" in css
    assert ".quick-scenario" in css
    assert ".example-panel" in css
    assert ".field-helper" in css
    assert ".form-actions" in css
    assert ".empty-state" in css
    assert ".how-to-card" in css
    assert ".toast-container" in css
    assert ".toast--success" in css
    assert ".toast--warning" in css
    assert ".toast--error" in css
    assert "--toast-info" in css
    assert '[data-theme="dark"]' in css
    assert "@media" in css
