import aiohttp
import asyncio
import json
import logging
from typing import List, Dict, Any, Optional

from app.config.settings import settings

logger = logging.getLogger(__name__)


class WarframeMarketClient:
    """Warframe.market API client."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._session = None
        return cls._instance
    
    async def _get_session(self):
        """Get or create aiohttp session."""
        if self._session is None:
            headers = {
                'User-Agent': 'JeffersonBot/2.0',
                'Content-Type': 'application/json'
            }
            self._session = aiohttp.ClientSession(
                base_url=settings.WFM_BASE_URL,
                headers=headers
            )
        return self._session
    
    def _normalize_item_name(self, item_name: str) -> str:
        """Normalize item name for API calls."""
        # Remove blueprint suffix
        if not (
            item_name.lower().endswith("prime blueprint")
            or item_name.lower().endswith("collar blueprint")
        ):
            item_name = item_name.lower().replace(" blueprint", "")
        
        # Replace spaces and special characters
        if "-" in item_name:
            item_name = " ".join(item_name.split("-"))
        if "&" in item_name:
            item_name = item_name.replace("&", "and")
        if "'" in item_name:
            item_name = item_name.replace("'", "")
        
        # Convert to lowercase with underscores
        return "_".join(item_name.lower().split(" "))
    
    async def get_orders(self, item_name: str, mod_rank: Optional[int] = None) -> List[Dict]:
        """Get orders for a specific item."""
        session = await self._get_session()
        clean_name = self._normalize_item_name(item_name)
        
        try:
            async with session.get(f"/items/{clean_name}/orders") as response:
                if response.status == 200:
                    data = await response.json()
                    orders = data.get("payload", {}).get("orders", [])
                    
                    # Filter by mod rank if specified
                    if mod_rank is not None:
                        orders = [
                            order for order in orders
                            if order.get("mod_rank") == mod_rank
                        ]
                    
                    return orders
                elif response.status == 404:
                    # Try adding blueprint suffix
                    blueprint_name = f"{clean_name}_blueprint"
                    async with session.get(f"/items/{blueprint_name}/orders") as bp_response:
                        if bp_response.status == 200:
                            bp_data = await bp_response.json()
                            return bp_data.get("payload", {}).get("orders", [])
                        else:
                            logger.warning(f"Item not found: {item_name}")
                            return []
                else:
                    logger.error(f"WFM API error for {item_name}: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error fetching orders for {item_name}: {e}")
            return []
    
    async def get_sell_orders(self, item_name: str, mod_rank: Optional[int] = None) -> List[Dict]:
        """Get sell orders for a specific item."""
        orders = await self.get_orders(item_name, mod_rank)
        
        # Filter for sell orders from active users
        sell_orders = [
            order for order in orders
            if (order.get("order_type") == "sell" and
                order.get("user", {}).get("status") == "ingame" and
                order.get("user", {}).get("platform") not in ["switch"])
        ]
        
        return sell_orders
    
    async def get_price_stats(self, item_name: str) -> Dict[str, Any]:
        """Get price statistics for an item."""
        session = await self._get_session()
        clean_name = self._normalize_item_name(item_name)
        
        try:
            async with session.get(f"/items/{clean_name}/statistics") as response:
                if response.status == 200:
                    return json.loads(await response.text())
                else:
                    logger.error(f"WFM stats error for {item_name}: {response.status}")
                    return {}
        except Exception as e:
            logger.error(f"Error fetching stats for {item_name}: {e}")
            return {}
    
    async def pricecheck(self, item_name: str, mod_rank: Optional[int] = None) -> List[int]:
        """Get lowest 3 prices for an item."""
        sell_orders = await self.get_sell_orders(item_name, mod_rank)
        
        if not sell_orders:
            return [10000, 10000, 10000]  # Return high prices as "not found"
        
        # Sort by price and get lowest 3
        sell_orders.sort(key=lambda x: x.get("platinum", 99999))
        lowest_prices = [order.get("platinum", 10000) for order in sell_orders[:3]]
        
        # Pad with 10000 if less than 3 orders found
        while len(lowest_prices) < 3:
            lowest_prices.append(10000)
        
        return lowest_prices
    
    async def close(self):
        """Close aiohttp session."""
        if self._session:
            await self._session.close()
            self._session = None


# Export singleton instance
wfm_client = WarframeMarketClient()