import logging
import time

import discord
from discord.ext import commands

from app.clients.warframe.worldstate.client import worldstate_client


class Alerts(commands.Cog):
    """Warframe alerts command."""

    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)

    @commands.hybrid_command(
        name="alerts", with_app_command=True, description="Data about current alerts."
    )
    async def alerts(self, ctx: commands.Context):
        """
        Usage: -alerts\n
        Data about current alerts
        """
        start = time.time()
        embed = discord.Embed(color=discord.Colour.random(), title="Alerts")

        try:
            # Get worldstate data using the new client
            worldstate = await worldstate_client.get_worldstate()
            self.logger.info(f"Received worldstate data: {worldstate}")
            alerts = worldstate.alerts
            # if len(alerts) == 0:
            #     embed.description = "There are no alerts currently running."
            #     await ctx.send(embed=embed)
            #     return

            self.logger.info(f"Processing {alerts} alerts")
            for alert in alerts:
                info = alert.mission_info
                key = f"{info.location} | {info.mission_type} | {info.faction} | ({info.min_level}-{info.max_level})"

                expiry_text = f"Ends: <t:{int(alert.expiry.timestamp())}:R>\n"

                if info.max_waves:
                    wave_text = f"Waves: {info.max_waves}\n"
                else:
                    wave_text = ""

                rewards = info.mission_reward
                reward_text = "Rewards:\n"
                if rewards.credits:
                    reward_text += f"- **Credits**: x{rewards.credits}\n"
                
                # Handle both items and counted_items
                if rewards.items:
                    for item in rewards.items:
                        reward_text += f"- **{item}**: x1\n"
                elif rewards.counted_items:
                    for item in rewards.counted_items:
                        reward_text += f"- **{item.item}**: x{item.quantity}\n"

                value = f"{expiry_text}{wave_text}{reward_text}"
                embed.add_field(name=key, value=value, inline=False)

            processing_time = round((time.time() - start) * 1000)
            embed.set_footer(text=f"Processing time: {processing_time}ms")
            await ctx.send(embed=embed)
        except Exception as e:
            self.logger.error(f"Error fetching alerts: {str(e)}")
            embed = discord.Embed(
                color=discord.Color.red(),
                title="Error",
                description="Failed to fetch alerts. Please try again later.",
            )
            await ctx.send(embed=embed)


async def setup(bot):
    """Setup function for the alerts cog."""
    await bot.add_cog(Alerts(bot))
