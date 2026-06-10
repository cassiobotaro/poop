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

### 122. `sqlite3` `Row` is an injected entry point that cannot be used at all

- **Where:** `poop/types/sqlite3.py:92-117` (`Row`)
- **Bug:** `Row` is bound into the namespace (per the `sqlite3` transformer) but nothing in `poop/types/sqlite3.py` ever constructs it — `fetchone`/`fetchall` always build `Tuple`s and there is no `row_factory` hook. Constructing it from user code is the only path left, and that is broken: `__init__` stores the POOP `Tuple`s as-is while `at`/`keys`/`values` are written for raw Python tuples (`self._columns.index(key._value)` searches a POOP `Tuple` for a raw `str`), so every lookup fails.
- **Repro:**

  ```python
  r = Row(("a", "b"), (1, "x"))
  r.at("a").print()
  # poop: tuple.index(x): x not in tuple
  ```

  Real Python (`sqlite3.Row` via `row_factory`): `r["a"]` → `1`.
- **Proposed fix:** either wire real support — `Connection.row_factory_row()` (or a `row_factory` kwarg) that makes cursors build `Row(tuple(col[0] for col in description), values)` — or make `Row.__init__` unwrap POOP `Tuple`/`List` inputs via `to_python` so the documented class is at least constructible; today it is dead weight that only crashes.

### 123. `re.sub`/`subn` reject a lambda replacement with an `AttributeError`

- **Where:** `poop/types/re.py:25` (`_unwrap_repl`), used by `Pattern.sub`/`Pattern.subn` (`poop/types/re.py:173,177`) and `Re.sub`/`Re.subn` (`poop/types/re.py:292,310`)
- **Bug:** `_unwrap_repl` unconditionally reads `repl._value`, so only `Str` replacements work. CPython's `re.sub` accepts a callable replacement (match → str), and POOP's own convention bridges POOP blocks into every other stdlib callback slot (`json` hooks, `sqlite3.create_function`, `difflib` `isjunk`, `shutil.copy_function`). Dynamic replacement is otherwise impossible in POOP (no loops to rebuild the string around `finditer`).
- **Repro:**

  ```python
  re.sub("a", lambda m: "X", "banana").print()
  # poop: 'Block' object has no attribute '_value'
  ```

  Real Python: `re.sub("a", lambda m: "X", "banana")` → `'bXnXnX'`.
- **Proposed fix:** teach `_unwrap_repl` to detect a callable and adapt it:

  ```python
  def _unwrap_repl(repl: Str | Block) -> Any:
      if callable(repl):
          return lambda m: to_python(repl(Match(m)))
      return repl._value
  ```

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

### 131. `configparser` `fallback=None` answers corrupted wrappers — `getboolean` silently answers `false`

- **Where:** `poop/types/configparser.py:200-266` (`ConfigParser.get` / `getint` / `getfloat` / `getboolean`; same helpers serve `RawConfigParser`)
- **Bug:** when the option is missing and `fallback=None` is passed (the canonical CPython idiom for "give me None back"), the POOP `none` singleton is forwarded to the stdlib, comes back as the result, and is then force-wrapped: `get` answers `Str(none)` — a `Str` whose `print()` explodes with `__str__ returned non-string (type NoneType)`; `getint`/`getfloat` answer `Int(none)`/`Float(none)` shells that crash on first arithmetic; `getboolean` runs `to_boolean(none)` and answers **`false`**, silently making a missing option indistinguishable from a real `false`. CPython answers `None` in all four cases.
- **Repro:**

  ```python
  cp = ConfigParser()
  cp.read_string("[s]\na = 1\n")
  v = cp.get("s", "missing", fallback=None)
  v.class_name().print()    # str
  v.print()                 # poop: __str__ returned non-string (type NoneType)
  cp.getboolean("s", "missing", fallback=None).print()  # False  (Python: None)
  cp.getint("s", "missing", fallback=None).class_name().print()  # int — corrupt shell
  ```

- **Proposed fix:** in all four methods, unwrap a `NoneClass` fallback to Python `None` before the kwargs dict is built, and check the impl result before wrapping: `result = self._impl.get(...)`; `return none if result is None else Str(result)` (resp. `Int`/`Float`/`to_boolean`).

### 132. `Logger("app")` builds a corrupt logger that explodes on first use

