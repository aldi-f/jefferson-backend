import json

from app.clients.redis import redis_client
from app.config.settings import settings


class WikiClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _get_cached(self, key: str) -> dict | None:
        cached_data = redis_client.get(f"{key}:{settings.CACHE_VERSION}")
        if not cached_data:
            return None
        return json.loads(cached_data)

    def get_weapon_data(self) -> dict | None:
        return self._get_cached("weapon")

    def get_void_data(self) -> dict | None:
        return self._get_cached("void")

    def get_prime_names(self) -> list[str]:
        void_data = self.get_void_data()
        if not void_data:
            return []
        primes = void_data.get("PrimeData", {})
        return [key for key in primes if "Prime" in key]

    def get_relic_names(self) -> list[str]:
        void_data = self.get_void_data()
        if not void_data:
            return []
        return list(void_data.get("RelicData", {}).keys())

    def find_prime(self, query: str) -> tuple[str | None, dict | None]:
        void_data = self.get_void_data()
        if not void_data:
            return None, None

        primes = void_data.get("PrimeData", {})
        query_lower = query.lower()

        for prime_key in primes:
            if "Prime" not in prime_key:
                continue
            if query_lower in prime_key.lower():
                return prime_key, primes[prime_key]
        return None, None

    def find_prime_part(
        self, prime_dict: dict, part_name: str
    ) -> tuple[str | None, dict | None]:
        parts_data = prime_dict.get("Parts", {})
        part_lower = part_name.lower()

        for part_key in parts_data:
            normalized = part_key.lower()
            if len(normalized.split()) > 1:
                normalized = normalized.replace("blueprint", "").strip()
            if part_lower in normalized:
                return part_key, parts_data[part_key]
        return None, None

    def parse_prime_input(self, text: str) -> tuple[str, str] | None:
        if not text or "forma" in text.lower():
            return None

        parts = text.lower().replace("bp", "blueprint").split()

        if len(parts) == 2:
            return parts[0], parts[1]
        elif len(parts) == 3:
            return " ".join(parts[:2]), parts[2]
        else:
            return " ".join(parts[:2]), " ".join(parts[2:])

    def get_relic_data(self, relic_name: str) -> dict | None:
        void_data = self.get_void_data()
        if not void_data:
            return None

        relics = void_data.get("RelicData", {})
        for key in relics:
            if key.lower() == relic_name.lower():
                return relics[key]
        return None


wiki_client = WikiClient()
