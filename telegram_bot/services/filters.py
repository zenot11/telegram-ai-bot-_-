from html import escape
from typing import Any

from telegram_bot.services.formatters import format_university_card
from telegram_bot.services.recommendation import (
    CATEGORY_AMBITIOUS,
    CATEGORY_REALISTIC,
    CATEGORY_SAFE,
    classify_university,
)
from telegram_bot.services.validation import education_type_label, normalize_education_type


FILTER_ALL = "all"
FILTER_SAFE = "safe"
FILTER_REALISTIC = "realistic"
FILTER_AMBITIOUS = "ambitious"
FILTER_BUDGET = "budget"
FILTER_PAID = "paid"

FILTER_NAMES = (
    FILTER_ALL,
    FILTER_SAFE,
    FILTER_REALISTIC,
    FILTER_AMBITIOUS,
    FILTER_BUDGET,
    FILTER_PAID,
)

FILTER_TITLES = {
    FILTER_ALL: "все варианты",
    FILTER_SAFE: "безопасные варианты",
    FILTER_REALISTIC: "реалистичные варианты",
    FILTER_AMBITIOUS: "амбициозные варианты",
    FILTER_BUDGET: "бюджет",
    FILTER_PAID: "платное",
}

EMPTY_FILTERS_TEXT = (
    "Пока нет результатов для фильтрации.\n"
    "Сначала сделай подбор через /search."
)


def filter_results(
    results: list[dict[str, Any]],
    filter_name: str,
    user_score: int | None = None,
) -> list[dict[str, Any]]:
    safe_results = [item for item in results if isinstance(item, dict)]
    if filter_name == FILTER_ALL:
        return safe_results
    if filter_name in {FILTER_SAFE, FILTER_REALISTIC, FILTER_AMBITIOUS}:
        return [
            item for item in safe_results
            if _item_category(item, user_score) == filter_name
        ]
    if filter_name == FILTER_BUDGET:
        return [item for item in safe_results if _item_type(item) == "budget"]
    if filter_name == FILTER_PAID:
        return [item for item in safe_results if _item_type(item) == "paid"]
    return safe_results


def get_filter_counts(results: list[dict[str, Any]], user_score: int | None = None) -> dict[str, int]:
    safe_results = [item for item in results if isinstance(item, dict)]
    return {
        FILTER_ALL: len(safe_results),
        FILTER_SAFE: len(filter_results(safe_results, FILTER_SAFE, user_score)),
        FILTER_REALISTIC: len(filter_results(safe_results, FILTER_REALISTIC, user_score)),
        FILTER_AMBITIOUS: len(filter_results(safe_results, FILTER_AMBITIOUS, user_score)),
        FILTER_BUDGET: len(filter_results(safe_results, FILTER_BUDGET, user_score)),
        FILTER_PAID: len(filter_results(safe_results, FILTER_PAID, user_score)),
    }


def format_filter_title(filter_name: str) -> str:
    return FILTER_TITLES.get(filter_name, FILTER_TITLES[FILTER_ALL])


def build_filters_overview_message(profile: dict[str, Any] | None, results: list[dict[str, Any]]) -> str:
    if not results:
        return EMPTY_FILTERS_TEXT

    score = _score(profile.get("score") if isinstance(profile, dict) else None)
    counts = get_filter_counts(results, score)
    return (
        "<b>Фильтры результатов</b>\n\n"
        "<b>Последний подбор:</b>\n"
        f"{escape(_value(profile.get('region') if isinstance(profile, dict) else None))} · "
        f"{escape(_value(profile.get('direction') if isinstance(profile, dict) else None))} · "
        f"{escape(_education_type_text(profile.get('education_type') if isinstance(profile, dict) else None))}\n"
        f"Баллы: {escape(_value(score))}\n\n"
        "Сейчас доступно:\n"
        f"🟢 Безопасные: {counts[FILTER_SAFE]}\n"
        f"🟡 Реалистичные: {counts[FILTER_REALISTIC]}\n"
        f"🔴 Амбициозные: {counts[FILTER_AMBITIOUS]}\n"
        f"Бюджет: {counts[FILTER_BUDGET]}\n"
        f"Платное: {counts[FILTER_PAID]}\n\n"
        "Выбери, что показать:"
    )


def build_filtered_results_message(
    profile: dict[str, Any] | None,
    all_results: list[dict[str, Any]],
    filtered_results: list[dict[str, Any]],
    filter_name: str,
) -> str:
    score = _score(profile.get("score") if isinstance(profile, dict) else None)
    title = format_filter_title(filter_name)
    total = len([item for item in all_results if isinstance(item, dict)])
    filtered = [item for item in filtered_results if isinstance(item, dict)]

    if not filtered:
        return (
            f"<b>Фильтр: {escape(title)}</b>\n\n"
            f"Найдено: 0 из {total}\n\n"
            f"По фильтру «{escape(title)}» вариантов нет.\n\n"
            "Можно попробовать:\n"
            "- выбрать другой фильтр;\n"
            "- сделать новый подбор;\n"
            "- посмотреть советы по подбору."
        )

    cards = "\n\n".join(
        format_university_card(index, item, score)
        for index, item in enumerate(filtered, start=1)
    )
    return (
        f"<b>Фильтр: {escape(title)}</b>\n\n"
        f"Найдено: {len(filtered)} из {total}\n\n"
        f"{cards}\n\n"
        "Проходные баллы могут меняться, поэтому перед подачей документов нужно проверить информацию на сайте вуза."
    )


def _item_category(item: dict[str, Any], user_score: int | None) -> str | None:
    existing = str(item.get("category") or "").strip().lower()
    if existing in {CATEGORY_SAFE, CATEGORY_REALISTIC, CATEGORY_AMBITIOUS}:
        return existing
    if user_score is None:
        return None
    return classify_university(user_score, item)


def _item_type(item: dict[str, Any]) -> str | None:
    return normalize_education_type(str(item.get("type") or ""))


def _score(value: Any) -> int | None:
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.strip().isdigit():
        return int(value.strip())
    return None


def _education_type_text(value: Any) -> str:
    label = education_type_label(str(value or ""))
    if label == "не указан":
        return "не указано"
    return label[:1].upper() + label[1:]


def _value(value: Any, fallback: str = "не указано") -> str:
    if value is None or value == "":
        return fallback
    return str(value)
