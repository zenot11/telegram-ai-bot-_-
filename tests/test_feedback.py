from pathlib import Path

from telegram_bot.services.feedback import (
    FEEDBACK_CATEGORIES,
    compact_feedback_message,
    get_feedback_category_label,
    normalize_feedback_category,
    validate_feedback_message,
)
from telegram_bot.storage import feedback_data


def configure_feedback_path(monkeypatch, tmp_path: Path) -> Path:
    path = tmp_path / "feedback.json"
    monkeypatch.setattr(feedback_data, "FEEDBACK_DATA_PATH", path)
    return path


def test_feedback_categories_and_labels() -> None:
    assert FEEDBACK_CATEGORIES["search_problem"] == "Проблема с подбором вузов"
    assert get_feedback_category_label("mini_app_problem") == "Проблема с Mini App"
    assert normalize_feedback_category("unknown") == "other"


def test_feedback_message_validation() -> None:
    assert validate_feedback_message("abc")[0] is False
    assert validate_feedback_message("x" * 1001)[0] is False
    assert validate_feedback_message("Mini App не открывается")[0] is True


def test_create_feedback_ticket_saves_expected_fields(tmp_path, monkeypatch) -> None:
    configure_feedback_path(monkeypatch, tmp_path)

    ticket = feedback_data.create_feedback_ticket(
        source="bot",
        user_id=123,
        user_name="Test User",
        category="search_problem",
        message="Не нашёл регион",
        context={"page": "telegram_bot"},
    )

    assert ticket["id"] == 1
    assert ticket["ticket_id"] == "AISH-0001"
    assert ticket["source"] == "bot"
    assert ticket["user_id"] == 123
    assert ticket["category_label"] == "Проблема с подбором вузов"
    assert ticket["status"] == "new"
    assert ticket["context"]["page"] == "telegram_bot"

    stored = feedback_data.load_feedback()
    assert stored["next_id"] == 2
    assert len(stored["tickets"]) == 1


def test_get_user_feedback_filters_and_limits(tmp_path, monkeypatch) -> None:
    configure_feedback_path(monkeypatch, tmp_path)

    for index in range(4):
        feedback_data.create_feedback_ticket("bot", 1, None, "other", f"Заявка {index}")
    feedback_data.create_feedback_ticket("mini_app", 2, None, "other", "Чужая заявка")

    tickets = feedback_data.get_user_feedback(1, limit=2)

    assert len(tickets) == 2
    assert tickets[0]["ticket_id"] == "AISH-0004"
    assert all(ticket["user_id"] == 1 for ticket in tickets)


def test_recent_feedback_and_compact_message(tmp_path, monkeypatch) -> None:
    configure_feedback_path(monkeypatch, tmp_path)

    feedback_data.create_feedback_ticket("bot", 1, None, "other", "Первое обращение")
    feedback_data.create_feedback_ticket("mini_app", None, None, "improvement", "Второе обращение")

    recent = feedback_data.get_recent_feedback(limit=1)

    assert recent[0]["ticket_id"] == "AISH-0002"
    assert compact_feedback_message("x" * 130).endswith("…")
