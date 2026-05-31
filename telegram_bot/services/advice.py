from html import escape
from typing import Any

from telegram_bot.services.recommendation import CATEGORY_AMBITIOUS, CATEGORY_REALISTIC, CATEGORY_SAFE
from telegram_bot.services.summary import count_categories
from telegram_bot.services.validation import education_type_label


EMPTY_ADVICE_TEXT = (
    "Пока нет последнего подбора.\n"
    "Сначала сделай подбор через /search."
)


def has_advice_context(profile: dict[str, Any] | None) -> bool:
    if not isinstance(profile, dict):
        return False
    return all(profile.get(key) not in (None, "") for key in ("region", "score", "direction", "education_type"))


def build_advice(
    profile: dict[str, Any] | None,
    results: list[dict[str, Any]],
    favorites: list[dict[str, Any]] | None = None,
) -> str:
    if not has_advice_context(profile):
        return EMPTY_ADVICE_TEXT

    safe_profile = profile or {}
    safe_results = [item for item in results if isinstance(item, dict)]
    safe_favorites = [item for item in favorites or [] if isinstance(item, dict)]
    balance = analyze_result_balance(safe_results, safe_profile.get("score"))
    next_steps = build_next_steps(safe_profile, safe_results, safe_favorites)
    next_action = _next_action(balance["total"], bool(safe_favorites))

    lines = [
        "<b>Советы по последнему подбору</b>",
        "",
        "<b>Запрос:</b>",
        (
            f"{escape(_value(safe_profile.get('region')))} · "
            f"{escape(_value(safe_profile.get('direction')))} · "
            f"{escape(_education_type_text(safe_profile.get('education_type')))}"
        ),
        f"Баллы: {escape(_value(safe_profile.get('score')))}",
        f"Найдено вариантов: {balance['total']}",
        "",
        "<b>Оценка:</b>",
        escape(_build_assessment(balance)),
        "",
        "<b>Что сделать дальше:</b>",
    ]
    lines.extend(f"{index}. {escape(step)}" for index, step in enumerate(next_steps, start=1))
    lines.extend(
        [
            "",
            "<b>Следующий шаг:</b>",
            escape(next_action),
            "",
            "Проходные баллы могут меняться, поэтому перед подачей документов нужно проверить информацию на сайте вуза.",
        ]
    )
    return "\n".join(lines)


def analyze_result_balance(results: list[dict[str, Any]], user_score: Any = None) -> dict[str, int]:
    score = _score(user_score)
    counts = count_categories(results, score) if score is not None else {
        CATEGORY_SAFE: 0,
        CATEGORY_REALISTIC: 0,
        CATEGORY_AMBITIOUS: 0,
    }
    return {
        "total": len([item for item in results if isinstance(item, dict)]),
        CATEGORY_SAFE: counts.get(CATEGORY_SAFE, 0),
        CATEGORY_REALISTIC: counts.get(CATEGORY_REALISTIC, 0),
        CATEGORY_AMBITIOUS: counts.get(CATEGORY_AMBITIOUS, 0),
    }


