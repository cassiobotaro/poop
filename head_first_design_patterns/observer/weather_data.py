"""
Notes:
- Setter is used to notify that changes have occurred
- Fields temperature, humidity, pressure are "private".
This means that we are preventing the alteration of any of
them without notification from their observers
- I have doubts about the presence of getters methods in this class.
- WheaterData represents a topic to subcribe containing
states that change.
WeatherData is a subject (Structural typing),
it have all required methods to be a subject.
No need inheretance to implement a subject.
"""
from typing import Protocol


class Observer(Protocol):
    def update(
        self, temperature: float, humidity: float, pressure: float
    ) -> None:
        ...


class Subject(Protocol):
    def register_observer(self, observer: Observer) -> None:
        ...

    def remove_observer(self, observer: Observer) -> None:
        ...

    def notify_observers(self) -> None:
        ...


class WeatherData:
    def __init__(self):
        self.observers: list[Observer] = []
        # abstracts states that when modified
        # will notify their subscribers
        self._temperature: float = 0.0
        self._humidity: float = 0.0
        self._pressure: float = 0.0

    def register_observer(self, observer: Observer) -> None:
        self.observers.append(observer)

    def remove_observer(self, observer: Observer) -> None:
        self.observers.remove(observer)

    def notify_observers(self) -> None:
        for observer in self.observers:
            observer.update(self._temperature, self._humidity, self._pressure)

    def measurements_changed(self) -> None:
        self.notify_observers()

    def set_measurements(
        self, temperature: float, humidity: float, pressure: float
    ) -> None:
        self._temperature = temperature
        self._humidity = humidity
        self._pressure = pressure
        self.measurements_changed()

    def get_temperature(self) -> float:
        return self._temperature

    def get_humidity(self) -> float:
        return self._humidity

    def get_pressure(self) -> float:
        return self._pressure
