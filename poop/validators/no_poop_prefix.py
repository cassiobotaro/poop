import ast

from poop.errors import ValidationError

_PREFIX = "_poop_"


class _Visitor(ast.NodeVisitor):
    def _reject(self, name: str, node: ast.AST, *, dotted: bool = False) -> None:
        if name.startswith(_PREFIX):
            label = f".{name}" if dotted else name
            raise ValidationError(
                f"{label} is forbidden — names starting with _poop_ are reserved for the runtime",
                lineno=getattr(node, "lineno", 0),
                col_offset=getattr(node, "col_offset", 0),
            )

    def _check_args(self, args: ast.arguments) -> None:
        # Parameters bind names inside the body, so a `_poop_`-prefixed
        # parameter (def or lambda) reopens a reserved identifier exactly
        # like a reference does. A bare `lambda _poop_x: 1` never mentions
        # the name in its body, so visit_Name alone would miss it.
        params = [*args.posonlyargs, *args.args, *args.kwonlyargs]
        if args.vararg is not None:
            params.append(args.vararg)
        if args.kwarg is not None:
            params.append(args.kwarg)
        for param in params:
            self._reject(param.arg, param)

    def visit_Name(self, node: ast.Name) -> None:
        self._reject(node.id, node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        self._reject(node.attr, node, dotted=True)
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._reject(node.name, node)
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        # The function name binds a callable; a `_poop_`-prefixed method or
        # nested def would create a reserved identifier the runtime owns,
        # and its name is never a Name node, so visit_Name would miss it.
        self._reject(node.name, node)
        self._check_args(node.args)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._reject(node.name, node)
        self._check_args(node.args)
        self.generic_visit(node)

    def visit_Lambda(self, node: ast.Lambda) -> None:
        self._check_args(node.args)
        self.generic_visit(node)


class NoPoopPrefixValidator:
    def validate(self, tree: ast.Module) -> None:
        _Visitor().visit(tree)
