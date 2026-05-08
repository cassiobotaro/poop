# Lesson 2 — Conditionals

**Goal:** branch on a condition without `if`, `else`, `and`, or `or`.

## What's new

POOP forbids the `if` statement. The replacement is a method on the
boolean value: it receives a **lambda** holding the code to run, and
decides whether to call it.

```python
(score >= 60).if_true(lambda: "passing".print())
```

The lambda is non-negotiable. If you forget it and write
`(score >= 60).if_true("passing".print())`, the string prints
unconditionally — the argument is evaluated *before* `if_true` even
sees it. The lambda is what defers the work until the boolean has
chosen.

For two-way branches use `if_true_if_false`, which **returns** the
chosen lambda's value. That's how you build the equivalent of Python's
ternary `a if cond else b`:

```python
label = (n % 2 == 0).if_true_if_false(
    lambda: "even",
    lambda: "odd",
)
```

For combining conditions, `and_` and `or_` take a lambda too — same
short-circuit semantics as Python's `and` / `or`.

## Walk-through

Save this to `vote.py`:

```python
age = 17
(age >= 18).if_true_if_false(
    lambda: "Can vote".print(),
    lambda: "Too young".print(),
)
```

Running `poop vote.py` prints `Too young`. Change `age = 19` and rerun
— now you get `Can vote`.

Chain conditions with `and_` / `or_`. The classic example is the leap
year rule: a year is a leap year if it's divisible by 400, or
divisible by 4 but not by 100.

```python
year = 2000
is_leap = (year % 400 == 0).or_(
    lambda: (year % 4 == 0).and_(lambda: (year % 100 == 0).not_())
)
is_leap.print()
```

Reading this from the inside out: divisible by 100 and *not* (`not_`)
that → handed as a lambda to `and_` (so it's only evaluated when
`year % 4 == 0`) → that whole chunk is the right side of `or_`, only
evaluated when `year` is *not* divisible by 400.

It's the same evaluation order Python's `and` / `or` give you — the
syntax is just different.

For chained `elif`-like ladders, nest `if_true_if_false`:

```python
score = 85
letter = (score >= 90).if_true_if_false(
    lambda: "A",
    lambda: (score >= 80).if_true_if_false(
        lambda: "B",
        lambda: (score >= 70).if_true_if_false(
            lambda: "C",
            lambda: "D",
        ),
    ),
)
letter.print()  # B
```

Three or four levels deep is fine. Past that, consider a dispatch
dictionary instead. (You'll see the dispatch pattern in
[Lesson 5](05-collections.md).)

POOP forbids defining a `def letter(score):` at module level — every
function lives inside a class. We'll cover that in
[Lesson 4](04-classes.md).

## Try it

Write a `Year` class with an `is_leap()` method following the rule
above. Print whether 2000, 1900, 2008, and 2017 are leap years.

## Anchor example

[`examples/leap_year.py`](https://github.com/cassiobotaro/poop/blob/main/examples/leap_year.py) — the leap-year rule packaged into a class.

## Reference

- [Python vs POOP — Conditionals](../python-vs-poop/conditionals.md)
  for `not_`, `xor`, `eqv`, `assert_`, and the rest.
- [Next lesson — Iteration →](03-iteration.md)
