from typing import TYPE_CHECKING, Self

from poop.types._iterable_mixin import _IterableMixin
from poop.types._peek import _PeekMixin
from poop.types._sentinel import UNPEEKED
from poop.types.object import Object

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator


class _Cursor[T: Object](_PeekMixin[T], _IterableMixin[T], Object, name="object"):
    """What every one-shot iterator and lazy view answers alike.

    `_IteratorBase` and `_LazyView` share all of it: `__iter__`, `iter` and
    the `<name>` repr, which reads the CPython name the `name=` class keyword
    cloaked the class under. They differ only in where the Python iterator
    comes from — handed in, or built on first use — which is what each keeps.
    """

    __slots__ = ("_iter",)

    def __iter__(self) -> Iterator[T]:
        # `self`, not the raw iterator: an element parked by `has_next` would
        # otherwise be skipped by whatever iterated next.
        return self

    def iter(self) -> Self:
        """The iterator itself, as `iter(it) is it` in Python.

        `_IterableMixin` gives every iterator the collection protocol (ADR 30,
        `doc/adr/0030-every-iterator-answers-has-next-by-buffering-one-element.md`)
        — `do`, `map`, `filter`, `find`, `reduce`, `sum`, `min`, `max`, `all`,
        `any`, `enumerate`, `zip` — and `iter` lives on this shared base so
        every iterator and lazy view answers it, and answers `self`, the mirror
        of `iter(zip(...)) is zip(...)` recorded there. One family gives one
        answer to `no_iter`'s substitute column (`col.iter()`), whichever
        iterator the receiver hands back — and the concrete ones are reached by
        ordinary chaining, since `Dict.reversed()` and the three view
        `reversed()`s all answer one:

            [1, 2].iter().iter()          # the same list_iterator
            d.keys().reversed().iter()    # the same dict_reversekeyiterator
        """
        return self

    def __str__(self) -> str:
        return f"<{type(self).__name__}>"


class _IteratorBase[T: Object](_Cursor[T], name="object"):
    """Base for one-shot POOP iterators.

    Wraps a Python iterator. `next()` raises `StopIteration` on exhaustion —
    catch it via `Try(...).except_(StopIteration, handler).run()`.

    Generic over the element type `T`: each concrete iterator declares
    the POOP type it yields (`ListIterator(_IteratorBase[Object])`,
    `StrIterator(_IteratorBase[Str])`, etc.). The `name=` kwarg sets
    the Python-style repr name so a single `__str__` can serve every
    iterator type:

        class ListIterator(_IteratorBase[Object], name="list_iterator"):
            __slots__ = ()
    """

    __slots__ = ()

    def __init_subclass__(
        cls,
        *,
        name: str | None = None,
        iterating: str | None = None,
        **kwargs: object,
    ) -> None:
        super().__init_subclass__(name=name, **kwargs)
        if name is not None:
            # The collection this walks, for the mutation refusal in
            # `_PeekMixin`: CPython's iterator names carry it in front
            # (`list_iterator`, `dict_keyiterator`, `set_iterator`), so the
            # label follows the name a concrete iterator already declares
            # rather than being a second thing to keep in step. `iterating=`
            # is for the one name where the prefix is not the collection's
            # own spelling (`memory_iterator` walks a `memoryview`). The lazy
            # views keep `_PeekMixin`'s default: they cannot name it.
            cls._iterating = iterating or name.split("_", 1)[0]

    def __init__(self, iterable: Iterable[T]) -> None:
        self._iter: Iterator[T] = iter(iterable)
        self._peeked = UNPEEKED

    def _materialize(self) -> Iterator[T]:
        return self._iter


class _LazyView[T: Object](_Cursor[T], name="object"):
    """Base for the lazy views `map`, `filter`, `zip` and `enumerate`.

    `_IteratorBase`'s sibling under `_Cursor`, over a generator built on first
    use instead of a Python iterator handed in. Each view supplies `_generate`,
    which builds that generator from the view's own arguments and drops them —
    the generator owns them from then on, so a consumed view stops pinning its
    whole source and its block.
    """

    __slots__ = ()

    def __init__(self) -> None:
        self._iter: Iterator[T] | None = None
        self._peeked = UNPEEKED

    def _generate(self) -> Iterator[T]:
        raise NotImplementedError

    def _materialize(self) -> Iterator[T]:
        if self._iter is None:
            self._iter = self._generate()
        return self._iter
