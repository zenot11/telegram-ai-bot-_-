from html import escape
from typing import Any

from telegram_bot.services.recommendation import (
    classify_university,
    format_score_delta,
    get_recommendation_label,
)


def format_university_card(
    index: int,
    item: dict[str, Any],
    user_score: int | None = None,
    *,
    icon: str = "🎓",
    include_note: bool = True,
) -> str:
    title = title_short(item)
    header_prefix = f"{icon} " if icon else ""
    lines = [
        f"{header_prefix}<b>{index}. {escape(title)}</b>",
        f"📍 Город: {escape(text_value(item.get('city')))}",
    ]

    if user_score is not None:
        category = classify_university(user_score, item)
        lines.append(f"{category_emoji(category)} Категория: {escape(category_text(category))}")

    subjects = subjects_text(item)
    if subjects:
        lines.append(f"📚 Предметы: {escape(subjects)}")

    lines.append(f"📊 Мин. балл: {escape(text_value(item.get('min_score')))}")

    if user_score is not None:
        lines.append(f"✅ Твои баллы: {user_score}")
        lines.append(format_delta_line(user_score, item))

    lines.append(f"🎯 Тип: {escape(text_value(item.get('type')))}")
    admission_type = admission_type_text(item.get("admission_type"))
    if admission_type and admission_type not in {normalize_label(item.get("type")), "бюджет", "платное"}:
        lines.append(f"🎫 Конкурс: {escape(admission_type)}")

    if has_display_value(item.get("price")):
        lines.append(f"💰 Стоимость: {escape(format_price(item.get('price')))}")

    if has_display_value(item.get("study_form")):
        lines.append(f"🏫 Форма: {escape(str(item['study_form']))}")
    if has_display_value(item.get("duration")):
        lines.append(f"⏱ Срок: {escape(str(item['duration']))}")
    if has_display_value(item.get("faculty")):
        lines.append(f"🏛 Факультет: {escape(str(item['faculty']))}")
    if has_display_value(item.get("year")):
        lines.append(f"📅 Год данных: {escape(str(item['year']))}")
    if has_display_value(item.get("url")):
        lines.append(f"🔗 Сайт: {escape(str(item['url']))}")

    if include_note and has_display_value(item.get("note")):
        lines.extend(["", f"Пометка: {escape(str(item['note']))}."])

    return "\n".join(lines)


def title_short(item: dict[str, Any]) -> str:
    university = text_value(item.get("university"), "Вуз")
    program = text_value(item.get("program"), "программа не указана")
    return f"{university} — {program}"


def text_value(value: Any, fallback: str = "не указано") -> str:
    if not has_display_value(value):
        return fallback
    return str(value)


def has_display_value(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str) and not value.strip():
        return False
    if isinstance(value, (list, tuple, set, dict)) and not value:
        return False
    return True


def subjects_text(item: dict[str, Any]) -> str:
    subjects = item.get("subjects")
    if isinstance(subjects, list):
        return ", ".join(str(subject) for subject in subjects if str(subject).strip())
    if isinstance(subjects, str) and subjects.strip():
        return subjects.strip()
    return ""


def format_price(value: Any) -> str:
    if not has_display_value(value):
        return "не указана"
    if isinstance(value, int):
        return f"{value:,} руб./год".replace(",", " ")
    if isinstance(value, str) and value.strip().isdigit():
        return f"{int(value):,} руб./год".replace(",", " ")
    return str(value)


def admission_type_text(value: Any) -> str:
    normalized = normalize_label(value)
    return {
        "target": "целевая квота",
        "special_quota": "особая квота",
        "separate_quota": "отдельная квота",
        "additional": "дополнительный набор",
        "budget": "бюджет",
        "paid": "платное",
    }.get(normalized, str(value).strip() if has_display_value(value) else "")


def normalize_label(value: Any) -> str:
    return str(value or "").strip().lower().replace(" ", "_").replace("-", "_")


def category_emoji(category: str) -> str:
    label = get_recommendation_label(category)
    return label.split(" ", 1)[0]


def category_text(category: str) -> str:
    label = get_recommendation_label(category)
    text = label.split(" ", 1)[1] if " " in label else label
    return text[:1].lower() + text[1:]


def format_delta_line(user_score: int, item: dict[str, Any]) -> str:
    delta = format_score_delta(user_score, item)
    if delta.startswith("Запас:"):
        return f"➕ {escape(delta)}"
    if delta.startswith("Не хватает:"):
        return f"➖ {escape(delta)}"
    return f"📌 {escape(delta)}"
