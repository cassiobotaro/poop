import ast

import pytest

from poop.errors import ExecutionError
from poop.executor import execute


def test_execute_valid_tree_runs_without_error() -> None:
    tree = ast.parse("x = 1 + 2")
    execute(tree)


def test_execute_raises_execution_error_on_runtime_exception() -> None:
    tree = ast.parse("raise ValueError('boom')")
    with pytest.raises(ExecutionError, match="boom"):
        execute(tree)


def test_execution_error_without_lineno_is_bare_message() -> None:
    assert str(ExecutionError("boom")) == "boom"


def test_execution_error_with_lineno_appends_line() -> None:
    assert str(ExecutionError("boom", 5)) == "boom (line 5)"


def test_execution_error_keeps_exception_class_name() -> None:
    # Without the class name a missing key renders as the bare `'zzz'`, with
    # nothing to say a lookup failed.
    tree = ast.parse("{'a': 1}['zzz']")
    with pytest.raises(ExecutionError) as exc_info:
        execute(tree, filename="prog.py")
    assert str(exc_info.value) == "KeyError: 'zzz' (line 1)"


def test_execution_error_without_message_is_bare_class_name() -> None:
    # `ValueError.raise_()` arrives with an empty str(exc): the name must not
    # trail a dangling colon.
    tree = ast.parse("raise ValueError()")
    with pytest.raises(ExecutionError) as exc_info:
        execute(tree, filename="prog.py")
    assert str(exc_info.value) == "ValueError (line 1)"


def test_execution_error_reports_user_line() -> None:
    tree = ast.parse("x = 1\ny = 2\nraise ValueError('boom')")
    with pytest.raises(ExecutionError) as exc_info:
        execute(tree, filename="prog.py")
    assert exc_info.value.lineno == 3
    assert "(line 3)" in str(exc_info.value)


def test_execution_error_reports_deepest_user_line() -> None:
    # The error surfaces inside a helper on line 2, called from line 3 — the
    # deepest user-source frame (line 2) is the relevant one.
    tree = ast.parse("def f():\n    return 1 / 0\nf()")
    with pytest.raises(ExecutionError) as exc_info:
        execute(tree, filename="prog.py")
    assert exc_info.value.lineno == 2


def test_execute_mutates_provided_namespace() -> None:
    ns: dict[str, object] = {}
    tree = ast.parse("x = 42")
    execute(tree, namespace=ns)
    assert ns["x"] == 42


def test_execute_separate_namespaces_are_isolated() -> None:
    tree1 = ast.parse("x = 42")
    tree2 = ast.parse("assert 'x' not in dir()")
    execute(tree1, namespace={})
    execute(tree2, namespace={})


def test_execute_namespace_is_available_in_code() -> None:
    tree = ast.parse("assert _sentinel == 99")
    execute(tree, namespace={"_sentinel": 99})
