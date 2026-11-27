import ast
import builtins
import sys
import traceback
from contextlib import contextmanager
from typing import TYPE_CHECKING, Literal

from poop.errors import ExecutionError
from poop.types._message import too_deep
from poop.types.exceptions import describe, describe_chain

if TYPE_CHECKING:
    from collections.abc import Generator
    from types import CodeType

# The only Python builtins user code may reach. `exec` hands a program
# CPython's entire builtins namespace unless the globals dict already carries
# one, and POOP covers only the names it bans or rewrites — so without this
# `OSError`, `copyright` and `NotImplemented` would be naked natives one
# identifier away, answering `type object 'OSError' has no attribute 'print'`
# instead of POOP's `does not understand #print`, against
# `poop/types/exceptions.py`, which mirrors only the exceptions a program can
# reach. An allow-list closes the whole class of escapes at once, where a
# validator can only close the names someone thought to enumerate
# (`doc/adr/0040-programs-are-confined-to-a-builtins-allow-list.md`).
#
# Everything here is language machinery with no message-passing substitute —
# the argument ADR 18 makes for `super`
# (`doc/adr/0018-class-machinery-is-accepted-only-where-it-was-argued-for.md`).
# `__build_class__` is what the `class` statement calls; `__name__` is read
# while creating one. `__import__` is how CPython itself imports from a
# program's frame: the warning for a coroutine collected unawaited goes
# through it, and without it CPython prints `KeyError: '__import__'` in the
# warning's place. No program can reach it: `import` is refused by
# `no_import`, the bare name by `no_dunder_name`, a dunder read by ADR 33.
_ALLOWED_BUILTINS: dict[str, object] = {
    "__build_class__": builtins.__build_class__,
    "__import__": builtins.__import__,
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
# ADR 34 says why that matters (`doc/adr/0034-only-the-exceptions-poop-can-reach-are-mirrored.md`):
# `RecursionError` is mirrored because recursion is POOP's substitute for
# every loop, which makes it the most reachable failure. Under CPython's
# default limit of 1000, a self-sending message runs 164 levels deep where the
# same recursion written as a Python function runs 998
# (`doc/adr/0061-the-recursion-limit-is-sized-by-frames-per-send.md`).
#
# Six thousand buys a POOP program roughly the thousand levels a Python program
# already gets, which is the honest target: a language should not be an order of
# magnitude shallower than the one it is built on, least of all the language
# that banned `for`. `while_true` and `while_false` are real Python `while`
# loops and have no ceiling at all, so this is about *structural* recursion —
# `examples/patterns/interpreter.py` walks a tree, and the depth follows the
# data.
#
# Safe to raise on 3.15, which is worth checking rather than assuming: CPython
# guards the C stack separately and answers a catchable `RecursionError`
# ("Stack overflow (used 8148 kB) while calling a Python object") rather than
# crashing. So the ceiling moves and the floor underneath it holds.
_FRAMES_PER_SEND = 6
_RECURSION_LIMIT = 1000 * _FRAMES_PER_SEND


@contextmanager
def _recursion_budget() -> Generator[None]:
    """The raised limit for the duration of one program, then the old one back.

    Raised, not set: a caller that has already asked for more keeps it. The
    REPL runs through `execute` per input, so each input runs under the
    budget and the prompt returns to the process's own. A library function
    that changed the interpreter's limit for good would be a side effect a
    test suite inherits without knowing: every test after the first POOP
    program, and pytest itself, would run at the raised limit.
    """
    previous = sys.getrecursionlimit()
    if previous >= _RECURSION_LIMIT:
        yield
        return
    sys.setrecursionlimit(_RECURSION_LIMIT)
    try:
        yield
    finally:
        sys.setrecursionlimit(previous)


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
    try:
        with _recursion_budget():
            exec(code, ns)  # noqa: S102
    except RecursionError as exc:
        # Reworded here rather than in `describe`, which every failure passes
        # through: this one is about the *interpreter's* budget, not about
        # anything the program's own objects said.
        raise ExecutionError(
            f"RecursionError: {too_deep()}",
            _user_lineno(exc, filename),
            tuple(describe_chain(exc)),
        ) from exc
    except Exception as exc:
        raise ExecutionError(
            describe(exc), _user_lineno(exc, filename), tuple(describe_chain(exc))
        ) from exc
