import asyncio
import json

from backend_stub.main import achievements, create_app, universities
from backend_stub.university_repository import (
    admission_type_label,
    contest_label,
    direction_matches,
    fetch_universities_json,
    fetch_universities_postgres,
    financing_label,
    get_university_display_name,
    is_synthetic_university_name,
    is_synthetic_university_record,
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
    assert financing_label("budget") == "бюджет"
    assert financing_label("paid") == "платное"
    assert contest_label("budget") == "общий конкурс"
    assert contest_label("target") == "целевая квота"
    assert contest_label("special_quota") == "особая квота"
    assert contest_label("individual_quota") == "отдельная квота"


def test_synthetic_university_detection_matches_supplemental_seed_patterns() -> None:
    assert is_synthetic_university_name("Региональный центр технологий и инженерии (Республика Крым)")
    assert is_synthetic_university_name("Институт социальных и цифровых профессий (Республика Адыгея)")
    assert not is_synthetic_university_name("Московский государственный университет")
    assert is_synthetic_university_record({"university_short_name": "РЦТИ-12"})
    assert is_synthetic_university_record({"short_name": "ИСЦП-1"})
    assert not is_synthetic_university_record({"university": "Московский государственный университет"})


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
    assert record["financing_label"] == "бюджет"
    assert record["contest_label"] == "общий конкурс"


def test_short_name_technical_detection_keeps_known_abbreviations() -> None:
    assert is_technical_university_name("РЦТИ-26") is True
    assert is_technical_university_name("ИБ") is True
    assert is_technical_university_name("МГУ") is False
    assert is_technical_university_name("МИРЭА") is False


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


def test_universities_endpoint_excludes_synthetic_records_by_default(monkeypatch) -> None:
    monkeypatch.setenv("USE_POSTGRES", "false")
    rows = [
        _record(region="Республика Крым", direction="Прикладная информатика"),
        {
            **_record(region="Республика Крым", direction="Прикладная информатика"),
            "university": "Региональный центр технологий и инженерии (Республика Крым)",
            "university_short_name": "РЦТИ-12",
        },
    ]
    app = create_app(universities_data=rows)

    class Request:
        pass

    request = Request()
    request.app = app
    request.query = {
        "region": "Крым",
        "direction": "IT",
        "type": "budget",
        "score": "230",
        "limit": "5",
    }
    response = asyncio.run(universities(request))
    payload = json.loads(response.text)

    assert response.status == 200
    assert [item["university"] for item in payload] == ["Тестовый вуз"]


def test_include_synthetic_returns_demo_records_in_json_mode(monkeypatch) -> None:
    monkeypatch.setenv("USE_POSTGRES", "false")
    app = create_app(
        universities_data=[
            {
                **_record(region="Республика Крым", direction="Прикладная информатика"),
                "university": "Региональный центр технологий и инженерии (Республика Крым)",
                "university_short_name": "РЦТИ-12",
            }
        ]
    )

    class Request:
        pass

    request = Request()
    request.app = app
    request.query = {
        "region": "Крым",
        "direction": "IT",
        "type": "budget",
        "score": "230",
        "limit": "5",
        "include_synthetic": "true",
    }
    response = asyncio.run(universities(request))
    payload = json.loads(response.text)

    assert response.status == 200
    assert payload[0]["university"] == "Региональный центр технологий и инженерии (Республика Крым)"
    assert payload[0]["financing_label"] == "бюджет"
    assert payload[0]["study_form_label"] == "очная"


class FakePool:
    def __init__(self, rows: list[dict]) -> None:
        self.rows = rows
        self.query = ""

    async def fetch(self, query: str, *params):
        self.query = query
        return self.rows


def test_postgres_fetch_filters_synthetic_records_and_keeps_include_flag() -> None:
    pool = FakePool(
        [
            {
                "university_name": "Региональный центр технологий и инженерии (Республика Крым)",
                "university_short_name": "РЦТИ-12",
                "city": "Симферополь",
                "region": "Республика Крым",
                "direction_name": "Прикладная информатика",
                "min_score": 180,
                "admission_type": "budget",
                "study_form": "full_time",
            }
        ]
    )

    default_records = asyncio.run(fetch_universities_postgres(pool, {"limit": 5}))
    assert default_records == []
    assert "Региональный центр технологий" in pool.query

    include_records = asyncio.run(fetch_universities_postgres(pool, {"limit": 5, "include_synthetic": True}))
    assert include_records


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
