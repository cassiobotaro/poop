import shlex as _shlex
from typing import Any

from poop.types._unwrap import _b
from poop.types.boolean import Boolean
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
    def lineno(self) -> int:
        return self._impl.lineno

    @property
    def whitespace_split(self) -> bool:
        return self._impl.whitespace_split

    @whitespace_split.setter
    def whitespace_split(self, value: Boolean) -> None:
        self._impl.whitespace_split = bool(value)


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
