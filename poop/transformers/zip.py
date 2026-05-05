import ast
from typing import ClassVar

from poop.transformers.base import BaseTransformer
from poop.types.zip import Zip


def _poop_zip(*sources: object, strict: object = None) -> Zip:
    from poop.types.boolean import Boolean

    s = None if strict is None else (strict if isinstance(strict, Boolean) else None)
    return Zip(*sources, strict=s)


class _ZipRewriter(ast.NodeTransformer):
    def visit_Call(self, node: ast.Call) -> ast.AST:
        self.generic_visit(node)
        if isinstance(node.func, ast.Name) and node.func.id == "zip":
            return ast.copy_location(
                ast.Call(
                    func=ast.Name(id="_poop_zip", ctx=ast.Load()),
                    args=node.args,
                    keywords=node.keywords,
                ),
                node,
            )
        return node


class ZipTransformer(BaseTransformer):
    rewriter = _ZipRewriter
    BINDINGS: ClassVar[dict[str, object]] = {"_poop_zip": _poop_zip}
