import ast
from typing import Protocol


class Validator(Protocol):
    def validate(self, tree: ast.Module) -> None: ...
