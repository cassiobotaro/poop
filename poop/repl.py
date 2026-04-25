import atexit
import codeop
import sys
from pathlib import Path

from poop.errors import PoopError
from poop.interpreter import Interpreter
from poop.transformers import DEFAULT_NAMESPACE

_BANNER = "POOP 💩  — Python infected by Smalltalk. Ctrl+D to exit."
_HISTORY_FILE = Path.home() / ".poop_history"
_HISTORY_MAX = 1000


def _setup_readline(namespace: dict[str, object]) -> None:
    try:
        import readline
        import rlcompleter
    except ImportError:
        return

    readline.parse_and_bind("tab: complete")
    readline.set_completer(rlcompleter.Completer(namespace).complete)
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
        print(repr(value))  # noqa: T201

    def run(self) -> None:
        print(_BANNER)  # noqa: T201
        buffer: list[str] = []
        original_hook = sys.displayhook
        sys.displayhook = self._displayhook

        try:
            while True:
                try:
                    indent = _indent_for(buffer)
                    line = _readline_input("... " if buffer else ">>> ", indent)
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
                    print(f"poop: {exc}", file=sys.stderr)  # noqa: T201
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
                    print(f"poop: {exc}", file=sys.stderr)  # noqa: T201
        finally:
            sys.displayhook = original_hook
