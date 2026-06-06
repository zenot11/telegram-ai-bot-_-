import json
from pathlib import Path

import pytest

from backend_stub.data_loader import (
    DataLoadError,
    load_universities,
    normalize_university_record,
    validate_universities_data,
    validate_university_record,
)


def valid_record() -> dict:
    return {
        "university": " Тестовый университет ",
        "city": " Майкоп ",
        "region": " Адыгея ",
        "program": " Прикладная информатика ",
        "direction": " IT ",
        "subjects": [" русский язык ", "математика", "информатика"],
        "min_score": 230,
        "type": "бюджет",
        "price": None,
        "url": " https://example.ru ",
        "study_form": " очная ",
        "duration": "4 года",
        "note": " контекст источника ",
    }


def test_valid_record_has_no_errors() -> None:
    assert validate_university_record(valid_record(), 1) == []


def test_missing_required_field_is_reported() -> None:
    record = valid_record()
    record.pop("university")

    errors = validate_university_record(record, 12)

    assert 'Record #12: missing required field "university"' in errors


def test_min_score_must_be_integer() -> None:
    record = valid_record()
    record["min_score"] = "230"

    errors = validate_university_record(record, 1)

    assert 'Record #1: "min_score" must be integer' in errors


def test_subjects_must_be_list() -> None:
    record = valid_record()
    record["subjects"] = "русский язык, математика"

    errors = validate_university_record(record, 1)

    assert 'Record #1: "subjects" must be list of strings' in errors


def test_subjects_must_contain_strings() -> None:
    record = valid_record()
    record["subjects"] = ["русский язык", 123]

    errors = validate_university_record(record, 1)

    assert 'Record #1: "subjects" must be list of strings' in errors


def test_wrong_type_is_reported() -> None:
    record = valid_record()
    record["type"] = "очное"

    errors = validate_university_record(record, 1)

    assert 'Record #1: "type" must be "бюджет" or "платное"' in errors


@pytest.mark.parametrize(
    ("raw_type", "expected"),
    [
        ("budget", "бюджет"),
        ("paid", "платное"),
        ("контракт", "платное"),
        ("бесплатно", "бюджет"),
    ],
)
def test_normalize_university_record_normalizes_type(raw_type: str, expected: str) -> None:
    record = valid_record()
    record["type"] = raw_type

    normalized = normalize_university_record(record)

    assert normalized["type"] == expected
    assert normalized["university"] == "Тестовый университет"
    assert normalized["subjects"] == ["русский язык", "математика", "информатика"]


def test_validate_universities_data_requires_list() -> None:
    errors = validate_universities_data({"items": []})

    assert errors == ["Data must be a JSON array of university records"]


def test_validate_universities_data_rejects_empty_list() -> None:
    errors = validate_universities_data([])

    assert errors == ["Data must contain at least one university record"]


def test_load_universities_reads_temp_json(tmp_path: Path) -> None:
    data_path = tmp_path / "universities.json"
    data_path.write_text(json.dumps([valid_record()], ensure_ascii=False), encoding="utf-8")

    rows = load_universities(data_path)

    assert rows[0]["university"] == "Тестовый университет"
    assert rows[0]["type"] == "бюджет"


def test_load_universities_raises_readable_error_for_bad_data(tmp_path: Path) -> None:
    data_path = tmp_path / "universities.json"
    bad_record = valid_record()
    bad_record.pop("program")
    data_path.write_text(json.dumps([bad_record], ensure_ascii=False), encoding="utf-8")

    with pytest.raises(DataLoadError) as error:
        load_universities(data_path)

    assert 'missing required field "program"' in str(error.value)


def test_real_universities_json_passes_validation() -> None:
    rows = load_universities()

    assert rows
    assert not validate_universities_data(rows)
