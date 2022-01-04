from typing import Any

from poop.hfdp.observer.util import Observable
from poop.hfdp.observer.weather_observable.weather_data import WeatherData


class CurrentConditionsDisplay:
    def __init__(self, observable: Observable):
        self.__temperature = 0.0
        self.__humidity = 0.0
        self.__observable = observable
        self.__observable.add_observer(self)

    def update(self, obs: Observable, arg: Any) -> None:
        if isinstance(obs, WeatherData):
            weather_data = obs
            self.__temperature = weather_data.get_temperature()
            self.__humidity = weather_data.get_humidity()
            self.display()

    def display(self) -> None:
        print(
            f"Current conditions: {self.__temperature:.1f}F degrees "
            f"and {self.__humidity:.1f}% humidity"
        )
