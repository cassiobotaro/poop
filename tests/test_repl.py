import pytest

from poop.errors import ExecutionError, ParseError, ValidationError
from poop.interpreter import Interpreter
from poop.repl import Repl
from poop.transformers import DEFAULT_NAMESPACE


def _repl() -> tuple[Repl, dict[str, object]]:
    interp = Interpreter()
    repl = Repl(interp)
    return repl, repl._ns


def test_namespace_persists_across_calls() -> None:
    from poop.types.int import Int

    repl, ns = _repl()
    repl._interpreter.run_source_repl("x = 42", ns)
    repl._interpreter.run_source_repl("y = x + 1", ns)
    assert ns["y"] == Int(43)


def test_repl_initial_namespace_contains_poop_bindings() -> None:
    _, ns = _repl()
    assert "_poop_true" in ns
    assert "_poop_false" in ns
    assert "_poop_int" in ns


def test_parse_error_does_not_kill_repl_namespace() -> None:
    repl, ns = _repl()
    repl._interpreter.run_source_repl("x = 1", ns)
    with pytest.raises(ParseError):
        repl._interpreter.run_source_repl("def :", ns)
    assert "x" in ns


def test_validation_error_does_not_kill_repl_namespace() -> None:
    repl, ns = _repl()
    repl._interpreter.run_source_repl("x = 1", ns)
    with pytest.raises(ValidationError):
        repl._interpreter.run_source_repl("if True:\n    pass", ns)
    assert "x" in ns


def test_execution_error_does_not_kill_repl_namespace() -> None:
    repl, ns = _repl()
    repl._interpreter.run_source_repl("x = 1", ns)
    with pytest.raises(ExecutionError):
        repl._interpreter.run_source_repl("y = 1 / 0", ns)
    assert "x" in ns
    assert "y" not in ns


def test_repl_namespace_is_independent_of_default_namespace() -> None:
    repl, ns = _repl()
    repl._interpreter.run_source_repl("sentinel_var = 99", ns)
    assert "sentinel_var" not in DEFAULT_NAMESPACE
