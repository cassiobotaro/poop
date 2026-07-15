# Migration Recipes — Python → POOP

Quick translations of common Python idioms to POOP source code. For the full reference of which Python constructs are forbidden and why, see [`INFECTIONS.md`](INFECTIONS.md). For end-to-end programs, see [`examples/`](examples).

> Every snippet pair shows the Python form you would normally write and the POOP form the validators and transformers force you to write instead. Snippets are valid as POOP source — primitive literals like `0`, `"hi"`, `True` are wrapped to POOP types by transformers at parse time, so methods like `.at(0)` and `.print()` work directly on Python literals without any manual wrapping.

## 0.53 → 0.54 migration

Namespaces that mirror Python module-level attributes now expose them as POOP `@property` attributes instead of zero-arg methods, matching CPython's shape. Update call sites:

| Old (≤ 0.53) | New (0.54+) |
|---|---|
| `sys.argv()` / `sys.platform()` / `sys.version_info()` / `sys.modules()` / `sys.path()` / `sys.flags()` / `sys.implementation()` / `sys.maxsize()` / `sys.byteorder()` / `sys.executable()` / `sys.stdout()` / `sys.stderr()` / `sys.stdin()` (and the rest of `sys.*`) | drop the `()` — `sys.argv`, `sys.platform`, ... |
| `time.tzname()` / `time.timezone()` / `time.altzone()` / `time.daylight()` | drop the `()` |
| `gc.callbacks()` | `gc.callbacks` |
| `tempfile.tempdir()` / `tempfile.set_tempdir(path)` | `tempfile.tempdir` (read) / `tempfile.tempdir = path` (assign; `none` clears) |
| `zoneinfo.TZPATH()` | `zoneinfo.TZPATH` |

Real Python callables (`sys.exit(code)`, `sys.getrecursionlimit()`, `gc.collect()`, `time.sleep(s)`, `tempfile.mkdtemp()`, …) stay as methods.

## Quick reference

A one-line summary of the most common substitutions. The sections below walk through each in context.

| Python | POOP |
|---|---|
| `print(x)` | `x.print()` |
| `if cond:` / `else:` | `cond.if_true(lambda: …)` / `cond.if_false(lambda: …)` |
| `for x in col:` | `col.do(lambda x: …)` |
| `while cond:` | `(lambda: cond).while_true(lambda: …)` |
| `not x` | `x.not_()` |
| `-x` | `x.negated()` |
| `len(x)` | `x.len()` |
| `x[i]` | `x.at(i)` |
| `x[a:b]` | `x.slice(a, b)` |
| `x and y` | `x.and_(lambda: y)` |
| `x or y` | `x.or_(lambda: y)` |
| `random.choice(xs)` | `random.choice(xs)` |
| `random.Random(seed)` | `Random(seed)` |
| `datetime.date.today()` | `Date.today()` |
| `decimal.Decimal("3.14")` | `Decimal("3.14")` |
| `string.ascii_letters` | `string.ascii_letters` |
| `string.Template(s).substitute(d)` | `Template(s).substitute(d)` |
| `ZoneInfo("America/Sao_Paulo")` | `ZoneInfo("America/Sao_Paulo")` |
| `calendar.isleap(year)` | `calendar.isleap(year)` |
| `class Color(Enum): RED = 1` | `class Color(Enum): RED = 1` |
| `struct.pack(">I", 42)` | `struct.pack(">I", 42)` |
| `codecs.encode(s, "rot_13")` | `codecs.encode(s, "rot_13")` |
| `filecmp.cmp(a, b)` | `filecmp.cmp(a, b)` |
| `tempfile.mkdtemp()` | `tempfile.mkdtemp()` |
| `shutil.copy(a, b)` | `shutil.copy(a, b)` |
| `pickle.dumps(obj)` | `pickle.dumps(obj)` |
| `zlib.compress(b)` | `zlib.compress(b)` |
| `gzip.compress(b)` | `gzip.compress(b)` |
| `bz2.compress(b)` | `bz2.compress(b)` |
| `lzma.compress(b)` | `lzma.compress(b)` |
| `zipfile.ZipFile(p, "w")` | `ZipFile(p, "w")` |
| `tarfile.open(p, "w:gz")` | `TarFile.open(p, "w:gz")` |
| `locale.getpreferredencoding()` | `locale.getpreferredencoding()` |
| `ipaddress.ip_address("::1")` | `ipaddress.ip_address("::1")` |
| `urllib.parse.urlparse(u)` | `urllib.parse.urlparse(u)` |
| `urllib.request.urlopen(u)` | `urllib.request.urlopen(u)` |
| `http.HTTPStatus.OK` | `http.HTTPStatus.OK` |
| `smtplib.SMTP(host, port)` | `SMTP(host, port)` |
| `csv.reader(f)` | `csv.reader(text)` |
| `configparser.ConfigParser()` | `ConfigParser()` |
| `pwd.getpwuid(uid)` | `pwd.getpwuid(uid)` |
| `grp.getgrnam(name)` | `grp.getgrnam(name)` |
| `resource.getrusage(who)` | `resource.getrusage(who)` |
| `sys.platform` | `sys.platform` |
| `sys.argv[0]` | `sys.argv.at(0)` |
| `sys.stdout.write(s)` | `sys.stdout.write(s)` |
| `atexit.register(f)` | `atexit.register(f)` |
| `gc.collect()` | `gc.collect()` |
| `EmailMessage().set_content(b)` | `EmailMessage().set_content(b)` |
| `email.utils.parseaddr(s)` | `email.utils.parseaddr(s)` |
| `html.escape(s)` | `html.escape(s)` |
| `ET.fromstring(text)` | `ET.fromstring(text)` |
| `ET.tostring(elem)` | `ET.tostring(elem)` |
| `class T(unittest.TestCase):` | `class T(TestCase):` |
| `cProfile.Profile()` | `Profile()` |
| `pstats.Stats(p)` | `Stats(p)` |
| `timeit.timeit("pass")` | `timeit.timeit("pass")` |
| `signal.SIGINT` | `signal.SIGINT` |
| `socket.socket(...)` | `Socket(...)` |
| `ssl.create_default_context()` | `ssl.create_default_context()` |
| `asyncio.run(coro)` | `asyncio.run(coro)` |
| `os.getpid()` | `os.getpid()` |
| `os.environ["HOME"]` | `os.environ.get("HOME")` |
| `io.StringIO(...)` | `StringIO(...)` |
| `time.time()` | `time.time()` |
| `logging.getLogger(...)` | `logging.getLogger(...)` |
| `platform.system()` | `platform.system()` |
| `threading.Thread(target=f)` | `Thread(target=f)` |
| `multiprocessing.cpu_count()` | `multiprocessing.cpu_count()` |
| `concurrent.futures.ThreadPoolExecutor()` | `ThreadPoolExecutor()` |
| `subprocess.run(["ls"])` | `subprocess.run(["ls"])` |
| `queue.Queue()` | `Queue()` |

