"""POOP's own diagnostics are carried by POOP exception classes.

A wrapper that composes a POOP message and raises a native `TypeError` labels
its own advice with Python's vocabulary, and — because the mirrors subclass
their native twin — nothing at runtime tells the two apart. The rule is only
enforceable as a sweep: per-site tests cannot stop the next wrapper from
reintroducing it, which is exactly how the sites this replaced accumulated.
"""

import ast
from pathlib import Path

import pytest

from poop.types.exceptions import MIRRORS

_ROOT = Path(__file__).resolve().parents[1]
_PACKAGES = ("poop/types", "poop/transformers")

# Enclosing function -> why the native class stays. Keyed by function rather
# than by line, which moves, or by file, which holds both kinds of raise.
_EXEMPT: dict[str, str] = {
    # Python's attribute protocol answering Python's own probe for `__copy__`
    # and friends — never read by a program, and reached while `exceptions` is
    # still importing, so the table it would consult may not hold the name yet.
    "__getattr__": "attribute protocol, not a diagnostic",
    # A subclass contract: `_dict_view` declares the hook, the view implements
    # it. No program can reach an unimplemented one.
    "_repr_items": "abstract stub",
    # Import-time wiring check — it fires before any program runs.
    "_merge_bindings": "import-time duplicate-binding guard",
}


class _Raises(ast.NodeVisitor):
    """Collects every `raise` with the function that encloses it."""

    def __init__(self) -> None:
        self.stack: list[str] = []
        self.found: list[tuple[ast.Raise, str]] = []

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self.stack.append(node.name)
        self.generic_visit(node)
        self.stack.pop()

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_Raise(self, node: ast.Raise) -> None:
        self.found.append((node, self.stack[-1] if self.stack else ""))
        self.generic_visit(node)


def _sources() -> list[Path]:
    return sorted(
        path
        for package in _PACKAGES
        for path in (_ROOT / package).rglob("*.py")
        if "__pycache__" not in path.parts
    )


def _raises() -> list[tuple[Path, ast.Raise, str]]:
    collected: list[tuple[Path, ast.Raise, str]] = []
    for path in _sources():
        visitor = _Raises()
        visitor.visit(ast.parse(path.read_text(encoding="utf-8")))
        collected.extend((path, node, func) for node, func in visitor.found)
    return collected


def _raised_name(node: ast.Raise) -> str | None:
    """The bare class name raised, if the raise names one directly."""
    exc = node.exc
    if isinstance(exc, ast.Call):
        exc = exc.func
    return exc.id if isinstance(exc, ast.Name) else None


def _mirror_key(node: ast.Raise) -> str | None:
    """The `MIRRORS[...]` key raised, if the raise goes through the table."""
    exc = node.exc
    if isinstance(exc, ast.Call):
        exc = exc.func
    if (
        isinstance(exc, ast.Subscript)
        and isinstance(exc.value, ast.Name)
        and exc.value.id == "MIRRORS"
        and isinstance(exc.slice, ast.Constant)
        and isinstance(exc.slice.value, str)
    ):
        return exc.slice.value
    return None


def test_no_native_exception_class_is_raised() -> None:
    offenders = [
        f"{path.relative_to(_ROOT)}:{node.lineno} raises {_raised_name(node)}"
        for path, node, func in _raises()
        if _raised_name(node) in MIRRORS and func not in _EXEMPT
    ]
    assert offenders == [], (
        "raise MIRRORS[...] instead — a POOP diagnostic on a native class "
        "labels POOP's own advice with Python's vocabulary"
    )


def test_every_mirror_key_raised_exists() -> None:
    """A typo in the key would otherwise surface as a KeyError at runtime."""
    keys = [
        (path.relative_to(_ROOT), node.lineno, key)
        for path, node, _ in _raises()
        if (key := _mirror_key(node)) is not None
    ]
    unknown = [entry for entry in keys if entry[2] not in MIRRORS]
    assert unknown == []
    # Guards the sweep itself: a walker that stopped matching would report a
    # clean run rather than a broken one.
    assert len(keys) > 20


@pytest.mark.parametrize("func", sorted(_EXEMPT))
def test_every_exemption_is_still_used(func: str) -> None:
    """An exemption outliving its raise silently widens the rule."""
    assert any(
        enclosing == func and _raised_name(node) in MIRRORS
        for _, node, enclosing in _raises()
    )