- **Where:** `poop/types/logging.py:358-364` (`Logger.__init__`)
- **Bug:** `Logger` is an injected user-visible entry point, but its constructor is the internal impl-wrapping one (`__init__(self, impl: Any)`). `Logger("app")` therefore silently stores the POOP `Str` as `_impl`; construction succeeds, and the first message send crashes with a baffling `'str' object has no attribute 'info'`. CPython's `logging.Logger("app")` constructs a working logger (named, level `NOTSET`).
- **Repro:**

  ```python
  lg = Logger("app")        # accepted
  lg.info("hello")          # poop: 'str' object has no attribute 'info'
  ```

- **Proposed fix:** make the public constructor accept what CPython's does — `def __init__(self, name: Str, level: Int | Str | None = None)` building `_logging.Logger(name._value, ...)` — and move internal wrapping to a `_from_impl` classmethod (the pattern the impl-wrapper types already use); update `Logging.getLogger` and `LoggerAdapter` to call `_from_impl`. Alternatively, if direct construction should stay discouraged, raise an immediate `TypeError("use logging.getLogger(name)")` instead of corrupting silently.

### 133. `SSLContext(ssl.PROTOCOL_TLS_CLIENT)` silently stores the protocol Int as the context

- **Where:** `poop/types/ssl.py:23-27` (`SSLContext.__init__`)
- **Bug:** the constructor treats any argument as a ready-made raw `ssl.SSLContext` (`self._impl = impl`). Passing a protocol constant — CPython's canonical constructor call, with `ssl.PROTOCOL_TLS_CLIENT`/`PROTOCOL_TLS_SERVER` exposed as `Int`s in the very same namespace — silently stores the `Int` as `_impl`; every subsequent attribute access crashes. There is also no other way to build a `PROTOCOL_TLS_SERVER` context from the protocol constant (the no-arg form hardcodes `PROTOCOL_TLS_CLIENT`).
- **Repro:**

  ```python
  ctx = SSLContext(ssl.PROTOCOL_TLS_CLIENT)   # accepted
  ctx.check_hostname.print()
  # poop: 'int' object has no attribute 'check_hostname'
  # Python: ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT).check_hostname -> True
  ```

- **Proposed fix:** accept the protocol form: `if isinstance(impl, Int): self._impl = _ssl.SSLContext(impl._value)` (keep the no-arg TLS-client default), and move raw-impl wrapping (used by `create_default_context` / `wrap_socket`) to a `_from_impl` classmethod so an arbitrary object can no longer be smuggled into `_impl`.

### 134. `MPQueue.put` of any POOP value poisons the queue — `get()` deadlocks

- **Where:** `poop/types/multiprocessing.py:83-99` (`MPQueue.put` / `get`)
- **Bug:** `put` hands the POOP wrapper to `multiprocessing.Queue` unchanged. The feeder thread then fails to pickle it (wrappers patch `__module__ = "builtins"`/`__name__`, so by-name lookup fails: `Can't pickle <class 'int'>: it's not found as builtins.Int`), the error is printed asynchronously on stderr, the item never reaches the pipe, and a plain `get()` blocks forever — the program hangs. With a timeout, the user gets `poop: ` with an empty message (`queue.Empty` has no text). CPython's `q.put(1); q.get()` answers `1`. The sibling `pickle` wrapper already solves exactly this with `to_python`/`to_poop` at the boundary.
- **Repro:**

  ```python
  q = MPQueue()
  q.put(1)
  q.get().print()
  # stderr: _pickle.PicklingError: Can't pickle <class 'int'>: it's not found as builtins.Int
  # ... then hangs forever (with get(timeout=3): "poop: " with empty message)
  ```

- **Proposed fix:** bridge at the boundary like `poop/types/pickle.py` does — `self._impl.put(to_python(item), b, ...)` in `put`/`put_nowait`, and `return to_poop(self._impl.get(...))` in `get`/`get_nowait`.

### 135. `dict(a=1, b=2)` rejects the keyword constructor form

