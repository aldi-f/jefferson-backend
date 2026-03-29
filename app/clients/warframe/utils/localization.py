import json
import re
from functools import lru_cache

from app.clients.redis import redis_client
from app.clients.warframe.utils.constant import *
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


@lru_cache
def localize_internal_name(internal_name: str, language: str = "en") -> str:
    """Localize an internal name."""
    new_internal_name = normalize_internal_name(internal_name)

    suffix = ""
    # Is it a blueprint?
    if "/Components/" in new_internal_name and new_internal_name.endswith("Blueprint"):
        data = redis_client.get(f"recipe:{settings.CACHE_VERSION}")
        if data:
            recipe = json.loads(data).get(new_internal_name)
            if recipe:
                new_internal_name = recipe.get("resultType")
                suffix = " Blueprint"

    # try with language
    data = redis_client.get(f"internalnames:{language}:{settings.CACHE_VERSION}")
    if data:
        test = json.loads(data).get(new_internal_name)

        if test:
            return test + suffix

    # try without language
    data = redis_client.get(f"internalnames:{settings.CACHE_VERSION}")
    if data:
        test = json.loads(data).get(new_internal_name)

        if test:
            return test + suffix

    return new_internal_name


@lru_cache
def localize_internal_mission_name(internal_name: str) -> str:
    data = redis_client.get(f"missions:{settings.CACHE_VERSION}")
    if data:
        data = json.loads(data)
        obj = data["by"]["InternalName"].get(internal_name, [])
        if len(obj) > 0:
            mission = obj[0]
            return f"{mission['Name']} ({mission['Planet']})"
    return internal_name


@lru_cache
def localize_mission_type_from_node(node_internal_name: str) -> str:
    data = redis_client.get(f"missions:{settings.CACHE_VERSION}")
    if data:
        data = json.loads(data)
        obj = data["by"]["InternalName"].get(node_internal_name, [])
        if len(obj) > 0:
            mission = obj[0]
            return mission.get("Type")
    return ""


def localize_internal_mission_type(internal_name: str) -> str:
    return MISSION_TYPE.get(internal_name, internal_name)


def localize_internal_faction_type(internal_name: str) -> str:
    return FACTION_TYPE.get(internal_name, internal_name)


def localize_archimedea_difficulty(internal_name: str) -> str:
    """If mapped, return the description."""
    if internal_name in ARCHIMEDEA_DIFFICULTIES:
        return ARCHIMEDEA_DIFFICULTIES.get(internal_name).get("description")
    return re.sub(r"([a-z])([A-Z])", r"\1 \2", internal_name)


def localize_archimedea_variable(internal_name: str) -> str:
    """If mapped, return the description."""
    if internal_name in ARCHIMEDEA_VARIABLES:
        return ARCHIMEDEA_VARIABLES.get(internal_name).get("description")
    return re.sub(r"([a-z])([A-Z])", r"\1 \2", internal_name)
