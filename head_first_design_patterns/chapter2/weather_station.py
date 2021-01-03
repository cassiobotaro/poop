"""
OO Basics

- Abstraction
- Encapsulation
- Polymorphism
- Inheritance

OO Principles

- Encapsulate what varies.
- Favor composition over inheritance
- Program to interfaces, not implementations
- Strive for loosely coupled design between objects that interact

OO Patterns

Strategy - defines a family of algorithms, encapsulates each one,
and makes them interchangeable.
Strategy lets the algorithm vary independently from clients that use it.

Observer - defines a one-to-many dependency between objects
so that when one object changes state, all its dependents are
notified and updated automatically.
"""
from weather_data import WeatherData
from display import (
    CurrentConditionsDisplay,
    StatisticsDisplay,
    ForecastDisplay,
    HeatIndexDisplay,
)


"""
Notes:
- All instantied displays register on subject(topic).
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
