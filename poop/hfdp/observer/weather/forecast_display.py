from poop.hfdp.observer.weather.subject import Subject


class ForecastDisplay:
    def __init__(self, weather_data: Subject):
        self.__current_pressure = 29.79
        self.__last_pressure = 0.0
        self.__weather_data = weather_data
        self.__weather_data.register_observer(self)

    def update(
        self, temperature: float, humidity: float, pressure: float
    ) -> None:
        self.__last_pressure = self.__current_pressure
        self.__current_pressure = pressure
        self.display()

    def display(self) -> None:
        print("Forecast:", end="")
        if self.__current_pressure > self.__last_pressure:
            print("Improving weather on the way!")
        elif self.__current_pressure == self.__last_pressure:
            print("More of the same")
        elif self.__current_pressure < self.__last_pressure:
            print("Watch out for cooler, rainy weather")
