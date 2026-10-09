"""The two directions between a POOP value and the Python value it wraps.

One registered function per type, dispatched on the argument's class. Two
`isinstance` ladders did this before, and depended on rung order in a way
nothing stated — `bool` had to be tested before `int`, being a subclass — while
a new wrapper had to be slotted in at the right height of both. Dispatch follows
the MRO, so the most specific registration wins without anyone ordering it, and
each type's two halves sit next to each other.

Anything unregistered passes through unchanged in both directions.
"""

from functools import singledispatch
from typing import Any

from poop.types.boolean import Boolean, to_boolean
from poop.types.byte_array import ByteArray
from poop.types.bytes import Bytes
from poop.types.complex import Complex
from poop.types.dict import Dict
from poop.types.float import Float
from poop.types.frozen_dict import FrozenDict
from poop.types.frozen_set import FrozenSet
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import NoneClass, none
from poop.types.sentinel import Sentinel
from poop.types.set import Set
from poop.types.string import Str
from poop.types.tuple import Tuple


@singledispatch
def to_python(obj: object) -> Any:
    return obj


@singledispatch
def to_poop(value: object) -> Any:
    return value


@to_python.register
def _(obj: NoneClass) -> None:
    return None


@to_poop.register
def _(value: None) -> NoneClass:
    return none


@to_python.register
def _(obj: Boolean) -> bool:
    return bool(obj)


@to_poop.register
def _(value: bool) -> Boolean:
    return to_boolean(value)


# `Complex` belongs with the other scalar rungs: left wrapped it reached
# `str.format` as a POOP object, and `object.__format__` refuses every non-empty
# spec — so `"{:.2f}".format(complex(1, 2))` failed where CPython answers
# `1.00+2.00j`, naming `complex.__format__` on the way out.
@to_python.register(Int)
@to_python.register(Float)
@to_python.register(Complex)
@to_python.register(Str)
@to_python.register(Bytes)
def _(obj: Int | Float | Complex | Str | Bytes) -> Any:
    return obj._value


@to_poop.register
def _(value: int) -> Int:
    return Int(value)


@to_poop.register
def _(value: float) -> Float:
    return Float(value)


@to_poop.register
def _(value: complex) -> Complex:
    return Complex(value)


@to_poop.register
def _(value: str) -> Str:
    return Str(value)


@to_poop.register
def _(value: bytes) -> Bytes:
    return Bytes(value)


@to_python.register
def _(obj: ByteArray) -> bytearray:
    return bytearray(obj._value)


@to_poop.register
def _(value: bytearray) -> ByteArray:
    return ByteArray(value)


@to_python.register
def _(obj: List) -> list[Any]:
    return [to_python(item) for item in obj._items]


@to_poop.register
def _(value: list) -> List:
    return List(*(to_poop(v) for v in value))


@to_python.register
def _(obj: Tuple) -> tuple[Any, ...]:
    return tuple(to_python(item) for item in obj._items)


@to_poop.register
def _(value: tuple) -> Tuple:
    return Tuple(*(to_poop(v) for v in value))


@to_python.register
def _(obj: Dict) -> dict[Any, Any]:
    return {to_python(k): to_python(v) for k, v in obj._data.items()}


@to_poop.register
def _(value: dict) -> Dict:
    d = Dict()
    for k, v in value.items():
        d.at_put(to_poop(k), to_poop(v))
    return d


@to_python.register
def _(obj: FrozenDict) -> frozendict[Any, Any]:
    return frozendict({to_python(k): to_python(v) for k, v in obj._data.items()})


@to_poop.register
def _(value: frozendict) -> FrozenDict:
    return FrozenDict._wrapping({to_poop(k): to_poop(v) for k, v in value.items()})


@to_python.register
def _(obj: Set) -> set[Any]:
    return {to_python(item) for item in obj._data}


@to_poop.register
def _(value: set) -> Set:
    return Set(*(to_poop(v) for v in value))


@to_python.register
def _(obj: FrozenSet) -> frozenset[Any]:
    return frozenset(to_python(item) for item in obj._data)


@to_poop.register
def _(value: frozenset) -> FrozenSet:
    return FrozenSet(*(to_poop(v) for v in value))


@to_python.register
def _(obj: Sentinel) -> sentinel:
    return sentinel(str(obj._name), repr=str(obj._repr))


@to_poop.register
def _(value: sentinel) -> Sentinel:
    # A native sentinel exposes nothing but its repr, which is its name unless
    # one was given — so the repr is the name here.
    return Sentinel(Str(repr(value)))
