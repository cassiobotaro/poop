"""Shared machinery for the collection transformers.

``list``/``tuple``/``set``/``frozenset``/``dict`` route ``<builtin>(x)``
and a bare ``<builtin>`` through ``BuiltinRewriter`` like every other
constructor; what is theirs is the literal — wrapping ``[a, b]`` in the POOP
constructor binding, spreads included — and the converter factories.
"""

import ast
from collections.abc import Callable, Iterable
from typing import TYPE_CHECKING, ClassVar, cast

from poop.transformers._arity import refuse_extra_arguments
from poop.transformers.base import BuiltinRewriter, call_at
from poop.types import mirrors
from poop.types._message import article
from poop.types.byte_array import ByteArray
from poop.types.bytes import Bytes
from poop.types.int import Int
from poop.types.string import Str

if TYPE_CHECKING:
    from poop.types.object import Object


def spread(value: object, kind: str) -> object:
    """`value`, or a refusal naming the literal the reader actually wrote.

    `[*5]`, `(*5,)` and `{*5}` are literals with a spread. CPython's own
    refusal, `list() argument after * must be an iterable, not int`, names
    `list()`: a message spelt as a call, which the wording sweep bans, and a
    construct absent from the source, since the reader wrote brackets — and
    `[*5]` is not even routed through the `list` converter.

    The block form is the model: `f(*5)` answers `<block> argument after *
    must be an iterable, not int`, naming the receiver in POOP's own spelling.
    """
    if isinstance(value, Iterable):
        return value

    raise mirrors.TypeError(
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


class LiteralRewriter(BuiltinRewriter):
    """A `BuiltinRewriter` that also owns a bracketed literal.

    `[a, b]`, `(a, b)` and `{a, b}` each become a call of the POOP class
    with the elements as arguments, spreads routed through `spread` under the
    literal's own name — the one sentence `[*5]` must answer with, since the
    reader wrote brackets and never a constructor.

    Only a `Load` literal is wrapped: `[a, b] = pair` is an unpacking target,
    which `UnpackTransformer` owns. A set literal has no context at all and is
    always a value.
    """

    literal_node: ClassVar[type[ast.List | ast.Tuple | ast.Set]]
    literal_target: ClassVar[str]

    def visit(self, node: ast.AST) -> ast.AST:
        if type(node) is not self.literal_node:
            return super().visit(node)
        self.generic_visit(node)
        literal = cast("ast.List | ast.Tuple | ast.Set", node)
        if not isinstance(getattr(literal, "ctx", ast.Load()), ast.Load):
            return literal
        return call_at(
            self.literal_target, _spread_elts(literal.elts, self.builtin), literal
        )


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
        if isinstance(arg, Iterable):
            return poop_type(*cast("Iterable[Object]", arg))
        # Both names come off the cloak, never a literal: a hand-written
        # "List" would say `cannot convert int to List`, half the sentence
        # in POOP's vocabulary and half in the wrapper's.
        raise mirrors.TypeError(
            f"cannot convert {type(arg).__qualname__} to {poop_type.__name__}"
        )

    return _from


def make_bytes_from[T: (Bytes, ByteArray)](
    poop_type: type[T],
    build: Callable[[bytes | bytearray | Iterable[int] | int], T],
    *,
    hint: str,
    copy: bool = False,
) -> Callable[..., T]:
    """The converter for `bytes(...)` or `bytearray(...)`: the two mirror each
    other message for message, constructor included.

    The text form delegates to `Str.encode`, the guarded codec surface, so the
    encoding and the error handler pass the checks `_codec.py` makes on any
    text; calling `str.encode` on `arg._value` here would go around them
    (`doc/adr/0046-text-codecs-are-limited-to-four-encodings-constructors-included.md`).
    The encoding is required, as CPython requires it: without one there is no
    answer, only a guess about what the text means as bytes. `bytearray` takes
    the same text form as `bytes`.

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
                raise mirrors.TypeError("string argument without an encoding")
            return build(arg.encode(*codec)._value)
        if codec:
            raise mirrors.TypeError("encoding without a string argument")
        if arg is None:
            return build(b"")
        if not copy and isinstance(arg, poop_type):
            return arg
        if isinstance(arg, (Bytes, Int)):
            return build(arg._value)
        if isinstance(arg, Iterable):
            return build(item._value for item in cast("Iterable[Int]", arg))
        raise mirrors.TypeError(f"cannot convert {type(arg).__qualname__} to {name}")

    return _from
