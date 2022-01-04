from typing import Any

from poop.hfdp.observer.util import Observable
from poop.hfdp.observer.weather_observable.weather_data import WeatherData


class StatisticsDisplay:
    def __init__(self, observable: Observable) -> None:
        self.__max_temp = 0.0
        self.__min_temp = 200.0
        self.__temp_sum = 0.0
        self.__num_readings = 0
        self.__observable = observable
        self.__observable.add_observer(self)

    def update(self, observable: Observable, arg: Any) -> None:
        if isinstance(observable, WeatherData):
            weather_data = observable
            temp = weather_data.get_temperature()
            self.__temp_sum += temp
            self.__num_readings += 1

            if temp > self.__max_temp:
                self.__max_temp = temp

            if temp < self.__min_temp:
                self.__min_temp = temp

            self.display()

    def display(self) -> None:
        average = self.__temp_sum / self.__num_readings
        print(
            "Avg/Max/Min temperature = "
            f"{average:.1f}/{self.__max_temp:.1f}/{self.__min_temp:.1f}"
        )
