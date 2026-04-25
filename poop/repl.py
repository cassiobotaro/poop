import codeop
import sys

from poop.errors import PoopError
from poop.interpreter import Interpreter
from poop.transformers import DEFAULT_NAMESPACE

_BANNER = "POOP 💩  — Python infected by Smalltalk. Ctrl+D to exit."


class Repl:
    def __init__(self, interpreter: Interpreter) -> None:
        self._interpreter = interpreter
        self._ns: dict[str, object] = dict(DEFAULT_NAMESPACE)

    def run(self) -> None:
        print(_BANNER)  # noqa: T201
        buffer: list[str] = []

        while True:
            try:
                line = input("... " if buffer else ">>> ")
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
