import textwrap as _textwrap
from collections.abc import Callable
from typing import Any

from poop.types._bridge import bridge
from poop.types._unwrap import _b
from poop.types.boolean import Boolean, false, true
from poop.types.int import Int
from poop.types.list import List
from poop.types.string import Str


def _i(value: Int | None, default: int) -> int:
    return default if value is None else value._value


def _opt_i(value: Int | None) -> int | None:
    return None if value is None else value._value


def _opt_s(value: Str | None, default: str | None) -> str | None:
    return default if value is None else value._value


def _wrap_lines(lines: list[str]) -> List:
    return List(*(Str(s) for s in lines))


class TextWrapper:
    """Wraps Python's `textwrap.TextWrapper` for reusable wrapping.

    Construction takes the full set of knobs from CPython
    (`width`, `initial_indent`, `subsequent_indent`, `expand_tabs`,
    `replace_whitespace`, `drop_whitespace`, `fix_sentence_endings`,
    `break_long_words`, `break_on_hyphens`, `tabsize`, `max_lines`,
    `placeholder`). Methods `wrap` and `fill` mirror the module-level
    shortcuts but reuse the configured instance.
    """

    __slots__ = ("_impl",)

    def __init__(
        self,
        width: Int | None = None,
        initial_indent: Str | None = None,
        subsequent_indent: Str | None = None,
        expand_tabs: Boolean | None = None,
        replace_whitespace: Boolean | None = None,
        drop_whitespace: Boolean | None = None,
        fix_sentence_endings: Boolean | None = None,
        break_long_words: Boolean | None = None,
        break_on_hyphens: Boolean | None = None,
        tabsize: Int | None = None,
        max_lines: Int | None = None,
        placeholder: Str | None = None,
    ) -> None:
        self._impl = _textwrap.TextWrapper(
            width=_i(width, 70),
            initial_indent=_opt_s(initial_indent, "") or "",
            subsequent_indent=_opt_s(subsequent_indent, "") or "",
            expand_tabs=_b(expand_tabs, True),
            replace_whitespace=_b(replace_whitespace, True),
            drop_whitespace=_b(drop_whitespace, True),
            fix_sentence_endings=_b(fix_sentence_endings, False),
            break_long_words=_b(break_long_words, True),
            break_on_hyphens=_b(break_on_hyphens, True),
            tabsize=_i(tabsize, 8),
            max_lines=_opt_i(max_lines),
            placeholder=_opt_s(placeholder, " [...]") or " [...]",
        )

    def wrap(self, text: Str) -> List:
        return _wrap_lines(self._impl.wrap(text._value))

    def fill(self, text: Str) -> Str:
        return Str(self._impl.fill(text._value))


class Textwrap:
    """Namespace mirroring Python's `textwrap` module.

    Module-level shortcuts (`wrap`, `fill`, `shorten`, `indent`,
    `dedent`); the reusable `TextWrapper` class is exposed alongside
    this namespace for callers that need to keep configuration.
    """

    @staticmethod
    def wrap(
        text: Str,
        width: Int = Int(70),
        *,
        initial_indent: Str = Str(""),
        subsequent_indent: Str = Str(""),
        expand_tabs: Boolean = true,
        replace_whitespace: Boolean = true,
        drop_whitespace: Boolean = true,
        fix_sentence_endings: Boolean = false,
        break_long_words: Boolean = true,
        break_on_hyphens: Boolean = true,
        tabsize: Int = Int(8),
        max_lines: Int | None = None,
        placeholder: Str = Str(" [...]"),
    ) -> List:
        return _wrap_lines(
            _textwrap.wrap(
                text._value,
                width=width._value,
                initial_indent=initial_indent._value,
                subsequent_indent=subsequent_indent._value,
                expand_tabs=bool(expand_tabs),
                replace_whitespace=bool(replace_whitespace),
                drop_whitespace=bool(drop_whitespace),
                fix_sentence_endings=bool(fix_sentence_endings),
                break_long_words=bool(break_long_words),
                break_on_hyphens=bool(break_on_hyphens),
                tabsize=tabsize._value,
                max_lines=_opt_i(max_lines),
                placeholder=placeholder._value,
            )
        )

    @staticmethod
    def fill(
        text: Str,
        width: Int = Int(70),
        *,
        initial_indent: Str = Str(""),
        subsequent_indent: Str = Str(""),
        expand_tabs: Boolean = true,
        replace_whitespace: Boolean = true,
        drop_whitespace: Boolean = true,
        fix_sentence_endings: Boolean = false,
        break_long_words: Boolean = true,
        break_on_hyphens: Boolean = true,
        tabsize: Int = Int(8),
        max_lines: Int | None = None,
        placeholder: Str = Str(" [...]"),
    ) -> Str:
        return Str(
            _textwrap.fill(
                text._value,
                width=width._value,
                initial_indent=initial_indent._value,
                subsequent_indent=subsequent_indent._value,
                expand_tabs=bool(expand_tabs),
                replace_whitespace=bool(replace_whitespace),
                drop_whitespace=bool(drop_whitespace),
                fix_sentence_endings=bool(fix_sentence_endings),
                break_long_words=bool(break_long_words),
                break_on_hyphens=bool(break_on_hyphens),
                tabsize=tabsize._value,
                max_lines=_opt_i(max_lines),
                placeholder=placeholder._value,
            )
        )

    @staticmethod
    def shorten(
        text: Str,
        width: Int,
        *,
        placeholder: Str = Str(" [...]"),
    ) -> Str:
        return Str(
            _textwrap.shorten(
                text._value,
                width=width._value,
                placeholder=placeholder._value,
            )
        )

    @staticmethod
    def indent(
        text: Str,
        prefix: Str,
        predicate: Callable[..., Any] | None = None,
    ) -> Str:
        return Str(
            _textwrap.indent(
                text._value,
                prefix._value,
                predicate=None if predicate is None else bridge(predicate),
            )
        )

    @staticmethod
    def dedent(text: Str) -> Str:
        return Str(_textwrap.dedent(text._value))
