# 48. `Range` stores an inclusive bound, decoded in one place, and reads its bounds by index

Date: 2026-08-09

## Status

Accepted

## Context

`Range` (`poop/types/range.py`) represents a closed integer interval. `_poop_range` subtracts one from the Python-spelled stop and `_range()` adds it back, which is an encoding, not a language feature; `__eq__` compares materialized ranges for that reason. `stop()` and `__str__` used to read the slot instead, so `range(3).stop()` answered `2` and `range(3)` printed as `range(0, 2)`, a spelling that, read back as POOP source, is a different sequence. `Slice`, handed its bound rather than encoding one, always answered the exclusive form, so the two disagreed about what a single selector means.

The converter in front of `Range.__init__` called `int(...)`, which truncates where an index refuses. `range(3.5)` answered `range(0, 3)` and `range(1, 10, 2.0)` a step of 2, silently running over a different sequence than the program describes. Non-numeric arguments leaked `int() argument must be a string, a bytes-like object or a real number`, naming a call for something spelt `range`. The converter then read `operator.index`, which kept CPython's `'float' object cannot be interpreted as an integer`; the `2026-10-15-fix-wrapper-equality-and-errors` change replaced it with the role-worded refusal every other integer argument uses.

Slicing wrapped the selected elements in a `List`, which allocated one `Int` per member of the result: `range(1000000000000).slice(0, 3)`, three elements in Python, materialized a trillion.

`Range` had only the `len` message, and `Object`'s default truthiness held: `range(0).not_()` answered `False` and `range(0).assert_("empty")` passed, where `[]`, `""`, `set()` and `b""` all refuse.

## Decision

`Range` keeps the inclusive encoding, and `_range()` is the one place it is undone.

- `stop()` and `__str__` report through `_range()`: `range(3).stop()` is `3` and `range(0, 4, 2)` prints as itself, as CPython does. `start()` and `step()` are answered from the slots, since neither is re-encoded.
- The converter (`poop/transformers/range.py`) reads each argument as an index through `an_int`, refused by its role: `#range's stop must be an int, got a float`, `#range's step must be an int, got a float`, `#range's stop must be an int, got a str`.
- A sliced `Range` is a `Range`, as `range(10)[1:3]` is `range(1, 3)` in CPython and as `reversed()` already answered. The exclusive stop is shifted back by `sign` to round-trip through the constructor's inclusive convention, the same encoding `reversed()` undoes.
- `__len__` and `__contains__` are wired, so an empty range is falsy and `includes` is membership. `__contains__` folds a `Boolean` as the three searches already do.

## Consequences

A printed range reads back as the same sequence, and slicing a range materializes none of its elements.

A float bound is refused instead of truncated. The boolean rung still passes, because admitting it is what an index is for: `range(True)` is `range(0, 1)`.

The stop slot holds the inclusive bound, which is how `stop()` and `__str__` once went wrong; only `_range()` decodes it.
