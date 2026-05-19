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
    assert "Избранное" in html
    assert "О проекте" in html
    assert "Итог подбора" in html
    assert "theme-toggle" in html
    assert "Переключить тему" in html
    assert "<form" in html
    assert "Подобрать варианты" in html
    assert "region" in html
    assert "score" in html
    assert "direction" in html
    assert "/miniapp/styles.css" in html
    assert "/miniapp/app.js" in html


def test_app_js_uses_backend_api_without_openai_key() -> None:
    js = read_mini_app_file("app.js")

    assert "/api/universities" in js
    assert "OPENAI_API_KEY" not in js
    assert "Backend-заглушка недоступна" in js


def test_app_js_has_local_filters_and_favorites() -> None:
    js = read_mini_app_file("app.js")

    assert "localStorage" in js
    assert "lastResults" in js
    assert "activeFilter" in js
    assert "function filterResults" in js
    assert "function addToFavorites" in js
    assert "function removeFromFavorites" in js
    assert "function clearFavorites" in js
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

    assert "демонстрационный прототип" in html
    assert "будут заменены" in html


def test_mini_app_user_texts_do_not_use_mvp_label() -> None:
    combined = "\n".join(
        read_mini_app_file(name)
        for name in ("index.html", "styles.css", "app.js", "favicon.svg")
    )

    assert "MVP" not in combined
