import argparse
import sys
from pathlib import Path

from poop import Interpreter
from poop.errors import PoopError


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="poop",
        description="Python interpreter infected by Smalltalk",
    )
    parser.add_argument("file", type=Path, help="Python source file to run")
    args = parser.parse_args()

    interpreter = Interpreter()
    try:
        interpreter.run_file(args.file)
    except PoopError as exc:
        print(f"poop: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
