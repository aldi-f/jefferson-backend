import time

from warframe_market.api import Rivens
from warframe_market.client import WarframeMarketClient


class RivenCache:
    _instance = None
    _weapon_names: list[str] | None = None
    _weapon_data: list[dict] | None = None
    _last_fetch: float = 0
    _ttl: int = 3600

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _is_fresh(self) -> bool:
        return (
            self._weapon_names is not None
            and (time.time() - self._last_fetch) < self._ttl
        )

    async def _fetch(self) -> None:
        client = WarframeMarketClient()
        rivens = await client.get(Rivens)
        self._weapon_data = []
        self._weapon_names = []
        for riven in rivens.data:
            name = riven.i18n.get("en")
            if not name:
                continue
            self._weapon_names.append(name.name)
            self._weapon_data.append({"slug": riven.slug, "name": name.name})
        self._last_fetch = time.time()

    async def get_weapon_names(self) -> list[str]:
        if not self._is_fresh():
            await self._fetch()
        return self._weapon_names or []

    async def resolve_weapon(self, query: str) -> tuple[str | None, str | None]:
        if not self._is_fresh():
            await self._fetch()

        if not self._weapon_data:
            return None, None

        query_lower = query.lower()
        for entry in self._weapon_data:
            if query_lower == entry["name"].lower() or query_lower in entry["name"].lower():
                return entry["slug"], entry["name"]
        return None, None


riven_cache = RivenCache()