## Control flow

### `if` / `else`

```python
# Python
result = handle_admin() if user.is_admin() else handle_guest()
```

```python
# POOP
result = user.is_admin().if_true_if_false(
    lambda: handle_admin(),
    lambda: handle_guest(),
)
```

### Single-branch `if`

```python
# Python
if balance < 0:
    raise ValueError("overdraft")
```

```python
# POOP
(balance < 0).if_true(lambda: ValueError.raise_("overdraft"))
```

### `and` / `or` / `not`

```python
# Python
ok = is_admin and not is_locked or is_owner
```

```python
# POOP
ok = is_admin.and_(lambda: is_locked.not_()).or_(lambda: is_owner)
```

> The `lambda:` wrappers preserve short-circuit semantics — branches are only evaluated if reached.

## Iteration

### `for` loop

```python
# Python
for item in items:
    process(item)
```

```python
# POOP
items.do(lambda item: process(item))
```

### List / set / dict comprehension

```python
# Python
result = [x * 2 for x in xs if x > 0]
```

```python
# POOP
result = list(xs.filter(lambda x: x > 0).map(lambda x: x * 2))
```

> `map` and `filter` return lazy iterators. Materialize with `list(...)`, `tuple(...)`, `set(...)`, `bytes(...)`.

### `range` loop

```python
# Python
for i in range(1, 11):
    print(i)
```

```python
# POOP
range(1, 11).do(lambda i: i.print())
```

### `enumerate` / `zip`

```python
# Python
for i, name in enumerate(names):
    ...
for a, b in zip(xs, ys):
    ...
```

```python
# POOP
names.enumerate().do(lambda pair: ...)   # pair.at(0) is index, pair.at(1) is value
xs.zip(ys).do(lambda pair: ...)
```

## Free functions on objects

```python
# Python
n = len(xs)
y = abs(x)
print(x)
text = repr(x)
ok = isinstance(x, MyClass)
total = sum(xs)
biggest = max(xs)
```

```python
# POOP
n = xs.len()
y = x.abs()
x.print()
text = x.repr()
ok = x.is_instance(MyClass)
total = xs.sum()
biggest = xs.max()
```

> Same pattern for `getattr`/`setattr`/`hasattr`/`dir`/`format`/`hash`/`id`/`callable`/`ascii` → `x.get_attr(name)`, `x.set_attr(name, val)`, `x.has_attr(name)`, `x.dir()`, `x.format(spec)`, `x.hash()`, `x.id()`, `x.callable()`, `x.ascii()`. For `type(x)` use `x.class_name()` — or better, polymorphism instead of type dispatch.

## Operators that look procedural

```python
# Python
y = -x
y = ~x
q, r = divmod(a, b)
y = round(x, 2)
```

```python
# POOP
y = x.negated()
y = x.bit_invert()
q, r = a.divmod(b)
y = x.round(2)
```

> Binary operators (`+`, `-`, `*`, `/`, `**`, `==`, `<`, …) stay native — the asymmetry is intentional, see `INFECTIONS.md` § "Binary infix operators".

## Subscripting and slicing

```python
# Python
first = xs[0]
window = xs[1:4]
```

```python
# POOP
first = xs.at(0)
window = xs.slice(1, 4)
```

> For reuse across collections, build a value with `slice(start, stop, step=None)` — the transformer rewrites the lowercase builtin into POOP's `Slice`. Pass it to `xs.slice(s)` on any sequence type.

## Membership

```python
# Python
3 in xs
"foo" in s
"key" in d
```

```python
# POOP
xs.includes(3)
s.includes("foo")
d.includes("key")
```

> `d.includes(k)` mirrors Python's `key in d` — checks keys. The views also respond to `.includes(...)` for the other axes: `d.keys().includes(k)`, `d.values().includes(v)`, `d.items().includes((k, v))`.

## Identity (`is`, `is None`)

```python
# Python
x is None
x is not None
x is y
```

```python
# POOP
x.is_none()
x.not_none()
x.is_identical(y)
```

> `is` is forbidden by the `no_is` validator. For `None` checks use `.is_none()` / `.not_none()`; for arbitrary identity use `.is_identical(other)` / `.not_identical(other)`.

## Raise / try / except

```python
# Python
try:
    risky()
except ValueError as e:
    handle(e)
```

```python
# POOP
Try(lambda: risky()).except_(ValueError, lambda e: handle(e)).run()
```

> Inside lambdas you cannot `raise` — write `ExcType.raise_("msg")`. The `RaiseTransformer` rewrites it to a callable so it composes inside blocks.

## Context managers (`with`)

```python
# Python
with lock:
    critical_section()
```

```python
# POOP
With(lambda: lock).do(lambda _: critical_section())
```

> `With` takes a *factory lambda*, not the cm directly — entry is deferred until `do()` runs.

## File I/O (`open`)

```python
# Python
with open("data.txt") as f:
    text = f.read()
open("out.txt", "w").write(text.upper())
```

```python
# POOP
text = Path("data.txt").read_text()
Path("out.txt").write_text(text.upper())
```

> `open()` is a definitive ban. `Path` covers `read_text` / `write_text` / `read_bytes` / `write_bytes` plus the rest of `pathlib`. There is no `Path.open(mode)` yet — file handles aren't exposed.

## Random (`random` module + `Random` class)

```python
# Python
import random

x = random.random()
n = random.randint(1, 10)
pick = random.choice(xs)
random.shuffle(xs)
sample = random.sample(xs, 3)
r = random.Random(42)
```

```python
# POOP
x = random.random()
n = random.randint(1, 10)
pick = random.choice(xs)
random.shuffle(xs)
sample = random.sample(xs, 3)
r = Random(42)
```

