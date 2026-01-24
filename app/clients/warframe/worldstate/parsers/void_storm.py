######################################################
 ## Void Storms
 ######################################################
from datetime import datetime

from msgspec import Struct, field
from pytz import UTC


def parse_mongo_date(date_dict: dict) -> datetime:
    """Parse MongoDB $date format to datetime."""
    number_long = date_dict["$date"]["$numberLong"]
    timestamp_ms = int(number_long)
    return datetime.fromtimestamp(timestamp_ms / 1000, tz=UTC)


class VoidStorm(Struct, kw_only=True):
    _id: dict = field(name="_id")
    node: str = field(name="Node")
    activation: datetime | dict = field(name="Activation")
    expiry: datetime | dict = field(name="Expiry")
    seed: int = field(name="Seed")
    modifier: str = field(name="Modifier")

    def __post_init__(self):
        # Parse date fields
        if isinstance(self.activation, dict):
            self.activation = parse_mongo_date(self.activation)
        if isinstance(self.expiry, dict):
            self.expiry = parse_mongo_date(self.expiry)


##########################################################
# Example structure from worldstate.json:
# "VoidStorms": [
#   {
#     "_id": {
#       "$oid": "6903d8e9726d2ae01b03aa10"
#     },
#     "Node": "Mercury/Arid",
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
#     "Seed": 12345,
#     "Modifier": "VOLATILE"
#   }
# ]