from pathlib import Path


MINI_APP_DIR = Path("mini_app")


def read_mini_app_file(name: str) -> str:
    return (MINI_APP_DIR / name).read_text(encoding="utf-8")


def test_mini_app_files_exist() -> None:
    assert (MINI_APP_DIR / "index.html").exists()
    assert (MINI_APP_DIR / "styles.css").exists()
    assert (MINI_APP_DIR / "app.js").exists()


def test_index_contains_aisha_and_search_form() -> None:
    html = read_mini_app_file("index.html")

    assert "Аиша" in html
    assert "<form" in html
    assert "Подобрать варианты" in html
    assert "region" in html
    assert "score" in html
    assert "direction" in html


def test_app_js_uses_backend_api_without_openai_key() -> None:
    js = read_mini_app_file("app.js")

    assert "/api/universities" in js
    assert "OPENAI_API_KEY" not in js
    assert "Backend-заглушка недоступна" in js


def test_styles_include_recommendation_categories() -> None:
    css = read_mini_app_file("styles.css")

    assert ".badge.safe" in css
    assert ".badge.realistic" in css
    assert ".badge.ambitious" in css


def test_index_mentions_demo_data_warning() -> None:
    html = read_mini_app_file("index.html")

    assert "Данные демонстрационные" in html
    assert "не гарантия поступления" in html
