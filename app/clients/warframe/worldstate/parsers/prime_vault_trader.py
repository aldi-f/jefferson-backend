######################################################
 ## Prime Vault Traders
 ######################################################
from datetime import datetime

from msgspec import Struct, field
from pytz import UTC


def parse_mongo_date(date_dict: dict) -> datetime:
    """Parse MongoDB $date format to datetime."""
    number_long = date_dict["$date"]["$numberLong"]
    timestamp_ms = int(number_long)
    return datetime.fromtimestamp(timestamp_ms / 1000, tz=UTC)


class PrimeVaultTrader(Struct, kw_only=True):
    _id: dict = field(name="_id")
    activation: datetime | dict = field(name="Activation")
    expiry: datetime | dict = field(name="Expiry")
    node: str = field(name="Node")
    item: str = field(name="Item")
    item_icon: str = field(name="ItemIcon")
    item_name: str = field(name="ItemName")
    item_tag: str = field(name="ItemTag")
    item_rarity: str = field(name="ItemRarity")
    vaulted: bool = field(name="Vaulted")

    def __post_init__(self):
        # Parse date fields
        if isinstance(self.activation, dict):
            self.activation = parse_mongo_date(self.activation)
        if isinstance(self.expiry, dict):
            self.expiry = parse_mongo_date(self.expiry)


##########################################################
# Example structure from worldstate.json:
# "PrimeVaultTraders": [
#   {
#     "_id": {
#       "$oid": "6903d8e9726d2ae01b03aa11"
#     },
#     "Activation": {
#       "$date": {
#         "$numberLong": "1761937200000"
#       }
#     },
#     "Expiry": {
#       "$date": {
#         "$numberLong": "1763146800000"
#       }
#     },
#     "Node": "Mercury/Arid",
#     "Item": "/Lotus/Weapons/Corpus/LongGuns/CrpBFG/CrpBFG",
#     "ItemIcon": "/Lotus/Interface/Icons/Items/CrpBFG.png",
#     "ItemName": "BFG",
#     "ItemTag": "/Lotus/Language/Items/CorpusWeaponName",
#     "ItemRarity": "RARE",
#     "Vaulted": true
#   }
# ]