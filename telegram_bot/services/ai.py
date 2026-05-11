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

    def is_ai_available(self) -> bool:
        return self.client is not None

    async def explain_results(
        self,
        profile: dict[str, Any],
        universities: list[dict[str, Any]],
    ) -> str | None:
        if not self.client:
            return None

        prompt = (
            "Пользователь подбирает вуз. Начни ответ с фразы «Как это можно понять:». "
            "Объясни найденные варианты простым языком, без обещаний поступления. "
            "Дай короткий план из 3 шагов. "
            "Не ставь диагнозы, не давай медицинские советы и не дави на пользователя.\n\n"
            f"Профиль: {json.dumps(profile, ensure_ascii=False)}\n"
            f"Варианты: {json.dumps(universities[:5], ensure_ascii=False)}"
        )
        return await self._ask(prompt, max_tokens=500)

    async def explain_universities(
        self,
        profile: dict[str, Any],
        universities: list[dict[str, Any]],
    ) -> str | None:
        return await self.explain_results(profile, universities)

    async def generate_support_reply(self, situation: str, fallback: str) -> str:
        if not self.client:
            return fallback

        prompt = (
            "Сформулируй короткий мягкий ответ для абитуриента по ситуации. "
            "Ответ должен быть по-русски, без диагнозов, медицинских советов, давления, "
            "шуток над тревогой и обещаний поступления. В конце предложи один маленький шаг.\n\n"
            f"Ситуация: {situation}\n"
            f"Базовый смысл ответа: {fallback}"
        )
        answer = await self._ask(prompt, max_tokens=300)
        return answer or fallback

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
                            "Отвечай мягко, спокойно и по-русски. "
                            "Не ставь диагнозы. Не давай медицинские советы. "
                            "Не обещай поступление. Не дави на пользователя. "
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


def is_ai_available() -> bool:
    return ai_service.is_ai_available()


async def explain_results(profile: dict[str, Any], universities: list[dict[str, Any]]) -> str | None:
    return await ai_service.explain_results(profile, universities)


async def generate_support_reply(situation: str, fallback: str) -> str:
    return await ai_service.generate_support_reply(situation, fallback)
