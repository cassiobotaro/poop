"""Shared machinery for the collection transformers.

``list``/``tuple``/``set``/``frozenset``/``dict`` route ``<builtin>(x)``
and a bare ``<builtin>`` through ``BuiltinRewriter`` like every other
constructor; what is theirs is the literal — wrapping ``[a, b]`` in the POOP
constructor binding, spreads included — and the converter factories.
"""

import ast
from collections.abc import Callable, Iterable
from typing import TYPE_CHECKING, Any, cast

from poop.transformers._arity import refuse_extra_arguments
from poop.transformers.base import call_at
from poop.types._message import article
from poop.types.byte_array import ByteArray
from poop.types.bytes import Bytes
from poop.types.exceptions import MIRRORS
from poop.types.int import Int
from poop.types.range import Range
from poop.types.string import Str

if TYPE_CHECKING:
    from poop.types.object import Object


def spread(value: object, kind: str) -> object:
    """`value`, or a refusal naming the literal the reader actually wrote.

    `[*5]`, `(*5,)` and `{*5}` are literals with a spread, and all three
    answered in terms of a constructor call the program never wrote:

        [*5]     # list() argument after * must be an iterable, not int

    `list()` is a message spelt as a call, which the wording sweep bans; it
    names a construct absent from the source, since the reader wrote brackets;
    and `[*5]` is not even routed through the `list` converter, so the name was
    doubly not the one that ran.

    The block form was already right and is the target this copies: `f(*5)`
    answers `<block> argument after * must be an iterable, not int`, naming the
    receiver in POOP's own spelling.
    """
    if isinstance(value, Iterable):
        return value

    raise MIRRORS["TypeError"](
        f"a {kind} literal can only spread a collection, "
        f"got {article(type(value).__qualname__)}"
    )


def _spread_elts(elts: list[ast.expr], kind: str) -> list[ast.expr]:
    """Each starred element routed through `spread`, the rest untouched."""
    return [
        ast.copy_location(
            ast.Starred(
                value=call_at("_poop_spread", [elt.value, ast.Constant(kind)], elt),
                ctx=elt.ctx,
            ),
            elt,
        )
        if isinstance(elt, ast.Starred)
        else elt
        for elt in elts
    ]


def wrap_elts(node: ast.List | ast.Tuple | ast.Set, target: str) -> ast.Call:
    return call_at(target, _spread_elts(node.elts, _LITERAL_KIND[type(node)]), node)


# What the reader wrote, for `spread`'s sentence — never the converter's name.
_LITERAL_KIND: dict[type[ast.AST], str] = {
    ast.List: "list",
    ast.Tuple: "tuple",
    ast.Set: "set",
}


def make_constructor[T](poop_type: type[T]) -> Callable[..., T]:
    def _constructor(*elements: Object) -> T:
        return poop_type(*elements)

    return _constructor


def make_iterable_from[T](
    poop_type: type[T], *, copy: bool = False
) -> Callable[..., T]:
    def _from(*args: object, **kwargs: object) -> T:
        refuse_extra_arguments(
            poop_type.__name__,
            args,
            kwargs,
            most=1,
            built_from="at most one collection",
            hint="write a literal for elements",
        )
        arg = args[0] if args else None
        if arg is None:
            return poop_type()
        if isinstance(arg, poop_type):
            # Mutable collections must not alias their source; CPython's
            # tuple(t) / frozenset(fs) do return the same object.
            if copy:
                return poop_type(*cast("Iterable[Object]", arg))
            return arg
        if isinstance(arg, Range):
            return poop_type(*arg._iter())
        if isinstance(arg, Iterable):
            return poop_type(*cast("Iterable[Object]", arg))
        # Both names come off the cloak, never a literal: a hand-written
        # "List" would say `cannot convert int to List`, half the sentence
        # in POOP's vocabulary and half in the wrapper's.
        raise MIRRORS["TypeError"](
            f"cannot convert {type(arg).__qualname__} to {poop_type.__name__}"
        )

    return _from


def make_bytes_from[T: (Bytes, ByteArray)](
    poop_type: type[T],
    build: Callable[[Any], T],
    *,
    hint: str,
    copy: bool = False,
) -> Callable[..., T]:
    """The converter for `bytes(...)` or `bytearray(...)`: the two mirror each
    other message for message, constructor included.

    The text form delegates to `Str.encode`, the guarded codec surface. Reaching
    into `arg._value` and calling `str.encode` here was the one argument in the
    language `_codec.py` never saw: `bytes("ab", "rot13")` answered `'rot13' is
    not a text encoding; use codecs.encode() to handle arbitrary codecs`,
    sending the reader to a module `no_import` forbids; `bytes("é", "ascii")`
    leaked CPython's codec report; and `bytes("ab", 5)` was silently *ignored*,
    falling back to utf-8. The encoding is required, as CPython requires it:
    without one there is no answer, only a guess about what the text means as
    bytes. `bytearray` once took no text at all — `most=1` refused legal
    Python, and the one-argument spelling fell through to iterating the text,
    answering `'str' object cannot be interpreted as an integer`.

    `build` makes the receiver from whatever its own builtin accepts, so a byte
    out of range is refused in that builtin's words (`bytes must be in
    range(0, 256)` against `byte must be ...`). `copy` is
    `make_iterable_from`'s: `bytes(b)` answers `b` itself, as CPython's does,
    and `bytearray(b)` a copy that does not alias it.
    """
    name = poop_type.__name__

    def _from(*args: object, **kwargs: object) -> T:
        refuse_extra_arguments(
            name,
            args,
            kwargs,
            most=3,
            built_from="at most one source, plus an encoding and errors for text",
            hint=hint,
        )
        arg = args[0] if args else None
        codec = cast("tuple[Str, ...]", args[1:])
        if isinstance(arg, Str):
            if not codec:
                raise MIRRORS["TypeError"]("string argument without an encoding")
            return build(arg.encode(*codec)._value)
        if codec:
            raise MIRRORS["TypeError"]("encoding without a string argument")
        if arg is None:
            return build(b"")
        if not copy and isinstance(arg, poop_type):
            return arg
        if isinstance(arg, Bytes | Int):
            return build(arg._value)
        if isinstance(arg, Iterable):
            return build(item._value for item in cast("Iterable[Int]", arg))
        raise MIRRORS["TypeError"](f"cannot convert {type(arg).__qualname__} to {name}")

    return _from
