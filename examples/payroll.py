"""
Payroll — polymorphism replacing `if employee.type == ...`

Three pay models — Salaried, Hourly, Commission — share `pay()`. The
canonical "replace conditional with polymorphism" example from
Fowler's *Refactoring*.

Compare with the procedural Python version:

    def pay(e):
        if e.kind == "salaried":
            return e.salary
        elif e.kind == "hourly":
            return e.rate * e.hours
        elif e.kind == "commission":
            return e.base + e.rate * e.sales

POOP forbids that branching shape. Each role is its own class and
computes its own pay.

Smalltalk:
    Object subclass: #Salaried
        instanceVariableNames: 'name salary'.
    Salaried>>pay
        ^salary

    Object subclass: #Hourly
        instanceVariableNames: 'name rate hours'.
    Hourly>>pay
        ^rate * hours

    Object subclass: #Commission
        instanceVariableNames: 'name base rate sales'.
    Commission>>pay
        ^base + (rate * sales)
"""


class Salaried:
    def __init__(self, name, salary):
        self._name = name
        self._salary = salary

    def name(self):
        return self._name

    def pay(self):
        return self._salary


class Hourly:
    def __init__(self, name, rate, hours):
        self._name = name
        self._rate = rate
        self._hours = hours

    def name(self):
        return self._name

    def pay(self):
        return self._rate * self._hours


class Commission:
    def __init__(self, name, base, rate, sales):
        self._name = name
        self._base = base
        self._rate = rate
        self._sales = sales

    def name(self):
        return self._name

    def pay(self):
        return self._base + self._rate * self._sales


employees = [
    Salaried("Alice", 5000.0),
    Hourly("Bob", 30.0, 160.0),
    Commission("Carol", 2000.0, 0.05, 50000.0),
]

employees.do(lambda e: (e.name() + ": " + e.pay().repr()).print())
