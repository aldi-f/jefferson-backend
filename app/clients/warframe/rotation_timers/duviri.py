from dataclasses import dataclass

from app.clients.warframe.rotation_timers.interval import IntervalRotationTimer

CYCLE_TIME = 36000
STATE_TIME = 7200
EPOCH_OFFSET = 52

STATES = [
    {"name": "Sorrow", "kullervo": True, "poi": ["Archarbor", "Kullervo's Hold"]},
    {"name": "Fear", "kullervo": True, "poi": ["Amphitheater", "Kullervo's Hold"]},
    {"name": "Joy", "kullervo": False, "poi": ["Archarbor", "Amphitheater"]},
    {"name": "Anger", "kullervo": True, "poi": ["Amphitheater", "Kullervo's Hold"]},
    {"name": "Envy", "kullervo": False, "poi": ["Archarbor", "Amphitheater"]},
]


@dataclass(frozen=True)
class DuviriRotationData:
    name: str
    kullervo: bool
    poi: list[str]


class DuviriRotation(IntervalRotationTimer):
    def __init__(
        self,
        epoch_offset: int = EPOCH_OFFSET,
        cycle_time: int = CYCLE_TIME,
        state_time: int = STATE_TIME,
    ):
        super().__init__(epoch_offset=epoch_offset, cycle_time=cycle_time, state_time=state_time)

    @property
    def rotation_count(self) -> int:
        return len(STATES)

    def get_rotation_data(self, index: int) -> DuviriRotationData:
        state = STATES[index % len(STATES)]
        return DuviriRotationData(
            name=state["name"],
            kullervo=state["kullervo"],
            poi=state["poi"],
        )


duviri_rotation = DuviriRotation()
