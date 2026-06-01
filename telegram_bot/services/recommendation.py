from typing import Any

from telegram_bot.services.scores import (
    format_score_delta_text,
    is_valid_score,
    parse_score,
    score_delta_value,
)


SAFE_SCORE_MARGIN = 25
AMBITIOUS_SCORE_MARGIN = 20

CATEGORY_SAFE = "safe"
CATEGORY_REALISTIC = "realistic"
CATEGORY_AMBITIOUS = "ambitious"
CATEGORY_UNAVAILABLE = "unavailable"

RECOMMENDATION_CATEGORIES = (
    CATEGORY_SAFE,
    CATEGORY_REALISTIC,
    CATEGORY_AMBITIOUS,
    CATEGORY_UNAVAILABLE,
)

VISIBLE_RECOMMENDATION_CATEGORIES = (
    CATEGORY_SAFE,
    CATEGORY_REALISTIC,
    CATEGORY_AMBITIOUS,
)

RECOMMENDATION_LABELS = {
    CATEGORY_SAFE: "🟢 Безопасный вариант",
    CATEGORY_REALISTIC: "🟡 Реалистичный вариант",
    CATEGORY_AMBITIOUS: "🔴 Амбициозный вариант",
    CATEGORY_UNAVAILABLE: "⚪ Пока недоступный вариант",
}


def classify_university(user_score: int, university: dict[str, Any]) -> str:
    min_score = get_min_score(university)
    if min_score is None or not is_valid_score(min_score):
        return CATEGORY_UNAVAILABLE

    if min_score <= user_score - SAFE_SCORE_MARGIN:
        return CATEGORY_SAFE
    if user_score - SAFE_SCORE_MARGIN < min_score <= user_score:
        return CATEGORY_REALISTIC
    if user_score < min_score <= user_score + AMBITIOUS_SCORE_MARGIN:
        return CATEGORY_AMBITIOUS
    return CATEGORY_UNAVAILABLE


def group_universities_by_recommendation(
    user_score: int,
    universities: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    groups = {category: [] for category in RECOMMENDATION_CATEGORIES}
    for university in universities:
        if not isinstance(university, dict):
            continue
        category = classify_university(user_score, university)
        groups[category].append(university)
    return groups


def visible_recommendations(groups: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for category in VISIBLE_RECOMMENDATION_CATEGORIES:
        result.extend(groups.get(category, []))
    return result


def format_recommendation_summary(groups: dict[str, list[dict[str, Any]]]) -> str:
    return (
        "Я разделила варианты по уровню уверенности:\n"
        "🟢 Безопасные — есть заметный запас по баллам.\n"
        "🟡 Реалистичные — баллы близки к проходному уровню.\n"
        "🔴 Амбициозные — немного не хватает, но можно рассматривать как цель.\n\n"
        "Это предварительная оценка, а не гарантия поступления."
    )


def get_recommendation_label(category: str) -> str:
    return RECOMMENDATION_LABELS.get(category, RECOMMENDATION_LABELS[CATEGORY_UNAVAILABLE])


def format_categories_explanation() -> str:
    return (
        "Как читать категории:\n\n"
        "🟢 Безопасный вариант — проходной балл ниже твоего с заметным запасом.\n"
        "🟡 Реалистичный вариант — баллы близки к твоим, запас небольшой.\n"
        "🔴 Амбициозный вариант — немного не хватает, но можно рассмотреть как цель.\n\n"
        "Важно: это не гарантия поступления, потому что реальные проходные баллы меняются каждый год."
    )


def get_min_score(university: dict[str, Any]) -> int | None:
    return parse_score(university.get("min_score"))


def score_delta(user_score: int, university: dict[str, Any]) -> int | None:
    return score_delta_value(user_score, university.get("min_score"))


def format_score_delta(user_score: int, university: dict[str, Any]) -> str:
    return format_score_delta_text(user_score, university.get("min_score"))
