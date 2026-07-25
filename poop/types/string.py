import builtins
from collections.abc import Callable, Iterator
from string import Formatter as _Formatter
from typing import TYPE_CHECKING, Any, ClassVar

from poop.types._iterable_mixin import _MISSING, _minmax
from poop.types._repeat import _repeat_count
from poop.types._unwrap import _faithful, _unwrap
from poop.types._value_eq import _ValueEqMixin
from poop.types.boolean import to_boolean
from poop.types.object import Object
from poop.types.str_iterator import StrIterator

if TYPE_CHECKING:
    from poop.types.boolean import Boolean, to_boolean
    from poop.types.bytes import Bytes
    from poop.types.int import Int
    from poop.types.list import List
    from poop.types.none import NoneClass
    from poop.types.slice import Slice
    from poop.types.tuple import Tuple

_str = str  # alias to avoid shadowing in annotations


def _reject_field_access(template: _str) -> None:
    """Refuse `{0.attr}` / `{0[key]}` — a format field is not an escape hatch.

    `str.format` reads attributes and items at *runtime*, from inside a string
    literal no validator can read, so `"{0.__class__}".format(5)` printed
    `<class 'int'>` — reopening exactly what `no_dunder_attribute` closes, and
    `{0[0]}` what `no_subscript` closes. This is the third half of the same
    ban, alongside `Object._reject_dunder`: both guard a spelling that reaches
    the runtime as data.

    Only the field *name* is inspected — a format spec may legitimately carry a
    dot (`{:.2f}`), and `Formatter.parse` already splits the two. The recursion
    covers a nested spec, which is parsed again at format time and would
    otherwise smuggle the same access through (`"{0:{1.__class__}}"`).
    """
    for _, field, spec, _ in _Formatter().parse(template):
        if field and ("." in field or "[" in field):
            raise ValueError(
                f"{{{field}}} is forbidden — a format field reaching an "
                "attribute or an item bypasses obj.get_attr(...) / obj.at(...); "
                "send the message and format the answer"
            )
        if spec:
            _reject_field_access(spec)


