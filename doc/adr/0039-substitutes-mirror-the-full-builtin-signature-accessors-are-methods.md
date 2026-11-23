# 39. Substitutes mirror the full builtin signature; accessors are methods

Date: 2026-07-17

## Status

Accepted

## Context

Every banned builtin or operator has a message as its substitute, and a substitute narrower than what it replaces leaves a program with nothing to write. Several were narrower, or read their arguments differently from CPython:

- `List.index` and `Tuple.index` branched on which bound was present, and the first branch dropped `stop`, so `[1, 2, 3].index(3, stop=1)` answered `2` where CPython raises. The same branch read an explicit `none` stop as stop at 0, which makes every search fail.
- The variadic `min`/`max` took operands only, so `(5).max(3, block)` compared the block as a value instead of applying it; any comparable third argument would have answered a plausible wrong number in silence. On the collection rungs `xs.min(0)` handed `0` to the key slot: `[1, 2].min(0)` answered `'int' object is not callable` and `[[3], [1]].min([9])` answered a plausible wrong list without raising. `sorted` had the same shape, where `xs.sorted(f)` and `xs.sorted(reverse_flag)` read the same to the receiver.
- `print` took `end`, `sep` and `flush` positionally, so `(5).print("x")` printed `5x`, the argument silently read as the terminator.
- `Int.pow` and `Float.pow` called their own `__pow__` and turned a `NotImplemented` into a refusal, but `__pow__` answers `NotImplemented` for a `Complex` on purpose so that CPython falls through to `Complex.__rpow__`. `2 ** complex(1, 1)` worked while `(2).pow(complex(1, 1))` refused.
- `at` / `slice` / `insert` / `pop` / `Slice.indices` read `index._value`, which leaked (`[1, 2].at([0])` answered `list does not understand #_value`) and refused a Boolean index, though `[10, 20][True]` is 20 in CPython. `(2).pow(3, True)` was refused while CPython's `pow(2, 3, True)` is `0`.
- `Set` is unhashable, so `s.includes({1})`, `s.discard({1})` and `s.remove({1})` all answered `cannot use 'set' as a set element (unhashable type: 'set')`, a refusal about storing given to three messages that only look. CPython probes with a temporary `frozenset`.
- `real`, `imag`, `numerator`, `denominator` and `Range`'s `start` / `stop` / `step` were `@property` getters. That made the operation an attribute access, and the message spelling failed with `'int' object is not callable`. Their neighbours in the same files (`Int.conjugate()`, `Float.is_integer()`, `Slice.start()`) were already methods.

## Decision

Every builtin-substitute method mirrors the full Python signature of the method it replaces, accepts what CPython accepts, and is a message rather than an attribute.

- Same optional and variadic arguments, and their combinations: `n.to_bytes()` and `xs.index(x, start, stop)` work as in CPython. An optional argument accepts the POOP wrapper or `none`, both falling back to the builtin's default. `List.index` and `Tuple.index` pass the bounds straight through, defaulting a missing `stop` to `len`, because `list.index` takes no `None` bound.
- Keyword-only where CPython is: `key` and `default` on `min`/`max` on every rung (the shared body lives in `poop/types/_minmax.py`), `key` and `reverse` on `sorted` and `sort`, `end`, `sep` and `flush` on `print`, `signed` on `to_bytes` / `from_bytes`. An absent `key` is tested with `_is_absent`, so `key=None` answers rather than refuses. `default` stays refused on the scalar `min`/`max`, as CPython refuses it. A positional argument to `print` is a wrong-arity call (`object.print() takes 1 positional argument but 2 were given`); printing the extra positionals, as CPython's `print(*objects)` does, was declined because the receiver is the object being printed.
- The message completes the operator's protocol: `poop/types/_pow.py` tries the reflected half before refusing, and the modulus form does not reflect, because CPython's three-argument `pow` has none. `Complex.pow` exists. `Int.divmod` does not reflect, because CPython refuses `divmod(2, 1+1j)` too.
- An index is read through `__index__`, which `Int` and `Boolean` answer; `Index` (`poop/types/_index.py`) is the alias every such signature names. `pow`'s modulus is read through `operator.index`.
- `_set_algebra.probed` answers a mutable `set` operand of the reading messages (`includes`, `discard`, `remove` on `Set`, and the two on `FrozenSet`) with an equivalent `FrozenSet`; `s.add({1})` stays refused. The set methods take any iterable while the operators keep CPython's restriction (ADR 42).
- Python's numeric accessors are methods: `(5).numerator()`, `range(1, 5).start()`. `MemoryView.readonly()` is a message where CPython has an attribute, so the bare `memoryview(b"ab").readonly` is a block, as every uncalled message is.

## Consequences

- A program can pass a substitute every argument CPython's builtin takes, in the positions CPython takes it, and a block is never read as an operand.
- `@property` remains allowed in user code as a class-definition decorator; it may not define what an operation on a wrapper is. `tests/test_cloak.py` sweeps every wrapper for a public `property`.
- `MemoryView` leaves out the buffer-protocol attributes that would answer a constant for every view a program can build (`shape`, `strides`, `itemsize`, `ndim`, `cast` and the rest). `tolist` and `readonly`, the two with content, are answered.
- A set really held inside a set is found by a reading message rather than blanket-refused.