> POOP exposes both `random` (lowercase, module-level singleton — `random.random()`, `random.choice(xs)`, …) and `Random` (PascalCase, the class — `Random(seed)` returns a fresh independently-seeded instance). The split mirrors Python exactly; the only shortcut is that `Random` is in scope without a `random.` prefix (no `import` needed). Cryptographic draws live in `secrets`, never `random`.

## Dates and times (`datetime` module + `Date` / `Time` / `DateTime` / `TimeDelta` / `TimeZone`)

```python
# Python
from datetime import date, datetime, timedelta, timezone

today = date.today()
dt = datetime(2026, 5, 15, 12, 30, tzinfo=timezone.utc)
future = dt + timedelta(days=7)
diff = future - dt          # timedelta(days=7)
iso = dt.isoformat()
parsed = datetime.fromisoformat("2026-05-15T12:30:00+00:00")
```

```python
# POOP
today = Date.today()
dt = DateTime(2026, 5, 15, 12, 30, tzinfo=TimeZone.utc)
future = dt + TimeDelta(days=7)
diff = future - dt          # TimeDelta(days=7)
iso = dt.isoformat()
parsed = DateTime.fromisoformat("2026-05-15T12:30:00+00:00")
```

> The five canonical types are bound at module scope (`Date`, `Time`, `DateTime`, `TimeDelta`, `TimeZone`) and also reachable through the `datetime` namespace (`datetime.date`, `datetime.time`, …) for users used to Python's module attributes. Arithmetic is closed under the type pairs: `Date + TimeDelta` → `Date`, `DateTime - DateTime` → `TimeDelta`, `TimeDelta / TimeDelta` → `Float` (ratio), `TimeDelta // TimeDelta` → `Int`. `TimeZone.utc` is the UTC constant; custom `tzinfo` subclasses are out of scope (use `TimeZone(TimeDelta(hours=h))` for fixed offsets).

## Arbitrary-precision decimals (`decimal` module + `Decimal` / `Context` classes)

```python
# Python
from decimal import Decimal, getcontext, ROUND_HALF_UP

price = Decimal("19.99")
total = price * Decimal("3") + Decimal("0.10")
rounded = total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
getcontext().prec = 50
```

```python
# POOP
price = Decimal("19.99")
total = price * Decimal("3") + Decimal("0.10")
rounded = total.quantize(Decimal("0.01"), decimal.ROUND_HALF_UP)
# precision setting: seed the scope or mutate the context
With(lambda: decimal.localcontext(prec=5)).do(lambda ctx: ...)
With(lambda: decimal.localcontext()).do(lambda ctx: ctx.set_prec(5))
```

> `Decimal` is in scope without a `decimal.` prefix (same pattern as `Random`, `UUID`). All arithmetic is closed (`Decimal + Decimal → Decimal`, etc.) and `Decimal` mixes with `Int`/`Float` in comparisons and `Int` in arithmetic. Rounding constants live on the `decimal` namespace as `Str` (`decimal.ROUND_HALF_UP`, …). Signal classes (`decimal.InvalidOperation`, `decimal.DivisionByZero`, …) are Python exception classes — pass them to `Try.except_(...)`. Scope precision/rounding with `decimal.localcontext(prec=…, rounding=…)`, or mutate the context inside the block via `ctx.set_prec(Int)` / `ctx.set_rounding(Str)`.

## ASCII character classes and string templates (`string` module + `Template` class)

```python
# Python
import string

alpha = string.ascii_lowercase
template = string.Template("Hello, $name!")
greeting = template.substitute({"name": "world"})
```

```python
# POOP
alpha = string.ascii_lowercase
template = Template("Hello, $name!")
greeting = template.substitute({"name": "world"})
```

> Constants on `string` (`ascii_letters`, `ascii_lowercase`, `ascii_uppercase`, `digits`, `hexdigits`, `octdigits`, `punctuation`, `printable`, `whitespace`) are `Str` values. `Template` is exposed bare (PascalCase, matching the `UUID` / `HMAC` convention). `.substitute(mapping)` raises `KeyError` on missing keys; `.safe_substitute(mapping)` leaves them in place. `string.Formatter` and `string.capwords` are out of scope — `Str.format` and `Str.title` cover them.

## IANA timezones (`zoneinfo` module + `ZoneInfo` class)

```python
# Python
from zoneinfo import ZoneInfo
import datetime

dt = datetime.datetime.now(tz=ZoneInfo("America/Sao_Paulo"))
```

```python
# POOP
dt = DateTime.now(ZoneInfo("America/Sao_Paulo"))
```

> `ZoneInfo` is bare (PascalCase). The lowercase `zoneinfo` namespace exposes `available_timezones()` (`Set[Str]`), `reset_tzpath(to=none)`, and `TZPATH` (attribute, not a method — `reset_tzpath` mutates it). `ZoneInfoNotFoundError` is a Python exception class for `Try.except_(...)`. `ZoneInfo.from_file` is deferred (POOP has no file-object abstraction). All `DateTime` constructors / `.now(tz=...)` / `.astimezone(tz)` entry points were widened to accept either `TimeZone` or `ZoneInfo`.

## Calendars (`calendar` module + `Calendar` class)

```python
# Python
import calendar

calendar.isleap(2024)                          # True
calendar.monthrange(2026, 5)                   # (4, 31)
cal = calendar.Calendar()
weeks = cal.monthdatescalendar(2026, 5)
```

```python
# POOP
calendar.isleap(2024)                          # true
calendar.monthrange(2026, 5)                   # (4, 31)
cal = Calendar()
weeks = cal.monthdatescalendar(2026, 5)
```

> Module-level shortcuts (`isleap`, `leapdays`, `weekday`, `monthrange`, `monthcalendar`, `month`, `calendar`, `timegm`) plus the weekday/month constants (`MONDAY` … `SUNDAY`, `JANUARY` … `DECEMBER`) live on the namespace. The reusable `Calendar` class is bare (PascalCase); its `iter*` methods return materialized POOP `List`s — POOP collections are not lazy. The rendering classes are bare too: `TextCalendar` (`formatmonth`/`formatyear`), `HTMLCalendar` (`formatmonth`/`formatyear`/`formatyearpage`), and the locale-aware `LocaleTextCalendar` / `LocaleHTMLCalendar`.

