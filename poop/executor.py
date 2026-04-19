import ast

from poop.errors import ExecutionError


def execute(
    tree: ast.Module,
    filename: str = "<unknown>",
    namespace: dict[str, object] | None = None,
) -> None:
    code = compile(tree, filename=filename, mode="exec")
    ns: dict[str, object] = dict(namespace) if namespace else {}
    try:
        exec(code, ns)  # noqa: S102
    except Exception as exc:
        raise ExecutionError(str(exc)) from exc
