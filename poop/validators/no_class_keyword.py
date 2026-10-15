import ast

from poop.validators.base import CollectingValidator, ErrorCollector


def _spelled(keyword: ast.keyword) -> str:
    """The keyword as written: `foo`, or `**opts` for a splat."""
    return keyword.arg if keyword.arg is not None else f"**{ast.unparse(keyword.value)}"


class _Visitor(ErrorCollector):
    """Refuses every keyword in a `class` statement.

    A keyword here is CPython's class-creation machinery — `metaclass=`, or an
    argument for `__init_subclass__` — and each spelling answered CPython:
    `class X(foo=1)` read `X.__init_subclass__() takes no keyword arguments`,
    `class X(Object, metaclass=Object)` read `metaclass conflict`. Only
    `metaclass=type` was refused, and by `no_type` banning the name. An
    `ast.keyword` also hangs off every call, so this is not a `NodeValidator`
    row: the position is what is refused, not the node.
    """

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        for keyword in node.keywords:
            self.report(
                f"class keyword '{_spelled(keyword)}' is forbidden — "
                f"a class is built from its bases alone",
                keyword,
            )
        self.generic_visit(node)


class NoClassKeywordValidator(CollectingValidator):
    visitor = _Visitor
