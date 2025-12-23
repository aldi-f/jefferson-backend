import discord
from discord.ext import commands
import logging
from typing import Optional
from app.config.settings import settings


class Help(commands.Cog):
    """Help command for Jefferson bot."""
    
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)

    @commands.hybrid_command(
        name="help", 
        with_app_command=True, 
        description="Shows help information for bot commands."
    )
    async def help(self, ctx: commands.Context, command_name: Optional[str] = None):
        """Display help information for commands."""
        
        if command_name:
            # Help for specific command
            command = self.bot.get_command(command_name)
            if not command:
                await ctx.send(f"❌ Command `{command_name}` not found.")
                return
            
            embed = discord.Embed(
                color=discord.Color.blue(),
                title=f"Help: {command_name}",
                description=command.description or "No description available."
            )
            
            if command.help:
                embed.add_field(name="Usage", value=f"```{command.help}```", inline=False)
            
            if isinstance(command, commands.HybridCommand):
                embed.add_field(name="Type", value="Slash & Text Command", inline=True)
            else:
                embed.add_field(name="Type", value="Text Command", inline=True)
                
        else:
            # General help
            embed = discord.Embed(
                color=discord.Color.blue(),
                title="Jefferson Bot Help",
                description="A comprehensive Warframe Discord bot with worldstate data, market information, and more."
            )
            
            # Group commands by cog
            cog_commands = {}
            for cmd in self.bot.commands:
                if not cmd.cog:
                    continue
                    
                cog_name = cmd.cog.__class__.__name__
                if cog_name not in cog_commands:
                    cog_commands[cog_name] = []
                cog_commands[cog_name].append(cmd)
            
            # Add fields for each cog
            for cog_name, commands_list in cog_commands.items():
                command_names = [f"`{settings.COMMAND_PREFIX}{cmd.name}`" for cmd in commands_list if cmd.enabled]
                if command_names:
                    embed.add_field(
                        name=cog_name.replace("Cog", ""),
                        value=", ".join(command_names[:10]) + ("..." if len(command_names) > 10 else ""),
                        inline=False
                    )
            
            embed.add_field(
                name="Getting Started",
                value=f"Use `{settings.COMMAND_PREFIX}help <command>` for detailed information about a specific command.",
                inline=False
            )
            
            embed.set_footer(text=f"Bot prefix: {settings.COMMAND_PREFIX}")
        
        await ctx.send(embed=embed)


async def setup(bot):
    """Setup function for the help cog."""
    await bot.add_cog(Help(bot))