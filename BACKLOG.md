# POOP Backlog

Pending work, open questions, and known inconsistencies. See `INFECTIONS.md` for what is already implemented.

## Validators — awaiting substitute

These validators are not yet active because the POOP substitute does not exist yet.

| Construct | Validator | Pending substitute |
|---|---|---|
| `raise` | `no_raise.py` | `Error` with `.signal()` |
| `with` / `async with` | `no_with.py` | `on_do` mechanism |
| `assert` | `no_assert.py` | `assert_:` in test framework |

## Next types

- **[HIGH PRIORITY] `Error`**: base class for POOP exceptions. **Critical dependency**: unblocks `no_raise`, `no_with` and `no_assert` — while `Error` does not exist, POOP code can freely use `raise` and `with`, without protection from the principles. Design decisions still open — see Open decisions section.

## Missing validators

- **`no_slice`**: slicing `obj[1:3]` looks like an operator but has no defined substitute yet — candidate: `obj.from_to(start, stop)`. Activate after deciding the name and implementing the method.
- **`slice` as a Python class**: `slice(1, 3, 2)` creates an object with `.start`, `.stop`, `.step`. Decide whether POOP should have its own `Slice` type, or if slicing should simply be banned without an object substitute.
- **[MEDIUM PRIORITY] `no_augmented_assign`**: `x += 1`, `x -= 1` etc. are not blocked — `ast.AugAssign`. Very frequent construct; the absence of blocking creates an implicit exception to the message model.
- **`no_import`**: `import os` inside POOP code is not blocked — decide whether to ban or restrict.
## Missing methods in existing types

- **[MEDIUM PRIORITY] Python API parity audit**: review every POOP type against its Python counterpart and add any missing methods. Each POOP type should expose all meaningful methods of the Python class it wraps, following the naming rule (Python names, not Smalltalk). Types to audit: `Int` (`int`), `Float` (`float`), `Str` (`str`), `List` (`list`), `Tuple` (`tuple`), `Dict` (`dict`), `Set` (`set`), `FrozenSet` (`frozenset`), `Bytes` (`bytes`), `ByteArray` (`bytearray`), `Complex` (`complex`), `Interval` (`range`).
  - **`Int`**: `as_integer_ratio()` → `Tuple(Int, Int)`, `conjugate()` → self, `denominator()` → `Int(1)`, `imag()` → `Int(0)`, `numerator()` → self, `real()` → self, `to_bytes(length, byteorder)` → `Bytes`.
  - **`Float`**: `conjugate()` → self, `hex()` → `Str`, `imag()` → `Float(0.0)`, `real()` → self.
  - **`Str`**: `casefold()`, `center(width)`, `encode(encoding)` → `Bytes`, `expandtabs()`, `isascii()`, `isdecimal()`, `isidentifier()`, `isnumeric()`, `isprintable()`, `istitle()`, `ljust(width)`, `partition(sep)` → `Tuple`, `removeprefix(prefix)`, `removesuffix(suffix)`, `rfind(sub)`, `rindex(sub)`, `rjust(width)`, `rpartition(sep)` → `Tuple`, `rsplit(sep)`, `splitlines()`, `zfill(width)`.
  - **`List`**: `clear()`, `copy()` → `List`, `count(obj)` → `Int`, `extend(other)`, `index(obj)` → `Int`, `insert(i, obj)`, `remove(obj)`, `reverse()`, `sort(key, reverse)`.
  - **`Tuple`**: `count(obj)` → `Int`, `index(obj)` → `Int`.
  - **`Dict`**: `clear()`, `copy()` → `Dict`, `items()` → `List` of `Tuple(key, val)`, `pop(key)`, `popitem()` → `Tuple`, `setdefault(key, default)`, `update(other)`.
  - **`Set`**: `clear()`, `copy()` → `Set`, `difference(*others)`, `difference_update(*others)`, `discard(obj)`, `intersection(*others)`, `intersection_update(*others)`, `isdisjoint(other)` → `Boolean`, `issubset(other)` → `Boolean`, `issuperset(other)` → `Boolean`, `pop()`, `symmetric_difference(other)`, `symmetric_difference_update(other)`, `union(*others)`, `update(*others)`.
  - **`FrozenSet`**: `copy()` → `FrozenSet`, `difference(*others)`, `intersection(*others)`, `isdisjoint(other)` → `Boolean`, `issubset(other)` → `Boolean`, `issuperset(other)` → `Boolean`, `symmetric_difference(other)`, `union(*others)`.
  - **`Bytes`**: `capitalize()`, `center(width)`, `count(sub)`, `endswith(suffix)`, `expandtabs()`, `find(sub)`, `index(sub)`, `isalnum()`, `isalpha()`, `isascii()`, `isdigit()`, `islower()`, `isspace()`, `istitle()`, `isupper()`, `join(iterable)`, `ljust(width)`, `lower()`, `lstrip()`, `partition(sep)`, `removeprefix(prefix)`, `removesuffix(suffix)`, `replace(old, new)`, `rfind(sub)`, `rindex(sub)`, `rjust(width)`, `rpartition(sep)`, `rsplit(sep)`, `rstrip()`, `split(sep)`, `splitlines()`, `startswith(prefix)`, `strip()`, `swapcase()`, `title()`, `upper()`, `zfill(width)`.
  - **`ByteArray`**: everything above from `Bytes`, plus: `append(byte)`, `clear()`, `copy()` → `ByteArray`, `extend(iterable)`, `insert(i, byte)`, `pop(index)`, `remove(byte)`, `resize(size)`, `reverse()`.
  - **`Interval`**: `count(value)` → `Int`, `index(value)` → `Int`, `start()` → `Int`, `stop()` → `Int`, `step()` → `Int`.
