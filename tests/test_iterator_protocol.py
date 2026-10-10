"""Every iterator answers `#iter` with itself.

Sweeping the family is the point, as `test_cloak.py` argues for the cloak: the
gap reached fifteen classes at once, because `iter` was the one message of the
`_IterableMixin` protocol defined per class rather than on a shared base. A
per-iterator assertion says nothing about the sixteenth, and `no_iter` names
`col.iter()` as the substitute for all of them.
"""

import importlib
import inspect
import pkgutil
from typing import Any

import pytest

import poop.types
from poop.types._iterator_base import _IteratorBase
from poop.types.byte_array import ByteArray
from poop.types.bytes import Bytes
from poop.types.dict import Dict
from poop.types.enumerate import Enumerate
from poop.types.filter import Filter
from poop.types.frozen_set import FrozenSet
from poop.types.int import Int
from poop.types.list import List
from poop.types.map import Map
from poop.types.memory_view import MemoryView
from poop.types.range import Range
from poop.types.set import Set
from poop.types.string import Str
from poop.types.tuple import Tuple
from poop.types.zip import Zip


def _iterator_classes() -> list[type]:
    """Every concrete `_IteratorBase` subclass, found by walking `poop.types`.

    `__module__` cannot select them — the cloak sets it to `builtins` — so the
    base class itself is the mark, exactly as `PoopMeta` is in `test_cloak.py`.

    Concrete means "cloaked under a CPython iterator name": the shared bases
    (`_DictItemIteratorBase`) are cloaked as `object` alongside the other
    mixins, and a base has no receiver to build.
    """
    found: dict[int, type] = {}
    for info in pkgutil.iter_modules(poop.types.__path__):
        module = importlib.import_module(f"poop.types.{info.name}")
        for _, cls in inspect.getmembers(module, inspect.isclass):
            concrete = cls.__name__ != "object"
            if issubclass(cls, _IteratorBase) and concrete:
                found[id(cls)] = cls
    return sorted(found.values(), key=lambda cls: (cls.__name__, id(cls)))


def _a_dict() -> Dict:
    d = Dict()
    d.at_put(Str("a"), Int(1))
    return d


# One live receiver per iterator, labelled by the spelling that reaches it, so
# the sweep walks real iterators rather than ones built straight from a list —
# a reverse view iterator is only reachable through the view that answers it.
# Several spellings share a class, exactly as they do in CPython (`set` and
# `frozenset` both answer a `set_iterator`), so the label is the receiver.
_RECEIVERS: list[tuple[str, object]] = [
    ("list", List(Int(1)).iter()),
    ("tuple", Tuple(Int(1)).iter()),
    ("str", Str("a").iter()),
    ("bytes", Bytes(b"a").iter()),
    ("bytearray", ByteArray(bytearray(b"a")).iter()),
    ("set", Set(Int(1)).iter()),
    ("frozenset", FrozenSet(Int(1)).iter()),
    ("range", Range(Int(0), Int(1)).iter()),
    ("memoryview", MemoryView(memoryview(b"a")).iter()),
    ("dict", _a_dict().iter()),
    ("dict.keys", _a_dict().keys().iter()),
    ("dict.values", _a_dict().values().iter()),
    ("dict.items", _a_dict().items().iter()),
    ("dict.reversed", _a_dict().reversed()),
    ("dict.keys.reversed", _a_dict().keys().reversed()),
    ("dict.values.reversed", _a_dict().values().reversed()),
    ("dict.items.reversed", _a_dict().items().reversed()),
    ("enumerate", Enumerate(List(Int(1)))),
    ("zip", Zip(List(Int(1)))),
    ("map", Map(List(Int(1)), lambda x: x)),
    ("filter", Filter(List(Int(1)), lambda x: x)),
]


@pytest.mark.parametrize(
    "iterator",
    [iterator for _, iterator in _RECEIVERS],
    ids=[label for label, _ in _RECEIVERS],
)
def test_an_iterator_answers_iter_with_itself(iterator: Any) -> None:
    assert iterator.iter() is iterator


def test_the_sweep_covers_every_iterator_class() -> None:
    """The receiver list above is not allowed to fall behind the modules.

    An iterator added without a receiver here would be swept by nothing, which
    is how the gap this file closes stayed invisible: `Map` and `Zip` answered
    `iter`, so every test anyone wrote happened to pass.
    """
    covered = {type(iterator) for _, iterator in _RECEIVERS}
    assert set(_iterator_classes()) <= covered
