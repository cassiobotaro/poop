import ast
from collections.abc import Iterable
from typing import ClassVar, cast

from poop.types.byte_array import ByteArray


def _poop_bytearray_from(arg: object = None) -> ByteArray:
    from poop.types.bytes import Bytes
    from poop.types.int import Int

    if arg is None:
        return ByteArray()
    if isinstance(arg, Bytes):
        return ByteArray(bytearray(arg._value))
    if isinstance(arg, Int):
        return ByteArray(bytearray(arg._value))
    if isinstance(arg, Iterable):
        from poop.types.int import Int

        ints = cast("Iterable[Int]", arg)
        return ByteArray(bytearray(item._value for item in ints))
    return ByteArray()


class ByteArrayTransformer:
    BINDINGS: ClassVar[dict[str, object]] = {
        "_poop_bytearray_from": _poop_bytearray_from
    }

    def transform(self, tree: ast.Module) -> ast.Module:
        tree = _ByteArrayRewriter().visit(tree)
        ast.fix_missing_locations(tree)
        return tree


class _ByteArrayRewriter(ast.NodeTransformer):
    def visit_Call(self, node: ast.Call) -> ast.AST:
        self.generic_visit(node)
        if (
            isinstance(node.func, ast.Name)
            and node.func.id == "bytearray"
            and not node.keywords
            and len(node.args) <= 1
        ):
            return ast.copy_location(
                ast.Call(
                    func=ast.Name(id="_poop_bytearray_from", ctx=ast.Load()),
                    args=node.args,
                    keywords=[],
                ),
                node,
            )
        return node
