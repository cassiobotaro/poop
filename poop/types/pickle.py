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


class Pickler(_pickle.Pickler):
    """POOP wrapper around `pickle.Pickler`.

    Inherits directly from `_pickle.Pickler` so subclasses can override
    `persistent_id(obj)` in POOP idiom — the override receives a POOP
    value and returns a POOP value (or `none` for "not persistent"),
    and the bridge layer unwraps the return for CPython.

    `dispatch_table` is a write-bridged property: assign a POOP `Dict`
    or a Python `dict` mapping `type` → reducer; each reducer value
    that is a POOP `Block` is wrapped via `block.bridge` on assignment
    and stored as a plain Python callable for CPython's pickle to
    read. Class-level `dispatch_table = {...}` declarations in
    subclasses are *not* auto-bridged in v1 — assign as an instance
    attribute after construction.

    Construction takes the protocol level (default
    `pickle.DEFAULT_PROTOCOL`); `.dump(obj)` appends a pickled object to
    the internal buffer, and `.getvalue()` returns the accumulated
    `Bytes`. The CPython file-object constructor is absent — POOP has
    no generic file abstraction, so the Pickler is in-memory by design.
    """

    def __init__(self, protocol: Int | None = None) -> None:
        self._buf = _io.BytesIO()
        super().__init__(self._buf, _opt_protocol(protocol))

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        user_persistent_id = cls.__dict__.get("persistent_id")
        if user_persistent_id is not None:
            from poop.types._bridge import to_poop, to_python

            def wrapped_persistent_id(self: _pickle.Pickler, obj: Any) -> Any:
                result = user_persistent_id(self, to_poop(obj))
                if result is none or isinstance(result, NoneClass):
                    return None
                return to_python(result)

            cls.persistent_id = wrapped_persistent_id  # type: ignore[method-assign]

    # `_pickle.Pickler.dispatch_table` is a C-level getset descriptor backed
    # by a struct field. A plain Python property would shadow it but leave
    # the C field NULL, so the C `save` path would never see our entries.
    # The property below delegates read/write to the parent's descriptor.
    _parent_dispatch_table: Any = _pickle.Pickler.dispatch_table  # type: ignore[attr-defined]

    @property
    def dispatch_table(self) -> Any:  # type: ignore[override]
        # Parent raises AttributeError when unset — preserve that contract.
        return Pickler._parent_dispatch_table.__get__(self, type(self))

    @dispatch_table.setter
    def dispatch_table(self, table: Any) -> None:
        if table is None or isinstance(table, NoneClass):
            Pickler._parent_dispatch_table.__delete__(self)
            return

        from poop.types._bridge import bridge as _bridge_fn
        from poop.types.block import Block

        if isinstance(table, Dict):
            entries: list[tuple[Any, Any]] = list(table._data.items())
        elif isinstance(table, dict):
            entries = list(table.items())
        else:
            raise TypeError(
                f"dispatch_table must be a Dict or dict, got {type(table).__name__}"
            )

        wrapped: dict[Any, Any] = {}
        for k, v in entries:
            wrapped[k] = _bridge_fn(v) if isinstance(v, Block) else v
        Pickler._parent_dispatch_table.__set__(self, wrapped)

    def dump(self, obj: Any) -> NoneClass:  # type: ignore[override]
        super().dump(_unwrap(obj))
        return none

    def getvalue(self) -> Bytes:
        return Bytes(self._buf.getvalue())

    def clear_memo(self) -> NoneClass:  # type: ignore[override]
        super().clear_memo()
        return none


class Unpickler(_pickle.Unpickler):
    """POOP wrapper around `pickle.Unpickler`.

    Inherits directly from `_pickle.Unpickler` so subclasses can
    override `persistent_load(pid)` in POOP idiom — the override
    receives the POOP-wrapped persistent ID and returns the
    reconstructed POOP object; the bridge handles wrap/unwrap.

    Construction takes the serialized `Bytes`; `.load()` reads the
    next pickled object from the stream. Multiple `dump` / `load`
    round-trips on the same buffer are supported as long as the
    caller advances the cursor.
    """

    def __init__(self, data: Bytes) -> None:
        self._buf = _io.BytesIO(data._value)
        super().__init__(self._buf)  # noqa: S301

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        user_persistent_load = cls.__dict__.get("persistent_load")
        if user_persistent_load is not None:
            from poop.types._bridge import to_poop, to_python

            def wrapped_persistent_load(self: _pickle.Unpickler, pid: Any) -> Any:
                return to_python(user_persistent_load(self, to_poop(pid)))

            cls.persistent_load = wrapped_persistent_load  # type: ignore[method-assign]

    def load(self) -> Any:  # type: ignore[override]
        return _wrap(super().load())


class PickleBuffer(Object):
    """Wraps `pickle.PickleBuffer` — out-of-band buffer for zero-copy
    pickle.

    Construct from POOP `Bytes` / `ByteArray` (or any buffer-protocol
    object). `.raw()` returns a `MemoryView` over the underlying bytes;
    `.release()` releases the buffer.
    """

    __slots__ = ("_impl",)

    def __init__(self, data: Bytes | Any) -> None:
        raw = data._value if isinstance(data, Bytes) else data
        self._impl = _pickle.PickleBuffer(raw)

    def raw(self) -> Any:
        from poop.types.memory_view import MemoryView

        return MemoryView(self._impl.raw())

    def release(self) -> NoneClass:
        self._impl.release()
        return none


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
    PickleBuffer: ClassVar[type[PickleBuffer]] = PickleBuffer

    @staticmethod
    def dumps(
        obj: Any,
        protocol: Int | None = None,
        *,
        fix_imports: Boolean = true,
        buffer_callback: Any = None,
    ) -> Bytes:
        return Bytes(
            _pickle.dumps(
                _unwrap(obj),
                _opt_protocol(protocol),
                fix_imports=bool(fix_imports),
                buffer_callback=buffer_callback,
            )
        )

    @staticmethod
    def loads(
        data: Bytes,
        /,
        *,
        fix_imports: Boolean = true,
        encoding: Str = Str("ASCII"),
        errors: Str = Str("strict"),
        buffers: Any = (),
    ) -> Any:
        return _wrap(
            _pickle.loads(  # noqa: S301 — see Unpickler note
                data._value,
                fix_imports=bool(fix_imports),
                encoding=encoding._value,
                errors=errors._value,
                buffers=buffers,
            )
        )

    @staticmethod
    def dump(
        obj: Any,
        file: Path,
        protocol: Int | None = None,
        *,
        fix_imports: Boolean = true,
        buffer_callback: Any = None,
    ) -> NoneClass:
        # POOP convention: path-based instead of file-object-based; the
        # CPython param name `file` is preserved for kwargs compatibility.
        file._path.write_bytes(
            _pickle.dumps(
                _unwrap(obj),
                _opt_protocol(protocol),
                fix_imports=bool(fix_imports),
                buffer_callback=buffer_callback,
            )
        )
        return none

    @staticmethod
    def load(
        file: Path,
        *,
        fix_imports: Boolean = true,
        encoding: Str = Str("ASCII"),
        errors: Str = Str("strict"),
        buffers: Any = (),
    ) -> Any:
        return _wrap(
            _pickle.loads(  # noqa: S301 — see Unpickler note
                file._path.read_bytes(),
                fix_imports=bool(fix_imports),
                encoding=encoding._value,
                errors=errors._value,
                buffers=buffers,
            )
        )
