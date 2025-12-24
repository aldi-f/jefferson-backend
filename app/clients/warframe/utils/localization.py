from app.clients.redis import redis_client


def normalize_internal_name(internal_name: str) -> str:
    """Remove unnecessary characters from an internal name."""
    new_internal_name = internal_name

    # For vendor items, remove StoreItems from the name
    new_internal_name = new_internal_name.replace("StoreItems/", "")

    # Others

    return new_internal_name


def localize_internal_name(internal_name: str, language: str = "en") -> str:
    """Localize an internal name."""
    new_internal_name = normalize_internal_name(internal_name)


def fetch_localized_name(internal_name: str) -> str:
    """Fetch the localized name from the API."""
    # Fetch the localized name from the API
    # ...

    return localized_name
