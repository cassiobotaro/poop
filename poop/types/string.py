import builtins
import re
from string import Formatter as _Formatter
from typing import TYPE_CHECKING, Any, ClassVar

from poop.types._affix import affix_needle
from poop.types._argument import (
    a_bound,
    a_collection,
    a_fill,
    a_needle,
    an_int,
    max_split,
    text_like,
)
from poop.types._at import at_index
from poop.types._cloak import cloak
from poop.types._codec import encoded
from poop.types._iterable_mixin import _IterableMixin
from poop.types._message import article, no_format_spec
from poop.types._minmax import _minmax
from poop.types._ordered import _OrderedMixin
from poop.types._raw import _faithful
from poop.types._repeat import _repeat_count
from poop.types._sentinel import MISSING, NOT_A_COUNT
from poop.types._unwrap import _is_absent, _opt_str, _unwrap_bool
from poop.types._value_eq import _ValueEqMixin
from poop.types.boolean import to_boolean
from poop.types.exceptions import MIRRORS, PoopExcMeta
from poop.types.int import Int
from poop.types.list import List
from poop.types.object import Object
from poop.types.slice import _resolve_py_slice
from poop.types.str_iterator import StrIterator
from poop.types.tuple import Tuple

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator

    from poop.types._index import Index
    from poop.types.boolean import Boolean
    from poop.types.bytes import Bytes
    from poop.types.none import NoneClass
    from poop.types.slice import Slice


# `Unknown format code 'd' for object of type 'str'`.
_UNKNOWN_CODE = re.compile(r"^Unknown format code '(.+?)' for object of type '(.+?)'$")
# The sibling shape, which no path worded: a spec CPython cannot parse at all,
# rather than one it parsed and the receiver would not take.
_BAD_SPEC = re.compile(r"^Invalid format specifier '(.*?)' for object of type '(.+?)'$")
# The `TypeError` half, leaking the other way. `Object.format` catches this one
# and composes POOP's sentence; the template path let it through, naming a
# dunder `no_dunder_attribute` will not let a program spell.
_NO_SPEC = re.compile(r"^unsupported format string passed to (.+?)\.__format__$")


