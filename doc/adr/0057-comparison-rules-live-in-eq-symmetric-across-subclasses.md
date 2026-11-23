# 57. Comparison rules live in `__eq__`, symmetric across subclasses

Date: 2026-10-04

## Status

Accepted

## Context

A POOP `==` answers a `Boolean`, so Python's derived `__ne__`, which answers a raw `bool`, cannot be used. The eleven wrappers had each restated their comparison rule in their own `__ne__` with the answer flipped, keeping two copies of each rule in step by hand.

Equality between a wrapper and a subclass of it was also wrong. `_ValueEqMixin._eq_comparable` asked `isinstance(other, type(self))`, and CPython calls the *right* operand's `__eq__` first when its class is a subclass of the left's. A program's `class Name(str)` compared against a `Str` therefore ran the subclass's test with the base on the other side and answered `false`, which is not `NotImplemented` and so was final. `Name("a") == "a"` was `False` in both orders while the two hashed alike: `{Name("a"): 1}.at("a")` was a `KeyError` where CPython answers `1`. The numeric tower was never affected, since it compares through `_NumericCompareMixin`'s own fold.

The `2026-10-15-fix-wrapper-equality-and-errors` change considered comparing against the class that *declares* `_eq_attr` (walking the MRO). It is correct too, but a longer read for the same answer.

## Decision

`__ne__` is written once, on `Object` (`poop/types/object.py`): it negates whatever `==` answers. `PoopMeta.__ne__` is the one other, for classes. Every comparison rule lives in its class's `__eq__` alone.

Value equality is symmetric across a subclass, as `str.__eq__` is: `_eq_comparable` answers `True` when either operand is an instance of the other's class, then falls through to the group test. `Name("a") == "a"` and `"a" == Name("a")` are both `True`, and a dict keyed by one is found by the other. Hash is already by value on every class that defines `_eq_attr`.

## Consequences

A rule changed in `__eq__` cannot disagree with its `!=`, because there is no second copy.

Two unrelated subclasses of `str`, `Name("a")` and `Name2("a")`, are equal. CPython agrees, since `str.__eq__` compares values, and the group test already made `set == frozenset` true by value.
