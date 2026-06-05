from telegram_bot.services.texts import BOTFATHER_TEXT, HELP_TEXT, TEXTS_FOR_TESTS


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


def test_information_texts_are_importable_without_telegram() -> None:
    assert "демонстрационный Telegram-сервис" in TEXTS_FOR_TESTS["about"]
    assert "Демо-сценарий для защиты" in TEXTS_FOR_TESTS["demo"]
    assert "компактное меню" in TEXTS_FOR_TESTS["demo"]
    assert "Мои результаты" in TEXTS_FOR_TESTS["demo"]
    assert "Помощник" in TEXTS_FOR_TESTS["demo"]
    assert "/summary" in TEXTS_FOR_TESTS["demo"]
    assert "/advice" in TEXTS_FOR_TESTS["demo"]
    assert "/history" in TEXTS_FOR_TESTS["demo"]
    assert "Приватность" in TEXTS_FOR_TESTS["privacy"]
    assert "Сначала выполни подбор вузов" in TEXTS_FOR_TESTS["next"]
    assert "Команды для /setcommands" in TEXTS_FOR_TESTS["botfather"]


def test_help_text_contains_current_commands() -> None:
    assert "Основное:" in HELP_TEXT
    assert "Результаты:" in HELP_TEXT
    assert "Помощь:" in HELP_TEXT
    assert "/support — психологическая поддержка" in HELP_TEXT
    assert "/feedback — обратная связь по работе сервиса" in HELP_TEXT

    for command in (
        "/start",
        "/menu",
        "/search",
        "/summary",
        "/favorites",
        "/advice",
        "/filters",
        "/export",
        "/history",
        "/compare",
        "/categories",
        "/support",
        "/feedback",
        "/my_feedback",
        "/webapp",
        "/about",
        "/demo",
        "/privacy",
        "/next",
        "/plan",
        "/botfather",
        "/clear_history",
        "/reset",
        "/help",
    ):
        assert command in HELP_TEXT


def test_botfather_text_contains_current_commands() -> None:
    for line in (
        "start - запуск бота",
        "menu - главное меню",
        "search - подбор вузов",
        "summary - итог последнего подбора",
        "favorites - избранные вузы",
        "advice - советы по подбору",
        "filters - фильтры результатов",
        "export - экспорт результата",
        "history - история подборов",
        "clear_history - очистить историю подборов",
        "compare - сравнение вузов",
        "categories - как читать категории",
        "support - психологическая поддержка",
        "feedback - обратная связь",
        "my_feedback - мои обращения",
        "webapp - открыть Mini App",
        "about - о проекте",
        "demo - сценарий демонстрации",
        "privacy - приватность",
        "next - следующий шаг после подбора",
        "plan - короткий план действий",
        "botfather - настройки BotFather",
        "reset - сброс введённых данных",
        "help - помощь",
    ):
        assert line in BOTFATHER_TEXT


def test_user_facing_texts_do_not_use_mvp_label() -> None:
    assert all("MVP" not in text for text in TEXTS_FOR_TESTS.values())


def test_user_facing_information_texts_do_not_show_dev_checklist() -> None:
    combined = "\n".join(TEXTS_FOR_TESTS.values())

    for term in DEV_ONLY_TERMS:
        assert term not in combined

    assert "/next — следующий шаг после подбора" in HELP_TEXT
    assert "next - следующий шаг после подбора" in BOTFATHER_TEXT
