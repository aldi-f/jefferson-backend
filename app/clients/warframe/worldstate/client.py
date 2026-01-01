import asyncio
import logging

import aiohttp
import msgspec
from typing_extensions import Self

from app.clients.warframe.worldstate.parsers.worldstate import WorldstateModel
from app.config.settings import settings

logger = logging.getLogger(__name__)


class WorldstateClient:
    """Warframe World State API client with caching."""

    _instance: Self | None = None
    _cached_data = None
    _cached_at: float | None = None

    def __new__(cls) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._session = None
        return cls._instance

    async def _get_session(self):
        """Get or create aiohttp session."""
        if self._session is None:
            self._session = aiohttp.ClientSession()
        return self._session

    async def get_worldstate_raw(self, params: dict = {}):
        """Get raw world state data without caching."""
        try:
            session = await self._get_session()
            async with session.get(settings.WORLDSTATE_URL, params=params) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    logger.error(f"Worldstate API error: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error fetching worldstate: {e}")
            return None

    async def get_worldstate(self):
        """Get current world state with caching."""
        now = asyncio.get_event_loop().time()

        cache_valid = (
            self._cached_data is not None
            and self._cached_at is not None
            and now - self._cached_at < settings.WORLDSTATE_CACHE_TTL
        )

        if not cache_valid:
            try:
                session = await self._get_session()
                async with session.get(settings.WORLDSTATE_URL) as response:
                    if response.status == 200:
                        data = await response.text()
                        self._cached_data = msgspec.json.decode(
                            data, type=WorldstateModel, strict=True
                        )

                        self._cached_at = now
                        logger.info("Worldstate data updated")
                    else:
                        logger.error(f"Worldstate API error: {response.status}")
                        if self._cached_data is None:
                            raise Exception(
                                f"Failed to fetch worldstate and no cache available: {response.status}"
                            )
            except Exception as e:
                logger.error(f"Error fetching worldstate: {e}")
                if self._cached_data is None:
                    raise e

        return self._cached_data

    async def clear_cache(self):
        """Clear cached worldstate data."""
        self._cached_data = None
        self._cached_at = None
        logger.info("Worldstate cache cleared")

    async def close(self):
        """Close aiohttp session."""
        if self._session:
            await self._session.close()
            self._session = None


worldstate_client = WorldstateClient()
