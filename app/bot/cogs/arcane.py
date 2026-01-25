import json
import logging
import re
import time
from dataclasses import dataclass

import discord
from discord.ext import commands

from app.clients.redis import redis_client
from app.clients.warframe.market.price_check import PriceCheck
from app.config.settings import settings


class Arcane(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)

    @commands.hybrid_command(
        name="arcane",
        with_app_command=True,
        description="Shows the closest matching arcane and its market price",
    )
    async def arcane(self, ctx: commands.Context, arcane_name: str = ""):
        """
        Usage: -arcane\n
        Shows the closest matching arcane and its market price
        """
        start = time.time()

        try:
            message = await ArcaneBuilder.build_arcane_message(arcane_name)

            if "embed" in message:
                processing_time = round((time.time() - start) * 1000)
                message["embed"].set_footer(
                    text=f"Processing time: {processing_time}ms"
                )

            await ctx.send(**message)
        except Exception as e:
            self.logger.error(f"Error fetching arcane: {str(e)}")
            embed = discord.Embed(
                color=discord.Color.red(),
                title="Error",
                description="Failed to fetch arcane. Please try again later.",
            )
            await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Arcane(bot))


@dataclass(frozen=True)
class ParsedArcane:
    name: str
    rarity: str
    max_rank: int | str
    stats: str
    price_unranked: str
    price_ranked: str


class ArcaneBuilder:
    @staticmethod
    def _error_message(description: str) -> dict:
        embed = discord.Embed(
            color=discord.Color.red(),
            title="Error",
            description=description,
        )
        return {"embed": embed}

    @staticmethod
    def _get_arcane_data() -> dict | None:
        cached_data = redis_client.get(f"arcane:{settings.CACHE_VERSION}")
        if not cached_data:
            return None
        return json.loads(cached_data).get("Arcanes")

    @staticmethod
    def _find_matching_arcane(
        arcane_name: str, arcane_data: dict
    ) -> tuple[str | None, dict | None]:
        # exact match
        for key, value in arcane_data.items():
            if key.lower() == arcane_name.lower():
                return key, value

        # fuzzy match
        for key, value in arcane_data.items():
            if arcane_name.lower() in key.lower():
                return key, value

        return None, None

    @staticmethod
    def _build_stats(matching_arcane: dict) -> str:
        criteria = ""
        if matching_arcane.get("Criteria"):
            criteria = f"{matching_arcane['Criteria']}:\n"
        return f"{criteria}" + re.sub(
            r"<br />", "\n", str(matching_arcane["Description"])
        )

    @staticmethod
    async def build_arcane_message(arcane_name: str) -> dict:
        if not arcane_name:
            return ArcaneBuilder._error_message("Please provide an arcane name.")

        arcane_data = ArcaneBuilder._get_arcane_data()
        if not arcane_data:
            return ArcaneBuilder._error_message(
                "No data available. Please try again later."
            )

        matching_arcane_name, matching_arcane = ArcaneBuilder._find_matching_arcane(
            arcane_name, arcane_data
        )
        if not matching_arcane or not matching_arcane_name:
            return ArcaneBuilder._error_message("No matching arcane found.")

        price_check = PriceCheck(item=matching_arcane_name)
        price_unranked = await price_check.check(rank=0)
        price_ranked = await price_check.check(rank=matching_arcane.get("MaxRank"))

        parsed = ParsedArcane(
            name=matching_arcane_name,
            rarity=matching_arcane.get("Rarity", "Unknown"),
            max_rank=matching_arcane.get("MaxRank", "Unknown"),
            stats=ArcaneBuilder._build_stats(matching_arcane),
            price_unranked=price_unranked,
            price_ranked=price_ranked,
        )

        arcane_embed = discord.Embed(
            title=f"{parsed.name} | {parsed.rarity}",
            description=(
                f"***At maximum rank ({parsed.max_rank})***\n\n"
                f"{parsed.stats}\n\n"
                f"Unranked: {parsed.price_unranked}\n"
                f"Rank {parsed.max_rank}: {parsed.price_ranked}"
            ),
        )
        return {"embed": arcane_embed}