- **Where:** `poop/transformers/_collection.py:31-47` (`CollectionRewriter.visit_Call` skips calls with keywords), `poop/transformers/dict.py:23-40` (`_poop_dict_from` takes a single positional)
- **Bug:** `dict(key=value, ...)` — a core CPython constructor form — is not routed through the dict factory: `visit_Call` bails out on keywords, `visit_Name` then renames `dict` to the bare `Dict` class, and `Dict.__init__()` (which takes nothing) raises `TypeError: Dict.__init__() got an unexpected keyword argument 'a'`. The documented contract is "constructor builtins are intercepted, not banned"; `dict()`, `dict(d)` and `dict(pairs)` all work — only the kwargs form crashes.
- **Repro:**

  ```python
  dict(a=1, b=2).print()
  # poop: Dict.__init__() got an unexpected keyword argument 'a'
  # Python: {'a': 1, 'b': 2}
  ```

- **Proposed fix:** in `_DictRewriter`, override `visit_Call` (or relax the shared guard for `dict` only) to also rewrite calls with keywords, forwarding them: `_poop_dict_from(*args, **kwargs)`; extend `_poop_dict_from(arg=None, **kwargs)` to seed from `arg` as today and then `d._data[Str(k)] = v` for each keyword. Other collection rewriters keep the no-keyword guard (their builtins accept none).

### ~~136. `Str.startswith`/`endswith` crash on a tuple of prefixes~~ — DONE

**Decision + implemented:** widened `Str.startswith`/`endswith` (`poop/types/string.py`) to `prefix: Str | Tuple`, unwrapping a `Tuple` into a raw `tuple` of strings (`tuple(str(p) for p in prefix._items)`) before delegating. `"abc".startswith(tuple("a", "z"))` now answers `true` — the message-shaped substitute for the forbidden `startswith(...) or startswith(...)`. Tests in `tests/test_types/test_str.py`.

### ~~137. CLI dumps a raw rich traceback when the source file does not exist~~ — DONE

**Decision + implemented:** wrapped the `file.read_text` call in `poop/cli.py` in `try/except OSError`, emitting `poop: cannot read '<path>': <strerror>` and exiting 1 — keeping the established one-line `poop:` style for missing files, directories, and permission errors instead of leaking a rich traceback. Tests in `tests/test_cli.py`.

### 138. Starred unpacking binds the rest-target to a raw Python `list`

- **Where:** transformer layer — no transformer in `DEFAULT_TRANSFORMERS`
  (`poop/transformers/__init__.py`) visits assignment targets, so
  `c, *rest = xs` reaches `exec` (`poop/executor.py:37`) untouched and
  CPython's `UNPACK_EX` builds the rest-collection as a native `list`.
  (`poop/validators/no_namespace_shadow.py:18` already walks `ast.Starred`
  targets, so the syntax is reachable and anticipated.)
- **Leak:** the starred name binds a raw `builtins.list` (its elements are
  POOP values, the container is not). Every POOP message on it crashes; the
  source type does not matter — `List`, `Tuple`, and `Str` right-hand sides
  all leak, including nested targets like `a, (b, *inner) = ...`.
- **Evidence:** e2e (`uv run python main.py /tmp/poop_star.py`):

  ```python
  c, *rest = [1, 2, 3]
  c.print()       # 1 — plain targets are fine
  rest.print()    # poop: 'list' object has no attribute 'print' (line 3)
  ```

  Direct probe through `Interpreter.transform_source` + `exec`:
  `rest.__class__ is [].__class__` → `True` (raw list), while
  `all(isinstance(e, Int) for e in rest)` → `True` and the plain target `c`
  is a POOP `Int`. Same result for `a, *b = (1, 2, 3)` and
  `first, *others = "xyz"`.
- **Proposed fix:** add an `unpack` transformer whose `visit_Assign` (and
  `visit_AnnAssign` is irrelevant — annotated targets cannot be starred)
  detects `ast.Starred` anywhere in the target tree and appends one rebind
  statement per starred name after the assignment, e.g.
  `c, *rest = xs` → `c, *rest = xs; rest = _poop_list_from(rest)` (the
  binding already exists: `_poop_list_from` in `poop/transformers/list.py:14`
  accepts any iterable of POOP elements). For attribute/starred targets like
  `a, *self.rest = xs`, emit the equivalent
  `self.rest = _poop_list_from(self.rest)`. `visit_Assign` may return a
  statement list, so the expansion is a plain `NodeTransformer`.

### 139. `*args` / `**kwargs` parameters bind a raw `tuple` / raw `dict` (with raw `str` keys)

