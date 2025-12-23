import asyncio
import logging

from app.bot.bot import create_bot
from app.config.logging import setup_logging
from app.config.settings import settings


async def main():
    setup_logging()
    logger = logging.getLogger("discord_bot_main")

    # Create bot instance
    bot = await create_bot()

    logger.info("Starting Jefferson Discord bot...")

    try:
        # Start the bot
        async with bot:
            await bot.start(settings.DISCORD_TOKEN)
    except Exception as e:
        logger.error(f"Failed to start bot: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
