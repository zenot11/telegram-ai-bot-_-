from telegram_bot.storage.user_data import UserDataStorage


def sample_profile() -> dict:
    return {
        "region": "Адыгея",
        "score": 230,
        "direction": "IT",
        "education_type": "budget",
    }


def sample_university() -> dict:
    return {
        "university": "АГУ",
        "city": "Майкоп",
        "program": "Прикладная информатика",
        "min_score": 185,
        "type": "бюджет",
        "url": "https://www.adygnet.ru",
    }


def second_university() -> dict:
    return {
        "university": "МГТУ",
        "city": "Майкоп",
        "program": "Информационные системы и технологии",
        "min_score": 172,
        "type": "бюджет",
        "url": "https://mkgtu.ru",
    }


def test_new_user_has_empty_profile(tmp_path) -> None:
    storage = UserDataStorage(str(tmp_path / "user_data.json"))

    assert storage.get_profile(123) is None
    assert storage.get_last_results(123) == []
    assert storage.get_favorites(123) == []


def test_save_profile_stores_basic_fields(tmp_path) -> None:
    storage = UserDataStorage(str(tmp_path / "user_data.json"))

    storage.save_profile(123, sample_profile())

    profile = storage.get_profile(123)
    assert profile is not None
    assert profile["telegram_id"] == 123
    assert profile["region"] == "Адыгея"
    assert profile["score"] == 230
    assert profile["direction"] == "IT"
    assert profile["education_type"] == "budget"


def test_save_last_results(tmp_path) -> None:
    storage = UserDataStorage(str(tmp_path / "user_data.json"))
    item = sample_university()

    storage.save_last_results(123, [item])

    assert storage.get_last_results(123) == [item]


def test_add_favorite_does_not_duplicate(tmp_path) -> None:
    storage = UserDataStorage(str(tmp_path / "user_data.json"))
    item = sample_university()

    assert storage.add_favorite(123, item) is True
    assert storage.add_favorite(123, item) is False

    assert storage.get_favorites(123) == [item]


def test_clear_favorites(tmp_path) -> None:
    storage = UserDataStorage(str(tmp_path / "user_data.json"))

    storage.add_favorite(123, sample_university())
    storage.clear_favorites(123)

    assert storage.get_favorites(123) == []


def test_remove_favorite_removes_selected_item(tmp_path) -> None:
    storage = UserDataStorage(str(tmp_path / "user_data.json"))

    storage.add_favorite(123, sample_university())
    storage.add_favorite(123, second_university())

    removed = storage.remove_favorite(123, 0)

    assert removed is not None
    assert removed["university"] == "АГУ"
    favorites = storage.get_favorites(123)
    assert len(favorites) == 1
    assert favorites[0]["university"] == "МГТУ"


def test_remove_favorite_ignores_invalid_index(tmp_path) -> None:
    storage = UserDataStorage(str(tmp_path / "user_data.json"))

    storage.add_favorite(123, sample_university())

    assert storage.remove_favorite(123, 10) is None
    assert storage.remove_favorite(123, -1) is None
    assert len(storage.get_favorites(123)) == 1


def test_clear_favorites_after_remove(tmp_path) -> None:
    storage = UserDataStorage(str(tmp_path / "user_data.json"))

    storage.add_favorite(123, sample_university())
    storage.add_favorite(123, second_university())
    storage.remove_favorite(123, 0)
    storage.clear_favorites(123)

    assert storage.get_favorites(123) == []


def test_reset_profile_clears_profile_and_favorites(tmp_path) -> None:
    storage = UserDataStorage(str(tmp_path / "user_data.json"))

    storage.save_profile(123, sample_profile())
    storage.save_last_results(123, [sample_university()])
    storage.add_favorite(123, sample_university())
    storage.reset_profile(123)

    assert storage.get_profile(123) is None
    assert storage.get_last_results(123) == []
    assert storage.get_favorites(123) == []
