"""
Adapter — wrap an incompatible object in the interface you expect

A `FahrenheitSensor` only speaks Fahrenheit, but the rest of the
program asks every sensor for `.celsius()`. `CelsiusAdapter` holds the
legacy sensor and translates the one message, so the new code never
learns the old vocabulary.

Compare with the procedural Python version:

    reading = sensor.reading()
    if sensor.is_fahrenheit():
        reading = (reading - 32) * 5 / 9

POOP forbids that branch leaking into the caller. The adapter absorbs
the conversion; from the outside it is just another thing that
answers `.celsius()`.

Smalltalk:
    CelsiusAdapter>>celsius
        ^(sensor reading - 32) * 5 / 9
"""


class FahrenheitSensor:
    def reading(self):
        return 98.6


class CelsiusAdapter:
    def __init__(self, sensor):
        self._sensor = sensor

    def celsius(self):
        return (self._sensor.reading() - 32.0) * 5.0 / 9.0


# A sensor that already speaks Celsius — the interface the client wants.
class CelsiusSensor:
    def celsius(self):
        return 21.0


sensors = [CelsiusSensor(), CelsiusAdapter(FahrenheitSensor())]
sensors.do(lambda sensor: (sensor.celsius().repr() + "C").print())
