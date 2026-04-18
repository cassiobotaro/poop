import ast

from poop.errors import ExecutionError


def execute(tree: ast.Module, filename: str = "<unknown>") -> None:
    code = compile(tree, filename=filename, mode="exec")
    namespace: dict[str, object] = {}
    try:
        exec(code, namespace)  # noqa: S102
    except Exception as exc:
        raise ExecutionError(str(exc)) from exc
