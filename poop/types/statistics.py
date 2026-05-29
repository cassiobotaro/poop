from __future__ import annotations

import statistics as _statistics
from typing import Any, ClassVar

from poop.types._impl_wrapper import _ImplWrapperMixin
from poop.types._unwrap import _kwargs_from
from poop.types.boolean import Boolean, false, true
from poop.types.float import Float
from poop.types.fractions import Fraction
from poop.types.int import Int
from poop.types.list import List
from poop.types.object import Object
from poop.types.string import Str
from poop.types.tuple import Tuple


def _to_number(value: Object) -> Any:
    if isinstance(value, Int | Float | Str):
        return value._value
    if isinstance(value, Fraction):
        return value._impl
    if isinstance(value, Boolean):
        return bool(value)
    return value


def _unwrap_data(data: List | Tuple) -> list[Any]:
    return [_to_number(v) for v in data]


def _opt_unwrap(value: Float | Int | None) -> Any:
    if value is None:
        return None
    return value._value


def _wrap_result(value: Any) -> Any:
    # `mean`, `stdev`, etc. return floats; `median*` may return int or
    # float depending on the data; `mode`/`multimode` return whatever
    # the data carries.
    if isinstance(value, bool):
        return true if value else false
    if isinstance(value, float):
        return Float(value)
    if isinstance(value, int):
        return Int(value)
    if isinstance(value, str):
        return Str(value)
    return value


class NormalDist(_ImplWrapperMixin):
    """Wraps Python's `statistics.NormalDist` — a normal distribution.

    Construct with `(mu=0.0, sigma=1.0)`, sample with `.samples(n)`,
    query densities and quantiles, and combine two `NormalDist`s with
    `+`/`-`/`*`/`/` for affine transformations.
    """

    __slots__ = ("_impl",)

    def __init__(self, mu: Float | None = None, sigma: Float | None = None) -> None:
        kwargs: dict[str, float] = {}
        kwargs.update(_kwargs_from(mu=mu, sigma=sigma))
        self._impl = _statistics.NormalDist(**kwargs)

    @classmethod
    def from_samples(cls, data: List | Tuple) -> NormalDist:
        return cls._from_impl(_statistics.NormalDist.from_samples(_unwrap_data(data)))

    @property
    def mean(self) -> Float:
        return Float(self._impl.mean)

    @property
    def stdev(self) -> Float:
        return Float(self._impl.stdev)

    @property
    def variance(self) -> Float:
        return Float(self._impl.variance)

    @property
    def median(self) -> Float:
        return Float(self._impl.median)

    @property
    def mode(self) -> Float:
        return Float(self._impl.mode)

    def cdf(self, x: Float | Int) -> Float:
        return Float(self._impl.cdf(_to_number(x)))

    def pdf(self, x: Float | Int) -> Float:
        return Float(self._impl.pdf(_to_number(x)))

    def inv_cdf(self, p: Float) -> Float:
        return Float(self._impl.inv_cdf(p._value))

    def zscore(self, x: Float | Int) -> Float:
        return Float(self._impl.zscore(_to_number(x)))

    def samples(self, n: Int, seed: Int | None = None) -> List:
        kwargs = _kwargs_from(seed=seed)
        return List(*(Float(s) for s in self._impl.samples(n._value, **kwargs)))

    def overlap(self, other: NormalDist) -> Float:
        return Float(self._impl.overlap(other._impl))

    def quantiles(self, n: Int | None = None) -> List:
        kwargs: dict[str, int] = {}
        if n is not None:
            kwargs["n"] = n._value
        return List(*(Float(q) for q in self._impl.quantiles(**kwargs)))

    # Affine arithmetic between NormalDist instances --------------------

    def __add__(self, other: NormalDist | Float | Int) -> NormalDist:
        if isinstance(other, NormalDist):
            return NormalDist._from_impl(self._impl + other._impl)
        return NormalDist._from_impl(self._impl + _to_number(other))

    def __radd__(self, other: Float | Int) -> NormalDist:
        return NormalDist._from_impl(_to_number(other) + self._impl)

    def __sub__(self, other: NormalDist | Float | Int) -> NormalDist:
        if isinstance(other, NormalDist):
            return NormalDist._from_impl(self._impl - other._impl)
        return NormalDist._from_impl(self._impl - _to_number(other))

    def __mul__(self, other: Float | Int) -> NormalDist:
        return NormalDist._from_impl(self._impl * _to_number(other))

    def __rmul__(self, other: Float | Int) -> NormalDist:
        return NormalDist._from_impl(_to_number(other) * self._impl)

    def __truediv__(self, other: Float | Int) -> NormalDist:
        return NormalDist._from_impl(self._impl / _to_number(other))

    def __eq__(self, other: object) -> Boolean:
        if not isinstance(other, NormalDist):
            return false
        return true if self._impl == other._impl else false

    def __ne__(self, other: object) -> Boolean:
        if not isinstance(other, NormalDist):
            return true
        return false if self._impl == other._impl else true

    def __hash__(self) -> int:
        return hash(self._impl)

    def __str__(self) -> str:
        return str(self._impl)

    __repr__ = __str__


