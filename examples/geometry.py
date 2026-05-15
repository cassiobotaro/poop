"""
Geometry primer

Demonstrates the Math namespace — the POOP equivalent of Python's
math module — by computing triangle and circle properties.

Smalltalk:
    | hyp area circ angle1 angle2 |
    hyp := (3 squared + 4 squared) sqrt.
    area := Float pi * 5 squared.
    circ := 2 * Float pi * 5.
    angle1 := 30 degreesToRadians sin.
    angle2 := 60 degreesToRadians cos.

    Transcript showCr: 'Hypotenuse 3-4: ' , hyp printString.
    Transcript showCr: 'Area r=5:       ' , area printString.
    Transcript showCr: 'Circumference:  ' , circ printString.
    Transcript showCr: 'sin 30 = 0.5:   ' , (angle1 closeTo: 0.5) printString.
    Transcript showCr: 'cos 60 = 0.5:   ' , (angle2 closeTo: 0.5) printString.
"""


class Geometry:
    def _label(self, text, value):
        (text + value.repr()).print()

    def hypotenuse(self, a, b):
        return Math.hypot(a, b)

    def circle_area(self, radius):
        return Math.PI * radius * radius

    def circle_circumference(self, radius):
        return 2.0 * Math.PI * radius

    def run(self):
        self._label("Hypotenuse 3-4: ", self.hypotenuse(3.0, 4.0))
        self._label("Area r=5:       ", self.circle_area(5.0))
        self._label("Circumference:  ", self.circle_circumference(5.0))

        sin30 = Math.sin(Math.radians(30.0))
        cos60 = Math.cos(Math.radians(60.0))
        self._label("sin 30 ≈ 0.5:   ", Math.isclose(sin30, 0.5))
        self._label("cos 60 ≈ 0.5:   ", Math.isclose(cos60, 0.5))

        self._label("sqrt(2):        ", Math.sqrt(2.0))
        self._label("5! = 120:       ", Math.factorial(5))
        self._label("gcd(12, 18):    ", Math.gcd(12, 18))


Geometry().run()
