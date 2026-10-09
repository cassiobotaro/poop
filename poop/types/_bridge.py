"""The two directions between a POOP value and the Python value it wraps.

One registered function per type, dispatched on the argument's class. Two
`isinstance` ladders did this before, and depended on rung order in a way
nothing stated — `bool` had to be tested before `int`, being a subclass — while
a new wrapper had to be slotted in at the right height of both. Dispatch follows
the MRO, so the most specific registration wins without anyone ordering it, and
each type's two halves sit next to each other.

Anything unregistered passes through unchanged in both directions.

`to_python` crosses *out* of the language, so `object` is its honest answer
and nothing in `poop/` reads a member of its containers back. `to_poop`
crosses *in*, and its callers depend on the answer — `Int.__pow__` is
declared `Int | Float | Complex` on its strength — so it is a public function
declared over a private dispatcher, one overload per registered native:
`singledispatch` cannot say "an `int` answers an `Int`", and the overloads can.
"""

from functools import singledispatch
from typing import overload

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
def to_python(obj: object) -> object:
    return obj


@singledispatch
def _to_poop(value: object) -> object:
    return value


# `bool` before `int` and `int` before `float`, as the natives nest: an
# argument matches the first overload that takes it.
@overload
def to_poop(value: None) -> NoneClass: ...
@overload
def to_poop(value: bool) -> Boolean: ...
@overload
def to_poop(value: int) -> Int: ...
@overload
def to_poop(value: float) -> Float: ...
@overload
def to_poop(value: complex) -> Complex: ...
@overload
def to_poop(value: str) -> Str: ...
@overload
def to_poop(value: bytes) -> Bytes: ...
@overload
def to_poop(value: bytearray) -> ByteArray: ...
@overload
def to_poop(value: list[object]) -> List: ...
@overload
def to_poop(value: tuple[object, ...]) -> Tuple: ...
@overload
def to_poop(value: dict[object, object]) -> Dict: ...
@overload
def to_poop(value: frozendict[object, object]) -> FrozenDict: ...
@overload
def to_poop(value: set[object]) -> Set: ...
@overload
def to_poop(value: frozenset[object]) -> FrozenSet: ...
@overload
def to_poop(value: sentinel) -> Sentinel: ...
@overload
def to_poop(value: object) -> object: ...
def to_poop(value: object) -> object:
    return _to_poop(value)


@to_python.register
def _(obj: NoneClass) -> None:
    return None


@_to_poop.register
def _(value: None) -> NoneClass:
    return none


@to_python.register
def _(obj: Boolean) -> bool:
    return bool(obj)


@_to_poop.register
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
def _(obj: Int | Float | Complex | Str | Bytes) -> int | float | complex | str | bytes:
    return obj._value


@_to_poop.register
def _(value: int) -> Int:
    return Int(value)


@_to_poop.register
def _(value: float) -> Float:
    return Float(value)


@_to_poop.register
def _(value: complex) -> Complex:
    return Complex(value)


@_to_poop.register
def _(value: str) -> Str:
    return Str(value)


@_to_poop.register
def _(value: bytes) -> Bytes:
    return Bytes(value)


@to_python.register
def _(obj: ByteArray) -> bytearray:
    return bytearray(obj._value)


@_to_poop.register
def _(value: bytearray) -> ByteArray:
    return ByteArray(value)


@to_python.register
def _(obj: List) -> list[object]:
    return [to_python(item) for item in obj._items]


@_to_poop.register
def _(value: list) -> List:
    return List(*(to_poop(v) for v in value))


@to_python.register
def _(obj: Tuple) -> tuple[object, ...]:
    return tuple(to_python(item) for item in obj._items)


@_to_poop.register
def _(value: tuple) -> Tuple:
    return Tuple(*(to_poop(v) for v in value))


@to_python.register
def _(obj: Dict) -> dict[object, object]:
    return {to_python(k): to_python(v) for k, v in obj._data.items()}


@_to_poop.register
def _(value: dict) -> Dict:
    d = Dict()
    for k, v in value.items():
        d.at_put(to_poop(k), to_poop(v))
    return d


@to_python.register
def _(obj: FrozenDict) -> frozendict[object, object]:
    return frozendict({to_python(k): to_python(v) for k, v in obj._data.items()})


@_to_poop.register
def _(value: frozendict) -> FrozenDict:
    return FrozenDict._wrapping({to_poop(k): to_poop(v) for k, v in value.items()})


@to_python.register
def _(obj: Set) -> set[object]:
    return {to_python(item) for item in obj._data}


@_to_poop.register
def _(value: set) -> Set:
    return Set(*(to_poop(v) for v in value))


@to_python.register
def _(obj: FrozenSet) -> frozenset[object]:
    return frozenset(to_python(item) for item in obj._data)


@_to_poop.register
def _(value: frozenset) -> FrozenSet:
    return FrozenSet(*(to_poop(v) for v in value))


@to_python.register
def _(obj: Sentinel) -> sentinel:
    return sentinel(str(obj._name), repr=str(obj._repr))


@_to_poop.register
def _(value: sentinel) -> Sentinel:
    # A native sentinel exposes nothing but its repr, which is its name unless
    # one was given — so the repr is the name here.
    return Sentinel(Str(repr(value)))
