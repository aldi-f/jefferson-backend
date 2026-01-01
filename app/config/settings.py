import os
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Settings:
    # Discord Configuration
    DISCORD_TOKEN: str = os.getenv("DISCORD_TOKEN", "")
    COMMAND_PREFIX: str = os.getenv("COMMAND_PREFIX", "-")
    TESTING_GUILD_ID: int | None = (
        int(os.getenv("TESTING_GUILD_ID", ""))
        if os.getenv("TESTING_GUILD_ID")
        else None
    )

    # Redis Configuration
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "1"))
    REDIS_PASSWORD: str | None = os.getenv("REDIS_PASSWORD")
    REDIS_URL: str = os.getenv(
        "REDIS_URL", f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
    )

    # Warframe API Configuration
    WORLDSTATE_URL: str = os.getenv(
        "WORLDSTATE_URL", "https://api.warframe.com/cdn/worldState.php"
    )
    WORLDSTATE_CACHE_TTL: int = int(
        os.getenv("WORLDSTATE_CACHE_TTL", "300")
    )  # 5 minutes

    # Job Configuration
    JOB_MAX_RETRIES: int = int(os.getenv("JOB_MAX_RETRIES", "5"))
    JOB_RETRY_DELAY: int = int(os.getenv("JOB_RETRY_DELAY", "2"))

    # Jobs-specific configuration
    GITHUB_DATA_URL: str = os.getenv(
        "GITHUB_DATA_URL",
        "https://raw.githubusercontent.com/aldi-f/warframe-wiki-scraper/refs/heads/main/data",
    )
    DATA_REFRESH_INTERVAL: int = int(
        os.getenv("DATA_REFRESH_INTERVAL", "3600")
    )  # 1 hour
    DATA_CACHE_SECONDS: int = int(os.getenv("DATA_CACHE_SECONDS", "3600"))  # 1 hour

    # Web Server Configuration
    ENABLE_FASTAPI: bool = os.getenv("ENABLE_FASTAPI", "false").lower() == "true"
    WEB_HOST: str = os.getenv("WEB_HOST", "0.0.0.0")
    WEB_PORT: int = int(os.getenv("WEB_PORT", "8000"))
    WEB_DEBUG: bool = os.getenv("WEB_DEBUG", "false").lower() == "true"

    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str | None = os.getenv("LOG_FILE")
    LOG_MAX_BYTES: int = int(os.getenv("LOG_MAX_BYTES", "10485760"))  # 10MB
    LOG_BACKUP_COUNT: int = int(os.getenv("LOG_BACKUP_COUNT", "5"))

    # OpenRouter Configuration
    OPENROUTER_API_KEY: str | None = os.getenv("OPENROUTER_API_KEY")

    # GitHub Data Sources
    GITHUB_SOURCES: dict = field(
        default_factory=lambda: {
            "ability": "https://raw.githubusercontent.com/aldi-f/warframe-wiki-scraper/refs/heads/main/data/ability.json",
            "arcane": "https://raw.githubusercontent.com/aldi-f/warframe-wiki-scraper/refs/heads/main/data/arcane.json",
            "blueprint": "https://raw.githubusercontent.com/aldi-f/warframe-wiki-scraper/refs/heads/main/data/blueprints.json",
            "companion": "https://raw.githubusercontent.com/aldi-f/warframe-wiki-scraper/refs/heads/main/data/companions.json",
            "enemy": "https://raw.githubusercontent.com/aldi-f/warframe-wiki-scraper/refs/heads/main/data/enemies.json",
            "internalnames": "https://raw.githubusercontent.com/aldi-f/warframe-wiki-scraper/refs/heads/main/data/internal_names.json",
            "internalnames:en": "https://raw.githubusercontent.com/calamity-inc/warframe-public-export-plus/refs/heads/senpai/dict.en.json",
            "missions": "https://raw.githubusercontent.com/aldi-f/warframe-wiki-scraper/refs/heads/main/data/missions.json",
            "mod": "https://raw.githubusercontent.com/aldi-f/warframe-wiki-scraper/refs/heads/main/data/mods.json",
            "skins": "https://raw.githubusercontent.com/WFCD/warframe-items/master/data/json/Skins.json",
            "tennogen": "https://raw.githubusercontent.com/aldi-f/warframe-wiki-scraper/refs/heads/main/data/tennogen.json",
            "void": "https://raw.githubusercontent.com/aldi-f/warframe-wiki-scraper/refs/heads/main/data/void.json",
            "warframe": "https://raw.githubusercontent.com/aldi-f/warframe-wiki-scraper/refs/heads/main/data/warframes.json",
            "weapon": "https://raw.githubusercontent.com/aldi-f/warframe-wiki-scraper/refs/heads/main/data/weapons.json",
        }
    )

    # To reference cache keys (e.g. ability:1)
    CACHE_VERSION = os.getenv("CACHE_VERSION", "1")

    # Which cogs to load (module paths)
    COGS: tuple[str, ...] = (
        "app.bot.cogs.alerts",
        # "app.bot.cogs.arcane",
        # "app.bot.cogs.archon",
        # "app.bot.cogs.baro",
        # "app.bot.cogs.bounty",
        # "app.bot.cogs.calendar",
        # "app.bot.cogs.circuit",
        # "app.bot.cogs.coda",
        # "app.bot.cogs.darvo",
        # "app.bot.cogs.duviri",
        # "app.bot.cogs.eda",
        # "app.bot.cogs.fissure",
        "app.bot.cogs.help",
        # "app.bot.cogs.mod",
        # "app.bot.cogs.nightwave",
        # "app.bot.cogs.ping",
        # "app.bot.cogs.pricecheck",
        # "app.bot.cogs.prime",
        # "app.bot.cogs.profile",
        # "app.bot.cogs.pset",
        # "app.bot.cogs.relic",
        # "app.bot.cogs.riven",
        # "app.bot.cogs.sortie",
        # "app.bot.cogs.weapons",
    )


settings = Settings()
