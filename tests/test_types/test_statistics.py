import pytest

from poop.interpreter import Interpreter
from poop.types.float import Float
from poop.types.int import Int
from poop.types.list import List
from poop.types.statistics import NormalDist, Statistics
from poop.types.string import Str
from poop.types.tuple import Tuple

# --- Central tendency ---


def test_mean_simple() -> None:
    assert Statistics.mean(List(Int(1), Int(2), Int(3), Int(4))) == Float(2.5)


def test_mean_over_fractions_answers_fraction() -> None:
    # proposal 129: exact-rational input must not leak a raw Fraction.
    from poop.types.fractions import Fraction

    data = List(Fraction(Str("1/4")), Fraction(Str("1/2")), Fraction(Str("3/4")))
    result = Statistics.mean(data)
    assert isinstance(result, Fraction)
    assert result == Fraction(Int(1), Int(2))


def test_median_over_fractions_answers_fraction() -> None:
    from poop.types.fractions import Fraction

    data = List(Fraction(Str("1/4")), Fraction(Str("1/2")), Fraction(Str("3/4")))
    assert isinstance(Statistics.median(data), Fraction)


# Decimal data — proposal 130


def test_mean_over_decimals_answers_decimal() -> None:
    from poop.types.decimal import Decimal

    data = List(Decimal(Str("1.5")), Decimal(Str("2.5")))
    result = Statistics.mean(data)
    assert isinstance(result, Decimal)
    assert result == Decimal(Str("2"))


def test_median_over_decimals_answers_decimal() -> None:
    from poop.types.decimal import Decimal

    data = List(Decimal(Str("1")), Decimal(Str("3")))
    result = Statistics.median(data)
    assert isinstance(result, Decimal)
    assert result == Decimal(Str("2"))


def test_stdev_over_decimals_answers_decimal() -> None:
    from poop.types.decimal import Decimal

    data = List(Decimal(Str("1")), Decimal(Str("3")))
    assert isinstance(Statistics.stdev(data), Decimal)


def test_fmean_over_decimals_answers_float() -> None:
    from poop.types.decimal import Decimal

    data = List(Decimal(Str("1.5")), Decimal(Str("2.5")))
    assert Statistics.fmean(data) == Float(2.0)


def test_fmean_returns_float() -> None:
    result = Statistics.fmean(List(Int(1), Int(2), Int(3)))
    assert isinstance(result, Float)
    assert result == Float(2.0)


def test_fmean_with_weights() -> None:
    weights = List(Float(1.0), Float(2.0), Float(3.0))
    result = Statistics.fmean(List(Int(1), Int(2), Int(3)), weights)
    assert isinstance(result, Float)


def test_geometric_mean() -> None:
    result = Statistics.geometric_mean(List(Float(1.0), Float(8.0), Float(27.0)))
    assert isinstance(result, Float)


def test_harmonic_mean() -> None:
    result = Statistics.harmonic_mean(List(Float(1.0), Float(2.0), Float(4.0)))
    assert isinstance(result, Float)


def test_median_odd() -> None:
    assert Statistics.median(List(Int(1), Int(3), Int(5))) == Int(3)


def test_median_even_returns_float() -> None:
    assert Statistics.median(List(Int(1), Int(2), Int(3), Int(4))) == Float(2.5)


def test_median_low() -> None:
    assert Statistics.median_low(List(Int(1), Int(2), Int(3), Int(4))) == Int(2)


def test_median_high() -> None:
    assert Statistics.median_high(List(Int(1), Int(2), Int(3), Int(4))) == Int(3)


def test_median_grouped() -> None:
    result = Statistics.median_grouped(
        List(Float(1.0), Float(2.0), Float(2.0), Float(3.0))
    )
    assert isinstance(result, Float)


def test_mode_single() -> None:
    assert Statistics.mode(List(Int(1), Int(2), Int(2), Int(3))) == Int(2)


def test_mode_str() -> None:
    result = Statistics.mode(List(Str("a"), Str("b"), Str("b"), Str("c")))
    assert result == Str("b")


def test_multimode_two() -> None:
    result = Statistics.multimode(List(Int(1), Int(1), Int(2), Int(2), Int(3)))
    assert isinstance(result, List)
    assert result == List(Int(1), Int(2))


# --- Spread ---


def test_pstdev() -> None:
    result = Statistics.pstdev(List(Int(1), Int(2), Int(3), Int(4), Int(5)))
    assert isinstance(result, Float)


def test_pvariance() -> None:
    result = Statistics.pvariance(List(Int(1), Int(2), Int(3), Int(4), Int(5)))
    assert isinstance(result, Float)
    assert result == Float(2.0)


def test_stdev() -> None:
    result = Statistics.stdev(List(Int(1), Int(2), Int(3), Int(4), Int(5)))
    assert isinstance(result, Float)


def test_variance() -> None:
    result = Statistics.variance(List(Int(1), Int(2), Int(3), Int(4), Int(5)))
    assert isinstance(result, Float)
    assert result == Float(2.5)


