"""
Null Object — polymorphism replacing `if obj is None`

A NullCustomer answers the same messages a real Customer does, but
with sensible defaults (guest greeting, no discount, free plan).
Callers iterate a mixed list of logged-in and anonymous users without
a single None-check.

Compare with the procedural Python version:

    if customer is None:
        greeting = "Welcome, guest"
    else:
        greeting = "Welcome back, " + customer.name

POOP forbids `is None` against types meant for polymorphism — every
"absent" customer is itself a Customer-shaped object.

Smalltalk:
    Object subclass: #Customer
        instanceVariableNames: 'name plan'.

    Customer>>greeting
        ^'Welcome back, ', name

    Customer>>plan
        ^plan

    Object subclass: #NullCustomer.

    NullCustomer>>greeting
        ^'Welcome, guest'

    NullCustomer>>plan
        ^'free'
"""


class Customer:
    def __init__(self, name, plan):
        self._name = name
        self._plan = plan

    def greeting(self):
        return "Welcome back, " + self._name

    def plan(self):
        return self._plan


class NullCustomer:
    def greeting(self):
        return "Welcome, guest"

    def plan(self):
        return "free"


visitors = [
    Customer("Alice", "premium"),
    NullCustomer(),
    Customer("Bob", "basic"),
    NullCustomer(),
]

visitors.do(lambda c: (c.greeting() + " (" + c.plan() + ")").print())
