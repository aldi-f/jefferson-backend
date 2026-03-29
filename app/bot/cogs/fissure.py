import logging
import time
from dataclasses import dataclass
from typing import Literal

import discord
from discord.ext import commands

from app.clients.warframe.worldstate.client import worldstate_client
from app.clients.warframe.worldstate.parsers.fissure import Fissure as FissureModel
from app.clients.warframe.worldstate.parsers.voidstorm import (
    VoidStorm as VoidStormModel,
)


class Fissure(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)

    @commands.hybrid_command(
        name="fissure",
        with_app_command=True,
        description="Data about current Fissures.",
    )
    async def fissure(self, ctx: commands.Context, fissure_type: str = ""):
        """
        Usage: -fissure <type>\n
        Data about current Fissures. Type can be sp or rj
        """
        try:
            start = time.time()
            worldstate = await worldstate_client.get_worldstate()
            if fissure_type.lower() not in ["sp", "rj", ""]:
                embed = discord.Embed(
                    color=discord.Color.red(),
                    title="Error",
                    description="Invalid fissure type. Use 'sp' for regular fissures, 'rj' for railjack void storms, or leave empty for normal.",
                )
                await ctx.send(embed=embed)
                return
            parsed_alerts = FissureBuilder.parse(
                starchart=worldstate.active_missions,
                railjack=worldstate.void_storms,
                fissure_type=fissure_type.lower(),
            )

            message = FissureBuilder.build_message(parsed_alerts, fissure_type.lower())

            processing_time = round((time.time() - start) * 1000)
            message["embed"].set_footer(
                text=f"Valid fissure types are: rj (Railjack), sp (Steel Path), <empty> (Normal)\nProcessing time: {processing_time}ms"
            )
            await ctx.send(**message)
        except Exception as e:
            self.logger.error(f"Error fetching fissures: {str(e)}")
            embed = discord.Embed(
                color=discord.Color.red(),
                title="Error",
                description="Failed to fetch fissures. Please try again later.",
            )
            await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Fissure(bot))


@dataclass(frozen=True)
class ParsedFissure:
    location: str
    mission_type: str
    expiry_ts: int
    tier: str

    @property
    def display_key(self) -> str:
        return f"{self.tier} - {self.mission_type}"

    @property
    def display_value(self) -> str:
        return f"{self.location}\nEnds: <t:{self.expiry_ts}:R>"


class FissureBuilder:
    @staticmethod
    def parse(
        starchart: list[FissureModel],
        railjack: list[VoidStormModel],
        fissure_type: Literal["sp", "rj", ""],
    ) -> list[ParsedFissure]:

        if fissure_type == "rj":
            return [
                ParsedFissure(
                    location=fissure.node,
                    mission_type=fissure.mission_type,
                    expiry_ts=int(fissure.expiry.timestamp()),
                    tier=fissure.mission_tier,
                )
                for fissure in railjack
            ]
        elif fissure_type == "sp":
            return [
                ParsedFissure(
                    location=fissure.node,
                    mission_type=fissure.mission_type,
                    expiry_ts=int(fissure.expiry.timestamp()),
                    tier=f"{fissure.modifier}",
                )
                for fissure in starchart
                if fissure.hard
            ]
        else:
            return [
                ParsedFissure(
                    location=fissure.node,
                    mission_type=fissure.mission_type,
                    expiry_ts=int(fissure.expiry.timestamp()),
                    tier=f"{fissure.modifier}",
                )
                for fissure in starchart
                if not fissure.hard
            ]

    @staticmethod
    def build_message(
        parsed_fissures: list[ParsedFissure], fissure_type: Literal["sp", "rj", ""]
    ) -> dict:

        title = (
            "Railjack Void Storms"
            if fissure_type == "rj"
            else "Steel Path Fissures"
            if fissure_type == "sp"
            else "Fissures"
        )
        embed = discord.Embed(color=discord.Colour.blue(), title=title)

        if not parsed_fissures:
            embed.description = "There are no fissures currently running."
            embed.color = discord.Colour.red()
            return {"embed": embed}

        for fissure in parsed_fissures:
            embed.add_field(
                name=fissure.display_key, value=fissure.display_value, inline=False
            )

        return {"embed": embed}
