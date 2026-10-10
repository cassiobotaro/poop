import ast
import atexit
import code
import codeop
import importlib
import inspect
import sys
import textwrap
from contextlib import contextmanager, suppress
from functools import cache
from pathlib import Path
from typing import TYPE_CHECKING

from rich.columns import Columns
from rich.text import Text

from poop.console import ERR, OUT, in_colour
from poop.errors import ParseError, PoopError, report
from poop.executor import confine
from poop.types._message import withheld_builtin
from poop.types._selectors import is_message, receiver_label
from poop.types.boolean import Boolean
from poop.types.complex import Complex
from poop.types.float import Float
from poop.types.int import Int
from poop.types.none import NoneClass
from poop.types.string import Str

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Iterator
    from types import ModuleType

    from rich.console import Console

    from poop.interpreter import Interpreter
    from poop.validators import Validator


# Imported once, here: a build without it (Windows ships none) gets a REPL
# with no completion or history rather than one that fails. Each of the three
# functions using it used to repeat the guarded import.
def _optional_readline() -> ModuleType | None:
    try:
        return importlib.import_module("readline")
    except ImportError:  # pragma: no cover - present wherever the suite runs
        return None


_readline = _optional_readline()

_HISTORY_FILE = Path.home() / ".poop_history"
_HISTORY_MAX = 1000

# readline needs \001/\002 non-printing markers to measure prompt width, which
# rich does not emit — so the prompt keeps manual ANSI, gated on rich's own
# stdout detection so it still respects a non-tty stdout and NO_COLOR.
_RESET = "\x1b[0m"
_DIM = "\x1b[2m"
_CYAN = "\x1b[36m"


def _value_text(value: object) -> Text:
    if isinstance(value, Boolean):
        return Text(repr(value), style="blue")
    if isinstance(value, (Int, Float, Complex)):
        return Text(repr(value), style="yellow")
    if isinstance(value, Str):
        return Text(repr(value._value), style="green")
    return Text(repr(value))


def _rl_color(console: Console, text: str, *codes: str) -> str:
    """Color a readline prompt (stdout-bound), keeping readline width markers."""
    if not in_colour(console):
        return text
    return f"\001{''.join(codes)}\002{text}\001{_RESET}\002"


_SAFE_AST_NODES: tuple[type[ast.AST], ...] = (
    ast.Expression,
    ast.Name,
    ast.Attribute,
    ast.Constant,
    ast.List,
    ast.Tuple,
    ast.Set,
    ast.Dict,
    ast.Load,
)


def _is_safe_expr(expr: str) -> bool:
    try:
        tree = ast.parse(expr, mode="eval")
    except SyntaxError:
        return False
    return all(isinstance(node, _SAFE_AST_NODES) for node in ast.walk(tree))


def _completion(name: str, value: object) -> str:
    """`name` as Tab completes it: with a `(` when it is called."""
    return f"{name}(" if callable(value) else name


class _PoopCompleter:
    def __init__(self, namespace: dict[str, object]) -> None:
        self._ns = namespace
        self._matches: list[str] = []

    def complete(self, text: str, state: int) -> str | None:
        if state == 0:
            self._matches = (
                self._attr_matches(text) if "." in text else self._name_matches(text)
            )
        try:
            return self._matches[state]
        except IndexError:
            return None

    def _name_matches(self, text: str) -> list[str]:
        # `is_message`, not a `_poop_`-only filter: any other `_`-prefixed key
        # is machinery too, and offering it teaches a name `get_attr` refuses.
        return sorted(
            _completion(name, value)
            for name, value in self._ns.items()
            if name.startswith(text) and is_message(name)
        )

    def _attr_matches(self, text: str) -> list[str]:
        expr, _, attr = text.rpartition(".")
        if not _is_safe_expr(expr):
            return []
        try:
            obj = eval(expr, self._ns)  # noqa: S307
            names = dir(obj)
        except Exception:  # noqa: BLE001
            return []
        # `getattr_static`: reading the attribute off the *type* was already
        # required, because `getattr(obj, name)` runs a `property` getter and
        # pressing Tab then executed program code. Going through `getattr` at
        # all stopped working when the class side started refusing instance
        # messages — `getattr(Int, "abs", None)` answers the default, so every
        # message lost its `(`. This resolves no descriptor at all, which is
        # what "off the type" meant in the first place.
        return sorted(
            f"{expr}.{_completion(name, inspect.getattr_static(obj, name, None))}"
            for name in names
            if name.startswith(attr) and is_message(name)
        )


