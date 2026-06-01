from datetime import datetime
from typing import Any

from telegram_bot.services.advice import build_next_steps
from telegram_bot.services.formatters import (
    admission_type_text,
    format_price,
    has_display_value,
    normalize_label,
    subjects_text,
    text_value,
    title_short,
)
from telegram_bot.services.recommendation import (
    CATEGORY_AMBITIOUS,
    CATEGORY_REALISTIC,
    CATEGORY_SAFE,
    classify_university,
    format_score_delta,
)
from telegram_bot.services.scores import is_valid_score, score_display, score_note
from telegram_bot.services.summary import count_categories
from telegram_bot.services.validation import education_type_label


EXPORT_MESSAGE_LIMIT = 3500
EXPORT_FILENAME = "aisha_export.txt"


def build_export_preview(
    profile: dict[str, Any] | None,
    results: list[dict[str, Any]],
    favorites: list[dict[str, Any]] | None = None,
) -> str:
    if not _has_export_context(profile, results):
        return "Пока нет результата для экспорта.\nСначала сделай подбор через /search."

    safe_profile = profile or {}
    safe_results = _safe_items(results)
    safe_favorites = _safe_items(favorites or [])
    score = _score(safe_profile.get("score"))
    counts = count_categories(safe_results, score) if score is not None else _empty_counts()

    return (
        "<b>Экспорт результата</b>\n\n"
        "Я могу подготовить отчёт по последнему подбору.\n"
        "В отчёте будут параметры поиска, найденные варианты, избранные вузы и короткие советы.\n\n"
        f"Найдено вариантов: {len(safe_results)}\n"
        f"Безопасные: {counts[CATEGORY_SAFE]}\n"
        f"Реалистичные: {counts[CATEGORY_REALISTIC]}\n"
        f"Амбициозные: {counts[CATEGORY_AMBITIOUS]}\n"
        f"В избранном: {len(safe_favorites)}\n\n"
        "Выбери формат:"
    )


def build_export_report(
    profile: dict[str, Any] | None,
    results: list[dict[str, Any]],
    favorites: list[dict[str, Any]] | None = None,
    exported_at: datetime | None = None,
) -> str:
    if not _has_export_context(profile, results):
        return (
            "Аиша — отчёт по подбору вузов\n\n"
            "Пока нет результата для экспорта.\n"
            "Сначала сделай подбор через /search."
        )

    safe_profile = profile or {}
    safe_results = _safe_items(results)
    safe_favorites = _safe_items(favorites or [])
    score = _score(safe_profile.get("score"))
    counts = count_categories(safe_results, score) if score is not None else _empty_counts()
    export_date = exported_at or datetime.now()

    lines = [
        "Аиша — отчёт по подбору вузов",
        "",
        f"Дата экспорта: {export_date.strftime('%d.%m.%Y %H:%M')}",
        "",
        "Параметры подбора:",
        f"Регион: {_value(safe_profile.get('region'))}",
        f"Направление: {_value(safe_profile.get('direction'))}",
        f"Тип обучения: {_education_type_text(safe_profile.get('education_type'))}",
        f"Баллы ЕГЭ: {_value(safe_profile.get('score'))}",
        "",
        "Итог:",
        f"Найдено вариантов: {len(safe_results)}",
        f"Безопасные: {counts[CATEGORY_SAFE]}",
        f"Реалистичные: {counts[CATEGORY_REALISTIC]}",
        f"Амбициозные: {counts[CATEGORY_AMBITIOUS]}",
        f"В избранном: {len(safe_favorites)}",
        "",
        "Варианты:",
    ]
    lines.extend(_format_items(safe_results, score))

    if safe_favorites:
        lines.extend(["", "Избранные варианты:"])
        lines.extend(_format_items(safe_favorites, score))

    lines.extend(["", "Советы:"])
    lines.extend(f"- {step}" for step in build_next_steps(safe_profile, safe_results, safe_favorites)[:4])
    lines.extend(
        [
            "",
            "Важно:",
            (
                "Данные демонстрационные. Проходные баллы могут меняться каждый год. "
                "Перед подачей документов нужно проверить информацию на официальном сайте вуза."
            ),
        ]
    )
    return _clean_export_text("\n".join(lines))


