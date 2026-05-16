import json
import time
from typing import Any

from warframe_market.client import WarframeMarketClient

from app.clients.redis import redis_client
from app.config.settings import settings


class MarketItemsCache:
    _instance = None
    _items: list[dict[str, Any]] | None = None
    _last_fetch: float = 0
    _ttl: int = 3600

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _is_fresh(self) -> bool:
        return (
            self._items is not None
            and (time.time() - self._last_fetch) < self._ttl
        )

    async def get_items(self) -> list[dict[str, Any]]:
        if self._is_fresh():
            return self._items

        redis_data = redis_client.get(
            f"market_items:{settings.CACHE_VERSION}"
        )
        if redis_data:
            self._items = json.loads(redis_data)
            self._last_fetch = time.time()
            return self._items

        items = await self._from_api()
        return items

    async def _from_api(self) -> list[dict[str, Any]]:
        client = WarframeMarketClient()
        items_response = await client.get_all_items()

        serialized = []
        for item in items_response.data:
            en_name = None
            if item.i18n:
                en_name = item.i18n.get("en", next(iter(item.i18n.values()))).name

            serialized.append(
                {
                    "name": en_name,
                    "slug": item.slug,
                    "max_rank": item.max_rank,
                    "max_charges": item.max_charges,
                    "subtypes": item.subtypes,
                    "tags": item.tags,
                }
            )

        self._items = serialized
        self._last_fetch = time.time()

        redis_client.set(
            f"market_items:{settings.CACHE_VERSION}",
            json.dumps(serialized),
            ex=settings.DATA_CACHE_SECONDS,
        )

        return self._items

    def invalidate(self):
        self._items = None
        self._last_fetch = 0


market_items_cache = MarketItemsCache()
