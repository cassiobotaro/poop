from __future__ import annotations

import csv as _csv
import io as _io
from typing import Any, ClassVar

from poop.types.boolean import Boolean
from poop.types.dict import Dict
from poop.types.float import Float
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import NoneClass, none
from poop.types.object import Object
from poop.types.string import Str
from poop.types.tuple import Tuple


def _opt_str(value: Str | None, default: str | None) -> str | None:
    return default if value is None else value._value


def _opt_int(value: Int | None) -> int | None:
    return None if value is None else value._value


def _source_iter(source: List | Str) -> Any:
    """Adapt a POOP source to an iterable of `str` lines for csv.reader."""
    if isinstance(source, Str):
        return source._value.splitlines(keepends=True)
    return [line._value if isinstance(line, Str) else line for line in source]


def _unwrap_row(row: List | Tuple) -> list[Any]:
    out: list[Any] = []
    for cell in row:
        if isinstance(cell, Str):
            out.append(cell._value)
        elif isinstance(cell, Int | Float):
            out.append(cell._value)
        elif cell is none or isinstance(cell, NoneClass):
            out.append("")
        else:
            out.append(cell)
    return out


def _wrap_fmtparams(kwargs: dict[str, Any]) -> dict[str, Any]:
    """Unwrap POOP types in csv format kwargs."""
    result: dict[str, Any] = {}
    for k, v in kwargs.items():
        if isinstance(v, Str | Int):
            result[k] = v._value
        elif isinstance(v, Boolean):
            result[k] = bool(v)
        else:
            result[k] = v
    return result


class Reader(Object):
    """Wraps Python's `csv.reader` — a row-by-row CSV iterator.

    The source can be a POOP `Str` (split on newlines) or a `List[Str]`
    of lines. Iteration yields `List[Str]` per row. The `.line_num`
    property tracks the underlying line counter (1-indexed).
    """

    __slots__ = ("_impl", "_dialect")

    def __init__(
        self,
        source: List | Str,
        dialect: Str | None = None,
        **fmtparams: Any,
    ) -> None:
        kwargs = _wrap_fmtparams(fmtparams)
        self._dialect = _opt_str(dialect, "excel") or "excel"
        self._impl = _csv.reader(_source_iter(source), self._dialect, **kwargs)

    def __iter__(self) -> Any:
        for row in self._impl:
            yield List(*(Str(cell) for cell in row))

    @property
    def line_num(self) -> Int:
        return Int(self._impl.line_num)

    @property
    def dialect(self) -> Str:
        return Str(self._dialect or "excel")


class Writer(Object):
    """Wraps Python's `csv.writer` over an internal `StringIO` buffer.

    `.writerow(row)` appends a single row; `.writerows(rows)` appends
    many. `.getvalue()` returns the accumulated CSV text as `Str`.
    """

    __slots__ = ("_buf", "_impl")

    def __init__(self, dialect: Str | None = None, **fmtparams: Any) -> None:
        kwargs = _wrap_fmtparams(fmtparams)
        self._buf = _io.StringIO()
        self._impl = _csv.writer(
            self._buf, _opt_str(dialect, "excel") or "excel", **kwargs
        )

    def writerow(self, row: List | Tuple) -> Int:
        return Int(self._impl.writerow(_unwrap_row(row)))

    def writerows(self, rows: List | Tuple) -> NoneClass:
        for row in rows:
            if not isinstance(row, List | Tuple):
                raise TypeError(
                    f"writerows entries must be List or Tuple, got {type(row).__name__}"
                )
            self._impl.writerow(_unwrap_row(row))
        return none

    def getvalue(self) -> Str:
        return Str(self._buf.getvalue())


class DictReader(Object):
    """Wraps Python's `csv.DictReader` — yields `Dict[Str, Str]` per row.

    `fieldnames` is auto-detected from the first row when omitted.
    `restkey` / `restval` cover the over/under-supplied row cases.
    """

    __slots__ = ("_impl",)

    def __init__(
        self,
        source: List | Str,
        fieldnames: List | None = None,
        restkey: Str | None = None,
        restval: Str | None = None,
        dialect: Str | None = None,
        **fmtparams: Any,
    ) -> None:
        kwargs = _wrap_fmtparams(fmtparams)
        names: Any = None
        if fieldnames is not None:
            names = [n._value if isinstance(n, Str) else n for n in fieldnames]
        self._impl = _csv.DictReader(
            _source_iter(source),
            fieldnames=names,
            restkey=_opt_str(restkey, None),
            restval=_opt_str(restval, None),
            dialect=_opt_str(dialect, "excel") or "excel",
            **kwargs,
        )

    def __iter__(self) -> Any:
        for row in self._impl:
            d = Dict()
            for k, v in row.items():
                key = Str(k) if isinstance(k, str) else k
                if isinstance(v, list):
                    val: Any = List(*(Str(item) for item in v))
                else:
                    val = Str(v) if v is not None else none
                d.at_put(key, val)
            yield d

    @property
    def fieldnames(self) -> List | NoneClass:
        names = self._impl.fieldnames
        if names is None:
            return none
        return List(*(Str(n if isinstance(n, str) else str(n)) for n in names))

    @property
    def line_num(self) -> Int:
        return Int(self._impl.line_num)


