# Lesson 3 — Iteration

**Goal:** loop without `for` or `while`.

## What's new

POOP forbids both loop keywords. The replacement: collections iterate
**themselves**. You hand them a lambda and they run it once per
element.

```python
[1, 2, 3].do(lambda x: x.print())
```

`do` is the side-effect form (returns `none`). When you want to keep
each result, use `map`. When you want only some elements, use `filter`.

```python
squares = [1, 2, 3, 4].map(lambda x: x * x)   # [1, 4, 9, 16]
evens   = [1, 2, 3, 4].filter(lambda x: x % 2 == 0)  # [2, 4]
```

For "do this N times", reach for `range(n).do(...)` — `range` returns
a POOP `Range` that supports the same iteration methods.

```python
range(5).do(lambda i: i.print())   # 0 1 2 3 4
```

## Walk-through

Print 1 to 5:

```python
range(1, 6).do(lambda i: i.print())
```

Now FizzBuzz — print 1 to 30, replacing multiples of 3 with `Fizz`,
multiples of 5 with `Buzz`, multiples of both with `FizzBuzz`. We
already know how to nest `if_true_if_false` from
[Lesson 2](02-conditionals.md):

```python
range(1, 31).do(
    lambda i: (i % 15 == 0).if_true_if_false(
        lambda: "FizzBuzz".print(),
        lambda: (i % 3 == 0).if_true_if_false(
            lambda: "Fizz".print(),
            lambda: (i % 5 == 0).if_true_if_false(
                lambda: "Buzz".print(),
                lambda: i.print(),
            ),
        ),
    )
)
```

It's verbose, but every piece is something you've already seen — a
range iterates with `do`, a boolean picks a branch with
`if_true_if_false`.

Pipelines of `filter` and `map` chain naturally:

```python
total = (
    range(1, 11)
    .filter(lambda x: x % 2 == 0)   # even numbers 2..10
    .map(lambda x: x * x)           # squared
    .sum()                           # added up
)
total.print()   # 220
```

That `.sum()` at the end is the same `sum` you'd reach for in Python
— except it's a method on the collection, not a global function. More
on that in [Lesson 5](05-collections.md).

## Try it

Save the FizzBuzz program above to `fizzbuzz.py` and run it. Then
modify it so it prints up to 100 instead of 30.

For a deeper challenge: also count how many `Fizz`-only outputs you
print (no `Buzz` or `FizzBuzz`).

## Anchor example

[`examples/fizzbuzz.py`](https://github.com/cassiobotaro/poop/blob/main/examples/fizzbuzz.py) — the canonical FizzBuzz, 1 to 100.

## Reference

- [Python vs POOP — Loops](../python-vs-poop/loops.md) for `while`,
  `enumerate` / `zip`, and the substitutes for `break` / `continue`.
- [Next lesson — Classes →](04-classes.md)
