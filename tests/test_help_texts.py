from telegram_bot.services.texts import BOTFATHER_TEXT, HELP_TEXT, TEXTS_FOR_TESTS


def test_information_texts_are_importable_without_telegram() -> None:
    assert "демонстрационный Telegram-сервис" in TEXTS_FOR_TESTS["about"]
    assert "Короткий сценарий демонстрации" in TEXTS_FOR_TESTS["demo"]
    assert "Приватность" in TEXTS_FOR_TESTS["privacy"]
    assert "финальную базу вузов" in TEXTS_FOR_TESTS["next"]
    assert "Команды для /setcommands" in TEXTS_FOR_TESTS["botfather"]


def test_help_text_contains_current_commands() -> None:
    for command in (
        "/start",
        "/menu",
        "/search",
        "/compare",
        "/categories",
        "/support",
        "/webapp",
        "/about",
        "/demo",
        "/privacy",
        "/next",
        "/botfather",
        "/reset",
        "/help",
    ):
        assert command in HELP_TEXT


def test_botfather_text_contains_current_commands() -> None:
    for line in (
        "start - запуск бота",
        "menu - главное меню",
        "search - подбор вузов",
        "compare - сравнение вузов",
        "categories - как читать категории",
        "support - психологическая поддержка",
        "webapp - открыть Mini App",
        "about - о проекте",
        "demo - сценарий демонстрации",
        "privacy - приватность",
        "next - что подготовить перед сдачей",
        "reset - сброс введённых данных",
        "help - помощь",
    ):
        assert line in BOTFATHER_TEXT


def test_user_facing_texts_do_not_use_mvp_label() -> None:
    assert all("MVP" not in text for text in TEXTS_FOR_TESTS.values())
