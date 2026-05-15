from telegram_bot.handlers.search import _format_university_card, _get_result_by_number


def test_search_card_renders_missing_price_as_not_specified() -> None:
    text = _format_university_card(
        1,
        {
            "university": "АГУ",
            "city": "Майкоп",
            "program": "Прикладная информатика",
            "subjects": ["русский язык", "математика", "информатика"],
            "min_score": 185,
            "type": "бюджет",
            "price": None,
            "url": "https://www.adygnet.ru",
            "study_form": "очная",
            "duration": "4 года",
            "note": "демонстрационные данные",
        },
        230,
    )

    assert "Стоимость: не указана" in text
    assert "Форма: очная" in text
    assert "Срок: 4 года" in text
    assert "Пометка: демонстрационные данные" in text
    assert "🎓 <b>1. АГУ — Прикладная информатика</b>" in text
    assert "📍 Город: Майкоп" in text
    assert "🟢 Категория: безопасный вариант" in text
    assert "📚 Предметы: русский язык, математика, информатика" in text
    assert "📊 Мин. балл: 185" in text
    assert "✅ Твои баллы: 230" in text
    assert "➕ Запас: +45" in text
    assert "🎯 Тип: бюджет" in text


def test_search_card_does_not_render_none_or_null_values() -> None:
    text = _format_university_card(
        1,
        {
            "university": "Тестовый вуз",
            "city": "Майкоп",
            "program": "Прикладная информатика",
            "subjects": ["математика"],
            "min_score": 185,
            "type": "бюджет",
            "price": None,
            "url": None,
            "study_form": None,
            "duration": None,
        },
        230,
    )

    assert "None" not in text
    assert "null" not in text
    assert "Сайт: None" not in text


def test_can_select_fourth_and_fifth_search_result() -> None:
    results = [{"university": f"Вуз {index}"} for index in range(1, 6)]

    assert _get_result_by_number(results, 4) == {"university": "Вуз 4"}
    assert _get_result_by_number(results, 5) == {"university": "Вуз 5"}


def test_missing_search_result_number_returns_none() -> None:
    results = [{"university": "Вуз 1"}]

    assert _get_result_by_number(results, 2) is None
    assert _get_result_by_number(results, 0) is None
