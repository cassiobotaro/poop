import ast

from poop.errors import ExecutionError


def execute(
    tree: ast.Module,
    filename: str = "<unknown>",
    namespace: dict[str, object] | None = None,
    *,
    interactive: bool = False,
) -> None:
    if interactive:
        interactive_tree = ast.Interactive(body=tree.body)
        ast.copy_location(interactive_tree, tree)
        code = compile(interactive_tree, filename=filename, mode="single")
    else:
        code = compile(tree, filename=filename, mode="exec")
    ns: dict[str, object] = namespace if namespace is not None else {}
    try:
        exec(code, ns)  # noqa: S102
    except Exception as exc:
        raise ExecutionError(str(exc)) from exc
