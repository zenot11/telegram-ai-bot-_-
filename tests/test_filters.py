from telegram_bot.services.filters import (
    FILTER_ALL,
    FILTER_AMBITIOUS,
    FILTER_BUDGET,
    FILTER_PAID,
    FILTER_REALISTIC,
    FILTER_SAFE,
    build_filtered_results_message,
    build_filters_overview_message,
    filter_results,
    get_filter_counts,
)


def profile(score: int = 230) -> dict:
    return {
        "region": "Адыгея",
        "score": score,
        "direction": "IT",
        "education_type": "budget",
    }


def university(name: str, min_score: int, education_type: str = "бюджет") -> dict:
    return {
        "university": name,
        "city": "Майкоп",
        "program": "Прикладная информатика",
        "direction": "IT",
        "subjects": ["русский язык", "математика", "информатика"],
        "min_score": min_score,
        "type": education_type,
        "price": None,
        "url": "https://example.ru",
    }


def sample_results() -> list[dict]:
    return [
        university("Безопасный вуз", 180, "бюджет"),
        university("Реалистичный вуз", 225, "бюджет"),
        university("Амбициозный вуз", 240, "платное"),
    ]


def test_filter_all_returns_all_results() -> None:
    results = sample_results()

    assert filter_results(results, FILTER_ALL, 230) == results


def test_filter_safe_returns_safe_results() -> None:
    filtered = filter_results(sample_results(), FILTER_SAFE, 230)

    assert len(filtered) == 1
    assert filtered[0]["university"] == "Безопасный вуз"


def test_filter_realistic_returns_realistic_results() -> None:
    filtered = filter_results(sample_results(), FILTER_REALISTIC, 230)

    assert len(filtered) == 1
    assert filtered[0]["university"] == "Реалистичный вуз"


def test_filter_ambitious_returns_ambitious_results() -> None:
    filtered = filter_results(sample_results(), FILTER_AMBITIOUS, 230)

    assert len(filtered) == 1
    assert filtered[0]["university"] == "Амбициозный вуз"


def test_filter_budget_returns_budget_results() -> None:
    filtered = filter_results(sample_results(), FILTER_BUDGET, 230)

    assert len(filtered) == 2
    assert all(item["type"] == "бюджет" for item in filtered)


def test_filter_paid_returns_paid_results() -> None:
    filtered = filter_results(sample_results(), FILTER_PAID, 230)

    assert len(filtered) == 1
    assert filtered[0]["type"] == "платное"


def test_empty_results_are_safe_to_format() -> None:
    text = build_filtered_results_message(profile(), [], [], FILTER_PAID)

    assert "Найдено: 0 из 0" in text
    assert "вариантов нет" in text
    assert "None" not in text
    assert "null" not in text


def test_filter_counts() -> None:
    counts = get_filter_counts(sample_results(), 230)

    assert counts[FILTER_ALL] == 3
    assert counts[FILTER_SAFE] == 1
    assert counts[FILTER_REALISTIC] == 1
    assert counts[FILTER_AMBITIOUS] == 1
    assert counts[FILTER_BUDGET] == 2
    assert counts[FILTER_PAID] == 1


def test_filter_message_escapes_html_values() -> None:
    rows = [university("<Вуз>", 180)]
    rows[0]["program"] = "<Программа>"
    text = build_filtered_results_message(profile(), rows, rows, FILTER_ALL)

    assert "&lt;Вуз&gt;" in text
    assert "&lt;Программа&gt;" in text
    assert "<Вуз>" not in text


def test_filters_overview_message_contains_counts() -> None:
    text = build_filters_overview_message(profile(), sample_results())

    assert "Фильтры результатов" in text
    assert "Безопасные: 1" in text
    assert "Реалистичные: 1" in text
    assert "Амбициозные: 1" in text
    assert "Бюджет: 2" in text
    assert "Платное: 1" in text
