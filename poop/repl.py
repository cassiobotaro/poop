import ast
import atexit
import codeop
import sys
import textwrap
from pathlib import Path
from typing import TYPE_CHECKING

from poop.errors import PoopError
from poop.transformers import DEFAULT_NAMESPACE
from poop.types.boolean import Boolean
from poop.types.complex import Complex
from poop.types.float import Float
from poop.types.int import Int
from poop.types.none import NoneClass
from poop.types.string import Str

if TYPE_CHECKING:
    from poop.interpreter import Interpreter

_BANNER = "POOP 💩  — Python infected by Smalltalk. Ctrl+D to exit."
_HISTORY_FILE = Path.home() / ".poop_history"
_HISTORY_MAX = 1000

_RESET = "\x1b[0m"
_DIM = "\x1b[2m"
_RED = "\x1b[31m"
_GREEN = "\x1b[32m"
_YELLOW = "\x1b[33m"
_BLUE = "\x1b[34m"
_CYAN = "\x1b[36m"


def _can_colorize() -> bool:
    try:
        return sys.stdout.isatty()
    except Exception:  # noqa: BLE001
        return False


def _color(text: str, *codes: str) -> str:
    if not _can_colorize():
        return text
    return f"{''.join(codes)}{text}{_RESET}"


def _rl_color(text: str, *codes: str) -> str:
    """Wrap non-printing ANSI bytes for readline prompts."""
    if not _can_colorize():
        return text
    return f"\001{''.join(codes)}\002{text}\001{_RESET}\002"


def _colorize_value(value: object) -> str:
    if not _can_colorize():
        return repr(value)
    if isinstance(value, Boolean):
        return _color(repr(value), _BLUE)
    if isinstance(value, NoneClass):
        return _color(repr(value), _DIM)
    if isinstance(value, (Int, Float, Complex)):
        return _color(repr(value), _YELLOW)
    if isinstance(value, Str):
        return _color(repr(value._value), _GREEN)
    return repr(value)


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
    atexit.register(_save_history)


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
# two can never drift apart.
_EXPLAIN_CALLS = frozenset(
    {
        "abs",
        "aiter",
        "all",
        "anext",
        "any",
        "ascii",
        "bin",
        "breakpoint",
        "callable",
        "chr",
        "compile",
        "dir",
        "divmod",
        "eval",
        "exec",
        "exit",
        "filter",
        "format",
        "getattr",
        "globals",
        "hasattr",
        "hash",
        "help",
        "hex",
        "id",
        "input",
        "isinstance",
        "issubclass",
        "iter",
        "len",
        "locals",
        "map",
        "max",
        "min",
        "next",
        "oct",
        "open",
        "ord",
        "pow",
        "print",
        "quit",
        "repr",
        "reversed",
        "round",
        "setattr",
        "sorted",
        "sum",
        "type",
        "vars",
    }
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
    "walrus": "(x := 1)",
    "match": "match x:\n    case _:\n        pass",
    "fstring": 'f"{x}"',
    "subscript": "x[0]",
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
            print(  # noqa: T201
                _color(f"poop: unknown meta-command :{cmd} — try :help", _RED),
                file=sys.stderr,
            )

    def _meta_methods(self, arg: str) -> None:
        if not arg:
            print("usage: :methods <expr>")  # noqa: T201
            return
        if not _is_safe_expr(arg):
            print(  # noqa: T201
                _color(
                    "poop: :methods takes a variable or literal — calls are "
                    "not evaluated",
                    _RED,
                ),
                file=sys.stderr,
            )
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
            print(_color(f"poop: {exc}", _RED), file=sys.stderr)  # noqa: T201
            return
        names = sorted(n for n in dir(obj) if not n.startswith("_"))
        header = f"{type(obj).__name__} understands {len(names)} messages:"
        print(_color(header, _DIM))  # noqa: T201
        print(textwrap.fill("  ".join(names), width=80))  # noqa: T201

    def _meta_explain(self, arg: str) -> None:
        if not arg:
            print("usage: :explain <construct>")  # noqa: T201
            return
        snippet = _explain_snippet(arg)
        if snippet is None:
            known = sorted(_EXPLAIN_CALLS | set(_EXPLAIN_SNIPPETS))
            print(  # noqa: T201
                f"poop: nothing to explain about {arg!r} — it may simply be "
                "allowed.\nKnown constructs:"
            )
            print(textwrap.fill("  ".join(known), width=80))  # noqa: T201
            return
        errors = self._interpreter.validate_all(snippet, "<explain>")
        if not errors:
            print(f"{arg} is allowed in POOP.")  # noqa: T201
            return
        for err in errors:
            print(err.args[0])  # noqa: T201

    def _displayhook(self, value: object) -> None:
        if value is None:
            return
        self._ns["_"] = value
        print(_colorize_value(value))  # noqa: T201

    def run(self) -> None:
        print(_BANNER)  # noqa: T201
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
                    print(_color(f"poop: {exc}", _RED), file=sys.stderr)  # noqa: T201
                    buffer = []
                    continue

                if result is None:
                    continue

                buffer = []
                if not source.strip():
                    continue

                try:
                    self._interpreter.run_source_repl(source, self._ns)
                except PoopError as exc:
                    print(_color(f"poop: {exc}", _RED), file=sys.stderr)  # noqa: T201
        finally:
            sys.displayhook = original_hook
