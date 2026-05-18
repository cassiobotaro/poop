from __future__ import annotations

import datetime as _datetime
import tomllib as _tomllib
from collections.abc import Callable
from typing import Any, ClassVar

from poop.types._bridge import bridge
from poop.types.boolean import false, true
from poop.types.datetime import Date, DateTime, Time
from poop.types.dict import Dict
from poop.types.float import Float
from poop.types.int import Int
from poop.types.list import List
from poop.types.path import Path
from poop.types.string import Str


def _wrap_collection(value: list[Any] | dict[Any, Any]) -> Any:
    if isinstance(value, list):
        return List(*(_wrap(v) for v in value))
    d = Dict()
    for k, v in value.items():
        d.at_put(Str(k) if isinstance(k, str) else _wrap(k), _wrap(v))
    return d


def _wrap(value: Any) -> Any:
    if isinstance(value, bool):
        return true if value else false
    if isinstance(value, int):
        return Int(value)
    if isinstance(value, float):
        return Float(value)
    if isinstance(value, str):
        return Str(value)
    if isinstance(value, (list, dict)):
        return _wrap_collection(value)
    # `datetime.datetime` is a subclass of `datetime.date`; check it first.
    if isinstance(value, _datetime.datetime):
        return DateTime._from_impl(value)
    if isinstance(value, _datetime.date):
        return Date._from_impl(value)
    if isinstance(value, _datetime.time):
        return Time._from_impl(value)
    return value


class Tomllib:
    """Namespace mirroring Python's `tomllib` module (read-only TOML).

    POOP keeps Python's exact `loads`/`load` names. `parse_float`
    accepts a POOP `Block` routed through `block.bridge` (default is
    Python `float`, mirroring CPython exactly). `load` takes a POOP
    `Path` (POOP has no file-object abstraction) — a forced
    receiver-type divergence from CPython's binary-file argument.

    TOML date/time/datetime values land as POOP `Date`/`Time`/`DateTime`.
    """

    TOMLDecodeError: ClassVar[type[Exception]] = _tomllib.TOMLDecodeError

    @staticmethod
    def loads(
        s: Str,
        /,
        *,
        parse_float: Callable[..., Any] = float,
    ) -> Dict:
        pf = (
            parse_float
            if parse_float is float
            else bridge(parse_float, unwrap_return=False)
        )
        # Top-level always a Dict — the TOML grammar guarantees it.
        return _wrap(_tomllib.loads(s._value, parse_float=pf))

    @staticmethod
    def load(
        fp: Path,
        /,
        *,
        parse_float: Callable[..., Any] = float,
    ) -> Dict:
        # CPython's load takes a binary file; POOP routes through Path.
        raw_bytes = fp.read_bytes()
        pf = (
            parse_float
            if parse_float is float
            else bridge(parse_float, unwrap_return=False)
        )
        return _wrap(_tomllib.loads(raw_bytes._value.decode("utf-8"), parse_float=pf))
