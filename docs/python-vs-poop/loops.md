# Loops

Python has `for x in col`, `for i in range(...)`, and `while cond`. POOP
forbids all three keywords. The replacements are methods on
**collections** (for `for`) and on **blocks** (for `while`).

## The POOP way

You don't iterate a collection in POOP — you ask it to iterate itself
by sending it a message:

```python
[1, 2, 3].do(lambda x: x.print())
```

The collection owns the loop. You hand it a lambda; it calls that
lambda once per element. There is no loop variable, no `break`, no
`continue` — just a method that runs your block.

For `while`, the same idea moves to blocks: you wrap the condition in a
lambda and ask **that lambda** to keep running a body until the
condition flips.

## `for x in col` → `col.do(...)`

**Python**

```python
for name in names:
    print("Hello, " + name)
```

**POOP**

```python
names.do(lambda name: ("Hello, " + name).print())
```

`do` returns `none` and exists for side effects. If you want to keep
each result, use `map`; to keep some of the elements, use `filter`. See
[Builtins](builtins.md) for those.

**Why:** the collection knows how to walk itself. You pass it a lambda;
it calls the lambda once per element with the current value bound to
the parameter.

**See also:** [`examples/greet.py`](https://github.com/cassiobotaro/poop/blob/main/examples/greet.py),
[`examples/common_interests.py`](https://github.com/cassiobotaro/poop/blob/main/examples/common_interests.py)

!!! info "Smalltalk origin"
    Smalltalk spells this `do:`. POOP keeps the name (without the colon)
    and reuses it across `List`, `Dict`, `Set`, `Range`, `Tuple`, and
    every other iterable type.

## `for i in range(n)` → `range(n).do(...)`

**Python**

```python
for i in range(1, 101):
    print(i)
```

**POOP**

```python
range(1, 101).do(lambda i: i.print())
```

`range` returns a POOP `Range` that responds to the same iteration
methods every other collection does. There is **no** `n.times_repeat`
or similar — `range(n).do(...)` is the canonical "do this N times".

**Why:** POOP doesn't introduce a special integer-loop method when
`range` already supplies an iterable.

**See also:** [`examples/fizzbuzz.py`](https://github.com/cassiobotaro/poop/blob/main/examples/fizzbuzz.py),
[`examples/collatz.py`](https://github.com/cassiobotaro/poop/blob/main/examples/collatz.py)

## `while cond` → `(lambda: cond).while_true(body)`

**Python**

```python
while n > 1:
    step()
```

**POOP**

```python
(lambda: n > 1).while_true(lambda: step())
```

Both arguments are lambdas:

- The **receiver** is a lambda that returns the current condition. It
  has to be a lambda — not a value — because the condition needs to be
  re-evaluated each iteration.
- The **body** is a lambda that runs once per iteration.

A real example, from `collatz.py`:

```python
class Collatz:
    def __init__(self, n):
        self._n = n

    def run(self):
        (lambda: self._n > 1).while_true(lambda: self._step())
```

`while_false(body)` exists for the inverted form (loop until the
condition becomes `true`).

**Why:** in Python `while cond:` re-checks `cond` each iteration
because it sits in a statement, not a value. POOP can't capture an
"un-evaluated condition" any other way, so you wrap it in a lambda.

**See also:** [`examples/collatz.py`](https://github.com/cassiobotaro/poop/blob/main/examples/collatz.py)

!!! info "Smalltalk origin"
    Smalltalk spells this `[ cond ] whileTrue: [ body ]`. The `[ ... ]`
    syntax is Smalltalk's block literal — the equivalent of `lambda:` in
    POOP.

## `enumerate` and `zip`

**Python**

```python
for i, name in enumerate(names):
    print(i, name)

for a, b in zip(xs, ys):
    print(a + b)
```

**POOP**

```python
names.enumerate().do(lambda pair: (pair.at(0), pair.at(1)).print())

xs.zip(ys).do(lambda pair: (pair.at(0) + pair.at(1)).print())
```

`enumerate()` and `zip()` are methods on every iterable. They return
collections of pair-tuples; you index into each pair with `at(0)` and
`at(1)` because POOP forbids `pair[0]` (see
[Builtins → Indexing](builtins.md)).

**Why:** POOP lifts the free-function builtins `enumerate` and `zip`
onto the iterable itself, so every iterable knows how to enumerate or
zip itself.

## `break` and `continue`

POOP has **no** direct replacement for `break` or `continue`. You stop
short or skip elements by choosing a different iteration method:

| Python pattern | POOP equivalent |
|---|---|
| `for x in col: if predicate(x): return x` | `col.find(lambda x: predicate(x))` — returns the first match or `none` |
| `for x in col: if not predicate(x): continue; ...` | `col.filter(lambda x: predicate(x)).do(lambda x: ...)` |
| `for x in col: if predicate(x): continue; ...` | `col.filter_false(lambda x: predicate(x)).do(lambda x: ...)` |
| `for x in col: if stop(x): break; accumulate(x)` | rebuild as a `reduce` that early-returns the accumulator, or restructure as `find` + `slice` |

**Why:** `break` and `continue` are Python statements that change
control flow mid-loop. POOP's iteration methods don't expose a
mid-loop hook — you select what runs by composing `find`, `filter`,
`filter_false`, and `map` instead.

## Pitfalls

- **No `times_repeat`.** If you reach for "do this N times", reach for
  `range(n).do(lambda i: ...)` instead. The `i` is unused but cheap.
- **Forgetting to wrap the condition in a lambda for `while_true`.**
  `(self._n > 1).while_true(...)` doesn't work — `self._n > 1` is
  evaluated once and produces a boolean, not a re-evaluable condition.
  You need `(lambda: self._n > 1).while_true(...)`.
- **Mutable state inside lambdas.** A lambda can read closed-over
  variables but can't reassign them. Put the state on `self` (an
  instance variable) and mutate that, the way `collatz.py` does with
  `self._n`.
- **`do` returns `none`.** It's a sink, not a pipeline step. To chain
  more operations after the loop, use `map` (or `filter`) and put the
  side-effecting `do` last.
