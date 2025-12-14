import asyncio

import aioredis

from app.config.settings import settings


class RedisSingleton:
    _client: aioredis.Redis | None = None
    _lock = asyncio.Lock()

    async def ensure_connected(self):
        async with self._lock:
            if self._client is None:
                kwargs = {}
                if settings.REDIS_TLS:
                    kwargs["ssl"] = True
                self._client = await aioredis.from_url(
                    settings.REDIS_URL, decode_responses=True, **kwargs
                )

    @property
    def client(self) -> aioredis.Redis:
        if self._client is None:
            raise RuntimeError("Redis not connected. Call ensure_connected() first.")
        return self._client

    async def close(self):
        if self._client:
            await self._client.close()
            self._client = None


redis = RedisSingleton()
