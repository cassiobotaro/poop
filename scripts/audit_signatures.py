"""Signature audit for POOP namespace wrappers.

Walks each lowercase stdlib mirror in DEFAULT_NAMESPACE, compares its
public surface against the corresponding CPython module, and writes
findings to docs/signature-audit.md.

Categories surfaced:
- missing-name     : CPython exposes it, POOP doesn't
- extra-name       : POOP exposes it, CPython doesn't (POOP-only)
- attr-vs-method   : CPython attribute, POOP method (violates convention)
- method-vs-attr   : CPython method/function, POOP attribute (rare)
- param-mismatch   : same name on both sides, but signature differs
- inspect-blind    : signature could not be introspected (likely *args/**kwargs)

False positives are expected and should be marked OK-sanctioned in
the triage doc.
"""

from __future__ import annotations

import importlib
import inspect
import sys
from collections.abc import Iterable
from dataclasses import dataclass

from poop.transformers import DEFAULT_NAMESPACE


@dataclass(frozen=True)
class Finding:
    module: str
    name: str
    category: str
    detail: str


def _public_names(obj: object) -> set[str]:
    return {n for n in dir(obj) if not n.startswith("_")}


def _inherited_object_methods() -> set[str]:
    from poop.types.object import Object

    return _public_names(Object)


_INHERITED = _inherited_object_methods() | _public_names(object) | _public_names(type)

# Tuple aliased so the `except` clause keeps its parentheses —
# `ruff format` (as of 0.15.x) strips parens from `except (A, B, C):`
# which is invalid Python 3 syntax.
_BLIND_ERRORS = (ValueError, TypeError, NameError, AttributeError)


def _classify(py_attr: object, poop_attr: object) -> tuple[str, str]:
    """Return (category, detail). Empty category means OK."""
    py_is_callable = callable(py_attr) and not isinstance(py_attr, type)
    poop_is_callable = callable(poop_attr) and not isinstance(poop_attr, type)
    poop_is_property = isinstance(poop_attr, property)

    py_is_data = not py_is_callable and not isinstance(py_attr, type)
    poop_is_data = (
        not poop_is_callable
        and not poop_is_property
        and not isinstance(poop_attr, type)
    )

    if py_is_data and poop_is_callable:
        return "attr-vs-method", "CPython is an attribute, POOP exposes a method"
    if py_is_callable and (poop_is_data or poop_is_property):
        return "method-vs-attr", "CPython is callable, POOP exposes a data/property"

    if py_is_callable and poop_is_callable:
        try:
            py_sig = inspect.signature(py_attr)
        except _BLIND_ERRORS:
            return "inspect-blind", "CPython signature not introspectable"
        try:
            poop_sig = inspect.signature(poop_attr)
        except _BLIND_ERRORS:
            return "inspect-blind", "POOP signature not introspectable"

        py_params = [
            (p.name, p.default is inspect.Parameter.empty)
            for p in py_sig.parameters.values()
            if p.kind
            not in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)
        ]
        poop_params = [
            (p.name, p.default is inspect.Parameter.empty)
            for p in poop_sig.parameters.values()
            if p.kind
            not in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)
            and p.name != "self"
        ]
        if py_params != poop_params:
            return (
                "param-mismatch",
                f"CPython `{py_sig}` vs POOP `{poop_sig}`",
            )

    return "", ""


def _audit_module(name: str, poop_class: object) -> Iterable[Finding]:
    try:
        py_module = importlib.import_module(name)
    except ImportError as exc:
        yield Finding(name, "<module>", "import-error", str(exc))
        return

    py_names = _public_names(py_module)
    poop_names = _public_names(poop_class) - _INHERITED

    for n in sorted(py_names - poop_names):
        yield Finding(name, n, "missing-name", f"CPython has `{name}.{n}`")

    for n in sorted(poop_names - py_names):
        yield Finding(
            name, n, "extra-name", f"POOP-only addition (no `{name}.{n}` in CPython)"
        )

    for n in sorted(py_names & poop_names):
        py_attr = getattr(py_module, n)
        poop_attr = inspect.getattr_static(poop_class, n)
        # Unwrap staticmethod for signature comparison
        if isinstance(poop_attr, staticmethod):
            poop_attr = poop_attr.__func__
        category, detail = _classify(py_attr, poop_attr)
        if category:
            yield Finding(name, n, category, detail)


