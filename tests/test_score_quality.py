from backend_stub.university_repository import normalize_pg_record
from telegram_bot.services.recommendation import CATEGORY_UNAVAILABLE, classify_university, format_score_delta
from telegram_bot.services.scores import is_valid_score, score_delta_value, score_display


def test_score_quality_marks_zero_and_one_as_invalid() -> None:
    assert not is_valid_score(0)
    assert not is_valid_score(1)
    assert is_valid_score(185)


def test_score_gap_is_not_calculated_for_invalid_min_score() -> None:
    assert score_delta_value(280, 0) is None
    assert score_delta_value(280, 1) is None
    assert score_delta_value(280, 185) == 95
    assert format_score_delta(280, {"min_score": 0}) == "Запас по баллам: требует уточнения"


def test_invalid_min_score_does_not_become_safe_category() -> None:
    assert classify_university(280, {"min_score": 0}) == CATEGORY_UNAVAILABLE
    assert classify_university(280, {"min_score": 1}) == CATEGORY_UNAVAILABLE


def test_postgres_record_adds_score_display_fields() -> None:
    record = normalize_pg_record(
        {
            "university_name": "Тестовый университет",
            "direction_name": "Прикладная информатика",
            "min_score": 0,
            "admission_type": "separate_quota",
            "year": 2025,
            "note": "отдельная квота",
        }
    )

    assert record["min_score"] == 0
    assert record["score_is_valid"] is False
    assert record["score_display"] == "не указан"
    assert record["score_note"] == "балл требует уточнения"


def test_valid_score_display_is_numeric_text() -> None:
    assert score_display(185) == "185"
