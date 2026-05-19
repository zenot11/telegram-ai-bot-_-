from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from threading import Lock
from typing import Any

from telegram_bot.services.feedback import get_feedback_category_label, normalize_feedback_category


FEEDBACK_DATA_PATH = Path("telegram_bot/storage/feedback.json")
FEEDBACK_STATUSES = {"new"}

_lock = Lock()


def load_feedback() -> dict[str, Any]:
    with _lock:
        return _read_feedback_unlocked()


def save_feedback(data: dict[str, Any]) -> None:
    with _lock:
        _write_feedback_unlocked(_normalize_feedback_data(data))


def create_feedback_ticket(
    source: str,
    user_id: int | None,
    user_name: str | None,
    category: str,
    message: str,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    with _lock:
        data = _read_feedback_unlocked()
        next_id = _next_ticket_id(data)
        normalized_category = normalize_feedback_category(category)
        ticket = {
            "id": next_id,
            "ticket_id": _format_ticket_id(next_id),
            "source": _normalize_source(source),
            "user_id": user_id if isinstance(user_id, int) else None,
            "user_name": _clean_optional_string(user_name),
            "category": normalized_category,
            "category_label": get_feedback_category_label(normalized_category),
            "message": str(message or "").strip(),
            "status": "new",
            "created_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            "context": context if isinstance(context, dict) else {},
        }
        data["tickets"].append(ticket)
        data["next_id"] = next_id + 1
        _write_feedback_unlocked(data)
        return ticket


def get_user_feedback(user_id: int, limit: int = 5) -> list[dict[str, Any]]:
    data = load_feedback()
    safe_limit = max(0, int(limit))
    tickets = [
        ticket for ticket in data.get("tickets", [])
        if isinstance(ticket, dict) and ticket.get("user_id") == user_id
    ]
    tickets.sort(key=lambda item: int(item.get("id", 0)), reverse=True)
    return tickets[:safe_limit]


def get_recent_feedback(limit: int = 20) -> list[dict[str, Any]]:
    data = load_feedback()
    safe_limit = max(0, int(limit))
    tickets = [ticket for ticket in data.get("tickets", []) if isinstance(ticket, dict)]
    tickets.sort(key=lambda item: int(item.get("id", 0)), reverse=True)
    return tickets[:safe_limit]


def clear_feedback_for_tests() -> None:
    save_feedback({"tickets": [], "next_id": 1})


def _read_feedback_unlocked() -> dict[str, Any]:
    if not FEEDBACK_DATA_PATH.exists():
        data = {"tickets": [], "next_id": 1}
        _write_feedback_unlocked(data)
        return data

    try:
        raw_data = json.loads(FEEDBACK_DATA_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"tickets": [], "next_id": 1}
    return _normalize_feedback_data(raw_data)


def _write_feedback_unlocked(data: dict[str, Any]) -> None:
    FEEDBACK_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    FEEDBACK_DATA_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _normalize_feedback_data(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict):
        return {"tickets": [], "next_id": 1}

    tickets = data.get("tickets", [])
    safe_tickets = [ticket for ticket in tickets if isinstance(ticket, dict)] if isinstance(tickets, list) else []
    max_id = max((int(ticket.get("id", 0)) for ticket in safe_tickets if _is_int_like(ticket.get("id"))), default=0)
    next_id = data.get("next_id")
    if not _is_int_like(next_id) or int(next_id) <= max_id:
        next_id = max_id + 1

    return {
        "tickets": safe_tickets,
        "next_id": int(next_id),
    }


def _next_ticket_id(data: dict[str, Any]) -> int:
    next_id = data.get("next_id", 1)
    return int(next_id) if _is_int_like(next_id) and int(next_id) > 0 else 1


def _format_ticket_id(ticket_id: int) -> str:
    return f"AISH-{ticket_id:04d}"


def _normalize_source(source: str) -> str:
    return source if source in {"bot", "mini_app"} else "bot"


def _clean_optional_string(value: str | None) -> str | None:
    text = str(value or "").strip()
    return text or None


def _is_int_like(value: Any) -> bool:
    if isinstance(value, bool):
        return False
    if isinstance(value, int):
        return True
    return isinstance(value, str) and value.isdigit()
