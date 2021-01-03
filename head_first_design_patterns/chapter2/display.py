from interface import DisplayElement, Observer


class CurrentConditionsDisplay(DisplayElement, Observer):
    def __init__(self, weather_data):
        self._temperature = 0.0
        self._humidity = 0.0
        self._weather_data = weather_data
        self._weather_data.register_observer(self)

    def update(self, temperature, humidity, pressure):
        self._temperature = temperature
        self._humidity = humidity
        self.display()

    def display(self):
        print(
            f"Current conditions: {self._temperature:.1f}F degrees "
            f"and {self._humidity:.1f}% humidity"
        )


class ForecastDisplay(DisplayElement, Observer):
    def __init__(self, weather_data):
        self._current_pressure = 29.79
        self._last_pressure = 0.0
        self._weather_data = weather_data
        self._weather_data.register_observer(self)

    def update(self, temperature, humidity, pressure):
        self._last_pressure = self._current_pressure
        self._current_pressure = pressure
        self.display()

    def display(self):
        print("Forecast:", end="")
        if self._current_pressure > self._last_pressure:
            print("Improving weather on the way!")
        elif self._current_pressure == self._last_pressure:
            print("More of the same")
        elif self._current_pressure < self._last_pressure:
            print("Watch out for cooler, rainy weather")


class HeatIndexDisplay(DisplayElement, Observer):
    def __init__(self, weather_data):
        self._heat_index = 0.0
        self._weather_data = weather_data
        self._weather_data.register_observer(self)

    def update(self, temperature, humidity, pressure):
        self._heat_index = self._compute_heat_index(temperature, humidity)
        self.display()

    def _compute_heat_index(self, t, rh):
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

    def display(self):
        print(f"Heat index is {self._heat_index:.5f}")


class StatisticsDisplay(DisplayElement, Observer):
    def __init__(self, weather_data):
        self._max_temp = 0.0
        self._min_temp = 200
        self._temp_sum = 0.0
        self._num_readings = 0
        self._weather_data = weather_data
        self._weather_data.register_observer(self)

    def update(self, temperature, humidity, pressure):
        self._temp_sum += temperature
        self._num_readings += 1

        if temperature > self._max_temp:
            self._max_temp = temperature

        if temperature < self._min_temp:
            self._min_temp = temperature

        self.display()

    def display(self):
        average = self._temp_sum / self._num_readings
        print(
            "Avg/Max/Min temperature = "
            f"{average:.1f}/{self._max_temp:.1f}/{self._min_temp:.1f}"
        )
