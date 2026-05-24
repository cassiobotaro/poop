"""
Money — a value object instead of a bare number

Money is an amount *and* a currency, kept together. It stores whole
cents as an `Int` (never a drifting `float`), answers arithmetic as
messages, refuses to add two different currencies, and can `allocate`
itself across shares without losing a cent — Fowler's classic remedy
for "10.00 / 3" rounding bugs.

Compare with the procedural Python version, where the amount is a
loose float and the currency lives somewhere else:

    total = 10.00 + 5.50          # float, may drift
    if currency_a != currency_b:  # check scattered across the code
        raise ValueError(...)

POOP keeps the rule inside the object: every `plus` re-checks the
currency, so the invariant can never be forgotten at a call site.

Smalltalk:
    Money>>+ aMoney
        self assertSameCurrency: aMoney.
        ^Money cents: cents + aMoney cents currency: currency

    Money>>allocate: n
        | base remainder |
        base := cents // n. remainder := cents \\ n.
        ^(0 to: n - 1) collect: [:i |
            Money cents: (i < remainder ifTrue: [base + 1] ifFalse: [base])
                  currency: currency]
"""


class Money:
    def __init__(self, cents, currency):
        self._cents = cents
        self._currency = currency

    def cents(self):
        return self._cents

    def currency(self):
        return self._currency

    def plus(self, other):
        self._assert_same(other)
        return Money(self._cents + other.cents(), self._currency)

    def times(self, factor):
        return Money(self._cents * factor, self._currency)

    def allocate(self, parts):
        base = self._cents // parts
        remainder = self._cents % parts
        return list(
            range(0, parts).map(
                lambda i: Money(
                    (i < remainder).if_true_if_false(lambda: base + 1, lambda: base),
                    self._currency,
                )
            )
        )

    def describe(self):
        major = self._cents // 100
        minor = self._cents % 100
        padded = (minor < 10).if_true_if_false(
            lambda: "0" + minor.repr(), lambda: minor.repr()
        )
        return self._currency + " " + major.repr() + "." + padded

    def _assert_same(self, other):
        (self._currency == other.currency()).if_false(
            lambda: ValueError.raise_(
                "cannot mix " + self._currency + " and " + other.currency()
            )
        )


ten = Money(1000, "BRL")
five_fifty = Money(550, "BRL")

ten.plus(five_fifty).describe().print()  # BRL 15.50
ten.times(3).describe().print()  # BRL 30.00

# Split 10.00 across 3 shares — every cent is accounted for.
Money(1000, "BRL").allocate(3).do(lambda share: share.describe().print())

# Adding different currencies is refused, not silently wrong.
Try(lambda: ten.plus(Money(100, "USD"))).except_(
    ValueError,
    lambda e: ("refused: " + e.message()).print(),
).run()
