from typing import TYPE_CHECKING, Any, ClassVar, Self

from poop.types._cloak import cloak
from poop.types._iterable_mixin import _IterableMixin
from poop.types._peek import _PeekMixin
from poop.types._sentinel import UNPEEKED
from poop.types.object import Object

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator


class _IteratorBase[T](_PeekMixin, _IterableMixin, Object):
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

    __slots__ = ("_iter",)
    _repr_name: ClassVar[str] = "iterator"

    def __init_subclass__(
        cls,
        *,
        name: str | None = None,
        iterating: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init_subclass__(**kwargs)
        if name is not None:
            cls._repr_name = name
            # class_name() reads type(x).__name__ — answer the CPython name.
            cloak(cls, name)
            # The collection this walks, for the mutation refusal in
            # `_PeekMixin`: CPython's iterator names carry it in front
            # (`list_iterator`, `dict_keyiterator`, `set_iterator`), so the
            # label follows the name a concrete iterator already declares
            # rather than being a second thing to keep in step. `iterating=`
            # is for the one name where the prefix is not the collection's
            # own spelling (`memory_iterator` walks a `memoryview`).
            cls._iterating = iterating or name.split("_", 1)[0]

    def __init__(self, iterable: Iterable[Any]) -> None:
        self._iter: Iterator[Any] = iter(iterable)
        self._peeked: Any = UNPEEKED

    def _materialize(self) -> Iterator[Any]:
        return self._iter

    def __iter__(self) -> Iterator[T]:
        return self

    def iter(self) -> Self:
        """The iterator itself, as `iter(it) is it` in Python.

        `_IterableMixin` gives every iterator the collection protocol — the
        paragraph in `INFECTIONS.md` that says so lists `do`, `map`, `filter`,
        `find`, `reduce`, `sum`, `min`, `max`, `all`, `any`, `enumerate`, `zip`
        — and `iter` was the one message of it defined per class instead of on
        a shared base, so the concrete iterators were the half of the family
        that never got one. `Map`, `Filter`, `Enumerate` and `Zip` answer it
        already, and answer `self`, which is the mirror of `iter(zip(...)) is
        zip(...)` recorded there. The other fifteen refused it:

            [1, 2].iter().iter()          # list_iterator does not understand
            d.keys().reversed().iter()    # #iter — did you mean #filter?

        One family, two answers to `no_iter`'s substitute column (`col.iter()`),
        decided by which iterator the receiver happened to hand back — and the
        refusing half is reached by ordinary chaining, since `Dict.reversed()`
        and the three view `reversed()`s all answer a concrete iterator.
        """
        return self

    def __str__(self) -> str:
        return f"<{self._repr_name}>"

    __repr__ = __str__


class _LazyView[T](_PeekMixin, _IterableMixin, Object):
    """Base for the lazy views `map`, `filter`, `zip` and `enumerate`.

    `_IteratorBase`'s sibling: the same `__iter__`, `iter`, `<name>` repr and
    cloak, driven by the same `name=` keyword, over a generator built on first
    use instead of a Python iterator handed in. Each view supplies `_generate`,
    which builds that generator from the view's own arguments and drops them —
    the generator owns them from then on, so a consumed view stops pinning its
    whole source and its block.
    """

    __slots__ = ("_iter",)
    _repr_name: ClassVar[str] = "view"

    def __init_subclass__(cls, *, name: str | None = None, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        if name is not None:
            cls._repr_name = name
            cloak(cls, name)

    def __init__(self) -> None:
        self._iter: Iterator[T] | None = None
        self._peeked: Any = UNPEEKED

    def _generate(self) -> Iterator[T]:
        raise NotImplementedError

    def _materialize(self) -> Iterator[T]:
        if self._iter is None:
            self._iter = self._generate()
        return self._iter

    def __iter__(self) -> Iterator[T]:
        # `self`, not the raw generator: an element parked by `has_next` would
        # otherwise be skipped by whatever iterated next.
        return self

    def iter(self) -> Self:
        return self

    def __str__(self) -> str:
        return f"<{self._repr_name}>"

    __repr__ = __str__


# Cloaked as `object`, as the shared mixins are: `iter` and `__str__` are
# inherited by every concrete iterator and view, so no single builtin name is true for
# all of them — and left alone CPython blamed `_IteratorBase` in every
# wrong-arity message, a private name `_reject_private` exists to keep out of
# user code.
cloak(_IteratorBase, "object")
cloak(_LazyView, "object")
