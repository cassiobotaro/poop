from __future__ import annotations

import html as _html
import html.entities as _html_entities
import html.parser as _html_parser
from typing import Any, ClassVar

from poop.types.boolean import Boolean, false, true
from poop.types.dict import Dict
from poop.types.int import Int
from poop.types.none import NoneClass, none
from poop.types.object import Object
from poop.types.string import Str
from poop.types.tuple import Tuple


def _name2cp_dict() -> Dict:
    d = Dict()
    for k, v in _html_entities.name2codepoint.items():
        d.at_put(Str(k), Int(v))
    return d


def _cp2name_dict() -> Dict:
    d = Dict()
    for k, v in _html_entities.codepoint2name.items():
        d.at_put(Int(k), Str(v))
    return d


def _entitydefs_dict() -> Dict:
    d = Dict()
    for k, v in _html_entities.entitydefs.items():
        d.at_put(Str(k), Str(v))
    return d


def _html5_dict() -> Dict:
    d = Dict()
    for k, v in _html_entities.html5.items():
        d.at_put(Str(k), Str(v))
    return d


class Entities:
    """Namespace mirroring Python's `html.entities` — named/numeric entity maps.

    Exposed as class attributes to match CPython's `html.entities.<name>`
    access shape: `Entities.name2codepoint` reads the dict, not calls it.
    """

    name2codepoint: ClassVar[Dict] = _name2cp_dict()
    codepoint2name: ClassVar[Dict] = _cp2name_dict()
    entitydefs: ClassVar[Dict] = _entitydefs_dict()
    html5: ClassVar[Dict] = _html5_dict()


class HTMLParser(Object):
    """Wraps Python's `html.parser.HTMLParser` — SAX-style HTML parser."""

    __slots__ = ("_impl",)

    def __init__(self, convert_charrefs: Boolean | None = None) -> None:
        flag = True if convert_charrefs is None else bool(convert_charrefs)
        self._impl = _html_parser.HTMLParser(convert_charrefs=flag)

    def feed(self, data: Str) -> NoneClass:
        self._impl.feed(data._value)
        return none

    def close(self) -> NoneClass:
        self._impl.close()
        return none

    def reset(self) -> NoneClass:
        self._impl.reset()
        return none

    def getpos(self) -> Tuple:
        line, offset = self._impl.getpos()
        return Tuple(Int(line), Int(offset))

    def get_starttag_text(self) -> Str | NoneClass:
        text = self._impl.get_starttag_text()
        return none if text is None else Str(text)

    def _impl_ref(self) -> Any:
        return self._impl


class HTML:
    """Namespace mirroring Python's `html` package."""

    entities: ClassVar[type[Entities]] = Entities
    parser: ClassVar[type[HTMLParser]] = HTMLParser

    @staticmethod
    def escape(s: Str, quote: Boolean | None = None) -> Str:
        flag = True if quote is None else bool(quote)
        return Str(_html.escape(s._value, quote=flag))

    @staticmethod
    def unescape(s: Str) -> Str:
        return Str(_html.unescape(s._value))

    @staticmethod
    def has_entity(name: Str) -> Boolean:
        return true if name._value in _html_entities.entitydefs else false
