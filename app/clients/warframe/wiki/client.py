import json

from app.clients.redis import redis_client
from app.config.settings import settings


class WikiClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_weapon_data(self) -> dict | None:
        cached_data = redis_client.get(f"weapon:{settings.CACHE_VERSION}")
        if not cached_data:
            return None
        return json.loads(cached_data)


wiki_client = WikiClient()
