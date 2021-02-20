from display import (
    CurrentConditionsDisplay,
    ForecastDisplay,
    HeatIndexDisplay,
    StatisticsDisplay,
)
from weather_data import WeatherData

"""
Notes:
- All instantied displays are registred in a subject(topic).
- When the states changes(set_measurements), all display are notified.
- We can register and unregister a observer as
we can see in the last two lines.
"""
weather_data = WeatherData()
current_Display = CurrentConditionsDisplay(weather_data)
statistics_display = StatisticsDisplay(weather_data)
forecast_display = ForecastDisplay(weather_data)
heat_index_display = HeatIndexDisplay(weather_data)

weather_data.set_measurements(80, 65, 30.4)
weather_data.set_measurements(82, 70, 29.2)
weather_data.set_measurements(78, 90, 29.2)

weather_data.remove_observer(forecast_display)
weather_data.set_measurements(62.0, 90.0, 28.1)
