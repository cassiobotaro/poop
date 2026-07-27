"""One-element lookahead, so exhaustion is a question rather than an exception.

POOP's own iterator example teaches the cursor protocol — `has_next` / `next`,
driven by `while_true`:

    (lambda: cursor.has_next()).while_true(lambda: cursor.next().print())

but that `cursor` was a hand-written class in the example. No built-in iterator
answered `has_next`, so the protocol POOP held up as idiomatic was the one thing
`[1, 2].iter()` could not do, and driving a built-in with `while_true` ran it
off the end. The alternatives were both unsatisfying: `next(default)` conflates
an exhausted iterator with one answering `none`, and a `Try` is a heavy spelling
for "am I done?".

**The cost is real and was chosen, not discovered.** A one-shot Python iterator
cannot be peeked, so `has_next` means buffering one element — and for `Map` and
`Filter` that pulls the user's block one step ahead of where it runs, which is
observable whenever the block prints or mutates. The buffer is filled *only* by
`has_next`: a program that never asks is unaffected, and one that does has
opted into the lookahead. The alternative — `has_next` only on the iterators
that can answer it structurally (`ListIterator`, `RangeIterator`, `StrIterator`)
— leaves a protocol half the iterators answer, which is the opposite of having
one.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from poop.types.exceptions import MIRRORS

if TYPE_CHECKING:
    from collections.abc import Iterator

    from poop.types.boolean import Boolean

# "No default given", so `it.next()` still raises while `it.next(x)` answers x —
# mirroring Python's two-arg `next(iterator, default)`.
_MISSING: Any = object()

# "Nothing buffered", distinct from a buffered `none`: an iterator yielding
# POOP's `none` must not read as an empty buffer.
_UNPEEKED: Any = object()


class _PeekMixin:
    """`has_next` / `next` over an iterator that can be looked ahead by one."""

    __slots__ = ("_peeked",)

    def _materialize(self) -> Iterator[Any]:
        """The underlying Python iterator. Supplied by the concrete class."""
        raise NotImplementedError

    def _wrap(self, value: Any) -> Any:
        """The POOP value behind a raw one from the iterator.

        Identity for almost every iterator. The dict item iterators re-wrap
        their `(k, v)` pairs as `Tuple`s, and they must do it *after* the
        buffer rather than instead of `next`, or a peeked pair would be
        delivered raw.
        """
        return value

    def _exhausted(self) -> Exception:
        return MIRRORS["StopIteration"](
            f"{type(self).__name__} is exhausted — "
            "send #next with a default, or ask #has_next"
        )

    def has_next(self) -> Boolean:
        from poop.types.boolean import false, true

        if self._peeked is not _UNPEEKED:
            return true
        try:
            self._peeked = next(self._materialize())
        except StopIteration:
            return false
        return true

    def _buffered(self) -> Any:
        value = self._peeked
        self._peeked = _UNPEEKED
        return self._wrap(value)

    def next(self, default: Any = _MISSING) -> Any:
        if self._peeked is not _UNPEEKED:
            return self._buffered()
        try:
            value = next(self._materialize())
        except StopIteration:
            if default is not _MISSING:
                return default
            # Still a mirrored StopIteration — it is in `_HIERARCHY` precisely
            # so a Try can catch it — but with a sentence. The native carries
            # no message at all, so the error degraded to a bare class name:
            # a word naming the CPython protocol that drives `for`, the loop
            # POOP forbids, with nothing to say what went wrong.
            raise self._exhausted() from None
        return self._wrap(value)

    def __next__(self) -> Any:
        # Every iteration path goes through the buffer, or a peeked element
        # would be skipped by the `do`/`map`/`filter` that came after the ask.
        if self._peeked is not _UNPEEKED:
            return self._buffered()
        return self._wrap(next(self._materialize()))
