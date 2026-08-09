"""The reflected half of `pow`, shared by `Int.pow` and `Float.pow`.

`no_pow` forbids `pow(a, b)` and names `a.pow(b)`. Both wrappers called their
own `__pow__` and turned a `NotImplemented` into a refusal — but `__pow__`
answers `NotImplemented` for a `Complex` *on purpose*, so that CPython's
operator protocol falls through to `Complex.__rpow__`. The operator did
exactly that; the message never got there:

    (2 ** complex(1, 1))    ->  (1.5384778027279442+1.2779225526272695j)
    (2).pow(complex(1, 1))  ->  TypeError: int does not understand #** …

So the substitute was narrower than the operator POOP still allows *and* than
the builtin it replaces — CPython computes `pow(2, 1+1j)` too. Completing the
protocol here is what makes the deliberate `NotImplemented` mean what it says.
"""

from typing import Any


def reflected_pow(receiver: Any, other: Any, modulus: Any) -> Any:
    """`other.__rpow__(receiver)`, or `NotImplemented` when there is no route.

    `modulus` is guarded rather than forwarded: the three-argument form has no
    reflected counterpart in CPython either, so a present modulus means the
    refusal stands.
    """
    from poop.types._unwrap import _is_absent

    if not _is_absent(modulus):
        return NotImplemented
    reflected = getattr(other, "__rpow__", None)
    if reflected is None:
        return NotImplemented
    return reflected(receiver)
