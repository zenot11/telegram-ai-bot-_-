from telegram_bot.handlers import feedback
from telegram_bot.keyboards.feedback import (
    FEEDBACK_CANCEL_CALLBACK,
    FEEDBACK_CATEGORY_PREFIX,
    feedback_cancel_keyboard,
    feedback_categories_keyboard,
    feedback_created_keyboard,
)
from telegram_bot.states.feedback_states import FeedbackStates


def test_feedback_handler_imports_router() -> None:
    assert feedback.router is not None


def test_feedback_states_exist() -> None:
    assert FeedbackStates.message.state == "FeedbackStates:message"


def test_feedback_categories_keyboard_contains_actions() -> None:
    markup = feedback_categories_keyboard()
    texts = [button.text for row in markup.inline_keyboard for button in row]
    callbacks = [button.callback_data for row in markup.inline_keyboard for button in row]

    assert "Вопрос по поступлению" in texts
    assert "Проблема с Mini App" in texts
    assert "Предложить улучшение" in texts
    assert f"{FEEDBACK_CATEGORY_PREFIX}search_problem" in callbacks
    assert FEEDBACK_CANCEL_CALLBACK in callbacks


def test_feedback_reply_keyboards_are_compact() -> None:
    cancel_texts = [button.text for row in feedback_cancel_keyboard().keyboard for button in row]
    created_texts = [button.text for row in feedback_created_keyboard().keyboard for button in row]

    assert "Отмена" in cancel_texts
    assert "Мои обращения" in created_texts
    assert "Создать ещё обращение" in created_texts
    assert "Вернуться в меню" in created_texts
