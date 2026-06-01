import asyncio
import json

from backend_stub.data_loader import load_universities
from backend_stub.main import UNIVERSITIES_KEY, create_app, universities
from backend_stub.university_repository import normalize_pg_record
from telegram_bot.services.recommendation import AMBITIOUS_SCORE_MARGIN


REQUIRED_API_FIELDS = {
    "university",
    "city",
    "region",
    "program",
    "direction",
    "subjects",
    "min_score",
    "type",
    "url",
}

OPTIONAL_API_FIELDS = {
    "price",
    "study_form",
    "study_form_label",
    "financing_label",
    "contest_label",
    "duration",
    "note",
}


def test_json_and_postgres_records_share_legacy_api_contract() -> None:
    json_record = load_universities()[0]
    postgres_record = normalize_pg_record(
        {
            "university_name": "МГУ",
            "university_short_name": "МГУ",
            "city": "Москва",
            "region": "Москва",
            "direction_name": "Прикладная информатика",
            "subjects": None,
            "min_score": 250,
            "admission_type": "budget",
            "website": "https://example.ru",
            "study_form": "full_time",
            "year": 2025,
            "faculty_name": "Факультет вычислительной математики и кибернетики",
        }
    )

    assert REQUIRED_API_FIELDS.issubset(json_record)
    assert REQUIRED_API_FIELDS.union(OPTIONAL_API_FIELDS).issubset(postgres_record)
    assert isinstance(json_record["subjects"], list)
    assert isinstance(postgres_record["subjects"], list)
    assert postgres_record["type"] == "бюджет"
    assert postgres_record["financing_label"] == "бюджет"
    assert postgres_record["study_form"] == "очная"
    assert postgres_record["study_form_label"] == "очная"
    assert postgres_record["contest_label"] == "общий конкурс"


def test_postgres_record_exposes_extra_fields_without_breaking_legacy_fields() -> None:
    record = normalize_pg_record(
        {
            "university_name": "Университет",
            "city": "Город",
            "region": "Регион",
            "direction_name": "Программа",
            "admission_type": "target",
            "latest_year": 2024,
            "faculty_name": "Институт технологий",
        }
    )

    assert record["subjects"] == []
    assert record["price"] is None
    assert record["duration"] == ""
    assert record["year"] == 2024
    assert record["faculty"] == "Институт технологий"
    assert record["admission_type"] == "target"
    assert record["admission_type_label"] == "целевая квота"
    assert record["contest_label"] == "целевая квота"
    assert record["source"] == "postgresql"


def test_universities_endpoint_keeps_ambitious_score_margin(monkeypatch) -> None:
    monkeypatch.setenv("USE_POSTGRES", "false")
    score = 230
    app = create_app(
        universities_data=[
            _university("В пределах запаса", score + AMBITIOUS_SCORE_MARGIN),
            _university("Выше запаса", score + AMBITIOUS_SCORE_MARGIN + 1),
        ]
    )

    class Request:
        pass

    request = Request()
    request.app = app
    request.query = {
        "region": "Адыгея",
        "score": str(score),
        "direction": "IT",
        "type": "budget",
        "limit": "10",
        "sort": "min_score_desc",
    }
    response = asyncio.run(universities(request))
    payload = json.loads(response.text)

    assert response.status == 200
    assert [item["university"] for item in payload] == ["В пределах запаса"]
    assert payload[0]["min_score"] == score + AMBITIOUS_SCORE_MARGIN
    assert app[UNIVERSITIES_KEY]


def _university(name: str, min_score: int) -> dict:
    return {
        "university": name,
        "city": "Майкоп",
        "region": "Адыгея",
        "program": "Прикладная информатика",
        "direction": "IT",
        "directions": ["IT"],
        "subjects": ["русский язык", "математика", "информатика"],
        "min_score": min_score,
        "type": "бюджет",
        "price": None,
        "url": "https://example.ru",
        "study_form": "очная",
        "duration": "4 года",
        "note": "тест",
    }
