from __future__ import annotations

import io as _io
import pickle as _pickle
from typing import Any, ClassVar

from poop.types.boolean import Boolean, false, true
from poop.types.bytes import Bytes
from poop.types.dict import Dict
from poop.types.float import Float
from poop.types.frozen_set import FrozenSet
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import NoneClass, none
from poop.types.object import Object
from poop.types.path import Path
from poop.types.set import Set
from poop.types.string import Str
from poop.types.tuple import Tuple


def _opt_protocol(protocol: Int | None) -> int | None:
    return None if protocol is None else protocol._value


def _unwrap(value: Any) -> Any:
    """Recursively convert a POOP value graph into native Python.

    POOP primitive wrappers (`Int` / `Str` / `Float` / `Bytes` /
    `Boolean` / `NoneClass`) and POOP collection types (`List` /
    `Tuple` / `Dict` / `Set` / `FrozenSet`) are unwrapped to their
    Python equivalents so the underlying `pickle` can serialize them
    by reference. POOP user-class instances and anything else passes
    through untouched.
    """
    if value is none or isinstance(value, NoneClass):
        return None
    if isinstance(value, Boolean):
        return bool(value)
    if isinstance(value, Int | Float | Str | Bytes):
        return value._value
    if isinstance(value, List):
        return [_unwrap(item) for item in value._items]
    if isinstance(value, Tuple):
        return tuple(_unwrap(item) for item in value._items)
    if isinstance(value, Dict):
        return {_unwrap(k): _unwrap(v) for k, v in value._data.items()}
    if isinstance(value, Set):
        return {_unwrap(item) for item in value._data}
    if isinstance(value, FrozenSet):
        return frozenset(_unwrap(item) for item in value._data)
    return value


def _wrap(value: Any) -> Any:  # noqa: C901 — flat isinstance ladder, one branch per primitive/container
    """Recursively convert a Python value graph back into POOP."""
    if value is None:
        return none
    if isinstance(value, bool):
        return true if value else false
    if isinstance(value, int):
        return Int(value)
    if isinstance(value, float):
        return Float(value)
    if isinstance(value, str):
        return Str(value)
    if isinstance(value, bytes):
        return Bytes(value)
    if isinstance(value, list):
        return List(*(_wrap(v) for v in value))
    if isinstance(value, tuple):
        return Tuple(*(_wrap(v) for v in value))
    if isinstance(value, dict):
        d = Dict()
        for k, v in value.items():
            d.at_put(_wrap(k), _wrap(v))
        return d
    if isinstance(value, set):
        return Set(*(_wrap(v) for v in value))
    if isinstance(value, frozenset):
        return FrozenSet(*(_wrap(v) for v in value))
    return value


class Pickler(Object):
    """Wraps Python's `pickle.Pickler` over an internal byte buffer.

    Construction takes the protocol level (default `pickle.DEFAULT_PROTOCOL`);
    `.dump(obj)` appends a pickled object to the buffer, and
    `.getvalue()` returns the accumulated `Bytes`. The CPython
    file-object constructor is absent — POOP has no generic file
    abstraction, so the Pickler is in-memory by design. The
    `clear_memo` / `fast` API is exposed for parity.
    """

    __slots__ = ("_buf", "_impl")

    def __init__(self, protocol: Int | None = None) -> None:
        self._buf = _io.BytesIO()
        self._impl = _pickle.Pickler(self._buf, _opt_protocol(protocol))

    def dump(self, obj: Any) -> NoneClass:
        self._impl.dump(_unwrap(obj))
        return none

    def getvalue(self) -> Bytes:
        return Bytes(self._buf.getvalue())

    def clear_memo(self) -> NoneClass:
        self._impl.clear_memo()
        return none

    @property
    def fast(self) -> Boolean:
        # Deprecated upstream but still part of the API surface.
        return true if self._impl.fast else false

    @fast.setter
    def fast(self, value: Boolean | bool) -> None:
        self._impl.fast = bool(value)


class Unpickler(Object):
    """Wraps Python's `pickle.Unpickler` over a `Bytes` buffer.

    Construction takes the serialized `Bytes`; `.load()` reads the
    next pickled object from the stream. Multiple `dump` /
    `load` round-trips on the same buffer are supported as long as
    the caller advances the cursor.
    """

    __slots__ = ("_buf", "_impl")

    def __init__(self, data: Bytes) -> None:
        self._buf = _io.BytesIO(data._value)
        # noqa: S301 — pickle is inherently unsafe with untrusted data;
        # documented in the namespace docstring. Callers are responsible
        # for validating the source.
        self._impl = _pickle.Unpickler(self._buf)  # noqa: S301

    def load(self) -> Any:
        return _wrap(self._impl.load())


class PickleNamespace:
    """Namespace mirroring Python's `pickle` module.

    Module-level shortcuts (`dumps` / `loads`) plus POOP-flavored
    `Path`-based `dump` / `load` (POOP has no file-object abstraction
    so dump/load take a `Path` directly rather than a file).

    Round-trip discipline: POOP types in → POOP types out. POOP
    primitive wrappers (`Int` / `Str` / `Float` / `Bytes` / `Boolean`
    / `NoneClass`) and POOP collections (`List` / `Tuple` / `Dict` /
    `Set` / `FrozenSet`) are unwrapped to their Python equivalents
    on dump and re-wrapped on load, so users never see a raw Python
    `int` / `str` / `list` / etc. POOP user-class instances pass
    through unchanged.

    `pickletools` and the `__reduce__` protocol hook are out of scope
    for v1.
    """

    HIGHEST_PROTOCOL: ClassVar[Int] = Int(_pickle.HIGHEST_PROTOCOL)
    DEFAULT_PROTOCOL: ClassVar[Int] = Int(_pickle.DEFAULT_PROTOCOL)

    PickleError: ClassVar[type[Exception]] = _pickle.PickleError
    PicklingError: ClassVar[type[Exception]] = _pickle.PicklingError
    UnpicklingError: ClassVar[type[Exception]] = _pickle.UnpicklingError

    Pickler: ClassVar[type[Pickler]] = Pickler
    Unpickler: ClassVar[type[Unpickler]] = Unpickler

    @staticmethod
    def dumps(obj: Any, protocol: Int | None = None) -> Bytes:
        return Bytes(_pickle.dumps(_unwrap(obj), _opt_protocol(protocol)))

    @staticmethod
    def loads(data: Bytes) -> Any:
        return _wrap(_pickle.loads(data._value))  # noqa: S301 — see Unpickler note

    @staticmethod
    def dump(obj: Any, path: Path, protocol: Int | None = None) -> NoneClass:
        # POOP convention: path-based instead of file-object-based.
        path._path.write_bytes(_pickle.dumps(_unwrap(obj), _opt_protocol(protocol)))
        return none

    @staticmethod
    def load(path: Path) -> Any:
        return _wrap(_pickle.loads(path._path.read_bytes()))  # noqa: S301 — see Unpickler note
