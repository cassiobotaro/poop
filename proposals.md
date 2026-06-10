# Proposals

### 115. `Int`/`Float` arithmetic raises `AttributeError` instead of returning `NotImplemented`, killing every reflected dunder

- **Where:** `poop/types/int.py:93-138` (`Int.__add__` / `__sub__` / `__mul__` / `__truediv__` / `__floordiv__` / `__mod__`), `poop/types/float.py:73-97` (same methods on `Float`)
- **Bug:** the binary operators special-case `Complex` (returning `NotImplemented`) but for any other non-`Int`/`Float` operand they fall through to `other._value`, raising `AttributeError`. Python therefore never gets the chance to try the right operand's reflected dunder, so `Fraction.__radd__`, `NormalDist.__rmul__`, etc. — which the wrappers carefully define — are unreachable. The same expressions with the operands swapped work fine.
- **Repro:**

  ```python
  (Fraction(1, 2) + 2).print()      # 5/2 — OK
  (2 + Fraction(1, 2)).print()      # poop: 'Fraction' object has no attribute '_value'
  (2.5 + Fraction(1, 2)).print()    # poop: 'Fraction' object has no attribute '_value'
  (2 * NormalDist(0.0, 1.0)).print()  # poop: 'NormalDist' object has no attribute '_value'
  ```

  Real Python: `2 + Fraction(1, 2)` → `Fraction(5, 2)`, `2 * NormalDist(0.0, 1.0)` → `NormalDist(mu=0.0, sigma=2.0)`.
- **Proposed fix:** in every `Int`/`Float` binary operator, return `NotImplemented` when the operand is not one of the known numeric wrappers, e.g.:

  ```python
  def __add__(self, other: Int | Float | Complex) -> Int | Float:
      if isinstance(other, Complex):
          return NotImplemented
      if not isinstance(other, Int | Float):
          return NotImplemented          # let other.__radd__ run
      ...
  ```

### 116. `TimeDelta + Date` answers a corrupted `TimeDelta` wrapping a `datetime.date`

- **Where:** `poop/types/datetime.py:68-72` (`TimeDelta.__add__` / `__sub__`), also `poop/types/datetime.py:74` (`TimeDelta.__mul__` has no `__rmul__` counterpart)
- **Bug:** `TimeDelta.__add__` is typed `other: TimeDelta` but never checks; it computes `self._impl + other._impl` and unconditionally wraps the result with `TimeDelta._from_impl`. With a `Date`/`DateTime` right operand the stdlib returns a `date`/`datetime`, which gets stuffed inside a `TimeDelta` shell — `class_name()` answers `TimeDelta` but every accessor explodes. Real Python answers a `date`. Relatedly, `2 * TimeDelta(days=1)` (valid in Python, `timedelta` defines `__rmul__`) crashes because `TimeDelta` has no `__rmul__`.
- **Repro:**

  ```python
  r = TimeDelta(days=1) + Date(2024, 1, 1)
  r.class_name().print()   # TimeDelta  (Python: date 2024-01-02)
  r.days.print()           # poop: 'datetime.date' object has no attribute 'days'

  (2 * TimeDelta(days=1)).days.print()
  # poop: 'TimeDelta' object has no attribute '_value'  (Python: 2)
  ```

- **Proposed fix:** in `TimeDelta.__add__`/`__sub__`, `isinstance`-check the operand: return `Date._from_impl(...)`/`DateTime._from_impl(...)` for date-like operands (or return `NotImplemented` and rely on `Date.__radd__`); add `__rmul__ = __mul__` (and `__radd__` for `Date`/`DateTime` symmetry) so reflected forms work once the `Int`/`Float` operators yield `NotImplemented`.

### 117. `Date`, `Time`, and `TimeDelta` cannot be ordered (`<` crashes)

