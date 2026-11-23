# 42. Sets and views copy CPython's method/operator asymmetry

Date: 2026-07-25

## Status

Accepted

## Context

CPython draws a line between the two ways of combining sets. The set methods (`union`, `intersection`, `difference`, `symmetric_difference`, `isdisjoint`, `issubset`, `issuperset` and the in-place updates) accept any iterable, while the operators (`|`, `&`, `-`, `^`, `<`, `<=`, `>`, `>=`) require two set-likes: `{1} | [2]` is a `TypeError`. The dict views split differently: the set-like views accept any iterable for `|`, `&`, `-`, `^` and for `isdisjoint` (`{"a": 1}.keys() | ["a", "c"]` is valid) but require a set-like on the right of `<= < >= >` (`dict_keys <= list` is a `TypeError`).

POOP's views had diverged from both halves. The older code read `other._data`, so `{"a": 1}.keys() | [2]` answered `list does not understand #_data` and rejected a valid program, and `{"a": 1}.keys() | 5` answered CPython's `'int' object is not iterable` through `set(5)`. The view base class also refused hashing for all three views, while CPython puts `d.values()` in a set.

Reusing `_SetAlgebraMixin`'s `_set_like` marker for the views was considered and rejected: claiming a view there would make `frozenset({1}) | {2: 3}.keys()` answer a frozenset, where CPython answers a set through the view's reflected operator.

## Decision

POOP copies CPython's asymmetry on both families.

- On `Set` and `FrozenSet`, the methods take any iterable and the operators require two set-likes. A non-iterable operand passed to a method raises the `TypeError` CPython would.
- On `dict_keys` and `dict_items`, both halves are written once on `_SetLikeView` (`poop/types/_dict_view.py`), through `_elements` and `_set_like_elements`. The algebraic half only iterates the operand and declines one that is not a collection (`_operand` answers `NotImplemented`). The comparison half answers `NotImplemented` for anything but the two set-like views and `Set` / `FrozenSet`. Neither reads `other._data`. Each view supplies its own side through one hook, `_own`: the keys, or a set of `Tuple` pairs.
- `_set_like_elements` does not reuse `_SetAlgebraMixin`'s `_set_like` marker.
- `DictKeys` and `DictItems` are unhashable (`__hash__ = None`), since they are set-like and compare by contents that change under them. `DictValues` is neither, so it compares and hashes by identity.

## Consequences

- A declined operand reads as every other operator refusal: `{"a": 1}.keys() | 5` answers `dict_keys does not understand #| with an int`.
- Mixed operations answer the class CPython answers, including through a view's reflected operator.
- A program that wants a list on the right of a set operator writes the method instead (`s.union(xs)`), as in CPython.
- `d.values()` can be stored in a set.
