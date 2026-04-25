import argparse
import sys
from pathlib import Path

from poop.errors import PoopError
from poop.interpreter import Interpreter


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="poop",
        description="Python interpreter infected by Smalltalk",
    )
    parser.add_argument("file", type=Path, nargs="?", help="Python source file to run")
    args = parser.parse_args()

    interpreter = Interpreter()
    if args.file is None:
        from poop.repl import Repl

        Repl(interpreter).run()
    else:
        try:
            interpreter.run_file(args.file)
        except PoopError as exc:
            print(f"poop: {exc}", file=sys.stderr)  # noqa: T201
            sys.exit(1)


if __name__ == "__main__":  # pragma: no cover
    main()