## Enumerations (`enum` module + `Enum` / `IntEnum` / `StrEnum` / `Flag` / `IntFlag` / `ReprEnum`)

```python
# Python
from enum import Enum, auto

class Color(Enum):
    RED = 1
    GREEN = 2
    BLUE = auto()

Color.RED.name        # "RED"
Color.RED.value       # 1
Color(2)              # Color.GREEN
```

```python
# POOP
class Color(Enum):
    RED = 1
    GREEN = 2
    BLUE = auto()

Color.RED.name_str()      # Str("RED")
Color.RED.value_object()  # Int(1)
Color(Int(2))             # Color.GREEN
```

> The bases (`Enum`, `IntEnum`, `StrEnum`, `Flag`, `IntFlag`, `ReprEnum`) are bare alongside the `enum` namespace; `auto()` is also bare. `.name` stays a Python `str` (CPython's enum protocol and decorators like `@unique` depend on that). Use `.name_str()` for a POOP `Str`. `.value` returns whatever was assigned — raw Python primitives stay raw; use `.value_object()` to wrap them. POOP value lookup works via `_missing_`: `Color(Int(1))` finds the same member as `Color(1)`. `enum.unique` / `verify` / `member` / `nonmember` apply directly. `ReprEnum` is re-exported as-is (it can't be subclassed without a data-type mixin). `EnumType` metaclass access is out of scope.

## Binary packing (`struct` module + `Struct` class)

```python
# Python
import struct

raw = struct.pack(">If", 42, 1.5)
n, x = struct.unpack(">If", raw)
size = struct.calcsize(">If")

s = struct.Struct(">If")
raw = s.pack(7, 2.5)
```

```python
# POOP
raw = struct.pack(">If", 42, 1.5)
result = struct.unpack(">If", raw)  # Tuple(Int(42), Float(1.5))
size = struct.calcsize(">If")

s = Struct(">If")
raw = s.pack(7, 2.5)
```

> Format-char wrapping back into POOP types is handled at the boundary: `int` → `Int`, `float` → `Float`, `bool` → `Boolean`, `bytes` → `Bytes`. `unpack` always returns a `Tuple`. Buffers accept `Bytes` / `ByteArray` / `MemoryView` for reads; writes (`pack_into`) require a writable buffer (`ByteArray` or `MemoryView`). `iter_unpack` is materialized to `List[Tuple]` — POOP collections are not lazy. `struct.error` is the Python exception class for `Try.except_`.

## Codecs (`codecs` module + `CodecInfo` class)

```python
# Python
import codecs

raw = codecs.encode("hello", "utf-8")      # b"hello"
text = codecs.decode(b"hello", "utf-8")    # "hello"
rot = codecs.encode("hello", "rot_13")     # "uryyb"
hex_bytes = codecs.encode(b"\xff", "hex_codec")  # b"ff"
info = codecs.lookup("utf-8")
```

```python
# POOP
raw = codecs.encode("hello", "utf-8")      # Bytes(b"hello")
text = codecs.decode(b"hello", "utf-8")    # Str("hello")
rot = codecs.encode("hello", "rot_13")     # Str("uryyb")
hex_bytes = codecs.encode(b"\xff", "hex_codec")  # Bytes(b"ff")
info = codecs.lookup("utf-8")              # CodecInfo
```

> `encode` and `decode` are polymorphic: text codecs return `Str`, binary codecs return `Bytes`. BOM constants (`BOM_UTF8`, `BOM_UTF16_LE`, …) live as class attributes on the `codecs` namespace. `CodecInfo.encode` / `.decode` mirror CPython's `(result, length_consumed)` tuple. Incremental encoder/decoder construction, `StreamReader` / `StreamWriter`, and `register` / `register_error` are out of scope — pair with future streaming I/O.

## File and directory comparison (`filecmp` module + `Dircmp` class)

```python
# Python
import filecmp

filecmp.cmp("a.txt", "b.txt")
match, mismatch, errors = filecmp.cmpfiles("dir1", "dir2", ["a", "b"])
dc = filecmp.dircmp("dir1", "dir2")
dc.report()
```

```python
# POOP
filecmp.cmp(Path("a.txt"), Path("b.txt"))
result = filecmp.cmpfiles(Path("dir1"), Path("dir2"), ["a", "b"])
dc = Dircmp(Path("dir1"), Path("dir2"))
dc.report()
```

> `Path` and `Str` are interchangeable as filesystem inputs. `cmpfiles` returns a single `Tuple(List[Str], List[Str], List[Str])` for `(match, mismatch, errors)`. `Dircmp` exposes the categorized name groups (`left_only`, `right_only`, `common`, `diff_files`, `same_files`, `funny_files`, etc.) as properties; `.subdirs` returns `Dict[Str, Dircmp]` for recursive walks. Use `.report_str()` to capture the textual summary as a `Str` instead of writing to stdout.

## Temporary files and directories (`tempfile` module + temp classes)

```python
# Python
import tempfile

with tempfile.TemporaryDirectory() as d:
    ...

with tempfile.NamedTemporaryFile() as f:
    f.write(b"data")
    name = f.name

fd, path = tempfile.mkstemp()
```

```python
# POOP
With.do(TemporaryDirectory(), Block(lambda d: ...))

ntf = NamedTemporaryFile()
ntf.write(b"data")
name = ntf.name
ntf.close()

result = tempfile.mkstemp()  # Tuple(Int(fd), Path)
```

> `TemporaryDirectory` / `TemporaryFile` / `NamedTemporaryFile` / `SpooledTemporaryFile` are bare alongside the `tempfile` namespace. Each is a context manager and exposes the minimal binary surface (`.read` / `.write` / `.seek` / `.tell` / `.flush` / `.close`) so callers can populate or drain the file without a separate POOP I/O abstraction. `NamedTemporaryFile.name` and `TemporaryDirectory.name` return `Path`. `tempfile.tempdir` reads the current search-path override; assign to it (`tempfile.tempdir = Path("/tmp")` or `tempfile.tempdir = none` to clear) to mutate it.

## High-level file operations (`shutil` module)

