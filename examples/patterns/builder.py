"""
Builder — assemble a complex object step by step

A `PizzaBuilder` collects options through chained messages and only
materialises a `Pizza` when `build` is sent. Each configuring message
returns `self`, so the steps read as a fluent sentence and the
caller never juggles a constructor with a dozen positional arguments.

Compare with the procedural Python version:

    pizza = Pizza(
        size="large",
        toppings=["cheese", "mushroom"],
        thin_crust=True,
    )

POOP favours small messages over wide constructors. The builder holds
the half-built state; `build` freezes it into the finished product.

Smalltalk:
    PizzaBuilder>>size: aSize
        size := aSize. ^self

    PizzaBuilder>>add: aTopping
        toppings add: aTopping. ^self

    PizzaBuilder>>build
        ^Pizza size: size toppings: toppings
"""


class Pizza:
    def __init__(self, size, toppings):
        self._size = size
        self._toppings = toppings

    def describe(self):
        return self._size + " pizza with " + ", ".join(self._toppings)


class PizzaBuilder:
    def __init__(self):
        self._size = "medium"
        self._toppings = []

    def size(self, size):
        self._size = size
        return self

    def add(self, topping):
        self._toppings.append(topping)
        return self

    def build(self):
        return Pizza(self._size, self._toppings)


pizza = PizzaBuilder().size("large").add("cheese").add("mushroom").add("olive").build()
pizza.describe().print()

# A plain builder keeps its defaults
PizzaBuilder().add("cheese").build().describe().print()
