from poop.interpreter import Interpreter
from poop.types.float import Float
from poop.types.int import Int
from poop.types.list import List
from poop.types.string import Str
from poop.types.timeit import TimeIt, Timer


def test_timeit_with_str_returns_float() -> None:
    result = TimeIt.timeit(Str("pass"), Str("pass"), Int(100))
    assert isinstance(result, Float)


def test_timeit_no_args_returns_float() -> None:
    # The default `number` is 1,000,000 — too slow for a unit test.
    # Force a small one.
    result = TimeIt.timeit(Str("pass"), number=Int(10))
    assert isinstance(result, Float)


def test_timeit_repeat_returns_list_of_float() -> None:
    result = TimeIt.repeat(Str("pass"), Str("pass"), Int(2), Int(10))
    assert isinstance(result, List)
    assert result.len() == Int(2)
    first = result.at(Int(0))
    assert isinstance(first, Float)


def test_timeit_default_timer_returns_float() -> None:
    assert isinstance(TimeIt.default_timer(), Float)


def test_timer_constructs() -> None:
    t = Timer(Str("pass"))
    assert isinstance(t, Timer)


def test_timer_timeit_returns_float() -> None:
    t = Timer(Str("pass"))
    assert isinstance(t.timeit(Int(10)), Float)


def test_timer_repeat_returns_list_of_float() -> None:
    t = Timer(Str("pass"))
    result = t.repeat(Int(2), Int(10))
    assert isinstance(result, List)
    assert result.len() == Int(2)


def test_timer_autorange_returns_tuple() -> None:
    t = Timer(Str("pass"))
    result = t.autorange()
    assert result.len() == Int(2)


def test_timeit_class_attr() -> None:
    assert TimeIt.Timer is Timer


# --- Interpreter integration ---


def test_timeit_via_interpreter() -> None:
    Interpreter().run_source('timeit.timeit("pass", "pass", 10).print()')
