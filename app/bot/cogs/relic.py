import asyncio
import logging
import time

import discord
from discord.ext import commands

from app.clients.warframe.market.price_check import PriceCheck
from app.clients.warframe.wiki.client import wiki_client


class Relic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)

    @commands.hybrid_command(
        name="relic",
        with_app_command=True,
        description="Find what parts your relic drops",
    )
    async def relic(self, ctx: commands.Context, *, relic_name: str = ""):
        start = time.time()

        try:
            message = await RelicBuilder.build_relic_message(relic_name)
            if "embed" in message:
                processing_time = round((time.time() - start) * 1000)
                message["embed"].set_footer(
                    text=f"Processing time: {processing_time}ms"
                )
            await ctx.send(**message)
        except Exception as e:
            self.logger.error(f"Error in relic command: {str(e)}")
            embed = discord.Embed(
                color=discord.Color.red(),
                title="Error",
                description="Failed to fetch relic data. Please try again later.",
            )
            await ctx.send(embed=embed)

    @relic.autocomplete("relic_name")
    async def relic_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> list[discord.app_commands.Choice[str]]:
        names = wiki_client.get_relic_names()
        matches = [
            discord.app_commands.Choice(name=key, value=key)
            for key in names
            if current.lower() in key.lower()
        ]
        return matches[:24]


async def setup(bot):
    await bot.add_cog(Relic(bot))


class RelicBuilder:
    @staticmethod
    def _error_message(description: str) -> dict:
        embed = discord.Embed(
            color=discord.Color.red(), title="Error", description=description
        )
        return {"embed": embed}

    @staticmethod
    async def _fetch_price(
        price_checker: PriceCheck, key: str, returns_dict: dict
    ):
        try:
            if "forma" in price_checker.slug.lower():
                returns_dict[key] = "(N/A)"
                return
            result = await price_checker.check()
            returns_dict[key] = result
        except Exception:
            returns_dict[key] = "(failed)"

    @staticmethod
    async def build_relic_message(relic_name: str) -> dict:
        if not relic_name:
            return RelicBuilder._error_message(
                "Please provide a relic to check."
            )

        void_data = wiki_client.get_void_data()
        if not void_data:
            return RelicBuilder._error_message(
                "No data available. Please try again later."
            )

        relics = void_data.get("RelicData", {})
        relic_key = None
        for key in relics:
            if key.lower() == relic_name.lower():
                relic_key = key
                break

        if not relic_key:
            return RelicBuilder._error_message(
                "This relic doesn't exist! \nCheck if you typed it correctly."
            )

        relic_data = relics[relic_key]
        drops = relic_data.get("Drops", [])

        relic_check = PriceCheck(item=relic_key + " relic")
        price = await relic_check.check_with_quantity()

        info = ""
        if relic_data.get("IsBaro"):
            info = "(B) "
        elif relic_data.get("Vaulted"):
            info = "(V) "

        embed = discord.Embed(
            title=f"{info}{relic_key}\n",
            color=discord.Colour.random(),
            description=f"Price \u00d7 Quantity: {price}",
        )

        returns: dict[int, dict[str, str]] = {}
        tasks = []
        for x in range(min(6, len(drops))):
            returns[x] = {}
            drop = drops[x]
            name = drop["Item"] + " " + drop["Part"]
            returns[x]["name"] = name
            price_checker = PriceCheck(item=name)
            task = asyncio.create_task(
                RelicBuilder._fetch_price(price_checker, "price", returns[x])
            )
            tasks.append(task)

        await asyncio.gather(*tasks)

        if len(drops) >= 6:
            embed.add_field(
                name="Common/Bronze",
                value=f"{returns[0]['name']} {returns[0].get('price', '(N/A)')}\n"
                + f"{returns[1]['name']} {returns[1].get('price', '(N/A)')}\n"
                + f"{returns[2]['name']} {returns[2].get('price', '(N/A)')}",
                inline=False,
            )
            embed.add_field(
                name="Uncommon/Silver",
                value=f"{returns[3]['name']} {returns[3].get('price', '(N/A)')}\n"
                + f"{returns[4]['name']} {returns[4].get('price', '(N/A)')}",
                inline=False,
            )
            embed.add_field(
                name="Rare/Gold",
                value=f"{returns[5]['name']} {returns[5].get('price', '(N/A)')}",
                inline=False,
            )

        return {"embed": embed}