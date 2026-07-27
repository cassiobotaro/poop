import ast
import builtins

from poop.errors import ExecutionError
from poop.types._message import poop_message

# The only Python builtins user code may reach. `exec` hands a program
# CPython's entire builtins namespace unless the globals dict already carries
# one, and POOP covered only the names it bans or rewrites — so `OSError`,
# `copyright`, `NotImplemented` and 55 of Python's 71 builtin exceptions were
# naked natives one identifier away, answering `type object 'OSError' has no
# attribute 'print'` instead of POOP's `does not understand #print`. That
# contradicted `poop/types/exceptions.py`, which mirrors 16 exceptions *on
# purpose*: "a language with no I/O and no codecs cannot reach the OSError
# subtree". An allow-list closes the whole class of escapes at once, where a
# validator can only close the names someone thought to enumerate.
#
# Everything here is language machinery with no message-passing substitute —
# the argument `INFECTIONS.md` already makes for `super`. `__build_class__` is
# what the `class` statement calls; `__name__` is read while creating one.
_ALLOWED_BUILTINS: dict[str, object] = {
    "__build_class__": builtins.__build_class__,
    "__name__": "__poop__",
    "super": builtins.super,
    "classmethod": builtins.classmethod,
    "staticmethod": builtins.staticmethod,
    "property": builtins.property,
}


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


def _describe(exc: BaseException) -> str:
    """Exception text for the error message, class name included.

    ``str(exc)`` alone drops the type: a missing key renders as the bare
    ``'zzz'``, with nothing to say a lookup failed, and a learner cannot tell
    which class escaped a ``Try``. Class names are safe to surface here —
    exceptions are never wrapped, so no ``_poop_*`` name can reach this path.
    An empty message degrades to the bare name rather than a dangling colon.
    """
    name = type(exc).__name__
    message = poop_message(exc)
    return f"{name}: {message}" if message else name


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
    # setdefault, not assignment: the REPL reuses one namespace across inputs,
    # and a program is free to have been handed its own (tests do).
    ns.setdefault("__builtins__", dict(_ALLOWED_BUILTINS))
    try:
        exec(code, ns)  # noqa: S102
    except Exception as exc:
        raise ExecutionError(_describe(exc), _user_lineno(exc, filename)) from exc
