import ast
import builtins
import sys
import traceback
from typing import TYPE_CHECKING, Literal

from poop.errors import ExecutionError
from poop.types._message import poop_message, too_deep
from poop.types.exceptions import poop_class_of

if TYPE_CHECKING:
    from types import CodeType

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


# One POOP message send is six Python frames, and only two of them are the
# program: the reader's method and the block it was written in. The other four
# are POOP getting out of its own way — `Block.__call__`, `_MethodBlock.__call__`
# twice (reading `self.count` and reading the branch message), and the branch
# method itself.
#
# `INFECTIONS.md` says why that matters: `RecursionError` is mirrored because
# "recursion is POOP's substitute for every loop, which makes it the most
# reachable of the lot". Nothing had ever adjusted the budget it runs against,
# so a self-sending message ran 164 levels deep where the same recursion written
# as a Python function runs 998 — both under CPython's default limit of 1000.
#
# Six thousand buys a POOP program roughly the thousand levels a Python program
# already gets, which is the honest target: a language should not be an order of
# magnitude shallower than the one it is built on, least of all the language
# that banned `for`. `while_true` and `while_false` are real Python `while`
# loops and have no ceiling at all, so this is about *structural* recursion —
# `examples/patterns/interpreter.py` walks a tree, and the depth follows the
# data.
#
# Safe to raise on 3.14, which is worth checking rather than assuming: CPython
# guards the C stack separately and answers a catchable `RecursionError`
# ("Stack overflow (used 8148 kB) while calling a Python object") rather than
# crashing. So the ceiling moves and the floor underneath it holds.
_FRAMES_PER_SEND = 6
_RECURSION_LIMIT = 1000 * _FRAMES_PER_SEND


def _user_lineno(exc: BaseException, filename: str) -> int | None:
    """Line of the deepest user-source frame, for the error message.

    Walk the traceback and keep the last frame whose filename matches the
    compiled program. Internal POOP frames (executor.py, the type methods)
    are skipped, so a failure inside `Int.__truediv__` still reports the
    user line that triggered it. Returns None when no user frame is present.

    ``traceback.walk_tb`` rather than ``traceback.extract_tb``: the second
    loads each frame's source through ``linecache`` and retains it in that
    module-global cache forever, and here only line numbers are needed.
    """
    user_lines = [
        lineno
        for frame, lineno in traceback.walk_tb(exc.__traceback__)
        if frame.f_code.co_filename == filename
    ]
    return user_lines[-1] if user_lines else None


def _describe(exc: BaseException) -> str:
    """Exception text for the error message, class name included.

    ``str(exc)`` alone drops the type: a missing key renders as the bare
    ``'zzz'``, with nothing to say a lookup failed, and a learner cannot tell
    which class escaped a ``Try``. An empty message degrades to the bare name
    rather than a dangling colon.

    The name is ``poop_class_of``'s, not ``type(exc)``'s, so the class in the
    report is always one a program can write and always the class a handler is
    given. Reading the raw type named ``MessageNotUnderstood`` — POOP's own
    class, outside ``MIRRORS`` — for every unknown selector in the language,
    while ``except_(AttributeError, …)`` caught it and ``e.class_().name()``
    answered ``AttributeError``: one failure under two names, which is the
    disagreement already closed for the ``Unicode*`` family.
    """
    name = poop_class_of(exc).__name__
    message = poop_message(exc)
    return f"{name}: {message}" if message else name


def confine(namespace: dict[str, object]) -> None:
    """Bind the builtins allow-list in `namespace`, unless one is already there.

    `exec` and `eval` plant CPython's full `builtins` in any namespace that
    reaches them without a `__builtins__`, so whoever evaluates against a
    namespace before `execute` has seen it — the REPL's `:methods` and its
    completer — must confine it first, or the whole session answers
    `AttributeError` where a program answers `NameError`.
    """
    # setdefault, not assignment: the REPL reuses one namespace across inputs,
    # and a program is free to have been handed its own (tests do).
    namespace.setdefault("__builtins__", dict(_ALLOWED_BUILTINS))


def _compile(
    tree: ast.Module, filename: str, mode: Literal["exec", "single"]
) -> CodeType:
    """`tree` compiled in `mode`, with a compile-time failure as a PoopError.

    `"single"` is the REPL's mode — an expression statement echoes its value —
    and takes an `ast.Interactive` rather than the parsed module.
    """
    source: ast.Module | ast.Interactive = tree
    if mode == "single":
        source = ast.copy_location(ast.Interactive(body=tree.body), tree)
    try:
        return compile(source, filename=filename, mode=mode)
    except SyntaxError as exc:
        # ast.parse accepts some constructs that compile rejects (e.g. a
        # module-level `return`); surface them as a PoopError instead of
        # leaking a raw SyntaxError past the CLI's error handler.
        raise ExecutionError(exc.msg, exc.lineno) from exc


def execute(
    tree: ast.Module,
    filename: str = "<unknown>",
    namespace: dict[str, object] | None = None,
    *,
    mode: Literal["exec", "single"] = "exec",
) -> None:
    code = _compile(tree, filename, mode)
    ns: dict[str, object] = namespace if namespace is not None else {}
    confine(ns)
    # Raised, not set: a caller that has already asked for more keeps it. The
    # REPL runs through here too, so both front ends get the same ceiling.
    if sys.getrecursionlimit() < _RECURSION_LIMIT:
        sys.setrecursionlimit(_RECURSION_LIMIT)
    try:
        exec(code, ns)  # noqa: S102
    except RecursionError as exc:
        # Reworded here rather than in `_describe`, which every failure passes
        # through: this one is about the *interpreter's* budget, not about
        # anything the program's own objects said.
        raise ExecutionError(
            f"RecursionError: {too_deep()}", _user_lineno(exc, filename)
        ) from exc
    except Exception as exc:
        raise ExecutionError(_describe(exc), _user_lineno(exc, filename)) from exc
