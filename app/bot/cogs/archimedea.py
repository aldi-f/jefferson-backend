import logging
import time
from dataclasses import dataclass

import discord
from discord.ext import commands

from app.clients.warframe.worldstate.client import worldstate_client
from app.clients.warframe.worldstate.parsers.archimedea import Archimedea


class WeeklyArchimedea(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)

    @commands.hybrid_command(
        name="archimedea",
        with_app_command=True,
        description="Data about current Archimedea (ETA/EDA).",
    )
    async def archon(self, ctx: commands.Context):
        """
        Usage: -archimedea\n
        Data about current Archimedea (ETA/EDA).
        """
        try:
            start = time.time()
            worldstate = await worldstate_client.get_worldstate()
            parsed_archimedea = ArchimedeaBuilder.parse(worldstate.conquests)

            message = ArchimedeaBuilder.build_message(parsed_archimedea)

            processing_time = round((time.time() - start) * 1000)
            message["embed"].set_footer(text=f"Processing time: {processing_time}ms")
            await ctx.send(**message)

        except Exception as e:
            self.logger.error(f"Error fetching alerts: {str(e)}")
            embed = discord.Embed(
                color=discord.Color.red(),
                title="Error",
                description="Failed to fetch alerts. Please try again later.",
            )
            await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(WeeklyArchimedea(bot))


@dataclass(frozen=True)
class ParsedArchimedea:
    expiry_ts: int

    @property
    def expiry_text(self) -> str:
        return f"Ends: <t:{self.expiry_ts}:R>"


class ArchimedeaBuilder:
    @staticmethod
    def get_shard(boss: str):
        boss = boss.lower()
        if "amar" in boss:
            return "<:CrimsonArchonShard:1052215232090620034>"

        elif "nira" in boss:
            return "<:AmberArchonShard:1052215210657714327>"

        elif "boreal" in boss:
            return "<:AzureArchonShard:1052215162704253030>"

        else:
            return ""

    @staticmethod
    def parse(worldstate_archon: list[Archimedea]) -> ParsedArchimedea:
        pass

    @staticmethod
    def build_message(parsed_archon: ParsedArchimedea) -> dict:
        embed = discord.Embed(color=discord.Colour.blue(), title="Archon Hunt")
        return {"embed": embed}
