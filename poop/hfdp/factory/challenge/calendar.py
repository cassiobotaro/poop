from abc import ABC, abstractmethod

from poop.hfdp.factory.challenge.zone import Zone


class Calendar(ABC):
    _zone: Zone | None = None

    def print(self) -> None:
        if self._zone is None:
            print("No time zone specified")
            return

        print(f"--- {self._zone.get_display_name()} Calendar ---")
        print(f"Offset from GMT: {self._zone.get_offset()}")

    @abstractmethod
    def create_calendar(self, appointments: list[str]) -> None: ...
