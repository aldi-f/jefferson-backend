######################################################
## Temporal/Deep Archimedea
######################################################
import re
from datetime import datetime

from msgspec import Struct, field
from pytz import UTC

from app.clients.warframe.utils.localization import localize_internal_mission_type


def parse_mongo_date(date_dict: dict) -> datetime:
    """Parse MongoDB $date format to datetime."""
    number_long = date_dict["$date"]["$numberLong"]
    timestamp_ms = int(number_long)
    return datetime.fromtimestamp(timestamp_ms / 1000, tz=UTC)


class _Difficulties(Struct):
    type: str = field(name="type")
    deviation: str = field(name="deviation")
    risks: list[str] = field(name="risks")

    def __post_init__(self):
        self.deviation = re.sub(r"([a-z])([A-Z])", r"\1 \2", self.deviation)
        self.risks = [re.sub(r"([a-z])([A-Z])", r"\1 \2", risk) for risk in self.risks]


class _ArchimedeaMission(Struct):
    faction: str = field(name="faction")
    mission_type: str = field(name="missionType")
    difficulties: list[_Difficulties] = field(name="difficulties")

    def __post_init__(self):
        if isinstance(self.mission_type, str):
            self.mission_type = localize_internal_mission_type(self.mission_type)

            # I'll parse this properly later
            if "defense" in self.mission_type.lower():
                self.mission_type = "Defense"


class Archimedea(Struct):
    activation: datetime | dict = field(name="Activation")
    expiry: datetime | dict = field(name="Expiry")
    type: str = field(name="Type")
    missions: list[_ArchimedeaMission] = field(name="Missions")
    variables: list[str] = field(name="Variables")

    def __post_init__(self):
        if isinstance(self.activation, dict):
            self.activation = parse_mongo_date(self.activation)
        if isinstance(self.expiry, dict):
            self.expiry = parse_mongo_date(self.expiry)


# "Conquests": [
#   {
#     "Activation": {
#       "$date": {
#         "$numberLong": "1768780800000"
#       }
#     },
#     "Expiry": {
#       "$date": {
#         "$numberLong": "1769385600000"
#       }
#     },
#     "Type": "CT_LAB",
#     "Missions": [
#       {
#         "faction": "FC_MITW",
#         "missionType": "MT_ALCHEMY",
#         "difficulties": [
#           {
#             "type": "CD_NORMAL",
#             "deviation": "AlchemicalShields",
#             "risks": ["Voidburst"]
#           },
#           {
#             "type": "CD_HARD",
#             "deviation": "AlchemicalShields",
#             "risks": ["Voidburst", "ShieldedFoes"]
#           }
#         ]
#       },
#       {
#         "faction": "FC_MITW",
#         "missionType": "MT_EXTERMINATION",
#         "difficulties": [
#           {
#             "type": "CD_NORMAL",
#             "deviation": "FortifiedFoes",
#             "risks": ["Deflectors"]
#           },
#           {
#             "type": "CD_HARD",
#             "deviation": "FortifiedFoes",
#             "risks": ["Deflectors", "Quicksand"]
#           }
#         ]
#       },
#       {
#         "faction": "FC_MITW",
#         "missionType": "MT_ASSASSINATION",
#         "difficulties": [
#           {
#             "type": "CD_NORMAL",
#             "deviation": "InfiniteTide",
#             "risks": ["AcceleratedEnemies"]
#           },
#           {
#             "type": "CD_HARD",
#             "deviation": "InfiniteTide",
#             "risks": ["AcceleratedEnemies", "DrainingResiduals"]
#           }
#         ]
#       }
#     ],
#     "Variables": [
#       "OperatorLockout",
#       "Withering",
#       "Starvation",
#       "TimeDilation"
#     ],
#     "RandomSeed": 639655
#   },
#   {