- **Where:** transformer layer — `poop/transformers/class_.py:9` rewrites
  only `ClassDef` bases; method signatures are untouched, so CPython's call
  machinery packs variadic parameters natively inside `exec`
  (`poop/executor.py:37`). `poop/validators/no_namespace_shadow.py` already
  validates `vararg`/`kwarg` names, so the syntax is sanctioned.
- **Leak:** inside a user method `def m(self, *args, **kw):`, `args` is a
  raw `builtins.tuple` and `kw` a raw `builtins.dict` whose keys are raw
  `str` (the values are POOP — they come from the transformed call site).
  Every POOP message on either container crashes.
- **Evidence:** e2e (`uv run python main.py /tmp/poop_varargs.py`):

  ```python
  class Calc:
      def total(self, *args):
          args.print()

  Calc().total(1, 2, 3)
  # poop: 'tuple' object has no attribute 'print' (line 3)
  ```

  Same for `**opts`: `poop: 'dict' object has no attribute 'print'`.
  Identity probe: `o.a.__class__ is (1,).__class__` → `True`,
  `o.k.__class__ is {}.__class__` → `True`, and every key satisfies
  `k.__class__ is "".__class__`.
- **Proposed fix:** in a signature transformer (same pass as the fix above,
  or a sibling), for every `FunctionDef`/`AsyncFunctionDef` with
  `args.vararg`/`args.kwarg`, inject a prologue as the first body
  statements: `args = _poop_tuple_from(args)` and
  `kw = _poop_dict_from_kwargs(kw)` — `_poop_tuple_from` already exists
  (`poop/transformers/tuple.py`); add a tiny `_poop_dict_from_kwargs(d)`
  binding that builds a `Dict` mapping `Str(k) → v`. Lambdas with variadic
  parameters need the nested-lambda form
  (`lambda *xs: body` → `lambda *xs: (lambda xs: body)(_poop_tuple_from(xs))`)
  since a prologue cannot be inserted into an expression body.

### 140. User methods without an explicit `return` answer raw Python `None`, not POOP `none`

- **Where:** transformer layer — nothing rewrites function bodies
  (`poop/transformers/class_.py` touches only class bases), so a method that
  falls off the end or uses a bare `return` answers CPython's implicit
  `None` inside `exec` (`poop/executor.py:37`). The `none` transformer
  (`poop/transformers/none.py`) only rewrites the `None` *literal*; the
  implicit return has no AST node to rewrite.
- **Leak:** the single most common method shape — a side-effecting method
  with no `return` — hands raw `NoneType` to its caller. `result.is_none()`,
  `result.print()`, `result.if_none(...)` all crash, even though POOP's own
  wrappers scrupulously return the `none` singleton from every void method.
- **Evidence:** e2e (`uv run python main.py /tmp/poop_implicit_none.py`):

  ```python
  class Greeter:
      def greet(self):
          "hi".print()

  r = Greeter().greet()
  r.is_none().print()
  # poop: 'NoneType' object has no attribute 'is_none' (line 6)
  ```

  A bare `return` leaks identically.
- **Proposed fix:** add a `return_` transformer that, for every
  `FunctionDef`/`AsyncFunctionDef`: (1) rewrites `return` (no value) to
  `return _poop_none`, and (2) appends `return _poop_none` when the last
  body statement is not a `Return`/`Raise` (an unreachable trailing return
  is harmless otherwise). The `_poop_none` binding already exists
  (`poop/transformers/none.py:17`). Must skip `__init__` — CPython raises
  `TypeError: __init__() should return None` for non-`None` returns;
  generators cannot occur (`no_yield`), so the rewrite is otherwise safe.

### 141. `import` statements pass validation and bind raw Python modules — shadowing injected namespaces

- **Where:** `poop/validators/__init__.py:66` (`DEFAULT_VALIDATORS` has no
  validator for `ast.Import`/`ast.ImportFrom`), and
  `poop/validators/no_namespace_shadow.py:6` (`_Visitor` checks
  `Assign`/`AnnAssign`/`AugAssign`/`ClassDef`/parameters but not import
  aliases, so even rebinding a protected namespace name via `import` slips
  through).
