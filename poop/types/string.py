import builtins
import string as _string
from collections.abc import Callable, Iterator
from typing import TYPE_CHECKING, Any, ClassVar

from poop.types._iterable_mixin import _MISSING
from poop.types._repeat import _repeat_count
from poop.types._unwrap import _unwrap
from poop.types._value_eq import _ValueEqMixin
from poop.types.boolean import to_boolean
from poop.types.object import Object
from poop.types.str_iterator import StrIterator

if TYPE_CHECKING:
    from poop.types.boolean import Boolean, to_boolean
    from poop.types.bytes import Bytes
    from poop.types.dict import Dict
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
        stop: Int | NoneClass | None = None,
        step: Int | NoneClass | None = None,
    ) -> Str:
        from poop.types.slice import Slice

        # Route the Int form through Slice so a POOP `none` stop/step
        # (from a `None` literal) means open-ended, like Python's obj[2:].
        if isinstance(start_or_slice, Slice):
            py = start_or_slice._py_slice()
        else:
            py = Slice(start_or_slice, stop, step)._py_slice()
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
        return to_boolean(char._value in self._value)

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
        return Str(self._value.replace(old._value, new._value, _unwrap(count, -1)))

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
        pieces: list[Any] = [getattr(p, "_value", p) for p in parts]
        return Str(self._value.join(pieces))

    def format(self, *args: Object, **kwargs: Object) -> Str:
        # CPython's str.format template substitution. Overrides the
        # inherited Object.format(spec); f-strings are forbidden, so this
        # is POOP's documented template-formatting surface. The rare
        # "apply a spec to a string" case stays expressible as
        # "{:^10}".format(s).
        from poop.types._bridge import to_python

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
            self._value.find(sub._value, _unwrap(start, None), _unwrap(end, None))
        )

    def index(
        self,
        sub: Str,
        start: Int | NoneClass | None = None,
        end: Int | NoneClass | None = None,
    ) -> Int:
        from poop.types.int import Int

        return Int(
            self._value.index(sub._value, _unwrap(start, None), _unwrap(end, None))
        )

    def count(
        self,
        sub: Str,
        start: Int | NoneClass | None = None,
        end: Int | NoneClass | None = None,
    ) -> Int:
        from poop.types.int import Int

        return Int(
            self._value.count(sub._value, _unwrap(start, None), _unwrap(end, None))
        )

    def startswith(
        self,
        prefix: Str | Tuple,
        start: Int | NoneClass | None = None,
        end: Int | NoneClass | None = None,
    ) -> Boolean:
        # CPython accepts a tuple of prefixes; in POOP this is the only
        # message-shaped substitute for the forbidden `s.startswith("a")
        # or s.startswith("b")`. Unwrap each element to its underlying value
        # (not str(p)) so a non-Str member reaches str.startswith and raises
        # the faithful TypeError instead of being silently stringified.
        needle: _str | tuple[Any, ...] = (
            prefix._value
            if isinstance(prefix, Str)
            else tuple(getattr(p, "_value", p) for p in prefix._items)
        )
        return to_boolean(
            self._value.startswith(needle, _unwrap(start, None), _unwrap(end, None))
        )

    def endswith(
        self,
        suffix: Str | Tuple,
        start: Int | NoneClass | None = None,
        end: Int | NoneClass | None = None,
    ) -> Boolean:
        needle: _str | tuple[Any, ...] = (
            suffix._value
            if isinstance(suffix, Str)
            else tuple(getattr(p, "_value", p) for p in suffix._items)
        )
        return to_boolean(
            self._value.endswith(needle, _unwrap(start, None), _unwrap(end, None))
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
            return Str(self._value.center(width._value))
        return Str(self._value.center(width._value, fill))

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
            return Str(self._value.ljust(width._value))
        return Str(self._value.ljust(width._value, fill))

    def rjust(self, width: Int, fillchar: Str | NoneClass | None = None) -> Str:
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

    def rfind(
        self,
        sub: Str,
        start: Int | NoneClass | None = None,
        end: Int | NoneClass | None = None,
    ) -> Int:
        from poop.types.int import Int

        return Int(
            self._value.rfind(sub._value, _unwrap(start, None), _unwrap(end, None))
        )

    def rindex(
        self,
        sub: Str,
        start: Int | NoneClass | None = None,
        end: Int | NoneClass | None = None,
    ) -> Int:
        from poop.types.int import Int

        return Int(
            self._value.rindex(sub._value, _unwrap(start, None), _unwrap(end, None))
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

    def __add__(self, other: Str) -> Str:
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


def _dict_to_mapping(mapping: Dict) -> dict[str, Any]:
    # Template.substitute / safe_substitute accept any mapping whose
    # keys are Python strs. POOP `Dict` keys are POOP `Str` values, so
    # unwrap them; values are stringified by `string.Template` itself.
    result: dict[str, Any] = {}
    for k, v in mapping._data.items():
        if not isinstance(k, Str):
            raise TypeError(
                f"Template mapping keys must be Str, got {type(k).__name__}"
            )
        result[k._value] = v._value if isinstance(v, Str) else v
    return result


class Template:
    """Wraps Python's `string.Template` for `$variable` substitution.

    Construction takes the template `Str`; `substitute` raises on
    missing keys, `safe_substitute` leaves them in place. The
    `template` property exposes the original source string.
    """

    __slots__ = ("_impl",)

    def __init__(self, template: Str) -> None:
        self._impl = _string.Template(template._value)

    def substitute(self, mapping: Dict) -> Str:
        return Str(self._impl.substitute(_dict_to_mapping(mapping)))

    def safe_substitute(self, mapping: Dict) -> Str:
        return Str(self._impl.safe_substitute(_dict_to_mapping(mapping)))

    @property
    def template(self) -> Str:
        return Str(self._impl.template)


class String:
    """Namespace mirroring Python's `string` module.

    ASCII character-class constants plus the `Template` class (exposed
    separately under its own PascalCase binding, matching the
    `hmac`/`HMAC` and `uuid`/`UUID` convention) and `capwords`.

    `string.Formatter` is deliberately omitted — `Str.format` covers
    the common case.
    """

    ascii_letters: ClassVar[Str] = Str(_string.ascii_letters)
    ascii_lowercase: ClassVar[Str] = Str(_string.ascii_lowercase)
    ascii_uppercase: ClassVar[Str] = Str(_string.ascii_uppercase)
    digits: ClassVar[Str] = Str(_string.digits)
    hexdigits: ClassVar[Str] = Str(_string.hexdigits)
    octdigits: ClassVar[Str] = Str(_string.octdigits)
    punctuation: ClassVar[Str] = Str(_string.punctuation)
    printable: ClassVar[Str] = Str(_string.printable)
    whitespace: ClassVar[Str] = Str(_string.whitespace)

    @staticmethod
    def capwords(s: Str, sep: Str | NoneClass | None = None) -> Str:
        return Str(_string.capwords(s._value, _unwrap(sep, None)))
