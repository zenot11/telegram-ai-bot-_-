from html import escape
from typing import Any


def compare_universities(items: list[dict[str, Any]]) -> dict[str, Any]:
    selected = [item for item in items if isinstance(item, dict)]
    return {
        "items": selected,
        "safe_option": get_min_score_safe_option(selected),
        "ambitious_option": get_max_score_ambitious_option(selected),
        "cheapest_paid_option": get_cheapest_paid_option(selected),
        "has_enough_items": len(selected) >= 2,
    }


def format_comparison(items: list[dict[str, Any]]) -> str:
    comparison = compare_universities(items)
    selected = comparison["items"]

    if len(selected) < 2:
        return (
            "Для сравнения нужно минимум два варианта. "
            "Пройди подбор ещё раз или сохрани несколько вузов в избранное."
        )

    cards = "\n\n".join(_format_item(index, item) for index, item in enumerate(selected, start=1))
    conclusion = _format_conclusion(comparison)

    return (
        "Сравнение вузов:\n\n"
        f"{cards}\n\n"
        "Вывод:\n"
        f"{conclusion}\n"
        "- Данные демонстрационные, для финального решения нужно сверить их с официальным сайтом вуза."
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


def get_cheapest_paid_option(items: list[dict[str, Any]]) -> dict[str, Any] | None:
    paid = [item for item in items if _price(item) is not None]
    if not paid:
        return None
    return min(paid, key=lambda item: _price(item) or 0)


def _format_item(index: int, item: dict[str, Any]) -> str:
    subjects = item.get("subjects")
    subjects_text = ", ".join(subjects) if isinstance(subjects, list) and subjects else "не указаны"

    return (
        f"<b>{index}. {escape(_text(item.get('university'), 'Вуз не указан'))}</b>\n"
        f"Город: {escape(_text(item.get('city')))}\n"
        f"Программа: {escape(_text(item.get('program')))}\n"
        f"Направление: {escape(_text(item.get('direction')))}\n"
        f"Предметы: {escape(subjects_text)}\n"
        f"Мин. балл: {escape(_text(item.get('min_score')))}\n"
        f"Тип: {escape(_text(item.get('type')))}\n"
        f"Стоимость: {escape(_format_price(item.get('price')))}\n"
        f"Сайт: {escape(_text(item.get('url')))}"
    )


def _format_conclusion(comparison: dict[str, Any]) -> str:
    lines: list[str] = []

    safe = comparison.get("safe_option")
    if safe:
        lines.append(f"- Самый безопасный по баллам вариант: {_title(safe)}.")
    else:
        lines.append("- Самый безопасный по баллам вариант определить нельзя: минимальные баллы не указаны.")

    ambitious = comparison.get("ambitious_option")
    if ambitious:
        lines.append(f"- Самый амбициозный по баллам вариант: {_title(ambitious)}.")
    else:
        lines.append("- Самый амбициозный вариант определить нельзя: минимальные баллы не указаны.")

    cheapest = comparison.get("cheapest_paid_option")
    if cheapest:
        lines.append(f"- Самый дешёвый платный вариант среди выбранных: {_title(cheapest)}.")

    lines.append("- Если нужен более безопасный вариант, лучше смотреть вуз с меньшим минимальным баллом.")
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
