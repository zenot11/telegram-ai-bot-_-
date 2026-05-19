import json
from pathlib import Path
from threading import Lock
from typing import Any

from telegram_bot.config import settings
from telegram_bot.services.history import HISTORY_LIMIT, build_history_entry


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

    def set_active_results(self, telegram_id: int, results: list[dict[str, Any]]) -> None:
        with self._lock:
            data = self._read_all_unlocked()
            current = data.get(str(telegram_id), {})
            if not isinstance(current, dict):
                current = {}
            current["telegram_id"] = telegram_id
            current["active_results"] = results
            data[str(telegram_id)] = current
            self._write_all_unlocked(data)

    def get_active_results(self, telegram_id: int) -> list[dict[str, Any]]:
        profile = self.get_profile(telegram_id)
        if not profile:
            return []

        results = profile.get("active_results", [])
        return results if isinstance(results, list) else []

    def has_active_results(self, telegram_id: int) -> bool:
        profile = self.get_profile(telegram_id)
        return isinstance(profile, dict) and isinstance(profile.get("active_results"), list)

    def clear_active_results(self, telegram_id: int) -> None:
        with self._lock:
            data = self._read_all_unlocked()
            current = data.get(str(telegram_id), {})
            if not isinstance(current, dict):
                return
            current.pop("active_results", None)
            data[str(telegram_id)] = current
            self._write_all_unlocked(data)

    def add_favorite(self, telegram_id: int, university_item: dict[str, Any]) -> bool:
        with self._lock:
            data = self._read_all_unlocked()
            current = data.get(str(telegram_id), {})
            if not isinstance(current, dict):
                current = {}

            favorites = current.get("favorites", [])
            if not isinstance(favorites, list):
                favorites = []

            new_key = self._favorite_key(university_item)
            if any(self._favorite_key(item) == new_key for item in favorites if isinstance(item, dict)):
                return False

            current["telegram_id"] = telegram_id
            favorites.append(university_item)
            current["favorites"] = favorites
            data[str(telegram_id)] = current
            self._write_all_unlocked(data)
            return True

    def merge_favorites(self, telegram_id: int, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        with self._lock:
            data = self._read_all_unlocked()
            current = data.get(str(telegram_id), {})
            if not isinstance(current, dict):
                current = {}

            favorites = current.get("favorites", [])
            if not isinstance(favorites, list):
                favorites = []
            merged = [item for item in favorites if isinstance(item, dict)]
            keys = {self.favorite_key(item) for item in merged}

            for item in items:
                key = self.favorite_key(item)
                if key not in keys:
                    merged.append(item)
                    keys.add(key)

            current["telegram_id"] = telegram_id
            current["favorites"] = merged
            data[str(telegram_id)] = current
            self._write_all_unlocked(data)
            return merged

    def get_favorites(self, telegram_id: int) -> list[dict[str, Any]]:
        profile = self.get_profile(telegram_id)
        if not profile:
            return []

        favorites = profile.get("favorites", [])
        return [item for item in favorites if isinstance(item, dict)] if isinstance(favorites, list) else []

    def clear_favorites(self, telegram_id: int) -> None:
        with self._lock:
            data = self._read_all_unlocked()
            current = data.get(str(telegram_id), {})
            if not isinstance(current, dict):
                current = {}
            current["telegram_id"] = telegram_id
            current["favorites"] = []
            data[str(telegram_id)] = current
            self._write_all_unlocked(data)

    def remove_favorite(self, telegram_id: int, index: int) -> dict[str, Any] | None:
        with self._lock:
            data = self._read_all_unlocked()
            current = data.get(str(telegram_id), {})
            if not isinstance(current, dict):
                return None

            favorites = current.get("favorites", [])
            if not isinstance(favorites, list) or index < 0 or index >= len(favorites):
                return None

            removed = favorites.pop(index)
            current["favorites"] = favorites
            data[str(telegram_id)] = current
            self._write_all_unlocked(data)
            return removed if isinstance(removed, dict) else None

    def remove_favorite_by_key(self, telegram_id: int, key: str) -> dict[str, Any] | None:
        with self._lock:
            data = self._read_all_unlocked()
            current = data.get(str(telegram_id), {})
            if not isinstance(current, dict):
                return None

            favorites = current.get("favorites", [])
            if not isinstance(favorites, list):
                return None

            normalized_key = str(key)
            for index, item in enumerate(favorites):
                if isinstance(item, dict) and self.favorite_key(item) == normalized_key:
                    removed = favorites.pop(index)
                    current["favorites"] = favorites
                    data[str(telegram_id)] = current
                    self._write_all_unlocked(data)
                    return removed
            return None

    def add_search_history(
        self,
        telegram_id: int,
        search_query: dict[str, Any],
        results: list[dict[str, Any]],
    ) -> dict[str, Any]:
        entry = build_history_entry(search_query, results)
        with self._lock:
            data = self._read_all_unlocked()
            current = data.get(str(telegram_id), {})
            if not isinstance(current, dict):
                current = {}

            history = current.get("history", [])
            if not isinstance(history, list):
                history = []

            current["telegram_id"] = telegram_id
            current["history"] = [entry] + [item for item in history if isinstance(item, dict)]
            current["history"] = current["history"][:HISTORY_LIMIT]
            data[str(telegram_id)] = current
            self._write_all_unlocked(data)
            return entry

    def get_search_history(self, telegram_id: int, limit: int = HISTORY_LIMIT) -> list[dict[str, Any]]:
        profile = self.get_profile(telegram_id)
        if not profile:
            return []

        history = profile.get("history", [])
        if not isinstance(history, list):
            return []
        safe_limit = max(0, min(limit, HISTORY_LIMIT))
        return [item for item in history if isinstance(item, dict)][:safe_limit]

    def clear_search_history(self, telegram_id: int) -> None:
        with self._lock:
            data = self._read_all_unlocked()
            current = data.get(str(telegram_id), {})
            if not isinstance(current, dict):
                current = {}
            current["telegram_id"] = telegram_id
            current["history"] = []
            data[str(telegram_id)] = current
            self._write_all_unlocked(data)

    def get_profile_summary(self, telegram_id: int) -> dict[str, Any]:
        profile = self.get_profile(telegram_id) or {}
        last_results = profile.get("last_results", [])
        favorites = profile.get("favorites", [])

        last_results_count = len(last_results) if isinstance(last_results, list) else 0
        favorites_count = len(favorites) if isinstance(favorites, list) else 0

        return {
            "telegram_id": telegram_id,
            "region": profile.get("region"),
            "score": profile.get("score"),
            "direction": profile.get("direction"),
            "education_type": profile.get("education_type"),
            "last_results_count": last_results_count,
            "favorites_count": favorites_count,
            "is_empty": favorites_count == 0 and last_results_count == 0 and not any(
                profile.get(key) is not None
                for key in ("region", "score", "direction", "education_type")
            ),
        }

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
        self.set_active_results(telegram_id, last_results)

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

    @staticmethod
    def favorite_key(item: dict[str, Any]) -> str:
        return "|".join(
            str(item.get(field, "")).strip().lower()
            for field in ("university", "program", "city", "min_score", "type")
        )

    @staticmethod
    def _favorite_key(item: dict[str, Any]) -> str:
        return UserDataStorage.favorite_key(item)


user_storage = UserDataStorage()
