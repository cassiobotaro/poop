import builtins
from collections.abc import Callable, Iterator
from string import Formatter as _Formatter
from typing import TYPE_CHECKING, Any, ClassVar

from poop.types._affix import affix_needle
from poop.types._argument import a_bound, text_like
from poop.types._at import at_index
from poop.types._cloak import cloak
from poop.types._codec import encoded
from poop.types._iterable_mixin import _IterableMixin
from poop.types._minmax import _MISSING, _minmax
from poop.types._repeat import _repeat_count
from poop.types._unwrap import _faithful, _unwrap
from poop.types._value_eq import _ValueEqMixin
from poop.types.boolean import to_boolean
from poop.types.exceptions import MIRRORS
from poop.types.object import Object
from poop.types.str_iterator import StrIterator

if TYPE_CHECKING:
    from poop.types._index import Index
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
            raise MIRRORS["ValueError"](
                f"{{{field}}} is forbidden — a format field reaching an "
                "attribute or an item bypasses obj.get_attr(...) / obj.at(...); "
                "send the message and format the answer"
            )
        if spec:
            _reject_field_access(spec)


def _needle(sub: object, selector: str) -> Any:
    """The substring `find` / `rfind` / `index` / `rindex` / `count` look for.

    These five keep their string meaning where `_IterableMixin.find` takes a
    block, so a reader arriving from `[1, 2].find(block)` writes a block here.
    CPython answers `find() argument 1 must be str, not function` — the method
    as a call, and `function`, which POOP prints as `<block>`.

    The `r`-prefixed pair is the same message read from the other end, and was
    left on `_faithful` — so `"abc".find(block)` and `"abc".rfind(block)`, the
    same mistake one letter apart, answered in two different vocabularies.
    """
    if not isinstance(sub, Str) and callable(sub):
        raise MIRRORS["TypeError"](
            f"str's #{selector} searches for a substring — "
            "it takes the text to look for, not a block"
        )
    # Anything else that is not text reached CPython and answered
    # `find() argument 1 must be str, not int` — the message spelt as a call.
    return text_like(sub, selector, "a str")


class Str(_ValueEqMixin, _IterableMixin, Object):
    """A string, and — since proposal 24 — a collection like any other.

    `no_map`, `no_filter`, `no_all`, `no_any` and `no_loops` each name a
    message on the collection as the substitute, `_IterableMixin` supplies
    them, and a `Str` did not inherit it: the most-written receiver in the
    language answered `str does not understand #do`, leaving iteration to be
    driven by hand through the cursor. The three string-specific messages
    (`find`, `count`, `index`, which search for a substring rather than for a
    match) override the mixin's below, and `sum` refuses.
    """

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

        try:
            return Int(ord(self._value))
        except TypeError:
            # CPython answers `ord() expected a character, but string of
            # length 3 found` — the builtin spelled as the call this message
            # substitutes.
            raise MIRRORS["TypeError"](
                f"#ord expects a single character, got {len(self._value)}"
            ) from None

    def input(self) -> Str:
        try:
            return Str(builtins.input(self._value))
        except EOFError:
            # `EOF when reading a line` names CPython's own end-of-file
            # condition and the *line* the reader never asked for. A pipe
            # rather than a terminal is enough to reach it — it is what
            # `examples/basics/greet.py` answered when its stdin was closed.
            raise MIRRORS["EOFError"]("there is no more input to read") from None

    def at(self, index: Index) -> Str:
        return Str(at_index(self._value, index, self))

    def slice(
        self,
        start_or_slice: Index | Slice | NoneClass | None,
        stop: Index | NoneClass | None = None,
        step: Index | NoneClass | None = None,
    ) -> Str:
        from poop.types.slice import _resolve_py_slice

        py = _resolve_py_slice(start_or_slice, stop, step)
        return Str(self._value[py])

    def __iter__(self) -> Iterator[Str]:
        for ch in self._value:
            yield Str(ch)

    def iter(self) -> StrIterator:
        return StrIterator(self)

    def sum(self, start: Any = None) -> Any:
        # The one mixin message a string must not answer: `sum("ab")` is a
        # TypeError in CPython, and adding the characters up would answer the
        # string back, which is `join`'s job.
        from poop.types.exceptions import MIRRORS

        raise MIRRORS["TypeError"](
            "str cannot be summed — send #join to a list of pieces instead"
        )

    def min(
        self,
        *,
        key: Callable[[Str], Any] | NoneClass | None = None,
        default: Any = _MISSING,
    ) -> Any:
        return _minmax(builtins.min, "#min", self, key, default)

    def max(
        self,
        *,
        key: Callable[[Str], Any] | NoneClass | None = None,
        default: Any = _MISSING,
    ) -> Any:
        return _minmax(builtins.max, "#max", self, key, default)

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

    def reversed(self) -> Str:
        # A `Str`, as `slice` and `at` on this receiver already answer one:
        # every other collection answers its own kind from `reversed`, so a
        # `List` of one-character `Str`s made this the single message on a
        # string that changes the type, and broke `s.reversed().upper()`.
        # The list spelling stays reachable as `list(s.reversed())`.
        return Str(self._value[::-1])

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
                text_like(old, "replace", "a str"),
                text_like(new, "replace", "a str"),
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
            self._value.find(
                _needle(sub, "find"),
                a_bound(start, "find", "start"),
                a_bound(end, "find", "end"),
            )
        )

    def index(
        self,
        sub: Str,
        start: Int | NoneClass | None = None,
        end: Int | NoneClass | None = None,
    ) -> Int:
        from poop.types.int import Int

        return Int(
            self._value.index(
                _needle(sub, "index"),
                a_bound(start, "index", "start"),
                a_bound(end, "index", "end"),
            )
        )

    def count(
        self,
        sub: Str,
        start: Int | NoneClass | None = None,
        end: Int | NoneClass | None = None,
    ) -> Int:
        from poop.types.int import Int

        return Int(
            self._value.count(
                _needle(sub, "count"),
                a_bound(start, "count", "start"),
                a_bound(end, "count", "end"),
            )
        )

    def startswith(
        self,
        prefix: Str | Tuple,
        start: Int | NoneClass | None = None,
        end: Int | NoneClass | None = None,
    ) -> Boolean:
        return to_boolean(
            self._value.startswith(
                affix_needle(prefix),
                a_bound(start, "startswith", "start"),
                a_bound(end, "startswith", "end"),
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
                affix_needle(suffix),
                a_bound(start, "endswith", "start"),
                a_bound(end, "endswith", "end"),
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
            encoded(
                self._value,
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
        return Str(self._value.removeprefix(text_like(prefix, "removeprefix", "a str")))

    def removesuffix(self, suffix: Str) -> Str:
        return Str(self._value.removesuffix(text_like(suffix, "removesuffix", "a str")))

    def rfind(
        self,
        sub: Str,
        start: Int | NoneClass | None = None,
        end: Int | NoneClass | None = None,
    ) -> Int:
        from poop.types.int import Int

        return Int(
            self._value.rfind(
                _needle(sub, "rfind"),
                a_bound(start, "rfind", "start"),
                a_bound(end, "rfind", "end"),
            )
        )

    def rindex(
        self,
        sub: Str,
        start: Int | NoneClass | None = None,
        end: Int | NoneClass | None = None,
    ) -> Int:
        from poop.types.int import Int

        return Int(
            self._value.rindex(
                _needle(sub, "rindex"),
                a_bound(start, "rindex", "start"),
                a_bound(end, "rindex", "end"),
            )
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


cloak(Str, "str")
