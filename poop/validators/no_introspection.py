import ast

from poop.errors import ValidationError

_FORBIDDEN = frozenset({"globals", "locals", "vars", "dir"})


class NoIntrospectionValidator:
    def validate(self, tree: ast.Module) -> None:
        _NoIntrospectionVisitor().visit(tree)


class _NoIntrospectionVisitor(ast.NodeVisitor):
    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name) and node.func.id in _FORBIDDEN:
            raise ValidationError(
                f"{node.func.id}() is forbidden — state lives in instances, not in scope introspection",
                lineno=node.lineno,
                col_offset=node.col_offset,
            )
        self.generic_visit(node)
