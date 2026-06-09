from typing import Any

from poop.interpreter import Interpreter
from poop.types.block import Block
from poop.types.dict import Dict
from poop.types.functools import FunctoolsNamespace, Partial
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import none
from poop.types.string import Str
from poop.types.tuple import Tuple

# --- partial ---


def test_partial_freezes_leading_args() -> None:
    double = Partial(lambda a, b: a * b, Int(2))
    assert double(Int(21)) == Int(42)


def test_partial_freezes_keyword_args() -> None:
    greet = Partial(lambda name, greeting: greeting + name, greeting=Str("Olá, "))
    assert greet(Str("Ana")) == Str("Olá, Ana")


def test_partial_call_kwargs_override_frozen() -> None:
    p = Partial(lambda x=None: x, x=Int(1))
    assert p(x=Int(2)) == Int(2)


def test_partial_over_bound_method_of_poop_type() -> None:
    strip = Partial(Str("  hi  ").strip)
    assert strip() == Str("hi")


def test_partial_over_bound_method_of_user_object() -> None:
    class Account:
        def __init__(self) -> None:
            self.balance: Any = Int(0)

        def deposit(self, amount: Int) -> Any:
            self.balance = self.balance + amount
            return self.balance

    account = Account()
    deposit_100 = Partial(account.deposit, Int(100))
    assert deposit_100() == Int(100)
    assert deposit_100() == Int(200)


def test_partial_over_constructor() -> None:
    p = Partial(Tuple, Int(1))
    assert p(Int(2)) == Tuple(Int(1), Int(2))


def test_partial_of_partial() -> None:
    add = Partial(lambda a, b, c: a + b + c, Int(1))
    add_more = Partial(add, Int(2))
    assert add_more(Int(3)) == Int(6)


def test_partial_func_args_keywords_properties() -> None:
    fn = Str("x").join
    p = Partial(fn, kw=Int(1))
    assert p.func is fn
    assert p.args == Tuple()
    assert isinstance(p.keywords, Dict)
    assert p.keywords.at(Str("kw")) == Int(1)


def test_partial_args_property_wraps_tuple() -> None:
    p = Partial(lambda a, b: a, Int(1))
    assert p.args == Tuple(Int(1))


def test_partial_masquerades_python_name() -> None:
    p = Partial(lambda: none)
    assert type(p).__name__ == "partial"
    assert "functools.partial" in str(p)


# --- cmp_to_key ---


def test_cmp_to_key_orders_with_comparison_block() -> None:
    key = FunctoolsNamespace.cmp_to_key(lambda a, b: b - a)
    result = List(Int(1), Int(3), Int(2)).sorted(key=key)
    assert result == List(Int(3), Int(2), Int(1))


def test_cmp_to_key_returns_block() -> None:
    assert isinstance(FunctoolsNamespace.cmp_to_key(lambda a, b: a - b), Block)


# --- reduce ---


def test_reduce_with_init() -> None:
    total = FunctoolsNamespace.reduce(
        lambda acc, x: acc + x, List(Int(1), Int(2)), Int(10)
    )
    assert total == Int(13)


def test_reduce_without_init_uses_first_element() -> None:
    total = FunctoolsNamespace.reduce(lambda acc, x: acc + x, List(Int(1), Int(2)))
    assert total == Int(3)


def test_reduce_treats_poop_none_init_as_absent() -> None:
    total = FunctoolsNamespace.reduce(lambda acc, x: acc + x, List(Int(5)), none)
    assert total == Int(5)


# --- cache / lru_cache ---


def test_cache_memoizes_calls() -> None:
    calls: list[Int] = []

    def expensive(n: Int) -> Any:
        calls.append(n)
        return n * n

    cached = FunctoolsNamespace.cache(expensive)
    assert cached(Int(3)) == Int(9)
    assert cached(Int(3)) == Int(9)
    assert len(calls) == 1


def test_cache_returns_block() -> None:
    assert isinstance(FunctoolsNamespace.cache(lambda n: n), Block)


def test_lru_cache_memoizes_calls() -> None:
    calls: list[Int] = []

    def expensive(n: Int) -> Any:
        calls.append(n)
        return n + n

    cached = FunctoolsNamespace.lru_cache(expensive)
    assert cached(Int(2)) == Int(4)
    assert cached(Int(2)) == Int(4)
    assert len(calls) == 1


def test_lru_cache_respects_maxsize() -> None:
    calls: list[Int] = []

    def expensive(n: Int) -> Int:
        calls.append(n)
        return n

    cached = FunctoolsNamespace.lru_cache(expensive, maxsize=Int(1))
    cached(Int(1))
    cached(Int(2))  # evicts 1
    cached(Int(1))  # recomputes
    assert len(calls) == 3


# --- Interpreter integration ---


def test_partial_via_interpreter() -> None:
    Interpreter().run_source(
        'saudar = partial(lambda s, n: s + n, "Olá, ")\nsaudar("Ana").print()'
    )


def test_partial_of_bound_method_via_interpreter() -> None:
    Interpreter().run_source('limpar = partial("  oi  ".strip)\nlimpar().print()')


def test_functools_namespace_via_interpreter() -> None:
    Interpreter().run_source(
        "total = functools.reduce(lambda acc, x: acc + x, [1, 2, 3], 0)\ntotal.print()"
    )


def test_cache_via_interpreter() -> None:
    Interpreter().run_source(
        "quadrado = functools.cache(lambda n: n * n)\nquadrado(4).print()"
    )
