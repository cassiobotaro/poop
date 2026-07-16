import ast
import atexit
import codeop
import sys
import textwrap
from pathlib import Path
from typing import TYPE_CHECKING

from rich.columns import Columns
from rich.console import Console
from rich.text import Text

from poop.errors import PoopError, format_error, render_error
from poop.transformers import DEFAULT_NAMESPACE
from poop.types.boolean import Boolean
from poop.types.complex import Complex
from poop.types.float import Float
from poop.types.int import Int
from poop.types.none import NoneClass
from poop.types.string import Str
from poop.validators import DEFAULT_VALIDATORS

if TYPE_CHECKING:
    from poop.interpreter import Interpreter

_HISTORY_FILE = Path.home() / ".poop_history"
_HISTORY_MAX = 1000

# atexit registrations are never removed, so guard against re-registering the
# history saver every time a Repl is constructed — otherwise each instance
# leaks another callback into the global atexit registry.
_history_saver_registered = False

# One console per stream, so colorization is decided per destination: value
# echoes and prompts write to stdout, diagnostics to stderr. rich detects each
# stream's tty independently and honors NO_COLOR, so `poop 2>err.log` never
# leaks ANSI into the file while the interactive stdout stays colored.
_OUT = Console()
_ERR = Console(stderr=True)

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


def _print_value(value: object) -> None:
    _OUT.print(_value_text(value), soft_wrap=True, highlight=False)


def _rl_color(text: str, *codes: str) -> str:
    """Color a readline prompt (stdout-bound), keeping readline width markers."""
    if not _OUT.is_terminal or _OUT.no_color:
        return text
    return f"\001{''.join(codes)}\002{text}\001{_RESET}\002"


def _error(message: str) -> None:
    """Report a REPL diagnostic: `poop:`-prefixed, red, on stderr.

    Every diagnostic the REPL emits shares that contract, so it lives in
    one place — a new call site cannot forget the prefix or the stream.
    """
    _ERR.print(Text(f"poop: {message}", style="red"), soft_wrap=True, highlight=False)


def _print_error(exc: PoopError, source: str | None) -> None:
    """Print a formatted error on stderr: message, source gutter, caret.

    On a colour terminal the offending line is Python-highlighted via
    `render_error`; off a terminal (a pipe, `NO_COLOR`) the plain `format_error`
    text is printed instead, so redirected error output stays clean.
    """
    if _ERR.is_terminal and not _ERR.no_color:
        _ERR.print(render_error(exc, source), soft_wrap=True)
    else:
        _ERR.print(
            format_error(exc, source), soft_wrap=True, highlight=False, markup=False
        )


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
        results = []
        for name, val in self._ns.items():
            if name.startswith(text) and not name.startswith("_poop_"):
                suffix = "(" if callable(val) else ""
                results.append(name + suffix)
        return sorted(results)

    def _attr_matches(self, text: str) -> list[str]:
        dot = text.rfind(".")
        expr, attr = text[:dot], text[dot + 1 :]
        if not _is_safe_expr(expr):
            return []
        try:
            obj = eval(expr, self._ns)  # noqa: S307
            results = []
            for name in dir(obj):
                if name.startswith(attr) and not name.startswith("__"):
                    val = getattr(obj, name, None)
                    suffix = "(" if callable(val) else ""
                    results.append(f"{expr}.{name}{suffix}")
            return sorted(results)
        except Exception:  # noqa: BLE001
            return []


def _setup_readline(namespace: dict[str, object]) -> None:
    try:
        import readline
    except ImportError:
        return

    readline.parse_and_bind("tab: complete")
    readline.set_completer(_PoopCompleter(namespace).complete)
    readline.set_completer_delims(" \t\n`!@#$^&*()-=+[{]}\\|;:'\",<>/?")

    try:
        readline.read_history_file(_HISTORY_FILE)
    except FileNotFoundError:
        pass

    readline.set_history_length(_HISTORY_MAX)

    global _history_saver_registered
    if not _history_saver_registered:
        atexit.register(_save_history)
        _history_saver_registered = True


def _save_history() -> None:
    try:
        import readline

        readline.write_history_file(_HISTORY_FILE)
    except Exception:  # noqa: BLE001, S110
        pass


def _indent_for(buffer: list[str]) -> str:
    if not buffer:
        return ""
    last = buffer[-1].rstrip()
    current = len(last) - len(last.lstrip())
    return " " * (current + 4) if last.endswith(":") else " " * current


def _readline_input(prompt: str, indent: str) -> str:
    try:
        import readline
    except ImportError:
        return input(prompt)

    if not indent:
        return input(prompt)

    def _pre_hook() -> None:
        readline.insert_text(indent)
        readline.redisplay()

    readline.set_pre_input_hook(_pre_hook)
    try:
        return input(prompt)
    finally:
        readline.set_pre_input_hook(None)


# Forbidden builtins explained by running `<name>(x)` through the
# validators — the explanation is the validator's own message, so the
# two can never drift apart. The topic list is derived from the same
# validators for the same reason: hand-maintained, it fell two names
# behind (`delattr`, `__import__`), and a missing topic does not fail
# quietly — it answers "it may simply be allowed" about a banned name.
_EXPLAIN_CALLS = frozenset(
    name
    for validator in DEFAULT_VALIDATORS
    for name in getattr(validator, "forbidden", ())
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
    "match": "match x:\n    case _:\n        pass",
    "fstring": 'f"{x}"',
    "subscript": "x[0]",
    "import": "import os",
    "invert": "~x",
    # `-x` on a Name, not on a literal: no_unary_minus allows `-1`.
    "unary_minus": "-x",
    "unary_plus": "+x",
    "type_alias": "type X = int",
    "dunder": "x.__dict__",
}

