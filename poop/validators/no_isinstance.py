import ast

from poop.errors import ValidationError


class NoIsinstanceValidator:
    def validate(self, tree: ast.Module) -> None:
        _NoIsinstanceVisitor().visit(tree)


class _NoIsinstanceVisitor(ast.NodeVisitor):
    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name) and node.func.id == "isinstance":
            raise ValidationError(
                "isinstance() is forbidden — use obj.is_instance(Type) instead",
                lineno=node.lineno,
                col_offset=node.col_offset,
            )
        self.generic_visit(node)
