import zoneinfo as _zoneinfo
from collections.abc import Iterable
from typing import ClassVar

from poop.types.none import NoneClass, none
from poop.types.set import Set
from poop.types.string import Str
from poop.types.tuple import Tuple


def _set_of_str(items: Iterable[str]) -> Set:
    return Set(*(Str(s) for s in items))


def _tuple_of_str(items: Iterable[str]) -> Tuple:
    return Tuple(*(Str(s) for s in items))


class ZoneInfo:
    """Wraps Python's `zoneinfo.ZoneInfo` — an IANA timezone.

    `ZoneInfo(key)` resolves through the standard cache;
    `ZoneInfo.no_cache(key)` bypasses it; `ZoneInfo.clear_cache(...)`
    purges entries. Instances are `datetime.tzinfo` subclasses
    internally — pass them to `DateTime.now(tz=...)`,
    `DateTime(tzinfo=...)`, or `DateTime.astimezone(tz)`.

    `ZoneInfo.from_file` is deferred — POOP has no file-object
    abstraction.
    """

    __slots__ = ("_impl",)

    def __init__(self, key: Str) -> None:
        self._impl = _zoneinfo.ZoneInfo(key._value)

    @classmethod
    def _from_impl(cls, impl: _zoneinfo.ZoneInfo) -> ZoneInfo:
        obj = cls.__new__(cls)
        obj._impl = impl
        return obj

    @classmethod
    def no_cache(cls, key: Str) -> ZoneInfo:
        return cls._from_impl(_zoneinfo.ZoneInfo.no_cache(key._value))

    @classmethod
    def clear_cache(cls, only_keys: Set | None = None) -> NoneClass:
        if only_keys is None:
            _zoneinfo.ZoneInfo.clear_cache()
        else:
            keys: list[str] = []
            for k in only_keys:
                if not isinstance(k, Str):
                    raise TypeError(
                        f"clear_cache only_keys must contain Str, got {type(k).__name__}"
                    )
                keys.append(k._value)
            _zoneinfo.ZoneInfo.clear_cache(only_keys=keys)
        return none

    @property
    def key(self) -> Str:
        return Str(self._impl.key)


class _ZoneinfoNamespace:
    """Singleton namespace mirroring Python's `zoneinfo` module.

    `TZPATH` is a `@property` returning a fresh snapshot — CPython
    exposes it as a module-level tuple attribute. `reset_tzpath`
    mutates it.
    """

    ZoneInfoNotFoundError: ClassVar[type[Exception]] = _zoneinfo.ZoneInfoNotFoundError

    def available_timezones(self) -> Set:
        return _set_of_str(_zoneinfo.available_timezones())

    def reset_tzpath(self, to: Tuple | None = None) -> NoneClass:
        if to is None:
            _zoneinfo.reset_tzpath()
        else:
            paths: list[str] = []
            for p in to:
                if not isinstance(p, Str):
                    raise TypeError(
                        f"reset_tzpath entries must be Str, got {type(p).__name__}"
                    )
                paths.append(p._value)
            _zoneinfo.reset_tzpath(to=paths)
        return none

    @property
    def TZPATH(self) -> Tuple:
        return _tuple_of_str(_zoneinfo.TZPATH)


Zoneinfo = _ZoneinfoNamespace()
