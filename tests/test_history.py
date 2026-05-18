from telegram_bot.services.history import build_history_entry, format_history_message
from telegram_bot.storage.user_data import UserDataStorage


def profile(region: str = "Адыгея", score: int = 230, direction: str = "IT", education_type: str = "budget") -> dict:
    return {
        "region": region,
        "score": score,
        "direction": direction,
        "education_type": education_type,
    }


def university(name: str = "АГУ", min_score: int = 185) -> dict:
    return {
        "university": name,
        "city": "Майкоп",
        "program": "Прикладная информатика",
        "direction": "IT",
        "subjects": ["русский язык", "математика", "информатика"],
        "min_score": min_score,
        "type": "бюджет",
        "price": None,
        "url": "https://example.ru",
    }


def test_build_history_entry_keeps_short_search_summary() -> None:
    entry = build_history_entry(profile(), [university("АГУ", 185), university("МГТУ", 225)])

    assert entry["region"] == "Адыгея"
    assert entry["score"] == 230
    assert entry["direction"] == "IT"
    assert entry["type"] == "бюджет"
    assert entry["total_results"] == 2
    assert entry["categories_count"]["safe"] == 1
    assert entry["categories_count"]["realistic"] == 1
    assert len(entry["top_items"]) == 2
    assert entry["top_items"][0]["university"] == "АГУ"


def test_storage_adds_history_newest_first_and_limits_to_five(tmp_path) -> None:
    storage = UserDataStorage(str(tmp_path / "user_data.json"))

    for index in range(7):
        storage.add_search_history(
            123,
            profile(region=f"Регион {index}", score=200 + index),
            [university(f"Вуз {index}", 170 + index)],
        )

    history = storage.get_search_history(123)

    assert len(history) == 5
    assert history[0]["region"] == "Регион 6"
    assert history[-1]["region"] == "Регион 2"


def test_clear_history_clears_only_history(tmp_path) -> None:
    storage = UserDataStorage(str(tmp_path / "user_data.json"))

    storage.save_profile(123, profile())
    storage.save_last_results(123, [university()])
    storage.add_favorite(123, university())
    storage.add_search_history(123, profile(), [university()])
    storage.clear_search_history(123)

    assert storage.get_search_history(123) == []
    assert storage.get_profile(123)["region"] == "Адыгея"
    assert storage.get_last_results(123)
    assert storage.get_favorites(123)


def test_reset_profile_clears_history(tmp_path) -> None:
    storage = UserDataStorage(str(tmp_path / "user_data.json"))

    storage.add_search_history(123, profile(), [university()])
    storage.reset_profile(123)

    assert storage.get_search_history(123) == []


def test_empty_results_history_is_saved_and_formatted() -> None:
    entry = build_history_entry(profile(region="Москва", score=260, direction="экономика"), [])
    text = format_history_message([entry])

    assert "Москва · экономика · Бюджет" in text
    assert "Найдено: 0" in text
    assert "Топ: вариантов не найдено" in text
    assert "None" not in text
    assert "null" not in text


def test_empty_history_message_is_helpful() -> None:
    text = format_history_message([])

    assert "История подборов пока пустая" in text
    assert "/search" in text


def test_history_keeps_normalized_values() -> None:
    entry = build_history_entry(profile(region="Адыгея", direction="IT", education_type="budget"), [university()])

    assert entry["region"] == "Адыгея"
    assert entry["direction"] == "IT"
    assert entry["type"] == "бюджет"
