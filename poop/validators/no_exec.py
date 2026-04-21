import ast

from poop.errors import ValidationError

_FORBIDDEN = frozenset({"exec", "eval", "compile"})


class NoExecValidator:
    def validate(self, tree: ast.Module) -> None:
        _NoExecVisitor().visit(tree)


class _NoExecVisitor(ast.NodeVisitor):
    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name) and node.func.id in _FORBIDDEN:
            raise ValidationError(
                f"{node.func.id}() is forbidden — metaprogramming is not allowed",
                lineno=node.lineno,
                col_offset=node.col_offset,
            )
        self.generic_visit(node)
