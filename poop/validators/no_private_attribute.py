"""`obj._value` is reaching into an object; `obj.get_attr(name)` says so.

The two *guarded* spellings of reaching into an object were already closed.
The third — the one a reader would actually type — was open, and what it
answered was a naked Python primitive:

    "abc".get_attr("_value")   # _value is private — POOP objects do not expose
                               #   their internals
    "abc"._value               # 'abc', a Python str
    "abc"._value.print()       # 'str' object has no attribute 'print'

That contradicts the language's first principle twice over. `INFECTIONS.md`
says "no naked Python primitive ever reaches runtime" and "Python native types
must not leak into POOP code"; the second line hands one out on request. And
the object that comes back answers nothing, in CPython's vocabulary — `'str'
object has no attribute 'print'` is precisely the sentence
`does_not_understand` exists to replace, reachable from a two-token expression.

The blind spot was visible in the code that worked around it.
`_selectors.is_message` explains that the REPL completer used to offer
`x._value` and calls that "the encapsulation leak taught by the tool meant to
teach the language" — the completer stopped *offering* the spelling, and the
spelling still worked. And `examples/patterns/memento.py` opens by showing
`saved = editor._content` as the procedural Python that POOP exists to prevent
(`# poking at internals`, in the example's own comment). The language taught
the rule in an example and did not enforce it.

`no_dunder_attribute` is the shape of the answer and shows it is enforceable
syntactically: it refuses `.__class__` at parse time on any receiver, and names
the substitute. The mangled `_poop_*` half is already covered by
`no_poop_prefix`, which reserves those names; this is the same reservation for
the single-underscore internals every wrapper declares in `__slots__`.
"""

import ast

from poop.errors import ValidationError
from poop.validators.base import CollectingValidator, ErrorCollector, collect_errors

# Receivers an object may reach a private name on, because reaching your own
# state is not reaching *into* anything.
#
# `cls` for a `classmethod`, and the enclosing class by its own name for a
# `@staticmethod`, which has neither `self` nor `cls` to write. That last is
# not hypothetical: it is one site, `Transaction._commit` in
# `examples/patterns/execute_around.py`. A sweep over `examples/` reports that
# single case and nothing else, so the rule costs one allowance and no
# rewrites.
_OWN = frozenset({"self", "cls"})


def private_message(name: str) -> str:
    """The rejection for a private attribute read or written by name."""
    return (
        f".{name} is forbidden — a leading underscore is an object's own "
        f"state; use obj.get_attr(name) to ask for it by name"
    )


def _is_private(name: str) -> bool:
    """A single leading underscore, and not a dunder.

    Dunders belong to `no_dunder_attribute`, which says something more specific
    about each of them, and `_poop_*` to `no_poop_prefix`, which reserves the
    whole family. Refusing them here too would answer two sentences for one
    spelling.
    """
    if name.startswith("_poop_"):
        return False
    return name.startswith("_") and not (name.startswith("__") and name.endswith("__"))


class _Visitor(ErrorCollector):
    def __init__(self, own_classes: frozenset[str]) -> None:
        super().__init__()
        self._own_classes = own_classes

    def visit_Attribute(self, node: ast.Attribute) -> None:
        receiver = node.value
        named = isinstance(receiver, ast.Name) and (
            receiver.id in _OWN or receiver.id in self._own_classes
        )
        if _is_private(node.attr) and not named:
            self.report(private_message(node.attr), node)
        self.generic_visit(node)


class _ClassNames(ast.NodeVisitor):
    """Every class name the module defines, for the `@staticmethod` allowance."""

    def __init__(self) -> None:
        self.names: set[str] = set()

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.names.add(node.name)
        self.generic_visit(node)


class NoPrivateAttributeValidator(CollectingValidator):
    def collect(self, tree: ast.Module) -> list[ValidationError]:
        names = _ClassNames()
        names.visit(tree)
        return collect_errors(_Visitor(frozenset(names.names)), tree)
