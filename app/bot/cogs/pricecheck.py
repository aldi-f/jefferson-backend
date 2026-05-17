import asyncio
import json
import logging
import re
import time

import discord
from discord.ext import commands
from Levenshtein import distance
from openai import OpenAI
from pydantic import BaseModel, ValidationError
from warframe_market.client import WarframeMarketClient
from warframe_market.models.item import ItemShortModel

from app.clients.warframe.market.price_check import PriceCheck
from app.config.settings import settings

logger = logging.getLogger(__name__)


class Items(BaseModel):
    items: list[str]


class ScreenshotScraper:
    def __init__(
        self,
        api_key: str = settings.OPENROUTER_API_KEY,
        base_url: str = "https://openrouter.ai/api/v1",
    ):
        self.api_key = api_key
        self.base_url = base_url

    @staticmethod
    def _generate_prompt(image_url: str) -> list:
        return [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Get me the names of all items here.",
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": image_url},
                    },
                ],
            }
        ]

    @staticmethod
    def _parse_and_validate_json(json_string: str) -> Items | None:
        try:
            data = json.loads(json_string)
            return Items(**data)
        except Exception:
            pass

        try:
            think_pattern = r"([\[\◁]think[\▷\]].*?[\[\◁]\/think[\▷\]])"
            matched = re.search(think_pattern, json_string, re.DOTALL)
            if matched:
                json_string = json_string[matched.end() :].strip()

            start = json_string.find("```json") + len("```json")
            end = json_string.find("```", start)
            json_content = json_string[start:end].strip()
            data = json.loads(json_content)
            return Items(**data)
        except (json.JSONDecodeError, ValidationError):
            return None
        except Exception:
            return None

    async def scrape(self, image_url: str) -> Items | None:
        def _blocking_scrape() -> Items | None:
            client = OpenAI(api_key=self.api_key, base_url=self.base_url)
            try:
                response = client.chat.completions.parse(
                    model="google/gemini-2.5-flash-lite",
                    messages=self._generate_prompt(image_url),
                    extra_body={"provider": {"require_parameters": True}},
                    response_format=Items,
                    n=1,
                )
                return self._parse_and_validate_json(
                    response.choices[0].message.content or ""
                )
            except Exception as e:
                logger.error(f"Error scraping screenshot: {e}")
                return None

        return await asyncio.to_thread(_blocking_scrape)


class ItemValidator:
    _instance = None
    _cached_items: list[ItemShortModel] | None = None
    _cached_time: float = 0
    _CACHE_TTL = 60 * 60 * 2

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def _get_all_market_items(self) -> list[ItemShortModel] | None:
        now = time.time()
        if (
            self._cached_items is not None
            and (now - self._cached_time) < self._CACHE_TTL
        ):
            return self._cached_items
        try:
            client = WarframeMarketClient()
            response = await client.get_all_items()
            self._cached_items = list(response.data)
            self._cached_time = now
            return self._cached_items
        except Exception as e:
            logger.error(f"Error fetching items: {e}")
            return None

    async def validate_items(self, items: list[str]) -> list[ItemShortModel]:
        all_items = await self._get_all_market_items()
        if not all_items:
            return []

        valid_items: list[ItemShortModel] = []
        for item in items:
            item_slug = "_".join(item.lower().strip().split(" "))
            closest_match: ItemShortModel | None = None
            closest_distance = float("inf")
            for market_item in all_items:
                dist = distance(item_slug, market_item.slug)
                if dist < closest_distance:
                    closest_distance = dist
                    closest_match = market_item
            if closest_match:
                valid_items.append(closest_match)
        return valid_items


class PriceCheckPaginationView(discord.ui.View):
    def __init__(
        self, pages: list[discord.Embed], author_id: int, *, timeout: float = 180
    ):
        super().__init__(timeout=timeout)
        self.pages = pages
        self.author_id = author_id
        self.index = 0
        self.message: discord.Message | None = None
        self._update_buttons()

    def _update_buttons(self):
        self.prev_button.disabled = self.index <= 0
        self.next_button.disabled = self.index >= (len(self.pages) - 1)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                "Only the command author can use these buttons.",
                ephemeral=True,
            )
            return False
        return True

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.secondary)
    async def prev_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        self.index = max(0, self.index - 1)
        self._update_buttons()
        await interaction.response.edit_message(embed=self.pages[self.index], view=self)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.secondary)
    async def next_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        self.index = min(len(self.pages) - 1, self.index + 1)
        self._update_buttons()
        await interaction.response.edit_message(embed=self.pages[self.index], view=self)

    async def on_timeout(self):
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = True
        if self.message:
            await self.message.edit(view=self)


