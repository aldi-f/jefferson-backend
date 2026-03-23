import logging
import time
from cmath import e
from dataclasses import dataclass

import discord
from discord.ext import commands

from app.clients.warframe.worldstate.client import worldstate_client
from app.clients.warframe.worldstate.parsers.darvo import Darvo as DarvoModel


class DarvoCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)

    @commands.hybrid_command(
        name="darvo",
        with_app_command=True,
        description="Show current Darvo's daily deal.",
    )
    async def darvo(self, ctx: commands.Context):
        """
        Usage: -darvo\n
        Show current Darvo's daily deal.
        """
        try:
            start = time.time()
            worldstate = await worldstate_client.get_worldstate()
            parsed_darvo = DarvoBuilder.parse(worldstate.daily_deals)

            message = DarvoBuilder.build_message(parsed_darvo)

            processing_time = round((time.time() - start) * 1000)
            embed = message["embed"]
            embed.set_footer(text=f"Processing time: {processing_time}ms")

            await ctx.send(embed=embed)
        except Exception as e:
            self.logger.error(f"Error fetching Darvo: {str(e)}")
            embed = discord.Embed(
                color=discord.Color.red(),
                title="Error",
                description="Failed to fetch Darvo. Please try again later.",
            )
            await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(DarvoCog(bot))


@dataclass(frozen=True)
class ParsedDarvo:
    item: str
    amount_left: int
    amount_total: int
    original_price: int
    sale_price: int
    discount: int
    expiry_ts: int

    @property
    def amount_text(self) -> str:
        return f"{self.amount_left}/{self.amount_total} left"

    @property
    def price_text(self) -> str:
        platinum_emote = "<:Platinum:992917150358589550>"
        return f"~~{self.original_price}~~ {self.sale_price}{platinum_emote} ({self.discount}% off)"

    @property
    def expiry_text(self) -> str:
        return f"<t:{self.expiry_ts}:f>"


class DarvoBuilder:
    @staticmethod
    def parse(worldstate_darvo: list[DarvoModel]) -> ParsedDarvo:
        darvo = worldstate_darvo[0]
        amount_left = darvo.amount_total - darvo.amount_sold

        return ParsedDarvo(
            item=darvo.store_item,
            amount_left=amount_left,
            amount_total=darvo.amount_total,
            original_price=darvo.original_price,
            sale_price=darvo.sale_price,
            discount=darvo.discount,
            expiry_ts=int(darvo.expiry.timestamp()),
        )

    @staticmethod
    def build_message(parsed_object: ParsedDarvo) -> dict:
        embed = discord.Embed(color=discord.Colour.blue(), title="Darvo's Daily Deal")

        description = (
            f"## {parsed_object.item}\n"
            f"### {parsed_object.amount_text}\n"
            f"Price: {parsed_object.price_text}\n\n"
            f"Ends: {parsed_object.expiry_text}"
        )
        embed.description = description
        return {"embed": embed}
