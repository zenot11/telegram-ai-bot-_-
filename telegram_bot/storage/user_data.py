import json
from pathlib import Path
from threading import Lock
from typing import Any

from telegram_bot.config import settings


class UserDataStorage:
    def __init__(self, path: str | None = None) -> None:
        self.path = Path(path or settings.user_data_path)
        self._lock = Lock()

    def save_profile(self, telegram_id: int, profile: dict[str, Any]) -> None:
        with self._lock:
            data = self._read_all_unlocked()
            current = data.get(str(telegram_id), {})
            if not isinstance(current, dict):
                current = {}

            current.update(
                {
                    "telegram_id": telegram_id,
                    "region": profile.get("region"),
                    "score": profile.get("score"),
                    "direction": profile.get("direction"),
                    "education_type": profile.get("education_type"),
                }
            )
            data[str(telegram_id)] = current
            self._write_all_unlocked(data)

    def get_profile(self, telegram_id: int) -> dict[str, Any] | None:
        data = self._read_all()
        user = data.get(str(telegram_id))
        return user if isinstance(user, dict) else None

    def reset_profile(self, telegram_id: int) -> None:
        with self._lock:
            data = self._read_all_unlocked()
            data.pop(str(telegram_id), None)
            self._write_all_unlocked(data)

    def save_last_results(self, telegram_id: int, last_results: list[dict[str, Any]]) -> None:
        with self._lock:
            data = self._read_all_unlocked()
            current = data.get(str(telegram_id), {})
            if not isinstance(current, dict):
                current = {}
            current["telegram_id"] = telegram_id
            current["last_results"] = last_results
            data[str(telegram_id)] = current
            self._write_all_unlocked(data)

    def get_last_results(self, telegram_id: int) -> list[dict[str, Any]]:
        profile = self.get_profile(telegram_id)
        if not profile:
            return []

        results = profile.get("last_results", [])
        return results if isinstance(results, list) else []

    def get_user(self, telegram_id: int) -> dict[str, Any] | None:
        return self.get_profile(telegram_id)

    def save_search(
        self,
        telegram_id: int,
        profile: dict[str, Any],
        last_results: list[dict[str, Any]],
    ) -> None:
        self.save_profile(telegram_id, profile)
        self.save_last_results(telegram_id, last_results)

    def reset_user(self, telegram_id: int) -> None:
        self.reset_profile(telegram_id)

    def _read_all(self) -> dict[str, Any]:
        with self._lock:
            return self._read_all_unlocked()

    def _read_all_unlocked(self) -> dict[str, Any]:
        if not self.path.exists():
            self._write_all_unlocked({})
            return {}
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}
        return data if isinstance(data, dict) else {}

    def _write_all_unlocked(self, data: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


user_storage = UserDataStorage()
