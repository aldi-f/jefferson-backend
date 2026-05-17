import asyncio
import logging
import time

import discord
from discord.ext import commands
from warframe_market.common import Subtype

from app.clients.warframe.market.price_check import PriceCheck
from app.clients.warframe.wiki.client import wiki_client


class Pset(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)

    @commands.hybrid_command(
        name="pset",
        with_app_command=True,
        description="Shows the price breakdown of a prime set",
    )
    async def pset(self, ctx: commands.Context, *, prime_set: str = ""):
        start = time.time()

        try:
            message = await PsetBuilder.build_pset_message(prime_set)
            if "embed" in message:
                processing_time = round((time.time() - start) * 1000)
                message["embed"].set_footer(
                    text=f"Processing time: {processing_time}ms"
                )
            await ctx.send(**message)
        except Exception as e:
            self.logger.error(f"Error in pset command: {str(e)}")
            embed = discord.Embed(
                color=discord.Color.red(),
                title="Error",
                description="Failed to fetch prime set data. Please try again later.",
            )
            await ctx.send(embed=embed)

    @pset.autocomplete("prime_set")
    async def pset_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> list[discord.app_commands.Choice[str]]:
        names = wiki_client.get_prime_names()
        matches = [
            discord.app_commands.Choice(name=key, value=key)
            for key in names
            if current.lower() in key.lower()
        ]
        return matches[:24]


async def setup(bot):
    await bot.add_cog(Pset(bot))


class PsetBuilder:
    @staticmethod
    def _error_message(description: str) -> dict:
        embed = discord.Embed(
            color=discord.Color.red(), title="Error", description=description
        )
        return {"embed": embed}

    @staticmethod
    async def _fetch_price(
        price_checker: PriceCheck, part_key: str, returns_dict: dict
    ):
        try:
            result = await price_checker.check(subtype=Subtype.BLUEPRINT)
            returns_dict[part_key] = result
        except Exception:
            returns_dict[part_key] = "(failed)"

    @staticmethod
    async def build_pset_message(prime_set: str) -> dict:
        if not prime_set:
            return PsetBuilder._error_message(
                "Be sure to provide a prime name"
            )

        if "forma" in prime_set.lower():
            return PsetBuilder._error_message(
                "Why would you search forma"
            )

        prime_key, _ = wiki_client.find_prime(prime_set)
        if not prime_key:
            return PsetBuilder._error_message(
                "Did not find any primes with that name"
            )

        try:
            set_name = f"{prime_key} set"
            set_price_checker = PriceCheck(item=set_name)
            pieces = await set_price_checker.get_set_pieces()
        except Exception:
            set_price_checker = PriceCheck(item=prime_key)
            pieces = await set_price_checker.get_set_pieces()

        returns: dict[str, str] = {}
        await asyncio.gather(
            *[
                PsetBuilder._fetch_price(
                    PriceCheck(item=data["slug"]), piece, returns
                )
                for piece, data in pieces.items()
            ]
        )

        set_piece = next(x for x in pieces.items() if x[1]["set"])
        pieces.pop(set_piece[0])

        text_lines = []
        for part_name, data in pieces.items():
            part_display = part_name.replace(prime_key, "").strip()
            quantity = data["quantity"]
            text_lines.append(
                f"{quantity}\u00d7 {part_display}: {returns.get(part_name, '(N/A)')}"
            )

        set_price = f"Full set: {returns.get(set_piece[0], '(N/A)')}"

        embed = discord.Embed(
            description=set_price + "\n\n" + "\n".join(text_lines),
            title=prime_key,
        )
        return {"embed": embed}