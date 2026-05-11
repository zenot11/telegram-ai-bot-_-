MAX_TOTAL_SCORE = 310

EDUCATION_TYPE_LABELS = {
    "budget": "бюджет",
    "paid": "платное",
}


def parse_score(text: str) -> tuple[int | None, str | None]:
    value = text.strip().replace(" ", "")
    if not value.isdigit():
        return None, "Введи суммарные баллы числом, например: 230."

    score = int(value)
    if score < 0 or score > MAX_TOTAL_SCORE:
        return None, f"Проверь баллы: для MVP ожидаю сумму от 0 до {MAX_TOTAL_SCORE}."

    return score, None


def normalize_education_type(text: str) -> str | None:
    value = text.strip().lower().replace("ё", "е")
    if value in {"budget", "бюджет"} or "бюдж" in value:
        return "budget"
    if value in {"paid", "платное", "платно", "контракт"} or "плат" in value:
        return "paid"
    return None


def education_type_label(value: str) -> str:
    return EDUCATION_TYPE_LABELS.get(value, "не указан")
