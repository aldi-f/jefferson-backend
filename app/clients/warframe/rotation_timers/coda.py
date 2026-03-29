from dataclasses import dataclass
from datetime import datetime, timedelta

from pytz import UTC

from app.clients.warframe.rotation_timers.base import RotationTimer

PINNED_START = datetime(2026, 3, 29, 0, 0, 0, tzinfo=UTC)
DAYS_IN_ROTATION = 4

ROTATIONS = [
    {
        "Primary": ["Coda Hema", "Coda Sporothrix"],
        "Secondary": ["Coda Catabolyst", "Coda Pox", "Coda Dual Torxica"],
        "Melee": ["Coda Mire", "Coda Motovore"],
    },
    {
        "Primary": ["Coda Bassocyst", "Coda Synapse", "Coda Bubonico"],
        "Secondary": ["Coda Tysis"],
        "Melee": ["Coda Caustacyst", "Coda Hirudo", "Coda Pathocyst"],
    },
]


@dataclass(frozen=True)
class CodaRotationData:
    primary: list[str]
    secondary: list[str]
    melee: list[str]


class CodaRotation(RotationTimer):
    def __init__(
        self, start_date: datetime = PINNED_START, interval_days: int = DAYS_IN_ROTATION
    ):
        super().__init__(start_date=start_date, interval_days=interval_days)

    @property
    def rotation_count(self) -> int:
        return len(ROTATIONS)

    def get_rotation_data(self, index: int) -> CodaRotationData:
        rotation = ROTATIONS[index % len(ROTATIONS)]
        return CodaRotationData(
            primary=rotation["Primary"],
            secondary=rotation["Secondary"],
            melee=rotation["Melee"],
        )

    def get_next_rotation_in(self, now: datetime | None = None) -> timedelta:
        if now is None:
            now = datetime.now(UTC)
        elapsed_days = (now - self.start_date).days
        if elapsed_days < 0:
            return timedelta(0)
        days_until_next = self.interval_days - (elapsed_days % self.interval_days)
        return timedelta(days=days_until_next)


coda_rotation = CodaRotation()
