from __future__ import annotations

import functools as _functools
from typing import Any, ClassVar, cast

from poop.types._impl_wrapper import _ImplWrapperMixin
from poop.types._unwrap import _is_absent, _opt_int
from poop.types.block import Block
from poop.types.dict import Dict
from poop.types.int import Int
from poop.types.none import NoneClass, none
from poop.types.object import Object
from poop.types.string import Str
from poop.types.tuple import Tuple


class Partial(_ImplWrapperMixin, Object):
    """Wraps `functools.partial` — freeze some arguments of any
    callable and answer a new callable.

    The callable can be anything that responds to a call: a block
    (`lambda a, b: a * b`), a bound method (`account.deposit`), a
    constructor, or another `partial`. Frozen arguments stay POOP
    values — the wrapped callable receives them as-is.
    """

    __slots__ = ("_impl",)

    def __init__(self, block: Any, *args: Any, **kwargs: Any) -> None:
        self._impl = _functools.partial(block, *args, **kwargs)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self._impl(*args, **kwargs)

    @property
    def func(self) -> Any:
        return self._impl.func

    @property
    def args(self) -> Tuple:
        return Tuple(*self._impl.args)

    @property
    def keywords(self) -> Dict:
        d = Dict()
        for k, v in self._impl.keywords.items():
            d.at_put(Str(k), v)
        return d

    def __str__(self) -> str:
        return str(self._impl)

    __repr__ = __str__


Partial.__module__ = "functools"
Partial.__name__ = "partial"


class _CachedBlock(Block):
    """A memoized block — a `Block` that also answers the cache's
    bookkeeping messages."""

    __slots__ = ()

    def cache_info(self) -> Dict:
        info = cast("Any", self._fn).cache_info()
        d = Dict()
        d.at_put(Str("hits"), Int(info.hits))
        d.at_put(Str("misses"), Int(info.misses))
        d.at_put(Str("maxsize"), none if info.maxsize is None else Int(info.maxsize))
        d.at_put(Str("currsize"), Int(info.currsize))
        return d

    def cache_clear(self) -> NoneClass:
        cast("Any", self._fn).cache_clear()
        return none


class FunctoolsNamespace:
    """Namespace mirroring Python's `functools` module."""

    partial: ClassVar[type[Partial]] = Partial
    # The descriptor works untouched in a POOP class body:
    #     deposit_100 = functools.partialmethod(deposit, 100)
    partialmethod: ClassVar[type] = _functools.partialmethod

    @staticmethod
    def cmp_to_key(block: Any) -> Block:
        # The stdlib key object compares the block's return against raw
        # 0 — unwrap the POOP Int so that comparison resolves.
        def _raw_cmp(a: Any, b: Any) -> Any:
            result = block(a, b)
            return getattr(result, "_value", result)

        return Block(_functools.cmp_to_key(_raw_cmp))

    @staticmethod
    def reduce(block: Any, iterable: Any, init: Any = None) -> Any:
        if _is_absent(init):
            return _functools.reduce(block, iter(iterable))
        return _functools.reduce(block, iter(iterable), init)

    @staticmethod
    def cache(block: Any) -> _CachedBlock:
        return _CachedBlock(_functools.cache(block))

    @staticmethod
    def lru_cache(block: Any, maxsize: Any = None) -> _CachedBlock:
        # CPython's lru_cache is bounded at 128 entries by default; only an
        # explicit `none` maxsize requests an unbounded cache (that is what
        # `cache` is for). An omitted argument arrives as the Python sentinel
        # `None`, whereas a user-supplied `none` is a NoneClass that
        # `_opt_int` maps to an unbounded cache.
        size = 128 if maxsize is None else _opt_int(maxsize)
        return _CachedBlock(_functools.lru_cache(maxsize=size)(block))