- **Where:** `poop/types/datetime.py:27` (`TimeDelta`), `poop/types/datetime.py:200` (`Date`), `poop/types/datetime.py:267` (`Time`) — none define `__lt__`/`__le__`/`__gt__`/`__ge__`; only `DateTime` does (`poop/types/datetime.py:446`)
- **Bug:** ordering two dates, times, or durations raises `TypeError`. Real Python orders all of them, and POOP itself orders `DateTime`, `Decimal`, and `Fraction`, so the gap is an oversight, not a design rule.
- **Repro:**

  ```python
  (Date(2024, 1, 1) < Date(2024, 6, 1)).print()
  # poop: '<' not supported between instances of 'Date' and 'Date'
  (TimeDelta(days=1) < TimeDelta(days=2)).print()   # same crash
  (Time(10, 0) < Time(11, 0)).print()               # same crash
  ```

  Real Python: all three answer `True`.
- **Proposed fix:** add the four comparison dunders to `Date`, `Time`, and `TimeDelta`, mirroring the existing `DateTime` block (`to_boolean(self._impl < other._impl)`, etc.) — ideally via a tiny shared mixin in `datetime.py`.

### 118. `replace(tzinfo=None)` cannot strip a timezone — aware values can never become naive

- **Where:** `poop/types/datetime.py:315-318` (`Time.replace`), `poop/types/datetime.py:429-432` (`DateTime.replace`)
- **Bug:** both `replace` implementations treat an explicit `tzinfo=None` the same as "argument absent" and keep `self._impl.tzinfo`. In real Python, `dt.replace(tzinfo=None)` is *the* idiom to drop the timezone; in POOP there is no way at all to turn an aware `DateTime`/`Time` into a naive one.
- **Repro:**

  ```python
  aware = DateTime(2024, 1, 1, 12, tzinfo=TimeZone.utc)
  aware.replace(tzinfo=None).tzinfo.is_none().print()   # False
  Time(10, 0, tzinfo=TimeZone.utc).replace(tzinfo=None).tzinfo.is_none().print()  # False
  ```

  Real Python: `aware.replace(tzinfo=None).tzinfo is None` → `True`.
- **Proposed fix:** use a module-level `_ABSENT = object()` sentinel as the `tzinfo` default in both `replace` signatures so the three cases are distinguishable: absent → keep current tzinfo, POOP `none` → pass `tzinfo=None` (strip), wrapper → pass `tzinfo._impl`.

### 119. `Fraction == Int` answers `false` while `Fraction >= Int` answers `true`

- **Where:** `poop/types/fractions.py:45` (`_eq_attr` via `_ValueEqMixin`) vs `poop/types/fractions.py:168` (`_cmp`)
- **Bug:** `Fraction` inherits `_ValueEqMixin.__eq__`, which only matches operands of the same class, so equality against `Int`/`Float` is always `false` — yet the class's own `_cmp` (used by `<`, `<=`, `>`, `>=`) and `_combine` (arithmetic) deliberately accept `Int` and `Float`. The result is internally inconsistent: `f >= 2` and `f <= 2` are both `true` while `f == 2` is `false`. Real Python: `Fraction(2) == 2` → `True`.
- **Repro:**

  ```python
  f = Fraction(2)
  (f >= 2).print()   # True
  (f == 2).print()   # False  (Python: True)
  (f != 2).print()   # True   (Python: False)
  ```

- **Proposed fix:** override `__eq__`/`__ne__` on `Fraction` with the `_cmp` dispatch (`Fraction`/`Int` compare against `self._impl`, `Float` against `float(self._impl)`), falling back to `false`/`true` for foreign types as today.

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

### 121. Documented `.do(...)` recipes crash: `GlobIter`, `csv.Reader`/`DictReader`, and `Shlex` lack the iteration surface

- **Where:** `poop/types/glob.py:16` (`GlobIter`), `poop/types/csv.py:53` (`Reader`), `poop/types/csv.py:118` (`DictReader`), `poop/types/shlex.py:12` (`Shlex`)
- **Bug:** all four classes define `__iter__` but do not mix in `_IterableMixin` (nor define `do`/`map`/`filter`). Since loops are forbidden, a bare `__iter__` is unreachable from user code except through the `list()`/`tuple()` converters. MIGRATION.md explicitly shows `glob.iglob("*.txt").do(lambda f: process(f))` (line 629), `lexer.do(lambda token: handle(token))` (line 841), and `csv.reader(text).do(Block(lambda row: row.print()))` (line 1614), and `GlobIter`'s own docstring promises "yields POOP `Path` objects on each `do(block)` call" — every one of those crashes.
- **Repro:**

  ```python
  glob.iglob("*.py").do(lambda f: f.print())
  # poop: 'GlobIter' object has no attribute 'do'
  csv.reader("a,b\r\n1,2\r\n").do(lambda row: row.print())
  # poop: 'Reader' object has no attribute 'do'
  Shlex("a b c").do(lambda token: token.print())
  # poop: 'Shlex' object has no attribute 'do'
  ```

