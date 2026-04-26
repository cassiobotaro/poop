import ast
from typing import ClassVar

from poop.transformers.base import BaseTransformer
from poop.types.complex import Complex


def _poop_complex_literal(value: complex) -> Complex:
    return Complex(value)


def _poop_complex_from(real: object = None, imag: object = None) -> Complex:
    from poop.types.float import Float
    from poop.types.int import Int
    from poop.types.string import Str

    if real is None:
        return Complex(complex(0, 0))
    if imag is None:
        if isinstance(real, Complex):
            return real
        if isinstance(real, (Int, Float)):
            return Complex(complex(real._value, 0))
        if isinstance(real, Str):
            return Complex(complex(real._value))
        return Complex(complex(0, 0))
    r = real._value if isinstance(real, (Int, Float)) else 0  # type: ignore[union-attr]
    i = imag._value if isinstance(imag, (Int, Float)) else 0  # type: ignore[union-attr]
    return Complex(complex(r, i))


class _ComplexRewriter(ast.NodeTransformer):
    def visit_BinOp(self, node: ast.BinOp) -> ast.AST:
        # Fold `r ± ij` literal patterns (e.g. 1+2j, 3.0-1j) into a single Complex.
        # Python parses these as BinOp instead of a single complex Constant.
        if (
            isinstance(node.op, (ast.Add, ast.Sub))
            and isinstance(node.left, ast.Constant)
            and isinstance(node.right, ast.Constant)
            and isinstance(node.right.value, complex)
            and isinstance(node.left.value, (int, float))
        ):
            imag_part = node.right.value
            if isinstance(node.op, ast.Sub):
                imag_part = -imag_part
            combined = complex(node.left.value, imag_part.imag)
            return ast.copy_location(
                ast.Call(
                    func=ast.Name(id="_poop_complex_literal", ctx=ast.Load()),
                    args=[ast.Constant(value=combined)],
                    keywords=[],
                ),
                node,
            )
        self.generic_visit(node)
        return node

    def visit_Constant(self, node: ast.Constant) -> ast.AST:
        if isinstance(node.value, complex):
            return ast.copy_location(
                ast.Call(
                    func=ast.Name(id="_poop_complex_literal", ctx=ast.Load()),
                    args=[node],
                    keywords=[],
                ),
                node,
            )
        return node

    def visit_Call(self, node: ast.Call) -> ast.AST:
        self.generic_visit(node)
        if (
            isinstance(node.func, ast.Name)
            and node.func.id == "complex"
            and not node.keywords
            and len(node.args) <= 2
        ):
            return ast.copy_location(
                ast.Call(
                    func=ast.Name(id="_poop_complex_from", ctx=ast.Load()),
                    args=node.args,
                    keywords=[],
                ),
                node,
            )
        return node


class ComplexTransformer(BaseTransformer):
    rewriter = _ComplexRewriter
    BINDINGS: ClassVar[dict[str, object]] = {
        "_poop_complex_literal": _poop_complex_literal,
        "_poop_complex_from": _poop_complex_from,
    }
