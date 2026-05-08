import ast
from collections.abc import Iterable
from typing import TYPE_CHECKING, ClassVar, cast

from poop.transformers.base import BaseTransformer
from poop.types.dict import Dict
from poop.types.list import List
from poop.types.tuple import Tuple

if TYPE_CHECKING:
    from poop.types.object import Object


def _poop_dict_from_pairs(*pairs: Object) -> Dict:
    d = Dict()
    it = iter(pairs)
    for k, v in zip(it, it):
        d._data[k] = v
    return d


def _poop_dict_from(arg: object = None) -> Dict:
    if arg is None:
        return Dict()
    if isinstance(arg, Dict):
        return arg
    if isinstance(arg, Iterable):
        d = Dict()
        for item in cast("Iterable[Object]", arg):
            if isinstance(item, (Tuple, List)):
                if len(item._items) != 2:
                    raise TypeError(
                        f"dict entry must have exactly 2 elements, got {len(item._items)}"
                    )
                d._data[item._items[0]] = item._items[1]
            else:
                raise TypeError(f"cannot use {type(item).__name__} as dict entry")
        return d
    raise TypeError(f"cannot convert {type(arg).__name__} to Dict")


class _DictRewriter(ast.NodeTransformer):
    def visit_Call(self, node: ast.Call) -> ast.AST:
        if (
            isinstance(node.func, ast.Name)
            and node.func.id == "dict"
            and not node.keywords
            and len(node.args) <= 1
        ):
            return ast.copy_location(
                ast.Call(
                    func=ast.Name(id="_poop_dict_from", ctx=ast.Load()),
                    args=[self.visit(arg) for arg in node.args],
                    keywords=[],
                ),
                node,
            )
        self.generic_visit(node)
        return node

    def visit_Dict(self, node: ast.Dict) -> ast.AST:
        self.generic_visit(node)
        # Collect non-None keys; bail out if dict has unpacking (**d)
        pairs = [(k, v) for k, v in zip(node.keys, node.values) if k is not None]
        if len(pairs) != len(node.keys):
            return node
        args: list[ast.expr] = []
        for k, v in pairs:
            args.append(k)
            args.append(v)
        return ast.copy_location(
            ast.Call(
                func=ast.Name(id="_poop_dict_from_pairs", ctx=ast.Load()),
                args=args,
                keywords=[],
            ),
            node,
        )

    def visit_Name(self, node: ast.Name) -> ast.AST:
        if node.id == "dict":
            return ast.copy_location(ast.Name(id="Dict", ctx=node.ctx), node)
        return node


class DictTransformer(BaseTransformer):
    rewriter = _DictRewriter
    BINDINGS: ClassVar[dict[str, object]] = {
        "_poop_dict_from_pairs": _poop_dict_from_pairs,
        "_poop_dict_from": _poop_dict_from,
        "Dict": Dict,
    }