def test_pstdev_with_mu() -> None:
    result = Statistics.pstdev(List(Int(1), Int(2), Int(3)), mu=Float(2.0))
    assert isinstance(result, Float)


# --- Quantiles ---


def test_quantiles_default() -> None:
    result = Statistics.quantiles(
        List(Int(1), Int(2), Int(3), Int(4), Int(5), Int(6), Int(7), Int(8))
    )
    assert isinstance(result, List)
    assert result.len() == Int(3)


def test_quantiles_explicit_n() -> None:
    result = Statistics.quantiles(
        List(Int(1), Int(2), Int(3), Int(4), Int(5)), n=Int(2)
    )
    assert result.len() == Int(1)


def test_quantiles_method_inclusive() -> None:
    result = Statistics.quantiles(
        List(Int(1), Int(2), Int(3), Int(4), Int(5)), method=Str("inclusive")
    )
    assert isinstance(result, List)


# --- Correlation ---


def test_correlation_linear() -> None:
    x = List(Int(1), Int(2), Int(3), Int(4))
    y = List(Int(2), Int(4), Int(6), Int(8))
    result = Statistics.correlation(x, y)
    assert isinstance(result, Float)
    assert result == Float(1.0)


def test_covariance() -> None:
    x = List(Int(1), Int(2), Int(3), Int(4))
    y = List(Int(1), Int(2), Int(3), Int(4))
    result = Statistics.covariance(x, y)
    assert isinstance(result, Float)


def test_linear_regression() -> None:
    x = List(Int(1), Int(2), Int(3), Int(4))
    y = List(Int(2), Int(4), Int(6), Int(8))
    result = Statistics.linear_regression(x, y)
    assert isinstance(result, Tuple)
    # slope ~ 2, intercept ~ 0
    slope = result.at(Int(0))
    intercept = result.at(Int(1))
    assert isinstance(slope, Float)
    assert isinstance(intercept, Float)
    assert abs(slope._value - 2.0) < 1e-9


def test_linear_regression_proportional() -> None:
    from poop.types.boolean import true

    x = List(Int(1), Int(2), Int(3))
    y = List(Int(2), Int(4), Int(6))
    result = Statistics.linear_regression(x, y, proportional=true)
    assert isinstance(result, Tuple)


# --- NormalDist class ---


def test_normaldist_defaults() -> None:
    nd = NormalDist()
    assert nd.mean == Float(0.0)
    assert nd.stdev == Float(1.0)


def test_normaldist_with_params() -> None:
    nd = NormalDist(Float(5.0), Float(2.0))
    assert nd.mean == Float(5.0)
    assert nd.stdev == Float(2.0)
    assert nd.variance == Float(4.0)


def test_normaldist_from_samples() -> None:
    data = List(Float(1.0), Float(2.0), Float(3.0), Float(4.0), Float(5.0))
    nd = NormalDist.from_samples(data)
    assert isinstance(nd, NormalDist)
    assert isinstance(nd.mean, Float)


def test_normaldist_cdf() -> None:
    nd = NormalDist()
    assert isinstance(nd.cdf(Float(0.0)), Float)
    assert abs(nd.cdf(Float(0.0))._value - 0.5) < 1e-9


def test_normaldist_pdf() -> None:
    nd = NormalDist()
    result = nd.pdf(Float(0.0))
    assert isinstance(result, Float)


def test_normaldist_inv_cdf() -> None:
    nd = NormalDist()
    result = nd.inv_cdf(Float(0.5))
    assert isinstance(result, Float)
    assert abs(result._value) < 1e-9


def test_normaldist_zscore() -> None:
    nd = NormalDist(Float(10.0), Float(2.0))
    assert nd.zscore(Float(12.0)) == Float(1.0)


def test_normaldist_samples_size() -> None:
    nd = NormalDist()
    samples = nd.samples(Int(50), seed=Int(42))
    assert isinstance(samples, List)
    assert samples.len() == Int(50)


def test_normaldist_overlap() -> None:
    a = NormalDist(Float(0.0), Float(1.0))
    b = NormalDist(Float(1.0), Float(1.0))
    result = a.overlap(b)
    assert isinstance(result, Float)
    assert 0.0 < result._value < 1.0


def test_normaldist_quantiles_default() -> None:
    nd = NormalDist()
    result = nd.quantiles()
    assert isinstance(result, List)
    assert result.len() == Int(3)


def test_normaldist_addition() -> None:
    a = NormalDist(Float(1.0), Float(1.0))
    b = NormalDist(Float(2.0), Float(1.0))
    result = a + b
    assert isinstance(result, NormalDist)
    assert result.mean == Float(3.0)


def test_normaldist_scaling() -> None:
    nd = NormalDist(Float(1.0), Float(2.0))
    scaled = nd * Float(3.0)
    assert isinstance(scaled, NormalDist)
    assert scaled.mean == Float(3.0)


