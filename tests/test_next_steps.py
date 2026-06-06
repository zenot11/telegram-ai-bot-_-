from telegram_bot.services.next_steps import build_next_steps_text


DEV_ONLY_TERMS = (
    "universities.json",
    "OPENAI_API_KEY",
    "WEBAPP_URL",
    "ngrok",
    "backend",
    ".env",
    "перед финальной сдачей",
    "финальные данные будут подставлены",
)


def test_next_steps_without_results_asks_to_search_first() -> None:
    text = build_next_steps_text(None, [])

    assert "Сначала выполни подбор вузов" in text
    assert "/search" in text
    assert all(term not in text for term in DEV_ONLY_TERMS)


def test_next_steps_with_results_contains_user_actions() -> None:
    text = build_next_steps_text(
        {
            "region": "Адыгея",
            "score": 230,
            "direction": "IT",
            "education_type": "budget",
        },
        [{"university": "АГУ", "program": "IT"}],
    )

    assert "Сохрани 2–3 подходящих вуза" in text
    assert "Сравни безопасные и реалистичные варианты" in text
    assert "Проверь официальные сайты вузов" in text
    assert "Mini App" in text
    assert "/export" in text
    assert "/feedback" in text
    assert all(term not in text for term in DEV_ONLY_TERMS)


def test_next_steps_escapes_profile_values() -> None:
    text = build_next_steps_text(
        {
            "region": "<Адыгея>",
            "score": 230,
            "direction": "IT & дизайн",
            "education_type": "paid",
        },
        [{"university": "АГУ"}],
    )

    assert "&lt;Адыгея&gt;" in text
    assert "IT &amp; дизайн" in text
    assert "Платное" in text


def test_next_steps_formats_any_financing_label() -> None:
    text = build_next_steps_text(
        {
            "region": "Москва",
            "score": 290,
            "direction": "IT",
            "education_type": "any",
        },
        [{"university": "Тестовый вуз"}],
    )

    assert "Любое" in text
    assert "any" not in text
