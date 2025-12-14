import asyncio

from app.config.logging import configure_logging
from app.config.settings import settings


def bootstrap():
    configure_logging(level=settings.LOG_LEVEL)
    # Future: optionally start FastAPI/Flask here
    # Example:
    # if settings.ENABLE_FASTAPI:
    #     from jeff.web.fastapi_app import run as run_fastapi
    #     run_fastapi()

    # Start bot
    from app.bot import bot

    asyncio.run(bot.start())


if __name__ == "__main__":
    bootstrap()