def _setup_readline(namespace: dict[str, object]) -> None:
    if _readline is None:
        return

    _readline.parse_and_bind("tab: complete")
    _readline.set_completer(_PoopCompleter(namespace).complete)
    _readline.set_completer_delims(" \t\n`!@#$^&*()-=+[{]}\\|;:'\",<>/?")

    with suppress(FileNotFoundError):
        _readline.read_history_file(_HISTORY_FILE)

    _readline.set_history_length(_HISTORY_MAX)
    _register_history_saver()


@cache
def _register_history_saver() -> None:
    # Once per process: atexit registrations are never removed, so each Repl
    # registering its own would leak another callback into the global registry.
    atexit.register(_save_history)


def _save_history() -> None:
    if _readline is None:
        return
    # Runs at exit, where an unwritable history file must not become a crash.
    with suppress(Exception):
        _readline.write_history_file(_HISTORY_FILE)


def _indent_for(buffer: list[str]) -> str:
    if not buffer:
        return ""
    last = buffer[-1].rstrip()
    current = len(last) - len(last.lstrip())
    return " " * (current + 4) if last.endswith(":") else " " * current


def _readline_input(prompt: str, indent: str) -> str:
    readline = _readline
    if readline is None or not indent:
        return input(prompt)

    def _pre_hook() -> None:
        readline.insert_text(indent)
        readline.redisplay()

    readline.set_pre_input_hook(_pre_hook)
    try:
        return input(prompt)
    finally:
        readline.set_pre_input_hook(None)


@contextmanager
def _displaying_through(
    hook: Callable[[object], None], ps1: str, ps2: str
) -> Iterator[None]:
    """Route expression results through `hook`, under POOP's prompts, for the duration.

    `sys.ps1` / `sys.ps2` are where `code.InteractiveConsole.interact` reads
    its prompts from, and `sys.displayhook` is how an expression statement
    echoes — all three process-wide, so all three are put back.
    """
    original = sys.displayhook, getattr(sys, "ps1", None), getattr(sys, "ps2", None)
    sys.displayhook, sys.ps1, sys.ps2 = hook, ps1, ps2
    try:
        yield
    finally:
        sys.displayhook, sys.ps1, sys.ps2 = original


def _explain_calls(validators: Iterable[Validator]) -> frozenset[str]:
    """The builtins `:explain` covers by running `<name>(x)` through validators.

    The explanation is the validator's own message, so the two can never
    drift apart. The topic list is derived from the same validators for the
    same reason: hand-maintained, it fell two names behind (`delattr`,
    `__import__`), and a missing topic does not fail quietly — it answers "it
    may simply be allowed" about a banned name. Read off the interpreter the
    REPL was handed, so an injected set explains its own bans.
    """
    return frozenset(
        name for validator in validators for name in getattr(validator, "forbidden", ())
    )


# Forbidden statements and operators need a minimal valid snippet.
_EXPLAIN_SNIPPETS: dict[str, str] = {
    "if": "if x:\n    pass",
    "ternary": "x if y else z",
    "for": "for i in x:\n    pass",
    "while": "while x:\n    pass",
    "comprehension": "[i for i in x]",
    "def": "def f():\n    pass",
    "assert": "assert x",
    "raise": "raise ValueError(x)",
    "try": "try:\n    pass\nexcept Exception:\n    pass",
    "with": "with x:\n    pass",
    "not": "not x",
    "and": "x and y",
    "or": "x or y",
    "in": "x in y",
    "is": "x is y",
    "del": "del x",
    "global": "class C:\n    def m(self):\n        global x",
    "yield": "class C:\n    def m(self):\n        yield x",
    "async": "class C:\n    async def m(self):\n        pass",
    # Bare `await x` parses (only compile() rejects it), so this reaches
    # no_async's Await row instead of being shadowed by the async def one.
    "await": "await x",
    "walrus": "(x := 1)",
    # A decorator no_decorator refuses — `@staticmethod` and its two siblings
    # are allowed, so a snippet using one would explain nothing.
    "decorator": "class C:\n    @twice\n    def m():\n        pass",
    "match": "match x:\n    case _:\n        pass",
    "fstring": 'f"{x}"',
    # All four messages `no_subscript` composes. The snippet was `x[0]` alone,
    # a *load*, so a reader who wrote `xs[0] = 9`, was told to use
    # `obj.at_put(key, value)` and typed `:explain subscript` to learn more was
    # shown the reading substitute — the one a writer must never be handed. `validate_all` collects every error and
    # `_meta_explain` prints them all, so listing the spellings is the change.
    "subscript": "x[0]\nx[0] = 1\nx[1:2]\nx[1:2] = y",
    "import": "import os",
    "invert": "~x",
    # `-x` on a Name, not on a literal: no_unary_minus allows `-1`.
    "unary_minus": "-x",
    "unary_plus": "+x",
    "type_alias": "type X = int",
    "dunder": "x.__dict__",
    "private": "x._value",
    # A bare mention, not `@property`: the decorator is the one position
    # no_class_machinery leaves open, so a snippet using it explains nothing.
    "property": "p = property",
}

