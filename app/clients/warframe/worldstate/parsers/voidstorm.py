######################################################
## Railjack Fissures
######################################################
from datetime import datetime

from msgspec import Struct, field
from pytz import UTC

from app.clients.warframe.utils.constant import VOID_TYPE
from app.clients.warframe.utils.localization import (
    localize_internal_mission_name,
    localize_mission_type_from_node,
)


def parse_mongo_date(date_dict: dict) -> datetime:
    """Parse MongoDB $date format to datetime."""
    number_long = date_dict["$date"]["$numberLong"]
    timestamp_ms = int(number_long)
    return datetime.fromtimestamp(timestamp_ms / 1000, tz=UTC)


class VoidStorm(Struct):
    activation: datetime | dict = field(name="Activation")
    expiry: datetime | dict = field(name="Expiry")
    node: str = field(name="Node")
    mission_tier: str = field(name="ActiveMissionTier")
    mission_type: str = field(default="")
    tier: int = field(default=0)

    def __post_init__(self):
        if isinstance(self.activation, dict):
            self.activation = parse_mongo_date(self.activation)
        if isinstance(self.expiry, dict):
            self.expiry = parse_mongo_date(self.expiry)
        if isinstance(self.node, str):
            self.mission_type = localize_mission_type_from_node(self.node)
            self.node = localize_internal_mission_name(self.node)
        if isinstance(self.mission_tier, str):
            self.mission_tier = VOID_TYPE.get(self.mission_tier, self.mission_tier)
            self.tier = list(VOID_TYPE.values()).index(self.mission_tier) + 1


######################################################
# "VoidStorms": [
#   {
#     "_id": {
#       "$oid": "6974f5e2acf2479ed5ce5f4a"
#     },
#     "Node": "CrewBattleNode501",
#     "Activation": {
#       "$date": {
#         "$numberLong": "1769276401401"
#       }
#     },
#     "Expiry": {
#       "$date": {
#         "$numberLong": "1769281801401"
#       }
#     },
#     "ActiveMissionTier": "VoidT2"
#   },
#   {
#     "_id": {
#       "$oid": "6974f5e2acf2479ed5ce5f48"
#     },
#     "Node": "CrewBattleNode518",
#     "Activation": {
#       "$date": {
#         "$numberLong": "1769276401396"
#       }
#     },
#     "Expiry": {
#       "$date": {
#         "$numberLong": "1769281801396"
#       }
#     },
#     "ActiveMissionTier": "VoidT1"
#   },
