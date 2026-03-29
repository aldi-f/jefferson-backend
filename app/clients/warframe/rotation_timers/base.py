from dataclasses import dataclass
from datetime import datetime, timedelta

from pytz import UTC


@dataclass
class RotationTimer:
    start_date: datetime
    interval_days: int

    def get_current_rotation_index(self, now: datetime | None = None) -> int:
        if now is None:
            now = datetime.now(UTC)
        elapsed_days = (now - self.start_date).days
        if elapsed_days < 0:
            return 0
        return (elapsed_days // self.interval_days) % self.rotation_count

    def get_next_rotation_date(self, now: datetime | None = None) -> datetime:
        if now is None:
            now = datetime.now(UTC)
        elapsed_days = (now - self.start_date).days
        current_cycle = elapsed_days // self.interval_days
        next_rotation_days = (current_cycle + 1) * self.interval_days
        return self.start_date + timedelta(days=next_rotation_days)

    def get_next_rotation_timestamp(self, now: datetime | None = None) -> int:
        return int(self.get_next_rotation_date(now).timestamp())

    @property
    def rotation_count(self) -> int:
        raise NotImplementedError

    def get_rotation_data(self, index: int):
        raise NotImplementedError

    def get_current_rotation_data(self, now: datetime | None = None):
        return self.get_rotation_data(self.get_current_rotation_index(now))