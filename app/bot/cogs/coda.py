import logging
import time
from dataclasses import dataclass

import discord
from discord.ext import commands

from app.clients.warframe.rotation_timers.coda import coda_rotation


class CodaCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)

    @commands.command(
        name="coda",
        description="Current Coda rotation",
        aliases=["coda_rotation"],
    )
    async def coda_cmd(self, ctx: commands.Context):
        await self.coda(ctx)

    @discord.app_commands.command(
        name="coda", description="Current Coda rotation"
    )
    async def coda_app_command(self, interaction: discord.Interaction):
        context: commands.Context = await self.bot.get_context(interaction)
        await self.coda(context)

    async def coda(self, ctx: commands.Context):
        try:
            start = time.time()
            parsed = CodaBuilder.parse_coda()
            message = CodaBuilder.build_coda_message(parsed)

            processing_time = round((time.time() - start) * 1000)
            message["embed"].set_footer(text=f"Processing time: {processing_time}ms")
            await ctx.send(**message)

        except Exception as e:
            self.logger.error(f"Error fetching coda: {str(e)}")
            embed = discord.Embed(
                color=discord.Color.red(),
                title="Error",
                description="Failed to fetch coda. Please try again later.",
            )
            await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(CodaCog(bot))


@dataclass(frozen=True)
class ParsedCoda:
    primary: list[str]
    secondary: list[str]
    melee: list[str]
    next_rotation_ts: int

    @property
    def expiry_text(self) -> str:
        return f"Ends: <t:{self.next_rotation_ts}:R>"


class CodaBuilder:
    @staticmethod
    def parse_coda() -> ParsedCoda:
        rotation = coda_rotation.get_current_rotation_data()
        next_ts = coda_rotation.get_next_rotation_timestamp()

        return ParsedCoda(
            primary=rotation.primary,
            secondary=rotation.secondary,
            melee=rotation.melee,
            next_rotation_ts=next_ts,
        )

    @staticmethod
    def build_coda_message(parsed: ParsedCoda) -> dict:
        embed = discord.Embed(
            color=discord.Color.green(),
            title="Current Coda Rotation",
            description=parsed.expiry_text,
        )
        embed.add_field(
            name="Primary",
            value="- " + "\n- ".join(parsed.primary),
            inline=False,
        )
        embed.add_field(
            name="Secondary",
            value="- " + "\n- ".join(parsed.secondary),
            inline=False,
        )
        embed.add_field(
            name="Melee",
            value="- " + "\n- ".join(parsed.melee),
            inline=False,
        )
        return {"embed": embed}