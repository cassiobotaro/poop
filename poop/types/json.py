from __future__ import annotations

import json as _json
from typing import Any, ClassVar

from poop.types.boolean import Boolean, false, true
from poop.types.dict import Dict
from poop.types.float import Float
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import NoneClass, none
from poop.types.object import Object
from poop.types.path import Path
from poop.types.string import Str


def _unwrap(obj: Any) -> Any:
    """Recursively convert a POOP value into its native-Python form.

    Used to feed the standard `json` encoder, which doesn't know POOP
    types.
    """
    if obj is none or isinstance(obj, NoneClass):
        return None
    if isinstance(obj, Boolean):
        return bool(obj)
    if isinstance(obj, (Int, Float, Str)):
        return obj._value
    if isinstance(obj, List):
        return [_unwrap(item) for item in obj._items]
    if isinstance(obj, Dict):
        out: dict[Any, Any] = {}
        for k, v in obj._data.items():
            # JSON only supports string keys at the protocol level.
            out[_unwrap(k)] = _unwrap(v)
        return out
    # Native Python primitive passing through (e.g., the user fed
    # raw bool/str/int) — pass it on; json will validate.
    return obj


def _wrap(value: Any) -> Any:
    """Recursively convert a Python value loaded from JSON into POOP."""
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
    if isinstance(value, list):
        return List(*(_wrap(v) for v in value))
    if isinstance(value, dict):
        d = Dict()
        for k, v in value.items():
            # JSON keys are always strings.
            d.at_put(Str(k) if isinstance(k, str) else _wrap(k), _wrap(v))
        return d
    return value  # opaque pass-through


class Json:
    """Namespace mirroring Python's `json` module.

    Round-trip discipline: POOP types in → POOP types out. The native
    `json` library walks Python types; this namespace wraps the
    entry/exit with `_unwrap`/`_wrap` so callers never see a raw
    `dict`/`list`/`str`/`int`/`float`/`bool`/`None`.

    `dump`/`load` are path-based per POOP's file-I/O convention (no
    `open` in POOP). The `cls`/`object_hook`/`parse_*`/`default` keyword
    arguments and the rest of the standard surface are deferred to
    Future work; v1 ships the 95% case with full POOP-type round-trip.
    """

    JSONDecodeError: ClassVar[type[Exception]] = _json.JSONDecodeError

    @staticmethod
    def dumps(
        obj: Any,
        *,
        skipkeys: Boolean = false,
        ensure_ascii: Boolean = true,
        check_circular: Boolean = true,
        allow_nan: Boolean = true,
        indent: Int | None = None,
        sort_keys: Boolean = false,
    ) -> Str:
        return Str(
            _json.dumps(
                _unwrap(obj),
                skipkeys=bool(skipkeys),
                ensure_ascii=bool(ensure_ascii),
                check_circular=bool(check_circular),
                allow_nan=bool(allow_nan),
                indent=None if indent is None else indent._value,
                sort_keys=bool(sort_keys),
            )
        )

    @staticmethod
    def loads(s: Str, /) -> Object:
        return _wrap(_json.loads(s._value))

    @staticmethod
    def dump(
        obj: Any,
        fp: Path,
        *,
        skipkeys: Boolean = false,
        ensure_ascii: Boolean = true,
        check_circular: Boolean = true,
        allow_nan: Boolean = true,
        indent: Int | None = None,
        sort_keys: Boolean = false,
    ) -> NoneClass:
        encoded = Json.dumps(
            obj,
            skipkeys=skipkeys,
            ensure_ascii=ensure_ascii,
            check_circular=check_circular,
            allow_nan=allow_nan,
            indent=indent,
            sort_keys=sort_keys,
        )
        fp.write_text(encoded)
        return none

    @staticmethod
    def load(fp: Path) -> Object:
        return _wrap(_json.loads(fp.read_text()._value))
