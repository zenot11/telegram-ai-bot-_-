import asyncio
import json
from pathlib import Path

from backend_stub.main import (
    STORAGE_KEY,
    UNIVERSITIES_KEY,
    admission_types,
    cities,
    create_app,
    directions,
    health,
    regions,
    study_forms,
    universities,
)
from backend_stub.university_repository import normalize_limit, normalize_pg_record, normalize_type


def test_json_fallback_is_default(monkeypatch) -> None:
    monkeypatch.delenv("USE_POSTGRES", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)

    app = create_app()

    assert app[STORAGE_KEY] == "json"
    assert app[UNIVERSITIES_KEY]


def test_use_postgres_false_does_not_require_database_url(monkeypatch) -> None:
    monkeypatch.setenv("USE_POSTGRES", "false")
    monkeypatch.delenv("DATABASE_URL", raising=False)

    app = create_app()

    assert app[STORAGE_KEY] == "json"
    assert app[UNIVERSITIES_KEY]


def test_env_example_contains_postgres_settings() -> None:
    content = Path(".env.example").read_text(encoding="utf-8")

    assert "USE_POSTGRES=false" in content
    assert "DATABASE_URL=postgresql://postgres:postgres@localhost:5432/tgbot" in content
    assert "USE_POSTGRES_TESTS=false" in content


def test_normalize_type_supports_postgres_and_russian_variants() -> None:
    assert normalize_type("budget") == "бюджет"
    assert normalize_type("paid") == "платное"
    assert normalize_type("бюджет") == "бюджет"
    assert normalize_type("платное") == "платное"
    assert normalize_type("контракт") == "платное"
    assert normalize_type("договор") == "платное"
    assert normalize_type("target") == "бюджет"


def test_limit_is_clamped_to_maximum() -> None:
    assert normalize_limit("999") == 200
    assert normalize_limit("bad") == 5


def test_normalize_pg_record_returns_api_contract_fields() -> None:
    row = {
        "university": "МГУ",
        "city": "Москва",
        "region": "Москва",
        "program": "Прикладная информатика",
        "direction": "Прикладная информатика",
        "subjects": "русский язык, математика, информатика",
        "min_score": "250",
        "type": "budget",
        "url": "https://www.msu.ru",
        "study_form": "full_time",
        "note": None,
    }

    record = normalize_pg_record(row)

    assert record["university"] == "МГУ"
    assert record["city"] == "Москва"
    assert record["region"] == "Москва"
    assert record["program"] == "Прикладная информатика"
    assert record["direction"] == "Прикладная информатика"
    assert record["subjects"] == ["русский язык", "математика", "информатика"]
    assert record["min_score"] == 250
    assert record["type"] == "бюджет"
    assert record["url"] == "https://www.msu.ru"
    assert record["study_form"] == "очная"
    assert record["duration"] == ""
    assert record["note"] == ""
    assert record["year"] is None
    assert record["source"] == "postgresql"


def test_normalize_pg_record_handles_missing_optional_fields() -> None:
    record = normalize_pg_record(
        {
            "university_name": "Университет",
            "city": None,
            "region": "Регион",
            "direction_name": "Программа",
            "min_score": None,
            "admission_type": "paid",
        }
    )

    assert record["university"] == "Университет"
    assert record["city"] == ""
    assert record["region"] == "Регион"
    assert record["program"] == "Программа"
    assert record["direction"] == "Программа"
    assert record["subjects"] == []
    assert record["min_score"] == 0
    assert record["type"] == "платное"
    assert record["url"] == ""
    assert record["price"] is None
    assert record["study_form"] == ""
    assert record["duration"] == ""
    assert record["note"] == ""


def test_health_json_mode_contains_storage(monkeypatch) -> None:
    monkeypatch.setenv("USE_POSTGRES", "false")
    app = create_app()

    class Request:
        pass

    request = Request()
    request.app = app
    response = asyncio.run(health(request))
    payload = json.loads(response.text)

    assert payload["status"] == "ok"
    assert payload["storage"] == "json"
    assert "features" in payload
    assert payload["data_source"] == "backend_stub/data/universities.json"
    assert payload["universities_count"] == len(app[UNIVERSITIES_KEY])


def test_api_universities_json_mode_keeps_contract(monkeypatch) -> None:
    monkeypatch.setenv("USE_POSTGRES", "false")
    app = create_app()

    class Request:
        pass

    request = Request()
    request.app = app
    request.query = {
        "region": "Адыгея",
        "score": "230",
        "direction": "IT",
        "type": "budget",
        "limit": "3",
    }
    response = asyncio.run(universities(request))
    payload = json.loads(response.text)

    assert response.status == 200
    assert payload
    assert len(payload) <= 3
    for item in payload:
        assert {
            "university",
            "city",
            "region",
            "program",
            "direction",
            "subjects",
            "min_score",
            "type",
            "url",
        }.issubset(item)


def test_regions_endpoint_json_mode(monkeypatch) -> None:
    payload = _run_json_handler(monkeypatch, regions)

    assert payload["storage"] == "json"
    assert payload["count"] >= 8
    assert "Адыгея" in payload["items"]
    assert payload["items"] == sorted(payload["items"])


def test_cities_endpoint_json_mode(monkeypatch) -> None:
    payload = _run_json_handler(monkeypatch, cities, {"region": "Адыгея"})

    assert payload["storage"] == "json"
    assert payload["items"] == ["Майкоп"]


def test_directions_endpoint_json_mode(monkeypatch) -> None:
    payload = _run_json_handler(monkeypatch, directions, {"region": "Москва", "type": "budget"})

    assert payload["storage"] == "json"
    assert payload["count"] > 0
    assert any("эконом" in item.lower() for item in payload["items"])


def test_study_forms_endpoint_json_mode(monkeypatch) -> None:
    payload = _run_json_handler(monkeypatch, study_forms)

    assert payload["storage"] == "json"
    assert "очная" in payload["items"]


def test_admission_types_endpoint_json_mode(monkeypatch) -> None:
    payload = _run_json_handler(monkeypatch, admission_types)

    assert payload["storage"] == "json"
    assert payload["items"] == ["бюджет", "платное"]


def test_api_universities_json_mode_supports_city_q_limit_and_sort(monkeypatch) -> None:
    payload = _run_json_handler(
        monkeypatch,
        universities,
        {
            "city": "Майкоп",
            "q": "IT",
            "limit": "2",
            "sort": "min_score_desc",
        },
    )

    assert len(payload) == 2
    assert all(item["city"] == "Майкоп" for item in payload)
    assert payload[0]["min_score"] >= payload[1]["min_score"]


def test_api_universities_json_mode_ignores_bad_score_and_limit(monkeypatch) -> None:
    payload = _run_json_handler(
        monkeypatch,
        universities,
        {
            "region": "Адыгея",
            "score": "not-a-number",
            "direction": "IT",
            "type": "budget",
            "limit": "not-a-number",
        },
    )

    assert payload
    assert len(payload) <= 5
    assert all(item["region"] == "Адыгея" for item in payload)


def test_mini_app_uses_directory_endpoints() -> None:
    content = Path("mini_app/app.js").read_text(encoding="utf-8")

    assert "/api/regions" in content
    assert "/api/directions" in content
    assert "loadBackendDirectories" in content
    assert "fetchDirectoryItems" in content


def _run_json_handler(monkeypatch, handler, query=None):
    monkeypatch.setenv("USE_POSTGRES", "false")
    app = create_app()

    class Request:
        pass

    request = Request()
    request.app = app
    request.query = query or {}
    response = asyncio.run(handler(request))
    assert response.status == 200
    return json.loads(response.text)
