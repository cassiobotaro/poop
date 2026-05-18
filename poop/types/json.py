from __future__ import annotations

import json as _json
from collections.abc import Callable
from typing import Any, ClassVar

from poop.types._bridge import bridge, to_poop, to_python
from poop.types.boolean import Boolean, false, true
from poop.types.none import NoneClass, none
from poop.types.object import Object
from poop.types.path import Path
from poop.types.string import Str
from poop.types.tuple import Tuple


def _maybe_bridge(
    block: Callable[..., Any] | None,
    *,
    wrap_args: bool = True,
    unwrap_return: bool = True,
) -> Callable[..., Any] | None:
    if block is None:
        return None
    return bridge(block, wrap_args=wrap_args, unwrap_return=unwrap_return)


class JSONEncoder(_json.JSONEncoder):
    """POOP wrapper around `json.JSONEncoder`.

    Subclass and override `default(o)` to teach JSON how to serialize
    POOP types it doesn't know natively. The override receives a POOP
    value and returns a POOP value — the bridge layer handles the
    Python-side `to_poop` / `to_python` wrap/unwrap so the override
    body stays in POOP idiom:

        class MyEncoder(JSONEncoder):
            def default(self, o):
                return o.is_instance(DateTime).if_true_if_false(
                    lambda: o.isoformat(),
                    lambda: super().default(o),
                )
    """

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        user_default = cls.__dict__.get("default")
        if user_default is None:
            return

        def wrapped_default(self: _json.JSONEncoder, o: Any) -> Any:
            return to_python(user_default(self, to_poop(o)))

        cls.default = wrapped_default  # type: ignore[method-assign]


class JSONDecoder(_json.JSONDecoder):
    """POOP wrapper around `json.JSONDecoder`.

    Pass `object_hook`, `parse_float`, `parse_int`, `parse_constant`,
    and `object_pairs_hook` as POOP `Block`s; the bridge wraps inputs
    into POOP types before invoking them. `strict` is a POOP
    `Boolean`. `decode(s)` accepts a POOP `Str` and returns POOP-typed
    output.
    """

    def __init__(
        self,
        *,
        object_hook: Callable[..., Any] | None = None,
        parse_float: Callable[..., Any] | None = None,
        parse_int: Callable[..., Any] | None = None,
        parse_constant: Callable[..., Any] | None = None,
        object_pairs_hook: Callable[..., Any] | None = None,
        strict: Boolean = true,
    ) -> None:
        super().__init__(
            object_hook=_maybe_bridge(object_hook, unwrap_return=False),
            parse_float=_maybe_bridge(parse_float, unwrap_return=False),
            parse_int=_maybe_bridge(parse_int, unwrap_return=False),
            parse_constant=_maybe_bridge(parse_constant, unwrap_return=False),
            object_pairs_hook=_maybe_bridge(object_pairs_hook, unwrap_return=False),
            strict=bool(strict),
        )

    def decode(self, s: Str | str, _w: Any = None) -> Object:  # type: ignore[override]
        text = s._value if isinstance(s, Str) else s
        return to_poop(super().decode(text))


