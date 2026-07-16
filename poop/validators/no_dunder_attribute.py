import ast

from poop.errors import ValidationError
from poop.validators.base import CollectingValidator, ErrorCollector

# `super().__init__(...)` is an `ast.Attribute` with a dunder attr, and
# INFECTIONS.md allows `super` explicitly — "without it, subclasses cannot
# extend parent behaviour — inheritance breaks entirely. There is no
# message-passing substitute." A blanket rule would contradict that.
_ALLOWED = frozenset({"__init__"})

# Named substitutes, so the message teaches rather than only refuses. The rule
# below is not a list, though: anything dunder-shaped is rejected, named here
# or not. An enumerated ban was tried on paper and is already incomplete —
# `x.__class__.__name__` answers a raw `str` and would have slipped through.
_SUBSTITUTES = {
    "__abs__": "n.abs()",
    "__bases__": "Klass.superclass()",
    "__class__": "obj.class_()",
    "__contains__": "col.includes(x)",
    "__hash__": "obj.hash()",
    "__len__": "obj.len()",
    "__mro__": "Klass.superclass()",
    "__name__": "Klass.name()",
}

_DICT_MESSAGE = (
    ".__dict__ is forbidden — it is vars(obj) by another spelling, exposing raw "
    "Python-native slot values; state lives in instances, reached by messages"
)


def dunder_message(attr: str) -> str | None:
    """The rejection for `attr`, or None when it is not a forbidden dunder.

    Shared with `Object`'s runtime guard: `get_attr("__dict__")` reopens
    exactly what this validator closes, and a computed name puts that spelling
    beyond any validator's reach — so the two halves of one ban must say one
    thing.
    """
    if not (attr.startswith("__") and attr.endswith("__")) or attr in _ALLOWED:
        return None
    if attr == "__dict__":
        return _DICT_MESSAGE
    substitute = _SUBSTITUTES.get(attr)
    if substitute is not None:
        return f".{attr} is forbidden — use {substitute} instead"
    return (
        f".{attr} is forbidden — dunders are Python's protocol, "
        "not POOP's message surface"
    )


class _Visitor(ErrorCollector):
    def visit_Attribute(self, node: ast.Attribute) -> None:
        message = dunder_message(node.attr)
        if message is not None:
            self.report(message, node)
        self.generic_visit(node)


class NoDunderAttributeValidator(CollectingValidator):
    def collect(self, tree: ast.Module) -> list[ValidationError]:
        visitor = _Visitor()
        visitor.visit(tree)
        return visitor.errors
