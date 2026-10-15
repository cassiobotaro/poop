import ast

from poop.transformers._collection import LiteralRewriter, make_iterable_from
from poop.transformers.base import BaseTransformer
from poop.types._alias import builtin_alias
from poop.types.list import List

_poop_list_from = make_iterable_from(List, copy=True)


class _ListRewriter(LiteralRewriter):
    builtin = "list"
    call_target = "_poop_list_from"
    name_target = "_poop_list_cls"
    literal_node = ast.List
    literal_target = "_poop_list"


class ListTransformer(BaseTransformer):
    rewriter = _ListRewriter
    BINDINGS = {
        # The class itself: its `__init__` is variadic, which is the shape a
        # literal's elements arrive in.
        "_poop_list": List,
        "_poop_list_from": _poop_list_from,
        "_poop_list_cls": builtin_alias(List, _poop_list_from, "list"),
    }
