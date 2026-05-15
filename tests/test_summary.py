from telegram_bot.services.summary import (
    EMPTY_SUMMARY_TEXT,
    count_categories,
    format_last_search_summary,
    format_search_brief_summary,
)


def university(name: str, min_score: int) -> dict:
    return {
        "university": name,
        "city": "Майкоп",
        "program": "Прикладная информатика",
        "direction": "IT",
        "subjects": ["русский язык", "математика", "информатика"],
        "min_score": min_score,
        "type": "бюджет",
        "price": None,
        "url": "https://example.ru",
    }


def profile() -> dict:
    return {
        "region": "Адыгея",
        "score": 230,
        "direction": "IT",
        "education_type": "budget",
    }


def test_empty_summary_explains_no_last_search() -> None:
    text = format_last_search_summary(None, [], 0)

    assert text == EMPTY_SUMMARY_TEXT
    assert "Пока нет последнего подбора" in text


def test_summary_contains_profile_fields_and_total_count() -> None:
    text = format_last_search_summary(profile(), [university("АГУ", 185), university("МГТУ", 225)], 0)

    assert "Регион: Адыгея" in text
    assert "Баллы: 230" in text
    assert "Направление: IT" in text
    assert "Тип обучения: бюджет" in text
    assert "Найдено вариантов: 2" in text


def test_summary_counts_recommendation_categories() -> None:
    items = [university("АГУ", 185), university("МГТУ", 220), university("КГУ", 240)]

    assert count_categories(items, 230) == {
        "safe": 1,
        "realistic": 1,
        "ambitious": 1,
    }

    text = format_search_brief_summary(items, 230)
    assert "🟢 Безопасные: 1" in text
    assert "🟡 Реалистичные: 1" in text
    assert "🔴 Амбициозные: 1" in text


def test_summary_shows_top_results_and_favorites_count() -> None:
    items = [
        university("АГУ", 185),
        university("МГТУ", 225),
        university("КГУ", 240),
        university("Тестовый вуз", 210),
    ]

    text = format_last_search_summary(profile(), items, favorites_count=2)

    assert "1. АГУ — Прикладная информатика" in text
    assert "2. МГТУ — Прикладная информатика" in text
    assert "3. КГУ — Прикладная информатика" in text
    assert "Тестовый вуз" not in text
    assert "Избранное: 2 вуза" in text


def test_summary_does_not_render_none_or_null() -> None:
    text = format_last_search_summary(profile(), [university("АГУ", 185)], 0)

    assert "None" not in text
    assert "null" not in text
