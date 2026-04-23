import ast
from typing import ClassVar


def _poop_raise(exc_type: type[BaseException], *args: object) -> None:
    raise exc_type(*args)


class RaiseTransformer:
    """Intercepts UppercaseName.raise_(args) and rewrites to _poop_raise(UppercaseName, *args).

    This allows POOP code to raise exceptions using message-passing syntax:
        KeyError.raise_("key not found")
    instead of the forbidden `raise` statement.

    Only intercepts calls where the receiver is a simple Name starting with an
    uppercase letter (Python convention for classes/exception types).
    """

    BINDINGS: ClassVar[dict[str, object]] = {
        "_poop_raise": _poop_raise,
    }

    def transform(self, tree: ast.Module) -> ast.Module:
        tree = _RaiseRewriter().visit(tree)
        ast.fix_missing_locations(tree)
        return tree


class _RaiseRewriter(ast.NodeTransformer):
    def visit_Call(self, node: ast.Call) -> ast.AST:
        self.generic_visit(node)
        if (
            isinstance(node.func, ast.Attribute)
            and node.func.attr == "raise_"
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id[:1].isupper()
        ):
            return ast.copy_location(
                ast.Call(
                    func=ast.Name(id="_poop_raise", ctx=ast.Load()),
                    args=[
                        ast.Name(id=node.func.value.id, ctx=ast.Load()),
                        *node.args,
                    ],
                    keywords=[],
                ),
                node,
            )
        return node
