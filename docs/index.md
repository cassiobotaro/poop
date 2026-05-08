# POOP

**POOP** is an acronym for **P**ython **O**bject **O**riented **P**rogramming.

A Python interpreter infected by Smalltalk.

## Quickstart

POOP rewrites Python so that **every operation is a message sent to an
object** — no free functions, no control-flow statements. Two mechanisms
drive this:

- **Validators** reject forbidden constructs (`if`, `for`, `while`,
  `print(...)`, `len(x)`, …).
- **Transformers** rewrite the AST before execution so every literal
  becomes a POOP type (`Int`, `Str`, `Boolean`, `List`, …) and `range()`
  / `bool()` / `list()` / … return their POOP equivalents.

### Key substitutions

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

For runnable side-by-side comparisons of every Python construct POOP
forbids, see [Python vs POOP](python-vs-poop/index.md).

### Hello, World

```python
"Hello, World!".print()
```

See [Getting started](getting-started.md) to install POOP and run your
first program.
