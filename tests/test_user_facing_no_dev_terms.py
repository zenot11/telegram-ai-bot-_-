import ast
from pathlib import Path


USER_FACING_FILES = (
    Path("telegram_bot/services/texts.py"),
    Path("telegram_bot/handlers/start.py"),
    Path("telegram_bot/handlers/menu.py"),
    Path("telegram_bot/handlers/search.py"),
)

DEV_ONLY_TERMS = (
    "universities.json",
    "OPENAI_API_KEY",
    "WEBAPP_URL",
    "ngrok",
    "backend",
    ".env",
    "перед финальной сдачей",
    "перед сдачей",
    "финальные данные будут подставлены",
)


def string_literals(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return [node.value for node in ast.walk(tree) if isinstance(node, ast.Constant) and isinstance(node.value, str)]


def test_user_facing_bot_strings_do_not_show_dev_checklist_terms() -> None:
    combined = "\n".join(
        literal
        for path in USER_FACING_FILES
        for literal in string_literals(path)
    )

    for term in DEV_ONLY_TERMS:
        assert term not in combined


def test_next_command_description_is_user_facing() -> None:
    source = Path("telegram_bot/main.py").read_text(encoding="utf-8")

    assert "Следующий шаг после подбора" in source
    assert "Что подготовить перед сдачей" not in source
