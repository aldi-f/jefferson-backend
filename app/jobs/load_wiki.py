# from typing import Iterable
# from app.clients.redis import redis

# async def fetch_wiki_items() -> Iterable[str]:
#     # TODO: implement actual wiki/GitHub data pulling
#     return ["Excalibur", "Rhino", "Nova"]

# async def load_wiki_items():
#     await redis.ensure_connected()
#     items = await fetch_wiki_items()
#     for item in items:
#         await redis.client.sadd("wiki_items", item)
