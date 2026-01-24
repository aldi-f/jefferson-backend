######################################################
 ## Invasions
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


class _Reward(Struct, kw_only=True):
    credits: int = field(name="credits", default=0)
    xp: int = field(name="xp", default=0)
    items: list[str] = field(name="items", default_factory=list)
    counted_items: list = field(name="countedItems", default_factory=list)


class Invasion(Struct, kw_only=True):
    _id: dict = field(name="_id")
    faction: str = field(name="Faction")
    defender_faction: str = field(name="DefenderFaction")
    node: str = field(name="Node")
    count: int = field(name="Count")
    goal: int = field(name="Goal")
    loc_tag: str = field(name="LocTag")
    completed: bool = field(name="Completed")
    chain_id: dict = field(name="ChainId")
    attacker_reward: _Reward = field(name="AttackerReward")
    defender_reward: _Reward = field(name="DefenderReward")

    def __post_init__(self):
        # Localize internal names
        if isinstance(self.faction, str):
            self.faction = localize_internal_name(self.faction)
        if isinstance(self.defender_faction, str):
            self.defender_faction = localize_internal_name(self.defender_faction)
        if isinstance(self.node, str):
            self.node = localize_internal_name(self.node)
        if isinstance(self.loc_tag, str):
            self.loc_tag = localize_internal_name(self.loc_tag)


##########################################################
# Example structure from worldstate.json:
# "Invasions": [
#   {
#     "_id": {
#       "$oid": "6903d8e9726d2ae01b03aa0e"
#     },
#     "Faction": "FC_CORPUS",
#     "DefenderFaction": "FC_GRINEER",
#     "Node": "Mercury/Sanctuary",
#     "Count": 10,
#     "Goal": 15,
#     "LocTag": "/Lotus/Language/Events/InvasionCorpusVsGrineer",
#     "Completed": false,
#     "ChainID": {
#       "$oid": "6903d8e9726d2ae01b03aa0f"
#     },
#     "AttackerReward": {
#       "credits": 0,
#       "xp": 0,
#       "items": ["/Lotus/StoreItems/Upgrades/Skins/Clan/OrbBadgeItem"],
#       "countedItems": []
#     },
#     "DefenderReward": {
#       "credits": 0,
#       "xp": 0,
#       "items": ["/Lotus/StoreItems/Upgrades/Mods/DualSource/Shotgun/ShotgunMedicMod"],
#       "countedItems": []
#     }
#   }
# ]