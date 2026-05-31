from datetime import datetime

from telegram_bot.services.export import (
    build_export_preview,
    build_export_report,
    make_export_filename,
    split_message,
)


def profile(score: int = 230) -> dict:
    return {
        "region": "Адыгея",
        "score": score,
        "direction": "IT",
        "education_type": "budget",
    }


def university(name: str, min_score: int, education_type: str = "бюджет") -> dict:
    return {
        "university": name,
        "city": "Майкоп",
        "program": "Прикладная информатика",
        "direction": "IT",
        "subjects": ["русский язык", "математика", "информатика"],
        "min_score": min_score,
        "type": education_type,
        "price": None,
        "study_form": "очная",
        "duration": "4 года",
        "url": "https://example.ru",
    }


def sample_results() -> list[dict]:
    return [
        university("Безопасный вуз", 180),
        university("Реалистичный вуз", 225),
        university("Амбициозный вуз", 240, "платное"),
    ]


def test_build_export_report_contains_search_context_and_results() -> None:
    report = build_export_report(
        profile(),
        sample_results(),
        exported_at=datetime(2026, 5, 18, 18, 30),
    )

    assert "Аиша — отчёт по подбору вузов" in report
    assert "Дата экспорта: 18.05.2026 18:30" in report
    assert "Регион: Адыгея" in report
    assert "Направление: IT" in report
    assert "Баллы ЕГЭ: 230" in report
    assert "Найдено вариантов: 3" in report
    assert "Безопасный вуз — Прикладная информатика" in report
    assert "Проходные баллы могут меняться" in report


def test_build_export_report_empty_results_is_safe() -> None:
    report = build_export_report(profile(), [])

    assert "Пока нет результата для экспорта" in report
    assert "None" not in report
    assert "null" not in report
    assert "undefined" not in report


def test_build_export_report_includes_favorites_section() -> None:
    report = build_export_report(profile(), sample_results(), favorites=[sample_results()[0]])

    assert "Избранные варианты:" in report
    assert "В избранном: 1" in report


def test_build_export_report_counts_categories() -> None:
    report = build_export_report(profile(), sample_results())

    assert "Безопасные: 1" in report
    assert "Реалистичные: 1" in report
    assert "Амбициозные: 1" in report


def test_build_export_report_handles_missing_optional_fields() -> None:
    item = {
        "university": "Вуз <А>",
        "program": "Программа & тест",
        "city": "Майкоп",
        "subjects": [],
        "min_score": 180,
        "type": "бюджет",
        "source": "postgresql",
    }
    report = build_export_report(profile(), [item])

    assert "Стоимость:" not in report
    assert "Предметы:" not in report
    assert "Вуз <А> — Программа & тест" in report
    assert "source" not in report
    assert "postgresql" not in report
    assert "None" not in report
    assert "null" not in report
    assert "undefined" not in report


def test_build_export_report_includes_postgres_metadata_when_available() -> None:
    item = university("Вуз", 210)
    item.update(
        {
            "year": 2025,
            "faculty": "Институт цифровых технологий",
            "admission_type": "special_quota",
            "source": "postgresql",
        }
    )
    report = build_export_report(profile(), [item])

    assert "Год данных: 2025" in report
    assert "Факультет: Институт цифровых технологий" in report
    assert "Конкурс: особая квота" in report
    assert "source" not in report
    assert "postgresql" not in report


def test_build_export_preview_contains_counts() -> None:
    preview = build_export_preview(profile(), sample_results(), favorites=[sample_results()[0]])

    assert "Экспорт результата" in preview
    assert "Найдено вариантов: 3" in preview
    assert "В избранном: 1" in preview


def test_split_message_short_text_returns_one_part() -> None:
    assert split_message("короткий текст", limit=50) == ["короткий текст"]


def test_split_message_long_text_respects_limit() -> None:
    parts = split_message("абзац\n\n" * 40, limit=50)

    assert len(parts) > 1
    assert all(len(part) <= 50 for part in parts)


def test_make_export_filename_is_safe_txt_name() -> None:
    filename = make_export_filename(user_id=123456)

    assert filename == "aisha_export.txt"
    assert filename.endswith(".txt")
    assert " " not in filename
    assert "/" not in filename