def split_message(text: str, limit: int = EXPORT_MESSAGE_LIMIT) -> list[str]:
    if len(text) <= limit:
        return [text]

    parts: list[str] = []
    remaining = text
    while len(remaining) > limit:
        split_at = remaining.rfind("\n\n", 0, limit)
        if split_at <= 0:
            split_at = remaining.rfind("\n", 0, limit)
        if split_at <= 0:
            split_at = limit
        parts.append(remaining[:split_at].strip())
        remaining = remaining[split_at:].strip()
    if remaining:
        parts.append(remaining)
    return parts


def make_export_filename(user_id: int | None = None) -> str:
    return EXPORT_FILENAME


def _format_items(items: list[dict[str, Any]], score: int | None) -> list[str]:
    if not items:
        return ["Варианты не найдены."]

    blocks: list[str] = []
    for index, item in enumerate(items, start=1):
        category = _category_text(classify_university(score, item) if score is not None else "")
        block = [
            "",
            f"{index}. {title_short(item)}",
            f"Город: {text_value(item.get('city'))}",
            f"Категория: {category}",
            f"Проходной балл: {score_display(item.get('min_score'))}",
        ]
        subjects = subjects_text(item)
        if subjects:
            block.insert(4, f"Предметы: {subjects}")
        if score is not None:
            block.append(f"Твои баллы: {score}")
            if is_valid_score(item.get("min_score")):
                block.append(format_score_delta(score, item))

        block.append(f"Тип: {text_value(item.get('type'))}")
        admission_type = admission_type_text(item.get("admission_type_label") or item.get("admission_type"))
        if admission_type and admission_type not in {normalize_label(item.get("type")), "бюджет", "платное"}:
            block.append(f"Конкурс: {admission_type}")
        if has_display_value(item.get("price")):
            block.append(f"Стоимость: {format_price(item.get('price'))}")
        if has_display_value(item.get("study_form")):
            block.append(f"Форма: {item['study_form']}")
        if has_display_value(item.get("duration")):
            block.append(f"Срок: {item['duration']}")
        if has_display_value(item.get("faculty")):
            block.append(f"Факультет: {item['faculty']}")
        if has_display_value(item.get("year")):
            block.append(f"Год данных: {item['year']}")
        if has_display_value(item.get("note")):
            block.append(f"Пометка: {item['note']}")
        elif score_note(item.get("min_score")):
            block.append(f"Пометка: {score_note(item.get('min_score'))}")
        if has_display_value(item.get("url")):
            block.append(f"Сайт: {item['url']}")
        blocks.append("\n".join(str(line) for line in block))
    return blocks


def _has_export_context(profile: dict[str, Any] | None, results: list[dict[str, Any]]) -> bool:
    return isinstance(profile, dict) and bool(_safe_items(results))


def _safe_items(items: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    return [item for item in items or [] if isinstance(item, dict)]


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


def _category_text(category: str) -> str:
    return {
        CATEGORY_SAFE: "безопасный вариант",
        CATEGORY_REALISTIC: "реалистичный вариант",
        CATEGORY_AMBITIOUS: "амбициозный вариант",
    }.get(category, "не указана")


def _empty_counts() -> dict[str, int]:
    return {
        CATEGORY_SAFE: 0,
        CATEGORY_REALISTIC: 0,
        CATEGORY_AMBITIOUS: 0,
    }


def _value(value: Any) -> str:
    return text_value(value)


def _clean_export_text(text: str) -> str:
    forbidden = ("None", "null", "undefined")
    cleaned = text
    for value in forbidden:
        cleaned = cleaned.replace(value, "не указано")
    return cleaned
