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


def test_execute_uses_isolated_namespace() -> None:
    tree1 = ast.parse("x = 42")
    tree2 = ast.parse("assert 'x' not in dir()")
    execute(tree1)
    execute(tree2)


def test_execute_namespace_is_available_in_code() -> None:
    tree = ast.parse("assert _sentinel == 99")
    execute(tree, namespace={"_sentinel": 99})
