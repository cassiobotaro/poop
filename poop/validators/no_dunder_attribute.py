import ast

from poop.types._selectors import is_dunder
from poop.validators.base import CollectingValidator, ErrorCollector

# `super().__init__(...)` is an `ast.Attribute` with a dunder attr, and
# ADR 18 allows `super` explicitly
# (`doc/adr/0018-class-machinery-is-accepted-only-where-it-was-argued-for.md`):
# without it, subclasses cannot extend parent behaviour and inheritance
# breaks, and there is no message-passing substitute. A blanket rule would contradict that.
_ALLOWED = frozenset({"__init__"})

# Named substitutes, so the message teaches rather than only refuses. The rule
# below is not a list, though: anything dunder-shaped is rejected, named here
# or not. An enumerated ban is always one name short — `x.__class__.__name__`
# answers a raw `str`, and a list that missed `__name__` would let it through.
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
    name: str,
    *,
    dotted: bool = True,
    allow_init: bool | None = None,
    scope: str = "global",
) -> str | None:
    """The rejection for `name`, or None when it is not a forbidden dunder.

    Shared with `Object`'s runtime guard: `get_attr("__dict__")` reopens
    exactly what this validator closes, and a computed name puts that spelling
    beyond any validator's reach — so the two halves of one ban must say one
    thing. `no_dunder_name` reads it too, with `dotted=False`: a dunder
    *global* (`__builtins__`) is the same ban one node type over. `scope` is
    what an undotted name is, so the sentence calls a class-body
    `__slots__ = ("a",)` a class attribute, not a global.

    `allow_init` controls the `__init__` carve-out apart from `dotted`,
    because the two answer unrelated questions ("how do I spell the label?"
    and "is this the `super().__init__(...)` syntax?"). `get_attr` is
    dotted-shaped but is not that syntax, and exempting it would let
    `s.get_attr("__init__")("ZAP")` re-run the constructor on a live `Str`,
    making every immutable wrapper mutable and losing the entry of a `Dict`
    keyed on one. It defaults to `dotted`. See
    `doc/adr/0033-dunder-access-is-banned-by-rule-at-runtime-too-init-only-on-a-super-receiver.md`.
    """
    if not is_dunder(name):
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
    kind = (
        "dunders are Python's protocol" if dotted else f"dunder {scope}s are Python's"
    )
    return f"{label} is forbidden — {kind}, not POOP's message surface"


def _is_super_call(node: ast.expr) -> bool:
    """Is `node` the `super()` in `super().__init__(...)`?

    The carve-out is for that syntax, not for the *name*: on any other
    receiver `s.__init__("zap")` would re-run the constructor on a live
    value, leaving `Str`, `Int` and `Tuple` all mutable and a `Dict` keyed on
    one holding an entry reachable under neither the old spelling nor the new.
    It is the hazard `_reject_dunder` describes for the `get_attr` path, by
    the shorter spelling.
    """
    match node:
        case ast.Call(func=ast.Name(id="super")):
            return True
    return False


class _Visitor(ErrorCollector):
    def visit_Attribute(self, node: ast.Attribute) -> None:
        message = dunder_message(node.attr, allow_init=_is_super_call(node.value))
        if message is not None:
            self.report(message, node)
        self.generic_visit(node)


class NoDunderAttributeValidator(CollectingValidator):
    visitor = _Visitor
