import ast

from poop.validators.base import CollectingValidator, ErrorCollector

# Each dunder a user class must not define, with the sentence that refuses it.
# A deny-list rather than an allow-list: the slots INFECTIONS.md says a class
# *may* define — `__init__`, `__str__`, `__repr__`, `__bool__`, `__hash__`,
# `__len__`, `__call__`, `__iter__`, `__next__`, `__enter__`, `__exit__`, the
# comparisons and some forty operator slots — are the long list, and missing
# one there refuses a legal program, where missing one here leaves a leak the
# wording sweep catches.
_LOOKUP = "it is Python's lookup protocol"
_CREATION = "a class is built from its bases alone"
_DESCRIPTOR = "a POOP object is reached by messages, not by descriptors"
_REFUSED: dict[str, str] = {
    "__getattribute__": (
        f"{_LOOKUP}; define does_not_understand(self, name) "
        f"for the messages the class does not answer"
    ),
    "__getattr__": "define does_not_understand(self, name) instead",
    "__setattr__": f"{_LOOKUP}; set_attr already answers an assignment",
    "__delattr__": f"{_LOOKUP}; del_attr already answers a removal",
    "__dir__": f"{_LOOKUP}; dir already answers the messages an object understands",
    "__new__": _CREATION,
    "__init_subclass__": _CREATION,
    "__class_getitem__": _CREATION,
    "__subclasshook__": _CREATION,
    "__set_name__": _DESCRIPTOR,
    "__get__": _DESCRIPTOR,
    "__set__": _DESCRIPTOR,
    "__delete__": _DESCRIPTOR,
}


class _Visitor(ErrorCollector):
    """Refuses a `def` of a lookup, creation or descriptor dunder in a class body.

    `no_dunder_attribute` bans *reading* a dunder and `no_dunder_name` a bare
    dunder name, but a class body could still *define* `__getattribute__` and
    rewire every message sent to its instances, or `__set_name__` and be handed
    a raw `str` by CPython, with no validator looking. The operator and
    protocol slots stay legal: INFECTIONS.md lists them as the ones a class
    may satisfy, and `PoopMeta.__new__` adapts the five CPython reads itself.
    """

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        for stmt in node.body:
            match stmt:
                case ast.FunctionDef(name=name) | ast.AsyncFunctionDef(name=name) if (
                    name in _REFUSED
                ):
                    self.report(
                        f"defining {name} is forbidden — {_REFUSED[name]}", stmt
                    )
        self.generic_visit(node)


class NoDunderDefValidator(CollectingValidator):
    visitor = _Visitor
