from pathlib import Path


MINI_APP_DIR = Path("mini_app")


def read_mini_app_file(name: str) -> str:
    return (MINI_APP_DIR / name).read_text(encoding="utf-8")


def test_mini_app_files_exist() -> None:
    assert (MINI_APP_DIR / "index.html").exists()
    assert (MINI_APP_DIR / "styles.css").exists()
    assert (MINI_APP_DIR / "app.js").exists()
    assert (MINI_APP_DIR / "favicon.svg").exists()


def test_index_contains_aisha_and_search_form() -> None:
    html = read_mini_app_file("index.html")

    assert "Аиша" in html
    assert "Построй будущее уже сегодня" in html
    assert "Привет, я Аиша" in html
    assert "Главная" in html
    assert "Подбор" in html
    assert "Фильтры" in html
    assert "Сравнение" in html
    assert "Избранное" in html
    assert "План" in html
    assert "Экспорт" in html
    assert "Поддержка" in html
    assert "О проекте" in html
    assert "Итог подбора" in html
    assert "theme-toggle" in html
    assert "Переключить тему" in html
    assert "<form" in html
    assert "Подобрать варианты" in html
    assert "region" in html
    assert "score" in html
    assert "direction" in html
    assert 'list="direction-options"' in html
    assert "direction-options" in html
    assert "city" in html
    assert "study-form" in html
    assert "admission-type" in html
    assert "directory-status" in html
    assert "/miniapp/styles.css" in html
    assert "/miniapp/app.js" in html


def test_app_js_uses_backend_api_without_openai_key() -> None:
    js = read_mini_app_file("app.js")

    assert "/api/universities" in js
    assert "/api/regions" in js
    assert "/api/cities" in js
    assert "/api/directions" in js
    assert "/api/study-forms" in js
    assert "/api/admission-types" in js
    assert "/api/achievements" in js
    assert "OPENAI_API_KEY" not in js
    assert "Не удалось получить данные" in js


def test_mini_app_uses_postgres_first_directories_and_alias_presets() -> None:
    js = read_mini_app_file("app.js")

    assert "directoryState" in js
    assert "PostgreSQL-база проекта" in js
    assert "Источник данных: JSON fallback" in js
    assert "formatDirectoryCount" in js
    assert "formatDirectionsDirectoryCount" in js
    assert "refreshDirectionSuggestions" in js
    assert "/api/directions?" in js
    assert "fetchDirectoryPayload" in js
    assert "normalizeDirectionForSearch" in js
    assert 'direction: "информационные технологии"' in js
    assert 'direction: "IT"' not in js
    assert 'value="IT"' not in read_mini_app_file("index.html")


def test_mini_app_has_empty_state_suggestions_and_achievements() -> None:
    js = read_mini_app_file("app.js")

    assert "renderEmptySearchState" in js
    assert "Точных совпадений не найдено" in js
    assert "Убрать необязательные фильтры" in js
    assert "Индивидуальные достижения" in js
    assert "renderAchievementsBlock" in js


def test_mini_app_has_score_quality_helpers_and_split_card_title() -> None:
    js = read_mini_app_file("app.js")
    css = read_mini_app_file("styles.css")

    assert "function hasValidMinScore" in js
    assert "function getScoreDisplay" in js
    assert "function getScoreClarification" in js
    assert "балл требует уточнения" in js
    assert "result-card__program" in js
    assert ".result-card__program" in css
    assert ".badge.unavailable" in css
    assert "Проходной балл: 0" not in js
    assert "Проходной балл: 1" not in js
    assert "Запас: +279" not in js


def test_app_js_has_local_filters_and_favorites() -> None:
    js = read_mini_app_file("app.js")

    assert "localStorage" in js
    assert "lastResults" in js
    assert "activeFilter" in js
    assert "function filterResults" in js
    assert "function addToFavorites" in js
    assert "function removeFromFavorites" in js
    assert "function clearFavorites" in js
    assert "X-Telegram-Init-Data" in js
    assert "/api/favorites" in js
    assert "aisha_favorites" in js
    assert "function initFavoritesSync" in js
    assert "function requestFavoritesApi" in js
    assert "Браузер: избранное хранится только в этом браузере" in js
    assert "window.Telegram && window.Telegram.WebApp" in js


def test_app_js_has_theme_toggle_without_tokens() -> None:
    js = read_mini_app_file("app.js")

    assert "aisha_theme" in js
    assert "function initTheme" in js
    assert "function applyTheme" in js
    assert "function toggleTheme" in js
    assert "dataset.theme" in js
    assert "TELEGRAM_BOT_TOKEN" not in js


def test_styles_include_recommendation_categories() -> None:
    css = read_mini_app_file("styles.css")

    assert ".badge.safe" in css
    assert ".badge.realistic" in css
    assert ".badge.ambitious" in css
    assert ".badge.unavailable" in css


def test_styles_include_light_site_layout_classes() -> None:
    css = read_mini_app_file("styles.css")

    assert ".hero-section" in css
    assert ".assistant-card" in css
    assert ".search-form" in css
    assert ".result-card" in css
    assert ".results-grid" in css
    assert ".tabs" in css
    assert ".tab-button" in css
    assert ".filter-chip" in css
    assert ".favorite-button" in css
    assert "@media" in css


def test_styles_include_theme_variables_and_dark_theme() -> None:
    css = read_mini_app_file("styles.css")

    assert "--background" in css
    assert "--surface" in css
    assert "--text" in css
    assert "--primary" in css
    assert '[data-theme="dark"]' in css
    assert ".theme-toggle" in css


def test_index_mentions_demo_data_warning() -> None:
    html = read_mini_app_file("index.html")

    assert "учебный прототип" in html
    assert "Режим источника данных зависит от подключённой базы" in html


def test_mini_app_user_texts_do_not_use_mvp_label() -> None:
    combined = "\n".join(
        read_mini_app_file(name)
        for name in ("index.html", "styles.css", "app.js", "favicon.svg")
    )

    assert "MVP" not in combined
