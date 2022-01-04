from poop.hfdp.observer.util import Observable


class WeatherData(Observable):
    def __init__(self) -> None:
        super().__init__()
        self.__temperature: float = 0.0
        self.__humidity: float = 0.0
        self.__pressure: float = 0.0

    def measurements_changed(self) -> None:
        self.set_changed()
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
