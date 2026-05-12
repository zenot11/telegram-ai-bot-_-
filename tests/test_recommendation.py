from telegram_bot.services.recommendation import (
    CATEGORY_AMBITIOUS,
    CATEGORY_REALISTIC,
    CATEGORY_SAFE,
    CATEGORY_UNAVAILABLE,
    classify_university,
    format_recommendation_summary,
    group_universities_by_recommendation,
)


def university(min_score: int) -> dict:
    return {"university": "Тестовый вуз", "min_score": min_score}


def test_classifies_safe_option() -> None:
    assert classify_university(230, university(180)) == CATEGORY_SAFE


def test_classifies_realistic_option() -> None:
    assert classify_university(230, university(220)) == CATEGORY_REALISTIC


def test_classifies_ambitious_option() -> None:
    assert classify_university(230, university(240)) == CATEGORY_AMBITIOUS


def test_classifies_unavailable_option() -> None:
    assert classify_university(230, university(260)) == CATEGORY_UNAVAILABLE


def test_groups_universities_by_recommendation() -> None:
    groups = group_universities_by_recommendation(
        230,
        [university(180), university(220), university(240), university(260)],
    )

    assert len(groups[CATEGORY_SAFE]) == 1
    assert len(groups[CATEGORY_REALISTIC]) == 1
    assert len(groups[CATEGORY_AMBITIOUS]) == 1
    assert len(groups[CATEGORY_UNAVAILABLE]) == 1


def test_recommendation_summary_mentions_categories() -> None:
    groups = group_universities_by_recommendation(
        230,
        [university(180), university(220), university(240)],
    )

    text = format_recommendation_summary(groups)

    assert "Безопасные" in text
    assert "Реалистичные" in text
    assert "Амбициозные" in text
    assert "не гарантия поступления" in text
