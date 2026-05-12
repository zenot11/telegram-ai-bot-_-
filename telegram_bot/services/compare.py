from html import escape
from typing import Any

from telegram_bot.services.recommendation import (
    classify_university,
    format_score_delta,
    get_min_score,
    get_recommendation_label,
    score_delta,
)


def compare_universities(items: list[dict[str, Any]], user_score: int | None = None) -> dict[str, Any]:
    selected = [item for item in items if isinstance(item, dict)]
    return {
        "items": selected,
        "user_score": user_score,
        "safe_option": get_min_score_safe_option(selected),
        "ambitious_option": get_max_score_ambitious_option(selected),
        "largest_score_margin_option": get_largest_score_margin_option(selected, user_score),
        "closest_deficit_option": get_closest_deficit_option(selected, user_score),
        "cheapest_option": get_cheapest_option(selected),
        "cheapest_paid_option": get_cheapest_option(selected),
        "budget_options": sum(1 for item in selected if _is_budget(item)),
        "paid_options": sum(1 for item in selected if _is_paid(item)),
        "common_subjects": get_common_subjects(selected),
        "unique_subjects": get_unique_subjects(selected),
        "has_enough_items": len(selected) >= 2,
    }


def format_comparison(items: list[dict[str, Any]], user_score: int | None = None) -> str:
    comparison = compare_universities(items, user_score=user_score)
    selected = comparison["items"]

    if len(selected) < 2:
        return (
            "Для сравнения нужно минимум два варианта. "
            "Пройди подбор ещё раз или сохрани несколько вузов в избранное."
        )

    cards = "\n\n".join(_format_item(index, item, user_score) for index, item in enumerate(selected, start=1))
    conclusion = _format_conclusion(comparison)

    return (
        "<b>Сравнение вузов</b>\n\n"
        f"{cards}\n\n"
        "<b>Вывод:</b>\n"
        f"{conclusion}\n"
        "\nВажно: Данные демонстрационные для MVP. "
        "Для финальной версии нужно подключить настоящую базу вузов или backend API."
    )


def get_min_score_safe_option(items: list[dict[str, Any]]) -> dict[str, Any] | None:
    scored = [item for item in items if _score(item) is not None]
    if not scored:
        return None
    return min(scored, key=lambda item: _score(item) or 0)


def get_max_score_ambitious_option(items: list[dict[str, Any]]) -> dict[str, Any] | None:
    scored = [item for item in items if _score(item) is not None]
    if not scored:
        return None
    return max(scored, key=lambda item: _score(item) or 0)


def get_cheapest_option(items: list[dict[str, Any]]) -> dict[str, Any] | None:
    priced = [item for item in items if _price(item) is not None]
    if not priced:
        return None
    return min(priced, key=lambda item: _price(item) or 0)


def get_cheapest_paid_option(items: list[dict[str, Any]]) -> dict[str, Any] | None:
    return get_cheapest_option(items)


def get_largest_score_margin_option(
    items: list[dict[str, Any]],
    user_score: int | None,
) -> dict[str, Any] | None:
    if user_score is None:
        return None

    scored = [
        item
        for item in items
        if score_delta(user_score, item) is not None and (score_delta(user_score, item) or 0) >= 0
    ]
    if not scored:
        return None
    return max(scored, key=lambda item: score_delta(user_score, item) or -10_000)


def get_closest_deficit_option(
    items: list[dict[str, Any]],
    user_score: int | None,
) -> dict[str, Any] | None:
    if user_score is None:
        return None

    deficit_items = [
        item
        for item in items
        if score_delta(user_score, item) is not None and (score_delta(user_score, item) or 0) < 0
    ]
    if not deficit_items:
        return None
    return max(deficit_items, key=lambda item: score_delta(user_score, item) or -10_000)


def get_common_subjects(items: list[dict[str, Any]]) -> list[str]:
    subject_sets = [_subject_set(item) for item in items]
    subject_sets = [subjects for subjects in subject_sets if subjects]
    if len(subject_sets) < 2:
        return []
    return sorted(set.intersection(*subject_sets))


def get_unique_subjects(items: list[dict[str, Any]]) -> list[str]:
    subject_sets = [_subject_set(item) for item in items]
    subject_sets = [subjects for subjects in subject_sets if subjects]
    if len(subject_sets) < 2:
        return []

    common = set(get_common_subjects(items))
    all_subjects = set.union(*subject_sets)
    return sorted(all_subjects - common)