def _reject_field_access(template: str) -> None:
    """Refuse `{0.attr}` / `{0[key]}` — a format field is not an escape hatch.

    `str.format` reads attributes and items at *runtime*, from inside a string
    literal no validator can read, so `"{0.__class__}".format(5)` printed
    `<class 'int'>` — reopening exactly what `no_dunder_attribute` closes, and
    `{0[0]}` what `no_subscript` closes. This is the third half of the same
    ban, alongside `_reject_dunder`: both guard a spelling that reaches
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


def _offered(named: dict[str, object]) -> str:
    """`: a, b` — the names a template could have used, or nothing."""
    return f": {', '.join(sorted(named))}" if named else " it"


def _template_refusal(exc: ValueError | TypeError) -> Exception:
    """POOP's wording for the failures a format spec raises.

    `Unknown format code 'd' for object of type 'str'` names a "format code"
    and an "object of type" — the type-level protocol `_message.py` rewrites
    everywhere else. The brace errors are the template parser's own and say
    `format string`, which is Python's name for what POOP calls a template.

    Shared by both spellings POOP offers. `Str.format` is the template surface
    and reached this; `Object.format` is the substitute `no_format` *names*, and
    it reached CPython — so `"{0:d}".format(2.5)` answered `a float cannot be
    formatted with 'd'` while `(2.5).format("d")` answered `Unknown format code
    'd' for object of type 'float'`. Same value, same code, same failure, and
    the leaking half was the one a validator sends the reader to.

    `Invalid format specifier` leaked on *both*, because the fallback below only
    rewrites `format string` and that sentence contains neither brace wording
    nor a format code. The `TypeError` leaked the other way — `Object.format`
    worded it and the template path did not — so the shared sentence lives in
    `no_format_spec` and both call sites compose it from there.
    """
    # POOP's own refusal — `_reject_field_access`'s — passes through
    # untouched, on the test `reword_if_native` uses for the same reason.
    if isinstance(type(exc), PoopExcMeta):
        return exc
    text = str(exc)
    match = _UNKNOWN_CODE.match(text)
    if match is not None:
        code, kind = match.groups()
        return MIRRORS["ValueError"](
            f"{article(kind)} cannot be formatted with {code!r}"
        )
    match = _BAD_SPEC.match(text)
    if match is not None:
        spec, kind = match.groups()
        return MIRRORS["ValueError"](
            f"{spec!r} is not a format spec {article(kind)} understands"
        )
    match = _NO_SPEC.match(text)
    if match is not None:
        return MIRRORS["TypeError"](no_format_spec(match.group(1)))
    return MIRRORS["ValueError"](text.replace("format string", "template"))


def _opt_text(chars: object, selector: str) -> Any:
    """The optional `chars` of the strip family, or POOP's refusal.

    CPython names the message as a bare word and its own default in one breath
    — `strip arg must be None or str` — where `None` is a value POOP spells
    `none` and "arg" is not a word the language uses.
    """
    if _is_absent(chars):
        return None
    return text_like(chars, selector, "a str", (str,))


class Str(_OrderedMixin, _ValueEqMixin, _IterableMixin, Object):
    """A string, and a collection like any other.

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

    def __init__(self, value: str | Str) -> None:
        self._value = value._value if isinstance(value, Str) else value

    def len(self) -> Int:
        return Int(len(self._value))

    def __len__(self) -> int:
        return len(self._value)

    def ord(self) -> Int:
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
        raise MIRRORS["TypeError"](
            "str cannot be summed — send #join to a list of pieces instead"
        )

    def min(
        self,
        *,
        key: Callable[[Str], Any] | NoneClass | None = None,
        default: Any = MISSING,
    ) -> Any:
        return _minmax(builtins.min, "#min", self, key, default)

    def max(
        self,
        *,
        key: Callable[[Str], Any] | NoneClass | None = None,
        default: Any = MISSING,
    ) -> Any:
        return _minmax(builtins.max, "#max", self, key, default)

    def includes(self, char: Str) -> Boolean:
        # `includes` is the substitute `no_in` points at, and its own refusal
        # quoted the banned operator in its Python spelling: `'in <string>'
        # requires string as left operand, not int`.
        operand: Any = text_like(char, "includes", "a str", (str,))
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
        return Str(self._value.strip(_opt_text(chars, "strip")))

    def lstrip(self, chars: Str | NoneClass | None = None) -> Str:
        return Str(self._value.lstrip(_opt_text(chars, "lstrip")))

    def rstrip(self, chars: Str | NoneClass | None = None) -> Str:
        return Str(self._value.rstrip(_opt_text(chars, "rstrip")))

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
                an_int(count, "replace", "count", -1),
            )
        )

    def split(
        self,
        sep: Str | NoneClass | None = None,
        maxsplit: Int | NoneClass | None = None,
    ) -> List:
        return List(
            *(
                Str(p)
                for p in self._value.split(
                    _opt_text(sep, "split"), max_split(maxsplit, "split")
                )
            )
        )

    def join(self, parts: List) -> Str:
        # Mirror CPython: unwrap each element to its underlying value and let
        # str.join validate. Str parts join cleanly; anything else (Int,
        # Bytes, ...) reaches str.join unwrapped and raises the faithful
        # TypeError instead of being silently stringified via str(p).
        pieces: list[Any] = [_faithful(p) for p in a_collection(parts, "join")]
        return Str(self._value.join(pieces))

    def format(self, *args: Object, **kwargs: Object) -> Str:
        # CPython's str.format template substitution. Overrides the
        # inherited Object.format(spec); f-strings are forbidden, so this
        # is POOP's documented template-formatting surface. The rare
        # "apply a spec to a string" case stays expressible as
        # "{:^10}".format(s).
        # circular: _bridge imports string
        from poop.types._bridge import to_python  # noqa: PLC0415

        positional = [to_python(a) for a in args]
        named = {k: to_python(v) for k, v in kwargs.items()}
        try:
            # Inside the guard: the unmatched-brace errors are raised by the
            # template parser this runs, not by `format` below.
            _reject_field_access(self._value)
            return Str(self._value.format(*positional, **named))
        except KeyError as exc:
            # A bare repr with nothing to say a lookup failed — the shape
            # `_at.py` was written to close for a missing dict key.
            raise MIRRORS["KeyError"](
                f"the template asks for {exc.args[0]!r}, "
                f"which no argument named{_offered(named)}"
            ) from None
        except IndexError:
            # `Replacement index 0 out of range for positional args tuple`
            # describes Python's calling convention, for a message whose
            # arguments POOP does not describe that way.
            raise MIRRORS["IndexError"](
                f"the template asks for more than the {len(positional)} "
                f"{'value' if len(positional) == 1 else 'values'} it was given"
            ) from None
        except ValueError as exc:
            raise _template_refusal(exc) from None
        except TypeError as exc:
            # The `TypeError` half, and the one that leaks *out* of the
            # template rather than into it: a receiver that takes no spec at
            # all answered `unsupported format string passed to
            # list.__format__` — a dunder `no_dunder_attribute` will not let a
            # program spell, from a construct the reader wrote with braces.
            # `Object.format` has composed POOP's sentence for this since it
            # was written; both now compose it from `no_format_spec`.
            raise _template_refusal(exc) from None

    def _search(
        self,
        method: Callable[..., int],
        selector: str,
        sub: object,
        start: Int | NoneClass | None,
        end: Int | NoneClass | None,
    ) -> Int:
        """`find` and its four siblings: one guarded call to the native method.

        The bound method rather than a name to `getattr`, so a misspelt
        selector cannot reach the wrong native method.
        """
        return Int(
            method(
                a_needle(self, sub, selector, "a str"),
                a_bound(start, selector, "start"),
                a_bound(end, selector, "end"),
            )
        )

    def _affix(
        self,
        method: Callable[..., bool],
        selector: str,
        affix: object,
        start: Int | NoneClass | None,
        end: Int | NoneClass | None,
    ) -> Boolean:
        """`startswith` / `endswith`, guarded the way `_search` is."""
        return to_boolean(
            method(
                affix_needle(affix, selector, "a str or a tuple of str", (str,)),
                a_bound(start, selector, "start"),
                a_bound(end, selector, "end"),
            )
        )

    def find(
        self,
        sub: Str,
        start: Int | NoneClass | None = None,
        end: Int | NoneClass | None = None,
    ) -> Int:
        return self._search(self._value.find, "find", sub, start, end)

    def index(
        self,
        sub: Str,
        start: Int | NoneClass | None = None,
        end: Int | NoneClass | None = None,
    ) -> Int:
        return self._search(self._value.index, "index", sub, start, end)

    def count(
        self,
        sub: Str,
        start: Int | NoneClass | None = None,
        end: Int | NoneClass | None = None,
    ) -> Int:
        return self._search(self._value.count, "count", sub, start, end)

    def startswith(
        self,
        prefix: Str | Tuple,
        start: Int | NoneClass | None = None,
        end: Int | NoneClass | None = None,
    ) -> Boolean:
        return self._affix(self._value.startswith, "startswith", prefix, start, end)

    def endswith(
        self,
        suffix: Str | Tuple,
        start: Int | NoneClass | None = None,
        end: Int | NoneClass | None = None,
    ) -> Boolean:
        return self._affix(self._value.endswith, "endswith", suffix, start, end)

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
        w = an_int(width, "center", "width")
        fill = a_fill(fillchar, "center", "one character", (str,))
        return Str(
            self._value.center(w) if fill is None else self._value.center(w, fill)
        )

    def encode(
        self,
        encoding: Str | NoneClass | None = None,
        errors: Str | NoneClass | None = None,
    ) -> Bytes:
        # circular: bytes imports string
        from poop.types.bytes import Bytes  # noqa: PLC0415

        return Bytes(
            encoded(
                self._value,
                _opt_str(encoding, "utf-8"),
                _opt_str(errors, "strict"),
            )
        )

    def expandtabs(self, tabsize: Int | NoneClass | None = None) -> Str:
        return Str(self._value.expandtabs(an_int(tabsize, "expandtabs", "tabsize", 8)))

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
        w = an_int(width, "ljust", "width")
        fill = a_fill(fillchar, "ljust", "one character", (str,))
        return Str(self._value.ljust(w) if fill is None else self._value.ljust(w, fill))

    def rjust(self, width: Int, fillchar: Str | NoneClass | None = None) -> Str:
        w = an_int(width, "rjust", "width")
        fill = a_fill(fillchar, "rjust", "one character", (str,))
        return Str(self._value.rjust(w) if fill is None else self._value.rjust(w, fill))

    def zfill(self, width: Int) -> Str:
        return Str(self._value.zfill(an_int(width, "zfill", "width")))

    def partition(self, sep: Str) -> Tuple:
        return Tuple(
            *[
                Str(s)
                for s in self._value.partition(
                    text_like(sep, "partition", "a str", (str,))
                )
            ]
        )

    def rpartition(self, sep: Str) -> Tuple:
        return Tuple(
            *[
                Str(s)
                for s in self._value.rpartition(
                    text_like(sep, "rpartition", "a str", (str,))
                )
            ]
        )

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
        return self._search(self._value.rfind, "rfind", sub, start, end)

    def rindex(
        self,
        sub: Str,
        start: Int | NoneClass | None = None,
        end: Int | NoneClass | None = None,
    ) -> Int:
        return self._search(self._value.rindex, "rindex", sub, start, end)

    def rsplit(
        self,
        sep: Str | NoneClass | None = None,
        maxsplit: Int | NoneClass | None = None,
    ) -> List:
        return List(
            *(
                Str(s)
                for s in self._value.rsplit(
                    _opt_text(sep, "rsplit"), max_split(maxsplit, "rsplit")
                )
            )
        )

    def splitlines(self, keepends: Boolean | NoneClass | None = None) -> List:
        return List(
            *[Str(s) for s in self._value.splitlines(_unwrap_bool(keepends, False))]
        )

    def __add__(self, other: object) -> Str:
        if not isinstance(other, Str):
            return NotImplemented  # foreign operand -> faithful TypeError
        return Str(self._value + other._value)

    def __mul__(self, other: object) -> Str:
        count = _repeat_count(other)
        if count is NOT_A_COUNT:
            return NotImplemented
        return Str(self._value * count)

    __rmul__ = __mul__

    def __hash__(self) -> int:
        return hash(self._value)

    def __str__(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return repr(self._value)


cloak(Str, "str")
