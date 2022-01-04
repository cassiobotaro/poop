from poop.hfdp.observer.weather_observable.current_conditions_display import (
    CurrentConditionsDisplay,
)
from poop.hfdp.observer.weather_observable.forecast_display import (
    ForecastDisplay,
)
from poop.hfdp.observer.weather_observable.heat_index_display import (
    HeatIndexDisplay,
)
from poop.hfdp.observer.weather_observable.statistics_display import (
    StatisticsDisplay,
)
from poop.hfdp.observer.weather_observable.weather_data import WeatherData


def main() -> None:
    weather_data = WeatherData()
    CurrentConditionsDisplay(weather_data)
    StatisticsDisplay(weather_data)
    ForecastDisplay(weather_data)
    HeatIndexDisplay(weather_data)

    weather_data.set_measurements(80, 65, 30.4)
    weather_data.set_measurements(82, 70, 29.2)
    weather_data.set_measurements(78, 90, 29.2)
