# Tutorial

A linear, hand-held walk through POOP for someone who already writes
Python. Six short lessons, ~45 minutes end to end.

## Prerequisites

- Python fluency — you can read and write a Python class without
  thinking about it.
- POOP installed. The [Getting started](../getting-started.md) page
  covers `uv sync --dev` and how to run a `.py` file with `poop`.

You don't need any Smalltalk background. Where Smalltalk shows up,
it's flagged as a curiosity, not a prerequisite.

## How to follow along

Most snippets are short — paste them into the [REPL](../repl.md) and
watch the output. Longer programs at the end of each lesson are
better saved to a file and run with `poop file.py`.

Each lesson has the same shape:

- **What's new** — one or two POOP ideas, in Python terms.
- **Walk-through** — short snippets that build up a small program.
- **Try it** — one exercise. The solution lives in the lesson's
  *anchor example*, a runnable file in
  [`examples/`](https://github.com/cassiobotaro/poop/tree/main/examples).
- **Reference** — link to the matching [Python vs POOP](../python-vs-poop/index.md)
  page when you want the exhaustive list.

## Lessons

1. [Strings](01-strings.md) — strings as objects; `.print()` and `.input()`.
2. [Conditionals](02-conditionals.md) — booleans receive blocks.
3. [Iteration](03-iteration.md) — `range(n).do(...)`, `map`, `filter`,
   lambdas.
4. [Classes](04-classes.md) — defining a class, instance state,
   `while_true` over mutable state.
5. [Collections](05-collections.md) — lists, dicts, sets, fluent
   pipelines.
6. [Errors](06-errors.md) — `Try(...).except_(...).run()` and `raise_`.

After lesson 6, the [`rpn_calculator.py`](https://github.com/cassiobotaro/poop/blob/main/examples/rpn_calculator.py)
example pulls everything together as a self-directed capstone.
