import ast

from poop.errors import ValidationError


class _Visitor(ast.NodeVisitor):
    def visit_Name(self, node: ast.Name) -> None:
        if node.id.startswith("_poop_"):
            raise ValidationError(
                f"{node.id} is forbidden — names starting with _poop_ are reserved for the runtime",
                lineno=getattr(node, "lineno", 0),
                col_offset=getattr(node, "col_offset", 0),
            )

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if node.attr.startswith("_poop_"):
            raise ValidationError(
                f".{node.attr} is forbidden — names starting with _poop_ are reserved for the runtime",
                lineno=getattr(node, "lineno", 0),
                col_offset=getattr(node, "col_offset", 0),
            )
        self.generic_visit(node)


class NoPoopPrefixValidator:
    def validate(self, tree: ast.Module) -> None:
        _Visitor().visit(tree)
