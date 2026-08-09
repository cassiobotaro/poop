import ast
from typing import ClassVar

from poop.transformers._arity import refuse_extra_arguments
from poop.transformers.base import BaseTransformer
from poop.types._message import article
from poop.types.complex import Complex
from poop.types.exceptions import MIRRORS
from poop.types.float import Float
from poop.types.int import Int
from poop.types.string import Str


def _poop_complex_literal(value: complex) -> Complex:
    return Complex(value)


def _poop_complex_from(*args: object, **kwargs: object) -> Complex:
    refuse_extra_arguments(
        "complex",
        args,
        kwargs,
        most=2,
        built_from="at most a real and an imaginary part",
        hint="write complex(real, imag)",
    )
    real = args[0] if args else None
    imag = args[1] if len(args) > 1 else None
    if real is None:
        return Complex(complex(0, 0))
    if imag is None:
        if isinstance(real, Complex):
            return real
        if isinstance(real, (Int, Float)):
            return Complex(complex(real._value, 0))
        if isinstance(real, Str):
            # `complex() arg is a malformed string` names the builtin as a
            # call; `int` and `float` were reworded to `'zz' is not a valid
            # int` and this was left on CPython's phrasing, in POOP's voice.
            try:
                return Complex(complex(real._value))
            except ValueError:
                raise MIRRORS["ValueError"](
                    f"{real._value!r} is not a valid complex"
                ) from None
        raise MIRRORS["TypeError"](
            f"cannot convert {type(real).__qualname__} to complex"
        )
    if not isinstance(real, (Int, Float)):
        raise MIRRORS["TypeError"](
            f"complex's real part must be int or float, "
            f"got {article(type(real).__qualname__)}"
        )
    if not isinstance(imag, (Int, Float)):
        raise MIRRORS["TypeError"](
            f"complex's imaginary part must be int or float, "
            f"got {article(type(imag).__qualname__)}"
        )
    return Complex(complex(real._value, imag._value))


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
        if isinstance(node.func, ast.Name) and node.func.id == "complex":
            return ast.copy_location(
                ast.Call(
                    func=ast.Name(id="_poop_complex_from", ctx=ast.Load()),
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
        if node.id == "complex":
            return ast.copy_location(ast.Name(id="_poop_complex", ctx=node.ctx), node)
        return node


class ComplexTransformer(BaseTransformer):
    rewriter = _ComplexRewriter
    BINDINGS: ClassVar[dict[str, object]] = {
        "_poop_complex": Complex,
        "_poop_complex_literal": _poop_complex_literal,
        "_poop_complex_from": _poop_complex_from,
    }
