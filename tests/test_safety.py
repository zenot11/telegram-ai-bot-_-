from telegram_bot.services.safety import is_crisis_message


def test_crisis_phrases_are_detected() -> None:
    assert is_crisis_message("не хочу жить")
    assert is_crisis_message("хочу умереть")
    assert is_crisis_message("суицид")
    assert is_crisis_message("мне небезопасно")


def test_regular_anxiety_is_not_crisis() -> None:
    assert not is_crisis_message("мне тревожно")
    assert not is_crisis_message("я боюсь не поступить")