def _affix_needle(affix: object) -> Any:
    """The `str.startswith` / `str.endswith` argument behind a POOP affix.

    A `Str` unwraps to its value; a `Tuple` to a tuple of faithfully unwrapped
    members — CPython accepts a tuple of prefixes, and in POOP that is the only
    message-shaped substitute for the forbidden `s.startswith("a") or
    s.startswith("b")`. Members unwrap through `_faithful` (not `str(p)`) so a
    non-`Str` member reaches `str.startswith` and raises the faithful
    `TypeError` instead of being silently stringified.

    Anything that is neither — an `Int`, a `List` — reaches CPython raw for the
    same reason: reading `._items` off it would answer `int does not
    understand #_items`, naming a POOP internal.
    """
    from poop.types.tuple import Tuple  # circular: tuple imports string

    if isinstance(affix, Str):
        return affix._value
    if isinstance(affix, Tuple):
        return tuple(_faithful(p) for p in affix._items)
    return _faithful(affix)


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
        stop: Int | NoneClass | None = None,
        step: Int | NoneClass | None = None,
    ) -> Str:
        from poop.types.slice import _resolve_py_slice

        py = _resolve_py_slice(start_or_slice, stop, step)
        return Str(self._value[py])

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
        return _minmax(builtins.min, self, key, default)

    def max(
        self,
        key: Callable[[Str], Any] | None = None,
        default: Any = _MISSING,
    ) -> Any:
        return _minmax(builtins.max, self, key, default)

    def includes(self, char: Str) -> Boolean:
        # getattr-unwrap: a non-`_value` argument (List, Set, …) reaches
        # str.__contains__ raw and raises the faithful TypeError ("requires
        # string as left operand"), instead of leaking `_value` through dispatch.
        operand: Any = _faithful(char)
        return to_boolean(operand in self._value)

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

    def strip(self, chars: Str | NoneClass | None = None) -> Str:
        return Str(self._value.strip(_unwrap(chars, None)))

    def lstrip(self, chars: Str | NoneClass | None = None) -> Str:
        return Str(self._value.lstrip(_unwrap(chars, None)))

    def rstrip(self, chars: Str | NoneClass | None = None) -> Str:
        return Str(self._value.rstrip(_unwrap(chars, None)))

    def replace(
        self,
        old: Str,
        new: Str,
        count: Int | NoneClass | None = None,
    ) -> Str:
        return Str(
            self._value.replace(
                _faithful(old),
                _faithful(new),
                _unwrap(count, -1),
            )
        )

    def split(
        self,
        sep: Str | NoneClass | None = None,
        maxsplit: Int | NoneClass | None = None,
    ) -> List:
        from poop.types.list import List

        return List(
            *(
                Str(p)
                for p in self._value.split(_unwrap(sep, None), _unwrap(maxsplit, -1))
            )
        )

    def join(self, parts: List) -> Str:
        # Mirror CPython: unwrap each element to its underlying value and let
        # str.join validate. Str parts join cleanly; anything else (Int,
        # Bytes, ...) reaches str.join unwrapped and raises the faithful
        # TypeError instead of being silently stringified via str(p).
        pieces: list[Any] = [_faithful(p) for p in parts]
        return Str(self._value.join(pieces))

    def format(self, *args: Object, **kwargs: Object) -> Str:
        # CPython's str.format template substitution. Overrides the
        # inherited Object.format(spec); f-strings are forbidden, so this
        # is POOP's documented template-formatting surface. The rare
        # "apply a spec to a string" case stays expressible as
        # "{:^10}".format(s).
        from poop.types._bridge import to_python

        _reject_field_access(self._value)
        return Str(
            self._value.format(
                *(to_python(a) for a in args),
                **{k: to_python(v) for k, v in kwargs.items()},
            )
        )

    def find(
        self,
        sub: Str,
        start: Int | NoneClass | None = None,
        end: Int | NoneClass | None = None,
    ) -> Int:
        from poop.types.int import Int

        return Int(
            self._value.find(_faithful(sub), _unwrap(start, None), _unwrap(end, None))
        )

    def index(
        self,
        sub: Str,
        start: Int | NoneClass | None = None,
        end: Int | NoneClass | None = None,
    ) -> Int:
        from poop.types.int import Int

        return Int(
            self._value.index(_faithful(sub), _unwrap(start, None), _unwrap(end, None))
        )

    def count(
        self,
        sub: Str,
        start: Int | NoneClass | None = None,
        end: Int | NoneClass | None = None,
    ) -> Int:
        from poop.types.int import Int

        return Int(
            self._value.count(_faithful(sub), _unwrap(start, None), _unwrap(end, None))
        )

    def startswith(
        self,
        prefix: Str | Tuple,
        start: Int | NoneClass | None = None,
        end: Int | NoneClass | None = None,
    ) -> Boolean:
        return to_boolean(
            self._value.startswith(
                _affix_needle(prefix), _unwrap(start, None), _unwrap(end, None)
            )
        )

    def endswith(
        self,
        suffix: Str | Tuple,
        start: Int | NoneClass | None = None,
        end: Int | NoneClass | None = None,
    ) -> Boolean:
        return to_boolean(
            self._value.endswith(
                _affix_needle(suffix), _unwrap(start, None), _unwrap(end, None)
            )
        )

    def isalpha(self) -> Boolean:
        return to_boolean(self._value.isalpha())

    def isdigit(self) -> Boolean:
        return to_boolean(self._value.isdigit())

    def isalnum(self) -> Boolean:
        return to_boolean(self._value.isalnum())

    def isspace(self) -> Boolean:
        return to_boolean(self._value.isspace())

    def isupper(self) -> Boolean:
        return to_boolean(self._value.isupper())

    def islower(self) -> Boolean:
        return to_boolean(self._value.islower())

    def casefold(self) -> Str:
        return Str(self._value.casefold())

    def center(self, width: Int, fillchar: Str | NoneClass | None = None) -> Str:
        fill = _unwrap(fillchar, None)
        if fill is None:
            return Str(self._value.center(_faithful(width)))
        return Str(self._value.center(_faithful(width), fill))

    def encode(
        self,
        encoding: Str | NoneClass | None = None,
        errors: Str | NoneClass | None = None,
    ) -> Bytes:
        from poop.types._unwrap import _opt_str
        from poop.types.bytes import Bytes

        return Bytes(
            self._value.encode(
                _opt_str(encoding, "utf-8"),
                _opt_str(errors, "strict"),
            )
        )

    def expandtabs(self, tabsize: Int | NoneClass | None = None) -> Str:
        size = _unwrap(tabsize, None)
        if size is None:
            return Str(self._value.expandtabs())
        return Str(self._value.expandtabs(size))

    def isascii(self) -> Boolean:
        return to_boolean(self._value.isascii())

    def isdecimal(self) -> Boolean:
        return to_boolean(self._value.isdecimal())

    def isidentifier(self) -> Boolean:
        return to_boolean(self._value.isidentifier())

    def isnumeric(self) -> Boolean:
        return to_boolean(self._value.isnumeric())

    def isprintable(self) -> Boolean:
        return to_boolean(self._value.isprintable())

    def istitle(self) -> Boolean:
        return to_boolean(self._value.istitle())

    def ljust(self, width: Int, fillchar: Str | NoneClass | None = None) -> Str:
        fill = _unwrap(fillchar, None)
        if fill is None:
            return Str(self._value.ljust(_faithful(width)))
        return Str(self._value.ljust(_faithful(width), fill))

    def rjust(self, width: Int, fillchar: Str | NoneClass | None = None) -> Str:
        fill = _unwrap(fillchar, None)
        if fill is None:
            return Str(self._value.rjust(_faithful(width)))
        return Str(self._value.rjust(_faithful(width), fill))

    def zfill(self, width: Int) -> Str:
        return Str(self._value.zfill(_faithful(width)))

    def partition(self, sep: Str) -> Tuple:
        from poop.types.tuple import Tuple

        return Tuple(*[Str(s) for s in self._value.partition(_faithful(sep))])

    def rpartition(self, sep: Str) -> Tuple:
        from poop.types.tuple import Tuple

        return Tuple(*[Str(s) for s in self._value.rpartition(_faithful(sep))])

    def removeprefix(self, prefix: Str) -> Str:
        return Str(self._value.removeprefix(_faithful(prefix)))

    def removesuffix(self, suffix: Str) -> Str:
        return Str(self._value.removesuffix(_faithful(suffix)))

    def rfind(
        self,
        sub: Str,
        start: Int | NoneClass | None = None,
        end: Int | NoneClass | None = None,
    ) -> Int:
        from poop.types.int import Int

        return Int(
            self._value.rfind(_faithful(sub), _unwrap(start, None), _unwrap(end, None))
        )

    def rindex(
        self,
        sub: Str,
        start: Int | NoneClass | None = None,
        end: Int | NoneClass | None = None,
    ) -> Int:
        from poop.types.int import Int

        return Int(
            self._value.rindex(_faithful(sub), _unwrap(start, None), _unwrap(end, None))
        )

    def rsplit(
        self,
        sep: Str | NoneClass | None = None,
        maxsplit: Int | NoneClass | None = None,
    ) -> List:
        from poop.types.list import List

        return List(
            *(
                Str(s)
                for s in self._value.rsplit(_unwrap(sep, None), _unwrap(maxsplit, -1))
            )
        )

    def splitlines(self, keepends: Boolean | NoneClass | None = None) -> List:
        from poop.types._unwrap import _unwrap_bool
        from poop.types.list import List

        return List(
            *[Str(s) for s in self._value.splitlines(_unwrap_bool(keepends, False))]
        )

    def __add__(self, other: object) -> Str:
        if not isinstance(other, Str):
            return NotImplemented  # foreign operand -> faithful TypeError
        return Str(self._value + other._value)

    def __mul__(self, other: object) -> Str:
        return Str(self._value * _repeat_count(other))

    def __rmul__(self, other: object) -> Str:
        return Str(self._value * _repeat_count(other))

    def __mod__(self, other: object) -> Str:
        # printf-style formatting: "v %s" % 5, "%s/%s" % (a, b), or
        # "%(k)s" % mapping. to_python deep-unwraps the right operand
        # (scalar, Tuple -> tuple, Dict -> dict), then CPython's str.__mod__
        # applies the template and raises faithful TypeErrors on mismatch.
        from poop.types._bridge import to_python

        return Str(self._value % to_python(other))

    def __lt__(self, other: object) -> Boolean:
        if not isinstance(other, Str):
            return NotImplemented  # foreign operand -> faithful TypeError
        return to_boolean(self._value < other._value)

    def __le__(self, other: object) -> Boolean:
        if not isinstance(other, Str):
            return NotImplemented
        return to_boolean(self._value <= other._value)

    def __gt__(self, other: object) -> Boolean:
        if not isinstance(other, Str):
            return NotImplemented
        return to_boolean(self._value > other._value)

    def __ge__(self, other: object) -> Boolean:
        if not isinstance(other, Str):
            return NotImplemented
        return to_boolean(self._value >= other._value)

    def __hash__(self) -> int:
        return hash(self._value)

    def __str__(self) -> _str:
        return self._value

    def __repr__(self) -> _str:
        return repr(self._value)


Str.__module__ = "builtins"
Str.__name__ = "str"
