import builtins
from collections.abc import Callable, Iterator
from typing import TYPE_CHECKING, Any, ClassVar

from poop.types._iterable_mixin import _MISSING
from poop.types._value_eq import _ValueEqMixin
from poop.types.boolean import false, true
from poop.types.object import Object
from poop.types.str_iterator import StrIterator

if TYPE_CHECKING:
    from poop.types.boolean import Boolean
    from poop.types.bytes import Bytes
    from poop.types.int import Int
    from poop.types.list import List
    from poop.types.none import NoneClass
    from poop.types.slice import Slice
    from poop.types.tuple import Tuple

_str = str  # alias to avoid shadowing in annotations


class Str(_ValueEqMixin, Object):
    __slots__ = ("_value",)
    _eq_attr: ClassVar[str] = "_value"

    def __init__(self, value: _str | Str) -> None:
        self._value = value._value if isinstance(value, Str) else value

    def len(self) -> Int:
        from poop.types.int import Int

        return Int(len(self._value))

    def __len__(self) -> int:
        return len(self._value)

    def ord(self) -> Int:
        from poop.types.int import Int

        return Int(ord(self._value))

    def input(self) -> Str:
        return Str(builtins.input(self._value))

    def at(self, index: Int) -> Str:
        return Str(self._value[index._value])

    def slice(
        self,
        start_or_slice: Int | Slice,
        stop: Int | None = None,
        step: Int | None = None,
    ) -> Str:
        from poop.types.slice import Slice

        if isinstance(start_or_slice, Slice):
            s = (
                start_or_slice._step._value
                if start_or_slice._step is not None
                else None
            )
            return Str(
                self._value[
                    start_or_slice._start._value : start_or_slice._stop._value : s
                ]
            )
        if stop is None:
            raise TypeError("stop is required when start is an Int")
        s = step._value if step is not None else None
        return Str(self._value[start_or_slice._value : stop._value : s])

    def __iter__(self) -> Iterator[Str]:
        for ch in self._value:
            yield Str(ch)

    def iter(self) -> StrIterator:
        return StrIterator(self)

    def min(
        self,
        key: Callable[[Str], Any] | None = None,
        default: Any = _MISSING,
    ) -> Any:
        kwargs: dict[str, Any] = {}
        if key is not None:
            kwargs["key"] = key
        if default is not _MISSING:
            kwargs["default"] = default
        return builtins.min(self, **kwargs)

    def max(
        self,
        key: Callable[[Str], Any] | None = None,
        default: Any = _MISSING,
    ) -> Any:
        kwargs: dict[str, Any] = {}
        if key is not None:
            kwargs["key"] = key
        if default is not _MISSING:
            kwargs["default"] = default
        return builtins.max(self, **kwargs)

    def includes(self, char: Str) -> Boolean:
        return true if char._value in self._value else false

    def __contains__(self, item: object) -> bool:
        if isinstance(item, Str):
            return item._value in self._value
        return False

    def reversed(self) -> List:
        from poop.types.list import List

        return List(*[Str(c) for c in reversed(self._value)])

    def upper(self) -> Str:
        return Str(self._value.upper())

    def lower(self) -> Str:
        return Str(self._value.lower())

    def capitalize(self) -> Str:
        return Str(self._value.capitalize())

    def title(self) -> Str:
        return Str(self._value.title())

    def swapcase(self) -> Str:
        return Str(self._value.swapcase())

    def strip(self) -> Str:
        return Str(self._value.strip())

    def lstrip(self) -> Str:
        return Str(self._value.lstrip())

    def rstrip(self) -> Str:
        return Str(self._value.rstrip())

    def replace(self, old: Str, new: Str) -> Str:
        return Str(self._value.replace(old._value, new._value))

    def split(self, sep: Str | NoneClass | None = None) -> List:
        from poop.types._unwrap import _unwrap
        from poop.types.list import List

        return List(*(Str(p) for p in self._value.split(_unwrap(sep, None))))

    def join(self, parts: List) -> Str:
        return Str(self._value.join(str(p) for p in parts))

    def find(self, sub: Str) -> Int:
        from poop.types.int import Int

        return Int(self._value.find(sub._value))

    def index(self, sub: Str) -> Int:
        from poop.types.int import Int

        return Int(self._value.index(sub._value))

    def count(self, sub: Str) -> Int:
        from poop.types.int import Int

        return Int(self._value.count(sub._value))

    def startswith(self, prefix: Str) -> Boolean:
        return true if self._value.startswith(prefix._value) else false

    def endswith(self, suffix: Str) -> Boolean:
        return true if self._value.endswith(suffix._value) else false

    def isalpha(self) -> Boolean:
        return true if self._value.isalpha() else false

    def isdigit(self) -> Boolean:
        return true if self._value.isdigit() else false

    def isalnum(self) -> Boolean:
        return true if self._value.isalnum() else false

    def isspace(self) -> Boolean:
        return true if self._value.isspace() else false

    def isupper(self) -> Boolean:
        return true if self._value.isupper() else false

    def islower(self) -> Boolean:
        return true if self._value.islower() else false

    def casefold(self) -> Str:
        return Str(self._value.casefold())

    def center(self, width: Int, fillchar: Str | NoneClass | None = None) -> Str:
        from poop.types._unwrap import _unwrap

        fill = _unwrap(fillchar, None)
        if fill is None:
            return Str(self._value.center(width._value))
        return Str(self._value.center(width._value, fill))

    def encode(self, encoding: Str) -> Bytes:
        from poop.types.bytes import Bytes

        return Bytes(self._value.encode(encoding._value))

    def expandtabs(self, tabsize: Int | NoneClass | None = None) -> Str:
        from poop.types._unwrap import _unwrap

        size = _unwrap(tabsize, None)
        if size is None:
            return Str(self._value.expandtabs())
        return Str(self._value.expandtabs(size))

    def isascii(self) -> Boolean:
        return true if self._value.isascii() else false

    def isdecimal(self) -> Boolean:
        return true if self._value.isdecimal() else false

    def isidentifier(self) -> Boolean:
        return true if self._value.isidentifier() else false

    def isnumeric(self) -> Boolean:
        return true if self._value.isnumeric() else false

    def isprintable(self) -> Boolean:
        return true if self._value.isprintable() else false

    def istitle(self) -> Boolean:
        return true if self._value.istitle() else false

    def ljust(self, width: Int, fillchar: Str | NoneClass | None = None) -> Str:
        from poop.types._unwrap import _unwrap

        fill = _unwrap(fillchar, None)
        if fill is None:
            return Str(self._value.ljust(width._value))
        return Str(self._value.ljust(width._value, fill))

    def rjust(self, width: Int, fillchar: Str | NoneClass | None = None) -> Str:
        from poop.types._unwrap import _unwrap

        fill = _unwrap(fillchar, None)
        if fill is None:
            return Str(self._value.rjust(width._value))
        return Str(self._value.rjust(width._value, fill))

    def zfill(self, width: Int) -> Str:
        return Str(self._value.zfill(width._value))

    def partition(self, sep: Str) -> Tuple:
        from poop.types.tuple import Tuple

        return Tuple(*[Str(s) for s in self._value.partition(sep._value)])

    def rpartition(self, sep: Str) -> Tuple:
        from poop.types.tuple import Tuple

        return Tuple(*[Str(s) for s in self._value.rpartition(sep._value)])

    def removeprefix(self, prefix: Str) -> Str:
        return Str(self._value.removeprefix(prefix._value))

    def removesuffix(self, suffix: Str) -> Str:
        return Str(self._value.removesuffix(suffix._value))

    def rfind(self, sub: Str) -> Int:
        from poop.types.int import Int

        return Int(self._value.rfind(sub._value))

    def rindex(self, sub: Str) -> Int:
        from poop.types.int import Int

        return Int(self._value.rindex(sub._value))

    def rsplit(self, sep: Str | None = None) -> List:
        from poop.types.list import List

        return List(
            *[
                Str(s)
                for s in self._value.rsplit(sep._value if sep is not None else None)
            ]
        )

    def splitlines(self) -> List:
        from poop.types.list import List

        return List(*[Str(s) for s in self._value.splitlines()])

    def __add__(self, other: Str) -> Str:
        return Str(self._value + other._value)

    def __mul__(self, other: Int) -> Str:
        return Str(self._value * other._value)

    def __rmul__(self, other: Int) -> Str:
        return Str(self._value * other._value)

    def __lt__(self, other: Str) -> Boolean:
        return true if self._value < other._value else false

    def __le__(self, other: Str) -> Boolean:
        return true if self._value <= other._value else false

    def __gt__(self, other: Str) -> Boolean:
        return true if self._value > other._value else false

    def __ge__(self, other: Str) -> Boolean:
        return true if self._value >= other._value else false

    def __hash__(self) -> int:
        return hash(self._value)

    def __str__(self) -> _str:
        return self._value

    def __repr__(self) -> _str:
        return repr(self._value)
