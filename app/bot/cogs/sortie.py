import logging
import time
from dataclasses import dataclass

import discord
from discord.ext import commands

from app.clients.warframe.worldstate.client import worldstate_client
from app.clients.warframe.worldstate.parsers.sortie import Sortie as SortieModel


class Sortie(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)

    @commands.hybrid_command(
        name="sortie",
        with_app_command=True,
        description="Data about current Sortie",
    )
    async def sortie(self, ctx: commands.Context):
        """
        Usage: -sortie\n
        Data about current Sortie
        """
        try:
            start = time.time()
            worldstate = await worldstate_client.get_worldstate()
            parsed_sortie = SortieBuilder.parse(worldstate.sorties)

            message = SortieBuilder.build_message(parsed_sortie)

            processing_time = round((time.time() - start) * 1000)
            message["embed"].set_footer(text=f"Processing time: {processing_time}ms")
            await ctx.send(**message)

        except Exception as e:
            self.logger.error(f"Error fetching sortie: {str(e)}")
            embed = discord.Embed(
                color=discord.Color.red(),
                title="Error",
                description="Failed to fetch sortie. Please try again later.",
            )
            await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Sortie(bot))


@dataclass(frozen=True)
class ParsedSortieMissions:
    mission_type: str
    node: str
    modifier_type: str


@dataclass(frozen=True)
class ParsedSortie:
    boss: str
    missions: list[ParsedSortieMissions]
    expiry_ts: int

    @property
    def main_text(self) -> str:
        return f"Boss: {self.boss}"

    @property
    def expiry_text(self) -> str:
        return f"Ends: <t:{self.expiry_ts}:R>"


class SortieBuilder:
    @staticmethod
    def parse(worldstate_sortie: list[SortieModel]) -> ParsedSortie:
        sortie = worldstate_sortie[0]  # list with 1 element
        missions = []
        for mission in sortie.variants:
            missions.append(
                ParsedSortieMissions(
                    mission_type=mission.mission_type,
                    node=mission.node,
                    modifier_type=mission.modifier_type,
                )
            )
        expiry_ts = int(sortie.expiry.timestamp())

        return ParsedSortie(boss=sortie.boss, missions=missions, expiry_ts=expiry_ts)

    @staticmethod
    def build_message(parsed_sortie: ParsedSortie) -> dict:
        embed = discord.Embed(color=discord.Colour.blue(), title="Sortie")
        embed.description = parsed_sortie.main_text + "\n" + parsed_sortie.expiry_text
        for i, mission in enumerate(parsed_sortie.missions):
            embed.add_field(
                name=f"({i + 1}) {mission.mission_type}",
                value=f"{mission.node}\nCondition: {mission.modifier_type}",
                inline=False,
            )
        return {"embed": embed}
