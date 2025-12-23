import discord
from discord.ext import commands
import logging
import time


class Alerts(commands.Cog):
    """Warframe alerts command."""
    
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)

    @commands.hybrid_command(
        name="alerts", 
        with_app_command=True, 
        description="Data about current alerts."
    )
    async def alerts(self, ctx: commands.Context):
        """
        Usage: !alerts\n
        Data about current alerts
        """
        start = time.time()
        embed = discord.Embed(color=discord.Colour.random(), title="Alerts")

        try:
            # Get worldstate data using the new client
            worldstate = await self.bot.worldstate.get_worldstate()
            alerts = worldstate.alerts

            if len(alerts) == 0:
                embed.description = "There are no alerts currently running."
                await ctx.send(embed=embed)
                return

            for alert in alerts:
                info = alert.mission_info
                key = f"{info.location} | {info.mission_type} | {info.faction} | ({info.min_level}-{info.max_level})"

                expiry_text = f"Ends: <t:{int(alert.expiry.timestamp())}:R>\n"

                desc_text = f"**{key}**\n{expiry_text}"

                if len(alert.mission_info.reward) == 0:
                    embed.add_field(
                        name=f"{info.mission_type}",
                        value=desc_text,
                        inline=False
                    )
                else:
                    for reward in alert.mission_info.reward:
                        if reward.__class__.__name__ == "Cred":
                            reward_str = f"{reward.credits:,} Credits"
                        elif reward.__class__.__name__ == "Item":
                            reward_str = f"{reward.name} ({reward.count})"
                        else:
                            reward_str = reward

                        field_name = f"{info.mission_type} - {reward_str}"
                        embed.add_field(name=field_name, value=desc_text, inline=False)

            processing_time = round((time.time() - start) * 1000)
            embed.set_footer(text=f"Processing time: {processing_time}ms")
            await ctx.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Error fetching alerts: {str(e)}")
            embed = discord.Embed(
                color=discord.Color.red(),
                title="Error",
                description="Failed to fetch alerts. Please try again later."
            )
            await ctx.send(embed=embed)


async def setup(bot):
    """Setup function for the alerts cog."""
    await bot.add_cog(Alerts(bot))