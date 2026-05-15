from telegram_bot.services.validation import parse_score


def test_parse_score_rejects_letters() -> None:
    score, error = parse_score("abc")

    assert score is None
    assert error is not None


def test_parse_score_rejects_negative_value() -> None:
    score, error = parse_score("-1")

    assert score is None
    assert error is not None


def test_parse_score_rejects_too_large_value() -> None:
    score, error = parse_score("401")

    assert score is None
    assert error is not None


def test_parse_score_accepts_valid_value() -> None:
    score, error = parse_score("230")

    assert score == 230
    assert error is None


def test_parse_score_strips_spaces() -> None:
    score, error = parse_score(" 230 ")

    assert score == 230
    assert error is None


def test_parse_score_accepts_points_with_word_suffix() -> None:
    score, error = parse_score("230 баллов")

    assert score == 230
    assert error is None


def test_parse_score_accepts_zero() -> None:
    score, error = parse_score("0")

    assert score == 0
    assert error is None


def test_parse_score_accepts_400() -> None:
    score, error = parse_score("400")

    assert score == 400
    assert error is None
