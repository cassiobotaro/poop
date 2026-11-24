# 63. Built exceptions have a POOP instance side

Date: 2026-10-15

## Status

Accepted

## Context

An exception a program builds, `ValueError("x")` or an instance of its own `class Field(Exception)`, descended from `Object` and answered none of what a *caught* `Error` answers. `message()` and `kind()` were refused, and `raise_()` was refused as a class-side message, so a pre-built exception could not be raised at all; only `Kind.raise_(...)` could. `print()` wrote the bare message where an `Error` writes `ValueError: x`.

Meanwhile `args`, `add_note` and `with_traceback` resolved through `BaseException` and answered natives (`'tuple' object has no attribute 'print'`). The refusals in `_PYTHON_ATTRIBUTES` were installed on the metaclass, which instance lookup never consults.

The `2026-10-15-close-raw-python-leaks` change considered making the mirror constructor answer an `Error`. It was rejected because `class Field(Exception)` then could not store fields on `self`. `Error` keeps wrapping a *caught* exception, and a program never holds an `Error` it built, so the two surfaces do not collide.

## Decision

The root mirror carries an instance side, added in `exceptions._build` (`poop/types/exceptions.py`): `message`, `kind`, `raise_`, `print` and `__repr__`. It refuses the three natives `args`, `add_note` and `with_traceback` on the instance with the class side's own sentences, so `dir()` stops advertising them.

`__str__` is deliberately left as the bare message. It is what `poop_message` reads, what CPython's traceback prints, and what a program's own `__str__` override replaces. A sequence's `print`, which writes `str` of each element, therefore shows the message, while `repr` and the object's own `print` show the described form through `exceptions.describe`, the one composition the executor's uncaught report uses too.

## Consequences

A built exception answers like a caught one and can be raised by sending it `raise_()`. The described form has one composition, shared by the instance side and the uncaught report.