def test_normaldist_shift_by_int() -> None:
    nd = NormalDist(Float(1.0), Float(1.0))
    shifted = nd + Int(5)
    assert shifted.mean == Float(6.0)


# --- Errors ---


def test_empty_mean_raises_statistics_error() -> None:
    with pytest.raises(Statistics.StatisticsError):
        Statistics.mean(List())


def test_stdev_too_few_raises() -> None:
    with pytest.raises(Statistics.StatisticsError):
        Statistics.stdev(List(Int(1)))


# --- _to_number / _wrap_result branches ---


def test_mode_with_booleans() -> None:
    from poop.types.boolean import false, true

    data = List(true, true, false)
    result = Statistics.mode(data)
    # _wrap_result converts python bools to POOP booleans.
    assert result is true


def test_harmonic_mean_with_weights() -> None:
    data = List(Float(1.0), Float(2.0), Float(4.0))
    weights = List(Float(1.0), Float(1.0), Float(1.0))
    result = Statistics.harmonic_mean(data, weights)
    assert isinstance(result, Float)


def test_variance_with_xbar() -> None:
    data = List(Int(1), Int(2), Int(3), Int(4), Int(5))
    result = Statistics.variance(data, xbar=Float(3.0))
    assert isinstance(result, Float)


def test_pvariance_with_mu() -> None:
    data = List(Int(1), Int(2), Int(3))
    result = Statistics.pvariance(data, mu=Float(2.0))
    assert isinstance(result, Float)


def test_stdev_with_xbar() -> None:
    data = List(Int(1), Int(2), Int(3))
    result = Statistics.stdev(data, xbar=Float(2.0))
    assert isinstance(result, Float)


def test_median_grouped_default_interval() -> None:
    result = Statistics.median_grouped(
        List(Float(1.0), Float(2.0), Float(2.0), Float(3.0))
    )
    assert isinstance(result, Float)


def test_correlation_with_method() -> None:
    x = List(Int(1), Int(2), Int(3), Int(4))
    y = List(Int(1), Int(2), Int(3), Int(4))
    result = Statistics.correlation(x, y, method=Str("ranked"))
    assert isinstance(result, Float)


# --- NormalDist extra coverage ---


def test_normaldist_subtraction() -> None:
    a = NormalDist(Float(5.0), Float(1.0))
    b = NormalDist(Float(3.0), Float(1.0))
    result = a - b
    assert result.mean == Float(2.0)


def test_normaldist_sub_scalar() -> None:
    nd = NormalDist(Float(5.0), Float(1.0))
    result = nd - Float(2.0)
    assert result.mean == Float(3.0)


def test_normaldist_radd_via_dunder() -> None:
    # Float doesn't return NotImplemented for non-Float types, so
    # `Float + NormalDist` won't reach __radd__. Test the dunder
    # directly.
    nd = NormalDist(Float(5.0), Float(1.0))
    result = nd.__radd__(Float(2.0))
    assert result.mean == Float(7.0)


def test_normaldist_rmul_via_dunder() -> None:
    nd = NormalDist(Float(1.0), Float(1.0))
    result = nd.__rmul__(Float(3.0))
    assert result.mean == Float(3.0)


def test_normaldist_truediv_scalar() -> None:
    nd = NormalDist(Float(6.0), Float(2.0))
    result = nd / Float(2.0)
    assert result.mean == Float(3.0)


def test_normaldist_equality() -> None:
    a = NormalDist(Float(1.0), Float(2.0))
    b = NormalDist(Float(1.0), Float(2.0))
    c = NormalDist(Float(2.0), Float(2.0))
    from poop.types.boolean import false, true

    assert (a == b) is true
    assert (a != c) is true
    assert (a == Int(0)) is false
    assert (a != Int(0)) is true


def test_normaldist_repr_matches_str() -> None:
    nd = NormalDist()
    assert repr(nd) == str(nd)


def test_normaldist_quantiles_explicit_n() -> None:
    nd = NormalDist()
    result = nd.quantiles(Int(2))
    assert result.len() == Int(1)


def test_normaldist_samples_no_seed() -> None:
    nd = NormalDist()
    result = nd.samples(Int(5))
    assert result.len() == Int(5)


def test_normaldist_median_mode() -> None:
    nd = NormalDist(Float(5.0), Float(1.0))
    assert nd.median == Float(5.0)
    assert nd.mode == Float(5.0)


def test_normaldist_hash() -> None:
    a = NormalDist(Float(1.0), Float(2.0))
    b = NormalDist(Float(1.0), Float(2.0))
    assert hash(a) == hash(b)


# --- Interpreter integration ---


def test_statistics_mean_reachable_via_interpreter() -> None:
    Interpreter().run_source("statistics.mean([1, 2, 3, 4]).print()")


def test_statistics_median_reachable_via_interpreter() -> None:
    Interpreter().run_source("statistics.median([1, 2, 3]).print()")


def test_NormalDist_reachable_via_interpreter() -> None:
    Interpreter().run_source("NormalDist(0.0, 1.0).cdf(0.0).print()")
