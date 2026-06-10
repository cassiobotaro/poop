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

Open items 110–114 below come from a raw-object leak audit (June 2026):
every public message was swept for return values that hand bare Python
objects — or internal class identities — to POOP user space, violating
the CONTRIBUTING.md rule "Methods must return POOP types — never bare
Python values". Documented-by-design pass-throughs (opaque tokens like
`enum.auto()` / `signal.SIG_DFL` / `email.policy.*`, raw class objects
as currency, `gc.callbacks`' mutable list) were left alone.

### 110. `asyncio.gather` resolves to a raw Python `list`

- **Where:** `poop/types/asyncio.py:79`
- **Leak:** `AsyncIO.gather` returns `_asyncio.gather(...)` unchanged, so
  awaiting it inside an `async def` hands the POOP program a bare Python
  `list` of results. A raw list answers no POOP messages — and with
  `for`, `len()`, and subscripts all banned, the aggregate is unusable
  (`.do`, `.at`, `.class_name` all raise `AttributeError`).
- **Evidence:** POOP program run via `uv run python main.py`:

  ```python
  class Gatherer:
      async def one(self, word):
          await asyncio.sleep(0.01)
          return word

      async def run(self):
          return await asyncio.gather(self.one("a"), self.one("b"))

  asyncio.run(Gatherer().run()).class_name().print()
  ```

  Output: `poop: 'list' object has no attribute 'class_name'` — a
  genuinely raw `builtins.list` (POOP `List` does answer `class_name`;
  its rebranded `__name__` is `list` too, but it never raises here).
- **Proposed fix:** make `gather` an async adapter that wraps the
  resolved results; `Error`-wrap exceptions on the
  `return_exceptions=true` path, mirroring what `Try` hands to handlers:

  ```python
  @staticmethod
  async def gather(*coros_or_futures: Any, return_exceptions: Boolean = false) -> List:
      results = await _asyncio.gather(
          *(_as_coro(a) for a in coros_or_futures),
          return_exceptions=bool(return_exceptions),
      )
      return List(*(Error(r) if isinstance(r, BaseException) else r for r in results))
  ```

  `wait_for(gather(...))` / `shield(gather(...))` keep composing —
  `_as_coro` accepts the coroutine this now returns. Update the
  INFECTIONS.md `asyncio.gather` row ("resolves to list of results" →
  "resolves to `List` of results").

### 111. `csv.get_dialect` bypasses the POOP `Dialect` wrapper

- **Where:** `poop/types/csv.py:336`
- **Leak:** returns the raw `_csv.Dialect` instance, so every attribute
  (`delimiter`, `quotechar`, `quoting`, …) is a bare `str`/`int`/`bool`.
  The sibling path `Sniffer.sniff` already wraps the very same kind of
  object in the POOP `Dialect` wrapper — whose docstring promises
  "downstream user code stays in POOP-land" — making this a classic
  wrap-one-path-but-not-the-other inconsistency.
- **Evidence:**
  - `uv run python -c "from poop.transformers import DEFAULT_NAMESPACE as NS; from poop.types.string import Str; print(type(NS['csv'].get_dialect(Str('excel'))))"`
    → `<class '_csv.Dialect'>` (the POOP wrapper would report
    `poop.types.csv.Dialect`).
  - POOP program: `csv.get_dialect("excel").delimiter.print()` →
    `poop: 'str' object has no attribute 'print'`.
- **Proposed fix:**

  ```diff
       @staticmethod
  -    def get_dialect(name: Str) -> Any:
  -        return _csv.get_dialect(name._value)
  +    def get_dialect(name: Str) -> Dialect:
  +        return Dialect(_csv.get_dialect(name._value))
  ```

### 112. `zlib.ZLIB_VERSION` is a bare `str`

- **Where:** `poop/types/zlib.py:116`
- **Leak:** the class attribute is bound to the raw version banner
  string while every sibling constant in the same namespace is wrapped
  (`Int`), and the analogous `sqlite3.sqlite_version` ships as a POOP
  `Str`. The divergence is currently noted inline ("raw str (version
  banner)") and in INFECTIONS.md, but it buys nothing: a banner string
  has no identity or mutation semantics that a `Str` wrap would lose —
  unlike the deliberate raw tokens (`signal.SIG_DFL`, `enum.auto()`).
  Also reachable as `compression.zlib.ZLIB_VERSION` (same class
  re-exported).
