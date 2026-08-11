import ast
from collections.abc import Iterable
from typing import ClassVar, cast

from poop.transformers._arity import refuse_extra_arguments
from poop.transformers.base import BaseTransformer
from poop.types._alias import builtin_alias
from poop.types.bytes import Bytes
from poop.types.exceptions import MIRRORS
from poop.types.int import Int
from poop.types.string import Str


def _poop_bytes_from(*args: object, **kwargs: object) -> Bytes:
    """`bytes()`, `bytes(source)` and the encoding form `bytes(text, encoding)`.

    The text branch delegates to `Str.encode`, which is the guarded codec
    surface — it used to reach into `arg._value` and call `str.encode` itself,
    so the one argument in the language that `_codec.py` never saw was the one
    in the constructor. Every consequence of that was the module's own
    docstring read back: `bytes("ab", "rot13")` answered `'rot13' is not a text
    encoding; use codecs.encode() to handle arbitrary codecs`, sending the
    reader to a module `no_import` forbids, while `"ab".encode("rot13")` one
    receiver away answered POOP's sentence. `bytes("é", "ascii")` leaked
    CPython's `codec` report under a class no program can spell, and
    `bytes("ab", 5)` — a wrong-*typed* encoding — was silently *ignored*,
    falling back to utf-8, the shape proposal 14 closed for `encode` itself.

    The encoding is required, as CPython requires it: without one there is no
    answer to give, only a guess about what the text means as bytes.
    """
    refuse_extra_arguments(
        "bytes",
        args,
        kwargs,
        most=3,
        built_from="at most one source, plus an encoding and errors for text",
        hint='write a b"…" literal for bytes',
    )
    arg = args[0] if args else None
    codec = cast("tuple[Str, ...]", args[1:])
    if isinstance(arg, Str):
        if not codec:
            raise MIRRORS["TypeError"]("string argument without an encoding")
        return arg.encode(*codec)
    if codec:
        raise MIRRORS["TypeError"]("encoding without a string argument")
    if arg is None:
        return Bytes(b"")
    if isinstance(arg, Bytes):
        return arg
    if isinstance(arg, Int):
        return Bytes(bytes(arg._value))
    if isinstance(arg, Iterable):
        ints = cast("Iterable[Int]", arg)
        return Bytes(bytes(item._value for item in ints))
    raise MIRRORS["TypeError"](f"cannot convert {type(arg).__qualname__} to bytes")


class _BytesRewriter(ast.NodeTransformer):
    def visit_Call(self, node: ast.Call) -> ast.AST:
        if isinstance(node.func, ast.Name) and node.func.id == "bytes":
            return ast.copy_location(
                ast.Call(
                    func=ast.Name(id="_poop_bytes_from", ctx=ast.Load()),
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

    def visit_Constant(self, node: ast.Constant) -> ast.AST:
        if isinstance(node.value, bytes):
            return ast.copy_location(
                ast.Call(
                    func=ast.Name(id="_poop_bytes", ctx=ast.Load()),
                    args=[node],
                    keywords=[],
                ),
                node,
            )
        return node

    def visit_Name(self, node: ast.Name) -> ast.AST:
        if node.id == "bytes":
            return ast.copy_location(ast.Name(id="_poop_bytes_cls", ctx=node.ctx), node)
        return node


class BytesTransformer(BaseTransformer):
    rewriter = _BytesRewriter
    BINDINGS: ClassVar[dict[str, object]] = {
        "_poop_bytes": Bytes,
        "_poop_bytes_cls": builtin_alias(Bytes, _poop_bytes_from, "bytes"),
        "_poop_bytes_from": _poop_bytes_from,
    }
