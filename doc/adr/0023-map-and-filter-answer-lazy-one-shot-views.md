# 23. `map` and `filter` answer lazy, one-shot views

Date: 2026-04-22

## Status

Accepted

## Context

`map(func, col)` and `filter(func, col)` are free functions with a procedural look, banned by `no_map` and `no_filter` (`poop/validators/no_map.py`, `poop/validators/no_filter.py`). Their substitutes are messages to the collection, and the answer could be a materialised collection of the receiver's type or a lazy view, as Python's builtins answer.

Python's own `map` and `filter` are one-shot, as its `zip` is: `list(z)` twice on one `zip` gives the pairs and then `[]`. An `__iter__` that answered a fresh generator instead of `self` would skip an element parked by `has_next`.

`Map` and `Filter` are Python generators, so a `StopIteration` raised by the user's block used to hit PEP 479 and surface as `generator raised StopIteration`, a report about a construct POOP does not have and `no_yield` bans. Letting the `StopIteration` through instead would end the view early and answer a quietly truncated collection.

## Decision

`col.map(block)`, `col.filter(block)` and `col.filter_false(block)` answer a lazy `Map` or `Filter` (`poop/types/map.py`, `poop/types/filter.py`), whatever the receiver's type, in the same family as `Enumerate` and `Zip`. The block runs on demand as the result is consumed.

- A program materialises a view by passing it to a constructor: `list(col.map(f))`, `tuple(col.filter(g))`, `set(col.map(f))`, `bytes(col.map(g))`.
- Both views inherit `_IterableMixin`, so the consuming messages (`do`, `sum`, `min`, `max`, `find`, `reduce`, `all`, `any`) work on them directly, and `col.map(f).filter(g).sum()` iterates once through the source.
- Both are one-shot. `__iter__` answers `self`, and `_materialize` builds the internal generator once and drops the source and the block with it, so a consumed view answers nothing on a second pass, by `.next()`, by `.do()`, or by a chained view.
- A `StopIteration` raised by the block is caught inside the generator and answers `a block ran off the end of an iterator — ask #has_next before #next`.
- `Map` and `Filter` are internal: they have no transformer and are not bound in `DEFAULT_NAMESPACE`. `_BlockView` (`poop/types/_block_view.py`) owns their slots, constructor, `_generate` and the guarded block call, and each supplies a one-line generator.

## Consequences

The views behave as Python's `map` and `filter` do, including being exhausted after one pass. The consuming messages drain them as they drain any one-shot iterator. Python tests, where the transformer does not run, construct a materialised list by varargs unpack (`List(*items.map(...))`) or import `Map(source, block)` / `Filter(source, block)` directly.
