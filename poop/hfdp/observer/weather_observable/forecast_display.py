from typing import Any

from poop.hfdp.observer.util import Observable
from poop.hfdp.observer.weather_observable.weather_data import WeatherData


class ForecastDisplay:
    def __init__(self, observable: Observable):
        self.__current_pressure = 29.79
        self.__last_pressure = 0.0
        self.__observable = observable
        self.__observable.add_observer(self)

    def update(self, observable: Observable, arg: Any) -> None:
        if isinstance(observable, WeatherData):
            weather_data = observable
            self.__last_pressure = self.__current_pressure
            self.__current_pressure = weather_data.get_pressure()
            self.display()

    def display(self) -> None:
        print("Forecast:", end="")
        if self.__current_pressure > self.__last_pressure:
            print("Improving weather on the way!")
        elif self.__current_pressure == self.__last_pressure:
            print("More of the same")
        elif self.__current_pressure < self.__last_pressure:
            print("Watch out for cooler, rainy weather")