```python
# Python
import shutil

shutil.copy("src.txt", "dst.txt")
shutil.copytree("src_dir", "dst_dir")
shutil.move("a", "b")
shutil.rmtree("doomed_dir")
where = shutil.which("git")
total, used, free = shutil.disk_usage(".")
shutil.make_archive("bundle", "zip", root_dir=".", base_dir="src")
```

```python
# POOP
shutil.copy(Path("src.txt"), Path("dst.txt"))
shutil.copytree(Path("src_dir"), Path("dst_dir"))
shutil.move(Path("a"), Path("b"))
shutil.rmtree(Path("doomed_dir"))
where = shutil.which("git")
usage = shutil.disk_usage(".")  # Tuple(Int, Int, Int)
shutil.make_archive(Path("bundle"), "zip", root_dir=Path("."), base_dir="src")
```

> `Path` and `Str` are interchangeable everywhere `shutil` takes a filesystem location. Return values are `Path` when CPython returns a path-like. `shutil.which` returns `Path` or `none`. `shutil.disk_usage` returns `Tuple(total, used, free)` of `Int`; `shutil.get_terminal_size` returns `Tuple(columns, lines)`. Archive helpers (`make_archive`, `unpack_archive`, `get_archive_formats`, `get_unpack_formats`) all wrap the CPython surface. `shutil.Error` and `shutil.SameFileError` are exposed as class attributes for use with `Try.except_`. `shutil.ignore_patterns(*patterns)` returns a block that drops into `copytree(ignore=...)`; `copytree` / `move` also accept a POOP lambda as `copy_function` via the block bridge.

## Pickle (`pickle` module + `Pickler` / `Unpickler` classes)

```python
# Python
import pickle

raw = pickle.dumps({"a": [1, 2, 3]})
data = pickle.loads(raw)

with open("snapshot.pkl", "wb") as f:
    pickle.dump(my_object, f)

with open("snapshot.pkl", "rb") as f:
    my_object = pickle.load(f)
```

```python
# POOP
raw = pickle.dumps({"a": [1, 2, 3]})       # Bytes
data = pickle.loads(raw)                    # Dict[Str, List[Int]]

pickle.dump(my_object, Path("snapshot.pkl"))
my_object = pickle.load(Path("snapshot.pkl"))
```

> `dump` / `load` are path-based — POOP has no file-object abstraction. POOP types round-trip cleanly: `Int` / `Str` / `Float` / `Bytes` / `Boolean` / `NoneClass` and the POOP collections (`List` / `Tuple` / `Dict` / `Set` / `FrozenSet`) are unwrapped to native Python on dump and re-wrapped to POOP on load — callers never see a raw `int` / `str` / `list` / etc. POOP user-class instances pass through unchanged. `Pickler(protocol=none)` is a `Bytes` buffer Pickler with `.dump(obj)`/`.getvalue()`/`.clear_memo()`/`.fast`; `Unpickler(data)` reads from a `Bytes` buffer with `.load()`. Constants `pickle.HIGHEST_PROTOCOL` / `DEFAULT_PROTOCOL` are `Int`. `PickleError` / `PicklingError` / `UnpicklingError` are exposed for `Try.except_`. **Security:** never `loads` pickle data from untrusted sources — it executes arbitrary code on deserialization.

## Compression (`zlib` / `gzip` / `bz2` / `lzma` / `zipfile` / `tarfile` + `compression` umbrella)

```python
# Python
import zlib, gzip, bz2, lzma, zipfile, tarfile

raw = zlib.compress(b"hello world")
zlib.decompress(raw)
zlib.crc32(b"abc")

with gzip.open("out.gz", "wb") as f:
    f.write(b"payload")

bz2.compress(b"payload")
lzma.decompress(lzma.compress(b"payload"))

with zipfile.ZipFile("a.zip", "w") as z:
    z.writestr("file.txt", b"data")
    z.extractall("/tmp/out")

with tarfile.open("a.tar.gz", "w:gz") as t:
    t.add("source", arcname="source")
```

```python
# POOP
raw = zlib.compress(b"hello world")        # Bytes
zlib.decompress(raw)
zlib.crc32(b"abc")                          # Int

With.do(gzip.open(Path("out.gz"), "wb"),
        Block(lambda f: f.write(b"payload")))

bz2.compress(b"payload")
lzma.decompress(lzma.compress(b"payload"))

With.do(ZipFile(Path("a.zip"), "w"), Block(lambda z: (
    z.writestr("file.txt", b"data"),
    z.extractall(Path("/tmp/out")),
)))

With.do(TarFile.open(Path("a.tar.gz"), "w:gz"),
        Block(lambda t: t.add(Path("source"), "source")))
```

> All compression entry points are `Bytes` in / `Bytes` out. File-handle classes (`GzipFile` / `BZ2File` / `LZMAFile`) and archive classes (`ZipFile` / `TarFile`) are `With`-friendly and path-based — POOP has no file-object abstraction. The `compression` umbrella (Python 3.14) re-exports the per-format namespaces under `compression.zlib` / `.gzip` / `.bz2` / `.lzma`. Streaming compressor/decompressor pairs (`Compress` / `Decompress`, `BZ2Compressor` / `BZ2Decompressor`, `LZMACompressor` / `LZMADecompressor`) cover the chunked use cases. `TarFile.extractall` defaults to the safe `filter="data"` (3.14+); callers who want the historical unsafe behavior pass `filter="fully_trusted"` explicitly. `compression.zstd` is out of scope until Python 3.14's API stabilises.

## Locale (`locale` module)

```python
# Python
import locale

locale.setlocale(locale.LC_ALL, "en_US.UTF-8")
locale.atof("1,234.56")              # 1234.56
locale.format_string("%d", 1000000, grouping=True)
encoding = locale.getpreferredencoding()
```

```python
# POOP
locale.setlocale(locale.LC_ALL, "en_US.UTF-8")
locale.atof("1,234.56")              # Float(1234.56)
locale.format_string("%d", 1000000, grouping=true)
encoding = locale.getpreferredencoding()  # Str
```

