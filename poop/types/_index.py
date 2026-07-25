"""What POOP accepts where Python accepts an index.

`bool` is an `int` subclass in CPython, so `[10, 20][True]` is `20` and
`"ab"[True]` is `"b"`. POOP's `Boolean` is not an `Int` subclass — the two
rungs of the tower are separate classes — so every message that takes an index
names both, and both answer `__index__`, which is what lets a call site hand
the wrapper straight to CPython instead of unwrapping `._value` by hand.
"""

from poop.types.boolean import Boolean
from poop.types.int import Int

type Index = Int | Boolean
