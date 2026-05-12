from telegram_bot.handlers.search import _format_university_card


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
            "note": "Демонстрационные данные для MVP",
        },
        230,
    )

    assert "Стоимость: не указана" in text
    assert "Форма: очная" in text
    assert "Срок: 4 года" in text
    assert "Пометка: Демонстрационные данные для MVP" in text
