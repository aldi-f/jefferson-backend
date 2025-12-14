import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    DISCORD_TOKEN: str = os.getenv("DISCORD_TOKEN", "")
    COMMAND_PREFIX: str = os.getenv("COMMAND_PREFIX", "-")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    TESTING_GUILD_ID: int | None = (
        int(os.getenv("TESTING_GUILD_ID", ""))
        if os.getenv("TESTING_GUILD_ID")
        else None
    )
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    ENABLE_FASTAPI: bool = os.getenv("ENABLE_FASTAPI", "false").lower() == "true"

    # Which cogs to load (module paths)
    COGS: tuple[str, ...] = (
        "app.cogs.alert",
        "app.cogs.arcane",
        "app.cogs.archon",
        "app.cogs.baro",
        "app.cogs.bounty",
        "app.cogs.calendar",
        "app.cogs.circuit",
        "app.cogs.coda",
        "app.cogs.darvo",
        "app.cogs.duviri",
        "app.cogs.eda",
        "app.cogs.event",
        "app.cogs.fissure",
        "app.cogs.help",
        "app.cogs.mod",
        "app.cogs.nightwave",
        "app.cogs.ping",
        "app.cogs.pricecheck",
        "app.cogs.prime",
        "app.cogs.profile",
        "app.cogs.pset",
        "app.cogs.relic",
        "app.cogs.riven",
        "app.cogs.scheduler",
        "app.cogs.sortie",
        "app.cogs.weapon",
    )


settings = Settings()