- **Leak:** `import os` binds the raw CPython module *over* POOP's injected
  `os` namespace, and every call on it returns raw Python values —
  the entire wrapper layer is bypassed in one line. `from os import getcwd`
  and `import json as j` leak the same way. MIGRATION.md's design statement
  ("No `import math` needed in POOP — the namespace is injected globally")
  and the import-free `examples/` tree show imports were never meant to be
  part of the language; they are simply unvalidated.
- **Evidence:** e2e (`uv run python main.py /tmp/poop_import_os.py`):

  ```python
  import os
  cwd = os.getcwd()
  cwd.print()
  # poop: 'str' object has no attribute 'print' (line 3)
  ```

  `from os import getcwd` produces the same raw `str`. Direct probe:
  after `import os`, `type(ns["os"])` is `<class 'module'>` and
  `os.getcwd()` returns a raw `str`. (`__import__("json")` is already
  unusable — POOP `Str` is not accepted as a module name — so the statement
  form is the only open door.)
- **Proposed fix:** add a `no_import` validator rejecting `ast.Import` and
  `ast.ImportFrom` with a message that names the substitute, e.g.
  `"import is forbidden — POOP injects its stdlib namespaces (math, os,
  json, …); the names are already in scope"`, and register it in
  `DEFAULT_VALIDATORS`. As defense-in-depth, `no_namespace_shadow` can also
  gain `visit_Import`/`visit_ImportFrom` over `alias.asname or alias.name`,
  but with `no_import` active that branch is unreachable.

### 142. `{**a, ...}` dict-literal splat (and `f(**kw)`) crash — POOP `Dict` cannot be used as a `**`-unpacking mapping

- **Where:** `poop/types/dict.py` (the `Dict` class exposes `at`/`keys`/`values`
  but no `__getitem__`, so it does not satisfy the mapping protocol Python's
  `**` unpacking needs), and `poop/transformers/dict.py:50-53` (the dict
  rewriter *bails out* — `return node` — whenever a display contains a `**`
  entry, leaving the raw Python `ast.Dict` in place to be merged at runtime by
  `dict.update`-style logic that the POOP `Dict` cannot service).
- **Bug:** A dict display with `**` unpacking (`{**a, "y": 2}`, `{**a, **b}`)
  crashes with `'dict' object is not subscriptable`, and so does a call-site
  keyword splat `f(**kw)` when `kw` is a POOP `Dict`. Python's `**` merge calls
  `kw.keys()` (which works — `keys()` exists) and then subscripts `kw[k]`, but
  `Dict` has no `__getitem__`, so the subscription raises. Both are the *natural*
  POOP translations of everyday Python: there is no other literal way to splice
  one dict into another, and `f(*args)` (positional splat) already works, so the
  asymmetry is surprising.
- **Repro** (`uv run python main.py file.py`):

  ```python
  a = {"x": 1}
  b = {**a, "y": 2}        # poop: 'dict' object is not subscriptable (line 2)
  ```

  ```python
  class Adder:
      def add(self, a, b):
          return a + b
  kw = {"a": 1, "b": 2}
  Adder().add(**kw).print() # poop: 'dict' object is not subscriptable
  ```

  By contrast `[*a, *b]`, `(*a, 3)`, `{*a, *b}` and `f(*list)` all work, because
  iteration (not the mapping protocol) is all they need.
- **Proposed fix:** stop bailing in `_DictRewriter.visit_Dict` — instead of
  `return node` when a `**` entry is present, rewrite the display into a POOP
  merge helper (e.g. `_poop_dict_merge(<entry>, ...)`, where each plain pair
  becomes a one-key `_poop_dict_from_pairs(...)` and each `**x` stays as `x`),
  building a real POOP `Dict` and keeping POOP semantics for keys/values. For the
  call-site `f(**kw)` path (which the transformer cannot reach), give `Dict` a
  `__getitem__` delegating to `self._data[key]` so it satisfies the mapping
  protocol; note that kwargs additionally require Python-`str` keys, so a fully
  correct `f(**kw)` also needs `keys()` to yield raw `str` for that one path
  (or a documented restriction that `**`-splatting a POOP `Dict` into a call is
  unsupported). The dict-literal fix is the high-value, self-contained one.

### 143. Open-ended slice `obj.slice(start, None)` crashes on every sliceable type

