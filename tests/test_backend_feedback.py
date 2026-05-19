import asyncio
import hashlib
import hmac
import json
import time
from pathlib import Path
from urllib.parse import urlencode

from backend_stub.feedback_api import INIT_DATA_HEADER, create_feedback, my_feedback
from telegram_bot.storage import feedback_data


TEST_BOT_TOKEN = "123456:TEST_TOKEN"


class FakeRequest:
    def __init__(self, body: dict | None = None, init_data: str | None = None) -> None:
        self.headers = {}
        if init_data is not None:
            self.headers[INIT_DATA_HEADER] = init_data
        self._body = body if body is not None else {}

    async def json(self) -> dict:
        return self._body


def configure_feedback_path(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(feedback_data, "FEEDBACK_DATA_PATH", tmp_path / "feedback.json")


def make_init_data(user_id: int = 123, tamper_hash: bool = False) -> str:
    data = {
        "user": json.dumps({"id": user_id, "first_name": "Test"}, ensure_ascii=False, separators=(",", ":")),
        "auth_date": str(int(time.time())),
    }
    data_check_string = "\n".join(f"{key}={value}" for key, value in sorted(data.items()))
    secret_key = hmac.new(b"WebAppData", TEST_BOT_TOKEN.encode("utf-8"), hashlib.sha256).digest()
    calculated_hash = hmac.new(secret_key, data_check_string.encode("utf-8"), hashlib.sha256).hexdigest()
    data["hash"] = "bad" + calculated_hash[3:] if tamper_hash else calculated_hash
    return urlencode(data)


def payload(response) -> dict:
    return json.loads(response.text)


def valid_body() -> dict:
    return {
        "category": "search_problem",
        "message": "Не нашёл регион в подборе",
        "context": {"page": "mini_app"},
    }


def test_create_feedback_local_mode_without_init_data(tmp_path, monkeypatch) -> None:
    configure_feedback_path(monkeypatch, tmp_path)

    response = asyncio.run(create_feedback(FakeRequest(valid_body())))
    data = payload(response)

    assert response.status == 200
    assert data["status"] == "ok"
    assert data["mode"] == "local"
    assert data["ticket"]["ticket_id"] == "AISH-0001"
    assert feedback_data.get_recent_feedback()[0]["user_id"] is None


def test_create_feedback_with_valid_init_data_saves_user_id(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", TEST_BOT_TOKEN)
    configure_feedback_path(monkeypatch, tmp_path)

    response = asyncio.run(create_feedback(FakeRequest(valid_body(), init_data=make_init_data(user_id=777))))
    data = payload(response)

    assert response.status == 200
    assert data["mode"] == "telegram"
    assert feedback_data.get_user_feedback(777)[0]["ticket_id"] == "AISH-0001"
    assert "hash" not in response.text
    assert TEST_BOT_TOKEN not in response.text


def test_create_feedback_with_invalid_init_data_rejects_request(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", TEST_BOT_TOKEN)
    configure_feedback_path(monkeypatch, tmp_path)

    response = asyncio.run(create_feedback(FakeRequest(valid_body(), init_data=make_init_data(tamper_hash=True))))
    data = payload(response)

    assert response.status == 401
    assert data["error"] == "invalid_init_data"
    assert feedback_data.get_recent_feedback() == []


def test_create_feedback_validates_category_and_message(tmp_path, monkeypatch) -> None:
    configure_feedback_path(monkeypatch, tmp_path)

    invalid_category = asyncio.run(create_feedback(FakeRequest({"category": "bad", "message": "Нормальный текст"})))
    short_message = asyncio.run(create_feedback(FakeRequest({"category": "other", "message": "abc"})))

    assert invalid_category.status == 400
    assert payload(invalid_category)["error"] == "invalid_category"
    assert short_message.status == 400
    assert payload(short_message)["error"] == "message_too_short"


def test_my_feedback_returns_user_tickets_and_local_empty(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", TEST_BOT_TOKEN)
    configure_feedback_path(monkeypatch, tmp_path)
    feedback_data.create_feedback_ticket("mini_app", 123, "Test", "other", "Моя заявка")
    feedback_data.create_feedback_ticket("mini_app", 456, "Other", "other", "Чужая заявка")

    local_response = asyncio.run(my_feedback(FakeRequest()))
    telegram_response = asyncio.run(my_feedback(FakeRequest(init_data=make_init_data(user_id=123))))

    assert payload(local_response) == {"status": "ok", "mode": "local", "tickets": []}
    telegram_payload = payload(telegram_response)
    assert telegram_payload["mode"] == "telegram"
    assert len(telegram_payload["tickets"]) == 1
    assert telegram_payload["tickets"][0]["message"] == "Моя заявка"
