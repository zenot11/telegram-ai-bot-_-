import asyncio
from typing import Any

import aiohttp


class UniversityAPIError(Exception):
    pass


async def fetch_universities(
    base_url: str,
    region: str,
    score: int,
    direction: str,
    education_type: str,
    limit: int = 5,
) -> list[dict[str, Any]]:
    url = f"{base_url.rstrip('/')}/api/universities"
    params = {
        "region": region,
        "score": str(score),
        "direction": direction,
        "type": education_type,
        "limit": str(limit),
    }

    timeout = aiohttp.ClientTimeout(total=10)
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    raise UniversityAPIError(f"Backend returned HTTP {response.status}")
                payload = await response.json(content_type=None)
    except (aiohttp.ClientError, asyncio.TimeoutError) as exc:
        raise UniversityAPIError("Backend is unavailable") from exc

    if not isinstance(payload, list):
        raise UniversityAPIError("Backend response must be a JSON list")

    return payload[:limit]


async def fetch_directory_items(base_url: str, endpoint: str, limit: int = 30) -> list[str]:
    safe_endpoint = endpoint if endpoint.startswith("/") else f"/{endpoint}"
    url = f"{base_url.rstrip('/')}{safe_endpoint}"

    timeout = aiohttp.ClientTimeout(total=5)
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise UniversityAPIError(f"Backend returned HTTP {response.status}")
                payload = await response.json(content_type=None)
    except (aiohttp.ClientError, asyncio.TimeoutError) as exc:
        raise UniversityAPIError("Backend is unavailable") from exc

    if not isinstance(payload, dict) or not isinstance(payload.get("items"), list):
        raise UniversityAPIError("Backend directory response must contain items")

    items = [str(item).strip() for item in payload["items"] if item is not None and str(item).strip()]
    return items[:limit]


async def fetch_achievements(base_url: str, limit: int = 8) -> list[dict[str, Any]]:
    url = f"{base_url.rstrip('/')}/api/achievements"
    params = {"limit": str(limit)}

    timeout = aiohttp.ClientTimeout(total=5)
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    raise UniversityAPIError(f"Backend returned HTTP {response.status}")
                payload = await response.json(content_type=None)
    except (aiohttp.ClientError, asyncio.TimeoutError) as exc:
        raise UniversityAPIError("Backend is unavailable") from exc

    if not isinstance(payload, dict) or not isinstance(payload.get("items"), list):
        raise UniversityAPIError("Backend achievements response must contain items")

    return [item for item in payload["items"] if isinstance(item, dict)][:limit]