- **Where:** the `slice` method of `poop/types/string.py:53`,
  `poop/types/list.py:43`, `poop/types/tuple.py:42`, `poop/types/bytes.py:46`,
  `poop/types/byte_array.py:49`, `poop/types/array.py:107`, and
  `poop/types/range.py:54`. Each ends with
  `s = step._value if step is not None else None` and
  `self._value[start_or_slice._value : stop._value : s]`.
- **Bug:** A `None` literal in POOP source is rewritten to the POOP `none`
  (`NoneClass`, whose `__name__` is set to `"NoneType"`), **not** Python's
  `None`. The `slice` methods guard with `if stop is None:` (a Python-identity
  check that POOP `none` never satisfies) and then read `stop._value` /
  `step._value` directly — but `NoneClass` has no `_value`, so any
  `obj.slice(start, None)` or `obj.slice(start, stop, None)` raises
  `'NoneType' object has no attribute '_value'`. This is the natural translation
  of Python's `obj[start:]` / open-ended slices, and the `no_subscript`
  validator explicitly directs users to `obj.slice(start, stop)`. There is no
  way to express "to the end" through the 3-arg form (omitting `stop` hits the
  `"stop is required when start is an Int"` guard instead). The `Slice`
  constructor *does* handle this — `poop/types/slice.py:_coerce` accepts both
  Python `None` and `NoneClass` — so only `obj.slice(slice(start, None))` works,
  which is awkward and undocumented.
- **Repro** (`uv run python main.py file.py`):

  ```python
  "hello".slice(2, None).print()        # poop: 'NoneType' object has no attribute '_value'
  [1, 2, 3, 4, 5].slice(1, None).print()
  range(0, 10).slice(2, None).print()
  (1, 2, 3, 4).slice(1, None).print()
  b"abcdef".slice(2, None).print()
  # all crash identically; only obj.slice(slice(2, None)) works
  ```

- **Proposed fix:** in each `slice` method coerce a POOP `none` argument the same
  way `Slice._coerce` does — treat both Python `None` and `NoneClass` as
  "absent". The smallest robust change is to route the 3-arg form through the
  existing `Slice` helper, e.g. build
  `Slice(start_or_slice, stop, step)._py_slice()` and index with it, so the
  single coercion site in `poop/types/slice.py` handles `None`/`NoneClass`/`Int`
  uniformly for every type. (The current `if stop is None` Int-required guard can
  then be dropped, since an absent/`none` stop becomes a valid open-ended slice.)

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

### 145. Rebinding (or passing) a forbidden builtin bypasses every call-name validator — raw `int`/`list`/class objects flow out

- **Where:** `poop/validators/_call_name.py:24` — the `_Visitor` produced by
  `make_call_name_validator` only rejects `ast.Call` nodes whose `func` is an
  `ast.Name`. A bare `ast.Name` reference to a forbidden builtin in any other
  position — assignment RHS, call argument, decorator, default value — passes
  all 39 validators built by the factory, and the executor's namespace
  (`poop/executor.py:37`, `exec` with implicit `__builtins__`) resolves it to
  the raw CPython builtin.
- **Leak:** one assignment reopens every blocked door: `f = len; f(xs)`
  answers a raw `int` (wrappers expose `__len__` for protocol interop),
  `srt = sorted; srt(xs)` answers a raw Python `list`, `t = type; t(x)`
  answers the raw class object. Argument position needs no assignment at
  all: `words.map(len)` yields raw `int` elements. Same shape as the
  `import` door (an unvalidated statement binding raw Python objects), but
  through names the validators were specifically built to block.
- **Evidence:** e2e (`uv run python main.py ...`):

  ```python
  f = len
  n = f([1, 2, 3])
  n.print()
  # poop: 'int' object has no attribute 'print' (line 3)
  ```

  `srt = sorted; srt([3, 1, 2]).print()` → `poop: 'list' object has no
  attribute 'print'`; `t = type; t(5).print()` → `poop: Object.print()
  missing 1 required positional argument: 'self'` (the raw class leaked, so
  `.print` is an unbound method); `["ab", "abc"].map(len).next().print()` →
  `poop: 'int' object has no attribute 'print'`. Not every alias leaks —
  `h = hex; h(255)` crashes because `Int` lacks `__index__` — but every
  blocked builtin satisfied by a wrapper dunder (`len`, `sorted`, `type`,
  `id`, `hash`, `isinstance`, ...) does.
