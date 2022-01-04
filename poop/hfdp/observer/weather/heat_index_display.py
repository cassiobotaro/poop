from poop.hfdp.observer.weather.subject import Subject


class HeatIndexDisplay:
    def __init__(self, weather_data: Subject):
        self._heat_index = 0.0
        self.__weather_data = weather_data
        self.__weather_data.register_observer(self)

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