- **Evidence:** POOP program: `zlib.ZLIB_VERSION.print()` →
  `poop: 'str' object has no attribute 'print'`.
- **Proposed fix:**

  ```diff
  -    ZLIB_VERSION: ClassVar[Any] = _zlib.ZLIB_VERSION  # raw str (version banner)
  +    ZLIB_VERSION: ClassVar[Str] = Str(_zlib.ZLIB_VERSION)
  ```

  plus the matching INFECTIONS.md row update (`Python str` → `Str`).

### 113. `true` / `false` / `none` leak internal class identities

- **Where:** `poop/types/boolean.py:203` (the `__name__ = "bool"` patch
  lands on the abstract `Boolean` base only — the concrete singleton
  classes `_TrueClass` / `_FalseClass` keep their internal names);
  `poop/types/none.py` (`NoneClass`, no rebrand at all)
- **Leak:** the internal class names `_TrueClass`, `_FalseClass`, and
  `NoneClass` escape through the public `class_name()` message and
  through interpreter error messages ("'_TrueClass' object has no
  attribute …"), where CPython answers `bool` / `NoneType`. This
  violates the INFECTIONS.md namespace-hygiene invariant ("POOP
  builtins answer to the same names Python builtins do") and the
  project rule against exposing internal class names to end users.
- **Evidence:** POOP program run via `uv run python main.py`:

  ```python
  (1 == 1).class_name().print()  # prints: _TrueClass   (CPython: bool)
  None.class_name().print()      # prints: NoneClass    (CPython: NoneType)
  ```

- **Proposed fix:** apply the same rebrand every other wrapper gets:

  ```python
  # boolean.py — alongside the existing Boolean rebrand
  for _cls in (_TrueClass, _FalseClass):
      _cls.__module__ = "builtins"
      _cls.__name__ = "bool"

  # none.py
  NoneClass.__module__ = "builtins"
  NoneClass.__name__ = "NoneType"
  ```

### 114. Dict views, one-shot iterators, and `MappingProxy` answer internal PascalCase names

- **Where:** `poop/types/dict_keys.py` / `dict_values.py` /
  `dict_items.py`; the 16 iterator modules built on
  `poop/types/_iterator_base.py:33` (`list_iterator.py`,
  `str_iterator.py`, `dict_key_iterator.py`, …); `poop/types/mapping_proxy.py`
- **Leak:** `class_name()` and error messages answer `DictKeys`,
  `DictItems`, `ListIterator`, `StrIterator`, `MappingProxy`, … where
  CPython answers `dict_keys`, `dict_items`, `list_iterator`,
  `str_iterator`, `mappingproxy`. The iterators already carry the
  CPython-accurate lowercase identity in `_repr_name` (their `__str__`
  prints `<list_iterator>`, `<dict_keyiterator>`, …), so the class
  `__name__` divergence is an oversight, not a decision.
- **Evidence:** POOP program run via `uv run python main.py`:

  ```python
  {"a": 1}.items().class_name().print()  # prints: DictItems     (CPython: dict_items)
  [1].iter().class_name().print()        # prints: ListIterator  (CPython: list_iterator)
  ```

- **Proposed fix:** one line in `_IteratorBase.__init_subclass__` —
  set `cls.__name__ = name` (and `cls.__module__ = "builtins"`) next to
  the existing `cls._repr_name = name`, reusing the per-class lowercase
  names the maintainer already chose — plus explicit rebrands for the
  three dict views (`dict_keys` / `dict_values` / `dict_items`) and
  `MappingProxy` (`mappingproxy`), mirroring the existing
  `List.__name__ = "list"` pattern.

---

Audit side notes (verified clean, no action): `tomllib` wraps TOML
dates/times into `Date`/`Time`/`DateTime`; `locale.localeconv` wraps
nested grouping lists; binary operators across all core and wrapper
types return POOP values; `Try` handlers receive `Error`; pickle
round-trips return POOP objects. One docs mismatch surfaced en route:
INFECTIONS.md ("Use `Path` and `With(Path(...).open(...))`") references
a `Path.open()` method that does not exist.
