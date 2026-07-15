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
| `ZoneInfo("America/Sao_Paulo")` | `ZoneInfo("America/Sao_Paulo")` |
| `class Color(Enum): RED = 1` | `class Color(Enum): RED = 1` |
| `EmailMessage().set_content(b)` | `EmailMessage().set_content(b)` |
| `ET.fromstring(text)` | `ET.fromstring(text)` |
| `ET.tostring(elem)` | `ET.tostring(elem)` |
| `class T(unittest.TestCase):` | `class T(TestCase):` |
| `cProfile.Profile()` | `Profile()` |
| `pstats.Stats(p)` | `Stats(p)` |
| `io.StringIO(...)` | `StringIO(...)` |

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

## In-memory buffers (`io` module + `StringIO` / `BytesIO`)

```python
# Python
import io

buf = io.StringIO()
buf.write("hello")
print(buf.getvalue())

with io.BytesIO(b"abc") as b:
    head = b.read(1)
```

```python
# POOP
buf = StringIO()
buf.write("hello")                         # Int — characters written
buf.getvalue().print()                     # Str

With(lambda: BytesIO(b"abc")).do(lambda b: b.read(1).print())
```

> `io` and `Path` are the two library-shaped names POOP keeps, on the same grounds: they are entry points the language itself needs rather than stdlib parity. `Path` is what the `open` ban points at, and `io` is its in-memory counterpart. Both buffers are `With` context managers, and both expose `read` / `readline` / `write` / `getvalue` / `seek` / `tell` / `truncate` / `close`, with `io.SEEK_SET` / `SEEK_CUR` / `SEEK_END` for `seek`. Disk I/O still goes through `Path` — POOP has no file-object abstraction.

