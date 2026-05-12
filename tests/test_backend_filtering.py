from backend_stub.main import filter_universities, load_universities, normalize_type
from telegram_bot.services.recommendation import AMBITIOUS_SCORE_MARGIN


def test_adygea_it_budget_returns_results() -> None:
    results = filter_universities(load_universities(), "Адыгея", 230, "IT", "бюджет")

    assert len(results) >= 1
    assert all(item["region"] == "Адыгея" for item in results)
    assert all(item["type"] == "бюджет" for item in results)


def test_low_score_does_not_return_programs_above_ambitious_margin() -> None:
    score = 170
    results = filter_universities(load_universities(), "Адыгея", score, "IT", "бюджет")

    assert results
    assert all(item["min_score"] <= score + AMBITIOUS_SCORE_MARGIN for item in results)


def test_returns_program_slightly_above_score_within_ambitious_margin() -> None:
    rows = [
        {
            "region": "Адыгея",
            "direction": "IT",
            "program": "Амбициозная программа",
            "directions": ["IT"],
            "min_score": 240,
            "type": "бюджет",
        }
    ]

    results = filter_universities(rows, "Адыгея", 230, "IT", "бюджет")

    assert len(results) == 1
    assert results[0]["min_score"] == 240


def test_does_not_return_program_above_ambitious_margin() -> None:
    rows = [
        {
            "region": "Адыгея",
            "direction": "IT",
            "program": "Пока недоступная программа",
            "directions": ["IT"],
            "min_score": 260,
            "type": "бюджет",
        }
    ]

    results = filter_universities(rows, "Адыгея", 230, "IT", "бюджет")

    assert results == []


def test_ayti_direction_finds_it() -> None:
    results = filter_universities(load_universities(), "Адыгея", 230, "айти", "бюджет")

    assert results
    assert all(item["direction"] == "IT" for item in results)


def test_informatics_direction_finds_it() -> None:
    results = filter_universities(load_universities(), "Адыгея", 230, "информатика", "бюджет")

    assert results
    assert all(item["direction"] == "IT" for item in results)


def test_lawyer_direction_finds_law_programs() -> None:
    results = filter_universities(load_universities(), "Москва", 260, "юрист", "контракт")

    assert results
    assert all(item["direction"] == "юриспруденция" for item in results)
    assert all(item["type"] == "платное" for item in results)


def test_med_direction_finds_medicine_programs() -> None:
    results = filter_universities(load_universities(), "Татарстан", 250, "мед", "бюджет")

    assert results
    assert all(item["direction"] == "медицина" for item in results)


def test_budget_type_normalization() -> None:
    assert normalize_type("Бюджет") == "бюджет"
    assert normalize_type("бюджетное") == "бюджет"
    assert normalize_type("budget") == "бюджет"


def test_paid_type_normalization() -> None:
    assert normalize_type("Платное") == "платное"
    assert normalize_type("контракт") == "платное"
    assert normalize_type("paid") == "платное"


def test_limit_restricts_results_count() -> None:
    results = filter_universities(load_universities(), "Адыгея", 230, "IT", "Бюджет", limit=2)

    assert len(results) <= 2


def test_search_does_not_return_unavailable_programs() -> None:
    score = 220
    results = filter_universities(load_universities(), "Крым", score, "туризм", "бюджет")

    assert results
    assert all(item["min_score"] <= score + AMBITIOUS_SCORE_MARGIN for item in results)


def test_unknown_region_returns_empty_list() -> None:
    results = filter_universities(load_universities(), "Неизвестный регион", 300, "IT", "budget")

    assert results == []
