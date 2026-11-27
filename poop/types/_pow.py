"""The reflected half of `pow`, shared by `Int.pow` and `Float.pow`.

`no_pow` forbids `pow(a, b)` and names `a.pow(b)`. `__pow__` answers
`NotImplemented` for a `Complex` *on purpose*, so that CPython's operator
protocol falls through to `Complex.__rpow__`. A message that turned that
`NotImplemented` into a refusal would be narrower than the operator POOP still
allows *and* than the builtin it replaces, so the message completes the
protocol here and both spellings answer the same:

    (2 ** complex(1, 1))    ->  (1.5384778027279442+1.2779225526272695j)
    (2).pow(complex(1, 1))  ->  (1.5384778027279442+1.2779225526272695j)

`doc/adr/0039-substitutes-mirror-the-full-builtin-signature-accessors-are-methods.md`.
"""

from poop.types._unwrap import _is_absent


def reflected_pow(receiver: object, other: object, modulus: object) -> object:
    """`other.__rpow__(receiver)`, or `NotImplemented` when there is no route.

    Answers whatever the operand's `__rpow__` answers — `object`, as typeshed
    types a reflected operator on an unknown operand — and so does the `pow`
    message built on it.

    `modulus` is guarded rather than forwarded: the three-argument form has no
    reflected counterpart in CPython either, so a present modulus means the
    refusal stands.
    """
    if not _is_absent(modulus):
        return NotImplemented
    reflected = getattr(other, "__rpow__", None)
    if reflected is None:
        return NotImplemented
    return reflected(receiver)
