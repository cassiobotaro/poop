# Lesson 6 — Errors

**Goal:** raise and handle exceptions without `try`, `except`, or
`raise` statements.

## What's new

POOP forbids the `try` and `raise` statements. Their replacements are
fluent builders made of method calls.

**Raise** — every exception class gains a `raise_(message)` method:

```python
ValueError.raise_("Insufficient funds")
```

That's exactly equivalent to `raise ValueError("Insufficient funds")`.

**Catch** — wrap the protected code in a `lambda`, hand it to `Try`,
register a handler with `except_(ExcType, handler)`, and call `.run()`
to actually execute everything:

```python
Try(lambda: risky_operation()).except_(
    ValueError,
    lambda e: ("Got error: " + e.message()).print(),
).run()
```

The handler receives an `Error` object that exposes `e.kind()` (the
exception class name) and `e.message()` (the string the exception was
raised with).

The lambdas defer evaluation: nothing runs until `.run()` ties the
knot. Chain `except_` calls to handle multiple exception types.

## Walk-through

A bank account that refuses overdrafts.

Save to `bank.py`:

```python
class BankAccount:
    def __init__(self):
        self._balance = 0

    def deposit(self, amount):
        self._balance = self._balance + amount
        return self

    def withdraw(self, amount):
        (self._balance >= amount).if_false(
            lambda: ValueError.raise_("Insufficient funds")
        )
        self._balance = self._balance - amount
        return self

    def balance(self):
        return self._balance


account = BankAccount()
account.deposit(100)

Try(lambda: account.withdraw(150)).except_(
    ValueError,
    lambda e: ("Error [" + e.kind() + "]: " + e.message()).print(),
).run()

account.balance().print()   # 100 — withdrawal was rejected

account.deposit(200)
account.withdraw(50)
account.balance().print()   # 250
```

Two pieces worth pausing on:

- `(self._balance >= amount).if_false(lambda: ValueError.raise_(...))`
  is the POOP version of an early `raise`. The lambda holds the
  `raise_` call so it only runs on the false branch.
- `deposit` and `withdraw` end with `return self`. That lets you chain
  `account.deposit(100).withdraw(50)` if you want — a common POOP
  pattern lifted from Smalltalk's "cascades".

## Try it

Add a `transfer(self, other, amount)` method to `BankAccount` that
withdraws from `self` and deposits into `other`. If `self` doesn't
have enough money, no money should move and the caller should see the
`ValueError`. Test it with two accounts where the source is too poor.

## Anchor example

[`examples/bank_account.py`](https://github.com/cassiobotaro/poop/blob/main/examples/bank_account.py) — the program above, runnable.

## Capstone

You now know enough POOP to read
[`examples/rpn_calculator.py`](https://github.com/cassiobotaro/poop/blob/main/examples/rpn_calculator.py) — a Reverse-Polish-Notation calculator that uses a class, a `dict` of operator lambdas, list manipulation, and string parsing. It's roughly 25 lines and pulls together every lesson in this tutorial.

## Reference

- [Python vs POOP — Builtins → try/except](../python-vs-poop/builtins.md) for the full `Try` / `With` reference.
- [`Error`](https://github.com/cassiobotaro/poop/blob/main/poop/types/error.py) — what the exception handler actually receives.
