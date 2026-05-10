import logging
import time
from dataclasses import dataclass

import discord
from discord.ext import commands

from app.clients.warframe.rotation_timers.duviri import duviri_rotation


class DuviriCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)

    @commands.command(
        name="duviri",
        description="Current Duviri rotation",
        aliases=["duviri_rotation"],
    )
    async def duviri_cmd(self, ctx: commands.Context):
        await self.duviri(ctx)

    @discord.app_commands.command(name="duviri", description="Current Duviri rotation")
    async def duviri_app_command(self, interaction: discord.Interaction):
        context: commands.Context = await self.bot.get_context(interaction)
        await self.duviri(context)

    async def duviri(self, ctx: commands.Context):
        try:
            start = time.time()
            parsed = DuviriBuilder.parse_duviri()
            message = DuviriBuilder.build_duviri_message(parsed)

            processing_time = round((time.time() - start) * 1000)
            message["embed"].set_footer(text=f"Processing time: {processing_time}ms")
            await ctx.send(**message)

        except Exception as e:
            self.logger.error(f"Error fetching duviri: {str(e)}")
            embed = discord.Embed(
                color=discord.Color.red(),
                title="Error",
                description="Failed to fetch duviri. Please try again later.",
            )
            await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(DuviriCog(bot))


@dataclass(frozen=True)
class ParsedDuviri:
    name: str
    kullervo: bool
    poi: list[str]
    next_rotation_ts: int
    next_name: str
    next_kullervo: bool

    @property
    def expiry_text(self) -> str:
        next_kullervo_text = " (Kullervo)" if self.next_kullervo else ""
        return (
            f"Next: {self.next_name}{next_kullervo_text} <t:{self.next_rotation_ts}:R>"
        )


class DuviriBuilder:
    @staticmethod
    def parse_duviri() -> ParsedDuviri:
        rotation = duviri_rotation.get_current_rotation_data()
        next_ts = duviri_rotation.get_next_rotation_timestamp()
        next_index = duviri_rotation.get_current_state_index() + 1
        next_rotation = duviri_rotation.get_rotation_data(
            next_index % duviri_rotation.rotation_count
        )

        return ParsedDuviri(
            name=rotation.name,
            kullervo=rotation.kullervo,
            poi=rotation.poi,
            next_rotation_ts=next_ts,
            next_name=next_rotation.name,
            next_kullervo=next_rotation.kullervo,
        )

    @staticmethod
    def build_duviri_message(parsed: ParsedDuviri) -> dict:
        embed = discord.Embed(
            color=discord.Color.purple(),
            title="Duviri Cycles",
            description=f"# {parsed.name}\n{'*Kullervo can spawn here*' if parsed.kullervo else ''}\n\n{parsed.expiry_text}",
        )
        poi_text = "- " + "\n- ".join(parsed.poi)
        embed.add_field(
            name="Points of Interest",
            value=poi_text,
            inline=False,
        )
        return {"embed": embed}
