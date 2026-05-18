from datetime import datetime
from html import escape
from typing import Any

from telegram_bot.services.formatters import title_short
from telegram_bot.services.recommendation import (
    CATEGORY_AMBITIOUS,
    CATEGORY_REALISTIC,
    CATEGORY_SAFE,
    classify_university,
)
from telegram_bot.services.validation import education_type_label, normalize_education_type


HISTORY_LIMIT = 5

CATEGORY_LABELS = {
    CATEGORY_SAFE: "безопасные",
    CATEGORY_REALISTIC: "реалистичные",
    CATEGORY_AMBITIOUS: "амбициозные",
}


def build_history_entry(
    search_query: dict[str, Any],
    results: list[dict[str, Any]],
    created_at: str | None = None,
) -> dict[str, Any]:
    score = search_query.get("score")
    categories_count = summarize_categories(results, score if isinstance(score, int) else None)
    top_items = [
        _short_top_item(item, score if isinstance(score, int) else None)
        for item in results[:3]
        if isinstance(item, dict)
    ]

    return {
        "region": _text(search_query.get("region")),
        "score": score,
        "direction": _text(search_query.get("direction")),
        "type": _education_type_text(search_query.get("education_type") or search_query.get("type")),
        "total_results": len(results),
        "categories_count": categories_count,
        "top_items": top_items,
        "created_at": created_at or datetime.now().strftime("%Y-%m-%d %H:%M"),
    }


def summarize_categories(results: list[dict[str, Any]], score: int | None) -> dict[str, int]:
    counts = {
        CATEGORY_SAFE: 0,
        CATEGORY_REALISTIC: 0,
        CATEGORY_AMBITIOUS: 0,
    }
    if score is None:
        return counts

    for item in results:
        if not isinstance(item, dict):
            continue
        category = classify_university(score, item)
        if category in counts:
            counts[category] += 1
    return counts


def format_history_message(history: list[dict[str, Any]]) -> str:
    if not history:
        return (
            "<b>История подборов</b>\n\n"
            "История подборов пока пустая.\n"
            "Сначала сделай подбор через /search."
        )

    blocks = ["<b>История подборов</b>"]
    for index, entry in enumerate(history[:HISTORY_LIMIT], start=1):
        blocks.append(_format_history_entry(index, entry))
    return "\n\n".join(blocks)


def _format_history_entry(index: int, entry: dict[str, Any]) -> str:
    lines = [
        f"<b>{index}. {escape(_text(entry.get('region')))} · {escape(_text(entry.get('direction')))} · {escape(_title_type(entry.get('type')))}</b>",
        f"Баллы: {escape(_text(entry.get('score')))}",
        f"Найдено: {escape(_text(entry.get('total_results'), '0'))}",
        f"Категории: {_format_category_counts(entry.get('categories_count'))}",
    ]
    if entry.get("created_at"):
        lines.append(f"Дата: {escape(_text(entry.get('created_at')))}")

    top_items = entry.get("top_items")
    if isinstance(top_items, list) and top_items:
        lines.append("Топ:")
        for item in top_items[:3]:
            if isinstance(item, dict):
                lines.append(f"— {escape(_top_title(item))}")
    else:
        lines.append("Топ: вариантов не найдено")

    return "\n".join(lines)


def _format_category_counts(value: Any) -> str:
    counts = value if isinstance(value, dict) else {}
    parts = [
        f"{label} — {int(counts.get(category, 0) or 0)}"
        for category, label in CATEGORY_LABELS.items()
    ]
    return ", ".join(parts)


def _short_top_item(item: dict[str, Any], score: int | None) -> dict[str, Any]:
    category = classify_university(score, item) if isinstance(score, int) else ""
    return {
        "university": _text(item.get("university"), "Вуз"),
        "program": _text(item.get("program"), "программа не указана"),
        "min_score": item.get("min_score"),
        "category": category,
    }


def _top_title(item: dict[str, Any]) -> str:
    return title_short(item)


def _education_type_text(value: Any) -> str:
    normalized = normalize_education_type(str(value or ""))
    if normalized:
        return education_type_label(normalized)
    return _text(value)


def _title_type(value: Any) -> str:
    text = _text(value)
    return text[:1].upper() + text[1:] if text else text


def _text(value: Any, fallback: str = "не указано") -> str:
    if value is None or value == "":
        return fallback
    return str(value)
