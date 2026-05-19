import pytest

from poop.parser import parse
from poop.transformers.enumerate import EnumerateTransformer, _poop_enumerate
from poop.transformers.int import IntTransformer
from poop.transformers.list import ListTransformer
from poop.transformers.range import RangeTransformer
from poop.types.boolean import false, true
from poop.types.dict import Dict
from poop.types.enumerate import Enumerate
from poop.types.int import Int
from poop.types.int import Int as _Int
from poop.types.list import List
from poop.types.range import Range
from poop.types.string import Str
from poop.types.tuple import Tuple


def test_enumerate_empty() -> None:
    result = List().enumerate()
    assert isinstance(result, Enumerate)


def test_enumerate_yields_index_value_tuples() -> None:
    e = List(Int(10), Int(20), Int(30)).enumerate()
    pairs = list(e)
    assert pairs == [
        Tuple(Int(0), Int(10)),
        Tuple(Int(1), Int(20)),
        Tuple(Int(2), Int(30)),
    ]


def test_enumerate_default_start_is_zero() -> None:
    pairs = list(List(Str("a")).enumerate())
    assert pairs[0] == Tuple(Int(0), Str("a"))


def test_enumerate_custom_start() -> None:
    pairs = list(List(Str("a"), Str("b")).enumerate(Int(5)))
    assert pairs[0] == Tuple(Int(5), Str("a"))
    assert pairs[1] == Tuple(Int(6), Str("b"))


def test_enumerate_poop_none_start_uses_default() -> None:
    from poop.types.none import none

    pairs = list(List(Str("a")).enumerate(start=none))
    assert pairs[0] == Tuple(Int(0), Str("a"))


def test_enumerate_is_one_shot() -> None:
    # Matches Python's enumerate: once exhausted, further iteration is empty.
    e = List(Int(1), Int(2)).enumerate()
    first = list(e)
    second = list(e)
    assert first == [Tuple(Int(0), Int(1)), Tuple(Int(1), Int(2))]
    assert second == []


def test_enumerate_do() -> None:
    seen: list[Tuple] = []
    List(Int(1), Int(2)).enumerate().do(lambda t: seen.append(t))
    assert seen == [Tuple(Int(0), Int(1)), Tuple(Int(1), Int(2))]


def test_enumerate_map() -> None:
    result = List(Int(10), Int(20)).enumerate().map(lambda t: t.at(Int(0)))
    assert List(*result) == List(Int(0), Int(1))


def test_enumerate_on_range() -> None:
    pairs = list(Range(Int(5), Int(7)).enumerate())
    assert pairs[0] == Tuple(Int(0), Int(5))
    assert pairs[1] == Tuple(Int(1), Int(6))
    assert pairs[2] == Tuple(Int(2), Int(7))


def test_enumerate_on_dict_iterates_keys() -> None:
    d = Dict()
    d.at_put(Str("a"), Int(1))
    d.at_put(Str("b"), Int(2))
    pairs = list(d.enumerate())
    assert pairs[0] == Tuple(Int(0), Str("a"))
    assert pairs[1] == Tuple(Int(1), Str("b"))


def test_enumerate_dict_custom_start() -> None:
    d = Dict()
    d.at_put(Str("x"), Int(0))
    pairs = list(d.enumerate(Int(3)))
    assert pairs[0] == Tuple(Int(3), Str("x"))


def test_enumerate_str_representation() -> None:
    e = List(Int(1)).enumerate()
    assert str(e) == "<enumerate>"


def test_enumerate_str_does_not_leak_start() -> None:
    e = List(Int(1)).enumerate(Int(7))
    assert str(e) == "<enumerate>"


def test_enumerate_rejects_non_iterable_source() -> None:
    with pytest.raises(TypeError, match="'int' object is not iterable"):
        Enumerate(Int(42))


def test_enumerate_eq_identity() -> None:
    e = List(Int(1)).enumerate()
    assert (e == e) is true
    assert (e == List(Int(1)).enumerate()) is false


def test_enumerate_ne_different() -> None:
    e1 = List(Int(1)).enumerate()
    e2 = List(Int(1)).enumerate()
    assert (e1 != e2) is true


def test_transformer_rewrites_enumerate_call() -> None:
    tree = parse("e = enumerate([1, 2])")
    tree = IntTransformer().transform(tree)
    tree = ListTransformer().transform(tree)
    tree = EnumerateTransformer().transform(tree)
    ns: dict[str, object] = {
        "_poop_enumerate": _poop_enumerate,
        "_poop_int": _Int,
        "_poop_list": List,
    }
    exec(compile(tree, "<test>", "exec"), ns)  # noqa: S102
    assert isinstance(ns["e"], Enumerate)


def test_transformer_enumerate_with_start() -> None:
    tree = parse("e = enumerate([1], 5)")
    tree = IntTransformer().transform(tree)
    tree = ListTransformer().transform(tree)
    tree = EnumerateTransformer().transform(tree)
    ns: dict[str, object] = {
        "_poop_enumerate": _poop_enumerate,
        "_poop_int": _Int,
        "_poop_list": List,
    }
    exec(compile(tree, "<test>", "exec"), ns)  # noqa: S102
    e = ns["e"]
    assert isinstance(e, Enumerate)
    pairs = list(e)  # type: ignore[arg-type]
    assert pairs[0] == Tuple(Int(5), Int(1))


def test_transformer_enumerate_empty_list() -> None:
    tree = parse("e = enumerate([])")
    tree = ListTransformer().transform(tree)
    tree = EnumerateTransformer().transform(tree)
    ns: dict[str, object] = {
        "_poop_enumerate": _poop_enumerate,
        "_poop_list": List,
    }
    exec(compile(tree, "<test>", "exec"), ns)  # noqa: S102
    assert isinstance(ns["e"], Enumerate)
    assert list(ns["e"]) == []  # type: ignore[arg-type]


def test_enumerate_on_range_transformer() -> None:
    tree = parse("e = enumerate(range(1, 4))")
    tree = IntTransformer().transform(tree)
    tree = RangeTransformer().transform(tree)
    tree = EnumerateTransformer().transform(tree)
    ns: dict[str, object] = {
        "_poop_enumerate": _poop_enumerate,
        "_poop_int": _Int,
        "_poop_range": __import__(
            "poop.transformers.range", fromlist=["_poop_range"]
        )._poop_range,
    }
    exec(compile(tree, "<test>", "exec"), ns)  # noqa: S102
    assert isinstance(ns["e"], Enumerate)


def test_iter_returns_self() -> None:
    e = List(Int(1), Int(2)).enumerate()
    assert e.iter() is e


def test_next_advances() -> None:
    e = List(Int(10), Int(20)).enumerate()
    assert e.next() == Tuple(Int(0), Int(10))
    assert e.next() == Tuple(Int(1), Int(20))


def test_exhaustion_raises_stop_iteration() -> None:
    import pytest

    e = List(Int(1)).enumerate()
    e.next()
    with pytest.raises(StopIteration):
        e.next()


def test_do_consumes_one_shot() -> None:
    # `.do()` iterates the Enumerate, consuming it; a second call yields nothing.
    e = List(Int(1), Int(2)).enumerate()
    seen_a: list[Tuple] = []
    e.do(lambda t: seen_a.append(t))
    seen_b: list[Tuple] = []
    e.do(lambda t: seen_b.append(t))
    assert seen_a == [Tuple(Int(0), Int(1)), Tuple(Int(1), Int(2))]
    assert seen_b == []
