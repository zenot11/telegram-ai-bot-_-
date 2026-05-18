from telegram_bot.services.advice import build_advice


def profile(
    region: str = "Адыгея",
    score: int = 230,
    direction: str = "IT",
    education_type: str = "budget",
) -> dict:
    return {
        "region": region,
        "score": score,
        "direction": direction,
        "education_type": education_type,
    }


def university(name: str = "АГУ", min_score: int = 185, direction: str = "IT") -> dict:
    return {
        "university": name,
        "city": "Майкоп",
        "program": "Прикладная информатика",
        "direction": direction,
        "subjects": ["русский язык", "математика", "информатика"],
        "min_score": min_score,
        "type": "бюджет",
        "price": None,
        "url": "https://example.ru",
    }


def test_advice_without_last_search_asks_to_search_first() -> None:
    text = build_advice(None, [])

    assert "Пока нет последнего подбора" in text
    assert "/search" in text


def test_advice_for_empty_results_suggests_changing_query() -> None:
    text = build_advice(profile(score=100), [])

    assert "Найдено вариантов: 0" in text
    assert "Проверь, правильно ли указаны баллы" in text
    assert "Попробуй соседний регион" in text
    assert "платное" in text
    assert "None" not in text
    assert "null" not in text


def test_advice_for_many_safe_options_says_search_is_calm() -> None:
    text = build_advice(profile(), [university("АГУ", 180), university("МГТУ", 190), university("КГУ", 200)])

    assert "достаточно спокойным" in text
    assert "запас" in text
    assert "Сохрани 1–2" in text
    assert "/compare" in text


def test_advice_for_only_ambitious_options_suggests_safer_routes() -> None:
    text = build_advice(profile(), [university("Амбициозный вуз", 240)])

    assert "больше амбициозный" in text
    assert "более спокойных" in text
    assert "соседний регион" in text


def test_advice_with_favorites_suggests_compare_favorites() -> None:
    text = build_advice(profile(), [university("АГУ", 185)], favorites=[university("АГУ", 185)])

    assert "Сравни избранные варианты через /compare" in text
    assert "Открой /compare" in text


def test_budget_with_few_results_suggests_paid_backup() -> None:
    text = build_advice(profile(education_type="budget"), [university("АГУ", 225)])

    assert "платное обучение" in text


def test_paid_advice_suggests_check_price_conditions() -> None:
    text = build_advice(profile(education_type="paid"), [university("АГУ", 225)])

    assert "Проверь стоимость" in text


def test_it_direction_advice_mentions_related_it_directions() -> None:
    text = build_advice(profile(direction="IT"), [university("АГУ", 185)])

    assert "информатику" in text
    assert "цифровые технологии" in text
    assert "программную инженерию" in text


def test_advice_escapes_user_profile_values() -> None:
    text = build_advice(
        profile(region="<Адыгея>", direction="<b>IT</b>"),
        [university("АГУ", 185)],
    )

    assert "&lt;Адыгея&gt;" in text
    assert "&lt;b&gt;IT&lt;/b&gt;" in text
    assert "<b>IT</b>" not in text


def test_advice_mentions_changing_scores_disclaimer() -> None:
    text = build_advice(profile(), [university("АГУ", 185)])

    assert "Проходные баллы могут меняться" in text
    assert "проверить информацию на сайте вуза" in text
