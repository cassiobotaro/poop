from __future__ import annotations

import sqlite3 as _sqlite3
from collections.abc import Callable
from types import TracebackType
from typing import Any, ClassVar, Self

from poop.types._bridge import bridge
from poop.types._unwrap import _unwrap
from poop.types.boolean import Boolean, false
from poop.types.bytes import Bytes
from poop.types.float import Float
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import NoneClass, none
from poop.types.object import Object
from poop.types.path import Path
from poop.types.string import Str
from poop.types.tuple import Tuple


def _wrap_value(value: Any) -> Any:
    if value is None:
        return none
    if isinstance(value, bool):
        from poop.types.boolean import false, true

        return true if value else false
    if isinstance(value, int):
        return Int(value)
    if isinstance(value, float):
        return Float(value)
    if isinstance(value, bytes):
        return Bytes(value)
    if isinstance(value, str):
        return Str(value)
    return value


def _wrap_row(raw: tuple[Any, ...]) -> Tuple:
    return Tuple(*[_wrap_value(v) for v in raw])


def _unwrap_value(value: Any) -> Any:
    if value is None or isinstance(value, NoneClass):
        return None
    if isinstance(value, Boolean):
        return bool(value)
    if hasattr(value, "_value"):
        return value._value
    return value


def _unwrap_params(params: Any) -> Any:
    if params is None or isinstance(params, NoneClass):
        return ()
    if isinstance(params, Tuple | List):
        return tuple(_unwrap_value(p) for p in params)
    return params


def _unwrap_database(database: Str | Path) -> Any:
    if isinstance(database, Path):
        return str(database._path)
    return database._value


class Blob(Object):
    """Wraps Python's `sqlite3.Blob` — random-access blob I/O.

    Opened via `Connection.blobopen(...)`. Reads return POOP `Bytes`;
    writes accept POOP `Bytes`. Position is tracked via `tell` / `seek`;
    `length()` returns the total byte length.
    """

    __slots__ = ("_impl",)

    def __init__(self, impl: Any) -> None:
        self._impl = impl

    def read(self, length: Int | NoneClass | None = None) -> Bytes:
        n = _unwrap(length, -1)
        if n == -1:
            return Bytes(self._impl.read())
        return Bytes(self._impl.read(n))

    def write(self, data: Bytes) -> NoneClass:
        self._impl.write(data._value)
        return none

    def tell(self) -> Int:
        return Int(self._impl.tell())

    def seek(self, offset: Int, origin: Int | NoneClass | None = None) -> NoneClass:
        whence = _unwrap(origin, 0)
        self._impl.seek(offset._value, whence)
        return none

    def length(self) -> Int:
        return Int(len(self._impl))

    def close(self) -> NoneClass:
        self._impl.close()
        return none

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self._impl.__exit__(exc_type, exc_value, traceback)


class Row(Object):
    """Dict-like row access by column name or index."""

    __slots__ = ("_columns", "_values")

    def __init__(self, columns: tuple[str, ...], values: tuple[Any, ...]) -> None:
        self._columns = columns
        self._values = values

    def at(self, key: Int | Str) -> Any:
        if isinstance(key, Int):
            return _wrap_value(self._values[key._value])
        idx = self._columns.index(key._value)
        return _wrap_value(self._values[idx])

    def keys(self) -> Tuple:
        return Tuple(*[Str(c) for c in self._columns])

    def values(self) -> Tuple:
        return Tuple(*[_wrap_value(v) for v in self._values])

    def len(self) -> Int:
        return Int(len(self._values))

    def __len__(self) -> int:
        return len(self._values)


