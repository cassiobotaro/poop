from __future__ import annotations

import html as _html
import html.entities as _html_entities
import html.parser as _html_parser
from typing import ClassVar

from poop.types._bridge import _str_str_dict
from poop.types.boolean import Boolean, to_boolean
from poop.types.dict import Dict
from poop.types.int import Int
from poop.types.list import List
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


class Entities:
    """Namespace mirroring Python's `html.entities` — named/numeric entity maps.

    Exposed as class attributes to match CPython's `html.entities.<name>`
    access shape: `Entities.name2codepoint` reads the dict, not calls it.
    """

    name2codepoint: ClassVar[Dict] = _name2cp_dict()
    codepoint2name: ClassVar[Dict] = _cp2name_dict()
    entitydefs: ClassVar[Dict] = _str_str_dict(_html_entities.entitydefs.items())
    html5: ClassVar[Dict] = _str_str_dict(_html_entities.html5.items())


def _attrs_to_poop(attrs: list[tuple[str, str | None]]) -> List:
    """Wrap a CPython attribute list as a POOP List of (name, value) tuples,
    with a missing value (`<input disabled>`) as POOP `none`."""
    return List(
        *[
            Tuple(Str(name), none if value is None else Str(value))
            for name, value in attrs
        ]
    )


class _BridgedHTMLParser(_html_parser.HTMLParser):
    """Inner parser that routes raw SAX events back to the POOP wrapper.

    CPython's HTMLParser fires ``handle_*`` on *itself*, so a POOP user's
    override would otherwise sit unused on the wrapper. This subclass forwards
    each event to the owning POOP `HTMLParser` (or user subclass) with
    POOP-wrapped arguments, making the override surface live.
    """

    def __init__(self, owner: HTMLParser, *, convert_charrefs: bool) -> None:
        super().__init__(convert_charrefs=convert_charrefs)
        self._owner = owner

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._owner.handle_starttag(Str(tag), _attrs_to_poop(attrs))

    def handle_endtag(self, tag: str) -> None:
        self._owner.handle_endtag(Str(tag))

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._owner.handle_startendtag(Str(tag), _attrs_to_poop(attrs))

    def handle_data(self, data: str) -> None:
        self._owner.handle_data(Str(data))

    def handle_comment(self, data: str) -> None:
        self._owner.handle_comment(Str(data))

    def handle_decl(self, decl: str) -> None:
        self._owner.handle_decl(Str(decl))

    def handle_pi(self, data: str) -> None:
        self._owner.handle_pi(Str(data))

    def handle_entityref(self, name: str) -> None:
        self._owner.handle_entityref(Str(name))

    def handle_charref(self, name: str) -> None:
        self._owner.handle_charref(Str(name))

    def unknown_decl(self, data: str) -> None:
        self._owner.unknown_decl(Str(data))


class HTMLParser(Object):
    """Wraps Python's `html.parser.HTMLParser` — SAX-style HTML parser.

    Subclass it and override the `handle_*` messages to receive parse events;
    each argument arrives as a POOP value (`Str`, or a `List` of
    `(Str, Str|none)` tuples for attributes).
    """

    __slots__ = ("_impl",)

    def __init__(self, convert_charrefs: Boolean | None = None) -> None:
        flag = True if convert_charrefs is None else bool(convert_charrefs)
        self._impl = _BridgedHTMLParser(self, convert_charrefs=flag)

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

    # Overridable SAX handlers. Defaults are no-ops; handle_startendtag
    # mirrors CPython by delegating to handle_starttag + handle_endtag so a
    # subclass overriding only handle_starttag still sees self-closing tags.
    def handle_starttag(self, tag: Str, attrs: List) -> NoneClass:
        return none

    def handle_endtag(self, tag: Str) -> NoneClass:
        return none

    def handle_startendtag(self, tag: Str, attrs: List) -> NoneClass:
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)
        return none

    def handle_data(self, data: Str) -> NoneClass:
        return none

    def handle_comment(self, data: Str) -> NoneClass:
        return none

    def handle_decl(self, decl: Str) -> NoneClass:
        return none

    def handle_pi(self, data: Str) -> NoneClass:
        return none

    def handle_entityref(self, name: Str) -> NoneClass:
        return none

    def handle_charref(self, name: Str) -> NoneClass:
        return none

    def unknown_decl(self, data: Str) -> NoneClass:
        return none


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
        return to_boolean(name._value in _html_entities.entitydefs)
