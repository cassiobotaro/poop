from typing import Any, Protocol


class Observer(Protocol):
    def update(self, observable: "Observable", arg: Any) -> None:
        pass


class Observable:
    def __init__(self) -> None:
        self.observers: list[Observer] = []
        self.changed = False

    def add_observer(self, observer: Observer) -> None:
        self.observers.append(observer)

    def delete_observer(self, observer: Observer) -> None:
        self.observers.remove(observer)

    def delete_observers(self) -> None:
        self.observers.clear()

    def notify_observers(self, value: Any = None) -> None:
        if self.changed:
            for observer in self.observers:
                observer.update(self, value)
            self.clear_changed()

    def count_observers(self) -> int:
        return len(self.observers)

    def has_changed(self) -> bool:
        return self.changed

    def clear_changed(self) -> None:
        self.changed = False

    def set_changed(self) -> None:
        self.changed = True
