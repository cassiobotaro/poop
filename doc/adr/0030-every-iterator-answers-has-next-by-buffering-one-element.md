# 30. Every iterator answers `has_next` by buffering one element

Date: 2026-05-05

## Status

Accepted

## Context

`no_iter` bans `iter(col)` and `next(it)` and names `col.iter()` and `it.next()` as their substitutes. Exhaustion surfaces as `StopIteration`, and the native one carries no message, so `_describe` degraded to the bare class name: a word naming the CPython protocol that drives `for`, the loop POOP forbids, with nothing to say what went wrong.

`examples/patterns/iterator.py` teaches a cursor protocol, which needs a way to test exhaustion without an exception. A one-shot Python iterator cannot be peeked, so answering `has_next` costs a buffered element, and for `Map`/`Filter` that pulls the user's block one step ahead of where it runs. The alternative, `has_next` only where it is structurally cheap (`ListIterator`, `RangeIterator`, `StrIterator`), leaves a protocol half the iterators answer, which is the opposite of having one.

Two more gaps sat on the same family:

- `iter` was defined per class rather than on a shared base. `Map`, `Filter`, `Enumerate` and `Zip` answered `col.iter()` and the fifteen concrete iterators refused it (`list_iterator does not understand #iter — did you mean #filter?`), which ordinary chaining reaches, since `Dict.reversed()` and the three view `reversed()`s answer a concrete iterator. The four that answered are why every per-iterator test happened to pass.
- `Map` and `Filter` are Python generators, so a `StopIteration` raised by the user's block hit PEP 479 and surfaced as `generator raised StopIteration`, a report about a construct POOP does not have and `no_yield` bans.

## Decision

Every collection's `.iter()` answers a specialized one-shot iterator that mirrors Python's iterator types (`list_iterator`, `tuple_iterator`, `set_iterator`, `dict_keyiterator`, `str_iterator`, `range_iterator`, `bytes_iterator`, `bytearray_iterator`, `memory_iterator`, and the rest). All inherit from `_IteratorBase` (`poop/types/_iterator_base.py`):

- `.next()` raises `StopIteration` on exhaustion with a sentence: `list_iterator is exhausted — send #next with a default, or ask #has_next`. `.next(default)` answers `default` instead, mirroring `next(it, default)`.
- Every lazy view and iterator answers `has_next` (`poop/types/_peek.py`) by buffering one element. Only `has_next` fills the buffer, and every iteration path routes through it.
- `_IteratorBase` inherits `_IterableMixin`, so an iterator answers the same protocol as collections and views, and `_IteratorBase.iter()` answers `self`, mirroring `iter(it) is it`.

`Map` and `Filter` catch a `StopIteration` raised by the user's block inside the generator and answer `a block ran off the end of an iterator — ask #has_next before #next`.

## Consequences

- Exhaustion is testable without an exception: `(lambda: it.has_next()).while_true(lambda: it.next().print())`.
- A program that never asks `has_next` is unaffected; one that asks has opted into the lookahead, including running a `Map`/`Filter` block one element early.
- A peeked element is not skipped by a `do` or `map` sent after the ask.
- What PEP 479 protects against stays protected: letting the `StopIteration` through would end the view early and answer a quietly truncated collection.
- The consuming messages (`find`, `reduce`, `min`, …) drain a one-shot iterator, as in Python; the lazy ones (`map`, `filter`, `enumerate`, `zip`) answer a fresh view over the remainder.
- `tests/test_iterator_protocol.py` sweeps the iterator family rather than asserting per iterator.
