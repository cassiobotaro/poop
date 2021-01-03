from interface import Subject

"""
Notes:
- Setter is used to notify that changes have occurred
- Fields temperature, humidity, pressure are "private".
This means that we are preventing the alteration of any of
them without notification from their observers
- I have doubts about the presence of getters methods in this class.
- WheaterData represents a topic to subcribe containing
states that change.
"""


class WeatherData(Subject):
    def __init__(self):
        self.observers = []
        # abstracts states that when modified
        # will notify their subscribers
        self._temperature = 0.0
        self._humidity = 0.0
        self._pressure = 0.0

    def register_observer(self, observer):
        self.observers.append(observer)

    def remove_observer(self, observer):
        self.observers.remove(observer)

    def notify_observers(self):
        for observer in self.observers:
            observer.update(self._temperature, self._humidity, self._pressure)

    def measurements_changed(self):
        self.notify_observers()

    def set_measurements(self, temperature, humidity, pressure):
        self._temperature = temperature
        self._humidity = humidity
        self._pressure = pressure
        self.measurements_changed()

    def get_temperature(self):
        return self._temperature

    def get_humidity(self):
        return self._humidity

    def get_pressure(self):
        return self._pressure
