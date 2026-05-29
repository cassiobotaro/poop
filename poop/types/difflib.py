import difflib as _difflib
from collections.abc import Callable, Iterable
from typing import Any, ClassVar

from poop.types._bridge import bridge
from poop.types._unwrap import _b, _kwargs_from
from poop.types.boolean import Boolean, false, to_boolean
from poop.types.float import Float
from poop.types.int import Int
from poop.types.list import List
from poop.types.string import Str
from poop.types.tuple import Tuple


def _str_iter(items: List) -> list[str]:
    # Iterating a POOP List yields Object; narrow to Str at the boundary.
    result: list[str] = []
    for s in items:
        if not isinstance(s, Str):
            raise TypeError(f"expected POOP Str, got {type(s).__name__}")
        result.append(s._value)
    return result


def _wrap_lines(lines: Iterable[str]) -> List:
    return List(*(Str(line) for line in lines))


def _seq_arg(value: Str | List) -> Any:
    # SequenceMatcher accepts any sequence; the two common POOP shapes
    # are Str (diff characters) and List[Str] (diff lines).
    if isinstance(value, Str):
        return value._value
    if isinstance(value, List):
        return _str_iter(value)
    raise TypeError(f"expected POOP Str or List, got {type(value).__name__}")


class SequenceMatcher:
    """Wraps Python's `difflib.SequenceMatcher`.

    Element-wise diff between two sequences (typically `Str` or
    `List[Str]`). Methods mirror CPython: `ratio`, `quick_ratio`,
    `real_quick_ratio`, `get_matching_blocks`, `get_opcodes`,
    `find_longest_match`.

    `isjunk` accepts a POOP `Block` routed through `block.bridge` —
    the block receives a POOP `Str` and returns a `Boolean` (or any
    truthy/falsy value). `autojunk` is a separate heuristic toggle.
    """

    __slots__ = ("_impl",)

    def __init__(
        self,
        a: Str | List,
        b: Str | List,
        isjunk: Callable[..., Any] | None = None,
        autojunk: Boolean | None = None,
    ) -> None:
        self._impl = _difflib.SequenceMatcher(
            None if isjunk is None else bridge(isjunk),
            _seq_arg(a),
            _seq_arg(b),
            autojunk=_b(autojunk, True),
        )

    def ratio(self) -> Float:
        return Float(self._impl.ratio())

    def quick_ratio(self) -> Float:
        return Float(self._impl.quick_ratio())

    def real_quick_ratio(self) -> Float:
        return Float(self._impl.real_quick_ratio())

    def get_matching_blocks(self) -> List:
        return List(
            *(
                Tuple(Int(m.a), Int(m.b), Int(m.size))
                for m in self._impl.get_matching_blocks()
            )
        )

    def get_opcodes(self) -> List:
        return List(
            *(
                Tuple(Str(tag), Int(i1), Int(i2), Int(j1), Int(j2))
                for tag, i1, i2, j1, j2 in self._impl.get_opcodes()
            )
        )

    def find_longest_match(
        self,
        alo: Int | None = None,
        ahi: Int | None = None,
        blo: Int | None = None,
        bhi: Int | None = None,
    ) -> Tuple:
        kwargs: dict[str, int] = {}
        kwargs.update(_kwargs_from(alo=alo, ahi=ahi, blo=blo, bhi=bhi))
        m = self._impl.find_longest_match(**kwargs)
        return Tuple(Int(m.a), Int(m.b), Int(m.size))


class Differ:
    """Wraps Python's `difflib.Differ` — `compare` between two line lists.

    Construction takes optional `linejunk` / `charjunk` `Block`s routed
    through `block.bridge`. `compare(a, b)` returns a `List[Str]` of
    marker-prefixed lines (`?`/`-`/`+`/space).
    """

    __slots__ = ("_impl",)

    def __init__(
        self,
        linejunk: Callable[..., Any] | None = None,
        charjunk: Callable[..., Any] | None = None,
    ) -> None:
        self._impl = _difflib.Differ(
            linejunk=None if linejunk is None else bridge(linejunk),
            charjunk=(
                _difflib.IS_CHARACTER_JUNK if charjunk is None else bridge(charjunk)
            ),
        )

    def compare(self, a: List, b: List) -> List:
        return _wrap_lines(self._impl.compare(_str_iter(a), _str_iter(b)))


