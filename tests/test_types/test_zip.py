import pytest

from poop.parser import parse
from poop.transformers.boolean import BooleanTransformer
from poop.transformers.int import IntTransformer
from poop.transformers.list import ListTransformer
from poop.transformers.zip import ZipTransformer, _poop_zip
from poop.types.boolean import false, true
from poop.types.int import Int
from poop.types.int import Int as _Int
from poop.types.list import List
from poop.types.range import Range
from poop.types.string import Str
from poop.types.tuple import Tuple
from poop.types.zip import Zip


def test_zip_two_lists() -> None:
    result = list(List(Int(1), Int(2)).zip(List(Str("a"), Str("b"))))
    assert result == [Tuple(Int(1), Str("a")), Tuple(Int(2), Str("b"))]


def test_zip_three_iterables() -> None:
    a = List(Int(1), Int(2))
    b = List(Int(3), Int(4))
    c = List(Int(5), Int(6))
    result = list(a.zip(b, c))
    assert result == [Tuple(Int(1), Int(3), Int(5)), Tuple(Int(2), Int(4), Int(6))]


def test_zip_stops_at_shortest() -> None:
    result = list(List(Int(1), Int(2), Int(3)).zip(List(Str("a"))))
    assert result == [Tuple(Int(1), Str("a"))]


def test_zip_empty() -> None:
    assert list(List().zip(List(Int(1)))) == []


def test_zip_strict_equal_lengths() -> None:
    result = list(List(Int(1), Int(2)).zip(List(Int(3), Int(4)), strict=true))
    assert result == [Tuple(Int(1), Int(3)), Tuple(Int(2), Int(4))]


def test_zip_strict_unequal_raises() -> None:
    z = List(Int(1), Int(2)).zip(List(Int(3)), strict=true)
    with pytest.raises(ValueError):
        list(z)


def test_zip_returns_zip_instance() -> None:
    assert isinstance(List(Int(1)).zip(List(Int(2))), Zip)


def test_zip_is_one_shot() -> None:
    # Matches Python's zip: once exhausted, further iteration is empty.
    z = List(Int(1), Int(2)).zip(List(Str("a"), Str("b")))
    first = list(z)
    second = list(z)
    assert first == [Tuple(Int(1), Str("a")), Tuple(Int(2), Str("b"))]
    assert second == []


def test_zip_do() -> None:
    seen: list[Tuple] = []
    List(Int(1), Int(2)).zip(List(Str("a"), Str("b"))).do(lambda t: seen.append(t))
    assert seen == [Tuple(Int(1), Str("a")), Tuple(Int(2), Str("b"))]


def test_zip_map() -> None:
    result = (
        List(Int(1), Int(2)).zip(List(Int(10), Int(20))).map(lambda t: t.at(Int(0)))
    )
    assert List(*result) == List(Int(1), Int(2))


def test_zip_on_range() -> None:
    result = list(Range(Int(1), Int(3)).zip(List(Str("a"), Str("b"), Str("c"))))
    assert result == [
        Tuple(Int(1), Str("a")),
        Tuple(Int(2), Str("b")),
        Tuple(Int(3), Str("c")),
    ]


def test_zip_eq_identity() -> None:
    z = List(Int(1)).zip(List(Int(2)))
    assert (z == z) is true
    assert (z == List(Int(1)).zip(List(Int(2)))) is false


def test_zip_ne_different() -> None:
    z1 = List(Int(1)).zip(List(Int(2)))
    z2 = List(Int(1)).zip(List(Int(2)))
    assert (z1 != z2) is true


def test_zip_str() -> None:
    assert str(List(Int(1)).zip(List(Int(2)))) == "<zip>"


def test_zip_rejects_non_iterable_source() -> None:
    with pytest.raises(TypeError, match="'int' object is not iterable"):
        Zip(Int(42), List(Int(1)))


def test_transformer_two_args() -> None:
    tree = parse("z = zip([1], [2])")
    tree = IntTransformer().transform(tree)
    tree = ListTransformer().transform(tree)
    tree = ZipTransformer().transform(tree)
    ns: dict[str, object] = {
        "_poop_zip": _poop_zip,
        "_poop_int": _Int,
        "_poop_list": List,
    }
    exec(compile(tree, "<test>", "exec"), ns)  # noqa: S102
    assert isinstance(ns["z"], Zip)


