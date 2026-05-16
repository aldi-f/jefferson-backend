import logging
import time
from dataclasses import dataclass
from typing import Any

import discord
from discord.ext import commands
from warframe_market.client import WarframeMarketClient

from app.clients.warframe.market.items_cache import market_items_cache


class Wfm(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)

    @commands.hybrid_command(
        name="wfm",
        with_app_command=True,
        description="Search for an item and show its Warframe Market prices",
    )
    async def wfm(self, ctx: commands.Context, *, item_name: str = ""):
        start = time.time()

        try:
            message = await WfmBuilder.build_wfm_message(item_name)

            if "embed" in message:
                processing_time = round((time.time() - start) * 1000)
                message["embed"].set_footer(
                    text=f"Processing time: {processing_time}ms"
                )

            await ctx.send(**message)
        except Exception as e:
            self.logger.error(f"Error in wfm command: {str(e)}")
            embed = discord.Embed(
                color=discord.Color.red(),
                title="Error",
                description="Failed to fetch item prices. Please try again later.",
            )
            await ctx.send(embed=embed)

    @wfm.autocomplete("item_name")
    async def wfm_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> list[discord.app_commands.Choice[str]]:
        items = await market_items_cache.get_items()
        if not items:
            return []

        matches = [
            discord.app_commands.Choice(name=item["name"], value=item["name"])
            for item in items
            if current.lower() in item["name"].lower()
        ]
        return matches[:24]


async def setup(bot):
    await bot.add_cog(Wfm(bot))


@dataclass(frozen=True)
class ParsedOrder:
    platinum: int
    quantity: int


@dataclass(frozen=True)
class ParsedWfmItem:
    name: str
    slug: str
    max_rank: int | None
    max_charges: int | None
    unranked_orders: list[ParsedOrder]
    ranked_orders: list[ParsedOrder] | None


class WfmBuilder:
    platinum_emoji = "<:Platinum:992917150358589550>"

    _show_quantity_keywords = {"lith", "meso", "neo", "axi"}

    @staticmethod
    def _should_show_quantity(item_name: str) -> bool:
        return any(kw in item_name.lower() for kw in WfmBuilder._show_quantity_keywords)

    @staticmethod
    def _error_message(description: str) -> dict:
        embed = discord.Embed(
            color=discord.Color.red(),
            title="Error",
            description=description,
        )
        return {"embed": embed}

    @staticmethod
    async def _get_items() -> list[dict[str, Any]] | None:
        try:
            return await market_items_cache.get_items()
        except Exception:
            return None

    @staticmethod
    def _find_item(
        item_name: str, items: list[dict[str, Any]]
    ) -> dict[str, Any] | None:
        for item in items:
            if item["name"].lower() == item_name.lower():
                return item

        for item in items:
            if item_name.lower() in item["name"].lower():
                return item

        return None

    @staticmethod
    def _format_orders(orders: list[ParsedOrder], show_quantity: bool = False) -> str:
        if not orders:
            return "(N/A)"

        if show_quantity:
            return " | ".join(
                [
                    f"{o.platinum}{WfmBuilder.platinum_emoji} × {o.quantity}"
                    for o in orders
                ]
            )

        return " | ".join(
            [f"{o.platinum}{WfmBuilder.platinum_emoji}" for o in orders]
        )

    @staticmethod
    async def _get_orders(
        slug: str, rank: int | None = None, charges: int | None = None
    ) -> list[ParsedOrder]:
        client = WarframeMarketClient()
        result = await client.get_top_orders_for_item(
            slug=slug, rank=rank, charges=charges
        )
        return [
            ParsedOrder(platinum=order.platinum, quantity=order.quantity)
            for order in result.data.sell
        ][:5]

    @staticmethod
    async def build_wfm_message(item_name: str) -> dict:
        if not item_name:
            return WfmBuilder._error_message("Please provide an item name.")

        items = await WfmBuilder._get_items()
        if not items:
            return WfmBuilder._error_message(
                "No item data available. Please try again later."
            )

        matched = WfmBuilder._find_item(item_name, items)
        if not matched:
            return WfmBuilder._error_message("No matching item found.")

        unranked_orders = await WfmBuilder._get_orders(matched["slug"])

        ranked_orders = None
        rank_label = None
        if matched.get("max_rank") is not None and matched["max_rank"] > 0:
            ranked_orders = await WfmBuilder._get_orders(
                matched["slug"], rank=matched["max_rank"]
            )
            rank_label = f"Rank {matched['max_rank']}"
        elif matched.get("max_charges") is not None and matched["max_charges"] > 0:
            ranked_orders = await WfmBuilder._get_orders(
                matched["slug"], charges=matched["max_charges"]
            )
            rank_label = f"{matched['max_charges']} charges"

        parsed = ParsedWfmItem(
            name=matched["name"],
            slug=matched["slug"],
            max_rank=matched.get("max_rank"),
            max_charges=matched.get("max_charges"),
            unranked_orders=unranked_orders,
            ranked_orders=ranked_orders,
        )

        market_url = f"https://warframe.market/items/{parsed.slug}"

        embed = discord.Embed(
            title=parsed.name,
            url=market_url,
            color=discord.Color.blue(),
        )

        show_qty = WfmBuilder._should_show_quantity(parsed.name)

        embed.add_field(
            name="Lowest 5 Sell Prices",
            value=WfmBuilder._format_orders(parsed.unranked_orders, show_qty),
            inline=False,
        )

        if parsed.ranked_orders:
            embed.add_field(
                name=f"Lowest 5 Sell Prices ({rank_label})",
                value=WfmBuilder._format_orders(parsed.ranked_orders, show_qty),
                inline=False,
            )

        return {"embed": embed}
