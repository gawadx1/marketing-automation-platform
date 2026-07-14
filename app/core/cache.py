import json
from typing import Optional, Any
import redis.asyncio as aioredis
from app.core.config import get_settings

settings = get_settings()

_redis_client: Optional[aioredis.Redis] = None


async def get_redis() -> aioredis.Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True,
            health_check_interval=30,
        )
    return _redis_client


async def close_redis():
    global _redis_client
    if _redis_client:
        await _redis_client.close()
        _redis_client = None


def _make_key(key: str) -> str:
    return f"{settings.CACHE_PREFIX}{key}"


async def cache_get(key: str) -> Optional[Any]:
    try:
        r = await get_redis()
        data = await r.get(_make_key(key))
        if data:
            return json.loads(data)
    except Exception:
        pass
    return None


async def cache_set(key: str, value: Any, ttl: Optional[int] = None):
    try:
        r = await get_redis()
        await r.setex(
            _make_key(key),
            ttl or settings.CACHE_TTL_SECONDS,
            json.dumps(value, default=str),
        )
    except Exception:
        pass


async def cache_delete(key: str):
    try:
        r = await get_redis()
        await r.delete(_make_key(key))
    except Exception:
        pass


async def cache_delete_pattern(pattern: str):
    try:
        r = await get_redis()
        full_pattern = _make_key(pattern)
        async for key in r.scan_iter(match=full_pattern, count=100):
            await r.delete(key)
    except Exception:
        pass


async def cache_health_check() -> bool:
    try:
        r = await get_redis()
        await r.ping()
        return True
    except Exception:
        return False