- **`List.sorted()` / `List.reversed()`**: return a new sorted/reversed copy. `Interval` has `reversed()`; `List` and `Tuple` do not.
- **`Tuple.sorted()` / `Tuple.reversed()`**: same.

## Python builtins — remaining decisions

| Builtin | Note |
|---|---|
| `sorted(x)` | `x.sorted()` pending in `List` / `Tuple` |
| `sum` | use `reduce(0, block)` — ban when transformer exists |
| `super` | needed for inheritance — allow |
| `property` / `classmethod` / `staticmethod` | class definition — allow |
| `getattr` | used internally by `responds_to` — allow |
| `issubclass` | evaluate alongside `isinstance` |
| `repr` | delegates to `__repr__` → `__str__` — allow |
| `ascii` | Python-specific — decide |

## Architecture / DX

- **REPL**: interactive loop — `poop` with no arguments opens the REPL.
- **Richer error messages**: `ValidationError` could suggest the POOP equivalent (e.g., `"use x.not_() instead of 'not x'"`).

## Code examples

- Expand `examples/` with collections: `List`, `Tuple`, `Interval` with `map`/`filter`/`filter_false`.

## Open decisions

- **Exception system design**: POOP blocks `raise`/`try` but the `Error` type and its interaction with Python's existing exception hierarchy is unresolved. Three strategies were considered:
  - **A — Generic wrapper**: `on_error` wraps any caught exception in a single `Error(e)` POOP object. Simple, but loses hierarchy — cannot distinguish `ValueError` from `KeyError` in the handler.
  - **B — Mirrored POOP hierarchy**: POOP defines its own `ValueError`, `KeyError`, `TypeError` etc., each inheriting from both `Error` (POOP) and the corresponding Python exception. Preserves hierarchy and `isinstance` checks, but requires wrapping every Python exception class — impractical given the size of the hierarchy.
  - **C — Python types as selector, POOP wrapper in handler** *(recommended)*: `on_error(exc_type, handler)` accepts a native Python exception class as the type selector (used directly in `except`), but wraps the caught exception in a POOP `Error` object before passing to the handler. Pragmatic and compatible with the full Python exception ecosystem; the only leak is the exception class reference used as argument.
  - For raising: `Error("msg", ValueError).raise_()` — `Error` wraps a Python exception instance and `raise_()` re-raises it. Avoids transforming every exception constructor; the `Error` constructor accepts an optional Python exception class as kind. The keyword `raise` is banned by `no_raise`; `raise_` follows PEP 8 keyword escape.
  - For resumable exceptions (Smalltalk-style `e resume: value`): not planned — Python's exception model does not support resumption natively.

- **Naming strategy for Python keyword → method**: `for`, `while`, `in` are Python keywords that cannot be used as method names. POOP currently handles them inconsistently: `for` → `for_each` (Java/JS compound), `while` → `while_true` (descriptive compound), `in` → `includes` (semantic equivalent from `__contains__`). Three approaches exist: (1) PEP 8 trailing underscore — `for_`, `while_`, `in_` — mechanical but ugly; (2) descriptive compound — `for_each`, `while_true` — readable but not Python names; (3) semantic equivalent — `includes`, `contains` — most Pythonic but requires case-by-case judgment. A consistent rule should be decided before adding new keyword-derived methods.

- **`while_true` not yet implemented**: `no_loops` blocks `ast.While` and documents `cond.while_true(block)` as the substitute, but `Boolean` does not implement `while_true`. The validator is active without a working substitute — violates the principle "activate validator only when the substitute exists". Implement `while_true(block)` on `Boolean` (and decide what it returns) before this is considered complete.

- **`in` operator not blocked**: `x in col` uses `__contains__` internally and is not rejected by any validator. POOP has `col.includes(x)` as the message-passing equivalent, but the operator form still works — a silent inconsistency. Decide: add a `no_in` validator, or explicitly allow `in` as syntactic sugar for `__contains__`.

- **`for_each` vs `for_`**: iteration method is named `for_each` because `for` is a Python keyword. `for_` (PEP 8 trailing-underscore convention) was rejected because it reads awkwardly. `for_each` is semantically clear but not a Python builtin name — worth revisiting when the broader keyword naming strategy is decided.

- **Classmethods as POOP messages**: some Python built-in types expose useful classmethods — `int.from_bytes(b, byteorder)`, `float.fromhex(s)`, `bytes.fromhex(s)`, `dict.fromkeys(keys)`. These cannot be expressed as messages to an instance. Two questions: (1) should POOP support sending messages to class objects at all, and (2) if so, should the transformer pipeline intercept `Int.from_bytes(...)` and rewrite it to a factory function? Until decided, these methods are excluded from the Python API parity audit.

- **`import`** (`ast.Import`, `ast.ImportFrom`): evaluate whether to ban or restrict to POOP module imports.
