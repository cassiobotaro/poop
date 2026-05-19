"""
Discount Strategies — polymorphism replacing `if kind == ...`

Three discount shapes — NoDiscount, PercentDiscount, FixedDiscount —
all respond to `apply(price)`. The cart loops over them with no
knowledge of which one is plugged in.

Compare with the procedural Python version:

    if d.kind == "percent":
        return price * (1 - d.rate)
    elif d.kind == "fixed":
        return price - d.amount
    else:
        return price

POOP forbids that branching shape. Each strategy is its own type and
owns its formula.

Smalltalk:
    Object subclass: #NoDiscount.
    NoDiscount>>applyTo: price
        ^price

    Object subclass: #PercentDiscount
        instanceVariableNames: 'rate'.
    PercentDiscount>>applyTo: price
        ^price * (1.0 - rate)

    Object subclass: #FixedDiscount
        instanceVariableNames: 'amount'.
    FixedDiscount>>applyTo: price
        ^price - amount
"""


class NoDiscount:
    def label(self):
        return "no discount"

    def apply(self, price):
        return price


class PercentDiscount:
    def __init__(self, rate):
        self._rate = rate

    def label(self):
        return "percent " + self._rate.repr()

    def apply(self, price):
        return price * (1.0 - self._rate)


class FixedDiscount:
    def __init__(self, amount):
        self._amount = amount

    def label(self):
        return "fixed " + self._amount.repr()

    def apply(self, price):
        return price - self._amount


price = 100.0

[
    NoDiscount(),
    PercentDiscount(0.2),
    FixedDiscount(15.0),
    PercentDiscount(0.5),
].do(lambda d: (d.label() + ": " + d.apply(price).repr()).print())