def _format_item(index: int, item: dict[str, Any], user_score: int | None) -> str:
    subjects = item.get("subjects")
    subjects_text = ", ".join(subjects) if isinstance(subjects, list) and subjects else "не указаны"
    category_line = ""
    score_lines = ""
    if user_score is not None:
        category = classify_university(user_score, item)
        category_line = f"Категория: {escape(get_recommendation_label(category))}\n"
        score_lines = (
            f"Твои баллы: {user_score}\n"
            f"{escape(format_score_delta(user_score, item))}\n"
        )

    return (
        f"<b>{index}. {escape(_title_short(item))}</b>\n"
        f"Город: {escape(_text(item.get('city')))}\n"
        f"Мин. балл: {escape(_text(item.get('min_score')))}\n"
        f"{category_line}"
        f"{score_lines}"
        f"Тип: {escape(_text(item.get('type')))}\n"
        f"Стоимость: {escape(_format_price(item.get('price')))}\n"
        f"Предметы: {escape(subjects_text)}\n"
        f"Сайт: {escape(_text(item.get('url')))}"
    )


def _format_conclusion(comparison: dict[str, Any]) -> str:
    lines: list[str] = []
    user_score = comparison.get("user_score")

    safe = comparison.get("safe_option")
    if safe:
        if isinstance(user_score, int):
            lines.append(
                f"Более спокойный вариант: {escape(_title_short(safe))}. "
                f"{escape(format_score_delta(user_score, safe))}."
            )
        else:
            lines.append(f"Самый безопасный вариант по баллам: {escape(_title_short(safe))}, потому что минимальный балл ниже.")
    else:
        lines.append("Самый безопасный вариант по баллам определить нельзя: минимальные баллы не указаны.")

    ambitious = comparison.get("ambitious_option")
    if ambitious:
        if isinstance(user_score, int):
            lines.append(
                f"Более амбициозный вариант: {escape(_title_short(ambitious))}. "
                f"{escape(format_score_delta(user_score, ambitious))}."
            )
        else:
            lines.append(f"Более амбициозный вариант: {escape(_title_short(ambitious))}, потому что минимальный балл выше.")
    else:
        lines.append("Более амбициозный вариант определить нельзя: минимальные баллы не указаны.")

    if isinstance(user_score, int):
        largest_margin = comparison.get("largest_score_margin_option")
        closest_deficit = comparison.get("closest_deficit_option")
        if largest_margin:
            lines.append(f"Больше всего запас по баллам у варианта: {escape(_title_short(largest_margin))}.")
        if closest_deficit:
            lines.append(f"Баллов пока не хватает для варианта: {escape(_title_short(closest_deficit))}.")

    budget_count = comparison.get("budget_options", 0)
    paid_count = comparison.get("paid_options", 0)
    lines.append(f"По типу обучения: бюджетных вариантов — {budget_count}, платных — {paid_count}.")

    cheapest = comparison.get("cheapest_option")
    if cheapest:
        lines.append(f"По стоимости: самый дешёвый вариант среди выбранных — {escape(_title_short(cheapest))}.")
    elif comparison.get("budget_options") == len(comparison.get("items", [])):
        lines.append("По стоимости: все выбранные варианты бюджетные, стоимость не указана.")
    else:
        lines.append("По стоимости: недостаточно данных для сравнения.")

    common_subjects = comparison.get("common_subjects") or []
    unique_subjects = comparison.get("unique_subjects") or []
    if common_subjects:
        lines.append(f"Общие предметы: {escape(', '.join(common_subjects))}.")
        if unique_subjects:
            lines.append(f"Отличающиеся предметы: {escape(', '.join(unique_subjects))}.")
    elif unique_subjects:
        lines.append("Общих предметов не видно по тестовым данным.")
    else:
        lines.append("Предметы не указаны или данных недостаточно для сравнения.")

    return "\n".join(lines)


def _score(item: dict[str, Any]) -> int | None:
    value = item.get("min_score")
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return None


def _price(item: dict[str, Any]) -> int | None:
    value = item.get("price")
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return None


def _is_budget(item: dict[str, Any]) -> bool:
    return str(item.get("type", "")).strip().lower() in {"бюджет", "budget"}


def _is_paid(item: dict[str, Any]) -> bool:
    return str(item.get("type", "")).strip().lower() in {"платное", "paid"}


def _subject_set(item: dict[str, Any]) -> set[str]:
    subjects = item.get("subjects")
    if not isinstance(subjects, list):
        return set()
    return {str(subject).strip().lower() for subject in subjects if str(subject).strip()}


def _format_price(value: Any) -> str:
    if value is None or value == "":
        return "не указана"
    price = _price({"price": value})
    if price is None:
        return str(value)
    return f"{price:,} руб./год".replace(",", " ")


def _text(value: Any, fallback: str = "не указано") -> str:
    if value is None or value == "":
        return fallback
    return str(value)


def _title(item: dict[str, Any]) -> str:
    university = _text(item.get("university"), "Вуз")
    program = _text(item.get("program"), "программа не указана")
    score = _text(item.get("min_score"))
    return f"{university} — {program} (мин. балл: {score})"


def _title_short(item: dict[str, Any]) -> str:
    university = _text(item.get("university"), "Вуз")
    program = _text(item.get("program"), "программа не указана")
    return f"{university} — {program}"
