import ast

from poop.transformers._arity import refuse_extra_arguments
from poop.transformers.base import BaseTransformer, BuiltinRewriter, name_at
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


class _BooleanRewriter(BuiltinRewriter):
    builtin = "bool"
    call_target = "_poop_bool_from"
    name_target = "_poop_bool_cls"

    def visit_Constant(self, node: ast.Constant) -> ast.AST:
        if node.value is True:
            return name_at("_poop_true", node)
        if node.value is False:
            return name_at("_poop_false", node)
        return node


class BooleanTransformer(BaseTransformer):
    rewriter = _BooleanRewriter
    BINDINGS = {
        "_poop_true": true,
        "_poop_false": false,
        "_poop_bool_from": _poop_bool_from,
        "_poop_boolean": Boolean,
        "_poop_bool_cls": builtin_alias(Boolean, _poop_bool_from, "bool"),
    }
