# 50. `MemoryView` is a one-dimensional byte view that answers `index` and `count`

Date: 2026-08-09

## Status

Accepted

## Context

`memoryview(...)` is rewritten to `_poop_memoryview_from(x)` and answers a `MemoryView` (`poop/types/memory_view.py`).

Its `__str__` was `repr(self._value)`, so `memoryview(b"ab").print()` answered `<memory at 0x70cb7ab59240>`. That is the raw pointer `Object.__hash__` refuses to answer, under the class name `memory`, which is neither the POOP name nor the cloak. It is unstable across runs, so no test could pin it and no example could show it. Printing the bytes themselves would re-materialize an arbitrarily large buffer just to print it, the cost a `Range` refuses when sliced.

The `no_subscript` and `no_in` bans point at `slice(...)` and `includes(x)`; `mv[0:2]` is a `memoryview` in CPython and `98 in memoryview(b"ab")` is `True`. Every other sequence in the family answers `index` and `count`, and `MemoryView` was the one receiver where a program could learn through `includes` that an element is there and then could not ask where. CPython's own miss, `memoryview.index(x): x not found`, is written as a call with a placeholder where the value belongs.

A diff of CPython's public names against `MemoryView` lists `shape`, `strides`, `suboffsets`, `itemsize`, `format`, `ndim`, `nbytes`, `c_contiguous`, `f_contiguous`, `contiguous`, `cast`, `toreadonly`, `release`, `obj`, `tolist` and `readonly` as missing. Most of them describe a buffer. POOP has only one-dimensional byte views (no `struct`, no `array`, no NumPy), so `shape` would answer `(n,)`, `strides` `(1,)`, `itemsize` `1`, `format` `'B'` and `ndim` `1` for every view a program can build, and `cast` would have nothing to cast to. `format` is already a message every value answers with another meaning (`Object.format`, the spec formatter), and `obj` would hand the underlying object back around the view.

## Decision

`MemoryView` is a one-dimensional view of bytes, and answers the sequence messages, not the buffer protocol.

- It prints what it is, not where it lives: `<memoryview of 2 bytes>`.
- Its contents are shown on request, by `hex()`, `tobytes()` and `tolist()`. `tolist()` answers the `List` of `Int` the iterable protocol already walks.
- It answers `slice(...)`, `includes(x)`, `index(x)` and `count(x)`. `count` takes one argument, as CPython's does, unlike the text wrappers' bounded twins. `index` reports a miss through `_at.no_element_equal_to`, in the family's words.
- `readonly()` is `true` for `memoryview(b"ab")` and `false` for `memoryview(bytearray(b"ab"))`, and a slice answers what the view it came from answers. It is a message, not the attribute CPython has, by the rule that made `real`, `imag`, `numerator` and `Range.start` methods.
- The buffer-layout names stay out: `shape`, `strides`, `suboffsets`, `itemsize`, `format` (as an attribute), `ndim`, `nbytes`, `c_contiguous`, `f_contiguous`, `contiguous`, `cast`, `toreadonly`, `release` and `obj`.

## Consequences

A view prints the same on every run, so tests and examples can show it.

The bans' substitutes all work on a view, and a program that finds an element can ask where it is.

POOP has no vocabulary for memory layout, so a program cannot reshape, cast or release a view. The bare `memoryview(b"ab").readonly` is the block, as every uncalled message is, and prints `<block>`.
