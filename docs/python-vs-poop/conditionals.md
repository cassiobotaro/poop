# Conditionals

Python has `if`, `elif`, `else`, the boolean operators `and` / `or` /
`not`, and `assert`. POOP forbids all of them. The replacements are
methods on the boolean values **`true`** and **`false`** that take
**lambdas**.

## The POOP way

In POOP, `x > 0` returns a boolean object, and that object decides what
to do next. You ask it by sending a message:

```python
(x > 0).if_true(lambda: "positive".print())
```

The lambda matters: POOP evaluates branches **only when the boolean
selects them**. This is the same lazy behavior `if` already gives you in
Python — the false branch never runs — but here you get it by passing
unevaluated code to a method instead of by writing a statement.

If you forget the lambda and write `(x > 0).if_true("positive".print())`,
the string prints unconditionally before `if_true` is even called. **A
missing lambda is the most common POOP mistake.**

## `if` → `if_true` / `if_false`

**Python**

```python
if value > 0:
    print("positive")
```

**POOP**

```python
(value > 0).if_true(lambda: "positive".print())
```

Use `if_false(lambda: ...)` when you'd write a Python `if not cond:`.
Both return `none` when the branch doesn't fire — they're chosen for
side effects, not values.

**Why:** the boolean receiver runs the block only when it matches.
The lambda defers `"positive".print()` so it doesn't execute on the
`false` branch.

**See also:** [`examples/leap_year.py`](https://github.com/cassiobotaro/poop/blob/main/examples/leap_year.py)

## `if` / `else` → `if_true_if_false`

**Python**

```python
label = "even" if n % 2 == 0 else "odd"
```

**POOP**

```python
label = (n % 2 == 0).if_true_if_false(
    lambda: "even",
    lambda: "odd",
)
```

For `elif` chains, nest the call:

```python
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
```

`if_false_if_true(false_block, true_block)` exists for symmetry — same
semantics with the arguments flipped. Use whichever reads better.

**Why:** unlike `if_true` / `if_false`, this form **always** returns the
value of the chosen lambda, so you can use it as an expression — like
Python's ternary `a if cond else b`.

**See also:** [`examples/fizzbuzz.py`](https://github.com/cassiobotaro/poop/blob/main/examples/fizzbuzz.py),
[`examples/grades.py`](https://github.com/cassiobotaro/poop/blob/main/examples/grades.py)

!!! info "Smalltalk origin"
    Smalltalk spells these `ifTrue:`, `ifFalse:`, and `ifTrue:ifFalse:`.
    POOP renames them with underscores to fit Python's identifier rules,
    but the semantics are identical.

## `and` / `or` → `and_` / `or_`

**Python**

```python
if user.is_active and user.has_permission():
    grant_access()
```

**POOP**

```python
user.is_active.and_(lambda: user.has_permission()).if_true(
    lambda: grant_access()
)
```

The right-hand side is wrapped in a lambda. That's not decoration — it
is what gives `and_` and `or_` Python's short-circuit behavior:
`user.has_permission()` is **not called** when `user.is_active` is
`false`.

A real example, picked from `leap_year.py`:

```python
return (self._value % 400 == 0).or_(
    lambda: (self._value % 4 == 0).and_(
        lambda: (self._value % 100 == 0).not_()
    )
)
```

**Why:** without the lambda, Python would evaluate the right side
eagerly. The lambda lets the boolean receiver decide whether to call it,
preserving short-circuit semantics.

**See also:** [`examples/leap_year.py`](https://github.com/cassiobotaro/poop/blob/main/examples/leap_year.py)

!!! info "Smalltalk origin"
    Smalltalk uses `and:` and `or:` (the `:` marks a block argument) for
    the lazy form, and `&` / `|` for the eager form. POOP only ships the
    lazy form.

## `not` → `not_`

**Python**

```python
if not name.startswith("_"):
    process(name)
```

**POOP**

```python
name.startswith("_").not_().if_true(lambda: process(name))
```

`not_` flips a boolean. The trailing underscore is there because `not`
is a Python keyword.

**Why:** every operator in POOP is a method, including negation. There
is no unary `not` syntax to fall back on.

## `xor` and `eqv`

**Python**

```python
a != b   # for booleans, this is xor
a == b   # for booleans, this is equivalence
```

**POOP**

```python
a.xor(b)
a.eqv(b)
```

Both take a value, not a lambda — there's no short-circuit to preserve.

**Why:** these are full-evaluation boolean operators; both operands need
to be inspected anyway.

## `assert` → `assert_`

**Python**

```python
assert balance >= 0, "balance must be non-negative"
```

**POOP**

```python
(balance >= 0).assert_("balance must be non-negative")
```

`assert_` is a method on booleans. On `true` it returns the boolean
unchanged; on `false` it raises `AssertionError` with the message.

**Why:** Python's `assert` is a statement; POOP forbids statements that
encode control flow, so the check becomes a method call instead.

## Pitfalls

- **Forgetting the lambda.** `cond.if_true("hi".print())` prints "hi"
  unconditionally because `"hi".print()` runs before `if_true` is
  called. Always pass `lambda: ...`.
- **Deeply nested branches.** Long `if_true_if_false` chains read worse
  than Python `if/elif`. When you reach four levels, consider extracting
  a helper method or using a `dict` keyed on the discriminator (see
  `examples/rpn_calculator.py` for the dispatch-table pattern).
- **Returning from inside a lambda.** A bare `return` inside the lambda
  returns from the lambda, not from the enclosing method. Compute the
  value with `if_true_if_false` and `return` the result.
