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
| `string.ascii_letters` | `string.ascii_letters` |
| `string.Template(s).substitute(d)` | `Template(s).substitute(d)` |
| `ZoneInfo("America/Sao_Paulo")` | `ZoneInfo("America/Sao_Paulo")` |
| `class Color(Enum): RED = 1` | `class Color(Enum): RED = 1` |
| `EmailMessage().set_content(b)` | `EmailMessage().set_content(b)` |
| `ET.fromstring(text)` | `ET.fromstring(text)` |
| `ET.tostring(elem)` | `ET.tostring(elem)` |
| `class T(unittest.TestCase):` | `class T(TestCase):` |
| `cProfile.Profile()` | `Profile()` |
| `pstats.Stats(p)` | `Stats(p)` |
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
