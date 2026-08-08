import ast
from typing import ClassVar

from poop.transformers.base import BaseTransformer


def _poop_raise(exc_type: type[BaseException], *args: object, **kwargs: object) -> None:
    raise exc_type(*args, **kwargs)


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
                    # Forwarded, not dropped. `raise` is a statement, so
                    # `raise_` is the only way to signal an error — and an
                    # exception whose fields arrive by keyword could not be
                    # raised at all. The failure named the argument the
                    # program *did* pass: `MyError.raise_("boom", code=42)`
                    # answered `missing 1 required positional argument:
                    # 'code'`. A `**kwargs` entry (`kw.arg is None`) rides
                    # along, since `_poop_raise` takes `**kwargs`.
                    keywords=node.keywords,
                ),
                node,
            )
        return node


class RaiseTransformer(BaseTransformer):
    """Intercepts UppercaseName.raise_(args) and rewrites to _poop_raise(UppercaseName, *args).

    This allows POOP code to raise exceptions using message-passing syntax:
        KeyError.raise_("key not found")
    instead of the forbidden `raise` statement.

    Only intercepts calls where the receiver is a simple Name starting with an
    uppercase letter (Python convention for classes/exception types).
    """

    rewriter = _RaiseRewriter
    BINDINGS: ClassVar[dict[str, object]] = {
        "_poop_raise": _poop_raise,
    }
