import json
from typing import Any

from telegram_bot.config import settings
from telegram_bot.services.safety import CRISIS_RESPONSE

try:
    from openai import AsyncOpenAI
except ImportError:
    AsyncOpenAI = None


class AIService:
    def __init__(self) -> None:
        self.client = None
        if settings.openai_api_key and AsyncOpenAI is not None:
            self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model

    async def explain_universities(
        self,
        profile: dict[str, Any],
        universities: list[dict[str, Any]],
    ) -> str | None:
        if not self.client:
            return None

        prompt = (
            "Пользователь подбирает вуз. Объясни найденные варианты простым языком, "
            "без обещаний поступления. Дай короткий план из 3 шагов. "
            "Не ставь диагнозы, не давай медицинские советы и не дави на пользователя.\n\n"
            f"Профиль: {json.dumps(profile, ensure_ascii=False)}\n"
            f"Варианты: {json.dumps(universities[:5], ensure_ascii=False)}"
        )
        return await self._ask(prompt, max_tokens=500)

    async def answer_free_question(self, text: str) -> str | None:
        if not self.client or not text.strip():
            return None

        prompt = (
            "Ответь как Аиша, мягкий AI-помощник для абитуриента. "
            "Помогай выбрать направление, составить короткий план поступления или снизить перегруз. "
            "Не обещай поступление, не ставь диагнозы и не давай медицинские советы.\n\n"
            f"Сообщение пользователя: {text}"
        )
        return await self._ask(prompt, max_tokens=450)

    async def _ask(self, prompt: str, max_tokens: int) -> str | None:
        if not self.client:
            return None

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Ты Аиша, спокойный и полезный помощник для абитуриентов. "
                            "Если в сообщении есть риск самоповреждения, суицида или опасности для себя, "
                            f"ответь только этим текстом: {CRISIS_RESPONSE}"
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.4,
                max_tokens=max_tokens,
            )
        except Exception:
            return None

        message = response.choices[0].message.content if response.choices else None
        return message.strip() if message else None


ai_service = AIService()
