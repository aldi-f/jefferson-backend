import logging
import time
from dataclasses import dataclass

import discord
from discord.ext import commands

from app.clients.warframe.worldstate.client import worldstate_client
from app.clients.warframe.worldstate.parsers.baro import Baro


class BaroKiteer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)

    @commands.hybrid_command(
        name="baro",
        with_app_command=True,
        description="Show current baro status and his inventory.",
    )
    async def baro(self, ctx: commands.Context):
        """
        Usage: -baro\n
        Show current baro status and his inventory
        """
        try:
            start = time.time()
            worldstate = await worldstate_client.get_worldstate()
            parsed_baro = BaroBuilder.parse(worldstate.void_traders)

            message = BaroBuilder.build_message(parsed_baro)

            processing_time = round((time.time() - start) * 1000)
            # add latency footer to all embeds
            for embed in message["embeds"]:
                embed.set_footer(
                    text=f"{embed.footer.text}\nProcessing time: {processing_time}ms"
                )
            view = BaroView(message["embeds"])

            await ctx.send(embed=message["embeds"][0], view=view)
        except Exception as e:
            self.logger.error(f"Error fetching Baro: {str(e)}")
            embed = discord.Embed(
                color=discord.Color.red(),
                title="Error",
                description="Failed to fetch Baro. Please try again later.",
            )
            await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(BaroKiteer(bot))


class BaroView(discord.ui.View):
    def __init__(self, embeds: list[discord.Embed], timeout: int = 180):
        super().__init__(timeout=timeout)
        self.embeds = embeds
        self.current_page = 0
        self.message = None

        # Disable buttons if only one page
        if len(self.embeds) <= 1:
            self.previous_button.disabled = True
            self.next_button.disabled = True
        else:
            self.previous_button.disabled = True

    def update_buttons(self):
        self.previous_button.disabled = self.current_page == 0
        self.next_button.disabled = self.current_page == len(self.embeds) - 1

    @discord.ui.button(label="◀", style=discord.ButtonStyle.primary)
    async def previous_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if self.current_page > 0:
            self.current_page -= 1
            self.update_buttons()
            await interaction.response.edit_message(
                embed=self.embeds[self.current_page], view=self
            )

    @discord.ui.button(label="▶", style=discord.ButtonStyle.primary)
    async def next_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if self.current_page < len(self.embeds) - 1:
            self.current_page += 1
            self.update_buttons()
            await interaction.response.edit_message(
                embed=self.embeds[self.current_page], view=self
            )


@dataclass(frozen=True)
class ParsedInventory:
    item: str
    ducats: int
    credits: int
    limit: int

    @property
    def ducat_emote(self) -> str:
        return "<:Ducat:967433339868950638>"

    @property
    def credit_emote(self) -> str:
        return "<:Credits:967435392427106348>"

    @property
    def item_key(self) -> str:
        if self.limit == 0:
            return f"{self.item}"

        return f"{self.item} ({self.limit} left)"

    @property
    def item_cost(self) -> str:
        return f"{self.ducats}{self.ducat_emote} | {self.credits}{self.credit_emote}"


@dataclass(frozen=True)
class ParsedBaro:
    location: str
    activation_ts: int
    expiry_ts: int
    inventory: list[ParsedInventory]

    @property
    def activation_text(self) -> str:
        return f"Incoming: <t:{self.activation_ts}:R>"

    @property
    def expiry_text(self) -> str:
        return f"Leaving: <t:{self.expiry_ts}:R>"


class BaroBuilder:
    items_per_page = 15  # discord limit on embed fields

    @staticmethod
    def parse(worldstate_baro: list[Baro]) -> ParsedBaro:

        # list with 1 element
        actual_worldstate_baro = worldstate_baro[0]
        inventory_list = []

        for item in actual_worldstate_baro.manifest:
            inventory_list.append(
                ParsedInventory(
                    item=item.item_type,
                    ducats=item.ducats,
                    credits=item.credits,
                    limit=item.limit or 0,
                )
            )

        return ParsedBaro(
            location=actual_worldstate_baro.node,
            activation_ts=int(actual_worldstate_baro.activation.timestamp()),
            expiry_ts=int(actual_worldstate_baro.expiry.timestamp()),
            inventory=inventory_list,
        )

    @staticmethod
    def build_message(parsed_object: ParsedBaro) -> dict:

        # Empty inventory means baro isn't active
        # If no baro active, activation text would be the next time he arrives
        if len(parsed_object.inventory) == 0:
            embed = discord.Embed(color=discord.Colour.blue(), title="Baro Ki'Teer")
            embed.description = parsed_object.activation_text
            embed.color = discord.Colour.red()
            return {"embed": embed}

        total_pages = (
            len(parsed_object.inventory) + BaroBuilder.items_per_page - 1
        ) // BaroBuilder.items_per_page

        embeds = []
        for page in range(total_pages):
            start = page * BaroBuilder.items_per_page
            end = min(start + BaroBuilder.items_per_page, len(parsed_object.inventory))

            embed = discord.Embed(color=discord.Colour.blue(), title="Baro Ki'Teer")
            embed.description = parsed_object.expiry_text

            for item in parsed_object.inventory[start:end]:
                embed.add_field(
                    name=item.item_key,
                    value=item.item_cost,
                    inline=False,
                )
            embed.set_footer(text=f"Page {page + 1}/{total_pages}")
            embeds.append(embed)

        return {"embeds": embeds}
