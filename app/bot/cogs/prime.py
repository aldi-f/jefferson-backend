import logging
import time

import discord
from discord.ext import commands

from app.clients.warframe.market.price_check import PriceCheck
from app.clients.warframe.wiki.client import wiki_client


class Prime(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)

    @commands.hybrid_command(
        name="prime",
        with_app_command=True,
        description="Find what relics drop a certain prime part",
    )
    async def prime(self, ctx: commands.Context, *, part: str = ""):
        start = time.time()

        try:
            message = await PrimeBuilder.build_prime_message(part)
            if "embed" in message:
                processing_time = round((time.time() - start) * 1000)
                message["embed"].set_footer(
                    text=f"Processing time: {processing_time}ms"
                )
            await ctx.send(**message)
        except Exception as e:
            self.logger.error(f"Error in prime command: {str(e)}")
            embed = discord.Embed(
                color=discord.Color.red(),
                title="Error",
                description="Failed to fetch prime data. Please try again later.",
            )
            await ctx.send(embed=embed)

    @prime.autocomplete("part")
    async def prime_autocomplete(
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
    await bot.add_cog(Prime(bot))


class PrimeBuilder:
    @staticmethod
    def _error_message(description: str) -> dict:
        embed = discord.Embed(
            color=discord.Color.red(), title="Error", description=description
        )
        return {"embed": embed}

    @staticmethod
    async def build_prime_message(part: str) -> dict:
        if not part:
            return PrimeBuilder._error_message(
                "Be sure to provide a prime part name"
            )

        if "forma" in part.lower():
            return PrimeBuilder._error_message("Forma is not implemented for now")

        void_data = wiki_client.get_void_data()
        if not void_data:
            return PrimeBuilder._error_message(
                "No data available. Please try again later."
            )

        relics = void_data.get("RelicData", {})
        parsed = wiki_client.parse_prime_input(part)
        if not parsed:
            return PrimeBuilder._error_message("Invalid input format.")

        item_name, part_name = parsed

        prime_key, prime_dict = wiki_client.find_prime(item_name)
        if not prime_dict:
            item_name = part.split()[0]
            prime_key, prime_dict = wiki_client.find_prime(item_name)
            if not prime_dict:
                return PrimeBuilder._error_message(
                    "Did not find the prime item!"
                )
            part_name = " ".join(part.split()[1:])

        part_key, part_dict = wiki_client.find_prime_part(
            prime_dict, part_name
        )
        if not part_dict:
            return PrimeBuilder._error_message(
                f"Did not find the part for {prime_key}!"
            )

        display_item = prime_key or ""
        if part_key:
            display_part = part_key
            if len(part_key.split()) > 1:
                display_part = part_key.replace("blueprint", "").strip()
            display_item += f" {display_part}"

        lines = []
        drops = part_dict.get("Drops", {})
        for relic_name, rarity in drops.items():
            relic_info = relics.get(relic_name, {})
            info = ""
            if relic_info.get("IsBaro"):
                info = "(B)"
            elif relic_info.get("Vaulted"):
                info = "(V)"
            lines.append(f"`{info:3} {relic_name} - {rarity}`")

        price_name = display_item.strip()
        try:
            price_checker = PriceCheck(item=price_name)
            price = await price_checker.check()
        except Exception:
            price = "(failed)"

        embed = discord.Embed(
            title=display_item,
            description=f"Market price: {price}\n\n" + "\n".join(lines),
        )
        return {"embed": embed}