class DictWriter(Object):
    """Wraps Python's `csv.DictWriter` over an internal `StringIO` buffer."""

    __slots__ = ("_buf", "_impl")

    def __init__(
        self,
        fieldnames: List,
        restval: Str | None = None,
        extrasaction: Str | None = None,
        dialect: Str | None = None,
        **fmtparams: Any,
    ) -> None:
        kwargs = _wrap_fmtparams(fmtparams)
        names = [n._value if isinstance(n, Str) else n for n in fieldnames]
        self._buf = _io.StringIO()
        self._impl = _csv.DictWriter(
            self._buf,
            fieldnames=names,
            restval=_opt_str(restval, ""),
            extrasaction=_opt_str(extrasaction, "raise") or "raise",  # ty: ignore[invalid-argument-type]
            dialect=_opt_str(dialect, "excel") or "excel",
            **kwargs,
        )

    def writeheader(self) -> Int:
        return Int(self._impl.writeheader())

    def writerow(self, row: Dict) -> Int:
        return Int(self._impl.writerow(_unwrap_dict(row)))

    def writerows(self, rows: List) -> NoneClass:
        for row in rows:
            if not isinstance(row, Dict):
                raise TypeError(
                    f"DictWriter rows must be Dict, got {type(row).__name__}"
                )
            self._impl.writerow(_unwrap_dict(row))
        return none

    def getvalue(self) -> Str:
        return Str(self._buf.getvalue())


def _unwrap_dict(row: Dict) -> dict[Any, Any]:
    out: dict[Any, Any] = {}
    for k, v in row._data.items():
        key = k._value if isinstance(k, Str) else k
        if isinstance(v, Str | Int):
            out[key] = v._value
        elif isinstance(v, Boolean):
            out[key] = bool(v)
        elif v is none or isinstance(v, NoneClass):
            out[key] = ""
        else:
            out[key] = v
    return out


class Sniffer(Object):
    """Wraps Python's `csv.Sniffer` — autodetects dialect from a sample."""

    __slots__ = ("_impl",)

    def __init__(self) -> None:
        self._impl = _csv.Sniffer()

    def sniff(self, sample: Str, delimiters: Str | None = None) -> Any:
        kwargs: dict[str, Any] = {}
        if delimiters is not None:
            kwargs["delimiters"] = delimiters._value
        return self._impl.sniff(sample._value, **kwargs)

    def has_header(self, sample: Str) -> Boolean:
        from poop.types.boolean import false, true

        return true if self._impl.has_header(sample._value) else false


class CSV:
    """Namespace mirroring Python's `csv` module.

    Reader / Writer / DictReader / DictWriter operate over POOP `Str` /
    `List[Str]` collections (no file-object abstraction). Writer-style
    classes accumulate into an internal `StringIO` exposed via
    `.getvalue()` — call it after writing all rows.
    """

    Reader: ClassVar[type[Reader]] = Reader
    Writer: ClassVar[type[Writer]] = Writer
    DictReader: ClassVar[type[DictReader]] = DictReader
    DictWriter: ClassVar[type[DictWriter]] = DictWriter
    Sniffer: ClassVar[type[Sniffer]] = Sniffer

    # Dialect class refs (re-exported from CPython).
    Dialect: ClassVar[type[Any]] = _csv.Dialect
    excel: ClassVar[type[Any]] = _csv.excel
    excel_tab: ClassVar[type[Any]] = _csv.excel_tab
    unix_dialect: ClassVar[type[Any]] = _csv.unix_dialect

    # Quoting constants.
    QUOTE_ALL: ClassVar[Int] = Int(_csv.QUOTE_ALL)
    QUOTE_MINIMAL: ClassVar[Int] = Int(_csv.QUOTE_MINIMAL)
    QUOTE_NONNUMERIC: ClassVar[Int] = Int(_csv.QUOTE_NONNUMERIC)
    QUOTE_NONE: ClassVar[Int] = Int(_csv.QUOTE_NONE)
    QUOTE_STRINGS: ClassVar[Int] = Int(_csv.QUOTE_STRINGS)
    QUOTE_NOTNULL: ClassVar[Int] = Int(_csv.QUOTE_NOTNULL)

    Error: ClassVar[type[Exception]] = _csv.Error

    @staticmethod
    def reader(
        source: List | Str,
        dialect: Str | None = None,
        **fmtparams: Any,
    ) -> Reader:
        return Reader(source, dialect, **fmtparams)

    @staticmethod
    def writer(dialect: Str | None = None, **fmtparams: Any) -> Writer:
        return Writer(dialect, **fmtparams)

    @staticmethod
    def list_dialects() -> List:
        return List(*(Str(n) for n in _csv.list_dialects()))

    @staticmethod
    def get_dialect(name: Str) -> Any:
        return _csv.get_dialect(name._value)

    @staticmethod
    def register_dialect(
        name: Str,
        dialect: Any = None,
        **fmtparams: Any,
    ) -> NoneClass:
        kwargs = _wrap_fmtparams(fmtparams)
        if dialect is None:
            _csv.register_dialect(name._value, **kwargs)
        else:
            _csv.register_dialect(name._value, dialect, **kwargs)
        return none

    @staticmethod
    def unregister_dialect(name: Str) -> NoneClass:
        _csv.unregister_dialect(name._value)
        return none

    @staticmethod
    def field_size_limit(new_limit: Int | None = None) -> Int:
        if new_limit is None:
            return Int(_csv.field_size_limit())
        return Int(_csv.field_size_limit(new_limit._value))
