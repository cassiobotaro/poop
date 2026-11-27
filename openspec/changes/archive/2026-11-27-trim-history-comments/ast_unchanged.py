"""Exit 1 if any changed `poop/` module differs from BASE in more than prose.

Usage: uv run python openspec/changes/trim-history-comments/ast_unchanged.py [BASE]

BASE defaults to the commit that proposed this change, whose `poop/` is the
tree before the sweep. Comments never reach the AST. A docstring is dropped
before the comparison, or blanked when it is its body's only statement, since
removing it there would leave an empty body.
"""

import ast
import subprocess
import sys
from pathlib import Path

BASE = sys.argv[1] if len(sys.argv) > 1 else "90f4053c"


def _git(*args: str) -> str:
    return subprocess.run(  # noqa: S603 — fixed git arguments
        ["git", *args],  # noqa: S607 — git from PATH, as a developer runs it
        check=True,
        capture_output=True,
        text=True,
    ).stdout


def _without_docstrings(source: str) -> str:
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if not isinstance(
            node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
        ):
            continue
        match node.body:
            case [ast.Expr(value=ast.Constant(value=str())) as doc, *rest]:
                if rest:
                    node.body = rest
                else:
                    doc.value = ast.Constant(value="")
    return ast.dump(tree, include_attributes=False)


def main() -> int:
    changed = _git("diff", "--name-only", BASE, "--", "poop/").split()
    differing = [
        path
        for path in changed
        if path.endswith(".py")
        and _without_docstrings(_git("show", f"{BASE}:{path}"))
        != _without_docstrings(Path(path).read_text(encoding="utf-8"))
    ]
    for path in differing:
        print(path)  # noqa: T201
    return 1 if differing else 0


if __name__ == "__main__":
    sys.exit(main())
