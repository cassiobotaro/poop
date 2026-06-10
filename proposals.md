# Proposals

### 200. `Int`/`Float` arithmetic raises `AttributeError` instead of returning `NotImplemented`, killing every reflected dunder

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

### 201. `TimeDelta + Date` answers a corrupted `TimeDelta` wrapping a `datetime.date`

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

### 202. `Date`, `Time`, and `TimeDelta` cannot be ordered (`<` crashes)

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

### 203. `replace(tzinfo=None)` cannot strip a timezone — aware values can never become naive

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

### 204. `Fraction == Int` answers `false` while `Fraction >= Int` answers `true`

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

### 205. `decimal` precision/rounding can never be changed — the documented `localcontext` recipe is impossible

- **Where:** `poop/types/decimal.py:153-176` (`Context` — `prec` and `rounding` are read-only properties, `__slots__ = ("_impl",)`, constructor takes only a raw `_decimal.Context`), `poop/types/decimal.py:253` (`localcontext`)
- **Bug:** MIGRATION.md tells users to "use `With(lambda: decimal.localcontext()).do(lambda ctx: …)` to scope precision/rounding changes", but the `Context` the body receives exposes no way to change anything: `prec`/`rounding` have no setters, `Context` is not an `Object` (no `set_attr`), and user code cannot construct a `Context` with different settings (the constructor takes a raw CPython context users can't make). Net effect: decimal precision in POOP is permanently stuck at the default.
- **Repro:**

  ```python
  With(lambda: decimal.localcontext()).do(lambda ctx: ctx.set_attr("prec", 5))
  # poop: 'Context' object has no attribute 'set_attr'
  ```

  (Plain attribute assignment is impossible inside the `do` lambda, and no other entry point mutates a context.) Real Python: `with decimal.localcontext() as ctx: ctx.prec = 5` works, as does `decimal.localcontext(prec=5)` on 3.11+.
- **Proposed fix:** mirror CPython 3.11+ kwargs on the namespace entry point — `decimal.localcontext(ctx=none, prec=none, rounding=none)` forwarding via `_kwargs_from` — and/or add `set_prec(Int)` / `set_rounding(Str)` mutator methods to `Context` (same pattern as `SSLContext.set_verify_mode`).

### 206. Documented `.do(...)` recipes crash: `GlobIter`, `csv.Reader`/`DictReader`, and `Shlex` lack the iteration surface

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

### 207. `sqlite3` `Row` is an injected entry point that cannot be used at all

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

### 208. `re.sub`/`subn` reject a lambda replacement with an `AttributeError`

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

### 209. The `Enum` functional API crashes in every form CPython supports

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

### 210. REPL echoes `None` after every `.print()` (and clobbers `_`)

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

### 211. The datetime family prints `<Date>` instead of its value

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
