import ast

from poop.errors import ValidationError


class NoComprehensionValidator:
    def validate(self, tree: ast.Module) -> None:
        _NoComprehensionVisitor().visit(tree)


class _NoComprehensionVisitor(ast.NodeVisitor):
    def visit_ListComp(self, node: ast.ListComp) -> None:
        raise ValidationError(
            "list comprehension is forbidden — use col.map(block) or col.filter(block) instead",
            lineno=node.lineno,
            col_offset=node.col_offset,
        )

    def visit_SetComp(self, node: ast.SetComp) -> None:
        raise ValidationError(
            "set comprehension is forbidden — use col.map(block) or col.filter(block) instead",
            lineno=node.lineno,
            col_offset=node.col_offset,
        )

    def visit_DictComp(self, node: ast.DictComp) -> None:
        raise ValidationError(
            "dict comprehension is forbidden — use col.map(block) or col.filter(block) instead",
            lineno=node.lineno,
            col_offset=node.col_offset,
        )

    def visit_GeneratorExp(self, node: ast.GeneratorExp) -> None:
        raise ValidationError(
            "generator expression is forbidden — use col.map(block) or col.filter(block) instead",
            lineno=node.lineno,
            col_offset=node.col_offset,
        )
