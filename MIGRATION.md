# Migration Recipes — Python → POOP

Quick translations of common Python idioms to POOP source code. For the full reference of which Python constructs are forbidden and why, see [`INFECTIONS.md`](INFECTIONS.md). For end-to-end programs, see [`examples/`](examples).

> Every snippet pair shows the Python form you would normally write and the POOP form the validators and transformers force you to write instead. Snippets are valid as POOP source — primitive literals like `0`, `"hi"`, `True` are wrapped to POOP types by transformers at parse time, so methods like `.at(0)` and `.print()` work directly on Python literals without any manual wrapping.

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

> Same pattern for `getattr`/`setattr`/`hasattr`/`dir`/`format`/`hash`/`id`/`callable`/`ascii` → `x.get_attr(name)`, `x.set_attr(name, val)`, `x.has_attr(name)`, `x.dir()`, `x.format(spec)`, `x.hash()`, `x.id()`, `x.callable()`, `x.ascii()`.

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

## Math (`math` module)

```python
# Python
import math

r = math.sqrt(x)
a = math.pi * r * r
ok = math.isclose(a, b)
h = math.hypot(3, 4, 12)
n = math.factorial(5)
```

```python
# POOP
r = math.sqrt(x)
a = math.pi * r * r
ok = math.isclose(a, b)
h = math.hypot(3, 4, 12)
n = math.factorial(5)
```

> `math` mirrors Python's `math` module exactly — same name (lowercase), same function names, parameter order, defaults, kw-only markers, return types. No `import math` needed in POOP — the namespace is injected globally.

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

## OS error codes (`errno` module)

```python
# Python
import errno

if exc.errno == errno.ENOENT:
    handle_missing()
name = errno.errorcode[exc.errno]
```

```python
# POOP
exc.errno.equals(errno.ENOENT).if_true(lambda: handle_missing())
name = errno.errorcode.at(exc.errno)
```

> Every public integer constant in `errno.*` is reachable as `errno.<NAME>` (POOP `Int`). The reverse map `errno.errorcode` is a POOP `Dict[Int, Str]` — use `.at(code)` to look up a name.

## Password prompts (`getpass` module)

```python
# Python
import getpass

user = getpass.getuser()
pwd = getpass.getpass("Password: ")
```

```python
# POOP
user = getpass.getuser()
pwd = getpass.getpass("Password: ")
```

> Both `getpass.getuser()` and `getpass.getpass(prompt)` return POOP `Str`. `getpass.GetPassWarning` is not exposed in POOP — the underlying CPython call still emits it to stderr, but POOP has no warning model to catch it.

## Cryptographic randomness (`secrets` module)

```python
# Python
import secrets

token = secrets.token_hex(16)
n = secrets.randbelow(100)
ok = secrets.compare_digest(a, b)
```

```python
# POOP
token = secrets.token_hex(16)
n = secrets.randbelow(100)
ok = secrets.compare_digest(a, b)
```

> Anything cryptographic goes through `secrets`, not `random`. `secrets.token_bytes` returns `Bytes`; `token_hex`/`token_urlsafe` return `Str`. `secrets.compare_digest(a, b, /)` is constant-time and accepts either `Str` or `Bytes` — but both arguments must be the same type, exactly like CPython.