> Categories (`LC_ALL` / `LC_CTYPE` / `LC_COLLATE` / `LC_TIME` / `LC_MONETARY` / `LC_NUMERIC` / `LC_MESSAGES`) and `CHAR_MAX` are class attributes on the namespace. `getlocale` / `getdefaultlocale` return a `Tuple(Str \| NoneClass, Str \| NoneClass)`. `localeconv` returns a `Dict[Str, Object]` covering the full LC_NUMERIC / LC_MONETARY convention. `locale.Error` is the Python exception class for `Try.except_` on unknown locale names. `LC_MESSAGES` falls back to `LC_ALL` on platforms missing the POSIX category (e.g. Windows). `currency` raises `ValueError` in the C locale (which has no monetary symbol).

## Internet protocols (`ipaddress`, `urllib`, `http`, `smtplib`)

```python
# Python
import ipaddress
import urllib.parse
import urllib.request
import http
import smtplib

addr = ipaddress.ip_address("192.0.2.1")
net = ipaddress.ip_network("192.0.2.0/24")

parts = urllib.parse.urlparse("https://example.com/p?k=v")
query = urllib.parse.urlencode({"a": 1, "b": 2})
with urllib.request.urlopen("file:///tmp/x") as r:
    body = r.read()

status = http.HTTPStatus.OK
conn = http.client.HTTPConnection("example.com")

smtp = smtplib.SMTP("smtp.example.com", 587)
```

```python
# POOP
addr = ipaddress.ip_address("192.0.2.1")
net = ipaddress.ip_network("192.0.2.0/24")

parts = urllib.parse.urlparse("https://example.com/p?k=v")
query = urllib.parse.urlencode({"a": 1, "b": 2})
With.do(urllib.request.urlopen("file:///tmp/x"), Block(lambda r: r.read()))

status = http.HTTPStatus(200)              # POOP Int round-trips into the IntEnum
conn = HTTPConnection("example.com")

smtp = SMTP("smtp.example.com", 587)
```

> `ipaddress` exposes both factory functions (`ip_address` / `ip_network` / `ip_interface`) and the explicit `IPv4Address` / `IPv6Address` / `IPv4Network` / `IPv6Network` / `IPv4Interface` / `IPv6Interface` classes. Address arithmetic with `Int` is supported (`addr + Int(1)`). `urllib.parse` is pure-text URL transformations; `urllib.request.urlopen` returns a `With`-friendly `Response` (`.read` / `.headers` / `.status`). `urllib.request.Request` is the bare request-builder; the handler hierarchy (`OpenerDirector` / `HTTPHandler` / …) is exposed as class refs for advanced callers. `http.HTTPStatus` and `http.HTTPMethod` are re-exports of CPython's enums with a `_missing_` patch so POOP `Int` / `Str` lookups work. `http.client.HTTPConnection` / `HTTPSConnection` wrap the upstream connection types; `HTTPResponse` exposes `.status` / `.read` / `.headers`. `http.server` / `http.cookies` / `http.cookiejar` are exposed under their submodule names. `smtplib.SMTP` / `SMTP_SSL` / `LMTP` cover the SMTP client surface (`helo` / `ehlo` / `starttls` / `login` / `sendmail` / `send_message` / `quit` / `close`); the full error hierarchy (`SMTPException` / `SMTPServerDisconnected` / `SMTPResponseException` / `SMTPSenderRefused` / `SMTPRecipientsRefused` / `SMTPDataError` / `SMTPConnectError` / `SMTPHeloError` / `SMTPNotSupportedError` / `SMTPAuthenticationError`) is exposed for `Try.except_`. `urllib.robotparser` is out of scope for v1.

## File formats (`csv` module + readers/writers, `configparser` module + parser)

```python
# Python
import csv, configparser

with open("data.csv") as f:
    for row in csv.reader(f):
        print(row)

cp = configparser.ConfigParser()
cp.read("app.ini")
host = cp.get("server", "host", fallback="localhost")
```

```python
# POOP
text = Path("data.csv").read_text()
csv.reader(text).do(Block(lambda row: row.print()))

cp = ConfigParser()
cp.read(Path("app.ini"))
host = cp.get("server", "host", fallback="localhost")
```

> POOP has no file-object abstraction, so `Reader` / `DictReader` take a `Str` (split on newlines) or `List[Str]` of lines; `Writer` / `DictWriter` accumulate into an internal buffer exposed via `.getvalue()`. `Sniffer` autodetects dialect from a sample. Dialect registration (`csv.register_dialect` / `unregister_dialect` / `get_dialect` / `list_dialects`) works as in CPython. `ConfigParser` has `read` (from `Path` / `Str` / `List[Path]`), `read_string` / `read_dict` / `read_file`, plus `write_str` and `write_to(path)` for serialization. Typed accessors (`getint` / `getfloat` / `getboolean`) return POOP wrappers. The full error hierarchy and both interpolation classes (`BasicInterpolation` / `ExtendedInterpolation`) are on the namespace.

## Unix-specific lookups (`pwd`, `grp`, `resource`)

```python
# Python
import pwd, grp, resource

entry = pwd.getpwuid(os.getuid())
group = grp.getgrnam("staff")
soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
usage = resource.getrusage(resource.RUSAGE_SELF)
```

```python
# POOP
entry = pwd.getpwuid(os_getuid_value)         # Passwd
group = grp.getgrnam("staff")                  # Group
limits = resource.getrlimit(resource.RLIMIT_NOFILE)  # Tuple(Int, Int)
usage = resource.getrusage(resource.RUSAGE_SELF)     # RUsage
```

> `pwd` and `grp` are tiny — `getpwuid` / `getpwnam` / `getpwall` and `getgrgid` / `getgrnam` / `getgrall` return `Passwd` / `Group` POOP records with the standard `.pw_*` / `.gr_*` accessors. `resource` queries process limits (`getrlimit` returns `Tuple(soft, hard)`; `setrlimit` accepts the same shape) and per-process rusage (`getrusage` returns `RUsage` with `.ru_utime` / `.ru_stime` as `Float` and the per-counter `.ru_maxrss` / `.ru_minflt` / etc. as `Int`). All standard `RLIMIT_*` and `RUSAGE_*` constants are class attributes — platform-specific ones bind to `none` rather than raising on import. `resource.prlimit` is Linux-only.

## Runtime services (`sys`, `atexit`, `gc`)

```python
# Python
import sys, atexit, gc

print(sys.platform, sys.version_info)
sys.stdout.write("hi\n")
script = sys.argv[0]
atexit.register(lambda: print("bye"))
gc.collect()
```

