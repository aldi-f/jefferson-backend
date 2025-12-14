import asyncio
import os

import discord
from discord.ext import commands

from app.clients.redis import redis
from app.config.settings import settings


class JeffersonBot(commands.Bot):
    def __init__(
        self,
        *args,
        initial_extensions: list[str],
        testing_guild_id: int | None = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.testing_guild_id = testing_guild_id
        self.initial_extensions = initial_extensions

    async def setup_hook(self) -> None:
        for extension in self.initial_extensions:
            await self.load_extension(extension)

        if self.testing_guild_id:
            guild = discord.Object(self.testing_guild_id)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)

        await redis.ensure_connected()


async def start():
    intents = discord.Intents.default()
    intents.message_content = True

    async with JeffersonBot(
        command_prefix=settings.COMMAND_PREFIX,
        intents=intents,
        initial_extensions=settings.COGS,
        testing_guild_id=settings.TESTING_GUILD_ID,
    ) as bot:

        @bot.event
        async def on_ready():
            print(f"Logged in as {bot.user} (id: {bot.user.id})")

        await bot.start(settings.DISCORD_TOKEN)
