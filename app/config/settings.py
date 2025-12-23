import os
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Settings:
    # Discord Configuration
    DISCORD_TOKEN: str = os.getenv("DISCORD_TOKEN", "")
    COMMAND_PREFIX: str = os.getenv("COMMAND_PREFIX", "-")
    TESTING_GUILD_ID: Optional[int] = (
        int(os.getenv("TESTING_GUILD_ID", ""))
        if os.getenv("TESTING_GUILD_ID")
        else None
    )
    
    # Redis Configuration
    REDIS_HOST: str = os.getenv("REDIS_HOST", "redis_jeff")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6378"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "1"))
    REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD")
    REDIS_URL: str = os.getenv("REDIS_URL", f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}")
    
    # Warframe API Configuration
    WORLDSTATE_URL: str = os.getenv("WORLDSTATE_URL", "https://api.warframe.com/cdn/worldState.php")
    WFM_BASE_URL: str = os.getenv("WFM_BASE_URL", "https://api.warframe.market/v1")
    WIKI_API_URL: str = os.getenv("WIKI_API_URL", "https://wiki.warframe.com/api.php")
    
    # Data Refresh Configuration
    DATA_REFRESH_INTERVAL: int = int(os.getenv("DATA_REFRESH_INTERVAL", "3600"))  # 1 hour
    WORLDSTATE_CACHE_TTL: int = int(os.getenv("WORLDSTATE_CACHE_TTL", "300"))      # 5 minutes
    
    # Job Configuration
    JOB_MAX_RETRIES: int = int(os.getenv("JOB_MAX_RETRIES", "5"))
    JOB_RETRY_DELAY: int = int(os.getenv("JOB_RETRY_DELAY", "2"))
    
    # Jobs-specific configuration
    WIKI_DATA_URL: str = os.getenv("WIKI_DATA_URL", "https://wiki.warframe.com/api.php")
    GITHUB_DATA_URL: str = os.getenv("GITHUB_DATA_URL", "https://raw.githubusercontent.com/aldi-f/warframe-wiki-scraper/refs/heads/main/data")
    DATA_CACHE_SECONDS: int = int(os.getenv("DATA_CACHE_SECONDS", "3600"))  # 1 hour
    
    # Web Server Configuration
    ENABLE_FASTAPI: bool = os.getenv("ENABLE_FASTAPI", "false").lower() == "true"
    WEB_HOST: str = os.getenv("WEB_HOST", "0.0.0.0")
    WEB_PORT: int = int(os.getenv("WEB_PORT", "8000"))
    WEB_DEBUG: bool = os.getenv("WEB_DEBUG", "false").lower() == "true"
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: Optional[str] = os.getenv("LOG_FILE")
    LOG_MAX_BYTES: int = int(os.getenv("LOG_MAX_BYTES", "10485760"))  # 10MB
    LOG_BACKUP_COUNT: int = int(os.getenv("LOG_BACKUP_COUNT", "5"))
    
    # OpenAI Configuration
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    
    # GitHub Data Sources
    GITHUB_SOURCES: dict = {
        "ability": "https://raw.githubusercontent.com/aldi-f/warframe-wiki-scraper/refs/heads/main/data/ability.json",
        "arcane": "https://raw.githubusercontent.com/aldi-f/warframe-wiki-scraper/refs/heads/main/data/arcane.json",
        "blueprint": "https://raw.githubusercontent.com/aldi-f/warframe-wiki-scraper/refs/heads/main/data/blueprints.json",
        "companion": "https://raw.githubusercontent.com/aldi-f/warframe-wiki-scraper/refs/heads/main/data/companions.json",
        "enemy": "https://raw.githubusercontent.com/aldi-f/warframe-wiki-scraper/refs/heads/main/data/enemies.json",
        "internalnames": "https://raw.githubusercontent.com/aldi-f/warframe-wiki-scraper/refs/heads/main/data/internal_names.json",
        "missions": "https://raw.githubusercontent.com/aldi-f/warframe-wiki-scraper/refs/heads/main/data/missions.json",
        "mod": "https://raw.githubusercontent.com/aldi-f/warframe-wiki-scraper/refs/heads/main/data/mods.json",
        "skins": "https://raw.githubusercontent.com/WFCD/warframe-items/master/data/json/Skins.json",
        "tennogen": "https://raw.githubusercontent.com/aldi-f/warframe-wiki-scraper/refs/heads/main/data/tennogen.json",
        "void": "https://raw.githubusercontent.com/aldi-f/warframe-wiki-scraper/refs/heads/main/data/void.json",
        "warframe": "https://raw.githubusercontent.com/aldi-f/warframe-wiki-scraper/refs/heads/main/data/warframes.json",
        "weapon": "https://raw.githubusercontent.com/aldi-f/warframe-wiki-scraper/refs/heads/main/data/weapons.json",
    }
    
    # Which cogs to load (module paths)
    COGS: tuple[str, ...] = (
        "app.bot.cogs.alerts",
        "app.bot.cogs.arcane",
        "app.bot.cogs.archon",
        "app.bot.cogs.baro",
        "app.bot.cogs.bounty",
        "app.bot.cogs.calendar",
        "app.bot.cogs.circuit",
        "app.bot.cogs.coda",
        "app.bot.cogs.darvo",
        "app.bot.cogs.duviri",
        "app.bot.cogs.eda",
        "app.bot.cogs.fissure",
        "app.bot.cogs.help",
        "app.bot.cogs.mod",
        "app.bot.cogs.nightwave",
        "app.bot.cogs.ping",
        "app.bot.cogs.pricecheck",
        "app.bot.cogs.prime",
        "app.bot.cogs.profile",
        "app.bot.cogs.pset",
        "app.bot.cogs.relic",
        "app.bot.cogs.riven",
        "app.bot.cogs.sortie",
        "app.bot.cogs.weapons",
    )


settings = Settings()
