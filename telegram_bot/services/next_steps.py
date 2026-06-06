from html import escape
from typing import Any


def build_next_steps_text(
    profile: dict[str, Any] | None,
    results: list[dict[str, Any]] | None,
) -> str:
    """Build a user-facing next-step message after the latest admission search."""

    safe_results = results if isinstance(results, list) else []
    if not safe_results:
        return (
            "Что делать дальше\n\n"
            "Сначала выполни подбор вузов. После этого я подскажу следующий шаг.\n\n"
            "Начать можно через /search."
        )

    safe_profile = profile if isinstance(profile, dict) else {}
    region = _text_value(safe_profile.get("region"), "регион не указан")
    direction = _text_value(safe_profile.get("direction"), "направление не указано")
    score = _text_value(safe_profile.get("score"), "баллы не указаны")
    education_type = _education_type_label(safe_profile.get("education_type"))

    return (
        "Что делать дальше\n\n"
        "Последний подбор:\n"
        f"{escape(region)} · {escape(direction)} · {escape(education_type)}\n"
        f"Баллы: {escape(score)}\n"
        f"Найдено вариантов: {len(safe_results)}\n\n"
        "Следующие шаги:\n"
        "1. Сохрани 2–3 подходящих вуза.\n"
        "2. Сравни безопасные и реалистичные варианты.\n"
        "3. Проверь официальные сайты вузов: проходные баллы и условия могут меняться.\n"
        "4. Посмотри стоимость, город, программу, форму и срок обучения.\n"
        "5. Сформируй отчёт через /export или открой Mini App для наглядного сравнения.\n"
        "6. Используй /feedback, если заметил ошибку в данных или работе сервиса.\n\n"
        "Это не гарантия поступления, а спокойный план действий после подбора."
    )


def _education_type_label(value: Any) -> str:
    normalized = str(value or "").strip().lower()
    if normalized in {"budget", "бюджет", "бюджетное"}:
        return "Бюджет"
    if normalized in {"paid", "платное", "контракт"}:
        return "Платное"
    if normalized in {"any", "all", "любое", "любой", "любая", "все"}:
        return "Любое"
    return _text_value(value, "финансирование не указано")


def _text_value(value: Any, fallback: str) -> str:
    if value is None:
        return fallback
    text = str(value).strip()
    return text or fallback