_META_HELP = """\
:methods <expr>     list the messages an object understands (expr is a
                    variable or literal — calls are not evaluated)
:explain <name>     why a construct is forbidden and what to use instead
                    (e.g. :explain if, :explain len, :explain fstring)
:help               show this help"""


def _explain_snippet(construct: str) -> str | None:
    if construct in _EXPLAIN_CALLS:
        return f"{construct}(x)"
    return _EXPLAIN_SNIPPETS.get(construct)


class Repl:
    def __init__(self, interpreter: Interpreter) -> None:
        self._interpreter = interpreter
        self._ns: dict[str, object] = dict(DEFAULT_NAMESPACE)
        self._input_no = 0
        _setup_readline(self._ns)

    def _meta(self, line: str) -> None:
        parts = line[1:].split(maxsplit=1)
        cmd = parts[0] if parts else ""
        arg = parts[1].strip() if len(parts) > 1 else ""
        if cmd == "methods":
            self._meta_methods(arg)
        elif cmd == "explain":
            self._meta_explain(arg)
        elif cmd == "help":
            print(_META_HELP)  # noqa: T201
        else:
            _error(f"unknown meta-command :{cmd} — try :help")

    def _meta_methods(self, arg: str) -> None:
        if not arg:
            print("usage: :methods <expr>")  # noqa: T201
            return
        if not _is_safe_expr(arg):
            _error(":methods takes a variable or literal — calls are not evaluated")
            return
        try:
            # Run the expression through the pipeline so literals become
            # POOP values ("abc" must answer Str's messages, not str's).
            tree = self._interpreter.transform_source(arg, "<methods>")
            stmt = tree.body[0]
            if not isinstance(stmt, ast.Expr):
                raise SyntaxError("not an expression")  # noqa: TRY301
            code = compile(ast.Expression(stmt.value), "<methods>", "eval")
            obj = eval(code, self._ns)  # noqa: S307
        except Exception as exc:  # noqa: BLE001
            _error(str(exc))
            return
        names = sorted(n for n in dir(obj) if not n.startswith("_"))
        header = f"{type(obj).__name__} understands {len(names)} messages:"
        _OUT.print(Text(header, style="dim"), soft_wrap=True, highlight=False)
        # rich lays the messages out in as many columns as the terminal is wide
        # (a single column when the width is unknown, e.g. a pipe), replacing a
        # hand-rolled textwrap.fill that always assumed 80.
        _OUT.print(Columns(names, padding=(0, 2), column_first=True))

    def _meta_explain(self, arg: str) -> None:
        if not arg:
            print("usage: :explain <construct>")  # noqa: T201
            return
        snippet = _explain_snippet(arg)
        if snippet is None:
            known = sorted(_EXPLAIN_CALLS | set(_EXPLAIN_SNIPPETS))
            # Not "it may simply be allowed": nothing here checked that, and
            # for a banned construct with no topic the guess is a flat lie.
            print(  # noqa: T201
                f"poop: no :explain topic for {arg!r}.\nKnown constructs:"
            )
            print(textwrap.fill("  ".join(known), width=80))  # noqa: T201
            return
        errors = self._interpreter.validate_all(snippet, "<explain>")
        if not errors:
            _OUT.print(Text(f"{arg} is allowed in POOP.", style="green"))
            return
        for err in errors:
            print(err.args[0])  # noqa: T201

    def _displayhook(self, value: object) -> None:
        # POOP's `none` (NoneClass) is the answer of every void message,
        # including `.print()` — the most common REPL expression. Mirror
        # CPython's REPL, which displays nothing for a None-valued
        # expression and leaves `_` untouched.
        if value is None or isinstance(value, NoneClass):
            return
        self._ns["_"] = value
        _print_value(value)

    def run(self) -> None:
        _OUT.print(
            Text.assemble(
                ("POOP 💩", "bold magenta"),
                "  — Python infected by Smalltalk. ",
                ("Ctrl+D to exit.", "dim"),
            )
        )
        buffer: list[str] = []
        original_hook = sys.displayhook
        sys.displayhook = self._displayhook

        try:
            while True:
                try:
                    indent = _indent_for(buffer)
                    prompt = (
                        _rl_color("...", _DIM) + " "
                        if buffer
                        else _rl_color(">>>", _CYAN) + " "
                    )
                    line = _readline_input(prompt, indent)
                except EOFError:
                    print()  # noqa: T201
                    break
                except KeyboardInterrupt:
                    print()  # noqa: T201
                    buffer = []
                    continue

                if not buffer and line.lstrip().startswith(":"):
                    self._meta(line.lstrip())
                    continue

                buffer.append(line)
                source = "\n".join(buffer)

                try:
                    result = codeop.compile_command(source)
                except SyntaxError as exc:
                    _error(str(exc))
                    buffer = []
                    continue

                if result is None:
                    continue

                buffer = []
                if not source.strip():
                    continue

                self._input_no += 1
                try:
                    self._interpreter.run_source_repl(
                        source, self._ns, filename=f"<repl-{self._input_no}>"
                    )
                except PoopError as exc:
                    # The one diagnostic that does not go through _error():
                    # it carries the source gutter and caret the plain sink
                    # cannot, and syntax-highlights the offending line on a tty.
                    _print_error(exc, source)
        finally:
            sys.displayhook = original_hook
