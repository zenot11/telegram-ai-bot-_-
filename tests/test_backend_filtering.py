from backend_stub.main import filter_universities, load_universities, normalize_type


def test_adygea_it_budget_returns_results() -> None:
    results = filter_universities(load_universities(), "Адыгея", 230, "IT", "бюджет")

    assert len(results) >= 1
    assert all(item["region"] == "Адыгея" for item in results)
    assert all(item["type"] == "бюджет" for item in results)


def test_low_score_does_not_return_programs_above_score() -> None:
    score = 170
    results = filter_universities(load_universities(), "Адыгея", score, "IT", "бюджет")

    assert results
    assert all(item["min_score"] <= score for item in results)


def test_ayti_direction_finds_it() -> None:
    results = filter_universities(load_universities(), "Адыгея", 230, "айти", "бюджет")

    assert results
    assert all(item["direction"] == "IT" for item in results)


def test_informatics_direction_finds_it() -> None:
    results = filter_universities(load_universities(), "Адыгея", 230, "информатика", "бюджет")

    assert results
    assert all(item["direction"] == "IT" for item in results)


def test_budget_type_normalization() -> None:
    assert normalize_type("Бюджет") == "бюджет"
    assert normalize_type("budget") == "бюджет"


def test_limit_restricts_results_count() -> None:
    results = filter_universities(load_universities(), "Адыгея", 230, "IT", "Бюджет", limit=2)

    assert len(results) <= 2


def test_unknown_region_returns_empty_list() -> None:
    results = filter_universities(load_universities(), "Неизвестный регион", 300, "IT", "budget")

    assert results == []
