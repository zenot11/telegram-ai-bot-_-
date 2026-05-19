from __future__ import annotations

from html import escape
from typing import Any


FEEDBACK_CATEGORIES: dict[str, str] = {
    "admission_question": "Вопрос по поступлению",
    "search_problem": "Проблема с подбором вузов",
    "mini_app_problem": "Проблема с Mini App",
    "data_error": "Ошибка в данных",
    "improvement": "Предложить улучшение",
    "other": "Другое",
}

FEEDBACK_STATUS_LABELS = {
    "new": "Новая",
}

MIN_FEEDBACK_MESSAGE_LENGTH = 5
MAX_FEEDBACK_MESSAGE_LENGTH = 1000


def get_feedback_category_label(category: str) -> str:
    return FEEDBACK_CATEGORIES.get(category, FEEDBACK_CATEGORIES["other"])


def normalize_feedback_category(value: str) -> str:
    normalized = str(value or "").strip()
    return normalized if normalized in FEEDBACK_CATEGORIES else "other"


def validate_feedback_category(value: str) -> tuple[bool, str]:
    if str(value or "").strip() not in FEEDBACK_CATEGORIES:
        return False, "invalid_category"
    return True, ""


def validate_feedback_message(message: str) -> tuple[bool, str]:
    text = str(message or "").strip()
    if not text:
        return False, "Напиши обращение чуть подробнее."
    if len(text) < MIN_FEEDBACK_MESSAGE_LENGTH:
        return False, "Опиши проблему чуть подробнее."
    if len(text) > MAX_FEEDBACK_MESSAGE_LENGTH:
        return False, "Сообщение слишком длинное. Сократи его до 1000 символов."
    return True, ""


def compact_feedback_message(message: str, limit: int = 120) -> str:
    text = " ".join(str(message or "").split())
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 1)].rstrip() + "…"


def format_feedback_ticket_created(ticket: dict[str, Any]) -> str:
    return (
        f"<b>Заявка {escape(str(ticket.get('ticket_id', '')))} создана.</b>\n\n"
        f"Тип: {escape(str(ticket.get('category_label', 'Другое')))}\n"
        f"Статус: {escape(status_label(str(ticket.get('status', 'new'))))}\n\n"
        "Спасибо! Мы сохранили обращение. Его можно будет проверить позже."
    )


def format_user_feedback(tickets: list[dict[str, Any]]) -> str:
    if not tickets:
        return (
            "<b>Мои обращения</b>\n\n"
            "Пока обращений нет. Если заметишь проблему в подборе, Mini App или данных, используй /feedback."
        )

    lines = ["<b>Мои обращения</b>"]
    for ticket in tickets:
        lines.extend(
            [
                "",
                f"{escape(str(ticket.get('ticket_id', '')))} · {escape(str(ticket.get('category_label', 'Другое')))}",
                f"Статус: {escape(status_label(str(ticket.get('status', 'new'))))}",
                f"Дата: {escape(str(ticket.get('created_at', 'не указана')))}",
                f"Текст: {escape(compact_feedback_message(str(ticket.get('message', ''))))}",
            ]
        )
    return "\n".join(lines)


def status_label(status: str) -> str:
    return FEEDBACK_STATUS_LABELS.get(status, status)
