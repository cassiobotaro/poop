from __future__ import annotations

from typing import TYPE_CHECKING, Any

from poop.types.boolean import Boolean, to_boolean
from poop.types.byte_array import ByteArray
from poop.types.bytes import Bytes
from poop.types.dict import Dict
from poop.types.float import Float
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import NoneClass, none
from poop.types.string import Str
from poop.types.tuple import Tuple

if TYPE_CHECKING:
    from collections.abc import Callable


def to_python(obj: Any) -> Any:
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
        out: dict[Any, Any] = {}
        for k, v in obj._data.items():
            out[to_python(k)] = to_python(v)
        return out
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
    return value


def bridge(
    block: Callable[..., Any],
    *,
    wrap_args: bool = True,
    unwrap_return: bool = True,
) -> Callable[..., Any]:
    """Adapt a POOP `Block` (or any callable) to a stdlib callback contract.

    Stdlib hooks expect plain Python callables that receive native
    Python arguments and return native Python values. POOP user code
    speaks POOP types. The bridge wraps each incoming arg into the
    matching POOP type via `to_poop`, invokes the block, then unwraps
    the return via `to_python` so the stdlib caller sees the type it
    asked for.

    Set `wrap_args=False` when the stdlib already hands a meaningful
    POOP-side value (or an opaque object `to_poop` would not improve).
    Set `unwrap_return=False` when the block's return value flows
    back into POOP-side code (e.g., `json.object_hook`, whose result
    becomes part of the loaded structure re-wrapped at the outer
    boundary anyway).

    Exceptions raised inside the block — whether through POOP's
    `Cls.raise_(...)` or naked CPython `raise` — propagate to the
    stdlib caller unchanged. `Try.except_` therefore keeps working
    around a bridged call.
    """

    def adapter(*args: Any, **kwargs: Any) -> Any:
        if wrap_args:
            args = tuple(to_poop(a) for a in args)
            kwargs = {k: to_poop(v) for k, v in kwargs.items()}
        result = block(*args, **kwargs)
        if unwrap_return:
            result = to_python(result)
        return result

    return adapter
