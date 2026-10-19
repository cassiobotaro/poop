# Proposal

## Why

POOP leaves the wrong-arity sentence to CPython, and since
`arity-names-the-receiver` that sentence names the class CPython would name.
A handful of messages still word their own arity refusal, and the reasons
split them into two kinds:

- The ones that **teach**. A missing block answers `#map expects a block,
  got nothing — write .map(lambda item: …)`, and a constructor answers
  `Try takes one block, got nothing — write Try(lambda: …)`. In a language
  where blocks replace `if`, `for` and `try`, the hint is the useful part.
- The ones that existed only because **the name was wrong**. `raise_(1)`
  answered `#raise_ takes no argument once the exception is built, got 1
  argument` because CPython's sentence named `Exception.raise_()` or
  `object.raise_()`. The rename now names the class correctly, so the POOP
  sentence adds nothing CPython's does not say.

Three findings break that line:

- The branch messages, which are POOP's substitutes for `if`, `and`/`or`
  and `while` and need the hint most, do not use it. `True.if_true()`,
  `True.and_()`, `None.if_none()`, `(5).if_none_if_not_none()` and
  `(lambda: True).while_true()` (16 messages on `bool`, `NoneType`, every
  object and `function`) answer
  CPython's `bool.if_true() missing 1 required positional argument:
  'block'`, while `[1].map()` and `[1].find()` answer POOP's hint.
- The `bool` pairs' hint shows one block where they take two: `.if_true_if_false(lambda: …)`.
  The `none` pairs show both (`lambda: …, lambda x: …`).
- A caught error's arity sentences blame `object`: `e.message(1)` answers
  `object.message() takes …` for an error that says it is a `ValueError`.
  `Error` is cloaked as `object`, so the rename (and the sweep's oracle)
  read that name. Returning `raise_` to CPython's shape without fixing this
  would bring back `object.raise_()`, the sentence that motivated the POOP
  wording.

## What Changes

- **The rule is written down**: POOP rewords an arity refusal only when it
  has a hint to give. It goes in `INFECTIONS.md` beside the arity paragraph.
- **A caught error's arity sentence names the exception's class**:
  `e.message(1)` answers `ValueError.message() takes 1 positional argument
  but 2 were given`. A message `Object` defines keeps `object`, as everywhere
  else.
- **`raise_` returns to CPython's shape** on a built and on a caught
  exception: `ValueError.raise_() takes 1 positional argument but 2 were
  given`.
- **The branch family refuses a missing block with the hint**, in
  `a_block`'s words: `#if_true expects a block, got nothing — write
  .if_true(lambda: …)`. This covers `if_true`, `if_false`,
  `if_true_if_false`, `if_false_if_true`, `and_` and `or_` on `bool`; `if_none`,
  `if_not_none` and both pairs on `NoneType` and on every object; and
  `while_true` and `while_false` on a block.
- **The `bool` pairs' hint shows both blocks**: `write
  .if_true_if_false(lambda: …, lambda: …)`.

Unchanged on purpose, because each one teaches:
- the converters (`range is built from a stop, … — write range(stop) or
  range(start, stop, step)`);
- `Try()` and `With()` (`— write Try(lambda: …)`);
- the missing-block refusals already in place (`map`, `do`, `find`,
  `reduce`, `else_`);
- `raise_from`'s refusals, which say what it accepts (`an exception or
  None`).

Out of scope, and why:
- **The block literal's own arity sentence** (`block expects 0 arguments,
  got 1`). A lambda has no name for CPython to give, which is what that
  rewording replaced, and the `block-arity` spec covers it.
- **`lambda item: …` in the single-block hints against `lambda x: …` in the
  pairs.** Both read correctly. Unifying the placeholder is a separate
  wording pass, not an arity question.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `message-arity`: adds that a caught error names its exception's class,
  and that a missing block in the branch family is refused with the hint.
- `exception-mirrors`: `raise_` on a built exception refuses an argument in
  CPython's shape.
- `error-type`: `raise_` on a caught error refuses an argument in CPython's
  shape.

## Impact

- `poop/types/block.py` (`_cpython_name` names a caught error by its kind;
  `while_true`/`while_false` defaults).
- `poop/types/boolean.py`, `poop/types/none.py`, `poop/types/object.py`
  (sentinel defaults on the branch family; `bool` pair hint).
- `poop/types/exceptions.py`, `poop/types/error.py` (`raise_` loses its
  `*extra` refusal).
- `tests/test_no_python_wording.py` (the oracle names a caught error by its
  kind), `tests/test_types/test_message_arity.py`, and the branch, error and
  exception test modules.
- `INFECTIONS.md`. `README.md` shows none of these sentences.