- **Proposed fix:** in `make_call_name_validator`, replace `visit_Call` with
  a `visit_Name` that rejects any reference to a forbidden name regardless
  of context (Load, Store, decorator, argument), reusing the same message
  template. Method substitutes are unaffected — `n.hex()` / `xs.len()` are
  `ast.Attribute` nodes, and keyword-argument names are not `Name` nodes.
  Trade-off to state in the message: the 39 forbidden names become fully
  reserved identifiers (`len = 5` is rejected too), which matches the spirit
  of `no_namespace_shadow`. Structural validators not built by the factory
  (`no_subscript`, `no_if`, ...) need no change.

### 146. Binding a lowercase builtin name (`int = 5`, `def __init__(self, dict)`) silently rebinds the interpreter's mangled internals

- **Where:** every type transformer's `visit_Name` rewrites with `ctx=node.ctx` — Store and parameter-body loads included: `poop/transformers/int.py:73-75`, `float.py:64-66`, `string.py:52-54`, `boolean.py:35-37`, `bytes.py:58-60`, `byte_array.py:43-45`, `memory_view.py:39-41`, `complex.py:96-98`, `range.py:38-40`, `enumerate.py:30-33`, `zip.py:36-38`, and `_collection.py:49-52` (shared by `list`/`tuple`/`set`/`dict`/`frozen_set`). No validator covers these 16 names — `no_namespace_shadow` protects only `DEFAULT_NAMESPACE` bindings (`math = 5` is rejected; `int = 5` is not), and the entry-145 call-name validators don't include the rewritten type names at all.
- **Bug:** the rewrite is context-blind, so a user binding of `bool`/`int`/`float`/`complex`/`str`/`bytes`/`bytearray`/`memoryview`/`list`/`tuple`/`dict`/`set`/`frozenset`/`range`/`enumerate`/`zip` becomes a binding of the mangled `_poop_*` global. Three flavors, all legal Python:
  1. module-scope assignment to a name whose rewrite target is also the literal constructor (`int`, `float`, `str`, `bytes`) replaces the constructor itself, so **every later literal of that type crashes**;
  2. function-scope assignment compiles to `_poop_str = _poop_str("hello")`, an `UnboundLocalError` that leaks the mangled name in the diagnostic;
  3. a `def`/lambda parameter keeps its name while body loads rewrite to the mangled global, so the body silently operates on the internal class instead of the argument.
- **Repro:**

  ```python
  str = "hello"
  "world".print()
  # poop: 'str' object is not callable   (Python: prints world)
  ```

  ```python
  int = 5
  x = 3
  # poop: 'int' object is not callable   (Python: x == 3)
  ```

  ```python
  class App:
      def run(self):
          str = "hello"
          return str
  App().run()
  # poop: cannot access local variable '_poop_str' where it is not associated with a value
  ```

  ```python
  class Tag:
      def __init__(self, dict):
          self._d = dict
      def get(self, k):
          return self._d.get(k)
  Tag({"a": 1}).get("a").print()
  # poop: Dict.get() missing 1 required positional argument: 'key'
  # (self._d silently bound the internal Dict class, not the argument; Python: prints 1)
  ```

- **Proposed fix:** make the 16 rewritten builtin names reserved identifiers, mirroring how `no_namespace_shadow` already treats namespace bindings: extend that validator (or add a sibling `no_builtin_shadow`) with the fixed name set, rejecting assignment targets, class names, and `def`/lambda parameters with a message like `'int' is a POOP builtin name; it cannot be rebound`. This is the same "reserved identifier" direction entry 145 proposes for the call-name validators, and it turns all three silent-corruption flavors into a clear parse-time diagnostic. (Scope-aware rewriting would preserve Python's shadowing semantics but costs a symbol table; rejection matches POOP's existing posture.)

### 147. sqlite3 named-placeholder parameters (`:name` + dict) are rejected — "parameters are of unsupported type"