_META_HELP = """\
:methods <expr>     list the messages an object understands (expr is a
                    variable or literal — calls are not evaluated)
:explain <name>     why a construct is forbidden and what to use instead
                    (e.g. :explain if, :explain len, :explain fstring)
:help               show this help"""


def _explain_snippet(construct: str, calls: frozenset[str]) -> str | None:
    if construct in calls:
        return f"{construct}(x)"
    return _EXPLAIN_SNIPPETS.get(construct)


class Repl(code.InteractiveConsole):
    """The POOP REPL: `code.InteractiveConsole` with the pipeline in `runsource`.

    The console ships the loop — accumulate lines, compile, ask for more on
    an incomplete statement, reset on a syntax error, switch the prompt,
    swallow Ctrl-C, end on Ctrl-D — and has an override point for each thing
    that is POOP's: `raw_input` for the prompt, the auto-indent, the meta
    commands and the byte-order mark; `runsource` for the pipeline, the
    per-input filename and the error report; `write` for the console's own
    few words, on stderr through `err`. The two consoles are constructor
    parameters, so a test hands its own in rather than patching the module.
    """

    def __init__(
        self, interpreter: Interpreter, *, out: Console = OUT, err: Console = ERR
    ) -> None:
        super().__init__()
        self._interpreter = interpreter
        self._out = out
        self._err = err
        self._ns: dict[str, object] = interpreter.new_namespace()
        # Before anything evaluates against it: `:methods` and the completer
        # `eval` on their own, and an unconfined namespace would be handed
        # CPython's builtins for the rest of the session.
        confine(self._ns)
        self._explain_calls = _explain_calls(interpreter.validators)
        self._input_no = 0
        # The stdin path's half of `utf-8-sig`. `poop <file>` decodes with the
        # codec that strips a byte-order mark; a piped program is read line by
        # line through `input()`, which does not, so `printf '\xef\xbb\xbf…' |
        # poop` answered the same `invalid non-printable character U+FEFF` the
        # file path used to. A mark is only a mark at the head of the stream,
        # so this is spent once.
        self._leading_mark = True
        _setup_readline(self._ns)

    # --- the three sinks ---

    def _say(self, text: str = "") -> None:
        """Write REPL output on stdout, as typed: no markup, no highlighting.

        The REPL wrote through the console for values and headers and through
        bare `print` for usage lines, `:help` and `:explain` — two paths to
        one stream, and only one of them the console that decides colour per
        destination.
        """
        self._out.print(text, soft_wrap=True, highlight=False, markup=False)

    def _error(self, message: str) -> None:
        """Report a REPL diagnostic: `poop:`-prefixed, red, on stderr.

        Every diagnostic the REPL emits shares that contract, so it lives in
        one place — a new call site cannot forget the prefix or the stream.
        """
        self._err.print(
            Text(f"poop: {message}", style="red"), soft_wrap=True, highlight=False
        )

    def _print_value(self, value: object) -> None:
        self._out.print(_value_text(value), soft_wrap=True, highlight=False)

    def write(self, data: str) -> None:
        """The console's own words — the newline after Ctrl-D, `KeyboardInterrupt`.

        On stderr, as `code.InteractiveConsole` writes them, through the
        console that decides colour for that stream.
        """
        self._err.print(data, end="", soft_wrap=True, highlight=False, markup=False)

    # --- meta-commands ---

    def _meta(self, line: str) -> None:
        cmd, _, arg = line[1:].strip().partition(" ")
        # Name-based dispatch, as `cmd.Cmd` does with `do_*`: `:foo` runs
        # `_meta_foo`. `isidentifier` keeps `:_meta` or `:__class__` from
        # reaching any other attribute.
        command = getattr(self, f"_meta_{cmd}", None) if cmd.isidentifier() else None
        if command is None:
            self._error(f"unknown meta-command :{cmd} — try :help")
            return
        command(arg.strip())

    def _meta_help(self, _arg: str) -> None:
        self._say(_META_HELP)

    def _meta_methods(self, arg: str) -> None:
        if not arg:
            self._say("usage: :methods <expr>")
            return
        if not _is_safe_expr(arg):
            self._error(
                ":methods takes a variable or literal — calls are not evaluated"
            )
            return
        try:
            # Run the expression through the pipeline so literals become
            # POOP values ("abc" must answer Str's messages, not str's).
            tree = self._interpreter.transform_source(arg, "<methods>")
            stmt = tree.body[0]
            if not isinstance(stmt, ast.Expr):  # pragma: no cover - defensive
                # `_is_safe_expr` already guaranteed an eval-mode expression, so
                # the transformed body is always an `Expr`; this guards a future
                # transformer that could inject a statement ahead of it.
                raise SyntaxError("not an expression")
            compiled = compile(ast.Expression(stmt.value), "<methods>", "eval")
            obj = eval(compiled, self._ns)  # noqa: S307
        except Exception as exc:  # noqa: BLE001
            self._error(str(exc))
            return
        names = sorted(n for n in dir(obj) if is_message(n))
        header = f"{receiver_label(obj)} understands {len(names)} messages:"
        self._out.print(Text(header, style="dim"), soft_wrap=True, highlight=False)
        # rich lays the messages out in as many columns as the terminal is wide
        # (a single column when the width is unknown, e.g. a pipe), replacing a
        # hand-rolled textwrap.fill that always assumed 80.
        self._out.print(Columns(names, padding=(0, 2), column_first=True))

    def _meta_explain(self, arg: str) -> None:
        if not arg:
            self._say("usage: :explain <construct>")
            return
        snippet = _explain_snippet(arg, self._explain_calls)
        if snippet is None:
            # A builtin the allow-list withholds has no topic, since no
            # validator refuses it — the executor's own sentence is the answer.
            withheld = withheld_builtin(arg)
            if withheld is not None:
                self._say(withheld)
                return
            known = sorted(self._explain_calls | set(_EXPLAIN_SNIPPETS))
            # Not "it may simply be allowed": nothing here checked that, and
            # for a banned construct with no topic the guess is a flat lie.
            self._say(f"poop: no :explain topic for {arg!r}.\nKnown constructs:")
            self._say(textwrap.fill("  ".join(known), width=80))
            return
        errors = self._interpreter.validate_all(snippet, "<explain>")
        if not errors:
            self._out.print(Text(f"{arg} is allowed in POOP.", style="green"))
            return
        for err in errors:
            self._say(err.message)

    # --- the console's override points ---

    def _displayhook(self, value: object) -> None:
        # POOP's `none` (NoneClass) is the answer of every void message,
        # including `.print()` — the most common REPL expression. Mirror
        # CPython's REPL, which displays nothing for a None-valued
        # expression and leaves `_` untouched.
        if value is None or isinstance(value, NoneClass):
            return
        self._ns["_"] = value
        self._print_value(value)

    def raw_input(self, prompt: str = "") -> str:
        """One line, under POOP's prompt — or a meta-command, run on the spot.

        The auto-indent follows the buffer the console keeps; a `:` line at
        the top level is dispatched here and the console is handed an empty
        line to push, which `runsource` lets through without running.
        """
        line = _readline_input(prompt, _indent_for(self.buffer))
        if self._leading_mark:
            self._leading_mark = False
            line = line.removeprefix("\ufeff")
        if not self.buffer and line.lstrip().startswith(":"):
            self._meta(line.lstrip())
            return ""
        return line

    def runsource(
        self, source: str, filename: str = "<input>", symbol: str = "single"
    ) -> bool:
        """The pipeline on a complete input; `True` while the input is incomplete.

        `codeop` decides completeness, as the console's own does; the
        difference is what runs afterwards and how its failures are reported
        — through `report`, which carries the source gutter and caret.
        """
        try:
            compiled = codeop.compile_command(source, filename, symbol)
        except SyntaxError as exc:
            report(ParseError.from_syntax_error(exc), source, self._err)
            return False
        if compiled is None:
            return True
        if not source.strip():
            return False
        self._input_no += 1
        try:
            self._interpreter.run_source_repl(
                source, self._ns, filename=f"<repl-{self._input_no}>"
            )
        except PoopError as exc:
            # Through `report`, like the syntax error above, rather than
            # `_error`: it carries the source gutter and caret the plain sink
            # cannot, highlighted on a tty.
            report(exc, source, self._err)
        return False

    def run(self) -> None:
        self._out.print(
            Text.assemble(
                ("POOP 💩", "bold magenta"),
                "  — Python infected by Smalltalk. ",
                ("Ctrl+D to exit.", "dim"),
            )
        )
        ps1 = _rl_color(self._out, ">>>", _CYAN) + " "
        ps2 = _rl_color(self._out, "...", _DIM) + " "
        with _displaying_through(self._displayhook, ps1, ps2):
            # Both messages empty: the banner is printed above, styled, and
            # the console's exit line names a class no POOP user has met.
            self.interact(banner="", exitmsg="")