def build_next_steps(
    profile: dict[str, Any],
    results: list[dict[str, Any]],
    favorites: list[dict[str, Any]] | None = None,
) -> list[str]:
    balance = analyze_result_balance(results, profile.get("score"))
    favorites_count = len([item for item in favorites or [] if isinstance(item, dict)])
    steps: list[str] = []

    if balance["total"] == 0:
        steps.extend(
            [
                "Проверь, правильно ли указаны баллы.",
                "Попробуй соседний регион или регион с большим количеством вузов.",
                "Попробуй более широкую формулировку направления.",
            ]
        )
    elif balance[CATEGORY_AMBITIOUS] > 0 and balance[CATEGORY_SAFE] == 0 and balance[CATEGORY_REALISTIC] == 0:
        steps.extend(
            [
                "Добавь 1–2 более спокойных варианта с меньшим минимальным баллом.",
                "Попробуй соседний регион или регион с большим количеством вузов.",
                "Проверь похожие направления, где требования могут быть мягче.",
            ]
        )
    elif balance[CATEGORY_SAFE] > 0:
        steps.append("Сохрани 1–2 самых подходящих вуза, чтобы не потерять спокойные варианты.")
    else:
        steps.append("Оставь запасной вариант: другой регион, похожее направление или другой тип обучения.")

    if balance["total"] > 0:
        if favorites_count:
            steps.append("Сравни избранные варианты через /compare.")
        else:
            steps.append("Сохрани 1–2 варианта в избранное, а потом сравни их через /compare.")

    education_type = str(profile.get("education_type") or "")
    if education_type == "budget" and balance["total"] <= 2:
        steps.append("Для запаса можно рассмотреть платное обучение.")
    elif education_type == "paid":
        if any(_has_price(item) for item in results if isinstance(item, dict)):
            steps.append("Проверь стоимость, скидки и условия оплаты на сайте вуза.")
        else:
            steps.append("Проверь стоимость, скидки и условия оплаты на официальном сайте вуза.")

    direction_step = _direction_step(profile.get("direction"))
    if direction_step:
        steps.append(direction_step)

    steps.append("Для более наглядного просмотра можно открыть Mini App через /webapp.")
    return _dedupe(steps)[:6]


def _build_assessment(balance: dict[str, int]) -> str:
    total = balance["total"]
    safe = balance[CATEGORY_SAFE]
    realistic = balance[CATEGORY_REALISTIC]
    ambitious = balance[CATEGORY_AMBITIOUS]

    if total == 0:
        return "По этим параметрам варианты не нашлись."
    if safe >= 2:
        return "Подбор выглядит достаточно спокойным: есть несколько безопасных вариантов с запасом по баллам."
    if safe > 0 and realistic > 0:
        return "Подбор выглядит сбалансированным: есть спокойные варианты и варианты ближе к проходному уровню."
    if realistic > 0 and safe == 0:
        return "Подбор выглядит рабочим, но запас небольшой. Лучше добавить 1–2 более спокойных варианта."
    if ambitious > 0 and safe == 0 and realistic == 0:
        return "Сейчас подбор больше амбициозный. Такие варианты можно оставить как цель, но стоит добавить более спокойные маршруты."
    if total <= 2:
        return "Вариантов немного, поэтому лучше расширить поиск и оставить запасной маршрут."
    return "Подбор можно использовать как стартовую точку: дальше стоит сохранить и сравнить несколько вариантов."


def _direction_step(value: Any) -> str | None:
    direction = str(value or "").strip().lower()
    if not direction:
        return None
    if direction == "it":
        return "Для IT можно также проверить информатику, цифровые технологии, программную инженерию и информационные системы."
    if direction == "экономика":
        return "Для экономики можно также проверить менеджмент, бизнес-информатику и финансы."
    if direction == "медицина":
        return "Для медицины можно также проверить биологию, сестринское дело или фармацию, если такие варианты есть в базе."
    if direction == "юриспруденция":
        return "Для юриспруденции можно также посмотреть государственное управление или экономику."
    return "Если вариантов мало, попробуй более широкую формулировку направления."


def _next_action(total: int, has_favorites: bool) -> str:
    if total == 0:
        return "Запусти новый подбор через /search."
    if has_favorites:
        return "Открой /compare и сравни избранные варианты."
    return "Открой /summary, сохрани 1–2 варианта и сравни их через /compare."


def _score(value: Any) -> int | None:
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.strip().isdigit():
        return int(value.strip())
    return None


def _has_price(item: dict[str, Any]) -> bool:
    value = item.get("price")
    return value is not None and str(value).strip() != ""


def _education_type_text(value: Any) -> str:
    label = education_type_label(str(value or ""))
    if label == "не указан":
        return "не указано"
    return label[:1].upper() + label[1:]


def _value(value: Any, fallback: str = "не указано") -> str:
    if value is None or value == "":
        return fallback
    return str(value)


def _dedupe(items: list[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for item in items:
        if item not in seen:
            result.append(item)
            seen.add(item)
    return result