class Cursor(Object):
    """Wraps Python's `sqlite3.Cursor` — query execution and result
    iteration."""

    __slots__ = ("_impl",)

    def __init__(self, impl: _sqlite3.Cursor) -> None:
        self._impl = impl

    def execute(
        self, sql: Str, params: Tuple | List | NoneClass | None = None
    ) -> Cursor:
        self._impl.execute(sql._value, _unwrap_params(params))
        return self

    def executemany(self, sql: Str, seq: Tuple | List) -> Cursor:
        seq_iter: Any = seq
        self._impl.executemany(
            sql._value,
            [_unwrap_params(row) for row in seq_iter],
        )
        return self

    def executescript(self, script: Str) -> Cursor:
        self._impl.executescript(script._value)
        return self

    def fetchone(self) -> Tuple | NoneClass:
        row = self._impl.fetchone()
        return none if row is None else _wrap_row(row)

    def fetchmany(self, size: Int | NoneClass | None = None) -> List:
        n = _unwrap(size, self._impl.arraysize)
        rows = self._impl.fetchmany(n)
        return List(*[_wrap_row(r) for r in rows])

    def fetchall(self) -> List:
        rows = self._impl.fetchall()
        return List(*[_wrap_row(r) for r in rows])

    def close(self) -> NoneClass:
        self._impl.close()
        return none

    @property
    def rowcount(self) -> Int:
        return Int(self._impl.rowcount)

    @property
    def lastrowid(self) -> Int | NoneClass:
        lid = self._impl.lastrowid
        return none if lid is None else Int(lid)

    @property
    def description(self) -> Tuple | NoneClass:
        desc = self._impl.description
        if desc is None:
            return none
        return Tuple(*[Tuple(Str(col[0]), *[none for _ in col[1:]]) for col in desc])

    @property
    def arraysize(self) -> Int:
        return Int(self._impl.arraysize)

    def __iter__(self) -> Any:
        for row in self._impl:
            yield _wrap_row(row)


class Connection(Object):
    """Wraps Python's `sqlite3.Connection` — a database connection."""

    __slots__ = ("_impl",)

    def __init__(self, impl: _sqlite3.Connection) -> None:
        self._impl = impl

    def cursor(self) -> Cursor:
        return Cursor(self._impl.cursor())

    def commit(self) -> NoneClass:
        self._impl.commit()
        return none

    def rollback(self) -> NoneClass:
        self._impl.rollback()
        return none

    def close(self) -> NoneClass:
        self._impl.close()
        return none

    def execute(
        self, sql: Str, params: Tuple | List | NoneClass | None = None
    ) -> Cursor:
        return Cursor(self._impl.execute(sql._value, _unwrap_params(params)))

    def executemany(self, sql: Str, seq: Tuple | List) -> Cursor:
        seq_iter: Any = seq
        return Cursor(
            self._impl.executemany(
                sql._value, [_unwrap_params(row) for row in seq_iter]
            )
        )

    def executescript(self, script: Str) -> Cursor:
        return Cursor(self._impl.executescript(script._value))

    def interrupt(self) -> NoneClass:
        self._impl.interrupt()
        return none

    def iterdump(self) -> List:
        return List(*[Str(line) for line in self._impl.iterdump()])

    def backup(
        self,
        target: Connection,
        pages: Int | NoneClass | None = None,
        name: Str | NoneClass | None = None,
        sleep: Float | NoneClass | None = None,
    ) -> NoneClass:
        self._impl.backup(
            target._impl,
            pages=_unwrap(pages, -1),
            name=_unwrap(name, "main"),
            sleep=_unwrap(sleep, 0.250),
        )
        return none

    def create_function(
        self,
        name: Str,
        narg: Int,
        func: Callable[..., Any],
        *,
        deterministic: Boolean = false,
    ) -> NoneClass:
        self._impl.create_function(
            name._value,
            narg._value,
            bridge(func),
            deterministic=bool(deterministic),
        )
        return none

    def create_collation(
        self,
        name: Str,
        callable_: Callable[..., Any] | None,
    ) -> NoneClass:
        # CPython allows None to remove a previously registered collation.
        adapter = None if callable_ is None else bridge(callable_)
        self._impl.create_collation(name._value, adapter)
        return none

    def blobopen(
        self,
        table: Str,
        column: Str,
        row: Int,
        *,
        readonly: Boolean = false,
        name: Str | None = None,
    ) -> Blob:
        impl = self._impl.blobopen(
            table._value,
            column._value,
            row._value,
            readonly=bool(readonly),
            name="main" if name is None else name._value,
        )
        return Blob(impl)

    def create_aggregate(
        self,
        name: Str,
        n_arg: Int,
        aggregate_class: type,
    ) -> NoneClass:
        """Register a user-defined aggregate.

        `aggregate_class` is a regular POOP class with `step(*args)` and
        `finalize()` methods. SQLite calls `step` with raw column
        values; POOP wraps them to POOP types before invoking the
        user's method. `finalize` returns a POOP value; POOP unwraps it
        to the native primitive SQLite expects.
        """
        from poop.types._bridge import to_poop, to_python

        class _PoopAggregateAdapter:
            def __init__(self) -> None:
                self._inner = aggregate_class()

            def step(self, *args: Any) -> None:
                self._inner.step(*(to_poop(a) for a in args))

            def finalize(self) -> Any:
                return to_python(self._inner.finalize())

        self._impl.create_aggregate(name._value, n_arg._value, _PoopAggregateAdapter)
        return none

    def __enter__(self) -> Self:
        self._impl.__enter__()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> Any:
        return self._impl.__exit__(exc_type, exc_value, traceback)