- **Proposed fix:** add `_IterableMixin` to the bases of `GlobIter`, `Reader`, `DictReader`, and `Shlex` (their existing `__iter__` already yields POOP values, which is all the mixin needs).

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

### 125. REPL echoes `None` after every `.print()` (and clobbers `_`)

- **Where:** `poop/repl.py:356-360` (`Repl._displayhook`)
- **Bug:** the displayhook suppresses only the raw Python `None` (`if value is None: return`). Every POOP message that answers `none` — including `.print()`, the single most common REPL expression — returns a `NoneClass`, which gets displayed as `None` and stored into `_`. CPython's REPL displays nothing for `None`-valued expressions (`>>> print("hi")` shows only `hi`) and leaves `_` untouched.
- **Repro:**

  ```text
  >>> "hi".print()
  hi
  None
  ```

  Expected (CPython behavior): just `hi`.
- **Proposed fix:** suppress `NoneClass` results in `_displayhook`:

  ```python
  def _displayhook(self, value: object) -> None:
      if value is None or isinstance(value, NoneClass):
          return
      ...
  ```

  (The `NoneClass` branch in `_colorize_value` then becomes dead and can go.)

### 126. The datetime family prints `<Date>` instead of its value

- **Where:** `poop/types/datetime.py` — `TimeDelta` (27), `TimeZone` (97), `Date` (200), `Time` (267), `DateTime` (325); none define `__str__`/`__repr__`
- **Bug:** all five wrappers fall back to `Object.__str__`, so `.print()` and the REPL show `<Date>`, `<TimeDelta>`, etc. Every sibling value wrapper (`Decimal`, `Fraction`, `UUID`, the `ipaddress` family) delegates `__str__` to its `_impl`, and real Python prints `2024-01-01` / `1 day, 2:00:00`.
- **Repro:**

  ```python
  Date(2024, 1, 1).print()          # <Date>      (Python: 2024-01-01)
  TimeDelta(days=1, hours=2).print()  # <TimeDelta> (Python: 1 day, 2:00:00)
  DateTime(2024, 1, 1).print()      # <DateTime>  (Python: 2024-01-01 00:00:00)
  ```

- **Proposed fix:** add to each of the five classes (or to a tiny shared mixin):

  ```python
  def __str__(self) -> str:
      return str(self._impl)

  __repr__ = __str__
  ```

### 127. asyncio `Future.exception()` answers the raw Python exception

- **Where:** `poop/types/asyncio.py:46`
- **Leak:** `Future.exception()` returns `to_poop(self._impl.exception())`, and
  `to_poop` has no branch for `BaseException` — the raw Python exception
  instance falls through to user space. This is inconsistent with the
  surrounding design: `asyncio.gather` (same file, line 89) wraps exceptions as
  `Error` precisely to "mirror what Try hands to handlers", and `Try.except_`
  handlers receive `Error`. A task's failure inspected via `.exception()` is
  the one asyncio path that still hands back the naked exception, so
  `.message()` / `.kind()` / `.class_name()` all blow up on it.
- **Evidence:** e2e POOP program (`uv run python main.py /tmp/poop_aio_leak.py`):

  ```python
  class App:
      async def boom(self):
          ValueError.raise_("nope")

      async def main(self):
          t = asyncio.create_task(self.boom())
          await asyncio.sleep(0.01)
          return t.exception()


  e = asyncio.run(App().main())
  e.class_name().print()
  ```

  Output: `poop: 'ValueError' object has no attribute 'class_name' (line 12)`.
  Direct probe confirms `type(t.exception())` is `<class 'ValueError'>`, not
  `Error`.
