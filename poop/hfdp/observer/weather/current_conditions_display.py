from poop.hfdp.observer.weather.subject import Subject


class CurrentConditionsDisplay:
    def __init__(self, weather_data: Subject):
        self.__temperature = 0.0
        self.__humidity = 0.0
        self.__weather_data = weather_data
        self.__weather_data.register_observer(self)

    def update(
        self, temperature: float, humidity: float, pressure: float
    ) -> None:
        self.__temperature = temperature
        self.__humidity = humidity
        self.display()

    def display(self) -> None:
        print(
            f"Current conditions: {self.__temperature:.1f}F degrees "
            f"and {self.__humidity:.1f}% humidity"
        )
