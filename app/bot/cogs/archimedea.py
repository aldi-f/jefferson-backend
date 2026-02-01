import logging
import time
from dataclasses import dataclass
from typing import Literal

import discord
from discord.ext import commands

from app.clients.warframe.worldstate.client import worldstate_client
from app.clients.warframe.worldstate.parsers.archimedea import Archimedea


class WeeklyArchimedea(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)

    @commands.hybrid_command(name="eta", description="Show the current ETA Rotation")
    async def eta(self, ctx: commands.Context):
        await self.archimedea(ctx, "eta")

    @commands.hybrid_command(name="eda", description="Show the current EDA Rotation")
    async def eda(self, ctx: commands.Context):
        await self.archimedea(ctx, "eda")

    async def archimedea(self, ctx: commands.Context, type: Literal["eta", "eda"]):
        try:
            start = time.time()
            worldstate = await worldstate_client.get_worldstate()
            eta, eda = ArchimedeaBuilder.parse(worldstate.conquests)

            message = ArchimedeaBuilder.build_message(eta if type == "eta" else eda)

            processing_time = round((time.time() - start) * 1000)
            message["embed"].set_footer(
                text=f"**CAUTION**: DE is providing the wrong deviations and risks, verify them in game!\nProcessing time: {processing_time}ms"
            )
            await ctx.send(**message)

        except Exception as e:
            self.logger.error(f"Error fetching alerts: {str(e)}")
            embed = discord.Embed(
                color=discord.Color.red(),
                title="Error",
                description="Failed to fetch alerts. Please try again later.",
            )
            await ctx.send(embed=embed)

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
class ParsedArchimedeaMissionDifficulty:
    type: str
    deviation: str
    risks: list[str]


@dataclass(frozen=True)
class ParsedArchimedeaMissions:
    mission_type: str
    faction: str
    difficulties: list[ParsedArchimedeaMissionDifficulty]

    @property
    def difficulties_text(self) -> str:
        # hard includes normal + the extra risks
        hard = filter(lambda d: d.type == "CD_HARD", self.difficulties).__next__()
        return f"Deviation: {hard.deviation}\n" + f"Risk: {'\nRisk: '.join(hard.risks)}"


@dataclass(frozen=True)
class ParsedArchimedea:
    type: str
    expiry_ts: int
    variables: list[str]
    missions: list[ParsedArchimedeaMissions]

    @property
    def expiry_text(self) -> str:
        return f"Ends: <t:{self.expiry_ts}:R>"


class ArchimedeaBuilder:
    @staticmethod
    def parse(worldstate_archimedea: list[Archimedea]):
        eta_raw = filter(lambda a: a.type == "CT_HEX", worldstate_archimedea).__next__()
        eda_raw = filter(lambda a: a.type == "CT_LAB", worldstate_archimedea).__next__()

        eta_missions = []
        for mission in eta_raw.missions:
            eta_difficulties = []
            for difficulty in mission.difficulties:
                eta_difficulties.append(
                    ParsedArchimedeaMissionDifficulty(
                        type=difficulty.type,
                        deviation=difficulty.deviation,
                        risks=difficulty.risks,
                    )
                )
            eta_missions.append(
                ParsedArchimedeaMissions(
                    mission_type=mission.mission_type,
                    faction=mission.faction,
                    difficulties=eta_difficulties,
                )
            )
        eta = ParsedArchimedea(
            type="Elite Temporal Archimedea",
            expiry_ts=int(eta_raw.expiry.timestamp()),
            variables=eta_raw.variables,
            missions=eta_missions,
        )

        eda_missions = []
        for mission in eda_raw.missions:
            eda_difficulties = []
            for difficulty in mission.difficulties:
                eda_difficulties.append(
                    ParsedArchimedeaMissionDifficulty(
                        type=difficulty.type,
                        deviation=difficulty.deviation,
                        risks=difficulty.risks,
                    )
                )
            eda_missions.append(
                ParsedArchimedeaMissions(
                    mission_type=mission.mission_type,
                    faction=mission.faction,
                    difficulties=eda_difficulties,
                )
            )
        eda = ParsedArchimedea(
            type="Elite Deep Archimedea",
            expiry_ts=int(eda_raw.expiry.timestamp()),
            variables=eda_raw.variables,
            missions=eda_missions,
        )
        return eta, eda

    @staticmethod
    def build_message(parsed_archimedea: ParsedArchimedea) -> dict:
        embed = discord.Embed(color=discord.Colour.blue(), title=parsed_archimedea.type)
        embed.description = parsed_archimedea.expiry_text
        for i, mission in enumerate(parsed_archimedea.missions):
            embed.add_field(
                name=f"({i + 1}) {mission.mission_type}",
                value=mission.difficulties_text,
                inline=False,
            )

        return {"embed": embed}
