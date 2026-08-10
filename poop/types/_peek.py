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

from typing import TYPE_CHECKING, Any, ClassVar

from poop.types._cloak import cloak
from poop.types._mutated import reword_if_native
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

    # What the mutation refusal calls the collection being walked. `_mutated`
    # exists so that refusal names its receiver (`dict changed while it was
    # being iterated`), and the cursor was the one place passing a literal —
    # so `d.do(...)` and `d.iter().next()` reported the same fact in two
    # vocabularies. `_IteratorBase` derives this from the CPython iterator
    # name each concrete iterator already declares; the lazy views (`Map`,
    # `Filter`, `Zip`, `Enumerate`) keep the default, which is honest: the
    # mutated collection is the one behind them, and they cannot name it.
    _iterating: ClassVar[str] = "the collection"

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
        except RuntimeError as exc:
            # The same rewording `next` and `__next__` already carry, and the
            # one message of the three that exists so a program can *ask*
            # instead of raising: it answered `dictionary changed size during
            # iteration` — a word POOP does not use for a `dict`, describing a
            # `for` loop the program did not write.
            raise reword_if_native(exc, self._iterating) from None
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
        except RuntimeError as exc:
            # `dictionary changed size during iteration` — a word POOP does not
            # use for a `dict`, describing a `for` loop the program did not
            # write. POOP's own RuntimeErrors pass through untouched.
            raise reword_if_native(exc, self._iterating) from None
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
        try:
            return self._wrap(next(self._materialize()))
        except RuntimeError as exc:
            raise reword_if_native(exc, self._iterating) from None


# Cloaked as `object`, the root's own spelling: these methods are inherited by
# many wrappers, so no single builtin name is true for all of them — and left
# alone CPython blamed `_PeekMixin` in every wrong-arity message, a private name
# `_reject_private` exists to keep out of user code.
cloak(_PeekMixin, "object")