class HtmlDiff:
    """Wraps Python's `difflib.HtmlDiff` — HTML diff renderer."""

    __slots__ = ("_impl",)

    def __init__(
        self,
        tabsize: Int | None = None,
        wrapcolumn: Int | None = None,
        linejunk: Callable[..., Any] | None = None,
        charjunk: Callable[..., Any] | None = None,
    ) -> None:
        self._impl = _difflib.HtmlDiff(
            tabsize=8 if tabsize is None else tabsize._value,
            wrapcolumn=None if wrapcolumn is None else wrapcolumn._value,
            linejunk=None if linejunk is None else bridge(linejunk),
            charjunk=(
                _difflib.IS_CHARACTER_JUNK if charjunk is None else bridge(charjunk)
            ),
        )

    def make_file(
        self,
        fromlines: List,
        tolines: List,
        fromdesc: Str | None = None,
        todesc: Str | None = None,
        context: Boolean = false,
        numlines: Int | None = None,
    ) -> Str:
        return Str(
            self._impl.make_file(
                _str_iter(fromlines),
                _str_iter(tolines),
                "" if fromdesc is None else fromdesc._value,
                "" if todesc is None else todesc._value,
                context=bool(context),
                numlines=5 if numlines is None else numlines._value,
            )
        )

    def make_table(
        self,
        fromlines: List,
        tolines: List,
        fromdesc: Str | None = None,
        todesc: Str | None = None,
        context: Boolean = false,
        numlines: Int | None = None,
    ) -> Str:
        return Str(
            self._impl.make_table(
                _str_iter(fromlines),
                _str_iter(tolines),
                "" if fromdesc is None else fromdesc._value,
                "" if todesc is None else todesc._value,
                context=bool(context),
                numlines=5 if numlines is None else numlines._value,
            )
        )


def _is_character_junk(ch: Str, ws: Str | None = None) -> Boolean:
    """Mirror of `difflib.IS_CHARACTER_JUNK` (default whitespace check)."""
    ws_arg = " \t" if ws is None else ws._value
    return to_boolean(_difflib.IS_CHARACTER_JUNK(ch._value, ws_arg))


def _is_line_junk(line: Str) -> Boolean:
    """Mirror of `difflib.IS_LINE_JUNK` (default: blank or '#'-prefixed)."""
    return to_boolean(_difflib.IS_LINE_JUNK(line._value))


class Difflib:
    """Namespace mirroring Python's `difflib` module.

    Diff producers return `List[Str]` of lines. `get_close_matches`
    does fuzzy matching against a list of candidates. The
    `SequenceMatcher` / `Differ` / `HtmlDiff` classes are exposed
    alongside this namespace for detailed diff queries.
    """

    Differ: ClassVar[type[Differ]] = Differ
    HtmlDiff: ClassVar[type[HtmlDiff]] = HtmlDiff

    IS_CHARACTER_JUNK: ClassVar[Callable[..., Boolean]] = _is_character_junk
    IS_LINE_JUNK: ClassVar[Callable[..., Boolean]] = _is_line_junk

    @staticmethod
    def unified_diff(
        a: List,
        b: List,
        fromfile: Str | None = None,
        tofile: Str | None = None,
        fromfiledate: Str | None = None,
        tofiledate: Str | None = None,
        n: Int | None = None,
        lineterm: Str | None = None,
    ) -> List:
        return _wrap_lines(
            _difflib.unified_diff(
                _str_iter(a),
                _str_iter(b),
                fromfile="" if fromfile is None else fromfile._value,
                tofile="" if tofile is None else tofile._value,
                fromfiledate="" if fromfiledate is None else fromfiledate._value,
                tofiledate="" if tofiledate is None else tofiledate._value,
                n=3 if n is None else n._value,
                lineterm="\n" if lineterm is None else lineterm._value,
            )
        )

    @staticmethod
    def context_diff(
        a: List,
        b: List,
        fromfile: Str | None = None,
        tofile: Str | None = None,
        fromfiledate: Str | None = None,
        tofiledate: Str | None = None,
        n: Int | None = None,
        lineterm: Str | None = None,
    ) -> List:
        return _wrap_lines(
            _difflib.context_diff(
                _str_iter(a),
                _str_iter(b),
                fromfile="" if fromfile is None else fromfile._value,
                tofile="" if tofile is None else tofile._value,
                fromfiledate="" if fromfiledate is None else fromfiledate._value,
                tofiledate="" if tofiledate is None else tofiledate._value,
                n=3 if n is None else n._value,
                lineterm="\n" if lineterm is None else lineterm._value,
            )
        )

    @staticmethod
    def ndiff(
        a: List,
        b: List,
        linejunk: Callable[..., Any] | None = None,
        charjunk: Callable[..., Any] | None = None,
    ) -> List:
        return _wrap_lines(
            _difflib.ndiff(
                _str_iter(a),
                _str_iter(b),
                linejunk=None if linejunk is None else bridge(linejunk),
                charjunk=(
                    _difflib.IS_CHARACTER_JUNK if charjunk is None else bridge(charjunk)
                ),
            )
        )

    @staticmethod
    def restore(seq: List, which: Int) -> List:
        return _wrap_lines(_difflib.restore(_str_iter(seq), which._value))

    @staticmethod
    def get_close_matches(
        word: Str,
        possibilities: List,
        n: Int | None = None,
        cutoff: Float | None = None,
    ) -> List:
        return _wrap_lines(
            _difflib.get_close_matches(
                word._value,
                _str_iter(possibilities),
                n=3 if n is None else n._value,
                cutoff=0.6 if cutoff is None else cutoff._value,
            )
        )
