import ast
import traceback

from poop.errors import ExecutionError


def _user_lineno(exc: BaseException, filename: str) -> int | None:
    """Line of the deepest user-source frame, for the error message.

    Walk the traceback and keep the last frame whose filename matches the
    compiled program. Internal POOP frames (executor.py, the type methods)
    are skipped, so a failure inside `Int.__truediv__` still reports the
    user line that triggered it. Returns None when no user frame is present.
    """
    lineno: int | None = None
    for frame in traceback.extract_tb(exc.__traceback__):
        if frame.filename == filename:
            lineno = frame.lineno
    return lineno


def execute(
    tree: ast.Module,
    filename: str = "<unknown>",
    namespace: dict[str, object] | None = None,
    *,
    interactive: bool = False,
) -> None:
    try:
        if interactive:
            interactive_tree = ast.Interactive(body=tree.body)
            ast.copy_location(interactive_tree, tree)
            code = compile(interactive_tree, filename=filename, mode="single")
        else:
            code = compile(tree, filename=filename, mode="exec")
    except SyntaxError as exc:
        # ast.parse accepts some constructs that compile rejects (e.g. a
        # module-level `return`); surface them as a PoopError instead of
        # leaking a raw SyntaxError past the CLI's error handler.
        raise ExecutionError(exc.msg, exc.lineno) from exc
    ns: dict[str, object] = namespace if namespace is not None else {}
    try:
        exec(code, ns)  # noqa: S102
    except Exception as exc:
        raise ExecutionError(str(exc), _user_lineno(exc, filename)) from exc
