import ast
from typing import ClassVar, Protocol


class Transformer(Protocol):
    def transform(self, tree: ast.Module) -> ast.Module: ...


class BaseTransformer:
    """Base class for AST transformers.

    Subclasses should define:
    - rewriter: the NodeTransformer class to use
    - BINDINGS: dict of names to inject into the namespace (optional)
    """

    rewriter: type[ast.NodeTransformer]
    BINDINGS: ClassVar[dict[str, object]] = {}

    def transform(self, tree: ast.Module) -> ast.Module:
        tree = self.rewriter().visit(tree)
        ast.fix_missing_locations(tree)
        return tree
