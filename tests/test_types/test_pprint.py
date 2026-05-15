import sys
from io import StringIO

from poop.interpreter import Interpreter
from poop.types.boolean import Boolean, false, true
from poop.types.dict import Dict
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import none
from poop.types.pprint import Pprint, PrettyPrinter
from poop.types.string import Str


def test_pformat_returns_poop_str() -> None:
    result = Pprint.pformat([1, 2, 3])
    assert isinstance(result, Str)


def test_pformat_outputs_repr_of_list() -> None:
    result = Pprint.pformat([1, 2, 3])
    assert "[1, 2, 3]" in result._value


def test_pformat_respects_width() -> None:
    long = list(range(20))
    narrow = Pprint.pformat(long, width=Int(10))
    wide = Pprint.pformat(long, width=Int(200))
    assert "\n" in narrow._value
    assert "\n" not in wide._value


def test_pprint_returns_none_and_writes_to_stdout() -> None:
    captured = StringIO()
    real_stdout = sys.stdout
    sys.stdout = captured
    try:
        result = Pprint.pprint([1, 2, 3])
    finally:
        sys.stdout = real_stdout
    assert result is none
    assert "[1, 2, 3]" in captured.getvalue()


def test_pp_returns_none() -> None:
    captured = StringIO()
    real_stdout = sys.stdout
    sys.stdout = captured
    try:
        result = Pprint.pp({"b": 1, "a": 2})
    finally:
        sys.stdout = real_stdout
    assert result is none
    output = captured.getvalue()
    # pp defaults sort_dicts=False; original order preserved.
    assert output.index("b") < output.index("a")


def test_isreadable_true_for_simple_dict() -> None:
    result = Pprint.isreadable({"a": 1})
    assert isinstance(result, Boolean)
    assert result is true


def test_isrecursive_false_for_flat() -> None:
    assert Pprint.isrecursive([1, 2, 3]) is false


def test_isrecursive_true_for_self_reference() -> None:
    lst: list[object] = [1]
    lst.append(lst)
    assert Pprint.isrecursive(lst) is true


def test_saferepr_returns_poop_str() -> None:
    assert isinstance(Pprint.saferepr({"a": 1}), Str)


def test_pretty_printer_class_pformat() -> None:
    pp = PrettyPrinter(indent=Int(2), width=Int(80))
    result = pp.pformat({"a": 1, "b": 2})
    assert isinstance(result, Str)


def test_pretty_printer_class_isreadable() -> None:
    pp = PrettyPrinter()
    assert pp.isreadable({"a": 1}) is true


def test_pretty_printer_class_isrecursive() -> None:
    pp = PrettyPrinter()
    assert pp.isrecursive([1, 2]) is false


def test_pretty_printer_class_pprint_writes_to_stdout() -> None:
    captured = StringIO()
    real_stdout = sys.stdout
    sys.stdout = captured
    try:
        # PrettyPrinter captures sys.stdout at construction; build it
        # inside the redirect to direct output to the StringIO.
        PrettyPrinter().pprint([1, 2, 3])
    finally:
        sys.stdout = real_stdout
    assert "[1, 2, 3]" in captured.getvalue()


def test_pprint_handles_poop_types() -> None:
    # POOP types alias __repr__ to __str__; pformat should produce the same.
    data = List(Int(1), Int(2), Str("hello"))
    result = Pprint.pformat(data)
    assert isinstance(result, Str)


def test_pprint_reachable_via_interpreter() -> None:
    Interpreter().run_source("pprint.pformat([1, 2, 3]).print()")


def test_PrettyPrinter_class_reachable_via_interpreter() -> None:
    Interpreter().run_source("PrettyPrinter().pformat([1, 2]).print()")


def test_dict_pformat_via_namespace() -> None:
    d = Dict().at_put(Str("k"), Int(1))
    result = Pprint.pformat(d)
    assert isinstance(result, Str)
