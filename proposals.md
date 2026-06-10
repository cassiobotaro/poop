# Proposals

### 104. `**` with a negative base and fractional exponent corrupts `Int`/`Float`

- **Where:** `poop/types/int.py:141` (`Int.__pow__`), `poop/types/float.py:99` (`Float.__pow__`)
- **Bug:** When `base ** exponent` mathematically yields a complex number
  (negative base raised to a fractional power), CPython returns a `complex`.
  POOP stores that raw `complex` inside an `Int` or `Float` wrapper, so the
  object lies about its own type and every later numeric operation breaks.
  `Int.__pow__` only checks `isinstance(result, float)`; a `complex` result
  falls through to `Int(result)`. `Float.__pow__` wraps unconditionally.
- **Repro:**
  ```python
  c = (-8) ** 0.5
  c.class_name().print()   # observed: int   | expected: complex
  (c < 5).print()          # observed: crash "'<' not supported between
                           #           instances of 'complex' and 'int'"
  ```
  Plain Python: `(-8) ** 0.5` is `(1.7e-16+2.83j)`, type `complex`.
  The `Float` path is just as wrong: `(-1.0) ** 0.5` reports `float` while
  holding `(6.1e-17+1j)`.
- **Proposed fix:** detect a `complex` result and return a POOP `Complex`:
  ```python
  # Int.__pow__, _is_absent(modulus) branch
  result = self._value**other._value
  if isinstance(result, complex):
      from poop.types.complex import Complex
      return Complex(result)
  if isinstance(result, float):
      return Float(result)
  return Int(result)
  ```
  Apply the same guard in `Float.__pow__`.

### 105. `dict(d)` returns the same object instead of a copy

- **Where:** `poop/transformers/dict.py:24` (`_poop_dict_from`)
- **Bug:** `_poop_dict_from` does `if isinstance(arg, Dict): return arg`, so
  `dict(d)` hands back the very same `Dict`. In CPython `dict(d)` is a shallow
  copy; mutating the result must not touch the source.
- **Repro:**
  ```python
  d = {"a": 1}
  e = dict(d)
  e.at_put("b", 2)
  d.print()              # observed: {'a': 1, 'b': 2}   | expected: {'a': 1}
  (d.is_identical(e)).print()  # observed: True         | expected: False
  ```
  Plain Python: `d` stays `{'a': 1}`, `d is e` is `False`.
- **Proposed fix:** return a copy: `if isinstance(arg, Dict): return arg.copy()`.

### 106. `list(x)` and `set(x)` return the same object instead of a copy

- **Where:** `poop/transformers/_collection.py` (`make_iterable_from`, the
  `if isinstance(arg, poop_type): return arg` branch)
- **Bug:** The shared collection converter returns the argument unchanged when
  it is already the target type. For the mutable collections `list` and `set`
  this means `list(a)` / `set(a)` alias the source, so appending/adding to the
  "copy" mutates the original. CPython always builds a fresh container.
- **Repro:**
  ```python
  a = [1, 2]
  b = list(a)
  b.append(3)
  a.print()                    # observed: 1 2 3   | expected: 1 2
  (a.is_identical(b)).print()  # observed: True    | expected: False
  ```
  (`set(s)` behaves identically — `b.add(...)` leaks back into `a`.)
  `tuple`/`frozenset` are immutable, so passing them through is harmless.
- **Proposed fix:** rebuild instead of aliasing:
  `if isinstance(arg, poop_type): return poop_type(*arg)`.

### 107. `bytearray(x)` silently returns empty for unsupported argument types

- **Where:** `poop/transformers/byte_array.py` (`_poop_bytearray_from`)
- **Bug:** The converter's fall-through `return ByteArray()` swallows any
  argument that is not `Bytes`/`Int`/`Iterable` (e.g. a `Float`), producing an
  empty bytearray instead of raising. CPython raises `TypeError`.
- **Repro:**
  ```python
  a = bytearray(1.5)
  a.len().print()   # observed: 0 (silent empty)   | expected: TypeError
  ```
  Plain Python: `bytearray(1.5)` → `TypeError: cannot convert 'float' object
  to bytearray`.
- **Proposed fix:** replace the final `return ByteArray()` with
  `raise TypeError(f"cannot convert {type(arg).__qualname__} to ByteArray")`.

### 108. `memoryview(x)` silently returns empty for unsupported argument types

- **Where:** `poop/transformers/memory_view.py` (`_poop_memoryview_from`)
- **Bug:** The converter returns `MemoryView(memoryview(b""))` for anything
  that is not `Bytes`/`ByteArray` (e.g. an `Int`, `Str`, or `List`), inventing
  an empty view instead of raising. CPython raises `TypeError`.
- **Repro:**
  ```python
  m = memoryview(5)
  m.class_name().print()   # observed: memoryview (over b"")   | expected: TypeError
  ```
  Plain Python: `memoryview(5)` → `TypeError: memoryview: a bytes-like object
  is required, not 'int'`.
- **Proposed fix:** drop the silent fallback and raise:
  `raise TypeError(f"memoryview: a bytes-like object is required, not {type(arg).__qualname__}")`.

### 109. Negative imaginary literal `-2j` crashes

- **Where:** `poop/types/complex.py` (no `__neg__`); interacts with
  `poop/validators/no_unary_minus.py` and `poop/transformers/complex.py`
- **Bug:** `no_unary_minus` allows unary minus on numeric literals, complex
  included, and the complex transformer wraps `2j` into a POOP `Complex`. But
  `Complex` defines `negated()` and no `__neg__`, so the surviving `USub`
  applies Python unary minus to a `Complex` and raises `TypeError`. Unlike the
  `int`/`float` rewriters (which collapse `-5` / `-1.5` into a single negative
  constant), the complex rewriter has no unary-minus folding, leaving a runtime
  negation that has no operator wired.
- **Repro:**
  ```python
  x = -2j
  x.print()   # observed: crash "bad operand type for unary -: 'complex'"
              # expected: (-0-2j)
  ```
  Plain Python: `-2j` → `(-0-2j)`.
- **Proposed fix:** add the operator hook to `Complex`:
  ```python
  def __neg__(self) -> Complex:
      return self.negated()
  ```
  (Optionally fold `-<complex literal>` in `_ComplexRewriter.visit_UnaryOp`
  for parity with the int/float rewriters.)
