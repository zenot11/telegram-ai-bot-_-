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
