######################################################
 ## Goals
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


class _InterimReward(Struct, kw_only=True):
    credits: int = field(name="credits", default=0)
    xp: int = field(name="xp", default=0)
    items: list[str] = field(name="items", default_factory=list)
    counted_items: list = field(name="countedItems", default_factory=list)


class Goal(Struct, kw_only=True):
    _id: dict = field(name="_id")
    activation: datetime | dict = field(name="Activation")
    expiry: datetime | dict = field(name="Expiry")
    node: str = field(name="Node")
    score_var: str = field(name="ScoreVar")
    score_loc_tag: str = field(name="ScoreLocTag")
    count: int = field(name="Count")
    health_pct: float = field(name="HealthPct")
    regions: list[int] = field(name="Regions")
    desc: str = field(name="Desc")
    tool_tip: str = field(name="ToolTip")
    optional_in_mission: bool = field(name="OptionalInMission")
    tag: str = field(name="Tag")
    upgrade_ids: list[dict] = field(name="UpgradeIds")
    personal: bool = field(name="Personal")
    community: bool = field(name="Community")
    goal_value: int = field(name="Goal")
    reward: _Reward = field(name="Reward")
    interim_goals: list[int] = field(name="InterimGoals")
    interim_rewards: list[_InterimReward] = field(name="InterimRewards")

    def __post_init__(self):
        # Parse date fields
        if isinstance(self.activation, dict):
            self.activation = parse_mongo_date(self.activation)
        if isinstance(self.expiry, dict):
            self.expiry = parse_mongo_date(self.expiry)
        
        # Localize internal names
        if isinstance(self.node, str):
            self.node = localize_internal_name(self.node)
        if isinstance(self.desc, str):
            self.desc = localize_internal_name(self.desc)
        if isinstance(self.tool_tip, str):
            self.tool_tip = localize_internal_name(self.tool_tip)
        if isinstance(self.score_loc_tag, str):
            self.score_loc_tag = localize_internal_name(self.score_loc_tag)


##########################################################
# Example structure from worldstate.json:
# "Goals": [
#   {
#     "_id": {
#       "$oid": "5c7cb0d00000000000000000"
#     },
#     "Activation": {
#       "$date": {
#         "$numberLong": "1769101200000"
#       }
#     },
#     "Expiry": {
#       "$date": {
#         "$numberLong": "1770310800000"
#       }
#     },
#     "Node": "SolNode129",
#     "ScoreVar": "FissuresClosed",
#     "ScoreLocTag": "/Lotus/Language/G1Quests/HeatFissuresEventScore",
#     "Count": 4,
#     "HealthPct": 0.04,
#     "Regions": [1],
#     "Desc": "/Lotus/Language/G1Quests/HeatFissuresEventName",
#     "ToolTip": "/Lotus/Language/G1Quests/HeatFissuresEventDesc",
#     "OptionalInMission": true,
#     "Tag": "HeatFissure",
#     "UpgradeIds": [...],
#     "Personal": true,
#     "Community": true,
#     "Goal": 100,
#     "Reward": {...},
#     "InterimGoals": [5, 25, 50, 75],
#     "InterimRewards": [...]
#   }
# ]