from dataclasses import dataclass

from app.utils.http import http_client


@dataclass(frozen=True)
class RivenAttribute:
    value: float
    url_name: str
    is_positive: bool

    @property
    def display(self) -> str:
        sign = "+" if self.is_positive else ""
        symbol = "%"
        bonus = " ".join(self.url_name.split("_")).capitalize()

        if "range" in self.url_name:
            symbol = "m"
        elif "combo_duration" in self.url_name:
            symbol = "s"
        elif "punch" in self.url_name:
            symbol = ""

        return f"{sign}{self.value}{symbol} {bonus}"


@dataclass(frozen=True)
class RivenListing:
    seller: str
    weapon_url_name: str
    riven_name: str
    buyout_price: int
    attributes: list[RivenAttribute]
    status: str


class RivenClient:
    _instance = None
    platinum_emoji = "<:Platinum:992917150358589550>"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def search_auctions(self, weapon_slug: str) -> list[RivenListing]:
        session = http_client.get_session()
        url = (
            f"https://api.warframe.market/v1/auctions/search"
            f"?type=riven&weapon_url_name={weapon_slug}&sort_by=price_asc"
        )

        async with session.get(url) as resp:
            data = await resp.json()

        auctions = data.get("payload", {}).get("auctions", [])
        listings: list[RivenListing] = []

        for auction in auctions:
            owner = auction.get("owner", {})
            item = auction.get("item", {})
            raw_attributes = item.get("attributes", [])

            attributes = [
                RivenAttribute(
                    value=att["value"],
                    url_name=att["url_name"],
                    is_positive=att.get("positive", True),
                )
                for att in raw_attributes
            ]

            listing = RivenListing(
                seller=owner.get("ingame_name", "Unknown"),
                weapon_url_name=item.get("weapon_url_name", ""),
                riven_name=item.get("name", ""),
                buyout_price=auction.get("buyout_price", 0),
                attributes=attributes,
                status=owner.get("status", "offline"),
            )
            listings.append(listing)

        return listings


riven_client = RivenClient()
