# 11. `__slots__` on every POOP class, mixins included

Date: 2026-04-22

## Status

Accepted

## Context

POOP types declare `__slots__` so that their instance variables are fixed. One slot-less class anywhere in an MRO restores the per-instance `__dict__` for everything below it, and the shared mixins `_ValueEqMixin`, `_IterableMixin` and `_SetAlgebraMixin` had none. The declaration was therefore defeated on 36 of the 49 POOP classes. `"abc".set_attr("x", 1)` succeeded, giving two equal `Str`s different attributes, while `(5).set_attr("x", 1)` refused. One message meant two things on two rungs of the same tower.

Closing it dropped a `Str` from 56 to 40 bytes, the same as an `Int`, and 100 000 of them from 14.2 MB to 9.4 MB.

## Decision

Every POOP type declares `__slots__`. Instance variables are declared in the class definition and fixed, never added dynamically to instances. Runtime method extension keeps working.

The shared mixins declare `__slots__ = ()` too. An empty `__slots__` on a mixin cannot collide with a concrete class's own, which is what makes it safe across all 36 classes.

Subclasses that need new instance variables can declare their own `__slots__` or omit them.

## Consequences

- `tests/test_slots.py` sweeps the whole MRO of every class, because the descriptor is installed on the first slot-less base and a per-mixin assertion would say nothing about the next mixin.
- `Object.set_attr` catches the refusal on a value and answers `str is a value — it holds no state of its own; only an object of a class you defined can be given one`. CPython's refusal named `__dict__`, a dunder `no_dunder_attribute` bans and `_reject_dunder` will not let a program spell.
- User classes are unaffected: `ClassTransformer` builds them without `__slots__`, so `self.count = 1` and `set_attr` keep working there.
