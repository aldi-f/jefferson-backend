import discord
from discord.ext import commands
import logging
import re
from typing import Optional

from app.config.settings import settings


class PriceCheck(commands.Cog):
    """Price checking command for Warframe market items."""
    
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)

    @commands.hybrid_command(
        name="pricecheck", 
        with_app_command=True,
        description="Check current market prices for Warframe items."
    )
    @commands.describe(item="Item name to search for")
    async def pricecheck(self, ctx: commands.Context, *, item: str):
        """
        Usage: !pricecheck <item>\n
        Check current market prices for Warframe items
        """
        if not item:
            await ctx.send("❌ Please specify an item to search for.")
            return
        
        await ctx.defer()  # Defer response for potentially long API calls
        
        try:
            # Use the Warframe Market client to search for items
            search_results = await self.bot.wfm.search_items(item)
            
            if not search_results:
                embed = discord.Embed(
                    color=discord.Color.orange(),
                    title="No Results",
                    description=f"No items found matching '**{item}**'"
                )
                await ctx.send(embed=embed)
                return
            
            # Get the first exact match or closest result
            item_data = search_results[0]  # Simplified for now
            
            # Get current orders
            orders = await self.bot.wfm.get_item_orders(item_data.get('url_name', ''))
            
            if not orders:
                embed = discord.Embed(
                    color=discord.Color.orange(),
                    title="No Data Available",
                    description=f"No market data available for **{item_data.get('item_name', item)}**"
                )
                await ctx.send(embed=embed)
                return
            
            # Process orders
            sell_orders = [o for o in orders if o.get('order_type') == 'sell']
            buy_orders = [o for o in orders if o.get('order_type') == 'buy']
            
            # Create embed
            embed = discord.Embed(
                color=discord.Color.green(),
                title=f"Price Check: {item_data.get('item_name', item)}",
                description=f"Current market data from warframe.market"
            )
            
            # Add sell orders
            if sell_orders:
                # Get top 5 cheapest sell orders
                sell_orders.sort(key=lambda x: x.get('platinum', 999999))
                top_sell = sell_orders[:5]
                
                sell_text = ""
                for order in top_sell:
                    rank = order.get('user', {}).get('status', 'Normal')
                    icon = "🟢" if rank == "Ingame" else "🔵"
                    quantity = order.get('quantity', 1)
                    platinum = order.get('platinum', 0)
                    seller = order.get('user', {}).get('ingame_name', 'Unknown')
                    mod_rank = f" (Rank {order.get('mod_rank')})" if order.get('mod_rank') else ""
                    
                    sell_text += f"{icon} **{platinum}** ×{quantity} - {seller}{mod_rank}\n"
                
                embed.add_field(
                    name=f"🔴 Sell Orders ({len(sell_orders)} total)",
                    value=sell_text or "No sell orders available",
                    inline=False
                )
            
            # Add buy orders
            if buy_orders:
                # Get top 5 highest buy orders
                buy_orders.sort(key=lambda x: x.get('platinum', 0), reverse=True)
                top_buy = buy_orders[:5]
                
                buy_text = ""
                for order in top_buy:
                    rank = order.get('user', {}).get('status', 'Normal')
                    icon = "🟢" if rank == "Ingame" else "🔵"
                    quantity = order.get('quantity', 1)
                    platinum = order.get('platinum', 0)
                    buyer = order.get('user', {}).get('ingame_name', 'Unknown')
                    mod_rank = f" (Rank {order.get('mod_rank')})" if order.get('mod_rank') else ""
                    
                    buy_text += f"{icon} **{platinum}** ×{quantity} - {buyer}{mod_rank}\n"
                
                embed.add_field(
                    name=f"🟢 Buy Orders ({len(buy_orders)} total)",
                    value=buy_text or "No buy orders available", 
                    inline=False
                )
            
            embed.set_footer(text="Data refreshed from warframe.market")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            self.logger.error(f"Error checking prices for '{item}': {str(e)}")
            embed = discord.Embed(
                color=discord.Color.red(),
                title="Error",
                description=f"Failed to fetch price data for **{item}**. Please try again later."
            )
            await ctx.send(embed=embed)


async def setup(bot):
    """Setup function for the pricecheck cog."""
    await bot.add_cog(PriceCheck(bot))