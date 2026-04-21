import ast

from poop.errors import ValidationError

_FORBIDDEN = frozenset({"setattr", "delattr"})


class NoSetattrValidator:
    def validate(self, tree: ast.Module) -> None:
        _NoSetattrVisitor().visit(tree)


class _NoSetattrVisitor(ast.NodeVisitor):
    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name) and node.func.id in _FORBIDDEN:
            raise ValidationError(
                f"{node.func.id}() is forbidden — use class methods to manage state instead",
                lineno=node.lineno,
                col_offset=node.col_offset,
            )
        self.generic_visit(node)
