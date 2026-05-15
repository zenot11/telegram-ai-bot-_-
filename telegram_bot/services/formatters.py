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

    lines.extend(
        [
            f"📚 Предметы: {escape(subjects_text(item))}",
            f"📊 Мин. балл: {escape(text_value(item.get('min_score')))}",
        ]
    )

    if user_score is not None:
        lines.append(f"✅ Твои баллы: {user_score}")
        lines.append(format_delta_line(user_score, item))

    lines.append(f"🎯 Тип: {escape(text_value(item.get('type')))}")
    lines.append(f"💰 Стоимость: {escape(format_price(item.get('price')))}")

    if item.get("study_form"):
        lines.append(f"🏫 Форма: {escape(str(item['study_form']))}")
    if item.get("duration"):
        lines.append(f"⏱ Срок: {escape(str(item['duration']))}")
    if item.get("url"):
        lines.append(f"🔗 Сайт: {escape(str(item['url']))}")

    if include_note:
        lines.extend(["", f"Пометка: {escape(str(item.get('note') or 'демонстрационные данные'))}."])

    return "\n".join(lines)


def title_short(item: dict[str, Any]) -> str:
    university = text_value(item.get("university"), "Вуз")
    program = text_value(item.get("program"), "программа не указана")
    return f"{university} — {program}"


def text_value(value: Any, fallback: str = "не указано") -> str:
    if value is None or value == "":
        return fallback
    return str(value)


def subjects_text(item: dict[str, Any]) -> str:
    subjects = item.get("subjects")
    if isinstance(subjects, list) and subjects:
        return ", ".join(str(subject) for subject in subjects if str(subject).strip()) or "не указаны"
    return "не указаны"


def format_price(value: Any) -> str:
    if value is None or value == "":
        return "не указана"
    if isinstance(value, int):
        return f"{value:,} руб./год".replace(",", " ")
    if isinstance(value, str) and value.strip().isdigit():
        return f"{int(value):,} руб./год".replace(",", " ")
    return str(value)


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
