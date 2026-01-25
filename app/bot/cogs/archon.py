import logging
import time
from dataclasses import dataclass

import discord
from discord.ext import commands

from app.clients.warframe.worldstate.client import worldstate_client
from app.clients.warframe.worldstate.parsers.archon import ArchonHunt


class Archon(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)

    @commands.hybrid_command(
        name="archon", with_app_command=True, description="Data about current alerts."
    )
    async def archon(self, ctx: commands.Context):
        """
        Usage: -archon\n
        Data about current alerts
        """
        try:
            start = time.time()
            worldstate = await worldstate_client.get_worldstate()
            parsed_archon = ArchonBuilder.parse_archon(worldstate.lite_sorties)

            message = ArchonBuilder.build_archon_message(parsed_archon)

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
    await bot.add_cog(Archon(bot))


@dataclass(frozen=True)
class ParsedArchonMissions:
    mission_type: str
    node: str


@dataclass(frozen=True)
class ParsedArchon:
    boss: str
    shard: str
    missions: list[ParsedArchonMissions]
    expiry_ts: int

    @property
    def main_text(self) -> str:
        return f"Boss: {self.boss}({self.shard})"

    @property
    def expiry_text(self) -> str:
        return f"Ends: <t:{self.expiry_ts}:R>"


class ArchonBuilder:
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
    def parse_archon(worldstate_archon: list[ArchonHunt]) -> ParsedArchon:
        archon = worldstate_archon[0]  # list with 1 element
        missions = []
        for mission in archon.missions:
            missions.append(
                ParsedArchonMissions(
                    mission_type=mission.mission_type, node=mission.node
                )
            )
        expiry_ts = int(archon.expiry.timestamp())

        shard = ArchonBuilder.get_shard(archon.boss)

        return ParsedArchon(
            boss=archon.boss, shard=shard, missions=missions, expiry_ts=expiry_ts
        )

    @staticmethod
    def build_archon_message(parsed_archon: ParsedArchon) -> dict:
        embed = discord.Embed(color=discord.Colour.blue(), title="Archon Hunt")
        embed.description = parsed_archon.main_text + "\n" + parsed_archon.expiry_text
        for i, mission in enumerate(parsed_archon.missions):
            embed.add_field(
                name=f"({i + 1}){mission.mission_type}",
                value=mission.node,
                inline=False,
            )
        return {"embed": embed}
