import json
from functools import cache

from app.clients.redis import redis_client
from app.config.settings import settings


def normalize_internal_name(internal_name: str) -> str:
    """Remove unnecessary characters from an internal name."""
    new_internal_name = internal_name

    # For vendor items, remove StoreItems from the name
    new_internal_name = new_internal_name.replace("StoreItems/", "")

    # For nightwave quests, add suffix for description only
    if new_internal_name.startswith("/Lotus/Types/Challenges/Seasons/"):
        unique_name = new_internal_name.split("/")[-1]
        new_internal_name = (
            f"/Lotus/Language/NightwaveChallenges/Challenge_{unique_name}_Description"
        )

    # Others

    return new_internal_name


@cache
def localize_internal_name(internal_name: str, language: str = "en") -> str:
    """Localize an internal name."""
    new_internal_name = normalize_internal_name(internal_name)

    data = redis_client.get(f"internalnames:{language}:{settings.CACHE_VERSION}")

    if data:
        return json.loads(data).get(new_internal_name, new_internal_name)

    return new_internal_name


@cache
def localize_internal_mission_name(internal_name: str) -> str:
    data = redis_client.get(f"missions:{settings.CACHE_VERSION}")
    if data:
        data = json.loads(data)
        obj = data["by"]["InternalName"].get(internal_name, [])
        if len(obj) > 0:
            mission = obj[0]
            return f"{mission['Name']} ({mission['Planet']})"
    return internal_name


@cache
def localize_internal_mission_type(internal_name: str) -> str:
    data = redis_client.get(f"missions:{settings.CACHE_VERSION}")
    if data:
        data = json.loads(data)
        mission_types = data["MissionTypes"]
        for mission_type, mission_dict in mission_types.items():
            if mission_dict.get("InternalName") == internal_name:
                return mission_type
    return internal_name
