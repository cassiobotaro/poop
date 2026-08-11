import ast
from typing import ClassVar

from poop.transformers._arity import refuse_extra_arguments
from poop.transformers.base import BaseTransformer
from poop.types._alias import builtin_alias
from poop.types.boolean import Boolean, false, to_boolean, true


def _poop_bool_from(*args: object, **kwargs: object) -> Boolean:
    refuse_extra_arguments(
        "bool",
        args,
        kwargs,
        most=1,
        built_from="at most one value to test",
        hint="write True or False for a literal",
    )
    value = args[0] if args else None
    if isinstance(value, Boolean):
        return value
    return to_boolean(bool(value))


class _BooleanRewriter(ast.NodeTransformer):
    def visit_Call(self, node: ast.Call) -> ast.AST:
        # `not node.keywords`, as every other constructor rewriter guards:
        # the helper's argument is optional, so a rewritten `bool(x=1)` fell
        # through to the default and answered `False` where CPython raises
        # `bool() takes no keyword arguments`. Declining to rewrite leaves
        # `visit_Name` to resolve the callee to the class, which refuses the
        # keyword the way `str(x=1)` and `list(x=1)` already do.
        if (
            isinstance(node.func, ast.Name)
            and node.func.id == "bool"
            and not node.keywords
        ):
            return ast.copy_location(
                ast.Call(
                    func=ast.Name(id="_poop_bool_from", ctx=ast.Load()),
                    args=[self.visit(arg) for arg in node.args],
                    keywords=[],
                ),
                node,
            )
        self.generic_visit(node)
        return node

    def visit_Constant(self, node: ast.Constant) -> ast.AST:
        if node.value is True:
            return ast.copy_location(ast.Name(id="_poop_true", ctx=ast.Load()), node)
        if node.value is False:
            return ast.copy_location(ast.Name(id="_poop_false", ctx=ast.Load()), node)
        return node

    def visit_Name(self, node: ast.Name) -> ast.AST:
        if node.id == "bool":
            return ast.copy_location(ast.Name(id="_poop_bool_cls", ctx=node.ctx), node)
        return node


class BooleanTransformer(BaseTransformer):
    rewriter = _BooleanRewriter
    BINDINGS: ClassVar[dict[str, object]] = {
        "_poop_true": true,
        "_poop_false": false,
        "_poop_bool_from": _poop_bool_from,
        "_poop_boolean": Boolean,
        "_poop_bool_cls": builtin_alias(Boolean, _poop_bool_from, "bool"),
    }
