import hashlib
import hmac
import json
import time
from typing import Any
from urllib.parse import parse_qsl


class TelegramAuthError(ValueError):
    pass


def parse_init_data(init_data: str) -> dict[str, str]:
    if not init_data:
        raise TelegramAuthError("initData is empty")

    pairs = parse_qsl(init_data, keep_blank_values=True, strict_parsing=False)
    parsed = {key: value for key, value in pairs}
    if not parsed:
        raise TelegramAuthError("initData is empty")
    return parsed


def validate_telegram_init_data(
    init_data: str,
    bot_token: str,
    max_age_seconds: int | None = 86400,
) -> dict[str, Any]:
    if not bot_token:
        raise TelegramAuthError("bot token is not configured")

    parsed = parse_init_data(init_data)
    received_hash = parsed.get("hash")
    if not received_hash:
        raise TelegramAuthError("initData hash is missing")

    check_items = [(key, value) for key, value in parsed.items() if key != "hash"]
    data_check_string = "\n".join(f"{key}={value}" for key, value in sorted(check_items))
    secret_key = hmac.new(b"WebAppData", bot_token.encode("utf-8"), hashlib.sha256).digest()
    calculated_hash = hmac.new(
        secret_key,
        data_check_string.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(calculated_hash, received_hash):
        raise TelegramAuthError("initData hash is invalid")

    if max_age_seconds is not None:
        auth_date = _parse_int(parsed.get("auth_date"))
        if auth_date is None:
            raise TelegramAuthError("auth_date is missing")
        if int(time.time()) - auth_date > max_age_seconds:
            raise TelegramAuthError("initData is expired")

    validated: dict[str, Any] = dict(parsed)
    user_raw = parsed.get("user")
    if user_raw:
        try:
            validated["user"] = json.loads(user_raw)
        except json.JSONDecodeError as error:
            raise TelegramAuthError("user payload is invalid") from error
    return validated


def extract_telegram_user_id(validated_data: dict[str, Any]) -> int | None:
    user = validated_data.get("user")
    if not isinstance(user, dict):
        return None
    user_id = user.get("id")
    if isinstance(user_id, bool):
        return None
    if isinstance(user_id, int):
        return user_id
    if isinstance(user_id, str) and user_id.isdigit():
        return int(user_id)
    return None


def _parse_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return None
