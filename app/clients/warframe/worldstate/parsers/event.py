 ######################################################
 ## Events
 ######################################################
from datetime import datetime

from msgspec import Struct, field
from pytz import UTC

from app.clients.warframe.utils.localization import localize_internal_name


def parse_mongo_date(date_dict: dict) -> datetime:
    """Parse MongoDB $date format to datetime."""
    number_long = date_dict["$date"]["$numberLong"]
    timestamp_ms = int(number_long)
    return datetime.fromtimestamp(timestamp_ms / 1000, tz=UTC)


class _Message(Struct):
    language_code: str = field(name="LanguageCode")
    message: str = field(name="Message")


class _Link(Struct):
    language_code: str = field(name="LanguageCode")
    link: str = field(name="Link")


class Event(Struct, kw_only=True):
    _id: dict = field(name="_id")
    messages: list[_Message] = field(name="Messages")
    prop: str = field(name="Prop")
    icon: str = field(name="Icon")
    priority: bool = field(name="Priority", default=False)
    mobile_only: bool = field(name="MobileOnly", default=False)
    community: bool = field(name="Community", default=False)
    
    # Optional fields
    image_url: str | None = field(name="ImageUrl", default=None)
    date: datetime | dict | None = field(name="Date", default=None)
    event_end_date: datetime | dict | None = field(name="EventEndDate", default=None)
    event_start_date: datetime | dict | None = field(name="EventStartDate", default=None)
    links: list[_Link] | None = field(name="Links", default=None)
    hide_end_date_modifier: bool | None = field(name="HideEndDateModifier", default=None)

    def __post_init__(self):
        # Parse date fields
        if isinstance(self.date, dict):
            self.date = parse_mongo_date(self.date)
        if isinstance(self.event_end_date, dict):
            self.event_end_date = parse_mongo_date(self.event_end_date)
        if isinstance(self.event_start_date, dict):
            self.event_start_date = parse_mongo_date(self.event_start_date)
        
        # Localize internal names if needed
        if isinstance(self.icon, str):
            self.icon = localize_internal_name(self.icon)


##########################################################
# Example structure from worldstate.json:
# "Events": [
#   {
#     "_id": {
#       "$oid": "62d31b87106360aa5703954d"
#     },
#     "Messages": [
#       {
#         "LanguageCode": "en",
#         "Message": "/Lotus/Language/CommunityMessages/JoinDiscord"
#       }
#     ],
#     "Prop": "https://discord.com/invite/playwarframe",
#     "Icon": "/Lotus/Interface/Icons/DiscordIconNoBacker.png",
#     "Priority": false,
#     "MobileOnly": false,
#     "Community": true
#   }
# ]