from pathlib import Path


def test_database_usage_doc_exists_and_covers_known_tables() -> None:
    content = Path("docs/DATABASE_USAGE.md").read_text(encoding="utf-8")

    assert "Database usage audit" in content
    for table in (
        "universities",
        "faculties",
        "directions",
        "passing_scores",
        "achievements",
        "users",
        "user_ege_scores",
        "user_achievements",
        "user_favorites",
        "v_directions_with_latest_budget",
    ):
        assert table in content
    assert "Используется сейчас?" in content
    assert "не используется" in content.lower()
    assert "JSON остаётся fallback" in content
