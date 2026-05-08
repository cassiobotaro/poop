# Builtins

Python ships dozens of free functions: `print`, `len`, `sum`, `min`,
`map`, `isinstance`, `sorted`, and so on. POOP forbids them all. The
replacements are **methods on the receiver**.

## The POOP way

In POOP, free functions are illegal — every operation belongs to an
object. Instead of `len(x)`, you ask `x` how long it is:

```python
items.len()
```

Where Python writes `f(x, y)`, POOP usually writes `x.f(y)` — the
first argument moves to the receiver position.

## `print` and `input`

**Python**

```python
print("Hello, World!")
name = input("What is your name? ")
```

**POOP**

```python
"Hello, World!".print()
name = "What is your name? ".input()
```

`print` lives on **every** POOP object via the `Object` base class, so
any value can be printed by sending it the message:

```python
42.print()
[1, 2, 3].print()
True.print()
```

`input` is a method on `Str`: the prompt is the receiver, and the
returned string is what the user typed.

`print` accepts the same `end=` and `flush=` keyword arguments as
Python's builtin.

**Why:** the message-passing model gives every object a uniform
"render to stdout" hook; there's no need for a top-level function.

**See also:** [`examples/hello_world.py`](https://github.com/cassiobotaro/poop/blob/main/examples/hello_world.py),
[`examples/greet.py`](https://github.com/cassiobotaro/poop/blob/main/examples/greet.py)

## `len`, `abs`, `round`

**Python**

```python
n = len(items)
d = abs(-7)
r = round(3.456)
```

**POOP**

```python
n = items.len()
d = (-7).abs()
r = (3.456).round()
```

The pattern is the same for every introspection-style builtin: drop
the function and call a method on the value.

**Why:** the value already knows its own length / magnitude / rounded
form. Asking it directly removes the indirection through a free
function.

**See also:** [`examples/statistics.py`](https://github.com/cassiobotaro/poop/blob/main/examples/statistics.py)

## `sum`, `min`, `max`, `sorted`, `reversed`

**Python**

```python
total = sum(numbers)
hi    = max(numbers)
lo    = min(numbers)
asc   = sorted(numbers)
desc  = list(reversed(numbers))
```

**POOP**

```python
total = numbers.sum()
asc   = numbers.sorted()
desc  = numbers.reversed()
```

`min` and `max` work between two values (`a.min(b)`, `a.max(b)`) — to
find the extreme of a whole list, sort it and pick the ends:

```python
numbers.sorted().at(0)                      # min
numbers.sorted().at(numbers.len() - 1)      # max
```

`sorted` accepts an optional `key=` lambda, mirroring Python's
`sorted(items, key=...)`.

**Why:** every aggregation lives on the collection rather than as a
separate function the collection has to be passed to.

**See also:** [`examples/statistics.py`](https://github.com/cassiobotaro/poop/blob/main/examples/statistics.py),
[`examples/grades.py`](https://github.com/cassiobotaro/poop/blob/main/examples/grades.py)

## `map`, `filter`, `reduce`

**Python**

```python
squared  = list(map(lambda x: x * x, numbers))
positive = list(filter(lambda x: x > 0, numbers))
total    = functools.reduce(lambda acc, x: acc + x, numbers, 0)
```

**POOP**

```python
squared  = numbers.map(lambda x: x * x)
positive = numbers.filter(lambda x: x > 0)
total    = numbers.reduce(0, lambda acc, x: acc + x)
```

Two things to notice:

1. `map` and `filter` return a **list directly** — no `list(...)` wrap.
2. `reduce` takes the **initial value first** (`reduce(init, block)`),
   the opposite of `functools.reduce`.

`filter_false(block)` is the complement of `filter` — keep elements
where the block returns falsy. It replaces the `itertools.filterfalse`
pattern.

**Why:** these methods chain naturally on the receiver, so a pipeline
reads top-to-bottom: `items.filter(...).map(...).do(...)`.

**See also:** [`examples/pipeline.py`](https://github.com/cassiobotaro/poop/blob/main/examples/pipeline.py),
[`examples/statistics.py`](https://github.com/cassiobotaro/poop/blob/main/examples/statistics.py)

!!! info "Smalltalk origin"
    Smalltalk spells these `collect:`, `select:`, and `inject:into:`.
    POOP keeps the Python names (`map`, `filter`, `reduce`) so a Python
    reader recognizes them immediately.

## `all`, `any`, and `in`

**Python**

```python
if all(x > 0 for x in numbers): ...
if any(x < 0 for x in numbers): ...
if "alice" in users: ...
```

**POOP**

```python
numbers.all(lambda x: x > 0).if_true(lambda: ...)
numbers.any(lambda x: x < 0).if_true(lambda: ...)
users.includes("alice").if_true(lambda: ...)
```

`all` and `any` take a predicate lambda — there is no implicit
truthiness check across the collection; you pick the test explicitly.

`includes(item)` replaces the `in` operator. To express `not in`,
chain `.not_()`:

```python
users.includes("alice").not_().if_true(lambda: ...)
```

**Why:** `in` is a Python operator with no method form; POOP routes
membership through `includes`, the same name Smalltalk-style
collections use across the language.

**See also:** [`examples/common_interests.py`](https://github.com/cassiobotaro/poop/blob/main/examples/common_interests.py)

## Indexing and slicing

**Python**

```python
first  = items[0]
window = items[1:4]
prefix = "POOP language"[0:4]
```

**POOP**

```python
first  = items.at(0)
window = items.slice(Slice(1, 4))
prefix = "POOP language".slice(Slice(0, 4))
```

`at(i)` replaces `obj[i]`. For ranges, build a `Slice(start, stop)` (or
`Slice(start, stop, step)`) and pass it to `slice(...)`. The same
`Slice` value works on lists, strings, tuples, byte arrays, and ranges.

**Why:** subscript syntax (`x[i]`) is forbidden because it's syntactic
sugar with no message-send equivalent in Python's grammar. POOP exposes
the underlying operation as a method.

**See also:** [`examples/slicing.py`](https://github.com/cassiobotaro/poop/blob/main/examples/slicing.py)

## `isinstance` and `hasattr`

**Python**

```python
if isinstance(x, Account):
    process(x)
if hasattr(x, "deposit"):
    x.deposit(100)
```

**POOP**

```python
x.is_instance(Account).if_true(lambda: process(x))
x.has_attr("deposit").if_true(lambda: x.deposit(100))
```

Both methods live on `Object`, so every value answers them.

**Why:** introspection moves from a global function (`isinstance(x, T)`)
to a message sent to the value (`x.is_instance(T)`).

## `try` / `except` → `Try(...).except_(...).run()`

**Python**

```python
try:
    account.withdraw(150)
except ValueError as e:
    print("Error: " + str(e))
```

**POOP**

```python
Try(lambda: account.withdraw(150)).except_(
    ValueError,
    lambda e: ("Error: " + e.message()).print(),
).run()
```

`Try(block)` wraps the protected code in a lambda. `except_(ExcType,
handler)` registers a handler — chain it for multiple exception types.
**Nothing runs until you call `.run()`**.

The handler receives an `Error` object that exposes `e.kind()` (the
exception class name) and `e.message()` (the string the exception was
raised with). Use `ValueError.raise_("msg")` to raise an exception in
the first place.

**Why:** `try` is a Python statement; POOP forbids statements, so the
construct becomes a fluent builder of method calls.

**See also:** [`examples/bank_account.py`](https://github.com/cassiobotaro/poop/blob/main/examples/bank_account.py)

## `with` → `With(...).do(...)`

**Python**

```python
with lock:
    critical_section()
```

**POOP**

```python
With(lambda: lock).do(lambda _: critical_section())
```

`With(cm_block)` takes a lambda that returns the context manager.
`.do(body_block)` runs the body with the `__enter__` value bound to the
parameter — use `_` if you don't need it. The context manager's
`__exit__` runs after the body, just like Python's `with`.

The context manager object must still implement Python's
`__enter__` / `__exit__` protocol — `With` only replaces the **syntax**.

**Why:** `with` is another Python statement that becomes a method call
in POOP. The lambdas defer evaluation so the construct can run setup,
body, and teardown in the right order.
