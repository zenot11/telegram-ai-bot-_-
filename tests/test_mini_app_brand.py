from pathlib import Path


MINI_APP_DIR = Path("mini_app")


def read_mini_app_file(name: str) -> str:
    return (MINI_APP_DIR / name).read_text(encoding="utf-8")


def test_index_contains_animated_aisha_brand_logo() -> None:
    html = read_mini_app_file("index.html")

    assert "aisha-brand-logo" in html
    assert 'aria-label="Aisha"' in html
    assert "brand-letter-a" in html
    assert "brand-letter-i" in html
    assert "brand-letter-s" in html
    assert "brand-letter-h" in html
    assert "brand-letter-a2" in html
    assert "--letter-index: 0" in html
    assert "--letter-index: 4" in html
    assert "fonts.googleapis" not in html
    assert "cdn" not in html.lower()


def test_styles_define_brand_animation_without_external_fonts() -> None:
    css = read_mini_app_file("styles.css")

    assert ".aisha-brand-logo" in css
    assert ".brand-letter" in css
    assert "@keyframes aishaLetterIn" in css
    assert "Georgia" in css
    assert "ui-serif" in css
    assert "--aisha-brand" in css
    assert "--aisha-glow" in css
    assert "prefers-reduced-motion" in css
    assert '[data-theme="dark"]' in css
    assert "@import url" not in css
    assert "@font-face" not in css
    assert "fonts.googleapis" not in css


def test_brand_app_js_does_not_expose_secrets_or_init_data() -> None:
    js = read_mini_app_file("app.js")

    assert "TELEGRAM_BOT_TOKEN" not in js
    assert "OPENAI_API_KEY" not in js
    assert "console.log(initData)" not in js
