import logging
import time
from dataclasses import dataclass

import discord
from discord.ext import commands

from app.clients.warframe.worldstate.client import worldstate_client
from app.clients.warframe.worldstate.parsers.circuit import Circuit as CircuitModel


class CircuitCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)

    @commands.hybrid_command(
        name="circuit",
        with_app_command=True,
        description="Show current Circuit rotation for Incarnon Genesis.",
    )
    async def circuit(self, ctx: commands.Context):
        try:
            start = time.time()
            worldstate = await worldstate_client.get_worldstate()
            parsed_circuit = CircuitBuilder.parse(worldstate.circuits)
            message = CircuitBuilder.build_message(parsed_circuit)
            processing_time = round((time.time() - start) * 1000)
            embed = message["embed"]
            embed.set_footer(text=f"Processing time: {processing_time}ms")
            await ctx.send(embed=embed)
        except Exception as e:
            self.logger.error(f"Error fetching Circuit: {str(e)}")
            embed = discord.Embed(
                color=discord.Color.red(),
                title="Error",
                description="Failed to fetch Circuit. Please try again later.",
            )
            await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(CircuitCog(bot))


@dataclass(frozen=True)
class ParsedCircuit:
    expiry_ts: int
    categories: list[tuple[str, list[str]]]

    @property
    def expiry_text(self) -> str:
        return f"<t:{self.expiry_ts}:R>"


class CircuitBuilder:
    @staticmethod
    def parse(worldstate_circuit: list[CircuitModel]) -> ParsedCircuit:
        circuits = worldstate_circuit
        expiry_ts = int(circuits[0].expiry.timestamp())
        categories = [(c.category, c.choices) for c in circuits]
        return ParsedCircuit(expiry_ts=expiry_ts, categories=categories)

    @staticmethod
    def build_message(parsed_object: ParsedCircuit) -> dict:
        embed = discord.Embed(
            color=discord.Colour.blue(),
            title="Current Circuit Rotation",
        )
        description = f"Ends: {parsed_object.expiry_text}\n"
        for category, choices in parsed_object.categories:
            description += f"### {category}\n"
            for choice in choices:
                description += f"- {choice}\n"

        embed.description = description

        return {"embed": embed}
