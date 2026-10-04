from typing import TYPE_CHECKING, cast

from poop.transformers._arity import refuse_extra_arguments
from poop.transformers.base import BaseTransformer, BuiltinRewriter, call_at
from poop.types._alias import builtin_alias
from poop.types.byte_array import ByteArray
from poop.types.bytes import Bytes
from poop.types.exceptions import MIRRORS
from poop.types.string import Str

if TYPE_CHECKING:
    import ast

# CPython's own parameter names: `str(object=b"", encoding=..., errors=...)`.
_SLOTS = ("object", "encoding", "errors")


def _poop_str_from(*args: object, **kwargs: object) -> Str:
    """`str()`, `str(x)` and the decoding form `str(bytes, encoding, errors)`.

    The two-argument form is CPython's and answers `"ab"` for
    `str(b"ab", "utf-8")`; the converter used to take one argument, so that
    call fell through to the class and reported `str.__init__() takes 2
    positional arguments but 3 were given` — a valid Python call, refused by
    a message naming a dunder the program never wrote.
    """
    refuse_extra_arguments(
        "str",
        args,
        kwargs,
        most=3,
        built_from="one value, or bytes with an encoding",
        hint="write str(b, encoding) to decode",
        # CPython names all three slots, so `str(b, encoding="utf-8")` is a
        # spelling a reader can write; the names are checked below.
        keywords=True,
    )
    # Fewer arguments than slots is the ordinary case; the guard above caps it.
    given: dict[str, object] = dict(zip(_SLOTS, args, strict=False))
    for name, value in kwargs.items():
        if name not in _SLOTS:
            raise MIRRORS["TypeError"](
                f"str takes no keyword argument {name!r} — "
                "it is built from one value, or bytes with an encoding"
            )
        if name in given:
            raise MIRRORS["TypeError"](f"str was given {name!r} twice")
        given[name] = value
    source = given.get("object")
    codec = [given[name] for name in ("encoding", "errors") if name in given]
    if codec:
        # The decoding form goes through `Bytes.decode` — the same codec table,
        # so an unknown encoding answers POOP's sentence rather than CPython's
        # advice to call a module the language cannot reach.
        if not isinstance(source, (Bytes, ByteArray)):
            raise MIRRORS["TypeError"](
                f"decoding needs bytes, got {type(source).__qualname__}"
            )
        return source.decode(*cast("tuple[Str, ...]", codec))
    if source is None:
        return Str("")
    if isinstance(source, Str):
        return source
    return Str(str(source))


class _StrRewriter(BuiltinRewriter):
    builtin = "str"
    call_target = "_poop_str_from"
    name_target = "_poop_str_cls"

    def visit_Constant(self, node: ast.Constant) -> ast.AST:
        if isinstance(node.value, str):
            return call_at("_poop_str", [node], node)
        return node


class StrTransformer(BaseTransformer):
    rewriter = _StrRewriter
    BINDINGS = {
        "_poop_str": Str,
        "_poop_str_cls": builtin_alias(Str, _poop_str_from, "str"),
        "_poop_str_from": _poop_str_from,
    }
