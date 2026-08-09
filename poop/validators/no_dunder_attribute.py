import ast

from poop.errors import ValidationError
from poop.validators.base import CollectingValidator, ErrorCollector, collect_errors

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
    # Only ever reached with the carve-out off — see `allow_init` below.
    "__init__": "Klass(...)",
    "__len__": "obj.len()",
    "__mro__": "Klass.superclass()",
    "__name__": "Klass.name()",
}

_DICT_REASON = (
    "it is vars(obj) by another spelling, exposing raw Python-native slot "
    "values; state lives in instances, reached by messages"
)


def dunder_message(
    name: str, *, dotted: bool = True, allow_init: bool | None = None
) -> str | None:
    """The rejection for `name`, or None when it is not a forbidden dunder.

    Shared with `Object`'s runtime guard: `get_attr("__dict__")` reopens
    exactly what this validator closes, and a computed name puts that spelling
    beyond any validator's reach — so the two halves of one ban must say one
    thing. `no_dunder_name` reads it too, with `dotted=False`: a dunder
    *global* (`__builtins__`) is the same ban one node type over.

    `allow_init` controls the `__init__` carve-out, which used to ride on
    `dotted` — one flag standing for two unrelated questions ("how do I spell
    the label?" and "is this the `super().__init__(...)` syntax?"). `get_attr`
    is dotted-shaped but is not that syntax, and it inherited the exemption:
    `s.get_attr("__init__")("ZAP")` re-ran the constructor on a live `Str`, so
    every immutable wrapper was mutable and a `Dict` keyed on one lost the
    entry. It defaults to `dotted`, keeping both AST validators unchanged.
    """
    if not (name.startswith("__") and name.endswith("__")):
        return None
    # `__init__` is carved out for `super().__init__(...)`, an attribute — a
    # bare `__init__` Name has no such use, and neither has `get_attr`.
    if (dotted if allow_init is None else allow_init) and name in _ALLOWED:
        return None
    label = f".{name}" if dotted else name
    if name == "__dict__":
        return f"{label} is forbidden — {_DICT_REASON}"
    substitute = _SUBSTITUTES.get(name)
    if substitute is not None:
        return f"{label} is forbidden — use {substitute} instead"
    kind = "dunders are Python's protocol" if dotted else "dunder globals are Python's"
    return f"{label} is forbidden — {kind}, not POOP's message surface"


def _is_super_call(node: ast.expr) -> bool:
    """Is `node` the `super()` in `super().__init__(...)`?

    The carve-out was written for that syntax and applied to the *name*, so it
    covered any receiver: `s.__init__("zap")` re-ran the constructor on a live
    value, leaving `Str`, `Int` and `Tuple` all mutable and a `Dict` keyed on
    one holding an entry reachable under neither the old spelling nor the new.
    That is the hazard `Object._reject_dunder` already describes word for word
    — it closed the `get_attr` path and left this, the shorter one, open.
    """
    return (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "super"
    )


class _Visitor(ErrorCollector):
    def visit_Attribute(self, node: ast.Attribute) -> None:
        message = dunder_message(node.attr, allow_init=_is_super_call(node.value))
        if message is not None:
            self.report(message, node)
        self.generic_visit(node)


class NoDunderAttributeValidator(CollectingValidator):
    def collect(self, tree: ast.Module) -> list[ValidationError]:
        return collect_errors(_Visitor(), tree)
