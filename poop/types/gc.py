from __future__ import annotations

import gc as _gc
from typing import Any, ClassVar

from poop.types._bridge import to_poop
from poop.types.boolean import Boolean, to_boolean
from poop.types.dict import Dict
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import NoneClass, none
from poop.types.tuple import Tuple


class _GCNamespace:
    """Singleton namespace mirroring (the control surface of) Python's `gc` module.

    Python `gc.callbacks` is an attribute — exposed here as `@property`.
    The introspection-heavy pieces (`get_objects` / `get_referrers` /
    `get_referents` / `is_tracked` / `is_finalized`) are out of scope.
    """

    DEBUG_STATS: ClassVar[Int] = Int(_gc.DEBUG_STATS)
    DEBUG_COLLECTABLE: ClassVar[Int] = Int(_gc.DEBUG_COLLECTABLE)
    DEBUG_UNCOLLECTABLE: ClassVar[Int] = Int(_gc.DEBUG_UNCOLLECTABLE)
    DEBUG_SAVEALL: ClassVar[Int] = Int(_gc.DEBUG_SAVEALL)
    DEBUG_LEAK: ClassVar[Int] = Int(_gc.DEBUG_LEAK)

    def enable(self) -> NoneClass:
        _gc.enable()
        return none

    def disable(self) -> NoneClass:
        _gc.disable()
        return none

    def isenabled(self) -> Boolean:
        return to_boolean(_gc.isenabled())

    def collect(self, generation: Int | None = None) -> Int:
        if generation is None:
            return Int(_gc.collect())
        return Int(_gc.collect(generation._value))

    def get_threshold(self) -> Tuple:
        return Tuple(*(Int(v) for v in _gc.get_threshold()))

    def set_threshold(
        self,
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

    def get_count(self) -> Tuple:
        return Tuple(*(Int(v) for v in _gc.get_count()))

    def get_stats(self) -> List:
        result: list[Dict] = []
        for stat in _gc.get_stats():
            d = Dict()
            for k, v in stat.items():
                from poop.types.string import Str

                d.at_put(Str(k), to_poop(v))
            result.append(d)
        return List(*result)

    def get_debug(self) -> Int:
        return Int(_gc.get_debug())

    def set_debug(self, flags: Int) -> NoneClass:
        _gc.set_debug(flags._value)
        return none

    def freeze(self) -> NoneClass:
        _gc.freeze()
        return none

    def unfreeze(self) -> NoneClass:
        _gc.unfreeze()
        return none

    def get_freeze_count(self) -> Int:
        return Int(_gc.get_freeze_count())

    @property
    def callbacks(self) -> Any:
        # Raw list — callbacks are Python callables; users `.append`/
        # `.remove` directly to register/unregister.
        return _gc.callbacks


GC = _GCNamespace()
