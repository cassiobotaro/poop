# Notes:
# All classes are DisplayElement due to the display method.
# No inheritance is needed.
# Structural typing is used here.
# They are also called as observers (they have update method).
from typing import Protocol

from head_first_design_patterns.observer.weather_data import Subject


class DisplayElement(Protocol):
    def display(self) -> None:
        ...


class CurrentConditionsDisplay:
    def __init__(self, weather_data: Subject):
        self._temperature = 0.0
        self._humidity = 0.0
        self._weather_data = weather_data
        self._weather_data.register_observer(self)

    def update(
        self, temperature: float, humidity: float, pressure: float
    ) -> None:
        self._temperature = temperature
        self._humidity = humidity
        self.display()

    def display(self) -> None:
        print(
            f"Current conditions: {self._temperature:.1f}F degrees "
            f"and {self._humidity:.1f}% humidity"
        )


class ForecastDisplay:
    def __init__(self, weather_data: Subject):
        self._current_pressure = 29.79
        self._last_pressure = 0.0
        self._weather_data = weather_data
        self._weather_data.register_observer(self)

    def update(
        self, temperature: float, humidity: float, pressure: float
    ) -> None:
        self._last_pressure = self._current_pressure
        self._current_pressure = pressure
        self.display()

    def display(self) -> None:
        print("Forecast:", end="")
        if self._current_pressure > self._last_pressure:
            print("Improving weather on the way!")
        elif self._current_pressure == self._last_pressure:
            print("More of the same")
        elif self._current_pressure < self._last_pressure:
            print("Watch out for cooler, rainy weather")


class HeatIndexDisplay:
    def __init__(self, weather_data: Subject):
        self._heat_index = 0.0
        self._weather_data = weather_data
        self._weather_data.register_observer(self)

    def update(
        self, temperature: float, humidity: float, pressure: float
    ) -> None:
        self._heat_index = self._compute_heat_index(temperature, humidity)
        self.display()

    def _compute_heat_index(self, t: float, rh: float) -> float:
        index = (
            16.923
            + (0.185212 * t)
            + (5.37941 * rh)
            - (0.100254 * t * rh)
            + (0.00941695 * (t * t))
            + (0.00728898 * (rh * rh))
            + (0.000345372 * (t * t * rh))
            - (0.000814971 * (t * rh * rh))
            + (0.0000102102 * (t * t * rh * rh))
            - (0.000038646 * (t * t * t))
            + (0.0000291583 * (rh * rh * rh))
            + (0.00000142721 * (t * t * t * rh))
            + (0.000000197483 * (t * rh * rh * rh))
            - (0.0000000218429 * (t * t * t * rh * rh))
            + (0.000000000843296 * (t * t * rh * rh * rh))
            - (0.0000000000481975 * (t * t * t * rh * rh * rh))
        )
        return index

    def display(self) -> None:
        print(f"Heat index is {self._heat_index:.5f}")


class StatisticsDisplay:
    def __init__(self, weather_data: Subject):
        self._max_temp = 0.0
        self._min_temp = 200
        self._temp_sum = 0.0
        self._num_readings = 0
        self._weather_data = weather_data
        self._weather_data.register_observer(self)

    def update(
        self, temperature: float, humidity: float, pressure: float
    ) -> None:
        self._temp_sum += temperature
        self._num_readings += 1

        if temperature > self._max_temp:
            self._max_temp = temperature

        if temperature < self._min_temp:
            self._min_temp = temperature

        self.display()

    def display(self) -> None:
        average = self._temp_sum / self._num_readings
        print(
            "Avg/Max/Min temperature = "
            f"{average:.1f}/{self._max_temp:.1f}/{self._min_temp:.1f}"
        )
