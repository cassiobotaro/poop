from poop.hfdp.observer.weather.current_conditions_display import (
    CurrentConditionsDisplay,
)
from poop.hfdp.observer.weather.forecast_display import ForecastDisplay
from poop.hfdp.observer.weather.statistics_display import StatisticsDisplay
from poop.hfdp.observer.weather.weather_data import WeatherData


def main() -> None:
    weather_data = WeatherData()

    CurrentConditionsDisplay(weather_data)
    StatisticsDisplay(weather_data)
    forecast_display = ForecastDisplay(weather_data)

    weather_data.set_measurements(80, 65, 30.4)
    weather_data.set_measurements(82, 70, 29.2)
    weather_data.set_measurements(78, 90, 29.2)

    weather_data.remove_observer(forecast_display)
    weather_data.set_measurements(62.0, 90.0, 28.1)