- **Proposed fix:** mirror the gather contract — `none` when there is no
  exception, `Error` otherwise:

  ```python
  def exception(self) -> Object:
      result = self._impl.exception()
      return none if result is None else Error(result)
  ```

  (`Error` is already imported in `poop/types/asyncio.py` for gather.)

### 128. concurrent `CFFuture.exception()` answers the raw Python exception

- **Where:** `poop/types/concurrent.py:30`
- **Leak:** same pattern as the asyncio twin: `CFFuture.exception(timeout)`
  returns `none if result is None else to_poop(result)`, and `to_poop` passes
  `BaseException` instances through raw. A failed `executor.submit(...)`
  future hands the naked Python exception to user code instead of `Error`.
- **Evidence:** e2e POOP program (`uv run python main.py /tmp/poop_cf_leak.py`):

  ```python
  ex = ThreadPoolExecutor()
  f = ex.submit(lambda: ValueError.raise_("kaput"))
  e = f.exception()
  e.class_name().print()
  ```

  Output: `poop: 'ValueError' object has no attribute 'class_name' (line 4)`.
  Direct probe confirms `type(f.exception())` is `<class 'ValueError'>`.
- **Proposed fix:**

  ```python
  def exception(self, timeout: Float | Int | None = None) -> Object:
      result = self._impl.exception(_opt_timeout(timeout))
      return none if result is None else Error(result)
  ```

  (import `Error` from `poop.types.error`; the `to_poop` local import and
  its `none`-check dance go away.)

### 129. `statistics` central-tendency functions leak raw `fractions.Fraction`

- **Where:** `poop/types/statistics.py:164` (`mean`), `:192` (`median`),
  `:196` (`median_low`), `:200` (`median_high`), `:215` (`mode`); root cause
  in `_to_number` (`:19`), which unwraps POOP `Fraction` to its raw
  `fractions.Fraction` impl.
- **Leak:** `_unwrap_data` converts POOP `Fraction` elements to raw
  `fractions.Fraction` so the stdlib can do exact arithmetic, but the result
  is re-wrapped with `to_poop`, which has no `fractions.Fraction` branch —
  the raw stdlib `Fraction` escapes to user space. Exact-rational data is the
  documented reason CPython's `statistics.mean` supports `Fraction` input, so
  this is a mainline path, not an exotic one. (`Decimal` data does not leak:
  `_to_number` passes the POOP wrapper through, so `median` answers the POOP
  `Decimal`; `mean` over Decimals raises instead — a separate, non-leak bug.)
- **Evidence:** e2e POOP program (`uv run python main.py /tmp/poop_stats_leak.py`):

  ```python
  data = list(Fraction("1/4"), Fraction("1/2"), Fraction("3/4"))
  m = statistics.mean(data)
  m.class_name().print()
  ```

  Output: `poop: 'Fraction' object has no attribute 'class_name' (line 3)`.
  Direct probe: `Statistics.mean(...)`, `Statistics.median(...)`, and
  `Statistics.mode(...)` over POOP Fractions all answer
  `<class 'fractions.Fraction'>`.
- **Proposed fix:** add a local re-wrap helper and use it instead of bare
  `to_poop` in `mean` / `median` / `median_low` / `median_high` / `mode`
  (and for `multimode` elements, which take the same `to_poop` path):

  ```python
  def _wrap_number(value: Any) -> Any:
      if isinstance(value, _fractions.Fraction):
          return Fraction._from_impl(value)
      return to_poop(value)
  ```

  (`poop/types/fractions.py` already exposes `_from_impl` via
  `_ImplWrapperMixin`; `import fractions as _fractions` at top.)

### 130. `statistics` functions crash on `Decimal` data