class Sqlite3:
    """Namespace mirroring Python's `sqlite3` module."""

    Connection: ClassVar[type[Connection]] = Connection
    Cursor: ClassVar[type[Cursor]] = Cursor
    Row: ClassVar[type[Row]] = Row
    Blob: ClassVar[type[Blob]] = Blob

    sqlite_version: ClassVar[Str] = Str(_sqlite3.sqlite_version)

    PARSE_DECLTYPES: ClassVar[Int] = Int(_sqlite3.PARSE_DECLTYPES)
    PARSE_COLNAMES: ClassVar[Int] = Int(_sqlite3.PARSE_COLNAMES)

    Warning: ClassVar[type[Exception]] = _sqlite3.Warning
    Error: ClassVar[type[Exception]] = _sqlite3.Error
    InterfaceError: ClassVar[type[Exception]] = _sqlite3.InterfaceError
    DatabaseError: ClassVar[type[Exception]] = _sqlite3.DatabaseError
    DataError: ClassVar[type[Exception]] = _sqlite3.DataError
    OperationalError: ClassVar[type[Exception]] = _sqlite3.OperationalError
    IntegrityError: ClassVar[type[Exception]] = _sqlite3.IntegrityError
    InternalError: ClassVar[type[Exception]] = _sqlite3.InternalError
    ProgrammingError: ClassVar[type[Exception]] = _sqlite3.ProgrammingError
    NotSupportedError: ClassVar[type[Exception]] = _sqlite3.NotSupportedError

    @staticmethod
    def complete_statement(sql: Str) -> Boolean:
        """Return `true` if `sql` is a complete SQLite statement."""
        from poop.types.boolean import false as _f
        from poop.types.boolean import true as _t

        return _t if _sqlite3.complete_statement(sql._value) else _f

    @staticmethod
    def enable_callback_tracebacks(flag: Boolean) -> NoneClass:
        """Toggle tracebacks for errors in user-defined SQL callbacks."""
        _sqlite3.enable_callback_tracebacks(bool(flag))
        return none

    @staticmethod
    def register_adapter(type_: type, adapter: Callable[..., Any]) -> NoneClass:
        """Teach sqlite3 how to convert `type_` into a value it can store.

        The adapter block receives a POOP-wrapped value and returns the
        Python primitive sqlite3 should write to the database — the
        bridge handles `to_poop` on input and `to_python` on output.
        """
        _sqlite3.register_adapter(type_, bridge(adapter))
        return none

    @staticmethod
    def register_converter(typename: Str, converter: Callable[..., Any]) -> NoneClass:
        """Teach sqlite3 how to decode a stored value for the SQL column
        type `typename`. The converter receives the raw `Bytes` payload
        and returns the value to surface to user code.
        """
        _sqlite3.register_converter(typename._value, bridge(converter))
        return none

    @staticmethod
    def connect(
        database: Str | Path,
        timeout: Float | NoneClass | None = None,
        detect_types: Int | NoneClass | None = None,
        isolation_level: Str | NoneClass | None = None,
        check_same_thread: Boolean | NoneClass | None = None,
        cached_statements: Int | NoneClass | None = None,
        uri: Boolean | NoneClass | None = None,
    ) -> Connection:
        kwargs: dict[str, Any] = {}
        if timeout is not None and not isinstance(timeout, NoneClass):
            kwargs["timeout"] = timeout._value
        if detect_types is not None and not isinstance(detect_types, NoneClass):
            kwargs["detect_types"] = detect_types._value
        if isolation_level is not None and not isinstance(isolation_level, NoneClass):
            kwargs["isolation_level"] = isolation_level._value
        if check_same_thread is not None and not isinstance(
            check_same_thread, NoneClass
        ):
            kwargs["check_same_thread"] = bool(check_same_thread)
        if cached_statements is not None and not isinstance(
            cached_statements, NoneClass
        ):
            kwargs["cached_statements"] = cached_statements._value
        if uri is not None and not isinstance(uri, NoneClass):
            kwargs["uri"] = bool(uri)
        return Connection(_sqlite3.connect(_unwrap_database(database), **kwargs))
