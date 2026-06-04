from __future__ import annotations

import xml.etree.ElementTree as _ET
from typing import Any, ClassVar

from poop.types._bridge import _str_str_dict
from poop.types.bytes import Bytes
from poop.types.dict import Dict
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import NoneClass, none
from poop.types.object import Object
from poop.types.string import Str


def _unwrap_attrib(attrib: Dict | None) -> dict[str, str]:
    if attrib is None:
        return {}
    result: dict[str, str] = {}
    # We iterate keys directly; values are POOP Str.
    for key in attrib.keys():
        val = attrib.at(key)
        if not isinstance(key, Str) or not isinstance(val, Str):
            raise TypeError("Element attrib must be Dict[Str, Str]")
        result[key._value] = val._value
    return result


class Element(Object):
    """Wraps Python's `xml.etree.ElementTree.Element`."""

    __slots__ = ("_impl",)

    def __init__(
        self,
        tag: Str | Any,
        attrib: Dict | None = None,
        **extra: Any,
    ) -> None:
        if isinstance(tag, Str):
            self._impl = _ET.Element(tag._value, _unwrap_attrib(attrib))
        else:
            self._impl = tag

    @property
    def tag(self) -> Str:
        return Str(self._impl.tag)

    @property
    def text(self) -> Str | NoneClass:
        return Str(self._impl.text) if self._impl.text is not None else none

    @text.setter
    def text(self, value: Str | NoneClass) -> None:
        self._impl.text = None if isinstance(value, NoneClass) else value._value

    @property
    def tail(self) -> Str | NoneClass:
        return Str(self._impl.tail) if self._impl.tail is not None else none

    @tail.setter
    def tail(self, value: Str | NoneClass) -> None:
        self._impl.tail = None if isinstance(value, NoneClass) else value._value

    @property
    def attrib(self) -> Dict:
        return _str_str_dict(self._impl.attrib.items())

    def get(self, key: Str, default: Str | NoneClass | None = None) -> Str | NoneClass:
        if default is None or isinstance(default, NoneClass):
            val = self._impl.get(key._value)
        else:
            val = self._impl.get(key._value, default._value)
        if val is None:
            return none
        return Str(val)

    def set(self, key: Str, value: Str) -> NoneClass:
        self._impl.set(key._value, value._value)
        return none

    def keys(self) -> List:
        return List(*(Str(k) for k in self._impl.keys()))

    def items(self) -> List:
        from poop.types.tuple import Tuple

        return List(*(Tuple(Str(k), Str(v)) for k, v in self._impl.items()))

    def append(self, child: Element) -> NoneClass:
        self._impl.append(child._impl)
        return none

    def extend(self, children: List) -> NoneClass:
        for child in children:
            if not isinstance(child, Element):
                raise TypeError("Element.extend expects List[Element]")
            self._impl.append(child._impl)
        return none

    def insert(self, index: Int, child: Element) -> NoneClass:
        self._impl.insert(index._value, child._impl)
        return none

    def remove(self, child: Element) -> NoneClass:
        self._impl.remove(child._impl)
        return none

    def clear(self) -> NoneClass:
        self._impl.clear()
        return none

    def find(self, path: Str) -> Element | NoneClass:
        result = self._impl.find(path._value)
        return none if result is None else Element(result)

    def findall(self, path: Str) -> List:
        return List(*(Element(e) for e in self._impl.findall(path._value)))

    def findtext(
        self, path: Str, default: Str | NoneClass | None = None
    ) -> Str | NoneClass:
        if default is None or isinstance(default, NoneClass):
            result = self._impl.findtext(path._value)
        else:
            result = self._impl.findtext(path._value, default._value)
        if result is None:
            return none
        return Str(result)

    def iter(self, tag: Str | NoneClass | None = None) -> List:
        if tag is None or isinstance(tag, NoneClass):
            return List(*(Element(e) for e in self._impl.iter()))
        return List(*(Element(e) for e in self._impl.iter(tag._value)))

    def iterfind(self, path: Str) -> List:
        return List(*(Element(e) for e in self._impl.iterfind(path._value)))

    def itertext(self) -> List:
        return List(*(Str(t) for t in self._impl.itertext()))

    def len(self) -> Int:
        return Int(len(self._impl))

    def __iter__(self) -> Any:
        for child in self._impl:
            yield Element(child)

    def __str__(self) -> str:
        return _ET.tostring(self._impl, encoding="unicode")

    __repr__ = __str__


