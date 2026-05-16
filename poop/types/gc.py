from __future__ import annotations

import gc as _gc
from typing import Any, ClassVar

from poop.types.boolean import Boolean, false, true
from poop.types.dict import Dict
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import NoneClass, none


def _wrap_value(value: Any) -> Any:
    if isinstance(value, bool):
        return true if value else false
    if isinstance(value, int):
        return Int(value)
    if isinstance(value, str):
        from poop.types.string import Str

        return Str(value)
    return value


class GC:
    """Namespace mirroring (the control surface of) Python's `gc` module.

    The introspection-heavy pieces (`get_objects` / `get_referrers` /
    `get_referents` / `is_tracked` / `is_finalized`) are out of scope
    — they clash with POOP's no-introspection rule. Toggling,
    forcing collections, thresholds, stats, debug flags, freeze, and
    callbacks are all surfaced.
    """

    DEBUG_STATS: ClassVar[Int] = Int(_gc.DEBUG_STATS)
    DEBUG_COLLECTABLE: ClassVar[Int] = Int(_gc.DEBUG_COLLECTABLE)
    DEBUG_UNCOLLECTABLE: ClassVar[Int] = Int(_gc.DEBUG_UNCOLLECTABLE)
    DEBUG_SAVEALL: ClassVar[Int] = Int(_gc.DEBUG_SAVEALL)
    DEBUG_LEAK: ClassVar[Int] = Int(_gc.DEBUG_LEAK)

    @staticmethod
    def enable() -> NoneClass:
        _gc.enable()
        return none

    @staticmethod
    def disable() -> NoneClass:
        _gc.disable()
        return none

    @staticmethod
    def isenabled() -> Boolean:
        return true if _gc.isenabled() else false

    @staticmethod
    def collect(generation: Int | None = None) -> Int:
        if generation is None:
            return Int(_gc.collect())
        return Int(_gc.collect(generation._value))

    @staticmethod
    def get_threshold() -> Any:
        t = _gc.get_threshold()
        from poop.types.tuple import Tuple

        return Tuple(*(Int(v) for v in t))

    @staticmethod
    def set_threshold(
        threshold0: Int,
        threshold1: Int | None = None,
        threshold2: Int | None = None,
    ) -> NoneClass:
        args: list[int] = [threshold0._value]
        if threshold1 is not None:
            args.append(threshold1._value)
        if threshold2 is not None:
            args.append(threshold2._value)
        _gc.set_threshold(*args)
        return none

    @staticmethod
    def get_count() -> Any:
        from poop.types.tuple import Tuple

        return Tuple(*(Int(v) for v in _gc.get_count()))

    @staticmethod
    def get_stats() -> List:
        result: list[Dict] = []
        for stat in _gc.get_stats():
            d = Dict()
            for k, v in stat.items():
                from poop.types.string import Str

                d.at_put(Str(k), _wrap_value(v))
            result.append(d)
        return List(*result)

    @staticmethod
    def get_debug() -> Int:
        return Int(_gc.get_debug())

    @staticmethod
    def set_debug(flags: Int) -> NoneClass:
        _gc.set_debug(flags._value)
        return none

    @staticmethod
    def freeze() -> NoneClass:
        _gc.freeze()
        return none

    @staticmethod
    def unfreeze() -> NoneClass:
        _gc.unfreeze()
        return none

    @staticmethod
    def get_freeze_count() -> Int:
        return Int(_gc.get_freeze_count())

    @staticmethod
    def callbacks() -> Any:
        # Return the raw list — callbacks are Python callables; users
        # `.append`/`.remove` directly to register/unregister.
        return _gc.callbacks
