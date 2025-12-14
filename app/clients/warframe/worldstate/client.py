# from typing import Any, Dict
# import aiohttp
# from jeff.utils.http import get_shared_session

# BASE_URL = "https://api.warframestat.us"

# class WorldstateClient:
#     def __init__(self, platform: str = "pc", language: str = "en"):
#         self.platform = platform
#         self.language = language

#     async def get(self, path: str) -> Dict[str, Any]:
#         url = f"{BASE_URL}/{self.platform}/{path}?language={self.language}"
#         session = get_shared_session()
#         async with session.get(url, timeout=20) as resp:
#             resp.raise_for_status()
#             return await resp.json()

#     async def get_fissures(self) -> Dict[str, Any]:
#         return await self.get("fissures")

#     async def get_alerts(self) -> Dict[str, Any]:
#         return await self.get("alerts")

#     async def get_cycles(self) -> Dict[str, Any]:
#         return await self.get("cycles")
