from telegram_bot.services.compare import (
    compare_universities,
    format_comparison,
    get_max_score_ambitious_option,
    get_min_score_safe_option,
)


def university(name: str, min_score: int | None, price: int | None = None) -> dict:
    return {
        "university": name,
        "city": "Майкоп",
        "program": "Прикладная информатика",
        "direction": "IT",
        "subjects": ["русский язык", "математика", "информатика"],
        "min_score": min_score,
        "type": "бюджет" if price is None else "платное",
        "price": price,
        "url": "https://example.ru",
    }


def test_compare_does_not_fail_on_empty_data() -> None:
    result = compare_universities([])
    text = format_comparison([])

    assert result["items"] == []
    assert result["has_enough_items"] is False
    assert "минимум два варианта" in text


def test_safe_option_has_lower_min_score() -> None:
    items = [university("АГУ", 185), university("МГТУ", 172)]

    assert get_min_score_safe_option(items)["university"] == "МГТУ"


def test_ambitious_option_has_higher_min_score() -> None:
    items = [university("АГУ", 185), university("МГТУ", 172)]

    assert get_max_score_ambitious_option(items)["university"] == "АГУ"


def test_formatted_text_contains_university_names() -> None:
    text = format_comparison([university("АГУ", 185), university("МГТУ", 172)])

    assert "АГУ" in text
    assert "МГТУ" in text


def test_formatted_text_contains_safe_conclusion() -> None:
    text = format_comparison([university("АГУ", 185), university("МГТУ", 172)])

    assert "безопасный" in text


def test_formatted_text_contains_demo_warning() -> None:
    text = format_comparison([university("АГУ", 185), university("МГТУ", 172)])

    assert "Данные демонстрационные" in text


def test_missing_price_is_rendered_as_not_specified() -> None:
    text = format_comparison([university("АГУ", 185), university("МГТУ", 172)])

    assert "Стоимость: не указана" in text


def test_single_university_explains_need_for_two_options() -> None:
    text = format_comparison([university("АГУ", 185)])

    assert "минимум два варианта" in text
