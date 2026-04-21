import ast
from typing import ClassVar

from poop.types.dict import Dict
from poop.types.object import Object


def _poop_dict_from_pairs(*pairs: Object) -> Dict:
    d = Dict()
    for i in range(0, len(pairs), 2):
        d._data[pairs[i]] = pairs[i + 1]
    return d


class DictTransformer:
    BINDINGS: ClassVar[dict[str, object]] = {
        "_poop_dict_from_pairs": _poop_dict_from_pairs
    }

    def transform(self, tree: ast.Module) -> ast.Module:
        tree = _DictRewriter().visit(tree)
        ast.fix_missing_locations(tree)
        return tree


class _DictRewriter(ast.NodeTransformer):
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
