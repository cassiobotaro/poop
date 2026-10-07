import ast

from poop.transformers._arity import refuse_extra_arguments
from poop.transformers.base import BaseTransformer, BuiltinRewriter, call_at
from poop.types._alias import builtin_alias
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
        match real:
            case Complex():
                return real
            case Int() | Float():
                return Complex(complex(real._value, 0))
            case Str():
                # `complex() arg is a malformed string` names the builtin as a
                # call; `int` and `float` were reworded to `'zz' is not a valid
                # int` and this was left on CPython's phrasing, in POOP's voice.
                try:
                    return Complex(complex(real._value))
                except ValueError:
                    raise MIRRORS["ValueError"](
                        f"{real._value!r} is not a valid complex"
                    ) from None
            case _:
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


class _ComplexRewriter(BuiltinRewriter):
    builtin = "complex"
    call_target = "_poop_complex_from"
    name_target = "_poop_complex_cls"
    literal_type = complex
    literal_target = "_poop_complex_literal"

    def visit_BinOp(self, node: ast.BinOp) -> ast.AST:
        # Fold `r ± ij` literal patterns (e.g. 1+2j, 3.0-1j) into a single Complex.
        # Python parses these as BinOp instead of a single complex Constant.
        match node:
            case ast.BinOp(
                left=ast.Constant(value=int() | float() as real),
                op=ast.Add() | ast.Sub() as op,
                right=ast.Constant(value=complex() as imag),
            ):
                sign = -1 if isinstance(op, ast.Sub) else 1
                combined = complex(real, sign * imag.imag)
                return call_at(
                    "_poop_complex_literal", [ast.Constant(value=combined)], node
                )
        return self.generic_visit(node)


class ComplexTransformer(BaseTransformer):
    rewriter = _ComplexRewriter
    BINDINGS = {
        "_poop_complex": Complex,
        "_poop_complex_cls": builtin_alias(Complex, _poop_complex_from, "complex"),
        "_poop_complex_literal": _poop_complex_literal,
        "_poop_complex_from": _poop_complex_from,
    }
