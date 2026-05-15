from __future__ import annotations

import datetime as _datetime
import tomllib as _tomllib
from typing import Any, ClassVar

from poop.types.boolean import false, true
from poop.types.dict import Dict
from poop.types.float import Float
from poop.types.int import Int
from poop.types.list import List
from poop.types.path import Path
from poop.types.string import Str

_DATETIME_TYPES = (_datetime.date, _datetime.time, _datetime.datetime)


def _wrap_collection(value: list[Any] | dict[Any, Any]) -> Any:
    if isinstance(value, list):
        return List(*(_wrap(v) for v in value))
    d = Dict()
    for k, v in value.items():
        d.at_put(Str(k) if isinstance(k, str) else _wrap(k), _wrap(v))
    return d


def _wrap(value: Any) -> Any:
    """Recursively convert TOML values into POOP types.

    TOML date/time/datetime values land here as `datetime.date`,
    `datetime.time`, `datetime.datetime` — POOP doesn't yet have a
    DateTime type, so flatten to ISO-8601 `Str`. Documented divergence
    that tightens once the `datetime` proposal ships.
    """
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
    if isinstance(value, _DATETIME_TYPES):
        # TOML date / time / datetime → ISO-8601 Str (transient
        # divergence pending the DateTime POOP type).
        return Str(value.isoformat())
    return value


class Tomllib:
    """Namespace mirroring Python's `tomllib` module (read-only TOML).

    POOP keeps Python's exact `loads`/`load` names. The `parse_float`
    keyword arg ships as a Python callable for v1; pairing it with
    POOP `Decimal` waits on the `decimal` proposal. `load` takes a
    POOP `Path` (POOP has no file-object abstraction), a forced
    receiver-type divergence from CPython's binary-file argument.

    Until the `DateTime` proposal lands, TOML date/time/datetime
    values flatten to ISO-8601 `Str` to avoid leaking
    `datetime.datetime` across the namespace boundary. When `DateTime`
    ships, the inner `_wrap` function tightens to return that POOP
    type instead.
    """

    TOMLDecodeError: ClassVar[type[Exception]] = _tomllib.TOMLDecodeError

    @staticmethod
    def loads(s: Str, /) -> Dict:
        result = _tomllib.loads(s._value)
        # Top-level always a Dict — the TOML grammar guarantees it.
        return _wrap(result)

    @staticmethod
    def load(path: Path, /) -> Dict:
        # CPython's load takes a binary file; POOP routes through Path.
        raw_bytes = path.read_bytes()
        return _wrap(_tomllib.loads(raw_bytes._value.decode("utf-8")))
