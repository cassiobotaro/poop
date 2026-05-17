from __future__ import annotations

import timeit as _timeit
from typing import Any, ClassVar

from poop.types.float import Float
from poop.types.int import Int
from poop.types.list import List
from poop.types.object import Object
from poop.types.string import Str
from poop.types.tuple import Tuple


def _unwrap_stmt(stmt: Any) -> Any:
    if isinstance(stmt, Str):
        return stmt._value
    return stmt


class Timer(Object):
    """Wraps Python's `timeit.Timer`."""

    __slots__ = ("_impl",)

    def __init__(
        self,
        stmt: Str | Any = None,
        setup: Str | Any = None,
        timer: Any = None,
    ) -> None:
        kwargs: dict[str, Any] = {}
        if stmt is not None:
            kwargs["stmt"] = _unwrap_stmt(stmt)
        if setup is not None:
            kwargs["setup"] = _unwrap_stmt(setup)
        if timer is not None:
            kwargs["timer"] = timer
        self._impl = _timeit.Timer(**kwargs)

    def timeit(self, number: Int | None = None) -> Float:
        n = 1000000 if number is None else number._value
        return Float(self._impl.timeit(number=n))

    def repeat(self, repeat: Int | None = None, number: Int | None = None) -> List:
        r = 5 if repeat is None else repeat._value
        n = 1000000 if number is None else number._value
        return List(*(Float(x) for x in self._impl.repeat(repeat=r, number=n)))

    def autorange(self) -> Tuple:
        number, time = self._impl.autorange()
        return Tuple(Int(number), Float(time))


class TimeIt:
    """Namespace mirroring Python's `timeit` module."""

    Timer: ClassVar[type[Timer]] = Timer

    @staticmethod
    def timeit(
        stmt: Str | Any = Str("pass"),
        setup: Str | Any = Str("pass"),
        timer: Any = _timeit.default_timer,
        number: Int = Int(1000000),
        globals: Any = None,
    ) -> Float:
        return Float(
            _timeit.timeit(
                stmt=_unwrap_stmt(stmt),
                setup=_unwrap_stmt(setup),
                timer=timer,
                number=number._value,
                globals=globals,
            )
        )

    @staticmethod
    def repeat(
        stmt: Str | Any = Str("pass"),
        setup: Str | Any = Str("pass"),
        timer: Any = _timeit.default_timer,
        repeat: Int = Int(5),
        number: Int = Int(1000000),
        globals: Any = None,
    ) -> List:
        return List(
            *(
                Float(x)
                for x in _timeit.repeat(
                    stmt=_unwrap_stmt(stmt),
                    setup=_unwrap_stmt(setup),
                    timer=timer,
                    repeat=repeat._value,
                    number=number._value,
                    globals=globals,
                )
            )
        )

    @staticmethod
    def default_timer() -> Float:
        return Float(_timeit.default_timer())
