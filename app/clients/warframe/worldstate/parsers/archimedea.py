######################################################
## Temporal/Deep Archimedea
######################################################
from datetime import datetime

from msgspec import Struct, field
from pytz import UTC

from app.clients.warframe.utils.localization import (
    localize_internal_mission_name,
    localize_internal_name,
)


def parse_mongo_date(date_dict: dict) -> datetime:
    """Parse MongoDB $date format to datetime."""
    number_long = date_dict["$date"]["$numberLong"]
    timestamp_ms = int(number_long)
    return datetime.fromtimestamp(timestamp_ms / 1000, tz=UTC)


class _Difficulties(Struct):
    type: str = field(name="Type")
    deviation: str = field(name="Deviation")
    risks: list[str] = field(name="Risks")


class _ArchimedeaMission(Struct):
    faction: str = field(name="Faction")
    type: str = field(name="Type")
    difficulties: list[_Difficulties] = field(name="difficulties")


class Archimedea(Struct):
    activation: datetime | dict = field(name="Activation")
    expiry: datetime | dict = field(name="Expiry")
    type: str = field(name="Type")
    missions: list[_ArchimedeaMission] = field(name="Missions")
    variables: list[str] = field(name="Variables")


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
