import hashlib
import hmac
import json
import time
from urllib.parse import urlencode

import pytest

from backend_stub.telegram_auth import (
    TelegramAuthError,
    extract_telegram_user_id,
    validate_telegram_init_data,
)


TEST_BOT_TOKEN = "123456:TEST_TOKEN"


def make_init_data(
    bot_token: str = TEST_BOT_TOKEN,
    user_id: int | None = 123,
    auth_date: int | None = None,
    tamper_hash: bool = False,
    include_hash: bool = True,
) -> str:
    data = {}
    if user_id is not None:
        data["user"] = json.dumps({"id": user_id, "first_name": "Test"}, ensure_ascii=False, separators=(",", ":"))
    if auth_date is not None:
        data["auth_date"] = str(auth_date)
    else:
        data["auth_date"] = str(int(time.time()))

    data_check_string = "\n".join(f"{key}={value}" for key, value in sorted(data.items()))
    secret_key = hmac.new(b"WebAppData", bot_token.encode("utf-8"), hashlib.sha256).digest()
    calculated_hash = hmac.new(secret_key, data_check_string.encode("utf-8"), hashlib.sha256).hexdigest()
    if include_hash:
        data["hash"] = "bad" + calculated_hash[3:] if tamper_hash else calculated_hash
    return urlencode(data)


def test_valid_init_data_passes() -> None:
    validated = validate_telegram_init_data(make_init_data(), TEST_BOT_TOKEN)

    assert extract_telegram_user_id(validated) == 123


def test_invalid_hash_is_rejected() -> None:
    with pytest.raises(TelegramAuthError, match="hash is invalid"):
        validate_telegram_init_data(make_init_data(tamper_hash=True), TEST_BOT_TOKEN)


def test_missing_hash_is_rejected() -> None:
    with pytest.raises(TelegramAuthError, match="hash is missing"):
        validate_telegram_init_data(make_init_data(include_hash=False), TEST_BOT_TOKEN)


def test_missing_user_returns_none() -> None:
    validated = validate_telegram_init_data(make_init_data(user_id=None), TEST_BOT_TOKEN)

    assert extract_telegram_user_id(validated) is None


def test_expired_auth_date_is_rejected() -> None:
    old_auth_date = int(time.time()) - 90000

    with pytest.raises(TelegramAuthError, match="expired"):
        validate_telegram_init_data(make_init_data(auth_date=old_auth_date), TEST_BOT_TOKEN)


def test_errors_do_not_contain_bot_token() -> None:
    with pytest.raises(TelegramAuthError) as error:
        validate_telegram_init_data(make_init_data(tamper_hash=True), TEST_BOT_TOKEN)

    assert TEST_BOT_TOKEN not in str(error.value)
