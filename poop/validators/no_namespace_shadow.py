import ast

from poop.errors import ValidationError

_NAMESPACE_MESSAGE = (
    "{name!r} is a POOP namespace binding; reassigning it shadows the "
    "runtime entry point"
)


class _Visitor(ast.NodeVisitor):
    def __init__(self, protected: frozenset[str], message: str) -> None:
        self._protected = protected
        self._message = message

    def _check(self, name: str, node: ast.AST) -> None:
        if name in self._protected:
            raise ValidationError(
                self._message.format(name=name),
                lineno=getattr(node, "lineno", 0),
                col_offset=getattr(node, "col_offset", 0),
            )

    def _visit_target(self, target: ast.AST) -> None:
        # Handles `x = ...`, `x: T = ...`, `x += ...`, and unpacking
        # forms like `x, y = ...` / `[x, y] = ...` / `(*x,) = ...`.
        if isinstance(target, ast.Name):
            self._check(target.id, target)
        elif isinstance(target, ast.Tuple | ast.List):
            for elt in target.elts:
                self._visit_target(elt)
        elif isinstance(target, ast.Starred):
            self._visit_target(target.value)

    def visit_Assign(self, node: ast.Assign) -> None:
        for target in node.targets:
            self._visit_target(target)
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        self._visit_target(node.target)
        self.generic_visit(node)

    def visit_AugAssign(self, node: ast.AugAssign) -> None:
        self._visit_target(node.target)
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._check(node.name, node)
        self.generic_visit(node)

    def _check_args(self, args: ast.arguments) -> None:
        # A parameter named after a namespace binding shadows it inside the
        # body exactly like a local assignment does, so `def m(self, math):`
        # makes `math.sqrt(...)` fail in confusing ways — the same hazard the
        # assignment check guards against.
        params = [*args.posonlyargs, *args.args, *args.kwonlyargs]
        if args.vararg is not None:
            params.append(args.vararg)
        if args.kwarg is not None:
            params.append(args.kwarg)
        for param in params:
            self._check(param.arg, param)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._check_args(node.args)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._check_args(node.args)
        self.generic_visit(node)

    def visit_Lambda(self, node: ast.Lambda) -> None:
        # Lambdas are POOP's block form and carry most user code, so the
        # same shadowing hazard the def check guards against applies here
        # too (`lambda math: math.sqrt(2)` silently shadows the namespace).
        self._check_args(node.args)
        self.generic_visit(node)


class NoNamespaceShadowValidator:
    def __init__(self) -> None:
        # Pull the set of user-facing entry points from
        # DEFAULT_NAMESPACE so the protected list stays in sync with
        # whatever the transformers register. Lazy import to avoid
        # validator → transformer eager-load at validators package
        # import time (the cycle would still close, but this keeps
        # the dependency clean).
        from poop.transformers import DEFAULT_NAMESPACE

        self._protected: frozenset[str] = frozenset(
            n for n in DEFAULT_NAMESPACE if not n.startswith("_poop_")
        )

    def validate(self, tree: ast.Module) -> None:
        _Visitor(self._protected, _NAMESPACE_MESSAGE).visit(tree)
