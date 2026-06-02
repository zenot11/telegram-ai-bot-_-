from typing import Any


INVALID_SCORE_DISPLAY = "не указан"
INVALID_SCORE_NOTE = "балл требует уточнения"
MIN_REASONABLE_SCORE = 40
SUSPICIOUS_SCORE_NOTE = "минимальный балл требует проверки на сайте вуза"


def parse_score(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    if isinstance(value, str):
        text = value.strip()
        if text.isdigit() or (text.startswith("-") and text[1:].isdigit()):
            return int(text)
    return None


def is_valid_score(value: Any) -> bool:
    score = parse_score(value)
    return score is not None and score >= MIN_REASONABLE_SCORE


def is_suspicious_score(value: Any) -> bool:
    score = parse_score(value)
    return score is not None and 1 < score < MIN_REASONABLE_SCORE


def score_display(value: Any) -> str:
    score = parse_score(value)
    if score is None or score <= 1:
        return INVALID_SCORE_DISPLAY
    if is_suspicious_score(score):
        return f"{score} (требует уточнения)"
    return str(score)


def score_note(value: Any) -> str:
    score = parse_score(value)
    if score is not None and score <= 1:
        return INVALID_SCORE_NOTE
    if is_suspicious_score(score):
        return f"минимальный балл {score} требует проверки на сайте вуза"
    return ""


def score_delta_value(user_score: Any, min_score: Any) -> int | None:
    user_score_value = parse_score(user_score)
    min_score_value = parse_score(min_score)
    if user_score_value is None or min_score_value is None:
        return None
    if not is_valid_score(min_score_value):
        return None
    return user_score_value - min_score_value


def format_score_delta_value(delta: int | None) -> str:
    if delta is None:
        return "требует уточнения"
    if delta >= 0:
        return f"+{delta}"
    return f"{abs(delta)} баллов"


def format_score_delta_text(user_score: Any, min_score: Any) -> str:
    delta = score_delta_value(user_score, min_score)
    if delta is None:
        return "Запас по баллам: требует уточнения"
    if delta >= 0:
        return f"Запас: +{delta}"
    return f"Не хватает: {abs(delta)} баллов"
