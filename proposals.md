# Proposals

### ~~115. `Int`/`Float` arithmetic raises `AttributeError` instead of returning `NotImplemented`, killing every reflected dunder~~ — DONE

**Decision + implemented:** the six binary operators (`__add__`/`__sub__`/`__mul__`/`__truediv__`/`__floordiv__`/`__mod__`) on `Int` (`poop/types/int.py`) and `Float` (`poop/types/float.py`) now guard with `if not isinstance(other, Int | Float): return NotImplemented`, so Python falls back to the right operand's reflected dunder. `2 + Fraction(1, 2)` → `Fraction(5, 2)`, `2 * NormalDist(...)` reaches `__rmul__`. This subsumes proposal 152 (`3 * "ab"` now answers `Str("ababab")` via `Str.__rmul__`). Tests in `tests/test_types/test_int.py` and `test_float.py`.

### ~~116. `TimeDelta + Date` answers a corrupted `TimeDelta` wrapping a `datetime.date`~~ — DONE

**Decision + implemented:** `TimeDelta.__add__`/`__sub__` now return `NotImplemented` for non-`TimeDelta` operands, and `Date`/`DateTime` gained an `__radd__` (delegating to `__add__`), so `TimeDelta + Date` answers a `Date` (and `+ DateTime` a `DateTime`) via reflected dispatch. Added `TimeDelta.__rmul__ = __mul__` so `2 * TimeDelta(...)` works (reachable now that proposal 115's `Int.__mul__` yields `NotImplemented`). Tests in `tests/test_types/test_datetime.py`.

### ~~117. `Date`, `Time`, and `TimeDelta` cannot be ordered (`<` crashes)~~ — DONE

**Decision + implemented:** added a shared `_OrderedImplMixin` in `poop/types/datetime.py` (`__lt__`/`__le__`/`__gt__`/`__ge__` over `self._impl`) and mixed it into `TimeDelta`, `Date`, and `Time`. `DateTime` now inherits it too (its inline copies were removed). All three orderings answer a POOP `Boolean`. Tests in `tests/test_types/test_datetime.py`.

### ~~118. `replace(tzinfo=None)` cannot strip a timezone — aware values can never become naive~~ — DONE

**Decision + implemented:** added a typed `_ABSENT` sentinel (`_AbsentType`) and a `_replace_tz` helper in `poop/types/datetime.py`; `Time.replace`/`DateTime.replace` now default `tzinfo` to `_ABSENT` so the three cases are distinct — omitted keeps the current tzinfo, POOP `none` strips to naive, a wrapper sets it. `aware.replace(tzinfo=none).tzinfo` now answers `none`. Tests in `tests/test_types/test_datetime.py`.

### ~~119. `Fraction == Int` answers `false` while `Fraction >= Int` answers `true`~~ — DONE

**Decision + implemented:** `Fraction` now overrides `__eq__`/`__ne__` to route through `_cmp` (the same dispatch used by `<`/`<=`/`>`/`>=`), so `Fraction(2) == 2` answers `true` and Float equality matches the ordering operators (`Fraction(1,2) == 0.5` → `true`, matching CPython). Foreign operands still fall back to `false`/`true`. Updated the stale `test_fraction_compared_to_float` and added tests in `tests/test_types/test_fractions.py`.

### 120. `decimal` precision/rounding can never be changed — the documented `localcontext` recipe is impossible

- **Where:** `poop/types/decimal.py:153-176` (`Context` — `prec` and `rounding` are read-only properties, `__slots__ = ("_impl",)`, constructor takes only a raw `_decimal.Context`), `poop/types/decimal.py:253` (`localcontext`)
- **Bug:** MIGRATION.md tells users to "use `With(lambda: decimal.localcontext()).do(lambda ctx: …)` to scope precision/rounding changes", but the `Context` the body receives exposes no way to change anything: `prec`/`rounding` have no setters, `Context` is not an `Object` (no `set_attr`), and user code cannot construct a `Context` with different settings (the constructor takes a raw CPython context users can't make). Net effect: decimal precision in POOP is permanently stuck at the default.
- **Repro:**

  ```python
  With(lambda: decimal.localcontext()).do(lambda ctx: ctx.set_attr("prec", 5))
  # poop: 'Context' object has no attribute 'set_attr'
  ```

  (Plain attribute assignment is impossible inside the `do` lambda, and no other entry point mutates a context.) Real Python: `with decimal.localcontext() as ctx: ctx.prec = 5` works, as does `decimal.localcontext(prec=5)` on 3.11+.
- **Proposed fix:** mirror CPython 3.11+ kwargs on the namespace entry point — `decimal.localcontext(ctx=none, prec=none, rounding=none)` forwarding via `_kwargs_from` — and/or add `set_prec(Int)` / `set_rounding(Str)` mutator methods to `Context` (same pattern as `SSLContext.set_verify_mode`).

### ~~121. Documented `.do(...)` recipes crash: `GlobIter`, `csv.Reader`/`DictReader`, and `Shlex` lack the iteration surface~~ — DONE

**Decision + implemented:** mixed `_IterableMixin` into `GlobIter` (`poop/types/glob.py`), `Reader`/`DictReader` (`poop/types/csv.py`), and `Shlex` (`poop/types/shlex.py`); their existing `__iter__` already yields POOP values, so `.do`/`.map`/`.filter` now work. The documented MIGRATION.md recipes (`glob.iglob(...).do(...)`, `csv.reader(...).do(...)`, `lexer.do(...)`) run. Tests in the three corresponding test files.

### ~~122. `sqlite3` `Row` is an injected entry point that cannot be used at all~~ — DONE

**Decision + implemented:** made `Row.__init__` (`poop/types/sqlite3.py`) unwrap its `columns`/`values` arguments via `to_python` (and `tuple(...)`), so the documented class is constructible from user code passing POOP `Tuple`/`List` (`Row(("a", "b"), (1, "x")).at("a")` → `1`). The `at`/`keys`/`values` methods, written for raw column strings, now work. Tests in `tests/test_types/test_sqlite3.py` (existing raw-tuple unit tests updated to POOP `Tuple`s, matching how user code calls it).

### ~~123. `re.sub`/`subn` reject a lambda replacement with an `AttributeError`~~ — DONE

**Decision + implemented:** `_unwrap_repl` (`poop/types/re.py`) now bridges a POOP `Block` replacement into a raw `match -> str` adapter (`lambda m: to_python(repl(Match(m)))`), returning the raw string only for `Str`. Widened the `repl` annotations on `Pattern.sub`/`subn` and `Re.sub`/`subn` to `Str | Block`. `re.sub("a", lambda m: "X", "banana")` → `"bXnXnX"`. Tests in `tests/test_types/test_re.py`.

### 124. The `Enum` functional API crashes in every form CPython supports

- **Where:** `poop/types/enum.py:56` (`Enum` and siblings — no interception of the functional form)
- **Bug:** `Enum("Color", ...)` delegates to CPython's `EnumType.__call__`, which receives POOP values: the member list is a POOP `List` of `Str`s, and since `Str` is iterable the enum machinery tries to unpack each name as a `(name, value)` pair. All three CPython call shapes fail, each with a different confusing message.
- **Repro:**

  ```python
  Enum("Color", ["RED", "GREEN"])        # poop: too many values to unpack (expected 2)
  Enum("Color", "RED GREEN")             # poop: not enough values to unpack (expected 2, got 1)
  Enum("Color", [("RED", 1), ("GREEN", 2)])  # poop: 'str' object is not subscriptable
  ```

  Real Python: all three produce a working `Color` enum.
- **Proposed fix:** give the POOP bases a small metaclass overriding `__call__`: when `names`-style arguments are present, unwrap them with `to_python` (Str → str, List/Tuple → list, Dict → dict) before delegating to `EnumType.__call__`. At minimum, raise a clear `TypeError` pointing at the class-statement form instead of leaking unpack errors.

### ~~125. REPL echoes `None` after every `.print()` (and clobbers `_`)~~ — DONE

**Decision + implemented:** `Repl._displayhook` (`poop/repl.py`) now suppresses POOP `none` (`isinstance(value, NoneClass)`) as well as raw `None`, so `.print()` no longer echoes `None` or clobbers `_`. The now-dead `NoneClass` branch in `_colorize_value` was removed. Tests in `tests/test_repl.py`.

### ~~126. The datetime family prints `<Date>` instead of its value~~ — DONE

**Decision + implemented:** added a shared `_StrReprMixin` in `poop/types/datetime.py` (`__str__` delegating to `str(self._impl)`, `__repr__ = __str__`) and mixed it into all five wrappers (`TimeDelta`, `TimeZone`, `Date`, `Time`, `DateTime`). `.print()` now shows `2024-01-01` / `1 day, 2:00:00` / `UTC`. Tests in `tests/test_types/test_datetime.py`.

### ~~127. asyncio `Future.exception()` answers the raw Python exception~~ — DONE

**Decision + implemented:** `Future.exception()` (`poop/types/asyncio.py`) now answers `none` when there is no exception and `Error(result)` otherwise, mirroring the `gather` contract instead of leaking the raw `BaseException` through `to_poop`. Tests in `tests/test_types/test_asyncio.py`.

### ~~128. concurrent `CFFuture.exception()` answers the raw Python exception~~ — DONE

**Decision + implemented:** `CFFuture.exception(timeout)` (`poop/types/concurrent.py`) now answers `none` or `Error(result)` (importing `Error` from `poop.types.error`) instead of routing a `BaseException` through `to_poop`. Tests in `tests/test_types/test_concurrent.py`.

### ~~129. `statistics` central-tendency functions leak raw `fractions.Fraction`~~ — DONE

**Decision + implemented:** added a local `_wrap_number` helper in `poop/types/statistics.py` that re-wraps a raw `fractions.Fraction` as a POOP `Fraction` (falling back to `to_poop`), used in `mean`/`median`/`median_low`/`median_high`/`mode`/`multimode`. `statistics.mean` over POOP Fractions now answers a POOP `Fraction`. (Kept the fix local rather than touching the global `to_poop`.) Tests in `tests/test_types/test_statistics.py`. Proposal 130 extends `_wrap_number` to `Decimal`.

### ~~130. `statistics` functions crash on `Decimal` data~~ — DONE

**Decision + implemented:** added a `Decimal` branch to `_to_number` (`return value._impl`) so the stdlib receives raw decimals, and a `decimal.Decimal` branch to the local `_wrap_number` helper so `mean`/`median`/`mode` answer a POOP `Decimal`. The spread functions (`stdev`/`variance`/`pstdev`/`pvariance`) route through a new `_wrap_spread` helper that answers `Decimal` for Decimal input and `Float` otherwise — preserving POOP's established Float convention for int/float spread results (kept the fix local to `statistics.py` rather than touching the global `to_poop`, whose CPython-natural typing would have changed `pvariance` of ints from `Float` to `Int`). Tests in `tests/test_types/test_statistics.py`.

### ~~131. `configparser` `fallback=None` answers corrupted wrappers — `getboolean` silently answers `false`~~ — DONE

**Decision + implemented:** added an `_unwrap_fallback` helper in `poop/types/configparser.py` that converts a POOP `none` fallback to real Python `None` (and unwraps typed fallbacks); `get`/`getint`/`getfloat`/`getboolean` now check the impl result and `return none if result is None else <wrap>(result)`. A missing option with `fallback=none` answers POOP `none` (so `getboolean` no longer silently answers `false`), and the return annotations widened to `… | NoneClass`. Tests in `tests/test_types/test_configparser.py`.

### ~~132. `Logger("app")` builds a corrupt logger that explodes on first use~~ — DONE

**Decision + implemented:** `Logger.__init__` (`poop/types/logging.py`) now mirrors CPython — `def __init__(self, name: Str, level: Int | Str | None = None)` building `_logging.Logger(name._value, ...)` — so `Logger("app")` constructs a working logger (standalone, level `NOTSET`). Internal wrapping moved to `_ImplWrapperMixin._from_impl` and `Logging.getLogger` updated to call it. Tests in `tests/test_types/test_logging.py`.

### ~~133. `SSLContext(ssl.PROTOCOL_TLS_CLIENT)` silently stores the protocol Int as the context~~ — DONE

**Decision + implemented:** `SSLContext.__init__` (`poop/types/ssl.py`) now takes a `protocol: Int` (CPython's canonical ctor argument) — `ssl.SSLContext(protocol._value)` — keeping the no-arg `PROTOCOL_TLS_CLIENT` default. Raw-impl wrapping moved to the `_ImplWrapperMixin._from_impl` classmethod (used by `create_default_context`), so an arbitrary object can no longer be smuggled into `_impl`. Tests in `tests/test_types/test_ssl.py`.

### ~~134. `MPQueue.put` of any POOP value poisons the queue — `get()` deadlocks~~ — DONE

**Decision + implemented:** `MPQueue.put`/`get` (`poop/types/multiprocessing.py`) now bridge at the boundary like `pickle.py` — `put(to_python(item), ...)` and `get` returns `to_poop(...)`. A POOP value survives the round trip (it previously failed to pickle in the feeder thread and deadlocked `get()`). Tests in `tests/test_types/test_multiprocessing.py`.

### ~~135. `dict(a=1, b=2)` rejects the keyword constructor form~~ — DONE

**Decision + implemented:** `_DictRewriter.visit_Call` (`poop/transformers/dict.py`) now forwards named keywords to `_poop_dict_from`, and `_poop_dict_from(arg=None, **kwargs)` seeds from `arg` (as before) then sets `d._data[Str(k)] = v` for each keyword. `dict(a=1, b=2)` → `{'a': 1, 'b': 2}`, and `dict(mapping, a=1)` works too. A `**` splat (`kw.arg is None`) is left to the generic path (its own concern). Other collection rewriters keep the no-keyword guard. Tests in `tests/test_transformers/test_dict.py`.

### ~~136. `Str.startswith`/`endswith` crash on a tuple of prefixes~~ — DONE

**Decision + implemented:** widened `Str.startswith`/`endswith` (`poop/types/string.py`) to `prefix: Str | Tuple`, unwrapping a `Tuple` into a raw `tuple` of strings (`tuple(str(p) for p in prefix._items)`) before delegating. `"abc".startswith(tuple("a", "z"))` now answers `true` — the message-shaped substitute for the forbidden `startswith(...) or startswith(...)`. Tests in `tests/test_types/test_str.py`.

### ~~137. CLI dumps a raw rich traceback when the source file does not exist~~ — DONE

**Decision + implemented:** wrapped the `file.read_text` call in `poop/cli.py` in `try/except OSError`, emitting `poop: cannot read '<path>': <strerror>` and exiting 1 — keeping the established one-line `poop:` style for missing files, directories, and permission errors instead of leaking a rich traceback. Tests in `tests/test_cli.py`.

### ~~138. Starred unpacking binds the rest-target to a raw Python `list`~~ — DONE

**Decision + implemented:** added an `UnpackTransformer` (`poop/transformers/unpack.py`, registered in `DEFAULT_TRANSFORMERS`) whose `visit_Assign` detects `ast.Starred` anywhere in the target tree and appends `target = _poop_list_from(target)` per starred name after the assignment — handling nested (`a, (b, *inner) = …`) and attribute (`a, *self.rest = …`) targets. The starred rest-collection is now a POOP `List` instead of a raw `list`. Tests in `tests/test_transformers/test_unpack.py`; catalogued in INFECTIONS.md.

### ~~139. `*args` / `**kwargs` parameters bind a raw `tuple` / raw `dict` (with raw `str` keys)~~ — DONE

**Decision + implemented:** added a `VarargsTransformer` (`poop/transformers/varargs.py`, registered in `DEFAULT_TRANSFORMERS`). For every `FunctionDef`/`AsyncFunctionDef` with `args.vararg`/`args.kwarg` it injects a prologue (`args = _poop_tuple_from(args)`, `kw = _poop_dict_from_kwargs(kw)`); variadic lambdas wrap their body in a nested lambda receiving the converted values. `args` is now a POOP `Tuple`, `kw` a POOP `Dict` with `Str` keys. Added a `_poop_dict_from_kwargs` binding to the dict transformer (`_poop_tuple_from` already existed). Tests in `tests/test_transformers/test_varargs.py`; catalogued in INFECTIONS.md.

### ~~140. User methods without an explicit `return` answer raw Python `None`, not POOP `none`~~ — DONE

**Decision + implemented:** added a `ReturnTransformer` (`poop/transformers/return_.py`, registered in `DEFAULT_TRANSFORMERS`) that, for every `FunctionDef`/`AsyncFunctionDef` except `__init__`, rewrites a bare `return` to `return _poop_none` and appends `return _poop_none` when the body does not already end in a `return`/`raise`. Void methods now answer the `none` singleton, so `result.is_none()` / `.print()` / `.if_none(...)` work. `__init__` is skipped (CPython requires real `None`); the `_poop_none` binding comes from `NoneTransformer`. Tests in `tests/test_transformers/test_return_.py`; catalogued in INFECTIONS.md.

### ~~141. `import` statements pass validation and bind raw Python modules — shadowing injected namespaces~~ — DONE

**Decision + implemented:** added a `no_import` validator (`poop/validators/no_import.py`, via `make_node_validator`) rejecting `ast.Import` and `ast.ImportFrom` with a message naming the substitute ("POOP injects its stdlib namespaces … the names are already in scope"), registered in `DEFAULT_VALIDATORS`. `import os` / `from os import getcwd` / `import json as j` are now caught at validation time instead of leaking raw Python modules. Tests in `tests/test_validators/test_no_import.py`; catalogued in INFECTIONS.md.

### ~~142. `{**a, ...}` dict-literal splat (and `f(**kw)`) crash — POOP `Dict` cannot be used as a `**`-unpacking mapping~~ — DONE

**Decision + implemented:** `_DictRewriter.visit_Dict` (`poop/transformers/dict.py`) no longer bails on a `**` entry — it rewrites the display into `_poop_dict_merge(...)`, folding runs of plain pairs (`_poop_dict_from_pairs(...)`) and each `**x` entry left to right (later keys win). `{**a, "y": 2}` and `{**a, **b}` now build a real POOP `Dict`. Added `Dict.__getitem__` (`poop/types/dict.py`) so the mapping protocol's read side works (user subscript stays forbidden by `no_subscript`). The call-site `f(**kw)` splat with a POOP `Dict` remains unsupported — Python requires raw-`str` keys for `**`-into-a-call, which conflicts with POOP `Str` keys — but now fails with the clearer `keywords must be strings` rather than `not subscriptable`. Tests in `tests/test_transformers/test_dict.py`.

### ~~143. Open-ended slice `obj.slice(start, None)` crashes on every sliceable type~~ — DONE

**Decision + implemented:** routed the Int form of every `slice` method (`Str`, `List`, `Tuple`, `Bytes`, `ByteArray`, `Array`, `Range`) through the existing `Slice` helper — `Slice(start_or_slice, stop, step)._py_slice()` — whose `_coerce` already treats both Python `None` and POOP `none` as absent. `obj.slice(2, none)` now means open-ended (`obj[2:]`), and the `"stop is required"` guard was dropped (so `obj.slice(2)` is also open-ended). Widened the `stop`/`step` annotations to `Int | NoneClass | None`. Tests in the affected type test files.

### 144. Enum-family members answer raw `bool`/`int` from every operator message — enum dispatch is impossible

- **Where:** `poop/types/enum.py:23` — `_PoopEnumMixin` adds `name_str` /
  `value_object` / `iter` / `_missing_`, but members do not inherit `Object`
  and no operator dunder is bridged: `Enum` members fall back to
  `object.__eq__`, `IntEnum`/`IntFlag` members to `int.__eq__` / `int.__lt__`
  / `int.__add__` / etc.
- **Leak:** `Color.RED == Color.GREEN` answers a raw Python `bool` (same for
  `!=`, and for `<`/`<=`/`>`/`>=` on `IntEnum`/`IntFlag`); `IntEnum` member
  arithmetic (`Priority.LOW + Priority.HIGH`) answers a raw `int`. Because
  `is` is forbidden (`no_is`) and members are not `Object`s (no
  `is_identical`), there is **no** POOP-typed way to compare two members at
  all — so the one branching idiom the language offers,
  `(state == State.IDLE).if_true(...)`, crashes, making state dispatch on an
  enum impossible. (`.name` / `.value` raw pass-through is documented by
  design in the module docstring; the operator results are not.)
- **Evidence:** e2e (`uv run python main.py ...`):

  ```python
  class State(Enum):
      IDLE = 1
      BUSY = 2

  current = State.IDLE
  (current == State.IDLE).if_true(lambda: "idle".print())
  # poop: 'bool' object has no attribute 'if_true' (line 6)
  ```

  `(Color.RED == Color.GREEN).print()` → `poop: 'bool' object has no
  attribute 'print'`; with `IntEnum`, `(LOW < HIGH).print()` → same, and
  `(LOW + HIGH).print()` → `poop: 'int' object has no attribute 'print'`;
  `IntFlag` equality leaks identically. Identity probe (display names are
  masked — `Boolean.__name__` is rebound to `"bool"`):
  `(Color.RED == Color.GREEN).__class__ is builtins.bool` → `True`,
  `isinstance(..., Boolean)` → `False`; `(LOW + HIGH).__class__ is
  builtins.int` → `True`; `hasattr(Color.RED, "is_identical")` → `False`.
- **Proposed fix:** bridge operator results in `_PoopEnumMixin`: add
  `__eq__`/`__ne__` returning `to_boolean(...)` — delegate to
  `super().__eq__(other)` and fall back to identity when it answers
  `NotImplemented` — plus `def __hash__(self): return super().__hash__()` to
  keep each family's hash; wrap `__lt__`/`__le__`/`__gt__`/`__ge__` the same
  way for the int-based families, and route `IntEnum` arithmetic results
  through `to_poop`. Verified feasible: a probe mixin with exactly that
  `__eq__` answers a POOP `Boolean` while alias resolution
  (`CRIMSON = 1` → `is RED`) and member-keyed dict lookup keep working,
  because `Boolean.__bool__` preserves truthiness for enum internals.

### ~~145. Rebinding (or passing) a forbidden builtin bypasses every call-name validator — raw `int`/`list`/class objects flow out~~ — DONE

**Decision + implemented:** `make_call_name_validator` (`poop/validators/_call_name.py`) now visits `ast.Name` instead of `ast.Call`, rejecting any reference to a forbidden name regardless of context (assignment RHS/target, argument, decorator, default), so the ~39 forbidden builtins are fully reserved identifiers and the wrapper layer can't be reopened by `f = len` / `words.map(len)` / `len = 5`. Method substitutes (`xs.len()`, `n.hex()`) are `ast.Attribute` nodes and keyword-argument names aren't `Name` nodes, so both stay unaffected. The full suite passes unchanged. Tests in `tests/test_validators/test_no_len.py`.

### ~~146. Binding a lowercase builtin name (`int = 5`, `def __init__(self, dict)`) silently rebinds the interpreter's mangled internals~~ — DONE

**Decision + implemented:** added a `no_builtin_shadow` validator (`poop/validators/no_builtin_shadow.py`) that reuses the `no_namespace_shadow` `_Visitor` (generalized to take a message) over the fixed set of 16 rewritten builtin names (`bool`/`int`/`float`/…/`zip`), registered in `DEFAULT_VALIDATORS`. Rebinding one via assignment, class name, or `def`/`lambda` parameter now raises `'<name>' is a POOP builtin name; it cannot be rebound` at parse time instead of silently corrupting the interpreter internals; constructor calls (`int("5")`) are unaffected. Tests in `tests/test_validators/test_no_builtin_shadow.py`; catalogued in INFECTIONS.md (also corrected the stale "does not catch parameters" note there).

### ~~147. sqlite3 named-placeholder parameters (`:name` + dict) are rejected — "parameters are of unsupported type"~~ — DONE

**Decision + implemented:** added a `Dict` branch to `_unwrap_params` (`poop/types/sqlite3.py`) — `return to_python(params)` deep-converts to a raw mapping — so named placeholders (`:name` + Dict) work in `execute`/`executemany` for both `Connection` and `Cursor`. Widened the `params` annotations to `Tuple | List | Dict | NoneClass`. Tests in `tests/test_types/test_sqlite3.py`.

### ~~148. `Decimal` is sealed off from `Int`/`Float`: mixed arithmetic and ordering crash, mixed equality answers `false`~~ — DONE

**Decision + implemented:** added `_arith`/`_cmp` helpers to `Decimal` (mirroring `Fraction`). Arithmetic accepts `Decimal`/`Int` and returns `NotImplemented` for `Float` (so `Decimal + float` raises `TypeError`, matching CPython) and foreign types; reflected dunders (`__radd__`…`__rpow__`) were added so `1 + d` works (reachable via proposal 115). Comparisons and `__eq__`/`__ne__` accept `Int`/`Float` via the raw `_decimal.Decimal` mixed-type comparison, falling back to `false`/`true` for foreign types. Tests in `tests/test_types/test_decimal.py`.

### 149. logging `Formatter.default_time_format` / `default_msec_format` answer bare Python `str` — and the msec knob is unusable in both directions

- **Where:** `poop/types/logging.py:242` — `class Formatter(_logging.Formatter)`
  neither rebinds nor intercepts the two CPython class-attribute knobs, so
  `default_time_format` and `default_msec_format` are inherited raw from
  `logging.Formatter`.
- **Leak:** reading `Formatter.default_time_format` or
  `Formatter.default_msec_format` answers a bare Python `str` — every POOP
  message on it crashes. These are CPython's documented `formatTime` knobs,
  and `default_msec_format` matters on its own: changing the asctime
  millisecond separator (`,` → `.`) is its canonical use, and nothing else on
  the POOP surface covers it (`Formatter(datefmt=...)` replaces the
  seconds-level format but never the msec suffix). The write direction is
  broken symmetrically: `Formatter.default_msec_format = "%s.%03d"` stores a
  POOP `Str` that the raw `formatTime` cannot `%`-format, so the next
  `%(asctime)s` log line dumps a CPython "Logging error" traceback instead of
  logging. An automated sweep over every `DEFAULT_NAMESPACE` entry point (plus
  one level of sub-namespaces) shows these are the only bare constants left
  that are not catalogued pass-throughs — `csv.excel`/`Logging.Filterer` are
  documented "Python class refs", and `enum.STRICT` / `signal.SIG_DFL` /
  `ssl.PURPOSE_*` are documented argument tokens.
- **Evidence:** e2e (`uv run python main.py ...`):

  ```python
  Formatter.default_msec_format.print()
  # poop: 'str' object has no attribute 'print' (line 1)
  ```

  Write path:

  ```python
  Formatter.default_msec_format = "%s.%03d"
  lg = logging.getLogger("t")
  h = logging.StreamHandler()
  h.setFormatter(Formatter("%(asctime)s %(message)s"))
  lg.addHandler(h)
  lg.warning("hello")
  # --- Logging error --- ... TypeError: unsupported operand type(s)
  # for %: 'str' and 'tuple'   (the stored Str cannot service formatTime)
  ```

  Identity probe: `Formatter.default_time_format.__class__ is builtins.str`
  → `True`, and the object `is logging.Formatter.default_time_format` (the
  raw stdlib attribute, untouched by the wrapper).
- **Proposed fix:** follow the `zlib.ZLIB_VERSION` precedent and bless the
  knobs as POOP values: rebind both on the wrapper —
  `default_time_format: ClassVar[Str] = Str(_logging.Formatter.default_time_format)`
  (same for `default_msec_format`) — and override `formatTime` in the POOP
  `Formatter` to unwrap before delegating (mirror CPython's four-line body,
  reading each knob through `v._value if isinstance(v, Str) else v`). That
  makes reads answer `Str` and makes user assignment of a POOP `Str` work.
  Optionally, a metaclass `__setattr__` can propagate the raw value to
  `_logging.Formatter` so formatters built by `logging.basicConfig` (raw
  instances) honor the knob globally, matching CPython.

### ~~150. `List` cannot be ordered — `<` crashes and `.sorted()` over nested lists fails~~ — DONE

**Decision + implemented:** added `__lt__`/`__le__`/`__gt__`/`__ge__` to `List` (`poop/types/list.py`), mirroring `Tuple` — each delegates to the raw `list` comparison (`to_boolean(self._items < other._items)`), which dispatches elementwise to the POOP element dunders. `[1, 2] < [1, 3]` and `.sorted()` over nested lists now work. Tests in `tests/test_types/test_list.py`.

### ~~151. The documented `Str.format` template form does not exist — the argument is parsed as a format spec~~ — DONE

**Decision + implemented:** implemented `Str.format(*args, **kwargs)` (`poop/types/string.py`) as CPython's `str.format` template method, unwrapping POOP args via `to_python` and overriding the inherited `Object.format(spec)`. `"Hello, {}!".format("world")` → `"Hello, world!"`, named/indexed/spec placeholders all work. The "apply a spec to a string" case is now expressed via the template form (`"{:^10}".format(s)`); the stale `Str` case in `test_format_int_with_hex_spec` was updated accordingly, and INFECTIONS.md:1514 clarified. Tests in `tests/test_types/test_str.py`.

### ~~152. `3 * "ab"` silently fabricates a corrupted `Int` wrapping a `str`~~ — DONE

**Decision + implemented:** fixed together with proposal 115 — `Int.__mul__` now returns `NotImplemented` for non-`Int`/`Float` operands, so `3 * "ab"` falls back to `Str.__rmul__` and answers `Str("ababab")` (likewise `Bytes`/`ByteArray`). Test `test_mul_by_str_repeats_via_str_rmul` in `tests/test_types/test_int.py`.

### ~~153. Lambda parameters bypass `no_namespace_shadow` — `def m(self, math)` is rejected, `lambda math: ...` is accepted~~ — DONE

**Decision + implemented:** added `visit_Lambda` to `_Visitor` (`poop/validators/no_namespace_shadow.py`), calling the existing `_check_args`, so a lambda parameter named after a namespace binding (`lambda math: math.sqrt(2)`) is rejected at validation time like the `def` form. Lambdas are POOP's block form and carry most user code, so this was the more common unchecked path. Tests in `tests/test_validators/test_no_namespace_shadow.py`.

### ~~154. `int(True)` / `float(True)` reject Boolean — and the diagnostic leaks the internal `_TrueClass` name~~ — DONE

**Decision + implemented:** added a `Boolean` branch to `_poop_int_from` (`int(True)` → `1`) and `_poop_float_from` (`float(True)` → `1.0`) — the sanctioned explicit flag-to-number bridge — and switched both error messages from `__qualname__` to `__name__` so diagnostics show the masked public names (`bool`/`int`/`float`/`complex`) instead of internal class names. Tests in `tests/test_transformers/test_int.py` and `test_float.py`.

### 155. `http.HTTPStatus` / `http.HTTPMethod` members are raw CPython enum objects — every read path leaks

- **Where:** `poop/types/http.py:327-328` (`Http.HTTPStatus` / `Http.HTTPMethod` re-export `_http.HTTPStatus` / `_http.HTTPMethod` unwrapped), `poop/types/http.py:29-42` (the `_missing_` patch that makes POOP `Int`/`Str` arguments resolve to members — proof that member lookup is an intended user path, not an internal token)
- **Leak:** the two enums are bound into the user namespace as the raw CPython
  classes, so every value that comes out of them is a bare Python object: the
  member itself (`HTTPStatus.OK`) answers no POOP message; `.value` is a raw
  `int`, `.phrase` / `.description` raw `str`; member equality answers a raw
  `bool`, so the one branching idiom POOP offers —
  `(status == HTTPStatus.OK).if_true(...)` — crashes, making status dispatch
  impossible. The module even patches `_missing_` so `HTTPStatus(Int(200))`
  resolves — and then hands back the raw member, so the supported POOP-side
  construction path leaks too. Distinct from entry 144 (POOP enum-family
  *user classes* leak operator results — those members at least carry
  `name_str`/`value_object`) and from entry 149's constants sweep (which
  excluded `enum.STRICT`-style *argument tokens*; `HTTPStatus` members are
  read as user-facing values, not passed back into wrapper calls).
- **Evidence:** e2e (`uv run python main.py ...`), each line crashing
  independently:

  ```python
  http.HTTPStatus.OK.print()
  # poop: 'HTTPStatus' object has no attribute 'print'   (Python: HTTPStatus.OK)
  http.HTTPStatus.OK.phrase.print()
  # poop: 'str' object has no attribute 'print'          (Python: OK)
  http.HTTPStatus(200).value.print()
  # poop: 'int' object has no attribute 'print'          (Python: 200)
  (http.HTTPStatus.OK == http.HTTPStatus.OK).if_true(lambda: "ok".print())
  # poop: 'bool' object has no attribute 'if_true'       (Python: True branch)
  http.HTTPMethod.GET.print()
  # poop: 'HTTPMethod' object has no attribute 'print'   (Python: HTTPMethod.GET)
  ```

  Probes of the sibling namespaces show this is the only raw-enum door of its
  kind on the surface: `signal`/`socket`/`re`/`ssl` expose their flag values
  as POOP `Int` constants (`signal.Signals` / `ssl.TLSVersion` are simply
  absent), so `http` is the lone namespace handing whole raw enum classes to
  user code as values.
- **Proposed fix:** rebuild both enums over the POOP enum-family bases from
  `poop/types/enum.py` instead of re-exporting CPython's: at import time
  construct a POOP `IntEnum` (`HTTPStatus`) and POOP `StrEnum`-shaped class
  (`HTTPMethod`) from `[(m.name, m.value) for m in _http.HTTPStatus]` (the
  *internal* functional call can pass raw names, dodging entry 124), attach
  `phrase` / `description` properties answering `Str` (backed by a lookup
  table built from the CPython members), and keep the `_missing_` unwrap so
  `HTTPStatus(Int(200))` still resolves — now to a POOP member. Combined with
  entry 144's operator bridging on `_PoopEnumMixin`, member equality then
  answers a POOP `Boolean` and status dispatch works. `HTTPClient` call sites
  that feed `_http` internals must unwrap via `member.value_object()._value`
  (or accept both classes) at the boundary.