class ElementTree(Object):
    """Wraps Python's `xml.etree.ElementTree.ElementTree`."""

    __slots__ = ("_impl",)

    def __init__(self, element: Element | Any | None = None) -> None:
        if element is None or isinstance(element, NoneClass):
            self._impl = _ET.ElementTree()
        elif isinstance(element, Element):
            self._impl = _ET.ElementTree(element._impl)
        else:
            self._impl = element

    def getroot(self) -> Element | NoneClass:
        root = self._impl.getroot()
        return none if root is None else Element(root)

    def write(self, path: Str, encoding: Str | None = None) -> NoneClass:
        enc = "us-ascii" if encoding is None else encoding._value
        self._impl.write(path._value, encoding=enc)
        return none

    def find(self, path: Str) -> Element | NoneClass:
        result = self._impl.find(path._value)
        return none if result is None else Element(result)

    def findall(self, path: Str) -> List:
        return List(*(Element(e) for e in self._impl.findall(path._value)))

    def findtext(
        self, path: Str, default: Str | NoneClass | None = None
    ) -> Str | NoneClass:
        if default is None or isinstance(default, NoneClass):
            result = self._impl.findtext(path._value)
        else:
            result = self._impl.findtext(path._value, default._value)
        if result is None:
            return none
        return Str(result)

    def iter(self, tag: Str | NoneClass | None = None) -> List:
        if tag is None or isinstance(tag, NoneClass):
            return List(*(Element(e) for e in self._impl.iter()))
        return List(*(Element(e) for e in self._impl.iter(tag._value)))


class ET:
    """Namespace mirroring Python's `xml.etree.ElementTree` module."""

    Element: ClassVar[type[Element]] = Element
    ElementTree: ClassVar[type[ElementTree]] = ElementTree
    ParseError: ClassVar[type[BaseException]] = _ET.ParseError

    @staticmethod
    def fromstring(text: Str) -> Element:
        return Element(_ET.fromstring(text._value))  # noqa: S314

    @staticmethod
    def XML(text: Str) -> Element:
        return Element(_ET.XML(text._value))  # noqa: S314

    @staticmethod
    def tostring(element: Element, encoding: Str | None = None) -> Str | Bytes:
        if encoding is None:
            return Str(_ET.tostring(element._impl, encoding="unicode"))
        if encoding._value == "unicode":
            return Str(_ET.tostring(element._impl, encoding="unicode"))
        return Bytes(_ET.tostring(element._impl, encoding=encoding._value))

    @staticmethod
    def parse(source: Str) -> ElementTree:
        return ElementTree(_ET.parse(source._value))  # noqa: S314

    @staticmethod
    def indent(tree: ElementTree | Element, space: Str | None = None) -> NoneClass:
        sp = "  " if space is None else space._value
        if isinstance(tree, ElementTree):
            _ET.indent(tree._impl, space=sp)
        else:
            _ET.indent(tree._impl, space=sp)
        return none

    @staticmethod
    def SubElement(parent: Element, tag: Str, attrib: Dict | None = None) -> Element:
        return Element(_ET.SubElement(parent._impl, tag._value, _unwrap_attrib(attrib)))


class XML:
    """Namespace mirroring Python's `xml` package — ElementTree-focused.

    The full `xml.dom` / `xml.sax` surface is intentionally out of scope.
    """

    etree: ClassVar[type[ET]] = ET
    ET: ClassVar[type[ET]] = ET
