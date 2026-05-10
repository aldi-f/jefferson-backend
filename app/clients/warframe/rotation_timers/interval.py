from dataclasses import dataclass
from datetime import datetime

from pytz import UTC


@dataclass
class IntervalRotationTimer:
    epoch_offset: int
    cycle_time: int
    state_time: int

    @property
    def rotation_count(self) -> int:
        raise NotImplementedError

    def get_rotation_data(self, index: int):
        raise NotImplementedError

    def get_current_state_index(self, now: int | None = None) -> int:
        if now is None:
            now = int(datetime.now(UTC).timestamp())
        cycle_delta = (now - self.epoch_offset) % self.cycle_time
        return (cycle_delta // self.state_time) % self.rotation_count

    def get_next_rotation_timestamp(self, now: int | None = None) -> int:
        if now is None:
            now = int(datetime.now(UTC).timestamp())
        cycle_delta = (now - self.epoch_offset) % self.cycle_time
        state_delta = cycle_delta % self.state_time
        until_next = self.state_time - state_delta
        return now + until_next

    def get_current_rotation_data(self, now: int | None = None):
        return self.get_rotation_data(self.get_current_state_index(now))