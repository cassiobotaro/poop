import atexit
import codeop
import sys
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


class Repl:
    def __init__(self, interpreter: Interpreter) -> None:
        self._interpreter = interpreter
        self._ns: dict[str, object] = dict(DEFAULT_NAMESPACE)
        _setup_readline(self._ns)

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
