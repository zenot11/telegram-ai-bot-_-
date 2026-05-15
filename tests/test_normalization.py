from telegram_bot.services.validation import (
    normalize_direction,
    normalize_region,
    normalize_study_type,
)


def test_region_normalization_handles_common_aliases_and_typos() -> None:
    cases = {
        "Адыгеая": "Адыгея",
        " адыгея ": "Адыгея",
        "республика адыгея": "Адыгея",
        "адыгея республика": "Адыгея",
        "адыгея.": "Адыгея",
        "мск": "Москва",
        "moscow": "Москва",
        "спб": "Санкт-Петербург",
        "питер": "Санкт-Петербург",
        "крым": "Крым",
        "казан": "Татарстан",
        "свердловск": "Свердловская область",
    }

    for value, expected in cases.items():
        assert normalize_region(value) == expected


def test_unknown_region_returns_cleaned_value() -> None:
    assert normalize_region(" новый регион ") == "Новый регион"


def test_direction_normalization_handles_synonyms() -> None:
    cases = {
        "айти": "IT",
        "айт": "IT",
        "информатика": "IT",
        "программирование": "IT",
        "разработка": "IT",
        "компьютерные науки": "IT",
        "психфак": "психология",
        "мед": "медицина",
        "лечебное дело": "медицина",
        "юрист": "юриспруденция",
        "юридический": "юриспруденция",
        "стройка": "строительство",
        "техническое": "инженерия",
    }

    for value, expected in cases.items():
        assert normalize_direction(value) == expected


def test_unknown_direction_returns_cleaned_value() -> None:
    assert normalize_direction(" новая сфера ") == "новая сфера"


def test_study_type_normalization_handles_budget_and_paid_aliases() -> None:
    budget_cases = ["Бюджет", "бюджетное", "бюджетный", "бесплатно", "гос", "budget"]
    paid_cases = ["платное", "платный", "контракт", "договор", "коммерция", "paid"]

    for value in budget_cases:
        assert normalize_study_type(value) == "budget"

    for value in paid_cases:
        assert normalize_study_type(value) == "paid"