def _stdlib_mirrors() -> list[tuple[str, object]]:
    return [
        (name, value)
        for name, value in sorted(DEFAULT_NAMESPACE.items())
        if not name.startswith("_poop_")
        and name.islower()
        and name in sys.stdlib_module_names
    ]


_CATEGORY_ORDER = [
    "attr-vs-method",
    "method-vs-attr",
    "param-mismatch",
    "extra-name",
    "inspect-blind",
    "import-error",
    "missing-name",
]

_CATEGORY_BLURB = {
    "attr-vs-method": "**Highest priority** — CPython exposes an attribute, POOP exposes a zero-arg method. Violates the mirror-Python convention. Each row should be fixed unless explicitly sanctioned.",
    "method-vs-attr": "CPython is callable, POOP exposes a property/data attribute. Rare; usually a bug.",
    "param-mismatch": "Both sides expose a callable, but the signatures differ (parameter names, defaults, or order). Triage each: keyword spelling drift is fix-worthy; sanctioned divergences (e.g., POOP renamed a Python kw to avoid a banned-builtin shadow) should be marked OK-sanctioned.",
    "extra-name": "POOP exposes a name that doesn't exist in CPython. May be a deliberate POOP-only convenience (mark OK-sanctioned) or accidental leak.",
    "inspect-blind": "Signature could not be introspected on one side. Usually because POOP wraps with `*args, **kwargs` or CPython exposes a C-built-in. Audit manually if you want.",
    "import-error": "Stdlib module could not be imported on this platform — informational only.",
    "missing-name": "CPython exposes a name that POOP does not. The largest bucket — most rows here are intentional omissions (helpers, deprecated APIs, niche classes). Skim for anything that ought to be exposed.",
}


def main() -> None:
    findings: list[Finding] = []
    mirrors = _stdlib_mirrors()
    for module_name, poop_value in mirrors:
        # `random` is bound as an instance, not a class — use its class for audit.
        poop_class = (
            type(poop_value) if not isinstance(poop_value, type) else poop_value
        )
        findings.extend(_audit_module(module_name, poop_class))

    by_category: dict[str, list[Finding]] = {c: [] for c in _CATEGORY_ORDER}
    for f in findings:
        by_category.setdefault(f.category, []).append(f)

    print("# Signature audit baseline")
    print()
    print(
        f"_Generated by `scripts/audit_signatures.py` against {len(mirrors)} stdlib mirrors. "
        f"{len(findings)} findings total._"
    )
    print()
    print(
        "Convention reference: see [INFECTIONS.md § Project conventions]"
        "(../INFECTIONS.md#project-conventions). Mark each row as `fix`, "
        "`defer-v0.6.0`, or `OK-sanctioned`."
    )
    print()
    print("## Summary")
    print()
    print("| Category | Count |")
    print("|---|---|")
    for cat in _CATEGORY_ORDER:
        print(f"| {cat} | {len(by_category[cat])} |")
    print()

    for cat in _CATEGORY_ORDER:
        rows = by_category[cat]
        if not rows:
            continue
        print(f"## {cat} ({len(rows)})")
        print()
        print(_CATEGORY_BLURB.get(cat, ""))
        print()
        print("| Module | Name | Detail | Decision |")
        print("|---|---|---|---|")
        for f in rows:
            detail = f.detail.replace("|", "\\|").replace("\n", " ")
            print(f"| `{f.module}` | `{f.name}` | {detail} | |")
        print()


if __name__ == "__main__":
    main()
