import ast
from typing import ClassVar

from poop.transformers.base import BaseTransformer
from poop.types.zip import Zip


def _poop_zip(*sources: object, strict: object = None) -> Zip:
    from poop.types._unwrap import _is_absent
    from poop.types.boolean import Boolean

    if _is_absent(strict):
        return Zip(*sources, strict=None)
    if isinstance(strict, Boolean):
        return Zip(*sources, strict=strict)
    raise TypeError(f"strict must be Boolean, got {type(strict).__name__}")


class _ZipRewriter(ast.NodeTransformer):
    def visit_Call(self, node: ast.Call) -> ast.AST:
        if isinstance(node.func, ast.Name) and node.func.id == "zip":
            return ast.copy_location(
                ast.Call(
                    func=ast.Name(id="_poop_zip", ctx=ast.Load()),
                    args=[self.visit(arg) for arg in node.args],
                    keywords=[
                        ast.keyword(arg=kw.arg, value=self.visit(kw.value))
                        for kw in node.keywords
                    ],
                ),
                node,
            )
        self.generic_visit(node)
        return node

    def visit_Name(self, node: ast.Name) -> ast.AST:
        if node.id == "zip":
            return ast.copy_location(ast.Name(id="_poop_zip_cls", ctx=node.ctx), node)
        return node


class ZipTransformer(BaseTransformer):
    rewriter = _ZipRewriter
    BINDINGS: ClassVar[dict[str, object]] = {
        "_poop_zip": _poop_zip,
        "_poop_zip_cls": Zip,
    }
