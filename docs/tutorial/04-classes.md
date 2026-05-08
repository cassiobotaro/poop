# Lesson 4 — Classes

**Goal:** define your own types and write a `while`-style loop that
mutates state.

## What's new

POOP forbids module-level functions — every function lives inside a
class as a method. The class syntax itself is regular Python:

```python
class Greeter:
    def __init__(self, prefix):
        self._prefix = prefix

    def greet(self, name):
        return self._prefix + ", " + name + "!"


Greeter("Hello").greet("Alice").print()
# Hello, Alice!
```

Convention from the bundled `examples/`: instance variables get a
leading underscore (`self._prefix`, `self._n`). It's not enforced —
just signals "internal" the way Python style guides do.

The other new piece is the **`while` replacement**. Wrap the
condition in a `lambda`, send it `while_true`:

```python
(lambda: condition).while_true(lambda: body())
```

Why a lambda for the condition? Because `condition` is evaluated once
when the line runs — but a `while` loop needs to re-check it every
iteration. The lambda lets the receiver decide *when* to evaluate.

## Walk-through

The Collatz sequence: start from a positive integer, repeatedly halve
it (when even) or compute `3n + 1` (when odd). It always reaches 1.
We need mutable state (the current value) and a loop.

Save this to `collatz.py`:

```python
class Collatz:
    def __init__(self, n):
        self._n = n
        self._steps = 0

    def _step(self):
        self._n.print()
        self._n = (self._n % 2 == 0).if_true_if_false(
            lambda: self._n // 2,
            lambda: self._n * 3 + 1,
        )
        self._steps = self._steps + 1

    def run(self):
        (lambda: self._n > 1).while_true(lambda: self._step())
        self._n.print()
        ("Steps: " + self._steps.repr()).print()


Collatz(7).run()
```

Run with `poop collatz.py`. The output ends in `1` after 16 steps.

A few things to notice:

- `lambda: self._n > 1` re-reads `self._n` every iteration because
  it's a method call (`getattr`) inside the lambda — the value isn't
  captured.
- `self._step()` mutates `self._n` and `self._steps`. Lambdas can
  *read* outer variables but can't reassign them — putting state on
  `self` is the canonical workaround.
- The condition body returns `none`, so `while_true` itself returns
  `none`. We just chain the next thing on the next line.

## Try it

Write a `Counter` class with `__init__(self, target)`, `_step` that
increments an internal `_count` and prints it, and `run` that uses
`while_true` to step until `_count` reaches `target`. Calling
`Counter(5).run()` should print 1, 2, 3, 4, 5.

## Anchor example

[`examples/collatz.py`](https://github.com/cassiobotaro/poop/blob/main/examples/collatz.py) — the program above. Try other starting values like 27 (takes 111 steps).

## Reference

- [Python vs POOP — Loops](../python-vs-poop/loops.md) for the
  `while_true` / `while_false` reference.
- [Next lesson — Collections →](05-collections.md)