class Pricecheck(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)
        self.scraper = ScreenshotScraper()
        self.validator = ItemValidator()

    @commands.hybrid_command(
        name="pricecheck",
        with_app_command=True,
        description="Extract items from a screenshot and check their Warframe Market prices",
        aliases=["check", "pc"],
    )
    async def pricecheck(
        self, ctx: commands.Context, attachment: discord.Attachment | None = None
    ):
        start = time.time()

        attachments = []
        if attachment:
            attachments = [attachment]
        elif ctx.message.attachments:
            attachments = list(ctx.message.attachments)

        if not attachments:
            embed = discord.Embed(
                color=discord.Color.red(),
                description="Provide a screenshot of your inventory to use this command",
            )
            await ctx.send(embed=embed)
            return

        valid_images = [
            a
            for a in attachments
            if a.content_type and a.content_type.startswith("image")
        ]

        if not valid_images:
            embed = discord.Embed(
                color=discord.Color.red(),
                description="Provide a valid image file",
            )
            await ctx.send(embed=embed)
            return

        async with ctx.typing():
            valid_items: list[ItemShortModel] = []
            seen_slugs: set[str] = set()

            for image in valid_images:
                scraped = await self.scraper.scrape(image.url)
                if scraped is None:
                    continue

                items = await self.validator.validate_items(scraped.items)
                for item in items:
                    if item.slug not in seen_slugs:
                        valid_items.append(item)
                        seen_slugs.add(item.slug)

            if not valid_items:
                embed = discord.Embed(
                    color=discord.Color.red(),
                    description="No valid items found in the screenshots.",
                )
                await ctx.send(embed=embed)
                return

            status_msg = await ctx.send(
                f"Found {len(valid_items)} items. Doing Price checks..."
            )

            items_with_price: list[tuple[ItemShortModel, list[int]]] = []
            for i, item in enumerate(valid_items):
                try:
                    price_check = PriceCheck(item=item.slug)
                    price_list = await price_check.check_raw()
                    items_with_price.append((item, price_list))
                except Exception as e:
                    logger.error(
                        f"Error checking price for {item.i18n['en'].name}: {e}"
                    )

                if (i + 1) % 3 == 0:
                    await asyncio.sleep(1)
                    await status_msg.edit(
                        content=f"Found {len(valid_items)} items. Doing Price checks... ({i + 1}/{len(valid_items)})"
                    )

            items_with_price.sort(
                key=lambda x: (
                    x[1][0] if x[1] else 0,
                    sum(x[1]) / len(x[1]) if x[1] else 0,
                ),
                reverse=True,
            )

            total_items = len(items_with_price)
            per_page = 20
            pages: list[discord.Embed] = []
            elapsed = int(time.time() - start)

            for page_index in range(0, total_items, per_page):
                page_items = items_with_price[page_index : page_index + per_page]
                item_text = f"Found {total_items} items in the screenshot:\n"
                for item, prices in page_items:
                    price_text = PriceCheck.format_output(prices)
                    item_text += f"- {item.i18n['en'].name}: {price_text}\n"

                page_num = (page_index // per_page) + 1
                total_pages = (total_items + per_page - 1) // per_page
                page_embed = discord.Embed(
                    title="Price Check", color=discord.Color.blue()
                )
                page_embed.description = item_text
                page_embed.set_footer(
                    text=f"Page {page_num}/{total_pages} \u2022 Processed in {elapsed} seconds"
                )
                pages.append(page_embed)

            if pages:
                view = PriceCheckPaginationView(pages=pages, author_id=ctx.author.id)
                await status_msg.edit(content="", embed=pages[0], view=view)
                view.message = status_msg


async def setup(bot):
    await bot.add_cog(Pricecheck(bot))