```python
# POOP
sys.platform.print()
sys.version_info.print()
sys.stdout.write("hi\n")
script = sys.argv.at(0)                  # Str (sys.argv mirrors Python; subscript → .at)
atexit.register(lambda: "bye".print())   # Block (lambda auto-wraps)
gc.collect().print()                     # Int
```

> POOP mirrors Python's `sys` module shape directly — Python attributes (`sys.argv`, `sys.platform`, `sys.version_info`, `sys.modules`, `sys.path`, `sys.maxsize`, …) are exposed as POOP `@property` attributes returning POOP types. So `sys.argv[0]` (subscript, banned in POOP) becomes `sys.argv.at(0)`. `sys.stdout` / `sys.stderr` / `sys.stdin` are properties returning `Stdout` / `Stdin` wrappers. Python callables (`sys.exit(code)`, `sys.getrecursionlimit()`, `sys.setrecursionlimit(n)`) stay as methods. The introspection-heavy `settrace` / `_getframe` / `monitoring` / `audit*` surface is intentionally absent. `atexit` mirrors CPython directly — `register` accepts a POOP `Block` (lambdas auto-wrap), `unregister` / `_run_exitfuncs` / `_clear` work as expected. `gc` exposes the **control surface only**: `enable`/`disable`/`isenabled`/`collect`/`get_threshold`/`set_threshold`/`get_count`/`get_stats`/`get_debug`/`set_debug`/`freeze`/`unfreeze`/`get_freeze_count` as methods plus `callbacks` as `@property` and the `DEBUG_*` constants — `get_objects` / `get_referrers` / `is_tracked` are excluded as introspection.

## Internet data / markup (`email`, `html`, `xml`)

```python
# Python
import email, html
from email.message import EmailMessage
import xml.etree.ElementTree as ET

m = EmailMessage()
m["Subject"] = "hi"
m.set_content("body")

safe = html.escape("<a>")
root = ET.fromstring("<r><a>x</a></r>")
ET.tostring(root, encoding="unicode")
```

```python
# POOP
m = EmailMessage()
m.at_put("Subject", "hi")
m.set_content("body")

safe = html.escape("<a>")              # Str
root = ET.fromstring("<r><a>x</a></r>")  # Element
ET.tostring(root).print()                # Str (use encoding="utf-8" for Bytes)
```