class Statistics:
    """Namespace mirroring Python's `statistics` module.

    Module-level helpers cover central tendency (`mean` / `fmean` /
    `geometric_mean` / `harmonic_mean` / `median*` / `mode` /
    `multimode`), spread (`pstdev` / `pvariance` / `stdev` /
    `variance`), quantiles, and correlation primitives
    (`correlation` / `covariance` / `linear_regression`).
    `NormalDist` is exposed bare alongside this namespace.

    `StatisticsError` is the Python exception class for `Try.except_`.
    The `_sum` private helper is out of scope.
    """

    NormalDist: ClassVar[type[NormalDist]] = NormalDist
    StatisticsError: ClassVar[type[Exception]] = _statistics.StatisticsError

    # Central tendency ---------------------------------------------------

    @staticmethod
    def mean(data: List | Tuple) -> Any:
        return _wrap_result(_statistics.mean(_unwrap_data(data)))

    @staticmethod
    def fmean(
        data: List | Tuple,
        weights: List | Tuple | None = None,
    ) -> Float:
        if weights is None:
            return Float(_statistics.fmean(_unwrap_data(data)))
        return Float(_statistics.fmean(_unwrap_data(data), _unwrap_data(weights)))

    @staticmethod
    def geometric_mean(data: List | Tuple) -> Float:
        return Float(_statistics.geometric_mean(_unwrap_data(data)))

    @staticmethod
    def harmonic_mean(
        data: List | Tuple,
        weights: List | Tuple | None = None,
    ) -> Float:
        if weights is None:
            return Float(_statistics.harmonic_mean(_unwrap_data(data)))
        return Float(
            _statistics.harmonic_mean(_unwrap_data(data), _unwrap_data(weights))
        )

    @staticmethod
    def median(data: List | Tuple) -> Any:
        return _wrap_result(_statistics.median(_unwrap_data(data)))

    @staticmethod
    def median_low(data: List | Tuple) -> Any:
        return _wrap_result(_statistics.median_low(_unwrap_data(data)))

    @staticmethod
    def median_high(data: List | Tuple) -> Any:
        return _wrap_result(_statistics.median_high(_unwrap_data(data)))

    @staticmethod
    def median_grouped(
        data: List | Tuple,
        interval: Float | Int | None = None,
    ) -> Float:
        if interval is None:
            return Float(_statistics.median_grouped(_unwrap_data(data)))
        return Float(
            _statistics.median_grouped(_unwrap_data(data), _to_number(interval))
        )

    @staticmethod
    def mode(data: List | Tuple) -> Any:
        return _wrap_result(_statistics.mode(_unwrap_data(data)))

    @staticmethod
    def multimode(data: List | Tuple) -> List:
        return List(
            *(_wrap_result(v) for v in _statistics.multimode(_unwrap_data(data)))
        )

    # Spread -------------------------------------------------------------

    @staticmethod
    def pstdev(data: List | Tuple, mu: Float | Int | None = None) -> Float:
        return Float(_statistics.pstdev(_unwrap_data(data), _opt_unwrap(mu)))

    @staticmethod
    def pvariance(data: List | Tuple, mu: Float | Int | None = None) -> Float:
        return Float(_statistics.pvariance(_unwrap_data(data), _opt_unwrap(mu)))

    @staticmethod
    def stdev(data: List | Tuple, xbar: Float | Int | None = None) -> Float:
        return Float(_statistics.stdev(_unwrap_data(data), _opt_unwrap(xbar)))

    @staticmethod
    def variance(data: List | Tuple, xbar: Float | Int | None = None) -> Float:
        return Float(_statistics.variance(_unwrap_data(data), _opt_unwrap(xbar)))

    # Quantiles ----------------------------------------------------------

    @staticmethod
    def quantiles(
        data: List | Tuple,
        n: Int | None = None,
        method: Str | None = None,
    ) -> List:
        kwargs = _kwargs_from(n=n, method=method)
        return List(
            *(Float(q) for q in _statistics.quantiles(_unwrap_data(data), **kwargs))
        )

    # Correlation --------------------------------------------------------

    @staticmethod
    def correlation(
        x: List | Tuple,
        y: List | Tuple,
        method: Str | None = None,
    ) -> Float:
        kwargs = _kwargs_from(method=method)
        return Float(
            _statistics.correlation(_unwrap_data(x), _unwrap_data(y), **kwargs)
        )

    @staticmethod
    def covariance(x: List | Tuple, y: List | Tuple) -> Float:
        return Float(_statistics.covariance(_unwrap_data(x), _unwrap_data(y)))

    @staticmethod
    def linear_regression(
        x: List | Tuple,
        y: List | Tuple,
        proportional: Boolean | None = None,
    ) -> Tuple:
        kwargs: dict[str, Any] = {}
        if proportional is not None:
            kwargs["proportional"] = bool(proportional)
        slope, intercept = _statistics.linear_regression(
            _unwrap_data(x), _unwrap_data(y), **kwargs
        )
        return Tuple(Float(slope), Float(intercept))
