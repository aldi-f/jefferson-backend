import discord
from discord.ext import commands
import logging


class Ping(commands.Cog):
    """Simple ping command to test bot response."""
    
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)

    @commands.hybrid_command(name="ping", with_app_command=True, description="Test bot connectivity")
    async def ping(self, ctx: commands.Context):
        """Check if the bot is responsive."""
        try:
            # Test Redis connection
            self.bot.redis.client.ping()
            status = "✅ All systems operational"
        except Exception as e:
            self.logger.error(f"Redis ping failed: {str(e)}")
            status = "⚠️ Redis connection issues detected"
        
        embed = discord.Embed(
            color=discord.Color.green(),
            title="Pong!",
            description=status
        )
        embed.set_footer(text=f"Requested by {ctx.author.name}")
        
        await ctx.send(embed=embed)


async def setup(bot):
    """Setup function for the ping cog."""
    await bot.add_cog(Ping(bot))