- **Where:** `poop/types/sqlite3.py:26-33` (`_unwrap_params`) — used by both `Connection.execute`/`executemany` (`poop/types/sqlite3.py:212-223`) and `Cursor.execute`/`executemany` (`poop/types/sqlite3.py:129-141`)
- **Bug:** `_unwrap_params` converts only `Tuple | List` sequences; any other value (notably a POOP `Dict`) is passed through raw, and the underlying `sqlite3` rejects the wrapper with `ProgrammingError: parameters are of unsupported type`. CPython documents named placeholders with a dict as one of the two first-class parameter styles, and the qmark style next to it works fine, so the failure looks like a SQL error rather than a wrapper gap. The annotations (`params: Tuple | List | NoneClass`) likewise exclude the mapping form.
- **Repro:**

  ```python
  conn = sqlite3.connect(":memory:")
  conn.execute("CREATE TABLE t (id INTEGER, name TEXT)")
  conn.execute("INSERT INTO t VALUES (?, ?)", (1, "alice"))         # qmark style: OK
  conn.execute("SELECT name FROM t WHERE id = :id", {"id": 1})
  # poop: parameters are of unsupported type        (Python: ('alice',))
  conn.executemany("INSERT INTO t VALUES (:id, :name)", [{"id": 2, "name": "b"}])
  # poop: parameters are of unsupported type        (Python: inserts the row)
  ```

- **Proposed fix:** add a `Dict` branch to `_unwrap_params` — `if isinstance(params, Dict): return to_python(params)` (the module already imports `to_python`, which deep-converts `Dict` via `_data`) — and widen the `params` annotations on all four execute methods to `Tuple | List | Dict | NoneClass`.

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

### 153. Lambda parameters bypass `no_namespace_shadow` — `def m(self, math)` is rejected, `lambda math: ...` is accepted

- **Where:** `poop/validators/no_namespace_shadow.py:46-66` (`_check_args` is called from `visit_FunctionDef` / `visit_AsyncFunctionDef` only; the visitor has no `visit_Lambda`)
- **Bug:** the validator's own comment spells out the hazard — "a parameter named after a namespace binding shadows it inside the body … fails in confusing ways" — and rejects the `def` form, but every lambda slips through with the exact same hazard. Since lambdas are POOP's block form (wrapped into `Block` by the block transformer) and carry most user code, the unchecked form is the *more* common one. Distinct from entry 146 (rewritten builtin names like `dict` as parameters — a transformer corruption) and entry 141 (imports): this is the namespace-binding validator missing one binding form it was built to police.
- **Repro:**

  ```python
  f = lambda math: math.sqrt(2)
  f(4).print()
  # poop: 'int' object has no attribute 'sqrt' (line 1)
  # while the def spelling is caught at validation time:
  #   def m(self, math): ...
  #   poop: 'math' is a POOP namespace binding; reassigning it shadows the runtime entry point
  ```

- **Proposed fix:** add to `_Visitor`:

  ```python
  def visit_Lambda(self, node: ast.Lambda) -> None:
      self._check_args(node.args)
      self.generic_visit(node)
  ```

### 154. `int(True)` / `float(True)` reject Boolean — and the diagnostic leaks the internal `_TrueClass` name

- **Where:** `poop/transformers/int.py:10-23` (`_poop_int_from` accepts `Int | Float | Str` only; the error message uses `type(value).__qualname__`), `poop/transformers/float.py:19` (`_poop_float_from`, same pattern)
- **Bug:** CPython's `int(True)` → `1`, `float(False)` → `0.0` — the canonical flag-to-number bridge. POOP's conversion factories have no Boolean branch, so the conversion crashes; and because the identity masking rebinds only `__name__` (booleans answer `bool` per v1.7.1), the `__qualname__`-based message exposes internals: `cannot convert _TrueClass to Int` — both `_TrueClass` and `Int` are names users should never see. POOP deliberately keeps Boolean out of *implicit* arithmetic (see the design note in `poop/validators/no_unary_minus.py`), but explicit conversion is the sanctioned bridge — `str(True)` already answers `"True"`.
- **Repro:**

  ```python
  int(True).print()
  # poop: cannot convert _TrueClass to Int   (Python: 1)
  x = True
  float(x).print()
  # poop: cannot convert _TrueClass to Float   (Python: 1.0)
  ```

- **Proposed fix:** add a Boolean branch to both factories — `if isinstance(value, Boolean): return Int(1 if bool(value) else 0)` (resp. `Float(1.0 ... 0.0)`); independently of that decision, build the error with `type(value).__name__` so the masked public names (`bool`, `int`, `float`) appear in diagnostics instead of internal class names.

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
