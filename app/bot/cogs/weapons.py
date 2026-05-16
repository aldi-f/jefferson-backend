import logging
import time
from typing import Any

import discord
from discord.ext import commands

from app.clients.warframe.wiki.client import wiki_client
from app.clients.warframe.wiki.models.weapon import Weapon


class Weapons(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)

    @commands.hybrid_command(
        name="weapon",
        with_app_command=True,
        description="Shows stats for a weapon",
        aliases=["wep", "weap"],
    )
    async def weapon(self, ctx: commands.Context, *, weapon_name: str = ""):
        start = time.time()

        try:
            message = await WeaponBuilder.build_weapon_message(weapon_name)

            if "embed" in message:
                processing_time = round((time.time() - start) * 1000)
                message["embed"].set_footer(
                    text=f"Processing time: {processing_time}ms"
                )

            await ctx.send(**message)
        except Exception as e:
            self.logger.error(f"Error fetching weapon: {str(e)}")
            embed = discord.Embed(
                color=discord.Color.red(),
                title="Error",
                description="Failed to fetch weapon. Please try again later.",
            )
            await ctx.send(embed=embed)

    @weapon.autocomplete("weapon_name")
    async def weapon_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> list[discord.app_commands.Choice[str]]:
        data = wiki_client.get_weapon_data()
        if not data:
            return []

        matches = [
            discord.app_commands.Choice(name=name, value=name)
            for name in data
            if current.lower() in name.lower()
        ]
        return matches[:24]


async def setup(bot):
    await bot.add_cog(Weapons(bot))


class WeaponBuilder:
    @staticmethod
    def _error_message(description: str) -> dict:
        embed = discord.Embed(
            color=discord.Color.red(),
            title="Error",
            description=description,
        )
        return {"embed": embed}

    @staticmethod
    def _get_weapon_data() -> dict | None:
        return wiki_client.get_weapon_data()

    @staticmethod
    def _find_weapon(weapon_name: str, data: dict) -> tuple[str | None, dict | None]:
        for key in data:
            if key.lower() == weapon_name.lower():
                return key, data[key]

        for key in data:
            if weapon_name.lower() in key.lower():
                return key, data[key]

        return None, None

    @staticmethod
    async def build_weapon_message(weapon_name: str) -> dict:
        if not weapon_name:
            return WeaponBuilder._error_message("Please provide a weapon name.")

        weapon_data = WeaponBuilder._get_weapon_data()
        if not weapon_data:
            return WeaponBuilder._error_message(
                "No data available. Please try again later."
            )

        matching_name, matching_data = WeaponBuilder._find_weapon(
            weapon_name, weapon_data
        )
        if not matching_name or not matching_data:
            return WeaponBuilder._error_message("No matching weapon found.")

        weapon_instance = Weapon.from_dict(matching_name, matching_data)

        wiki_url = (
            f"https://wiki.warframe.com/w/{'_'.join(matching_name.split(' '))}"
        )

        wep_embed = discord.Embed(
            title=matching_name,
            description=weapon_instance.get_description(),
            url=wiki_url,
            color=discord.Color.random(),
        )

        for attack in weapon_instance.attacks:
            wep_embed.add_field(
                name=attack.title, value=str(attack), inline=True
            )

        return {"embed": wep_embed}
