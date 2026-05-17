<p align="center">
  <img src="poop.png" alt="POOP logo" width="600">
</p>

# POOP 💩

**POOP** — **P**ython **O**bject **O**riented **P**rogramming. A Python 3.14 interpreter that enforces Smalltalk-style message passing by rejecting `if`/`for`/`print`/`isinstance` and rewriting Python literals (`1`, `"hi"`, `True`, `[…]`, `{…}`) into POOP types where every operation is a message to a receiver.

POOP is for **educational exploration of message-passing semantics inside the Python ecosystem**, not for production. Status: **experimental** — the API changes between minor versions.

## Install

End user (until POOP is published to PyPI):

```bash
git clone https://github.com/cassiobotaro/poop.git
cd poop
uv sync
uv run poop examples/hello_world.py
```

Contributor / development setup lives in [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Hello, POOP

```python
"Hello, World!".print()
```

Run it:

```bash
poop hello.py            # run a file
poop                     # interactive REPL (Ctrl+D to exit)
```

## The ten essentials

| Python | POOP |
|---|---|
| `print(x)` | `x.print()` |
| `if cond: …` / `else:` | `cond.if_true(lambda: …)` / `cond.if_true_if_false(lambda: …, lambda: …)` |
| `for x in col: …` | `col.do(lambda x: …)` |
| `while cond: …` | `(lambda: cond).while_true(lambda: …)` |
| `len(x)` | `x.len()` |
| `x[i]` | `x.at(i)` |
| `x[a:b]` | `x.slice(a, b)` |
| `not x` | `x.not_()` |
| `x and y` / `x or y` | `x.and_(lambda: y)` / `x.or_(lambda: y)` |
| `-x` | `x.negated()` |

Full Python → POOP recipe book: [`MIGRATION.md`](MIGRATION.md). Design rationale: [`INFECTIONS.md`](INFECTIONS.md).

## What's banned (and what to use instead)

POOP runs ~60 validators on every program. Grouped by theme:

**Control flow** — messages on a Boolean, not statements.
- `if` / `else` / ternary → `cond.if_true(lambda: …)` / `cond.if_true_if_false(lambda: …, lambda: …)`
- `for` / `while` / `match` → `col.do(…)` / `(lambda: cond).while_true(…)` / polymorphism
- `with` / `try` / `raise` / `assert` → `With(lambda: cm()).do(…)` / `Try(lambda: …).except_(ExcType, lambda e: …).run()` / `ValueError.raise_("msg")` / `obj.assert_("msg")`

**Free functions** — call as a method on the receiver.
- `print` / `len` / `abs` / `hash` / `round` / `pow` / `divmod` / `min` / `max` / `sum` / `sorted` / `reversed` → `x.print()`, `x.len()`, `x.abs()`, `x.hash()`, …
- `map` / `filter` → `col.map(lambda x: …)` / `col.filter(lambda x: …)`
- `ascii` / `bin` / `chr` / `repr` / `format` → corresponding methods on `Int` / `Str`
- `input` / `open` → `"prompt".input()` / `Path("file").read_text()`
- `iter` → `col.iter()` / `it.next()`

**Introspection** — POOP code talks via messages, not reflection.
- `isinstance` / `issubclass` / `callable` / `id` / `dir` / `hasattr` / `getattr` / `setattr` / `type(...)` → use polymorphism (subclass dispatch) instead of asking what something is

**Operator sugar** — methods on the receiver.
- `x[i]` / `x[a:b]` → `x.at(i)` / `x.slice(a, b)`
- `not x` / `x and y` / `x or y` → `x.not_()` / `x.and_(lambda: y)` / `x.or_(lambda: y)`
- `-x` / `+x` / `~x` → `x.negated()` / drop the `+` / `x.bit_invert()`
- `x is None` / `x in y` → `x.is_none()` / `y.includes(x)` (identity via `x.is_identical(y)`)

**Syntax shortcuts that hide behaviour.**
- comprehensions (`[x for x in …]`, `{…}`, generator exprs) → explicit `.map` / `.filter` / `.do`
- top-level `def` (free functions) → define as a method inside a class
- `yield` / walrus `:=` / `del` / `global` → out of scope

**Side-channels.**
- `exec` / `breakpoint` / `exit` — interpreter escape hatches forbidden

The full catalog with one row per validator and the substitute recipe lives in [`INFECTIONS.md`](INFECTIONS.md).

## Learn by example

[`examples/`](examples/) ships ~25 programs grouped by what they teach.

**Language basics**
- [`hello_world.py`](examples/hello_world.py) — the smallest POOP program
- [`greet.py`](examples/greet.py) — string input + concatenation
- [`fizzbuzz.py`](examples/fizzbuzz.py) — control flow via `if_true_if_false`
- [`leap_year.py`](examples/leap_year.py) — `and_` / `or_` / `not_`
- [`collatz.py`](examples/collatz.py) — while-style recursion
- [`grades.py`](examples/grades.py) — collection processing
- [`geometry.py`](examples/geometry.py) — classes with state
- [`slicing.py`](examples/slicing.py) — `Slice` as a reusable value object
- [`bank_account.py`](examples/bank_account.py) — encapsulation

**Idiomatic POOP**
- [`pipeline.py`](examples/pipeline.py) — `filter` / `filter_false` / `map` / `do` chain
- [`safe_config.py`](examples/safe_config.py) — `if_none` / `if_not_none` cascade
- [`common_interests.py`](examples/common_interests.py) — set operations
- [`statistics.py`](examples/statistics.py) — number aggregation
- [`rpn_calculator.py`](examples/rpn_calculator.py) — stack as a POOP `List`
- [`roman_numerals.py`](examples/roman_numerals.py) — string mapping
- [`async_greeter.py`](examples/async_greeter.py) — `async def` + `await asyncio.sleep` (since v0.52.0)

**Classic OO patterns** (Sandi Metz / GoF)
- [`null_customer.py`](examples/null_customer.py) — Null Object
- [`discounts.py`](examples/discounts.py) — Strategy
- [`door.py`](examples/door.py) — State
- [`payroll.py`](examples/payroll.py) — polymorphism replacing `if employee.type == ...`
- [`tree.py`](examples/tree.py) — Composite replacing `isinstance`
- [`decorators.py`](examples/decorators.py) — Decorator (composition by delegation)
- [`observer.py`](examples/observer.py) — Observer
- [`template_method.py`](examples/template_method.py) — Template Method
- [`visitor.py`](examples/visitor.py) — Visitor
- [`house_jack_built.py`](examples/house_jack_built.py) — recursive composition refactor

## Type annotations

Annotations (`x: int`, `def f(x: int) -> str:`) are not evaluated at runtime in Python and do not cause errors in POOP programs, but they are misleading: POOP transforms every literal to its own types (`Int`, `Str`, …), so a variable annotated as `int` holds an `Int` at runtime. Avoid annotations in POOP code. `type X = int` is explicitly banned by the validator pipeline.

## Where to next

- [`MIGRATION.md`](MIGRATION.md) — full Python → POOP recipe book
- [`INFECTIONS.md`](INFECTIONS.md) — every validator / transformer / type, with rationale
- [`proposals.md`](proposals.md) — open design backlog
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — dev setup, atomic-commit conventions, release flow
- [Issues](https://github.com/cassiobotaro/poop/issues) — bugs and feature requests
