import ast
from typing import Protocol


class Transformer(Protocol):
    def transform(self, tree: ast.Module) -> ast.Module: ...