def test_transformer_three_args() -> None:
    tree = parse("z = zip([1], [2], [3])")
    tree = IntTransformer().transform(tree)
    tree = ListTransformer().transform(tree)
    tree = ZipTransformer().transform(tree)
    ns: dict[str, object] = {
        "_poop_zip": _poop_zip,
        "_poop_int": _Int,
        "_poop_list": List,
    }
    exec(compile(tree, "<test>", "exec"), ns)  # noqa: S102
    z = ns["z"]
    assert isinstance(z, Zip)
    assert list(z) == [Tuple(Int(1), Int(2), Int(3))]


def test_transformer_strict_true() -> None:
    tree = parse("z = zip([1, 2], [3, 4], strict=True)")
    tree = BooleanTransformer().transform(tree)
    tree = IntTransformer().transform(tree)
    tree = ListTransformer().transform(tree)
    tree = ZipTransformer().transform(tree)
    ns: dict[str, object] = {
        "_poop_zip": _poop_zip,
        "_poop_true": true,
        "_poop_false": false,
        "_poop_int": _Int,
        "_poop_list": List,
    }
    exec(compile(tree, "<test>", "exec"), ns)  # noqa: S102
    z = ns["z"]
    assert isinstance(z, Zip)
    result = list(z)  # type: ignore[arg-type]
    assert result == [Tuple(Int(1), Int(3)), Tuple(Int(2), Int(4))]


def test_transformer_strict_unequal_raises() -> None:
    tree = parse("z = zip([1], [2, 3], strict=True)")
    tree = BooleanTransformer().transform(tree)
    tree = IntTransformer().transform(tree)
    tree = ListTransformer().transform(tree)
    tree = ZipTransformer().transform(tree)
    ns: dict[str, object] = {
        "_poop_zip": _poop_zip,
        "_poop_true": true,
        "_poop_false": false,
        "_poop_int": _Int,
        "_poop_list": List,
    }
    exec(compile(tree, "<test>", "exec"), ns)  # noqa: S102
    z = ns["z"]
    assert isinstance(z, Zip)
    with pytest.raises(ValueError):
        list(z)


def test_iter_returns_self() -> None:
    z = List(Int(1), Int(2)).zip(List(Int(3), Int(4)))
    assert z.iter() is z


def test_next_advances() -> None:
    z = List(Int(1), Int(2)).zip(List(Int(10), Int(20)))
    assert z.next() == Tuple(Int(1), Int(10))
    assert z.next() == Tuple(Int(2), Int(20))


def test_exhaustion_raises_stop_iteration() -> None:
    z = List(Int(1)).zip(List(Int(10)))
    z.next()
    with pytest.raises(StopIteration):
        z.next()


def test_do_consumes_one_shot() -> None:
    # `.do()` iterates the Zip, consuming it; a second call yields nothing.
    z = List(Int(1), Int(2)).zip(List(Int(10), Int(20)))
    seen_a: list[Tuple] = []
    z.do(lambda t: seen_a.append(t))
    seen_b: list[Tuple] = []
    z.do(lambda t: seen_b.append(t))
    assert seen_a == [Tuple(Int(1), Int(10)), Tuple(Int(2), Int(20))]
    assert seen_b == []


def test_poop_zip_accepts_python_none_strict() -> None:
    z = _poop_zip(List(Int(1)), List(Int(2)), strict=None)
    assert z._strict is false


def test_poop_zip_accepts_poop_none_strict() -> None:
    from poop.types.none import none

    z = _poop_zip(List(Int(1)), List(Int(2)), strict=none)
    assert z._strict is false


def test_poop_zip_accepts_boolean_strict() -> None:
    z = _poop_zip(List(Int(1)), List(Int(2)), strict=true)
    assert z._strict is true


def test_poop_zip_rejects_non_boolean_strict() -> None:
    with pytest.raises(TypeError, match="strict must be Boolean, got Int"):
        _poop_zip(List(Int(1)), List(Int(2)), strict=Int(1))