class Json:
    """Namespace mirroring Python's `json` module.

    Round-trip discipline: POOP types in → POOP types out. The native
    `json` library walks Python types; this namespace unwraps on entry
    via `to_python` and re-wraps on exit via `to_poop`. Callback
    kwargs (`default`, `object_hook`, `parse_float`, `parse_int`,
    `parse_constant`, `object_pairs_hook`) accept POOP `Block`s and
    are routed through `block.bridge` so the user's block receives
    POOP-typed arguments and can return POOP-typed values.

    `dump`/`load` are path-based per POOP's file-I/O convention (no
    `open` in POOP).
    """

    JSONDecodeError: ClassVar[type[Exception]] = _json.JSONDecodeError
    JSONEncoder: ClassVar[type[_json.JSONEncoder]] = JSONEncoder
    JSONDecoder: ClassVar[type[_json.JSONDecoder]] = JSONDecoder

    @staticmethod
    def dumps(
        obj: Any,
        *,
        skipkeys: Boolean = false,
        ensure_ascii: Boolean = true,
        check_circular: Boolean = true,
        allow_nan: Boolean = true,
        cls: type[_json.JSONEncoder] | None = None,
        indent: Any | None = None,
        separators: Tuple | None = None,
        default: Callable[..., Any] | None = None,
        sort_keys: Boolean = false,
    ) -> Str:
        kwargs: dict[str, Any] = {
            "skipkeys": bool(skipkeys),
            "ensure_ascii": bool(ensure_ascii),
            "check_circular": bool(check_circular),
            "allow_nan": bool(allow_nan),
            "sort_keys": bool(sort_keys),
        }
        if indent is not None:
            kwargs["indent"] = to_python(indent)
        if separators is not None:
            kwargs["separators"] = tuple(to_python(s) for s in separators._items)
        if cls is not None:
            kwargs["cls"] = cls
        bridged_default = _maybe_bridge(default)
        if bridged_default is not None:
            kwargs["default"] = bridged_default
        return Str(_json.dumps(to_python(obj), **kwargs))

    @staticmethod
    def loads(
        s: Str,
        /,
        *,
        cls: type[_json.JSONDecoder] | None = None,
        object_hook: Callable[..., Any] | None = None,
        parse_float: Callable[..., Any] | None = None,
        parse_int: Callable[..., Any] | None = None,
        parse_constant: Callable[..., Any] | None = None,
        object_pairs_hook: Callable[..., Any] | None = None,
    ) -> Object:
        kwargs: dict[str, Any] = {}
        if cls is not None:
            kwargs["cls"] = cls
        bridged_object_hook = _maybe_bridge(object_hook, unwrap_return=False)
        if bridged_object_hook is not None:
            kwargs["object_hook"] = bridged_object_hook
        bridged_parse_float = _maybe_bridge(parse_float, unwrap_return=False)
        if bridged_parse_float is not None:
            kwargs["parse_float"] = bridged_parse_float
        bridged_parse_int = _maybe_bridge(parse_int, unwrap_return=False)
        if bridged_parse_int is not None:
            kwargs["parse_int"] = bridged_parse_int
        bridged_parse_constant = _maybe_bridge(parse_constant, unwrap_return=False)
        if bridged_parse_constant is not None:
            kwargs["parse_constant"] = bridged_parse_constant
        bridged_object_pairs_hook = _maybe_bridge(
            object_pairs_hook, unwrap_return=False
        )
        if bridged_object_pairs_hook is not None:
            kwargs["object_pairs_hook"] = bridged_object_pairs_hook
        return to_poop(_json.loads(s._value, **kwargs))

    @staticmethod
    def dump(
        obj: Any,
        fp: Path,
        *,
        skipkeys: Boolean = false,
        ensure_ascii: Boolean = true,
        check_circular: Boolean = true,
        allow_nan: Boolean = true,
        cls: type[_json.JSONEncoder] | None = None,
        indent: Any | None = None,
        separators: Tuple | None = None,
        default: Callable[..., Any] | None = None,
        sort_keys: Boolean = false,
    ) -> NoneClass:
        encoded = Json.dumps(
            obj,
            skipkeys=skipkeys,
            ensure_ascii=ensure_ascii,
            check_circular=check_circular,
            allow_nan=allow_nan,
            cls=cls,
            indent=indent,
            separators=separators,
            default=default,
            sort_keys=sort_keys,
        )
        fp.write_text(encoded)
        return none

    @staticmethod
    def load(
        fp: Path,
        *,
        cls: type[_json.JSONDecoder] | None = None,
        object_hook: Callable[..., Any] | None = None,
        parse_float: Callable[..., Any] | None = None,
        parse_int: Callable[..., Any] | None = None,
        parse_constant: Callable[..., Any] | None = None,
        object_pairs_hook: Callable[..., Any] | None = None,
    ) -> Object:
        return Json.loads(
            fp.read_text(),
            cls=cls,
            object_hook=object_hook,
            parse_float=parse_float,
            parse_int=parse_int,
            parse_constant=parse_constant,
            object_pairs_hook=object_pairs_hook,
        )