> `email` exposes the modern `EmailMessage` API plus `email.utils` (`parseaddr`/`formataddr`/`getaddresses`/`parsedate`/`formatdate`/`make_msgid`) and the preset `email.policy` constants (`default`, `SMTP`, `SMTPUTF8`, `HTTP`, `strict`, `compat32`). Headers are accessed via the POOP `at`/`at_put` pair (Python's `msg["X"]` is subscript-shaped — banned by `no_subscript`). `html` is small: `html.escape`/`html.unescape` for the safe text helpers, `HTMLParser` for SAX-style parsing, and `html.entities` for the codepoint maps (`name2codepoint`/`codepoint2name`/`html5`/`entitydefs`). `xml` ships **ElementTree only** — `ET.fromstring`/`ET.XML`/`ET.parse`/`ET.tostring`/`ET.SubElement`/`ET.indent`, plus the `Element` / `ElementTree` records. Use `ET.ParseError` in `Try.except_` to catch bad XML. The full `xml.dom.minidom` / `xml.sax` surface is out of scope — ElementTree covers the vast majority of XML use cases in modern Python. As in CPython, the default parser does not load external DTDs, but POOP does **not** swap in `defusedxml` automatically — wrap untrusted XML accordingly.

## Dev / debug / profile (`unittest`, `cProfile`, `pstats`, `timeit`)

```python
# Python
import unittest, cProfile, pstats, timeit

class MyTests(unittest.TestCase):
    def test_x(self):
        self.assertEqual(1, 1)

with cProfile.Profile() as p:
    do_work()
pstats.Stats(p).sort_stats("cumulative").print_stats()

t = timeit.timeit("pass", number=10000)
```

```python
# POOP
class MyTests(TestCase):
    def test_x(self):
        self.assertEqual(1, 1)

result = MyTests().run_method("test_x")
result.wasSuccessful().print()

With(Profile()).do(Block(lambda p: do_work()))
Stats(p).sort_stats(SortKey.CUMULATIVE).print_stats().print()

t = timeit.timeit("pass", "pass", 10000)   # Float
```

> `unittest` is a POOP-flavoured re-implementation of the xUnit surface. `TestCase` subclasses define `test_*` methods and `setUp`/`tearDown` hooks; the standard assertion family is available (`assertEqual`, `assertTrue`, `assertGreater`, `assertIsInstance`, `assertAlmostEqual`, `assertRaises`, …) and all raise POOP's `AssertionError` on failure with optional `Str` messages. Run a single test via `case.run_method(Str("name"))`, or batch via `TestSuite` + `TestRunner`. The full `unittest.mock` surface (`MagicMock`, `patch`, `sentinel`) is out of scope for v1. `cProfile.Profile` mirrors CPython directly — `enable`/`disable`/`runcall`, plus context-manager support via POOP's `With`. `Stats` wraps `pstats.Stats` with chainable `sort_stats`/`reverse_order`/`strip_dirs`; `print_*` methods return the captured output as `Str` instead of writing to stdout. Sort keys live on the `SortKey` class as POOP `Str`s. `timeit` is straightforward — `timeit.timeit(stmt, setup, number)` returns `Float`, `timeit.repeat` returns `List[Float]`, `Timer.autorange()` returns `Tuple(Int, Float)`.

## Networking (`signal`, `socket`, `ssl`, `asyncio`)

```python
# Python
import signal, socket, ssl, asyncio

signal.signal(signal.SIGINT, my_handler)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(("example.com", 443))

ctx = ssl.create_default_context()
secure = ctx.wrap_socket(sock, server_hostname="example.com")

async def go():
    await asyncio.sleep(1)
    return 42

asyncio.run(go())
```

```python
# POOP
signal.signal(signal.SIGINT, my_handler)        # POOP Block as handler

sock = Socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(("example.com", 443))

ctx = ssl.create_default_context()
secure = ctx.wrap_socket(sock, server_hostname="example.com")

class Go:
    async def run(self):
        await asyncio.sleep(1)
        return 42

asyncio.run(Go().run()).print()
```

> POOP exposes `signal.signal`/`getsignal`/`strsignal`/`raise_signal`/`pthread_kill`/`sigpending` plus the common signal constants (`SIGINT`, `SIGTERM`, `SIGABRT`, `SIGCHLD`, `SIGUSR1`, …). Platform-specific constants bind to `none` rather than raising on import. The `Socket` class mirrors `socket.socket` directly — `bind`/`listen`/`accept`/`connect`/`send`/`sendall`/`recv`/`sendto`/`recvfrom`/`shutdown`/`close`, plus the address-resolution module helpers (`gethostbyname`, `gethostbyname_ex`, `getfqdn`, `getservbyname/port`, `inet_aton/ntoa`, `inet_pton/ntop`) and the high-level `create_connection`/`create_server` factories. POOP `Socket` works as a `With` context manager. `ssl.create_default_context()` returns an `SSLContext`; mutators are method-based (`set_verify_mode`, `set_check_hostname`, `set_ciphers`) to keep POOP's no-property-mutation discipline. `ssl.SSLError` and its subclasses are catchable via `Try.except_`. `asyncio` exposes `run`, `sleep`, `gather`, `wait_for`, `shield`, `create_task`, and `Future`. Since v0.52.0 POOP source can define `async def` methods inside a class and `await` other coroutines directly — drive them with `asyncio.run(SomeClass().run())`. Use `Future.done/cancelled/result/exception/cancel` to inspect tasks. `async for` / `async with` / async generators remain forbidden.

## Generic OS (`os`, `io`, `time`, `logging`, `platform`)

```python
# Python
import os, io, time, logging, platform

random_bytes = os.urandom(16)
pid = os.getpid()
cwd = os.getcwd()
home = os.environ.get("HOME")

buf = io.StringIO()
buf.write("hello")
buf.getvalue()

t = time.time()
time.sleep(0.1)

logger = logging.getLogger("app")
logger.info("hi")

system = platform.system()
```

```python
# POOP
random_bytes = os.urandom(16)             # Bytes
pid = os.getpid()                          # Int
cwd = os.getcwd()                          # Path
home = os.environ.get("HOME")              # Str | none

buf = StringIO()
buf.write("hello")
buf.getvalue().print()                     # Str

t = time.time()                            # Float
time.sleep(0.1)

logger = logging.getLogger("app")
logger.info("hi")

platform.system().print()                  # Str
```

> POOP mirrors Python's `os` module shape directly: `os.getpid()`/`getppid()`/`getuid()`/`getgid()`/`geteuid()`/`getegid()` for process IDs, `os.umask`/`chdir`/`getcwd`/`kill` for current-process state, plus the low-level helpers (`urandom`, `cpu_count`, `process_cpu_count`, `getloadavg`) and the standard flag/separator constants (`F_OK`/`R_OK`/`W_OK`/`X_OK`, `O_RDONLY` etc, `sep`/`linesep`/`pathsep`/`devnull`). Environment access lives on the `os.environ` sub-namespace — since POOP forbids subscript syntax, Python's `os.environ["X"] = "y"` becomes `os.environ.set("X", "y")` (the `get`/`unset`/`has`/`keys`/`values`/`as_dict` methods round out the API). `os.path` is **intentionally absent**: every operation is reachable through POOP's `Path` mirror. `io` exposes the in-memory buffers `StringIO` / `BytesIO` (both work as `With` context managers) plus the seek constants — disk I/O continues to go through `Path.read_text`/`write_text`/`read_bytes`/`write_bytes`. `time` mirrors the wall-clock / monotonic / perf-counter / process-time / thread-time API in both seconds (`Float`) and nanoseconds (`Int`), plus parse/format helpers and `StructTime`. `logging` is the canonical Python `Logger`/`Handler`/`Formatter` triad — `set*` accessors return `none`, mutable booleans use `set_propagate`. `logging.config` and `logging.handlers` are out of scope for v1. `platform` returns runtime environment metadata; `Uname` exposes the standard six-field record.

## Concurrent execution (`threading`, `multiprocessing`, `concurrent`, `subprocess`, `queue`)

```python
# Python
import threading, multiprocessing, concurrent.futures, subprocess, queue

t = threading.Thread(target=do_work)
t.start(); t.join()

with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
    results = list(ex.map(square, range(10)))

result = subprocess.run(["ls", "-la"], capture_output=True, text=True)

q = queue.Queue()
q.put(item); item = q.get()
```

```python
# POOP
t = Thread(target=do_work)
t.start(); t.join()

With(lambda: ThreadPoolExecutor(4)).do(
    lambda ex: ex.map(square, list(range(10))).do(lambda r: r.print())
)

result = subprocess.run(["ls", "-la"], capture_output=true, text=true)
result.stdout.print()

q = Queue()
q.put(item); item = q.get()
```

> POOP exposes `threading.Thread` plus the standard primitives `Lock` / `RLock` / `Event` / `Semaphore` / `BoundedSemaphore` / `Condition` / `Barrier`, all `With`-friendly, and `Local` for per-thread storage (`at`/`at_put`/`includes`). Module helpers like `current_thread`/`active_count`/`get_ident`/`stack_size` are on the `threading` namespace; `threading.Timer` lives there too (a bare `Timer` would collide with `timeit.Timer`). `multiprocessing` mirrors the shape — `multiprocessing.Process` lives only on the namespace (not bound as a top-level name) to match Python's idiomatic usage; `Pool`/`MPQueue` are top-level. Targets passed to `Process`/`Pool` workers must be **module-level Python functions** — POOP's `Block`-wrapped lambdas don't pickle across the `forkserver` boundary that's now the Linux default. `concurrent.futures` exposes `ThreadPoolExecutor` and `ProcessPoolExecutor` (both `With`-friendly) plus `CFFuture` (renamed from `Future` to disambiguate from `asyncio.Future`). `concurrent.wait`/`.as_completed` work the same as in CPython. `subprocess.run` returns a `CompletedProcess` whose `.stdout`/`.stderr` are POOP `Str` (when `text=true`) or `Bytes`. `Popen` exposes the full lifecycle. `queue` has the same four classes as CPython — `Queue` (FIFO), `LifoQueue`, `PriorityQueue`, and `SimpleQueue` — with `Empty`/`Full` exception classes for `Try.except_`.
