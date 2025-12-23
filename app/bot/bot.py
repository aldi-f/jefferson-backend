import logging

import discord
from discord.ext import commands

from app.clients.redis.client import RedisClient
from app.config.settings import settings


class JeffersonBot(commands.Bot):
    """Main Discord bot class for Jefferson."""

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True

        super().__init__(
            command_prefix=settings.COMMAND_PREFIX,
            intents=intents,
            help_command=None,
            case_insensitive=True,
        )

        self.redis = RedisClient()
        self.logger = logging.getLogger("jefferson_bot")

    async def setup_hook(self):
        self.logger.info("Setting up Jefferson bot...")

        # Load cogs
        for cog_module in settings.COGS:
            try:
                await self.load_extension(cog_module)
                self.logger.info(f"Loaded cog: {cog_module}")
            except Exception as e:
                self.logger.error(f"Failed to load cog {cog_module}: {str(e)}")

        # Sync commands if testing guild is specified
        if settings.TESTING_GUILD_ID:
            guild = discord.Object(id=settings.TESTING_GUILD_ID)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
            self.logger.info(
                f"Synced commands to testing guild: {settings.TESTING_GUILD_ID}"
            )
        # Do not sync commands for now
        # else:
        #     await self.tree.sync()
        #     self.logger.info("Synced global commands")

        self.logger.info("Redis connection established")

    async def on_ready(self):
        self.logger.info(f"Bot is ready! Logged in as {self.user}")
        self.logger.info(f"Bot ID: {self.user.id}")
        self.logger.info(f"Connected to {len(self.guilds)} guilds")

    async def on_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ):
        """Global command error handler."""
        self.logger.error(f"Command error in {ctx.command}: {str(error)}")

        if isinstance(error, commands.CommandNotFound):
            return

        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                "❌ Missing required argument. Use the help command for usage."
            )
            return

        if isinstance(error, commands.BadArgument):
            await ctx.send("❌ Invalid argument format.")
            return

        # Generic error response
        await ctx.send("❌ An error occurred while executing that command.")

    async def on_app_command_error(
        self,
        interaction: discord.Interaction,
        error: discord.app_commands.AppCommandError,
    ):
        """Global slash command error handler."""
        self.logger.error(f"Slash command error: {str(error)}")

        if interaction.response.is_done():
            return

        try:
            if isinstance(error, discord.app_commands.CheckFailure):
                await interaction.response.send_message(
                    "❌ You don't have permission to use this command.", ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    "❌ An error occurred while executing this command.", ephemeral=True
                )
        except discord.errors.InteractionResponded:
            pass


async def create_bot() -> JeffersonBot:
    bot = JeffersonBot()
    return bot
