import ast

from poop.validators.base import CollectingValidator, ErrorCollector

_ALIAS_MESSAGE = "type aliases are forbidden — POOP types differ from Python builtins"


def _spelled(node: ast.TypeVar | ast.ParamSpec | ast.TypeVarTuple) -> str:
    """The parameter as the program wrote it between the brackets."""
    match node:
        case ast.TypeVarTuple(name=name):
            return f"*{name}"
        case ast.ParamSpec(name=name):
            return f"**{name}"
        case _:
            return node.name


class _Visitor(ErrorCollector):
    """Refuses `type X = …` and every PEP 695 type parameter.

    A type parameter is not a `NodeValidator` row because its sentence names
    the parameter as written — `[T]`, `[*Ts]`, `[**P]` — so a reader sees
    what to drop. Left unvalidated, `class X[T]:` reached CPython's generic
    intrinsic, which imports `typing` through a builtin the allow-list
    withholds and died with `KeyError: '__import__'`, and `def m[T](self):`
    handed the method a raw `typing.TypeVar`.
    """

    def visit_TypeAlias(self, node: ast.TypeAlias) -> None:
        self.report(_ALIAS_MESSAGE, node)
        self.generic_visit(node)

    def _type_param(self, node: ast.TypeVar | ast.ParamSpec | ast.TypeVarTuple) -> None:
        self.report(
            f"type parameters are forbidden — POOP has no static types; "
            f"drop the [{_spelled(node)}]",
            node,
        )
        self.generic_visit(node)

    visit_TypeVar = visit_ParamSpec = visit_TypeVarTuple = _type_param


class NoTypeAliasValidator(CollectingValidator):
    visitor = _Visitor
