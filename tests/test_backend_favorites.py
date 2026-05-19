import asyncio
import hashlib
import hmac
import json
import time
from urllib.parse import urlencode

import pytest
from aiohttp import web

from backend_stub.favorites_api import (
    FAVORITES_STORAGE_KEY,
    INIT_DATA_HEADER,
    add_favorite,
    clear_favorites,
    get_favorites,
    remove_favorite,
    sync_favorites,
)
from telegram_bot.storage.user_data import UserDataStorage


TEST_BOT_TOKEN = "123456:TEST_TOKEN"


class FakeRequest:
    def __init__(self, storage: UserDataStorage, body: dict | None = None, init_data: str | None = None) -> None:
        self.app = {FAVORITES_STORAGE_KEY: storage}
        self.headers = {}
        if init_data is not None:
            self.headers[INIT_DATA_HEADER] = init_data
        self._body = body if body is not None else {}

    async def json(self) -> dict:
        return self._body


def university(number: int = 1) -> dict:
    return {
        "university": f"Вуз {number}",
        "city": "Майкоп",
        "region": "Адыгея",
        "program": f"Программа {number}",
        "direction": "IT",
        "subjects": ["русский язык", "математика", "информатика"],
        "min_score": 180 + number,
        "type": "бюджет",
        "price": None,
        "url": f"https://example{number}.ru",
    }


def make_init_data() -> str:
    data = {
        "user": json.dumps({"id": 123, "first_name": "Test"}, ensure_ascii=False, separators=(",", ":")),
        "auth_date": str(int(time.time())),
    }
    data_check_string = "\n".join(f"{key}={value}" for key, value in sorted(data.items()))
    secret_key = hmac.new(b"WebAppData", TEST_BOT_TOKEN.encode("utf-8"), hashlib.sha256).digest()
    data["hash"] = hmac.new(secret_key, data_check_string.encode("utf-8"), hashlib.sha256).hexdigest()
    return urlencode(data)


def payload(response: web.Response) -> dict:
    return json.loads(response.text)


def request(storage: UserDataStorage, body: dict | None = None) -> FakeRequest:
    return FakeRequest(storage, body=body, init_data=make_init_data())


def test_get_favorites_without_init_data_returns_401(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", TEST_BOT_TOKEN)
    storage = UserDataStorage(str(tmp_path / "user_data.json"))

    with pytest.raises(web.HTTPUnauthorized):
        asyncio.run(get_favorites(FakeRequest(storage)))


def test_get_favorites_with_valid_init_data_returns_items(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", TEST_BOT_TOKEN)
    storage = UserDataStorage(str(tmp_path / "user_data.json"))
    storage.add_favorite(123, university())

    response = asyncio.run(get_favorites(request(storage)))
    data = payload(response)

    assert data["status"] == "ok"
    assert data["mode"] == "telegram"
    assert len(data["favorites"]) == 1


def test_add_favorite_does_not_duplicate(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", TEST_BOT_TOKEN)
    storage = UserDataStorage(str(tmp_path / "user_data.json"))

    body = {"item": university()}
    asyncio.run(add_favorite(request(storage, body)))
    response = asyncio.run(add_favorite(request(storage, body)))
    data = payload(response)

    assert len(data["favorites"]) == 1


def test_remove_favorite_by_key(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", TEST_BOT_TOKEN)
    storage = UserDataStorage(str(tmp_path / "user_data.json"))
    item = university()
    storage.add_favorite(123, item)
    key = storage.favorite_key(item)

    response = asyncio.run(remove_favorite(request(storage, {"key": key})))
    data = payload(response)

    assert data["favorites"] == []


def test_clear_favorites(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", TEST_BOT_TOKEN)
    storage = UserDataStorage(str(tmp_path / "user_data.json"))
    storage.add_favorite(123, university())

    response = asyncio.run(clear_favorites(request(storage, {})))
    data = payload(response)

    assert data["favorites"] == []


def test_sync_merges_local_and_server_favorites_without_duplicates(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", TEST_BOT_TOKEN)
    storage = UserDataStorage(str(tmp_path / "user_data.json"))
    storage.add_favorite(123, university(1))

    response = asyncio.run(sync_favorites(request(storage, {"local_favorites": [university(1), university(2)]})))
    data = payload(response)

    assert len(data["favorites"]) == 2
    assert [item["university"] for item in data["favorites"]] == ["Вуз 1", "Вуз 2"]
