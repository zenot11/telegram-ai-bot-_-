from html import escape
from typing import Any

from telegram_bot.services.formatters import title_short
from telegram_bot.services.recommendation import (
    CATEGORY_AMBITIOUS,
    CATEGORY_REALISTIC,
    CATEGORY_SAFE,
    classify_university,
)
from telegram_bot.services.validation import education_type_label


EMPTY_SUMMARY_TEXT = (
    "Пока нет последнего подбора.\n"
    "Нажми «Подобрать вуз» или используй /search — я сохраню результаты и смогу показать итог."
)

CATEGORY_SUMMARY_LABELS = {
    CATEGORY_SAFE: "🟢 Безопасные",
    CATEGORY_REALISTIC: "🟡 Реалистичные",
    CATEGORY_AMBITIOUS: "🔴 Амбициозные",
}


def format_search_brief_summary(results: list[dict[str, Any]], user_score: int) -> str:
    if not results:
        return ""

    return (
        "<b>Краткий итог подбора:</b>\n"
        f"Найдено вариантов: {len(results)}\n\n"
        f"{_format_category_counts(count_categories(results, user_score))}\n\n"
        "Лучше начать с безопасных и реалистичных вариантов, а амбициозные оставить как цель.\n\n"
        "Это не гарантия поступления: данные демонстрационные, а реальные проходные баллы меняются каждый год."
    )


def format_last_search_summary(
    profile: dict[str, Any] | None,
    last_results: list[dict[str, Any]],
    favorites_count: int,
) -> str:
    if not profile or not last_results:
        return EMPTY_SUMMARY_TEXT

    score = profile.get("score")
    direction = profile.get("direction")
    region = profile.get("region")
    education_type = profile.get("education_type")

    lines = [
        "<b>Мой последний подбор:</b>",
        f"📍 Регион: {escape(_value(region))}",
        f"📊 Баллы: {escape(_value(score))}",
        f"🎯 Направление: {escape(_value(direction))}",
        f"🏛 Тип обучения: {education_type_label(str(education_type or ''))}",
        "",
        f"Найдено вариантов: {len(last_results)}",
    ]

    if isinstance(score, int):
        lines.extend(["", _format_category_counts(count_categories(last_results, score))])

    lines.extend(["", "<b>Топ вариантов:</b>"])
    lines.extend(_format_top_results(last_results))

    lines.extend(
        [
            "",
            f"Избранное: {favorites_count} {_plural(favorites_count, 'вуз', 'вуза', 'вузов')}",
            "",
            "Можно открыть:",
            "- Избранные вузы",
            "- Сравнить вузы",
            "- Mini App",
        ]
    )

    return "\n".join(lines)


def count_categories(results: list[dict[str, Any]], user_score: int) -> dict[str, int]:
    counts = {
        CATEGORY_SAFE: 0,
        CATEGORY_REALISTIC: 0,
        CATEGORY_AMBITIOUS: 0,
    }
    for item in results:
        if not isinstance(item, dict):
            continue
        category = classify_university(user_score, item)
        if category in counts:
            counts[category] += 1
    return counts


def _format_category_counts(counts: dict[str, int]) -> str:
    lines = [
        f"{label}: {counts.get(category, 0)}"
        for category, label in CATEGORY_SUMMARY_LABELS.items()
        if counts.get(category, 0) > 0
    ]
    return "\n".join(lines) if lines else "Категории: недостаточно данных"


def _format_top_results(results: list[dict[str, Any]]) -> list[str]:
    top = results[:3]
    if not top:
        return ["не указаны"]
    return [f"{index}. {escape(title_short(item))}" for index, item in enumerate(top, start=1)]


def _value(value: Any) -> str:
    if value is None or value == "":
        return "не указано"
    return str(value)


def _plural(count: int, one: str, few: str, many: str) -> str:
    if count % 10 == 1 and count % 100 != 11:
        return one
    if 2 <= count % 10 <= 4 and not 12 <= count % 100 <= 14:
        return few
    return many
