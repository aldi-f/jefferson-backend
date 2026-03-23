import logging
import time
from dataclasses import dataclass

import discord
from discord.ext import commands

from app.clients.warframe.worldstate.client import worldstate_client
from app.clients.warframe.worldstate.parsers.nightwave import (
    Nightwave as NightwaveModel,
)


class NightwaveCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)

    @commands.hybrid_command(
        name="nightwave",
        with_app_command=True,
        description="Show current Nightwave season and challenges.",
    )
    async def nightwave(self, ctx: commands.Context):
        try:
            start = time.time()
            worldstate = await worldstate_client.get_worldstate()
            parsed_nightwave = NightwaveBuilder.parse(worldstate.season_info)
            message = NightwaveBuilder.build_message(parsed_nightwave)
            processing_time = round((time.time() - start) * 1000)
            embed = message["embed"]
            embed.set_footer(text=f"Latency: {processing_time}ms")
            await ctx.send(embed=embed)
        except Exception as e:
            self.logger.error(f"Error fetching Nightwave: {str(e)}")
            embed = discord.Embed(
                color=discord.Color.red(),
                title="Error",
                description="Failed to fetch Nightwave. Please try again later.",
            )
            await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(NightwaveCog(bot))


@dataclass(frozen=True)
class ParsedChallenge:
    type: str
    challenge: str
    standing: int

    @property
    def field_key(self) -> str:
        return f"{self.type}: {self.challenge}"

    @property
    def field_value(self) -> str:
        return f"{self.standing} reputation"


@dataclass(frozen=True)
class ParsedNightwave:
    affiliation_tag: str
    challenges: list[ParsedChallenge]


class NightwaveBuilder:
    @staticmethod
    def parse(worldstate_nightwave: NightwaveModel) -> ParsedNightwave:
        challenges = [
            ParsedChallenge(type=c.type, challenge=c.challenge, standing=c.standing)
            for c in worldstate_nightwave.active_challenges
        ]
        return ParsedNightwave(
            affiliation_tag=worldstate_nightwave.affiliation_tag,
            challenges=challenges,
        )

    @staticmethod
    def build_message(parsed_object: ParsedNightwave) -> dict:
        embed = discord.Embed(
            title=parsed_object.affiliation_tag,
            description="Challanges:",
            color=discord.Colour.red(),
        )

        for challange in parsed_object.challenges:
            embed.add_field(
                name=challange.field_key,
                value=challange.field_value,
                inline=False,
            )

        return {"embed": embed}
