import asyncio
from types import SimpleNamespace

from aiogram.types import ReplyKeyboardRemove

from telegram_bot.handlers.search import search_direction, search_score, start_search
from telegram_bot.keyboards.search import education_type_keyboard
from telegram_bot.services.api import _university_query_params
from telegram_bot.services.search_prompts import DIRECTION_PROMPT, REGION_PROMPT
from telegram_bot.services.validation import education_type_label, normalize_education_type
from telegram_bot.states.search_states import SearchStates


class DummyMessage:
    def __init__(self, text: str = "") -> None:
        self.text = text
        self.from_user = SimpleNamespace(id=1)
        self.answers: list[tuple[str, dict]] = []

    async def answer(self, text: str, **kwargs) -> None:
        self.answers.append((text, kwargs))


class DummyState:
    def __init__(self) -> None:
        self.state = None
        self.data = {}

    async def set_state(self, state) -> None:
        self.state = state

    async def update_data(self, **kwargs) -> None:
        self.data.update(kwargs)


def keyboard_texts(markup) -> list[str]:
    return [button.text for row in markup.keyboard for button in row]


def test_region_step_uses_manual_input_prompt_without_region_keyboard() -> None:
    message = DummyMessage()
    state = DummyState()

    asyncio.run(start_search(message, state))

    text, kwargs = message.answers[-1]
    assert state.state == SearchStates.region
    assert text == REGION_PROMPT
    assert "Введи регион" in text
    assert "Москва" in text
    assert "Республика Крым" in text
    assert "Краснодарский край" in text
    assert isinstance(kwargs["reply_markup"], ReplyKeyboardRemove)


def test_direction_step_uses_manual_input_prompt_without_direction_keyboard() -> None:
    message = DummyMessage("290")
    state = DummyState()

    asyncio.run(search_score(message, state))

    text, kwargs = message.answers[-1]
    assert state.state == SearchStates.direction
    assert text == DIRECTION_PROMPT
    assert "Введи направление" in text
    assert "IT" in text
    assert "09.03.04" in text
    assert "экономика" in text
    assert "архитектура" in text
    assert isinstance(kwargs["reply_markup"], ReplyKeyboardRemove)


def test_financing_step_uses_fixed_buttons_only_after_manual_direction() -> None:
    message = DummyMessage("IT")
    state = DummyState()

    asyncio.run(search_direction(message, state))

    text, kwargs = message.answers[-1]
    assert state.state == SearchStates.education_type
    assert text == "Какое финансирование рассматриваешь?"
    assert keyboard_texts(kwargs["reply_markup"]) == ["Бюджет", "Платное", "Любое", "Назад"]
    assert keyboard_texts(education_type_keyboard()) == ["Бюджет", "Платное", "Любое", "Назад"]


def test_manual_financing_aliases_still_normalize() -> None:
    assert normalize_education_type("бюджет") == "budget"
    assert normalize_education_type("Бюджет") == "budget"
    assert normalize_education_type("budget") == "budget"
    assert normalize_education_type("платное") == "paid"
    assert normalize_education_type("Платное") == "paid"
    assert normalize_education_type("контракт") == "paid"
    assert normalize_education_type("paid") == "paid"
    assert normalize_education_type("любое") == "any"
    assert normalize_education_type("Любое") == "any"
    assert normalize_education_type("any") == "any"
    assert education_type_label("any") == "любое"


def test_any_financing_omits_backend_type_filter() -> None:
    any_params = _university_query_params("Москва", 290, "IT", "any", 20)
    any_ru_params = _university_query_params("Москва", 290, "IT", "Любое", 20)
    budget_params = _university_query_params("Москва", 290, "IT", "budget", 20)

    assert "type" not in any_params
    assert "type" not in any_ru_params
    assert budget_params["type"] == "budget"
