import json
import logging
from typing import Any

from telegram_bot.config import settings
from telegram_bot.services.safety import CRISIS_RESPONSE, is_crisis_message

try:
    from openai import AsyncOpenAI
except ImportError:
    AsyncOpenAI = None


logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "Ты Аиша, AI-помощник для абитуриентов. "
    "Отвечай мягко, спокойно, по-русски и коротко. "
    "Не ставь диагнозы. Не давай медицинские советы. "
    "Не обещай поступление. Не дави на пользователя. "
    "Не обесценивай тревогу и не шути над тревогой. "
    "Не выдумывай официальные данные и не утверждай, что тестовые данные являются настоящими. "
    "Если есть признаки самоповреждения, суицида или опасности для себя, "
    f"верни только этот текст: {CRISIS_RESPONSE}"
)


class AIService:
    def __init__(self) -> None:
        self.client = None
        if settings.openai_api_key and AsyncOpenAI is not None:
            self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        elif settings.openai_api_key and AsyncOpenAI is None:
            logger.warning("OPENAI_API_KEY is set, but openai package is not installed.")

        self.model = settings.openai_model

    def is_ai_available(self) -> bool:
        return self.client is not None

    async def explain_results(
        self,
        profile: dict[str, Any],
        results: list[dict[str, Any]],
    ) -> str | None:
        if not self.client:
            return None

        safe_profile = {
            "region": profile.get("region"),
            "score": profile.get("score"),
            "direction": profile.get("direction"),
            "education_type": profile.get("education_type"),
        }

        user_prompt = (
            "Коротко объясни результаты подбора вузов в стиле Аиши. "
            "Ответ должен быть 3-6 предложений. "
            "Объясни, что список является стартовой точкой для сравнения, а не гарантией поступления. "
            "Предложи сравнить программы, минимальные баллы и оставить 1-2 запасных варианта.\n\n"
            f"Профиль пользователя: {json.dumps(safe_profile, ensure_ascii=False)}\n"
            f"Найденные варианты: {json.dumps(results[:5], ensure_ascii=False)}"
        )
        return await self._ask(user_prompt, max_tokens=360)

    async def explain_universities(
        self,
        profile: dict[str, Any],
        universities: list[dict[str, Any]],
    ) -> str | None:
        return await self.explain_results(profile, universities)

    async def generate_support_reply(
        self,
        user_text: str,
        situation: str | None = None,
    ) -> str | None:
        if is_crisis_message(user_text):
            return CRISIS_RESPONSE

        if not self.client or not user_text.strip():
            return None

        user_prompt = (
            "Сгенерируй мягкий ответ поддержки для абитуриента. "
            "Помоги разложить задачу на маленькие шаги. "
            "Ответ должен быть коротким и понятным, 3-5 предложений.\n\n"
            f"Ситуация: {situation or 'обычная тревога или неопределённость из-за поступления'}\n"
            f"Сообщение пользователя: {user_text}"
        )
        return await self._ask(user_prompt, max_tokens=300)

    async def explain_comparison(self, items: list[dict[str, Any]]) -> str | None:
        if not self.client or not items:
            return None

        user_prompt = (
            "Коротко поясни сравнение вузов для абитуриента. "
            "Объясни простым языком, какой вариант выглядит безопаснее по минимальному баллу, "
            "какой амбициознее, и на что обратить внимание. "
            "Не обещай поступление, не давай гарантий, не дави на пользователя. "
            "Обязательно скажи, что данные демонстрационные и их нужно сверить с официальными сайтами вузов.\n\n"
            f"Варианты для сравнения: {json.dumps(items[:3], ensure_ascii=False)}"
        )
        return await self._ask(user_prompt, max_tokens=320)

    async def explain_recommendation_groups(
        self,
        profile: dict[str, Any],
        groups: dict[str, list[dict[str, Any]]],
    ) -> str | None:
        if not self.client:
            return None

        safe_profile = {
            "region": profile.get("region"),
            "score": profile.get("score"),
            "direction": profile.get("direction"),
            "education_type": profile.get("education_type"),
        }
        group_counts = {category: len(items) for category, items in groups.items()}
        preview = {
            category: items[:2]
            for category, items in groups.items()
            if category in {"safe", "realistic", "ambitious"}
        }

        user_prompt = (
            "Коротко объясни группировку вузов по категориям: безопасные, реалистичные, амбициозные. "
            "Ответ должен быть 3-5 предложений, спокойным и практичным. "
            "Не обещай поступление и не называй тестовые данные официальными. "
            "Посоветуй начать с безопасных и реалистичных вариантов, а амбициозные оставить как цель.\n\n"
            f"Профиль пользователя: {json.dumps(safe_profile, ensure_ascii=False)}\n"
            f"Количество вариантов по категориям: {json.dumps(group_counts, ensure_ascii=False)}\n"
            f"Примеры вариантов: {json.dumps(preview, ensure_ascii=False)}"
        )
        return await self._ask(user_prompt, max_tokens=320)

    async def answer_free_question(self, text: str) -> str | None:
        if is_crisis_message(text):
            return CRISIS_RESPONSE

        if not self.client or not text.strip():
            return None

        user_prompt = (
            "Ответь как Аиша, мягкий AI-помощник для абитуриента. "
            "Помогай выбрать направление, составить короткий план поступления или снизить перегруз. "
            "Ответ должен быть коротким и практичным.\n\n"
            f"Сообщение пользователя: {text}"
        )
        return await self._ask(user_prompt, max_tokens=360)

    async def _ask(self, user_prompt: str, max_tokens: int) -> str | None:
        if not self.client:
            return None

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.4,
                max_tokens=max_tokens,
            )
        except Exception:
            logger.exception("OpenAI request failed")
            return None

        message = response.choices[0].message.content if response.choices else None
        return message.strip() if message else None


ai_service = AIService()


def is_ai_available() -> bool:
    return ai_service.is_ai_available()


async def explain_results(profile: dict[str, Any], results: list[dict[str, Any]]) -> str | None:
    return await ai_service.explain_results(profile, results)


async def generate_support_reply(user_text: str, situation: str | None = None) -> str | None:
    return await ai_service.generate_support_reply(user_text, situation)


async def explain_comparison(items: list[dict[str, Any]]) -> str | None:
    return await ai_service.explain_comparison(items)


async def explain_recommendation_groups(
    profile: dict[str, Any],
    groups: dict[str, list[dict[str, Any]]],
) -> str | None:
    return await ai_service.explain_recommendation_groups(profile, groups)
