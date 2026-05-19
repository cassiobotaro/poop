"""
Observer — polymorphism + `.do` replacing event-loop boilerplate

A Thermometer broadcasts each reading to its observers. Display
prints, Alarm fires when a threshold is crossed, History accumulates.
The subject never asks "what kind of observer is this?" — it just
sends `.update(reading)` and lets each receiver decide.

Compare with the procedural Python version:

    for observer in subject.observers:
        if isinstance(observer, Alarm):
            if reading > observer.threshold:
                observer.fire()
        elif isinstance(observer, Display):
            print(reading)
        ...

POOP forbids both `for` and `isinstance`. Subscribers live in a
`List` that the subject walks with `.do(...)`; each one decides how
to react when it receives `.update(...)`.

Smalltalk:
    Object subclass: #Thermometer
        instanceVariableNames: 'observers'.
    Thermometer>>attach: observer
        observers add: observer

    Thermometer>>read: reading
        observers do: [:o | o update: reading]

    Object subclass: #Alarm
        instanceVariableNames: 'threshold'.
    Alarm>>update: reading
        reading > threshold ifTrue: [Transcript show: 'ALARM']
"""


class Thermometer:
    def __init__(self):
        self._observers = []

    def attach(self, observer):
        self._observers.append(observer)

    def detach(self, observer):
        self._observers.remove(observer)

    def read(self, reading):
        self._observers.do(lambda o: o.update(reading))


class Display:
    def update(self, reading):
        ("display: " + reading.repr() + "C").print()


class Alarm:
    def __init__(self, threshold):
        self._threshold = threshold

    def update(self, reading):
        (reading > self._threshold).if_true(
            lambda: ("ALARM at " + reading.repr() + "C").print()
        )


class History:
    def __init__(self):
        self._readings = []

    def update(self, reading):
        self._readings.append(reading)

    def readings(self):
        return self._readings


thermometer = Thermometer()
display = Display()
alarm = Alarm(30)
history = History()

thermometer.attach(display)
thermometer.attach(alarm)
thermometer.attach(history)

thermometer.read(22)
thermometer.read(28)
thermometer.read(35)

("history: " + history.readings().repr()).print()

thermometer.detach(alarm)
thermometer.read(40)
("after detach, history: " + history.readings().repr()).print()
