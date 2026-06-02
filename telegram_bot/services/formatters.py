from html import escape
from typing import Any

from telegram_bot.services.recommendation import (
    classify_university,
    format_score_delta,
    get_recommendation_label,
)
from telegram_bot.services.scores import is_suspicious_score, is_valid_score, score_display, score_note


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
    lines = [f"{header_prefix}<b>{index}. {escape(title)}</b>"]
    location = location_text(item)
    if location:
        lines.append(f"📍 {escape(location)}")

    if user_score is not None:
        category = classify_university(user_score, item)
        lines.append(f"{category_emoji(category)} Категория: {escape(category_text(category))}")

    subjects = subjects_text(item)
    if subjects:
        lines.append(f"📚 Предметы: {escape(subjects)}")

    lines.append(f"📊 {escape(score_line_text(item))}")

    if user_score is not None:
        lines.append(f"✅ Твои баллы: {user_score}")
        if is_valid_score(item.get("min_score")):
            lines.append(format_delta_line(user_score, item))

    lines.append(f"🎯 Финансирование: {escape(financing_text(item))}")
    admission_type = contest_text(item)
    if admission_type:
        lines.append(f"🎫 Конкурс: {escape(admission_type)}")
    short_name = short_name_text(item)
    if short_name:
        lines.append(f"🏷 Краткое название: {escape(short_name)}")

    if has_display_value(item.get("price")):
        lines.append(f"💰 Стоимость: {escape(format_price(item.get('price')))}")

    study_form = study_form_text(item)
    if study_form:
        lines.append(f"🏫 Форма обучения: {escape(study_form)}")
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
    elif include_note and score_note(item.get("min_score")):
        lines.extend(["", f"Пометка: {escape(score_note(item.get('min_score')))}."])

    return "\n".join(lines)


def title_short(item: dict[str, Any]) -> str:
    university = display_university_name(item)
    program = text_value(item.get("program"), "программа не указана")
    return f"{university} — {program}"


def display_university_name(item: dict[str, Any]) -> str:
    for key in ("university_full_name", "university_name", "university"):
        value = item.get(key)
        if has_display_value(value) and not is_technical_university_name(value):
            return str(value)
    for key in ("university", "university_short_name"):
        value = item.get(key)
        if has_display_value(value):
            return str(value)
    return "Вуз"


def location_text(item: dict[str, Any]) -> str:
    city = text_value(item.get("city"), "")
    region = text_value(item.get("region"), "")
    if city and region and not same_location_name(city, region):
        return f"{city}, {region}"
    return city or region


def short_name_text(item: dict[str, Any]) -> str:
    short_name = normalize_short_name_display(item.get("university_short_name"), display_university_name(item))
    if not short_name:
        return ""
    display_name = display_university_name(item)
    if normalize_label(short_name) == normalize_label(display_name):
        return ""
    if is_technical_university_name(short_name):
        return ""
    return short_name


def score_line_text(item: dict[str, Any]) -> str:
    min_score = item.get("min_score")
    if is_valid_score(min_score):
        return f"Проходной балл: {score_display(min_score)}"
    if is_suspicious_score(min_score):
        return f"Минимальный балл: {score_display(min_score)}"
    return f"Проходной балл: {score_display(min_score)}"


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
        "target_quota": "целевая квота",
        "целевая": "целевая квота",
        "целевая_квота": "целевая квота",
        "special": "особая квота",
        "special_quota": "особая квота",
        "особая_квота": "особая квота",
        "separate": "отдельная квота",
        "separate_quota": "отдельная квота",
        "individual_quota": "отдельная квота",
        "отдельная_квота": "отдельная квота",
        "additional": "дополнительный набор",
        "дополнительный_набор": "дополнительный набор",
        "общий_бюджет": "общий конкурс",
        "общий_конкурс": "общий конкурс",
        "budget": "бюджет",
        "бюджет": "бюджет",
        "paid": "платное",
        "платное": "платное",
    }.get(normalized, str(value).strip() if has_display_value(value) else "")


def financing_text(item: dict[str, Any]) -> str:
    value = item.get("financing_label", item.get("type"))
    normalized = normalize_label(value)
    if normalized in {"budget", "бюджет", "бюджетное", "бюджетный"}:
        return "бюджет"
    if normalized in {"paid", "платное", "платный", "контракт"}:
        return "платное"
    return text_value(value)


def study_form_text(item: dict[str, Any]) -> str:
    return text_value(item.get("study_form_label", item.get("study_form")), "")


def contest_text(item: dict[str, Any]) -> str:
    label = admission_type_text(item.get("contest_label") or item.get("admission_type_label") or item.get("admission_type"))
    if normalize_label(label) in {"budget", "бюджет", "paid", "платное", "общий_конкурс"}:
        return ""
    return label


def normalize_label(value: Any) -> str:
    return str(value or "").strip().lower().replace(" ", "_").replace("-", "_")


def normalize_short_name_display(value: Any, full_name: Any = "") -> str:
    text = text_value(value, "")
    if not text:
        return ""
    normalized = text.upper().replace("Ё", "Е")
    if normalize_label(normalized) == normalize_label(full_name):
        return ""
    if is_technical_university_name(text):
        return ""
    compact = normalized.replace(" ", "").replace(".", "")
    if any(char.isdigit() for char in compact):
        return ""
    letters_count = sum(1 for char in compact if char.isalpha())
    if 2 <= letters_count <= 16 and len(normalized) <= 24:
        return normalized
    return ""


def same_location_name(left: Any, right: Any) -> bool:
    left_text = normalize_location_name(left)
    right_text = normalize_location_name(right)
    return bool(left_text and right_text and left_text == right_text)


def normalize_location_name(value: Any) -> str:
    text = str(value or "").strip().lower().replace("ё", "е")
    for prefix in ("г. ", "город ", "республика "):
        if text.startswith(prefix):
            text = text.removeprefix(prefix)
    return " ".join(text.split())


def is_technical_university_name(value: Any) -> bool:
    text = str(value or "").strip()
    if not text:
        return False
    known_abbreviations = {"МГУ", "СПБГУ", "МФТИ", "МИРЭА", "КФУ", "РУДН", "ВШЭ", "МАИ", "МЭИ", "МГТУ"}
    normalized = text.upper().replace("Ё", "Е")
    if normalized in known_abbreviations:
        return False
    if any(char.isdigit() for char in text):
        return True
    if len(text) <= 2 and text.upper() == text and any(char.isalpha() for char in text):
        return True
    if "-" in text and any(char.isdigit() for char in text) and len(text) <= 12:
        letters = text.replace("-", "").replace("_", "")
        return all(char.isalpha() or char.isdigit() for char in letters)
    return False


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
