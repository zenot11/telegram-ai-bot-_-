from telegram_bot.handlers.search import _format_university_card, _get_result_by_number


def test_search_card_hides_missing_price_and_renders_available_metadata() -> None:
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
            "note": "контекст источника",
            "year": 2025,
            "faculty": "Факультет цифровых технологий",
            "admission_type": "target",
            "source": "postgresql",
        },
        230,
    )

    assert "Стоимость:" not in text
    assert "Форма обучения: очная" in text
    assert "Срок: 4 года" in text
    assert "Факультет: Факультет цифровых технологий" in text
    assert "Год данных: 2025" in text
    assert "Конкурс: целевая квота" in text
    assert "Пометка: контекст источника" in text
    assert "source" not in text
    assert "postgresql" not in text
    assert "🎓 <b>1. АГУ — Прикладная информатика</b>" in text
    assert "📍 Майкоп" in text
    assert "🟢 Категория: безопасный вариант" in text
    assert "📚 Предметы: русский язык, математика, информатика" in text
    assert "📊 Проходной балл: 185" in text
    assert "✅ Твои баллы: 230" in text
    assert "➕ Запас: +45" in text
    assert "🎯 Финансирование: бюджет" in text
    assert "Конкурс: бюджет" not in text


def test_search_card_does_not_duplicate_same_city_and_region() -> None:
    text = _format_university_card(
        1,
        {
            "university": "Московский тестовый вуз",
            "city": "Москва",
            "region": "Москва",
            "program": "Программная инженерия",
            "min_score": 240,
            "type": "платное",
        },
        276,
    )

    assert "📍 Москва" in text
    assert "Москва, Москва" not in text


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
            "source": "postgresql",
        },
        230,
    )

    assert "None" not in text
    assert "null" not in text
    assert "undefined" not in text
    assert "Сайт: None" not in text
    assert "source" not in text
    assert "postgresql" not in text


def test_search_card_hides_empty_subjects_duration_and_note() -> None:
    text = _format_university_card(
        1,
        {
            "university": "Тестовый вуз",
            "city": "Москва",
            "program": "Информатика",
            "subjects": [],
            "min_score": 220,
            "type": "бюджет",
            "price": "",
            "duration": "",
            "note": "",
        },
        230,
    )

    assert "Предметы:" not in text
    assert "Стоимость:" not in text
    assert "Срок:" not in text
    assert "Пометка:" not in text
    assert "[]" not in text


def test_search_card_does_not_show_invalid_score_as_gap() -> None:
    text = _format_university_card(
        1,
        {
            "university": "Тестовый вуз",
            "city": "Москва",
            "program": "Информатика",
            "subjects": [],
            "min_score": 0,
            "type": "бюджет",
            "admission_type_label": "отдельная квота",
            "year": 2025,
            "note": "отдельная квота",
        },
        280,
    )

    assert "Проходной балл: 0" not in text
    assert "Проходной балл: не указан" in text
    assert "Запас: +280" not in text
    assert "Категория: безопасный вариант" not in text
    assert "Конкурс: отдельная квота" in text
    assert "Год данных: 2025" in text
    assert "Пометка: отдельная квота" in text


def test_can_select_fourth_and_fifth_search_result() -> None:
    results = [{"university": f"Вуз {index}"} for index in range(1, 6)]

    assert _get_result_by_number(results, 4) == {"university": "Вуз 4"}
    assert _get_result_by_number(results, 5) == {"university": "Вуз 5"}


def test_can_select_second_page_search_result_by_global_number() -> None:
    page_results = [{"university": f"Вуз {index}"} for index in range(6, 11)]

    assert _get_result_by_number(page_results, 6, start_index=6) == {"university": "Вуз 6"}
    assert _get_result_by_number(page_results, 10, start_index=6) == {"university": "Вуз 10"}
    assert _get_result_by_number(page_results, 5, start_index=6) is None


def test_missing_search_result_number_returns_none() -> None:
    results = [{"university": "Вуз 1"}]

    assert _get_result_by_number(results, 2) is None
    assert _get_result_by_number(results, 0) is None
