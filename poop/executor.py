import ast

from poop.errors import ExecutionError


def _user_lineno(exc: BaseException, filename: str) -> int | None:
    """Line of the deepest user-source frame, for the error message.

    Walk the traceback and keep the last frame whose filename matches the
    compiled program. Internal POOP frames (executor.py, the type methods)
    are skipped, so a failure inside `Int.__truediv__` still reports the
    user line that triggered it. Returns None when no user frame is present.

    The traceback is walked directly rather than via ``traceback.extract_tb``,
    which would load each frame's source through ``linecache`` and retain it
    in that module-global cache forever — here only line numbers are needed.
    """
    lineno: int | None = None
    tb = exc.__traceback__
    while tb is not None:
        if tb.tb_frame.f_code.co_filename == filename:
            lineno = tb.tb_lineno
        tb = tb.tb_next
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
