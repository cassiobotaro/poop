from poop.hfdp.observer.weather.observer import Observer


class WeatherData:
    def __init__(self) -> None:
        self.__observers: list[Observer] = []
        # abstracts states that when modified
        # will notify their subscribers
        self.__temperature: float = 0.0
        self.__humidity: float = 0.0
        self.__pressure: float = 0.0

    def register_observer(self, observer: Observer) -> None:
        self.__observers.append(observer)

    def remove_observer(self, observer: Observer) -> None:
        self.__observers.remove(observer)

    def notify_observers(self) -> None:
        for observer in self.__observers:
            observer.update(
                self.__temperature, self.__humidity, self.__pressure
            )

    def measurements_changed(self) -> None:
        self.notify_observers()

    def set_measurements(
        self, temperature: float, humidity: float, pressure: float
    ) -> None:
        self.__temperature = temperature
        self.__humidity = humidity
        self.__pressure = pressure
        self.measurements_changed()

    def get_temperature(self) -> float:
        return self.__temperature

    def get_humidity(self) -> float:
        return self.__humidity

    def get_pressure(self) -> float:
        return self.__pressure
