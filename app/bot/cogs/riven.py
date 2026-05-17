import logging
import time

import discord
from discord.ext import commands

from app.clients.warframe.market.riven_cache import riven_cache
from app.clients.warframe.market.riven_client import riven_client


class Riven(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)

    @commands.hybrid_command(
        name="riven",
        with_app_command=True,
        description="Shows the matching riven prices for a weapon",
    )
    async def riven(self, ctx: commands.Context, *, weapon: str = ""):
        start = time.time()

        try:
            message = await RivenBuilder.build_riven_message(weapon)
            if "embed" in message:
                processing_time = round((time.time() - start) * 1000)
                message["embed"].set_footer(
                    text=f"Processing time: {processing_time}ms"
                )
            await ctx.send(**message)
        except Exception as e:
            self.logger.error(f"Error in riven command: {str(e)}")
            embed = discord.Embed(
                color=discord.Color.red(),
                title="Error",
                description="Failed to fetch riven data. Please try again later.",
            )
            await ctx.send(embed=embed)

    @riven.autocomplete("weapon")
    async def riven_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> list[discord.app_commands.Choice[str]]:
        names = await riven_cache.get_weapon_names()
        matches = [
            discord.app_commands.Choice(name=name, value=name)
            for name in names
            if current.lower() in name.lower()
        ]
        return matches[:24]


async def setup(bot):
    await bot.add_cog(Riven(bot))


class RivenBuilder:
    @staticmethod
    def _error_message(description: str) -> dict:
        embed = discord.Embed(
            color=discord.Color.red(), title="Error", description=description
        )
        return {"embed": embed}

    @staticmethod
    async def build_riven_message(weapon: str) -> dict:
        if not weapon:
            return RivenBuilder._error_message(
                "Please provide a weapon name."
            )

        slug, display_name = await riven_cache.resolve_weapon(weapon)
        if not slug:
            return RivenBuilder._error_message(
                "Riven not found, make sure to type the correct name."
            )

        listings = await riven_client.search_auctions(slug)

        embed = discord.Embed(
            title=display_name or weapon, color=discord.Color.blue()
        )

        counter = 0
        for listing in listings:
            if counter == 3:
                break
            if listing.status == "offline":
                continue

            attrs_text = "\n".join(att.display for att in listing.attributes)

            embed.add_field(
                name=(
                    f"{listing.seller}: "
                    f"{listing.weapon_url_name.capitalize()} "
                    f"{listing.riven_name.capitalize()} "
                    f"{listing.buyout_price}{riven_client.platinum_emoji}"
                ),
                value=attrs_text,
                inline=False,
            )
            counter += 1

        if counter == 0:
            return RivenBuilder._error_message(
                "No active riven listings found for this weapon."
            )

        return {"embed": embed}