from typing import Protocol

from poop.hfdp.observer.simple.observer import Observer


class Subject(Protocol):
    def register_observer(self, observer: Observer) -> None:
        ...

    def remove_observer(self, observer: Observer) -> None:
        ...

    def notify_observers(self) -> None:
        ...
