from __future__ import annotations

from typing import Any

from poop.types.boolean import Boolean, to_boolean
from poop.types.byte_array import ByteArray
from poop.types.bytes import Bytes
from poop.types.dict import Dict
from poop.types.float import Float
from poop.types.frozen_set import FrozenSet
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import NoneClass, none
from poop.types.set import Set
from poop.types.string import Str
from poop.types.tuple import Tuple


def to_python(obj: Any) -> Any:  # noqa: C901 — flat isinstance ladder, one branch per primitive/container
    if obj is none or isinstance(obj, NoneClass):
        return None
    if isinstance(obj, Boolean):
        return bool(obj)
    if isinstance(obj, (Int, Float, Str, Bytes)):
        return obj._value
    if isinstance(obj, ByteArray):
        return bytearray(obj._value)
    if isinstance(obj, List):
        return [to_python(item) for item in obj._items]
    if isinstance(obj, Tuple):
        return tuple(to_python(item) for item in obj._items)
    if isinstance(obj, Dict):
        return {to_python(k): to_python(v) for k, v in obj._data.items()}
    if isinstance(obj, Set):
        return {to_python(item) for item in obj._data}
    if isinstance(obj, FrozenSet):
        return frozenset(to_python(item) for item in obj._data)
    return obj


def to_poop(value: Any) -> Any:  # noqa: C901 — flat isinstance ladder, one branch per primitive/container
    if value is None:
        return none
    if isinstance(value, bool):
        return to_boolean(value)
    if isinstance(value, int):
        return Int(value)
    if isinstance(value, float):
        return Float(value)
    if isinstance(value, str):
        return Str(value)
    if isinstance(value, bytearray):
        return ByteArray(value)
    if isinstance(value, bytes):
        return Bytes(value)
    if isinstance(value, list):
        return List(*(to_poop(v) for v in value))
    if isinstance(value, tuple):
        return Tuple(*(to_poop(v) for v in value))
    if isinstance(value, dict):
        d = Dict()
        for k, v in value.items():
            d.at_put(Str(k) if isinstance(k, str) else to_poop(k), to_poop(v))
        return d
    if isinstance(value, set):
        return Set(*(to_poop(v) for v in value))
    if isinstance(value, frozenset):
        return FrozenSet(*(to_poop(v) for v in value))
    return value
