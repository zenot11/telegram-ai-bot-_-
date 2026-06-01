from pathlib import Path

from telegram_bot.services.advice import build_next_steps
from telegram_bot.services.compare import format_comparison
from telegram_bot.services.export import build_export_report
from telegram_bot.services.formatters import format_university_card


def test_bot_card_export_and_compare_do_not_show_technical_optional_values() -> None:
    items = [
        _result("Вуз 1", 240),
        _result("Вуз 2", 235),
    ]
    profile = {
        "region": "Москва",
        "score": 230,
        "direction": "информатика",
        "education_type": "budget",
    }

    text = "\n".join(
        [
            format_university_card(1, items[0], 230),
            build_export_report(profile, items),
            format_comparison(items, user_score=230),
        ]
    )

    assert "None" not in text
    assert "null" not in text
    assert "undefined" not in text
    assert "[]" not in text
    assert "Предметы: []" not in text
    assert "Стоимость: None" not in text
    assert "Срок: " not in text
    assert "source" not in text
    assert "postgresql" not in text
    assert "Год данных: 2025" in text
    assert "Факультет: Институт технологий" in text


def test_paid_advice_handles_missing_price_without_claiming_price_data() -> None:
    profile = {
        "region": "Москва",
        "score": 230,
        "direction": "информатика",
        "education_type": "paid",
    }

    steps = build_next_steps(profile, [_result("Платный вуз", 220, education_type="платное")])

    assert "Проверь стоимость, скидки и условия оплаты на официальном сайте вуза." in steps


def test_mini_app_has_optional_field_helpers_and_postgres_metadata_without_source_ui() -> None:
    js = Path("mini_app/app.js").read_text(encoding="utf-8")

    assert "function hasValue" in js
    assert "function formatSubjects" in js
    assert "function formatAdmissionType" in js
    assert "shouldShowAdmissionType" in js
    assert "Год данных" in js
    assert "Факультет" in js
    assert "item.source" not in js
    assert "Источник" not in js
    assert ".source" not in js


def _result(name: str, min_score: int, education_type: str = "бюджет") -> dict:
    return {
        "university": name,
        "city": "Москва",
        "region": "Москва",
        "program": "Информатика",
        "direction": "Информатика",
        "subjects": [],
        "min_score": min_score,
        "type": education_type,
        "price": None,
        "url": "",
        "study_form": "очная",
        "duration": "",
        "year": 2025,
        "faculty": "Институт технологий",
        "source": "postgresql",
    }
