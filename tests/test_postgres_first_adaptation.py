import asyncio
import json

from backend_stub.main import achievements, create_app, universities
from backend_stub.university_repository import (
    admission_type_label,
    direction_matches,
    fetch_universities_json,
    get_university_display_name,
    is_technical_university_name,
    normalize_pg_record,
    postgres_direction_terms,
    region_search_terms,
)


def test_region_aliases_include_postgres_republic_names() -> None:
    assert "Республика Крым" in region_search_terms("Крым")
    assert "Республика Адыгея" in region_search_terms("Адыгея")


def test_json_filter_matches_postgres_style_region_aliases() -> None:
    rows = [_record(region="Республика Крым", direction="Прикладная информатика")]

    results = fetch_universities_json(
        rows,
        {
            "region": "Крым",
            "score": 230,
            "direction": "IT",
            "type": "budget",
            "limit": 5,
        },
    )

    assert results
    assert results[0]["region"] == "Республика Крым"


def test_direction_alias_it_expands_to_real_postgres_directions() -> None:
    terms = postgres_direction_terms("IT")

    assert "Прикладная информатика" in terms
    assert "Информационная безопасность" in terms
    assert "Программная инженерия" in terms
    assert direction_matches(_record(direction="Информационные системы и технологии"), "информационные технологии")


def test_multiword_direction_alias_does_not_match_single_generic_word() -> None:
    assert direction_matches(_record(direction="Лечебное дело"), "мед")
    assert not direction_matches(_record(direction="Инженерное дело"), "мед")


def test_admission_type_labels_are_human_readable() -> None:
    assert admission_type_label("special_quota") == "особая квота"
    assert admission_type_label("target_quota") == "целевая квота"
    assert admission_type_label("target") == "целевая квота"


def test_postgres_normalization_prefers_full_university_name_over_technical_short_name() -> None:
    record = normalize_pg_record(
        {
            "university_name": "Региональный центр технологий и инженерии (Республика Крым)",
            "university_short_name": "РЦТИ-12",
            "city": "Симферополь",
            "region": "Республика Крым",
            "direction_name": "Прикладная информатика",
            "min_score": 186,
            "admission_type": "budget",
        }
    )

    assert is_technical_university_name("РЦТИ-12") is True
    assert get_university_display_name(record["university_full_name"], record["university_short_name"]) == record["university"]
    assert record["university"] == "Региональный центр технологий и инженерии (Республика Крым)"


def test_achievements_endpoint_works_in_json_fallback(monkeypatch) -> None:
    monkeypatch.setenv("USE_POSTGRES", "false")
    app = create_app()

    class Request:
        pass

    request = Request()
    request.app = app
    request.query = {"limit": "2"}
    response = asyncio.run(achievements(request))
    payload = json.loads(response.text)

    assert response.status == 200
    assert payload["storage"] == "json"
    assert payload["count"] == 2
    assert {"title", "category", "points", "description"}.issubset(payload["items"][0])


def test_api_universities_accepts_alias_filters_without_database(monkeypatch) -> None:
    monkeypatch.setenv("USE_POSTGRES", "false")
    app = create_app(universities_data=[_record(region="Республика Адыгея", direction="Прикладная информатика")])

    class Request:
        pass

    request = Request()
    request.app = app
    request.query = {
        "region": "Адыгея",
        "direction": "IT",
        "type": "budget",
        "score": "230",
        "limit": "5",
    }
    response = asyncio.run(universities(request))
    payload = json.loads(response.text)

    assert response.status == 200
    assert len(payload) == 1


def _record(region: str = "Республика Крым", direction: str = "Прикладная информатика") -> dict:
    return {
        "university": "Тестовый вуз",
        "city": "Симферополь",
        "region": region,
        "program": direction,
        "direction": direction,
        "directions": [direction],
        "subjects": [],
        "min_score": 180,
        "type": "бюджет",
        "price": None,
        "url": "https://example.ru",
        "study_form": "очная",
        "duration": "",
        "note": "",
    }
