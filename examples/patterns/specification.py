"""
Specification — business rules as objects you can combine

Each rule (`InStock`, `CheaperThan`, `Featured`) answers
`is_satisfied_by(product)`. Rules combine through `and_` / `or_` /
`not_`, which build composite specifications — so a complex predicate
is assembled from small, named, reusable pieces instead of a tangled
boolean expression.

Compare with the procedural Python version:

    if product.in_stock and (product.price < 50 or product.featured):
        ...

POOP forbids `and`, `or`, and `not` as operators (`no_and_or`,
`no_not`). That ban is exactly what this pattern thrives on: boolean
logic becomes a tree of objects, and each leaf rule can be tested,
named, and reused on its own.

Smalltalk:
    AndSpecification>>isSatisfiedBy: candidate
        ^(left isSatisfiedBy: candidate)
            and: [right isSatisfiedBy: candidate]

    Specification>>and: aSpec ^AndSpecification left: self right: aSpec
"""


class Specification:
    def and_(self, other):
        return AndSpecification(self, other)

    def or_(self, other):
        return OrSpecification(self, other)

    def not_(self):
        return NotSpecification(self)


class InStock(Specification):
    def is_satisfied_by(self, product):
        return product.in_stock()


class CheaperThan(Specification):
    def __init__(self, limit):
        self._limit = limit

    def is_satisfied_by(self, product):
        return product.price() < self._limit


class Featured(Specification):
    def is_satisfied_by(self, product):
        return product.featured()


class AndSpecification(Specification):
    def __init__(self, left, right):
        self._left = left
        self._right = right

    def is_satisfied_by(self, product):
        return self._left.is_satisfied_by(product).and_(
            lambda: self._right.is_satisfied_by(product)
        )


class OrSpecification(Specification):
    def __init__(self, left, right):
        self._left = left
        self._right = right

    def is_satisfied_by(self, product):
        return self._left.is_satisfied_by(product).or_(
            lambda: self._right.is_satisfied_by(product)
        )


class NotSpecification(Specification):
    def __init__(self, spec):
        self._spec = spec

    def is_satisfied_by(self, product):
        return self._spec.is_satisfied_by(product).not_()


class Product:
    def __init__(self, name, price, in_stock, featured):
        self._name = name
        self._price = price
        self._in_stock = in_stock
        self._featured = featured

    def name(self):
        return self._name

    def price(self):
        return self._price

    def in_stock(self):
        return self._in_stock

    def featured(self):
        return self._featured


products = [
    Product("Mouse", 25, True, False),
    Product("Keyboard", 80, True, True),
    Product("Monitor", 300, False, True),
    Product("Cable", 10, True, False),
]

# in stock AND (cheaper than 50 OR featured)
wanted = InStock().and_(CheaperThan(50).or_(Featured()))

products.filter(lambda product: wanted.is_satisfied_by(product)).do(
    lambda product: (product.name() + " ✓").print()
)
