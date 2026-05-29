import shlex as _shlex
from typing import Any

from poop.types._unwrap import _b
from poop.types.boolean import Boolean, to_boolean
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import NoneClass, none
from poop.types.string import Str


class Shlex:
    """Wraps Python's `shlex.shlex` lexer for streaming tokenization.

    Construction parameters mirror CPython:
    `Shlex(instream=Str | None, infile=Str | None, posix=Boolean,
           punctuation_chars=Boolean)`.

    `instream` can be a POOP `Str`; `infile` is a filename label used
    in error messages. The lexer surface kept in v1 is the common
    iterative one: `.get_token()`, `.read_token()`, the integer
    `.lineno`, and the boolean knobs `.posix` / `.whitespace_split`.
    """

    __slots__ = ("_impl",)

    def __init__(
        self,
        instream: Str | None = None,
        infile: Str | None = None,
        posix: Boolean | None = None,
        punctuation_chars: Boolean | None = None,
    ) -> None:
        self._impl = _shlex.shlex(
            instream._value if instream is not None else None,
            infile._value if infile is not None else None,
            posix=_b(posix, False),
            punctuation_chars=_b(punctuation_chars, False),
        )

    def get_token(self) -> Str | NoneClass:
        tok = self._impl.get_token()
        if tok is None or tok == self._impl.eof:
            return none
        return Str(tok)

    def __iter__(self) -> Any:
        for tok in self._impl:
            yield Str(tok)

    @property
    def lineno(self) -> Int:
        return Int(self._impl.lineno)

    @property
    def whitespace_split(self) -> Boolean:
        return to_boolean(self._impl.whitespace_split)

    @whitespace_split.setter
    def whitespace_split(self, value: Boolean) -> None:
        self._impl.whitespace_split = bool(value)

    # Extended streaming surface (CPython's full Shlex).

    def read_token(self) -> Str | NoneClass:
        tok = self._impl.read_token()
        if tok is None or tok == self._impl.eof:
            return none
        return Str(tok)

    def push_token(self, tok: Str) -> NoneClass:
        self._impl.push_token(tok._value)
        return none

    def push_source(self, newstream: Str, newfile: Str | None = None) -> NoneClass:
        nf = None if newfile is None else newfile._value
        self._impl.push_source(newstream._value, nf)
        return none

    def pop_source(self) -> NoneClass:
        self._impl.pop_source()
        return none

    def error_leader(
        self,
        infile: Str | NoneClass | None = None,
        lineno: Int | NoneClass | None = None,
    ) -> Str:
        from poop.types._unwrap import _is_absent

        ifname = None if _is_absent(infile) else infile._value  # ty: ignore[unresolved-attribute]
        lineno_val = None if _is_absent(lineno) else lineno._value  # ty: ignore[unresolved-attribute]
        return Str(self._impl.error_leader(ifname, lineno_val))

    @property
    def commenters(self) -> Str:
        return Str(self._impl.commenters)

    @commenters.setter
    def commenters(self, value: Str) -> None:
        self._impl.commenters = value._value

    @property
    def wordchars(self) -> Str:
        return Str(self._impl.wordchars)

    @wordchars.setter
    def wordchars(self, value: Str) -> None:
        self._impl.wordchars = value._value

    @property
    def whitespace(self) -> Str:
        return Str(self._impl.whitespace)

    @whitespace.setter
    def whitespace(self, value: Str) -> None:
        self._impl.whitespace = value._value

    @property
    def escape(self) -> Str:
        return Str(self._impl.escape)

    @escape.setter
    def escape(self, value: Str) -> None:
        self._impl.escape = value._value

    @property
    def quotes(self) -> Str:
        return Str(self._impl.quotes)

    @quotes.setter
    def quotes(self, value: Str) -> None:
        self._impl.quotes = value._value

    @property
    def escapedquotes(self) -> Str:
        return Str(self._impl.escapedquotes)

    @escapedquotes.setter
    def escapedquotes(self, value: Str) -> None:
        self._impl.escapedquotes = value._value

    @property
    def debug(self) -> Int:
        return Int(self._impl.debug)

    @debug.setter
    def debug(self, value: Int) -> None:
        self._impl.debug = value._value

    @property
    def token(self) -> Str:
        return Str(self._impl.token)

    @property
    def infile(self) -> Str | NoneClass:
        return Str(self._impl.infile) if self._impl.infile is not None else none

    @property
    def source(self) -> Str | NoneClass:
        return Str(self._impl.source) if self._impl.source is not None else none


class Shlex_:
    """Namespace mirroring Python's `shlex` module.

    POSIX-style shell tokenization (`split`), joining (`join`), and
    safe shell quoting (`quote`). Streaming/iterative lexing lives on
    the separate `Shlex` class, exposed alongside this namespace.
    """

    @staticmethod
    def split(
        s: Str,
        comments: Boolean | None = None,
        posix: Boolean | None = None,
    ) -> List:
        tokens = _shlex.split(
            s._value, comments=_b(comments, False), posix=_b(posix, True)
        )
        return List(*(Str(t) for t in tokens))

    @staticmethod
    def join(split_command: Any) -> Str:
        # `split_command` is typed Any because POOP `List` iteration
        # yields `Object`; the contract is "iterable of Str" at
        # runtime.
        return Str(_shlex.join(s._value for s in split_command))

    @staticmethod
    def quote(s: Str) -> Str:
        return Str(_shlex.quote(s._value))