- **Where:** `poop/types/statistics.py:19-26` (`_to_number`), `poop/types/_bridge.py:56-84` (`to_poop` has no `decimal.Decimal` branch)
- **Bug:** `_to_number` unwraps `Int`/`Float`/`Str`/`Fraction`/`Boolean` but passes `Decimal` wrappers through untouched, so every `statistics` function that goes through `_unwrap_data` feeds POOP `Decimal` objects to the stdlib. `mean`/`stdev`/`variance` blow up inside `statistics._sum` (the wrapper's `as_integer_ratio()` answers a POOP `Tuple` of `Int`s, which the stdlib then mixes with raw ints), `median` of an even-length dataset crashes averaging the two middle wrappers, and `fmean` rejects the wrapper outright. CPython supports `Decimal` data in all of these.
- **Repro:**

  ```python
  statistics.mean(list(Decimal("1.5"), Decimal("2.5"))).print()
  # poop: unsupported operand type(s) for +: 'int' and 'int'   (Python: 2)
  statistics.stdev(list(Decimal("1"), Decimal("3"))).print()
  # poop: unsupported operand type(s) for +=: 'int' and 'int'  (Python: 1.4142...)
  statistics.median(list(Decimal("1"), Decimal("3"))).print()
  # poop: 'int' object has no attribute '_impl'                (Python: 2)
  statistics.fmean(list(Decimal("1.5"), Decimal("2.5"))).print()
  # poop: must be real number, not Decimal                     (Python: 2.0)
  ```

- **Proposed fix:** add a `Decimal` branch to `_to_number` (`if isinstance(value, Decimal): return value._impl`), and add a `decimal.Decimal` branch to `to_poop` (`return Decimal._from_impl(value)` via a local import to dodge the cycle) so `mean`/`median`/`mode`, which return through `to_poop`, answer a POOP `Decimal` instead of a raw one. `stdev`/`variance`/`pstdev`/`pvariance` wrap results in `Float(...)`; route those through `to_poop` as well so Decimal-in gives Decimal-out, matching CPython.

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

### 136. `Str.startswith`/`endswith` crash on a tuple of prefixes

- **Where:** `poop/types/string.py:197-225` (`Str.startswith` / `Str.endswith`)
- **Bug:** both methods assume the first argument is a single `Str` and dereference `prefix._value`. CPython's contract also accepts a tuple of strings — and in POOP that form matters doubly, because `s.startswith("a") or s.startswith("b")` is forbidden (`no_and_or`), making the tuple form the only message-shaped substitute for the disjunction. Passing a `Tuple` crashes with `AttributeError`.
- **Repro:**

  ```python
  "abc".startswith(tuple("a", "z")).print()
  # poop: 'tuple' object has no attribute '_value'   (Python: True)
  "abc".endswith(tuple("c", "z")).print()
  # poop: 'tuple' object has no attribute '_value'   (Python: True)
  ```

- **Proposed fix:** widen the parameter to `Str | Tuple` and unwrap accordingly: `needle = prefix._value if isinstance(prefix, Str) else tuple(p._value for p in prefix._items)` before calling `self._value.startswith(needle, ...)`; same for `endswith`.

### 137. CLI dumps a raw rich traceback when the source file does not exist

- **Where:** `poop/cli.py:64` (`source = file.read_text(encoding="utf-8")`)
- **Bug:** every pipeline error (syntax, validator, runtime) prints a clean one-line `poop: ...` diagnostic, but an unreadable path escapes the `_poop_errors` guard: `poop missing.py` prints a full rich-formatted `FileNotFoundError` traceback through typer, and `poop somedir/` an `IsADirectoryError` traceback — internal frames (`cli.py`, `pathlib`) exposed for an ordinary user mistake.
- **Repro:**

  ```bash
  uv run python main.py /tmp/nonexistent_file.py
  # ╭─── Traceback (most recent call last) ───╮ ... FileNotFoundError: [Errno 2] ...
  # expected something like: poop: cannot read '/tmp/nonexistent_file.py': No such file or directory
  ```

- **Proposed fix:** either declare the constraint on the argument — `typer.Argument(exists=True, dir_okay=False, readable=True)` — letting typer print its standard short error, or wrap the `read_text` call in `try/except OSError as exc` and `typer.echo(f"poop: cannot read '{file}': {exc.strerror}", err=True)` + `typer.Exit(1)`, keeping the established error style.
