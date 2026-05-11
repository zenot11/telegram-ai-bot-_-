from dataclasses import dataclass
import os

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    telegram_bot_token: str
    openai_api_key: str | None
    backend_base_url: str
    user_data_path: str
    openai_model: str


def load_settings() -> Settings:
    return Settings(
        telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN", "").strip(),
        openai_api_key=os.getenv("OPENAI_API_KEY", "").strip() or None,
        backend_base_url=os.getenv("BACKEND_BASE_URL", "http://localhost:8000").strip().rstrip("/"),
        user_data_path=os.getenv("USER_DATA_PATH", "telegram_bot/storage/user_data.json").strip(),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip(),
    )


settings = load_settings()
