import asyncio
import hashlib
import hmac
import json
import time
from urllib.parse import urlencode

from backend_stub.webapp_session import INIT_DATA_HEADER, webapp_session


TEST_BOT_TOKEN = "123456:TEST_TOKEN"


class FakeRequest:
    def __init__(self, init_data: str | None = None) -> None:
        self.headers = {}
        if init_data is not None:
            self.headers[INIT_DATA_HEADER] = init_data


def make_init_data(
    bot_token: str = TEST_BOT_TOKEN,
    user_id: int | None = 123,
    auth_date: int | None = None,
    tamper_hash: bool = False,
) -> str:
    data = {
        "auth_date": str(auth_date or int(time.time())),
    }
    if user_id is not None:
        data["user"] = json.dumps(
            {
                "id": user_id,
                "first_name": "Test",
                "username": "test_user",
            },
            ensure_ascii=False,
            separators=(",", ":"),
        )

    data_check_string = "\n".join(f"{key}={value}" for key, value in sorted(data.items()))
    secret_key = hmac.new(b"WebAppData", bot_token.encode("utf-8"), hashlib.sha256).digest()
    calculated_hash = hmac.new(
        secret_key,
        data_check_string.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    data["hash"] = "bad" + calculated_hash[3:] if tamper_hash else calculated_hash
    return urlencode(data)


def response_payload(response) -> dict:
    return json.loads(response.text)


def test_webapp_session_without_init_data_returns_local_mode() -> None:
    response = asyncio.run(webapp_session(FakeRequest()))
    payload = response_payload(response)

    assert response.status == 200
    assert payload == {
        "status": "ok",
        "mode": "local",
        "authenticated": False,
    }


def test_webapp_session_with_valid_init_data_returns_safe_user(monkeypatch) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", TEST_BOT_TOKEN)

    response = asyncio.run(webapp_session(FakeRequest(make_init_data(user_id=456))))
    payload = response_payload(response)

    assert response.status == 200
    assert payload["status"] == "ok"
    assert payload["mode"] == "telegram"
    assert payload["authenticated"] is True
    assert payload["user"]["id"] == 456
    assert payload["user"]["first_name"] == "Test"
    assert payload["user"]["username"] == "test_user"
    assert "hash" not in payload
    assert "initData" not in payload


def test_webapp_session_with_invalid_init_data_returns_unauthorized(monkeypatch) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", TEST_BOT_TOKEN)

    response = asyncio.run(webapp_session(FakeRequest(make_init_data(tamper_hash=True))))
    payload = response_payload(response)

    assert response.status == 401
    assert payload == {
        "status": "error",
        "mode": "telegram",
        "authenticated": False,
        "error": "invalid_init_data",
    }


def test_webapp_session_without_bot_token_returns_safe_error(monkeypatch) -> None:
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)

    response = asyncio.run(webapp_session(FakeRequest(make_init_data())))
    payload = response_payload(response)
    response_text = response.text

    assert response.status == 503
    assert payload["error"] == "bot_token_not_configured"
    assert TEST_BOT_TOKEN not in response_text
    assert "TELEGRAM_BOT_TOKEN" not in response_text
    assert "initData" not in response_text
    assert "hash" not in response_text


def test_webapp_session_rejects_valid_hash_without_user(monkeypatch) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", TEST_BOT_TOKEN)

    response = asyncio.run(webapp_session(FakeRequest(make_init_data(user_id=None))))
    payload = response_payload(response)

    assert response.status == 401
    assert payload["error"] == "invalid_init_data"
