import asyncio

from backend_stub.university_repository import (
    build_university_filters,
    fetch_universities_postgres,
    normalize_pg_record,
)
from telegram_bot.services.export import build_export_report
from telegram_bot.services.formatters import format_university_card
from telegram_bot.services.recommendation import AMBITIOUS_SCORE_MARGIN


class FakePool:
    def __init__(self, rows: list[dict]) -> None:
        self.rows = rows
        self.query = ""
        self.params: tuple = ()

    async def fetch(self, query: str, *params):
        self.query = query
        self.params = params
        return self.rows


def test_postgres_fetch_uses_ambitious_margin_and_normalizes_quality_fields() -> None:
    pool = FakePool(
        [
            {
                "university": "МГУ",
                "university_name": "Московский государственный университет",
                "university_short_name": "МГУ",
                "city": "Москва",
                "region": "Москва",
                "program": "Прикладная информатика",
                "direction": "Прикладная информатика",
                "subjects": None,
                "min_score": 250,
                "admission_type": "target",
                "study_form": "full_time",
                "faculty": "Факультет вычислительной математики и кибернетики",
                "year": 2025,
                "source": "postgresql",
            }
        ]
    )
    filters = build_university_filters({"score": "230", "limit": "3"})

    records = asyncio.run(fetch_universities_postgres(pool, filters))

    assert "ps.min_score <=" in pool.query
    assert 230 + AMBITIOUS_SCORE_MARGIN in pool.params
    assert 3 in pool.params
    assert records == [
        {
            "university": "Московский государственный университет",
            "city": "Москва",
            "region": "Москва",
            "program": "Прикладная информатика",
            "direction": "Прикладная информатика",
            "profile": "",
            "direction_code": "",
            "subjects": [],
            "min_score": 250,
            "score_is_valid": True,
            "score_display": "250",
            "score_note": "",
            "type": "бюджет",
            "url": "",
            "price": None,
            "study_form": "очная",
            "duration": "",
            "note": "",
            "year": 2025,
            "faculty": "Факультет вычислительной математики и кибернетики",
            "admission_type": "target",
            "admission_type_label": "целевая квота",
            "university_short_name": "МГУ",
            "university_full_name": "Московский государственный университет",
            "source": "postgresql",
        }
    ]


def test_postgres_record_with_missing_optional_fields_is_clean_in_user_outputs() -> None:
    record = normalize_pg_record(
        {
            "university_name": "Университет",
            "city": "Москва",
            "region": "Москва",
            "direction_name": "Информатика",
            "subjects": None,
            "min_score": 240,
            "admission_type": "budget",
            "year": 2025,
            "source": "postgresql",
        }
    )
    profile = {
        "region": "Москва",
        "score": 230,
        "direction": "информатика",
        "education_type": "budget",
    }

    card = format_university_card(1, record, 230)
    report = build_export_report(profile, [record])
    combined = f"{card}\n{report}"

    assert "Предметы:" not in combined
    assert "Стоимость:" not in combined
    assert "Срок:" not in combined
    assert "source" not in combined
    assert "postgresql" not in combined
    assert "None" not in combined
    assert "null" not in combined
    assert "undefined" not in combined
    assert "Год данных: 2025" in combined
