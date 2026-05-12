import asyncio
import importlib

from telegram_bot.services.safety import CRISIS_RESPONSE


def load_ai_without_key(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "")

    import telegram_bot.config as config

    importlib.reload(config)

    import telegram_bot.services.ai as ai

    return importlib.reload(ai)


def test_ai_is_not_available_without_key(monkeypatch) -> None:
    ai = load_ai_without_key(monkeypatch)

    assert ai.is_ai_available() is False


def test_explain_results_returns_none_without_key(monkeypatch) -> None:
    ai = load_ai_without_key(monkeypatch)

    result = asyncio.run(
        ai.explain_results(
            {"region": "Адыгея", "score": 230, "direction": "IT", "education_type": "budget"},
            [{"university": "АГУ", "program": "Прикладная информатика"}],
        )
    )

    assert result is None


def test_generate_support_reply_returns_none_without_key(monkeypatch) -> None:
    ai = load_ai_without_key(monkeypatch)

    result = asyncio.run(ai.generate_support_reply("Мне тревожно"))

    assert result is None


def test_explain_recommendation_groups_returns_none_without_key(monkeypatch) -> None:
    ai = load_ai_without_key(monkeypatch)

    result = asyncio.run(
        ai.explain_recommendation_groups(
            {"region": "Адыгея", "score": 230, "direction": "IT", "education_type": "budget"},
            {"safe": [], "realistic": [], "ambitious": [], "unavailable": []},
        )
    )

    assert result is None


def test_crisis_reply_does_not_require_openai(monkeypatch) -> None:
    ai = load_ai_without_key(monkeypatch)

    result = asyncio.run(ai.generate_support_reply("не хочу жить"))

    assert result == CRISIS_RESPONSE
