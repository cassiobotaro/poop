# 47. `Boolean` stays outside `Int` and answers the int side

Date: 2026-08-09

## Status

Accepted

## Context

In CPython `bool` is an `int` subclass, and POOP's numeric comparisons include `Boolean` in the tower for that reason (`True == 1` is `true`). POOP keeps `Boolean` out of `Int`'s subtree deliberately (`_index.py`: "the two rungs of the tower are separate classes"). Everything that makes `bool` an `int` in CPython is therefore re-supplied by hand on `Boolean`: arithmetic, reflected arithmetic, comparison, `__index__`.

The messages were not re-supplied at first. `True.abs()`, `True.divmod(2)`, `True.pow(2)`, `True.round()`, `True.bin()` and the rest answered `bool does not understand #…`, while `no_abs`, `no_divmod`, `no_pow`, `no_round` and `no_bin` each named exactly those as the substitute. Two members were missing beyond that. `__lshift__`/`__rshift__` and their reflected twins were never written, because a shift has no boolean-algebra reading, unlike `&`, `|` and `^`: `True << True` answered `bool does not understand #<<` while both mixed spellings worked, `Int` covering them from its own side with a comment naming this hole. `from_bytes` was the one half-pair in the message family, and the near-miss hint pointed the reader at `#to_bytes`, the message they had not asked for.

Python 3.15 deprecates `~True` for removal in 3.16: "this returns the bitwise inversion of the underlying int object and is usually not what you expect from negating a bool". Delegating `bit_invert` to the int answered `-2` in silence, and would have kept answering it after CPython stopped. POOP has no warnings channel.

Two separate classes also made the class side disagree with itself. `Object.class_` answers `type(self)`, which for the singletons is `_TrueClass` or `_FalseClass`: two classes both called `bool`, neither equal to the bare name, with a second `bool` rung on the ladder above each, so `True.class_() == bool` was `False`. `xor` and `eqv`, the two messages on the receiver that take a value rather than a block, guarded nothing: `False.xor(5)` answered `5` and `True.eqv("abc")` answered `abc`. Folding the argument through truthiness was considered and rejected: it would accept in silence what `and_`/`or_` refuse. These two came with the `2026-10-15-fix-wrapper-equality-and-errors` change.

## Decision

`Boolean` (`poop/types/boolean.py`) stays a separate class beside `Int`, not under it, and answers the int side by delegation.

- The int-side messages delegate through `_as_int()`, the same fold the arithmetic uses, and each answers an `Int` as CPython does (`abs(True)` is `1`, not `True`).
- `min`/`max` are an exception: they answer one of their operands, and `min(True, 5)` is `True` in CPython, so they route through `_minmax` over `(self, *others)` as `Int` does.
- The shifts and their reflected twins fold to `Int` whatever the operand is, as CPython does.
- `from_bytes` answers a `Boolean`, against the family's rule, because CPython builds this one through `cls` (`bool.from_bytes(b"\x05", "big")` is `True`).
- `bit_invert` is refused, carrying the deprecation warning's two alternatives through the hint table in `_selectors.py`: `bool does not understand #bit_invert — did you mean #not_? the bitwise inversion is the int's — send #bit_invert to int(flag)`.
- `Boolean.class_` answers `Boolean`, cloaked as `bool`, whose `superclass()` is `object`. `Boolean()` answers `false` as `bool()` does, so `True.class_()()` stays consistent with CPython's `type(True)()`.
- `xor` and `eqv` take a `Boolean` through `a_boolean`, which refuses in the `a_block` shape: `#xor expects a bool, got an int`.

## Consequences

The rest of the int side stays, because CPython keeps it. Answering a `Boolean` from an int-side message would be a quiet type error, so only `min`, `max` and `from_bytes` answer one.

Every member that makes `bool` an `int` has to be written on `Boolean` by hand; the shifts and `from_bytes` were two that had been missed.

The `bit_invert` refusal lands before CPython's removal, since POOP cannot warn.

`is_instance` and `is_subclass` are unaffected by `Boolean.class_`.
