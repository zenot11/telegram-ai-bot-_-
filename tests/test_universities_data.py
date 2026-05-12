from backend_stub.main import load_universities


REQUIRED_FIELDS = {
    "university",
    "city",
    "region",
    "program",
    "direction",
    "subjects",
    "min_score",
    "type",
    "price",
    "url",
}


def test_universities_json_has_at_least_eight_regions() -> None:
    rows = load_universities()
    regions = {item["region"] for item in rows}

    assert len(regions) >= 8
    assert {
        "Адыгея",
        "Москва",
        "Краснодарский край",
        "Санкт-Петербург",
        "Татарстан",
        "Крым",
        "Ростовская область",
        "Свердловская область",
    }.issubset(regions)


def test_universities_json_has_at_least_nine_directions() -> None:
    rows = load_universities()
    directions = {item["direction"] for item in rows}

    assert len(directions) >= 9
    assert {
        "IT",
        "психология",
        "медицина",
        "экономика",
        "юриспруденция",
        "педагогика",
        "дизайн",
        "строительство",
        "туризм",
    }.issubset(directions)


def test_every_university_item_has_required_fields() -> None:
    rows = load_universities()

    assert rows
    for item in rows:
        assert REQUIRED_FIELDS.issubset(item)
        assert isinstance(item["subjects"], list)
        assert isinstance(item["min_score"], int)
