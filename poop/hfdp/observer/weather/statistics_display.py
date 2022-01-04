from poop.hfdp.observer.weather.subject import Subject


class StatisticsDisplay:
    def __init__(self, weather_data: Subject):
        self.__max_temp = 0.0
        self.__min_temp = 200.0
        self.__temp_sum = 0.0
        self.__num_readings = 0
        self.__weather_data = weather_data
        self.__weather_data.register_observer(self)

    def update(
        self, temperature: float, humidity: float, pressure: float
    ) -> None:
        self.__temp_sum += temperature
        self.__num_readings += 1

        if temperature > self.__max_temp:
            self.__max_temp = temperature

        if temperature < self.__min_temp:
            self.__min_temp = temperature

        self.display()

    def display(self) -> None:
        average = self.__temp_sum / self.__num_readings
        print(
            "Avg/Max/Min temperature = "
            f"{average:.1f}/{self.__max_temp:.1f}/{self.__min_temp:.1f}"
        )
